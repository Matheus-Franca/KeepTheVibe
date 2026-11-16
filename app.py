"""KeepTheVibe - aplicação Streamlit principal."""
from html import escape
import os
import pandas as pd
import streamlit as st

from src import auth
from src.api_spotify import SpotifyAPIError, create_playlist, get_top_tracks, get_track_covers, get_user
from src.demo import create_demo_playlist, get_demo_top_tracks, load_demo_dataset
from src.recommender import CONTEXT_TAGS, VibeRecommender, load_dataset

DEMO_MODE = os.getenv("KTV_DEMO_MODE", "").strip().lower() in {"1", "true", "yes", "on"}

st.set_page_config(page_title="KeepTheVibe", page_icon="🎧", layout="wide")
st.markdown("""
<style>
.ktv-title{font-size:3.2rem;font-weight:800;letter-spacing:-.03em;margin:0}
.ktv-title span{color:#1DB954}
.ktv-sub{color:#A0A3AD;font-size:1.1rem}
.ktv-card{background:#181A20;border-radius:14px;padding:10px;margin-bottom:14px}
.ktv-card img{width:100%;border-radius:10px;aspect-ratio:1;object-fit:cover}
.ktv-card b{display:block;margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ktv-card small{color:#A0A3AD}
</style>""", unsafe_allow_html=True)


@st.cache_resource
def get_engine(demo_mode: bool = False) -> VibeRecommender:
    dataset = load_demo_dataset() if demo_mode else load_dataset()
    return VibeRecommender(dataset)


def brand():
    st.markdown('<p class="ktv-title">Keep<span>The</span>Vibe</p>', unsafe_allow_html=True)


if DEMO_MODE:
    token = None
    st.session_state["display_name"] = "Demonstração local"
else:
    # ---------- Tela de entrada (RF01) ----------
    auth.handle_callback()
    token = auth.ensure_valid_token()

    if not token:
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.write(""); st.write("")
            brand()
            st.markdown('<p class="ktv-sub">Playlists que acompanham a sua vibe do momento — não a média do algoritmo. '
                        'Ajuste energia e humor, escolha o contexto e salve direto no seu Spotify.</p>',
                        unsafe_allow_html=True)
            try:
                st.link_button("🎧 Conectar com Spotify", auth.get_login_url(), type="primary", use_container_width=True)
            except KeyError:
                st.error("Credenciais ausentes. Configure .streamlit/secrets.toml (veja o README).")
        st.stop()

    if "user_id" not in st.session_state:
        try:
            user = get_user(token)
            st.session_state["user_id"] = user["id"]
            st.session_state["display_name"] = user.get("display_name") or user["id"]
        except SpotifyAPIError as e:
            st.error(str(e)); auth.logout(); st.stop()

if DEMO_MODE:
    st.info("Modo de demonstração: faixas e playlists são fictícias e ficam apenas nesta sessão.")

engine = get_engine(DEMO_MODE)
df = engine.df

# ---------- Sidebar: modo + vibe (RF02/RF03) ----------
with st.sidebar:
    brand()
    if DEMO_MODE:
        st.caption("Modo de demonstração")
    else:
        st.caption(f"Conectado como **{st.session_state['display_name']}**")
    mode = st.radio("Modo de recomendação", ["Modo 1: Análise de Perfil", "Modo 2: Seleção Direta"])
    st.divider()
    st.subheader("Vibe do momento")
    energy = st.slider("Energia", 0.0, 1.0, 0.5, 0.05, help="Calmo ← → Agitado")
    st.caption("Calmo ⟵⟶ Agitado")
    valence = st.slider("Valência / Humor", 0.0, 1.0, 0.5, 0.05)
    st.caption("Melancólico ⟵⟶ Contagiante")
    tags = st.multiselect("Tags de contexto", list(CONTEXT_TAGS))
    n_tracks = st.slider("Tamanho da playlist", 10, 50, 20, 5)
    st.divider()
    if st.button("Limpar sessão demo" if DEMO_MODE else "Sair", use_container_width=True):
        auth.logout()
        st.session_state.pop("demo_playlist", None)
        st.rerun()

# ---------- Área central ----------
seed_ids, seed_artists, can_generate = [], [], True

if mode.startswith("Modo 1"):
    st.header("Seu perfil recente")
    if "top_tracks" not in st.session_state:
        if DEMO_MODE:
            st.session_state["top_tracks"] = get_demo_top_tracks(df)
        else:
            try:
                st.session_state["top_tracks"] = get_top_tracks(token)
            except SpotifyAPIError as e:
                st.error(str(e)); st.session_state["top_tracks"] = []
    top = st.session_state["top_tracks"]
    if top:
        cols = st.columns(5)
        for i, t in enumerate(top[:10]):
            with cols[i % 5]:
                cover = (f'<img src="{escape(t["album_cover_url"], quote=True)}"/>'
                         if t["album_cover_url"] else "")
                st.markdown(f'<div class="ktv-card">{cover}'
                            f'<b>{escape(t["track_name"])}</b><small>{escape(t["artist_name"])}</small></div>',
                            unsafe_allow_html=True)
        seed_ids = [t["track_id"] for t in top]
        seed_artists = [t["artist_name"] for t in top]
        if engine.seed_vector(seed_ids, seed_artists) is None:
            st.info("Suas top tracks não estão no dataset local — a recomendação usará apenas os controles de vibe.")
    else:
        st.info("Não encontramos top tracks suficientes. A recomendação usará apenas os controles de vibe.")
else:
    st.header("Escolha de 1 a 3 músicas base")
    catalog = df.dropna(subset=["track_name", "artists"])
    labels = (catalog["track_name"] + " — " + catalog["artists"]).to_dict()

    picked = st.multiselect(
        "Buscar no catálogo",
        options=catalog.index.tolist(),
        format_func=lambda i: labels[i],
        max_selections=3,
        placeholder="Digite o nome da música ou artista",
    )
    seed_ids = catalog.loc[picked, "track_id"].tolist()
    can_generate = 1 <= len(seed_ids) <= 3  # RN05
    if not can_generate:
        st.caption("Selecione ao menos 1 música para habilitar a geração.")

if st.button("✨ Gerar Playlist", type="primary", disabled=not can_generate):
    seed = engine.seed_vector(seed_ids, seed_artists)
    target, weights = engine.build_query(seed, energy, valence, tags)
    results = engine.recommend(target, weights, n=n_tracks, exclude_ids=seed_ids)
    st.session_state["recommendation_results"] = results
    if DEMO_MODE:
        st.session_state["spotify_track_metadata"] = {}
    else:
        covers, failed_cover_ids = get_track_covers(results["track_id"].astype(str).tolist())
        st.session_state["spotify_track_metadata"] = {
            track_id: {"album_cover_url": cover_url}
            for track_id, cover_url in covers.items()
        }
        if failed_cover_ids:
            st.warning(f"Não foi possível carregar a capa de {len(failed_cover_ids)} faixa(s).")
    st.session_state["vibe_label"] = " + ".join(tags) or f"E{int(energy*100)} V{int(valence*100)}"
    st.session_state.pop("playlist_url", None)
    st.session_state.pop("demo_playlist", None)

# ---------- Resultados (RF04/RF05) ----------
res: pd.DataFrame | None = st.session_state.get("recommendation_results")
if res is not None and not res.empty:
    st.divider()
    head, act = st.columns([3, 1])
    head.subheader(f"Sua playlist · {len(res)} faixas")
    with act:
        save_label = "💾 Criar playlist demo" if DEMO_MODE else "💾 Salvar no Spotify"
        if st.button(save_label, type="primary", use_container_width=True):
            if DEMO_MODE:
                st.session_state["demo_playlist"] = create_demo_playlist(
                    res, st.session_state.get("vibe_label", ""))
            else:
                with st.spinner("Criando playlist..."):
                    try:
                        st.session_state["playlist_url"] = create_playlist(
                            token, res["track_id"].tolist(),
                            st.session_state.get("vibe_label", ""))
                    except SpotifyAPIError as e:
                        st.error(str(e))  # RN04

    if DEMO_MODE:
        if playlist := st.session_state.get("demo_playlist"):
            st.success("Playlist criada no modo demo e guardada nesta sessão.")
            st.caption(f'{playlist["name"]} · {len(playlist["tracks"])} faixas fictícias')
    elif url := st.session_state.get("playlist_url"):
        st.success("Playlist salva na sua conta!")
        st.link_button("Abrir no Spotify", url)

    cols = st.columns(5)
    track_metadata = st.session_state.get("spotify_track_metadata", {})
    for i, r in res.iterrows():
        with cols[i % 5]:
            spotify_data = track_metadata.get(r["track_id"], {})
            local_track_name = r.get("track_name")
            local_artists = r.get("artists", r.get("artist_name"))
            local_genre = r.get("track_genre", r.get("genre"))
            track_name = spotify_data.get("track_name") or (
                "" if pd.isna(local_track_name) else str(local_track_name)
            ) or "Faixa sem título"
            artists = spotify_data.get("artists") or (
                "" if pd.isna(local_artists) else str(local_artists)
            ) or "Artista desconhecido"
            genre = (
                "Gênero não disponível"
                if pd.isna(local_genre) or not str(local_genre).strip()
                else str(local_genre)
            )
            cover_url = spotify_data.get("album_cover_url", "")
            if cover_url:
                st.image(cover_url, use_container_width=True)
            else:
                st.caption("Capa fictícia indisponível" if DEMO_MODE else "Capa não disponível no Spotify")
            track_details = f'<small>{r["similarity"]:.0%}'
            if DEMO_MODE:
                track_details += " · Demonstração</small>"
            else:
                track_details += (
                    f' · <a href="https://open.spotify.com/track/{escape(str(r["track_id"]), quote=True)}" '
                    f'target="_blank" rel="noopener noreferrer">Abrir ↗</a></small>'
                )
            st.markdown(
                f'<div class="ktv-card"><b>{escape(track_name)}</b>'
                f'<small>{escape(artists)} · {escape(genre)}</small><br>'
                f'{track_details}</div>', unsafe_allow_html=True)
    st.caption("Quer ajustar? Mude os controles na barra lateral e clique em Gerar Playlist de novo.")
