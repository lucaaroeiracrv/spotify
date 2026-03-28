# 🎵 Spotify Playlist Categorizer

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Spotify](https://img.shields.io/badge/API-Spotify-black)

Organize qualquer playlist do Spotify por **gênero musical** e, se quiser, crie **automaticamente uma playlist por gênero** diretamente na sua conta Spotify. Fluxo 100% local: o script abre o navegador, você autoriza e ele captura o retorno via callback em `http://127.0.0.1:8888/callback`.

---

## 🔖 Funcionalidades

- 🎵 Extrai músicas de uma playlist (pública ou privada, se autorizado).
- 🧠 Agrupa por gêneros com barra de progresso durante a coleta.
- 📋 Copia a lista categorizada para a área de transferência.
- 💾 Salva a lista em `playlists/<nome_da_playlist>.txt`.
- 🪄 Cria automaticamente playlists no Spotify: uma por gênero.

---

## ✅ Pré-requisitos

- Python 3.10 ou superior
- Bibliotecas: `requests`, `pyperclip` e `python-dotenv`

Instale as dependências:

```powershell
pip install -r requirements.txt
