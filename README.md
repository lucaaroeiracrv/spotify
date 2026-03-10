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
- Bibliotecas: `requests`, `pyperclip` e `python-dotenv`

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Ou manualmente:

```powershell
pip install requests pyperclip python-dotenv
```

---

## ⚡ Guia rápido (5 passos)

### Passo 1: Clonar e instalar dependências

```powershell
git clone <seu_repo>
cd spotify
pip install -r requirements.txt
```

### Passo 2: Configurar credenciais do Spotify

1) Crie um app no dashboard: https://developer.spotify.com/dashboard
   - Clique em "Create an App"
   - Aceite os termos e crie
   - Acesse as configurações e adicione em "Redirect URIs": `http://127.0.0.1:8888/callback`
   - Salve e copie seu **Client ID** e **Client Secret**

2) Abra o arquivo `.env.example` e veja o template

3) Crie um novo arquivo `.env` (já no `.gitignore`):
   ```
   SPOTIFY_CLIENT_ID=SEU_CLIENT_ID
   SPOTIFY_CLIENT_SECRET=SEU_CLIENT_SECRET
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

4) **NUNCA** faça commit deste arquivo. Ele está no `.gitignore`.

### Passo 3: Execute o script

```powershell
python spotify-playlist-categorizer.py
```

### Passo 4: Autorize no navegador
- O navegador abrirá automaticamente
- Após autorizar, você verá "Autenticacao concluida!"
- Volte ao terminal

### Passo 5: Cole o link da playlist
- Exemplo válido: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- Escolha uma opção (copiar, salvar ou criar playlists)

---

## 🔐 Configuração do Spotify (detalhado)

**Importante**: As credenciais sensíveis (Client ID, Client Secret) **não devem ser versionadas** no Git.

### Como configurar após clonar:

1) **Crie um app em**: https://developer.spotify.com/dashboard
   - Login com sua conta Spotify
   - Clique em "Create an App"
   - Aceite os termos
   - Copie o **Client ID** e **Client Secret**

2) **Configure a Redirect URI no dashboard**:
   - Vá para as configurações do seu app
   - Em "Redirect URIs", adicione: `http://127.0.0.1:8888/callback`
   - Clique em Save

3) **Crie o arquivo `.env`** na raiz do projeto:
   ```
   SPOTIFY_CLIENT_ID=abc123def456...
   SPOTIFY_CLIENT_SECRET=xyz789uvw012...
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

### Por que usar `.env`?

| Arquivo | Commit | Conteúdo |
|---------|--------|----------|
| `.env.example` | ✅ Sim | Template vazio (documentação) |
| `.env` | ❌ Não (`.gitignore`) | Suas credenciais reais |

**Fluxo de segurança:**
- Você clona o repo → recebe `.env.example`
- Você cria `.env` com suas credenciais pessoais
- Git ignora `.env` (`.gitignore`)
- Suas credenciais nunca são expostas

**Escopos usados**: `playlist-modify-public playlist-modify-private`

---

## 🚀 Como usar (passo a passo)

### Setup inicial (uma única vez):

1. **Clone e instale**:
   ```powershell
   git clone <seu_repositorio>
   cd spotify
   pip install -r requirements.txt
   ```

2. **Configure credenciais**:
   - Copie `.env.example` → `.env`
   - Preencha seu Client ID e Client Secret
   - **Não commit!** O arquivo está em `.gitignore`

3. **Execute o script**:
   ```powershell
   python spotify-playlist-categorizer.py
   ```

### Uso regular:

1. O navegador abre automaticamente com a página de autorização
2. Clique em "Authorize"
3. Você verá "Autenticacao concluida!" — volte ao terminal
4. Cole o link da playlist quando solicitado
5. Escolha a opção desejada:
   - **1**: Copiar lista para área de transferência
   - **2**: Salvar em arquivo (`playlists/<nome>.txt`)
   - **3**: Copiar + Salvar
   - **4**: Criar playlists no Spotify (uma por gênero)

---

## 🧪 Exemplo de sessão

```text
=== SPOTIFY PLAYLIST ORGANIZER ===
Autorização necessária. O navegador será aberto.
Aguardando autorização no navegador...
✅ Autenticado! User ID: 1234567890

Cole o link da playlist do Spotify: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
Carregando músicas: [==========================>         ] 65%

Escolha uma opção:
1 - Copiar lista completa (com categorias) para área de transferência
2 - Salvar lista em arquivo texto
3 - Copiar + Salvar
4 - Criar playlists no Spotify (uma para cada gênero)

Digite sua escolha: 4
Prefixo para as playlists (ex: "[Rock]", deixe vazio para sem prefixo): 
Playlists públicas? (s/n, padrão: n): s

🎵 Criando playlists no Spotify...
Criando playlist: Sertanejo (45 músicas)...
  ✅ Criada com sucesso!
Criando playlist: Rock (32 músicas)...
  ✅ Criada com sucesso!

🎉 Concluído! 2 playlists criadas no seu Spotify!
```

---

## ️ Dicas e observações

- O script usa um servidor local em `127.0.0.1:8888` para capturar o código OAuth.
- A correspondência de gênero é baseada nos gêneros do primeiro artista da faixa retornado pela API do Spotify.
- O script adiciona faixas em lotes de até 100 (limite da API).
- Tokens não são salvos em disco (gerados a cada execução).

---

## 🧯 Solução de problemas

| Problema | Solução |
|----------|---------|
| `INVALID_CLIENT` ou erro 400 | Verifique se a Redirect URI cadastrada é exatamente `http://127.0.0.1:8888/callback` |
| Timeout aguardando autorização | Confirme que a porta `8888` não está ocupada e finalize a autorização no navegador |
| Erro 401 em chamadas à API | Refaça a autorização executando o script novamente |
| Erro 429 (rate limit) | Aguarde alguns segundos/minutos e tente novamente |
| Não consigo criar playlists | Verifique os escopos e se você autorizou corretamente |
| App em modo "Development" | Apenas usuários adicionados no dashboard poderão autorizar |
| `ModuleNotFoundError: requests` | Execute `pip install -r requirements.txt` |

---

## 🔒 Segurança

- ✅ Suas credenciais ficam em `.env` (nunca em `.py`)
- ✅ O arquivo está em `.gitignore` e nunca será versionado
- ✅ O script não persiste tokens em disco
- ✅ Todos os tokens são gerados a cada execução
- ❌ Nunca comite `.env`

---

## 💡 Ideias futuras

- Filtro de gêneros (incluir/excluir) antes de criar playlists
- Remoção de duplicadas por gênero
- Exportação para CSV/Excel
- UI com Tkinter/PySimpleGUI
- Suporte a variáveis de ambiente (`.env`)

---

## ✉️ Contato

Dúvidas ou sugestões? Abra uma Issue/PR neste repositório.

