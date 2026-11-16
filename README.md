# KeepTheVibe

Aplicação Streamlit que recomenda músicas conforme energia, humor e contexto, com opção de salvar a seleção no Spotify.

## Clonar e testar localmente

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

Instale as dependências e execute os testes automatizados:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

## Executar no modo demo

O modo demo não requer conta ou credenciais do Spotify. Ele usa faixas fictícias, gera recomendações localmente e guarda a playlist somente na sessão atual. O salvamento é simulado: nenhuma playlist é enviada ao Spotify.

Ative o modo demo e inicie o app:

```powershell
# Windows (PowerShell)
$env:KTV_DEMO_MODE = "1"
streamlit run app.py
```

```bash
# macOS ou Linux
KTV_DEMO_MODE=1 streamlit run app.py
```

Sem `KTV_DEMO_MODE`, o app usa o fluxo normal de autenticação com o Spotify. Para esse fluxo, configure `.streamlit/secrets.toml` localmente:

```toml
[spotify]
client_id = "SEU_CLIENT_ID"
client_secret = "SEU_CLIENT_SECRET"
redirect_uri = "http://localhost:8501"
```

## Deploy no Streamlit Community Cloud

A aplicação foi implantada no Streamlit Community Cloud a partir do repositório GitHub, usando `app.py` como arquivo principal. As dependências são instaladas a partir de `requirements.txt`, e as credenciais ficam configuradas em **Settings → Secrets**, não no código.

Para as funcionalidades reais do Spotify — como carregar o perfil e salvar uma playlist — o usuário precisa entrar com uma conta Spotify autorizada para o app. Devido a aplicação estar no modo de desenvolvimento do Spotify, caso tenha interesse você pode solicitar o seu acesso via e-mail, mandando seu nome e o e-mail da sua conta spotify 


O modo demo descrito acima é destinado à execução local. Ele não cria playlists no Spotify; no deploy, o fluxo padrão exige autenticação e autorização da conta.
