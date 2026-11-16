"""Gera um dataset de exemplo em data/spotify_tracks.parquet.

Substitua por um dataset real (ex.: Kaggle "Spotify Tracks Dataset") mantendo as colunas do PRD.
IDs aqui são sintéticos — para exportar ao Spotify, use um dataset com track_id reais.
"""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
GENRES = {
    "rock": (0.5, 0.8, 0.5, 125), "pop": (0.7, 0.65, 0.65, 118), "lofi": (0.6, 0.3, 0.45, 85),
    "edm": (0.75, 0.9, 0.55, 128), "mpb": (0.55, 0.45, 0.6, 105), "acoustic": (0.5, 0.25, 0.4, 95),
    "funk": (0.85, 0.75, 0.75, 130), "classical": (0.3, 0.15, 0.3, 90), "indie": (0.55, 0.55, 0.45, 115),
    "hip-hop": (0.8, 0.65, 0.5, 95),
}
rows = []
for g, (d, e, v, t) in GENRES.items():
    for i in range(300):
        rows.append({
            "track_id": f"{g[:3]}{i:05d}{rng.integers(1e6):06d}",
            "track_name": f"{g.title()} Track {i + 1}",
            "artist_name": f"{g.title()} Artist {i % 40 + 1}",
            "album_name": f"{g.title()} Album {i % 60 + 1}",
            "album_cover_url": f"https://picsum.photos/seed/{g}{i}/300",
            "danceability": float(np.clip(rng.normal(d, 0.12), 0, 1)),
            "energy": float(np.clip(rng.normal(e, 0.15), 0, 1)),
            "valence": float(np.clip(rng.normal(v, 0.2), 0, 1)),
            "tempo": float(np.clip(rng.normal(t, 15), 50, 200)),
            "genre": g,
        })
out = Path(__file__).resolve().parent.parent / "data" / "spotify_tracks.parquet"
pd.DataFrame(rows).to_parquet(out, index=False)
print(f"{len(rows)} faixas salvas em {out}")
