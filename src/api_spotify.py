"""Comunicação com a API e oEmbed do Spotify."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import requests
import spotipy


class SpotifyAPIError(Exception):
    """Erro amigável para exibir na UI (RN04)."""


def client(token: str) -> spotipy.Spotify:
    return spotipy.Spotify(auth=token, requests_timeout=10, retries=2)


def get_user(token: str) -> dict:
    try:
        return client(token).current_user()
    except spotipy.SpotifyException as exc:
        raise SpotifyAPIError(_friendly(exc)) from exc


def get_top_tracks(token: str, limit: int = 20, time_range: str = "short_term") -> list[dict]:
    try:
        items = client(token).current_user_top_tracks(limit=limit, time_range=time_range)["items"]
    except spotipy.SpotifyException as exc:
        raise SpotifyAPIError(_friendly(exc)) from exc
    return [
        {
            "track_id": t["id"],
            "track_name": t["name"],
            "artist_name": t["artists"][0]["name"] if t["artists"] else "",
            "album_cover_url": (t["album"]["images"] or [{}])[0].get("url", ""),
        }
        for t in items
    ]


def get_track_covers(track_ids: list[str]) -> tuple[dict[str, str], list[str]]:
    """Obtém as capas pelo oEmbed oficial do Spotify, sem usar o endpoint /tracks depreciado."""
    if not track_ids:
        return {}, []

    def fetch_cover(track_id: str) -> tuple[str, str | None]:
        try:
            response = requests.get(
                "https://open.spotify.com/oembed",
                params={"url": f"https://open.spotify.com/track/{track_id}"},
                timeout=8,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return track_id, None
        cover_url = payload.get("thumbnail_url") if isinstance(payload, dict) else None
        return track_id, cover_url

    covers = {}
    failed_ids = []
    with ThreadPoolExecutor(max_workers=min(5, len(track_ids))) as executor:
        for track_id, cover_url in executor.map(fetch_cover, track_ids):
            if cover_url:
                covers[track_id] = cover_url
            else:
                failed_ids.append(track_id)
    return covers, failed_ids


def create_playlist(token: str, user_id: str, track_ids: list[str], vibe_label: str = "") -> str:
    """Cria a playlist (prefixo KeepTheVibe), adiciona faixas em lotes de 100 e retorna a URL."""
    sp = client(token)
    name = f"KeepTheVibe · {vibe_label or 'Mix'} · {datetime.now():%d/%m %H:%M}"
    try:
        pl = sp.user_playlist_create(
            user_id, name, public=False,
            description="Gerada pelo KeepTheVibe — recomendação baseada na sua vibe do momento.",
        )
        uris = [f"spotify:track:{tid}" for tid in track_ids]
        for i in range(0, len(uris), 100):
            sp.playlist_add_items(pl["id"], uris[i:i + 100])
    except spotipy.SpotifyException as exc:
        raise SpotifyAPIError(_friendly(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - rede/timeout
        raise SpotifyAPIError("Não foi possível falar com o Spotify agora. Tente novamente.") from exc
    return pl["external_urls"]["spotify"]


def _friendly(exc: spotipy.SpotifyException) -> str:
    if exc.http_status == 429:
        return "O Spotify está limitando as requisições (rate limit). Aguarde alguns segundos e tente de novo."
    if exc.http_status in (401, 403):
        return "Sua sessão do Spotify expirou ou não tem permissão. Conecte-se novamente."
    return f"Erro na API do Spotify ({exc.http_status})."
