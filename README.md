# 🎵 Spotify Playlist Categorizer

Organizador de playlists do Spotify com **classificação por gênero dominante**, exportação em `.txt`, cópia para a área de transferência e criação automática de playlists separadas por estilo.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Spotify](https://img.shields.io/badge/API-Spotify-black)
![TensorFlow](https://img.shields.io/badge/ML-TensorFlow-orange)
![Status](https://img.shields.io/badge/Status-Ativo-green)

---

## 👥 Integrantes

- **Luca Aroeira**
- **Diego Duque**
- **Kauan Silva**

---

## 📖 Sobre o projeto

O projeto lê uma playlist do Spotify, classifica cada música em um **gênero principal** e organiza o resultado em blocos como `Pop`, `Rock`, `Metal`, `Trap`, `MPB`, `Sertanejo` etc.

A classificação atual usa uma abordagem **híbrida**:

1. **biblioteca de referências** por gênero;
2. **metadados do Spotify** e contexto do artista;
3. **tags externas opcionais** (Last.fm, Hugging Face, OpenAI);
4. **aprendizado local incremental** com TensorFlow.

> O foco do projeto é escolher **apenas o gênero mais provável** para cada faixa.

---

## ✨ Funcionalidades

- autenticação OAuth com Spotify;
- leitura de playlists públicas/privadas autorizadas;
- classificação híbrida por gênero;
- cache local de previsões;
- aprendizado incremental com TensorFlow;
- exportação para `.txt`;
- cópia da lista para a área de transferência;
- criação automática de playlists no Spotify por categoria;
- geração de uma playlist única de teste com `gerarPlaylistTeste.py`.

---

## ✅ Requisitos

- Python **3.10+**
- dependências em `requirements.txt`

Instalação:

```bash
pip install -r requirements.txt
```

Dependências atuais:

- `requests`
- `pyperclip`
- `python-dotenv`
- `tensorflow`

---

## ⚙️ Configuração

### 1. Criar app no Spotify

Acesse o dashboard:

```text
https://developer.spotify.com/dashboard
```

Crie um app e configure a Redirect URI:

```text
http://127.0.0.1:8888/callback
```

### 2. Criar o `.env`

Use o `.env.example` como base:

```env
SPOTIFY_CLIENT_ID=SEU_CLIENT_ID_AQUI
SPOTIFY_CLIENT_SECRET=SEU_CLIENT_SECRET_AQUI
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

CLASSIFICATION_PROVIDER=auto
GENRE_AI_ALWAYS_ON=false
LASTFM_API_KEY=
HUGGINGFACE_API_KEY=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

> ⚠️ O arquivo `.env` não deve ser enviado para o GitHub.

---

## 🚀 Como executar

### Classificar uma playlist

```bash
python spotify-playlist-categorizer.py
```

Fluxo básico:

1. autorizar a conta no navegador;
2. colar o link da playlist;
3. ver as músicas agrupadas por gênero;
4. escolher entre copiar, salvar ou criar playlists no Spotify.

### Gerar playlist de teste

```bash
python gerarPlaylistTeste.py
```

Esse script autentica a conta e cria **uma playlist única** com as músicas de teste predefinidas no código.

---

## 🧠 Arquitetura da classificação

O núcleo do projeto está em `services/genre_classifier.py`.

### Fontes usadas pela classificação

- **`data/genre_reference_library.json`**  
  Base de músicas de referência por gênero.

- **Metadados do Spotify**  
  Gêneros do artista, nome da faixa, álbum e contexto.

- **APIs opcionais**  
  - Last.fm → tags musicais adicionais  
  - Hugging Face / OpenAI → classificação semântica complementar

- **Modelo local TensorFlow**  
  Aprende com exemplos confirmados e refina bordas difíceis como:
  - `Eletrônica` × `Pop`
  - `Rock` × `Metal`
  - `Boom Bap` × `Rap`
  - `Sertanejo` × `Sertanejo Universitário`

---

## 📂 Estrutura do projeto

```text
spotify/
├── spotify-playlist-categorizer.py   # script principal
├── gerarPlaylistTeste.py             # gera playlist única de teste
├── services/
│   ├── __init__.py
│   └── genre_classifier.py           # motor de classificação
├── data/
│   ├── genre_reference_library.json  # base de referência por gênero
│   ├── genre_learning_samples.json   # amostras para treino incremental
│   └── genre_prediction_cache.json   # cache local de previsões
├── models/
│   ├── genre_classifier.keras        # modelo TensorFlow treinado
│   └── genre_classifier_meta.json    # metadados do modelo
├── screens/
│   ├── auth_success.html
│   ├── auth_success.css
│   ├── auth_error.html
│   └── auth_error.css
├── requirements.txt
├── .env.example
├── README.md
└── explain.md                        # explicação de cada arquivo
```

---

## 📄 Arquivo extra de explicação

Foi criado um arquivo chamado **`explain.md`** com a função de cada arquivo e pasta do projeto.

---

## 🧪 Exemplo de uso

```text
Cole o link da playlist do Spotify:
https://open.spotify.com/playlist/...

Carregando músicas da playlist... Pronto!

-------------(POP)-------------
Flowers - Miley Cyrus
Roar - Katy Perry
...
```

---

## 🧰 Solução de problemas

| Problema | Possível solução |
|---|---|
| `INVALID_CLIENT` | confira `CLIENT_ID`, `CLIENT_SECRET` e Redirect URI |
| `401 Unauthorized` | refaça a autenticação |
| `429 Too Many Requests` | aguarde alguns segundos e tente de novo |
| porta `8888` ocupada | altere o callback no `.env` e no app do Spotify |
| erro ao salvar `.txt` | o nome da playlist é sanitizado automaticamente para Windows |
| dependências ausentes | rode `pip install -r requirements.txt` |

---

## 💡 Próximas melhorias possíveis

- adicionar novos gêneros como `Forró`, `Piseiro`, `Dancehall` e `Indie`;
- usar mais sinais de áudio (`preview_url`, BPM, energia, dançabilidade);
- exportar para CSV/Excel;
- criar interface gráfica.

---

## ✉️ Observação final

Este projeto é acadêmico, mas já está estruturado para estudo sério de:

- integração com APIs;
- autenticação OAuth;
- classificação híbrida por regras + IA;
- persistência local e treino incremental.

Se quiser expandir o projeto, o melhor ponto de entrada é `services/genre_classifier.py`.
