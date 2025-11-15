
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

## ✅ Pré‑requisitos

- Python 3.10 ou superior
- Bibliotecas: `requests` e `pyperclip`

Instale as dependências:

```powershell
pip install requests pyperclip
```

---

## ⚡ Guia rápido (5 passos)

1) No Dashboard do Spotify, crie um app e adicione o Redirect URI: `http://127.0.0.1:8888/callback`.
2) Abra o arquivo `spotify-playlist-categorizer.py` e preencha, no topo:
   ```python
   INLINE_CLIENT_ID = "SEU_CLIENT_ID"
   INLINE_CLIENT_SECRET = "SEU_CLIENT_SECRET"
   INLINE_REDIRECT_URI = "http://127.0.0.1:8888/callback"  # mantenha
   ```
   Observação: limpe esses valores antes de fazer commit (não versionar segredos).
3) Execute:
   ```powershell
   python spotify-playlist-categorizer.py
   ```
4) Autorize no navegador; a página mostrará “Autenticacao concluida!”.
5) Cole o link da playlist (ex.: `https://open.spotify.com/playlist/123...`) e escolha a opção desejada (copiar, salvar ou criar playlists por gênero).

---

## 🔐 Configuração do Spotify (rápida)

1) Crie um app no dashboard: https://developer.spotify.com/dashboard
- Em “Redirect URIs”, adicione: `http://127.0.0.1:8888/callback` e clique em Save.
- Copie o `Client ID` e o `Client Secret`.

2) Informe as credenciais diretamente no código (inline):

```python
INLINE_CLIENT_ID = "SEU_CLIENT_ID"
INLINE_CLIENT_SECRET = "SEU_CLIENT_SECRET"
INLINE_REDIRECT_URI = "http://127.0.0.1:8888/callback"  # mantenha
```

Importante: limpe esses valores antes de fazer commit.

Escopos usados: `playlist-modify-public playlist-modify-private`.

---

## 🚀 Como usar (passo a passo)

1) Configure as credenciais (onde substituir o quê):
    - Abra `spotify-playlist-categorizer.py` e, no topo, troque pelos seus valores do dashboard:
       ```python
       INLINE_CLIENT_ID = "SEU_CLIENT_ID"        # exemplo: 1a2b3c4d...
       INLINE_CLIENT_SECRET = "SEU_CLIENT_SECRET"# exemplo: abcd1234...
       INLINE_REDIRECT_URI = "http://127.0.0.1:8888/callback"  # não altere
       ```
       Mantenha a URL do Redirect exatamente igual. Limpe esses valores antes de commitar.

2) Rode o script:
   ```powershell
   python spotify-playlist-categorizer.py
   ```

3) Autorize no navegador:
   - O navegador abrirá com a página de autorização do Spotify.
   - Após autorizar, você verá “Autenticacao concluida!”; volte ao terminal.

4) Cole o link da playlist quando o terminal pedir:
   - Exemplo válido: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`

5) Escolha o que fazer com a lista categorizada:
   - 1: Copiar para a área de transferência
   - 2: Salvar em arquivo texto (`playlists/<nome>.txt`)
   - 3: Copiar + Salvar
   - 4: Criar playlists no Spotify (uma por gênero)

6) Se escolher criar playlists:
   - Prefixo (opcional): ex.: `[Rock]` (pressione Enter para deixar vazio)
   - Públicas? Digite `s` para públicas ou `n` para privadas

---

## 🧪 Exemplo de sessão (resumido)

```text
=== SPOTIFY PLAYLIST ORGANIZER ===
Autorização necessária. O navegador será aberto.
Aguardando autorização no navegador...
✅ Autenticado! User ID: 1234567890

Cole o link da playlist do Spotify: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
Carregando músicas: [==========================>         ] 65%
...

Escolha uma opção:
1 - Copiar lista
2 - Salvar em arquivo
3 - Copiar + Salvar
4 - Criar playlists no Spotify (uma por gênero)

Prefixo para as playlists (ex.: "[Rock]"): [Enter]
Playlists públicas? (s/n): s
```

---

## 🛠️ Dicas e observações

- O script usa um servidor local em `127.0.0.1:8888` para capturar o código OAuth.
- A correspondência de gênero é baseada nos gêneros do(s) artista(s) na API do Spotify; atualmente usa o primeiro artista da faixa.
- O script adiciona faixas em lotes de até 100 (limite da API).

---

## 🧯 Solução de problemas

- `INVALID_CLIENT` ou erro 400 ao trocar o código por token: verifique se a Redirect URI cadastrada no dashboard é exatamente `http://127.0.0.1:8888/callback`.
- Timeout aguardando autorização: finalize a autorização no navegador e confirme que a porta `8888` não está ocupada.
- Erro 401 em chamadas à API: refaça a autorização executando o script novamente.
- Erro 429 (rate limit): aguarde alguns segundos/minutos e tente novamente.
- Não consigo criar playlists: verifique os escopos `playlist-modify-public` e `playlist-modify-private` do app e a autorização concedida.
- App em modo “Development”: apenas usuários adicionados no dashboard poderão autorizar.

---

## 🔒 Segurança

- Não versione suas credenciais: limpe os valores inline antes de commit.
- O script não persiste tokens em disco.

---

## 💡 Ideias futuras

- Filtro de gêneros (incluir/excluir) antes de criar playlists.
- Remoção de duplicadas por gênero.
- Exportação para CSV/Excel.
- UI com Tkinter/PySimpleGUI.

---

## ✉️ Contato

Dúvidas ou sugestões? Abra uma Issue/PR neste repositório.

