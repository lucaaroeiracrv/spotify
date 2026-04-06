# Explain do projeto

Este arquivo resume **o que cada arquivo e pasta faz** dentro do projeto `spotify`.

---

## 📁 Raiz do projeto

### `spotify-playlist-categorizer.py`
Script principal do sistema.

Responsabilidades:
- autenticar no Spotify via OAuth;
- ler as músicas de uma playlist;
- chamar o classificador em `services/genre_classifier.py`;
- agrupar as músicas por gênero;
- exibir o resultado no terminal;
- copiar a lista para a área de transferência;
- salvar a lista em `.txt`;
- criar playlists por gênero na conta do usuário.

---

### `gerarPlaylistTeste.py`
Script auxiliar para montar **uma única playlist de teste** no Spotify usando listas fixas de músicas definidas no próprio arquivo.

Responsabilidades:
- autenticar no Spotify;
- buscar músicas pelo nome;
- juntar tudo em uma playlist única;
- abrir páginas locais de sucesso/erro no navegador.

---

### `README.md`
Documentação principal do projeto: instalação, configuração, execução e visão geral da arquitetura.

---

### `explain.md`
Este arquivo. Serve como guia rápido para entender a função de cada parte do código.

---

### `requirements.txt`
Lista de dependências Python do projeto.

Atualmente inclui:
- `requests`
- `pyperclip`
- `python-dotenv`
- `tensorflow`

---

### `.env.example`
Exemplo de variáveis de ambiente.

Mostra como configurar:
- credenciais do Spotify;
- provider de classificação;
- chaves opcionais de Last.fm, Hugging Face e OpenAI.

---

## 📁 Pasta `services/`

### `services/__init__.py`
Marca a pasta como pacote Python para permitir imports como:

```python
from services.genre_classifier import HybridGenreClassifier
```

### `services/genre_classifier.py`
É o **coração do projeto**.

Responsabilidades:
- normalizar rótulos canônicos (`Pop`, `Rock`, `Metal`, etc.);
- carregar a biblioteca de referências em `data/genre_reference_library.json`;
- aplicar regras e heurísticas de classificação;
- enriquecer a decisão com metadados do Spotify;
- usar Last.fm / Hugging Face / OpenAI quando disponíveis;
- manter cache de previsões;
- treinar e consultar o modelo local TensorFlow;
- decidir o gênero dominante final de cada música.

Em resumo: **é onde a inteligência da categorização mora**.

---

## 📁 Pasta `data/`

### `data/genre_reference_library.json`
Biblioteca manual de músicas de referência por gênero.

Uso:
- serve como base de comparação;
- ajuda a calibrar bordas difíceis;
- influencia regras, exemplos e classificações por referência.

---

### `data/genre_learning_samples.json`
Conjunto de amostras acumuladas para aprendizado incremental.

Uso:
- guarda exemplos já vistos/classificados;
- alimenta o treino do TensorFlow.

---

### `data/genre_prediction_cache.json`
Cache local das classificações já feitas.

Uso:
- evita reprocessar a mesma faixa toda vez;
- acelera execuções repetidas.

---

## 📁 Pasta `models/`

### `models/genre_classifier.keras`
Modelo TensorFlow salvo em disco.

Uso:
- guardar o aprendizado local do classificador;
- reaproveitar o modelo entre execuções.

### `models/genre_classifier_meta.json`
Metadados do modelo treinado.

Contém por exemplo:
- quantidade de amostras (`sample_count`);
- labels suportadas;
- versão do classificador;
- data da última atualização.

---

## 📁 Pasta `screens/`

Esses arquivos são usados nas telas exibidas pelo navegador durante a autenticação.

### `screens/auth_success.html`
Página mostrada quando a autorização com Spotify foi iniciada/concluída com sucesso.

### `screens/auth_success.css`
Estilo visual da tela de sucesso.

### `screens/auth_error.html`
Página mostrada quando ocorre algum erro na autenticação.

### `screens/auth_error.css`
Estilo visual da tela de erro.

---

## 🔄 Fluxo resumido do projeto

1. o usuário executa `spotify-playlist-categorizer.py`;
2. o script autentica no Spotify;
3. as músicas da playlist são carregadas;
4. cada música passa por `HybridGenreClassifier`;
5. o classificador consulta referências, regras, cache e modelo local;
6. o resultado é agrupado e mostrado ao usuário;
7. opcionalmente a lista é salva/copieda ou viram playlists novas.

---

## 🛠️ Onde mexer dependendo do objetivo

- **melhorar a classificação** → `services/genre_classifier.py`
- **adicionar/remover músicas de referência** → `data/genre_reference_library.json`
- **mudar o fluxo principal do programa** → `spotify-playlist-categorizer.py`
- **mudar a playlist de teste** → `gerarPlaylistTeste.py`
- **ajustar autenticação visual** → `screens/`
- **atualizar documentação** → `README.md` e `explain.md`

---

## ✅ Resumo final

Se você quiser entender o projeto rapidamente, leia nesta ordem:

1. `README.md`
2. `explain.md`
3. `spotify-playlist-categorizer.py`
4. `services/genre_classifier.py`

Isso já dá uma visão quase completa de como o sistema funciona.
