# KeepTheVibe (MVP)

Playlists do Spotify guiadas pela sua vibe: Streamlit + Scikit-learn (similaridade de cosseno) sobre um dataset local.

## 1. Instalar
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Credenciais do Spotify
1. Crie um app em https://developer.spotify.com/dashboard
2. Em **Redirect URIs** adicione `http://localhost:8501` (e a URL do Streamlit Cloud, se publicar).
3. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha.
4. Em modo desenvolvimento, adicione seu e-mail em **User Management** no dashboard.

## 3. Dataset
O pacote inclui `data/spotify_tracks.parquet` **de exemplo (IDs sintéticos)**. Para recomendações e
exportação reais, substitua por um dataset com `track_id` reais do Spotify (ex.: Kaggle
"Spotify Tracks Dataset"), mantendo as colunas: `track_id, track_name, artist_name, album_name,
album_cover_url, danceability, energy, valence, tempo, genre`. Para regenerar o exemplo:
`python scripts/generate_sample_dataset.py`.

## 4. Rodar
```bash
streamlit run app.py
pytest
```

## Publicar (Streamlit Community Cloud)
Suba o repositório no GitHub, crie o app apontando para `app.py` e cole o conteúdo do
`secrets.toml` em **Settings → Secrets** (com `REDIRECT_URI` = URL pública do app).
