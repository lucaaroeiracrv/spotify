
# 🎵 Spotify Playlist Categorizer

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Spotify](https://img.shields.io/badge/API-Spotify-black)

Este script em Python permite que você extraia as músicas de uma playlist do Spotify e as organize por **gênero musical**. Além disso, você pode copiar automaticamente a lista para sua área de transferência.

---

## 🔖 Funcionalidades

- 🎵 Extrai músicas de uma playlist pública do Spotify.
- 📝 Organiza as músicas por gênero musical.
- 📈 Exibe barra de progresso durante a coleta das músicas.
- 📄 Copia a lista para a área de transferência (opcional).

---

## ✅ Pré-requisitos

- Python 3.10 ou superior instalado
- Bibliotecas `requests` e `pyperclip`

Instale as dependências com:

```bash
pip install requests pyperclip
```

---

## 🔐 Como obter o token do Spotify

1. Acesse: [Spotify Developer Console](https://developer.spotify.com/console/get-playlist-tracks/)
2. Clique em **"Get Token"** no canto superior direito.
3. Marque as permissões:
   - `playlist-read-private` (caso queira playlists privadas)
   - Ou apenas clique em **"Request Token"** para playlists públicas.
4. Copie o token gerado.
5. No código, substitua o valor da variável `TOKEN`:

```python
TOKEN = 'seu_token_aqui'
```

🚨 **Atenção:** o token expira após um tempo. Gere um novo se necessário.

---

## 🚀 Como usar

1. Clone este repositório ou copie o código para sua máquina.
2. Instale as dependências.
3. Execute o script no terminal:

```bash
python spotify-playlist-categorizer.py
```

4. Cole o link da playlist do Spotify quando solicitado.
5. Aguarde a barra de progresso.
6. Escolha se deseja copiar a lista para a área de transferência.

---

## 💡 Ideias para melhorias

- 💾 Salvar lista em .txt ou .csv
- 🔍 Filtrar por gênero
- 👥 Mostrar todos os artistas
- ℹ️ Mostrar mais informações (álbum, duração etc.)
- 🖥️ Criar uma interface gráfica
- 📊 Exportar para Excel
- 🔑 Autenticação OAuth para buscar playlists privadas
- 🎤 Buscar letras das músicas
- ❌ Remover músicas duplicadas
- 🧠 Agrupar gêneros semelhantes

---

## ✉️ Contato

Dúvidas, sugestões ou contribuições? Fique à vontade para abrir uma [Issue](https://github.com/seu-usuario/seu-repositorio/issues) ou enviar um PR!

