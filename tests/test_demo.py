from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src import api_spotify, auth
from src.demo import create_demo_playlist, load_demo_dataset
from src.recommender import VibeRecommender


def test_demo_data_generates_recommendations_with_fictional_tracks():
    dataset = load_demo_dataset()
    engine = VibeRecommender(dataset)
    target, weights = engine.build_query(None, energy=0.8, valence=0.7)

    results = engine.recommend(target, weights, n=10)

    assert not results.empty
    assert results["track_id"].str.startswith("demo-track-").all()
    assert results["track_name"].str.startswith("Faixa Demo ").all()


def test_demo_playlist_keeps_results_in_a_local_playlist_record():
    dataset = load_demo_dataset()
    playlist = create_demo_playlist(dataset.head(3), "Foco")

    assert playlist["name"] == "KeepTheVibe Demo · Foco"
    assert len(playlist["tracks"]) == 3
    assert playlist["tracks"][0]["track_id"].startswith("demo-track-")


def test_demo_ui_generates_and_saves_without_spotify(monkeypatch):
    monkeypatch.setenv("KTV_DEMO_MODE", "1")
    for module, function_names in (
        (auth, ("handle_callback", "ensure_valid_token")),
        (api_spotify, ("get_user", "get_top_tracks", "get_track_covers", "create_playlist")),
    ):
        for function_name in function_names:
            monkeypatch.setattr(
                module,
                function_name,
                lambda *args, **kwargs: pytest.fail("Spotify calls must not run in demo mode"),
            )

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path, default_timeout=20).run()
    assert not app.exception

    next(button for button in app.button if "Gerar Playlist" in button.label).click()
    app.run()
    assert not app.exception

    next(button for button in app.button if "Criar playlist demo" in button.label).click()
    app.run()

    assert not app.exception
    playlist = app.session_state["demo_playlist"]
    assert len(playlist["tracks"]) == 20
    assert all(track["track_id"].startswith("demo-track-") for track in playlist["tracks"])
    assert any("Playlist criada no modo demo" in message.value for message in app.success)
