# KeepTheVibe

Aplicação Streamlit que recomenda músicas de acordo com a energia, o humor e o contexto escolhidos e permite salvar a seleção como playlist no Spotify.

## Clonar e executar localmente

Pré-requisitos: Git e Python 3.10 ou superior.

```bash
git clone https://github.com/Matheus-Franca/KeepTheVibe.git
cd KeepTheVibe
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS ou Linux
source .venv/bin/activate
```

Instale as dependências e execute os testes:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

Para iniciar a aplicação localmente:

```bash
streamlit run app.py
```

## Configurar o Spotify

1. Crie uma aplicação em [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Em **Redirect URIs**, adicione `http://localhost:8501` para execução local.
3. Crie `.streamlit/secrets.toml` localmente com as credenciais da aplicação:

   ```toml
   [spotify]
   client_id = "SEU_CLIENT_ID"
   client_secret = "SEU_CLIENT_SECRET"
   redirect_uri = "http://localhost:8501"
   ```

4. No modo de desenvolvimento do Spotify, adicione em **User Management** os usuários que poderão autenticar na aplicação.

Não publique nem envie `secrets.toml` ao GitHub. Esse arquivo já está listado no `.gitignore`.

## Dataset

A aplicação carrega `data/spotify_tracks.parquet` em tempo de execução. O arquivo precisa estar presente no repositório e conter os dados usados pelo recomendador, incluindo `track_id`, `artists`, `danceability`, `energy`, `valence` e `tempo`. Para mostrar os detalhes das faixas, também são usadas colunas como `track_name` e `track_genre`.

Antes de publicar, confirme que o dataset contém faixas e IDs válidos do Spotify. O arquivo de dados deve ser incluído no GitHub para que o Streamlit Community Cloud possa carregá-lo durante o deploy.

## Deploy no Streamlit Community Cloud

1. Envie o projeto para um repositório GitHub e confirme que ele inclui `app.py`, `requirements.txt` e `data/spotify_tracks.parquet`.
2. Acesse [share.streamlit.io](https://share.streamlit.io/), entre com sua conta GitHub e escolha **Create app**.
3. Selecione o repositório `Matheus-Franca/KeepTheVibe`, a branch desejada e `app.py` como arquivo principal.
4. Crie o app e anote a URL pública gerada pelo Streamlit.
5. No Spotify Developer Dashboard, adicione essa URL como **Redirect URI**. Use exatamente o endereço do app, por exemplo `https://nome-do-app.streamlit.app`.
6. Nas configurações do app no Streamlit Community Cloud, abra **Settings → Secrets** e informe as credenciais em formato TOML:

   ```toml
   [spotify]
   client_id = "SEU_CLIENT_ID"
   client_secret = "SEU_CLIENT_SECRET"
   redirect_uri = "https://nome-do-app.streamlit.app"
   ```

7. Salve as configurações e reinicie o app, se necessário. O Streamlit instala as dependências listadas em `requirements.txt` durante o deploy.

O endereço configurado como `redirect_uri` precisa ser idêntico ao registrado no Spotify Developer Dashboard. Para testar o app publicado, a conta Spotify também precisa estar autorizada no modo de desenvolvimento da aplicação.
