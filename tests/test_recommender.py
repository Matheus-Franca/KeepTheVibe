import numpy as np
import pandas as pd
from src.recommender import VibeRecommender


def make_df():
    rows = []
    for i, (e, v) in enumerate([(0.9, 0.9), (0.95, 0.85), (0.1, 0.1), (0.15, 0.2), (0.5, 0.5)]):
        rows.append(dict(track_id=f"t{i}", track_name=f"n{i}", artist_name=f"a{i}", album_name="x",
                         album_cover_url="", danceability=0.5, energy=e, valence=v, tempo=120.0, genre="g"))
    return pd.DataFrame(rows)


def test_high_energy_happy_vibe_ranks_high_tracks_first():
    eng = VibeRecommender(make_df())
    t, w = eng.build_query(None, energy=1.0, valence=1.0)
    assert set(eng.recommend(t, w, n=2)["track_id"]) == {"t0", "t1"}


def test_calm_sad_vibe_ranks_low_tracks_first():
    eng = VibeRecommender(make_df())
    t, w = eng.build_query(None, energy=0.0, valence=0.0)
    assert set(eng.recommend(t, w, n=2)["track_id"]) == {"t2", "t3"}


def test_seed_tracks_are_excluded():
    eng = VibeRecommender(make_df())
    seed = eng.seed_vector(["t0"])
    t, w = eng.build_query(seed, 0.9, 0.9)
    assert "t0" not in eng.recommend(t, w, n=5, exclude_ids=["t0"])["track_id"].tolist()
