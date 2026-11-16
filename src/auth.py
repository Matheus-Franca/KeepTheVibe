"""RF01 - Autenticação Spotify OAuth (credenciais lidas apenas de st.secrets, RN03)."""
import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler

SCOPES = "user-top-read playlist-modify-public playlist-modify-private"


def _oauth() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=st.secrets["spotify"]["client_id"],
        client_secret=st.secrets["spotify"]["client_secret"],
        redirect_uri=st.secrets["spotify"]["redirect_uri"],
        scope=SCOPES,
        cache_handler=MemoryCacheHandler(),  # RN01: nada persistido em disco
        show_dialog=True,
    )


def get_login_url() -> str:
    return _oauth().get_authorize_url()


def handle_callback() -> bool:
    """Troca o ?code= da URL por um token e guarda em st.session_state."""
    code = st.query_params.get("code")
    if not code or st.session_state.get("access_token"):
        return bool(st.session_state.get("access_token"))
    try:
        info = _oauth().get_access_token(code, as_dict=True, check_cache=False)
        st.session_state["access_token"] = info["access_token"]
        st.session_state["token_info"] = info
    except Exception as exc:  # noqa: BLE001
        st.error(f"Falha na autenticação com o Spotify: {exc}")
        return False
    finally:
        st.query_params.clear()
    return True


def ensure_valid_token() -> str | None:
    info = st.session_state.get("token_info")
    if not info:
        return None
    oauth = _oauth()
    if oauth.is_token_expired(info):
        try:
            info = oauth.refresh_access_token(info["refresh_token"])
            st.session_state["token_info"] = info
            st.session_state["access_token"] = info["access_token"]
        except Exception:  # noqa: BLE001
            logout()
            return None
    return st.session_state["access_token"]


def logout() -> None:
    for k in ("access_token", "token_info", "user_id", "recommendation_results", "top_tracks"):
        st.session_state.pop(k, None)
