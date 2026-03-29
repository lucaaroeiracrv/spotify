# 🎵 Spotify Playlist Categorizer

> **Projeto acadêmico desenvolvido para fins de estudo, aprendizado e automação utilizando a API do Spotify.**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Spotify](https://img.shields.io/badge/API-Spotify-black)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-yellow)
![Projeto](https://img.shields.io/badge/Projeto-Acadêmico-purple)

---

## 👥 Integrantes

- **Luca Aroeira**
- **Diego Duque**
- **Kaun Silva**

---

## 📖 Sobre o projeto

O **Spotify Playlist Categorizer** é uma aplicação em Python que organiza playlists do Spotify por **gênero musical** e permite automatizar a criação de playlists separadas na conta do usuário.

Este projeto foi desenvolvido com finalidade acadêmica, aplicando conceitos como:

- Consumo de API (Spotify API)
- Autenticação OAuth
- Automação de tarefas
- Manipulação de dados
- Organização e boas práticas em Python

---

## ✨ Funcionalidades

- Autenticação com a API do Spotify  
- Leitura de playlists  
- Classificação de músicas por gênero  
- Exportação para arquivo `.txt`  
- Cópia para área de transferência  
- Criação automática de playlists no Spotify  

---

## ✅ Pré-requisitos

Antes de começar, você precisa ter:

- Python **3.10 ou superior**
- Bibliotecas:
  - `requests`
  - `pyperclip`
  - `python-dotenv`

### Instalação das dependências:

```bash
pip install -r requirements.txt
```

Ou manualmente:

```bash
pip install requests pyperclip python-dotenv
```

---

## 🚀 Como executar

### 1. Clone o repositório

```bash
git clone <seu_repositorio>
cd spotify
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure o Spotify

1. Acesse: https://developer.spotify.com/dashboard  
2. Clique em **Create an App**  
3. Crie o aplicativo  
4. Adicione a Redirect URI:

```
http://127.0.0.1:8888/callback
```

5. Copie:
- Client ID  
- Client Secret  

---

### 4. Crie o arquivo `.env`

```env
SPOTIFY_CLIENT_ID=SEU_CLIENT_ID
SPOTIFY_CLIENT_SECRET=SEU_CLIENT_SECRET
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

> ⚠️ Nunca envie o `.env` para o GitHub.

---

### 5. Execute o projeto

```bash
python spotify-playlist-categorizer.py
```

---

## 🔐 Configuração e segurança

- As credenciais ficam no `.env`
- O `.env` está no `.gitignore`
- Tokens não são salvos em disco
- Autenticação feita via OAuth
- Escopos utilizados:

```
playlist-modify-public playlist-modify-private
```

---

## 🧪 Exemplo de uso

```
=== SPOTIFY PLAYLIST ORGANIZER ===
Autorização necessária. O navegador será aberto.
Aguardando autorização...

✅ Autenticado!

Cole o link da playlist:
https://open.spotify.com/playlist/...

Escolha uma opção:
1 - Copiar
2 - Salvar
3 - Copiar + Salvar
4 - Criar playlists por gênero

🎵 Criando playlists...
✅ Concluído!
```

---

## 📌 Como usar

1. Execute o script  
2. Autorize no navegador  
3. Cole o link da playlist  
4. Escolha a ação desejada  

---

## 🧰 Solução de problemas

| Problema | Solução |
|----------|--------|
| INVALID_CLIENT | Verifique a Redirect URI |
| Timeout | Porta 8888 pode estar ocupada |
| Erro 401 | Refaça a autenticação |
| Erro 429 | Aguarde e tente novamente |
| Módulos faltando | Rode `pip install -r requirements.txt` |

---

## 💡 Melhorias futuras

- Filtro de gêneros  
- Remoção de duplicatas  
- Exportação para Excel/CSV  
- Interface gráfica  
- Melhor categorização musical  

---

## 📂 Estrutura do projeto

```
spotify/
├── spotify-playlist-categorizer.py
├── requirements.txt
├── .env.example
├── README.md
```

---

## ✉️ Considerações finais

Este projeto foi desenvolvido com fins acadêmicos, com foco em aprendizado prático de integração com APIs, automação e boas práticas de desenvolvimento.

Sinta-se à vontade para contribuir ou adaptar o projeto para seus próprios estudos 🚀
