"""RF03/RF04 - Motor de similaridade de cosseno sobre o dataset local."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "spotify_tracks.parquet"
FEATURES = ["danceability", "energy", "valence", "tempo"]

# Tags de contexto: alvo parcial (feature -> valor 0..1) e peso extra por feature
CONTEXT_TAGS = {
    "Treino": {"target": {"energy": 0.9, "tempo": 0.75, "danceability": 0.75}, "boost": {"energy": 1.5, "tempo": 1.4}},
    "Foco": {"target": {"energy": 0.35, "danceability": 0.35, "tempo": 0.4}, "boost": {"energy": 1.3, "danceability": 1.2}},
    "Relaxamento": {"target": {"energy": 0.2, "tempo": 0.25, "valence": 0.5}, "boost": {"energy": 1.5, "tempo": 1.3}},
}


def load_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return df.drop_duplicates("track_id").reset_index(drop=True)


class VibeRecommender:
    def __init__(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True)
        self.scaler = MinMaxScaler().fit(self.df[FEATURES])
        self.X = self.scaler.transform(self.df[FEATURES])

    def seed_vector(self, track_ids: list[str] | None = None, artists: list[str] | None = None) -> np.ndarray | None:
        mask = pd.Series(False, index=self.df.index)
        if track_ids:
            mask |= self.df["track_id"].isin(track_ids)
        if not mask.any() and artists:
            mask |= self.df["artist_name"].str.lower().isin([a.lower() for a in artists])
        return self.X[mask.values].mean(axis=0) if mask.any() else None

    def build_query(self, seed: np.ndarray | None, energy: float, valence: float,
                    tags: list[str] | None = None, vibe_strength: float = 0.6):
        """Combina sementes com sliders/tags. Retorna (vetor alvo, pesos por feature)."""
        idx = {f: i for i, f in enumerate(FEATURES)}
        target = np.full(len(FEATURES), 0.5) if seed is None else seed.copy()
        weights = np.ones(len(FEATURES))
        # sliders atuam como alvo + peso multiplicador direto
        for feat, val in (("energy", energy), ("valence", valence)):
            i = idx[feat]
            target[i] = (1 - vibe_strength) * target[i] + vibe_strength * val
            weights[i] *= 1 + 2 * abs(val - 0.5)
        for tag in tags or []:
            cfg = CONTEXT_TAGS.get(tag)
            if not cfg:
                continue
            for feat, val in cfg["target"].items():
                target[idx[feat]] = 0.5 * target[idx[feat]] + 0.5 * val
            for feat, b in cfg["boost"].items():
                weights[idx[feat]] *= b
        return np.clip(target, 0, 1), weights

    def recommend(self, target: np.ndarray, weights: np.ndarray, n: int = 20,
                  exclude_ids: list[str] | None = None) -> pd.DataFrame:
        # centraliza em 0.5 para o cosseno capturar direção (alto/baixo) e não só proporção
        Xw = (self.X - 0.5) * weights
        qw = ((target - 0.5) * weights).reshape(1, -1)
        if not np.any(qw):
            qw = qw + 1e-6
        sims = cosine_similarity(Xw, qw).ravel()
        dist = np.linalg.norm(Xw - qw, axis=1)
        score = sims - 0.5 * dist  # desempate por proximidade absoluta
        out = self.df.assign(similarity=sims, score=score)
        if exclude_ids:
            out = out[~out["track_id"].isin(exclude_ids)]
        out = out.sort_values("score", ascending=False)
        out = out.groupby("artists", sort=False).head(2)  # diversidade
        return out.head(n).reset_index(drop=True)
