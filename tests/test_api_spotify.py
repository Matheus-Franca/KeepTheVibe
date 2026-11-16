from src import api_spotify


def test_create_playlist_uses_current_user_endpoint_and_adds_tracks(monkeypatch):
    class FakeSpotify:
        def __init__(self):
            self.created = None
            self.added = []

        def current_user_playlist_create(self, name, public, description):
            self.created = (name, public, description)
            return {"id": "playlist-id", "external_urls": {"spotify": "https://open.spotify.com/playlist/playlist-id"}}

        def playlist_add_items(self, playlist_id, items):
            self.added.append((playlist_id, items))

    fake_spotify = FakeSpotify()
    monkeypatch.setattr(api_spotify, "client", lambda token: fake_spotify)

    url = api_spotify.create_playlist("token", ["track-1", "track-2"], "Focus")

    assert fake_spotify.created[0].startswith("KeepTheVibe · Focus · ")
    assert fake_spotify.created[1:] == (
        False,
        "Gerada pelo KeepTheVibe — recomendação baseada na sua vibe do momento.",
    )
    assert fake_spotify.added == [
        ("playlist-id", ["spotify:track:track-1", "spotify:track:track-2"]),
    ]
    assert url == "https://open.spotify.com/playlist/playlist-id"


def test_get_track_covers_uses_spotify_oembed(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"thumbnail_url": "https://i.scdn.co/image/cover"}

    calls = []

    def fake_get(url, params, timeout):
        calls.append((url, params, timeout))
        return FakeResponse()

    monkeypatch.setattr(api_spotify.requests, "get", fake_get)

    covers, failed_ids = api_spotify.get_track_covers(["track-id"])

    assert calls == [(
        "https://open.spotify.com/oembed",
        {"url": "https://open.spotify.com/track/track-id"},
        8,
    )]
    assert covers == {"track-id": "https://i.scdn.co/image/cover"}
    assert failed_ids == []


def test_get_track_covers_reports_unavailable_covers(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            raise api_spotify.requests.HTTPError("not found")

    monkeypatch.setattr(api_spotify.requests, "get", lambda *args, **kwargs: FakeResponse())

    covers, failed_ids = api_spotify.get_track_covers(["bad-id"])

    assert covers == {}
    assert failed_ids == ["bad-id"]
