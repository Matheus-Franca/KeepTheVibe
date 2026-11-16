"""Dados e operações locais do modo de demonstração."""
import pandas as pd


def load_demo_dataset() -> pd.DataFrame:
    genres = ["Pop Demo", "Rock Demo", "Eletrônica Demo", "Jazz Demo"]
    rows = []
    for index in range(40):
        rows.append({
            "track_id": f"demo-track-{index + 1:02d}",
            "track_name": f"Faixa Demo {index + 1:02d}",
            "artists": f"Artista Demo {index // 2 + 1:02d}",
            "album_name": f"Álbum Demo {index // 4 + 1:02d}",
            "album_cover_url": "",
            "danceability": round(0.2 + ((index * 13) % 70) / 100, 2),
            "energy": round(0.1 + ((index * 17) % 80) / 100, 2),
            "valence": round(0.1 + ((index * 29 + 7) % 80) / 100, 2),
            "tempo": float(70 + (index * 23) % 100),
            "track_genre": genres[index % len(genres)],
        })
    return pd.DataFrame(rows)


def get_demo_top_tracks(dataset: pd.DataFrame) -> list[dict]:
    return [
        {
            "track_id": row["track_id"],
            "track_name": row["track_name"],
            "artist_name": row["artists"],
            "album_cover_url": "",
        }
        for _, row in dataset.head(10).iterrows()
    ]


def create_demo_playlist(results: pd.DataFrame, vibe_label: str) -> dict:
    tracks = results[["track_id", "track_name", "artists", "track_genre"]].to_dict("records")
    return {
        "name": f"KeepTheVibe Demo · {vibe_label or 'Mix'}",
        "tracks": tracks,
    }
