from src import api_spotify


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
