import requests
import pyperclip
import sys
import time
import os
from pathlib import Path
import webbrowser
import base64
from urllib.parse import urlencode, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import re
import unicodedata
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# CONFIGURAÇÃO
# As credenciais são lidas do arquivo .env
# Se .env não existir, o script pedirá para criar
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '').strip()
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '').strip()
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback').strip()

TOKEN = None
USER_ID = None
auth_code_received = None
auth_received_time = None
auth_status = 'idle'  # 'idle', 'pending', 'success', 'error'
auth_error_message = ''

# Network / retry settings
REQUEST_TIMEOUT = 10  # seconds for requests
MAX_RETRIES = 5
BACKOFF_FACTOR = 0.5

# Create a requests.Session with retries/backoff for resilient API calls
SESSION = None

def create_session():
    global SESSION
    if SESSION is not None:
        return SESSION
    session = requests.Session()
    try:
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD"]),
        )
    except TypeError:
        # older urllib3 uses 'method_whitelist'
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=frozenset(["GET", "POST", "PUT", "DELETE", "HEAD"]),
        )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    SESSION = session
    return SESSION


def request_with_retries(method, url, **kwargs):
    """Make HTTP request using the global session with retries and handle 429 Retry-After.

    Returns a requests.Response or None on unrecoverable error.
    """
    session = create_session()
    attempt = 0
    while attempt <= MAX_RETRIES:
        attempt += 1
        try:
            resp = session.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
        except requests.exceptions.RequestException as e:
            if attempt > MAX_RETRIES:
                print(f"Erro de conexão ({e}) ao acessar: {url}")
                return None
            sleep_time = BACKOFF_FACTOR * (2 ** (attempt - 1))
            time.sleep(sleep_time)
            continue

        # If rate limited, respect Retry-After if present
        if resp is not None and resp.status_code == 429:
            retry_after = resp.headers.get('Retry-After')
            try:
                wait = int(retry_after) if retry_after is not None else BACKOFF_FACTOR * (2 ** (attempt - 1))
            except Exception:
                wait = BACKOFF_FACTOR * (2 ** (attempt - 1))
            print(f"Recebi 429; aguardando {wait} segundos antes de tentar novamente...")
            time.sleep(wait)
            continue

        return resp
    return None

# Mapeamento de gêneros específicos para categorias principais
# Dica: adicione novos termos aqui conforme necessário
GENRE_KEYWORDS = {

    # =======================
    # SERTANEJO
    # =======================
    "Sertanejo Tradicional": {
        "sertanejo tradicional", "sertanejo raiz", "moda de viola",
        "modao", "modão", "viola caipira", "música caipira",
        "musica caipira", "sertanejo antigo", "folk brasileiro",
    },

    "Sertanejo Universitário": {
        "sertanejo universitário", "sertanejo universitario",
        "sertanejo pop",
    },

    "Sertanejo": {
        "sertanejo", "agronejo", "country brasileiro",
        "arrocha", "piseiro", "pisadinha", "forró", "forro",
        "brega", "tecnobrega", "seresta",
    },

    # =======================
    # SAMBA / PAGODE
    # =======================
    "Samba": {
        "samba", "samba carioca", "samba paulista", "samba raiz",
        "samba de roda", "samba-enredo", "samba de terreiro",
        "samba de gafieira", "axé", "axe",
    },

    "Pagode": {
        "pagode", "pagode romântico", "pagode romantico",
        "pagode sentimental", "pagode anos 90", "pagode moderno",
        "pagode baiano", "nova mpb", "mpb", "brazilian pop",
    },

    # =======================
    # RAP / TRAP / FUNK
    # =======================
    "Trap": {
        "trap", "brazilian trap", "trap brasileiro",
        "trap nacional", "trap funk", "drill", "drill brasileiro",
    },

    "Boom Bap": {
        "boom bap", "boom-bap", "old school rap",
        "classic hip hop", "brazilian hip hop",
    },

    "Funk": {
        "funk", "brazilian funk", "funk brasileiro",
        "funk carioca", "funk consciente", "funk melody",
        "funk pop", "funk de bh", "brega funk", "150 bpm",
    },

    # =======================
    # ROCK
    # =======================
    "Rock": {
        "rock", "alternative rock", "indie rock", "garage rock",
        "grunge", "hard rock", "classic rock", "psychedelic rock",
        "soft rock", "punk rock", "post-punk", "new wave",
    },

    "Rock Brasileiro": {
        "rock brasileiro", "rock nacional", "pop rock brasileiro",
        "indie brasileiro", "alternativo brasileiro",
    },

    # =======================
    # METAL
    # =======================
    "Metal": {
        "metal", "heavy metal", "thrash metal", "death metal",
        "black metal", "doom metal", "power metal", "nu metal",
        "metalcore", "deathcore", "industrial metal",
        "metal brasileiro",
    },

    # =======================
    # POP
    # =======================
    "Pop": {
        "pop", "dance pop", "electropop", "synthpop",
        "indie pop", "alt pop", "teen pop", "pop rock",
        "pop internacional",
    },

    # =======================
    # ELETRÔNICA
    # =======================
    "Eletrônica": {
        "electronic", "eletronica", "eletrônica", "edm",
        "house", "deep house", "tech house", "progressive house",
        "techno", "minimal techno", "trance", "psytrance",
        "drum and bass", "dnb", "dubstep", "hardstyle",
        "electro house",
    },

    # =======================
    # REGGAE
    # =======================
    "Reggae": {
        "reggae", "roots reggae", "reggae brasileiro",
        "dub", "dancehall",
    },

    # =======================
    # R&B / SOUL
    # =======================
    "R&B / Soul": {
        "r&b", "soul", "neo soul", "contemporary r&b",
        "alternative r&b", "quiet storm",
    },

    # =======================
    # LATINO
    # =======================
    "Latino": {
        "latin", "latino", "latin pop", "reggaeton",
        "bachata", "salsa", "merengue",
    },

    # =======================
    # JAZZ / CLÁSSICA
    # =======================
    "Jazz": {
        "jazz", "smooth jazz", "jazz fusion",
        "bossa jazz", "latin jazz",
    },

    "Clássica": {
        "classical", "classica", "clássica",
        "orchestral", "instrumental classical",
        "symphonic",
    },
}


def normalize_string(text: str) -> str:
    if not text:
        return ""
    text = text.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize_genre_name(genre: str) -> str:
    return normalize_string(genre)

def _keyword_matches(normalized_genre: str, keyword: str) -> bool:
    normalized_keyword = normalize_genre_name(keyword)
    if not normalized_keyword:
        return False
    # Regex com bordas de palavra, mas aceitando espaços internos
    pattern = r"\b" + re.escape(normalized_keyword).replace(r"\ ", r"\s+") + r"\b"
    return re.search(pattern, normalized_genre) is not None

def map_genre_to_main(genre: str) -> str | None:
    normalized = normalize_genre_name(genre)
    if not normalized:
        return None
    for main_genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            if _keyword_matches(normalized, kw):
                return main_genre
    return None

def choose_main_genres(genres: list[str], max_categories: int = 2) -> list[str]:
    candidates = []
    for g in genres:
        main = map_genre_to_main(g)
        if main and main not in candidates:
            candidates.append(main)

    if not candidates:
        return ["Outros"]
    return candidates[:max_categories]

#region ideias
# 1. Salvar a lista em um arquivo
# Permita salvar a lista em um .txt ou .csv para facilitar o compartilhamento.

# 2. Filtrar por gênero
# Adicione uma opção para mostrar/copiar apenas músicas de um gênero específico.

# 3. Mostrar todos os artistas
# Se a música tiver mais de um artista, mostre todos (não só o primeiro).


# 4. Mostrar mais informações
# Inclua o álbum, duração da música, popularidade ou link direto para a faixa.

# 5. Interface gráfica
# Crie uma interface simples com Tkinter ou PySimpleGUI para facilitar o uso.

# 6. Exportar para Excel
# Permita exportar a lista para um arquivo .xlsx com colunas para música, artista, gênero, etc.

# 7. Buscar playlists do usuário
# Implemente autenticação OAuth para buscar playlists diretamente da sua conta Spotify.

# 8. Buscar letras das músicas
# Integre com APIs de letras (ex: Vagalume, Genius) para mostrar/copiar as letras junto.

# 9. Remover duplicadas
# Adicione uma opção para remover músicas repetidas da lista.

# 10. Melhorar agrupamento de gêneros
# Agrupe gêneros semelhantes (ex: "sertanejo", "sertanejo universitário", "sertanejo pop" → "Sertanejo").
#endregion

def get_auth_url():
    """Gera URL de autenticação OAuth"""
    scopes = 'playlist-modify-public playlist-modify-private'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scopes
    }
    return f"https://accounts.spotify.com/authorize?{urlencode(params)}"

def get_token_from_code(auth_code):
    """Troca o código de autorização por um token de acesso"""
    url = "https://accounts.spotify.com/api/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = request_with_retries("POST", url, headers=headers, data=data)
    if response is not None and response.status_code == 200:
        return response.json().get('access_token')
    else:
        if response is None:
            print("\n⚠️  Erro ao obter token: sem resposta da rede.")
        else:
            print(f"\n⚠️  Erro ao obter token. Status: {response.status_code}")
            print(f"Resposta: {response.text}")
    return None

def get_user_id(token):
    """Obtém o ID do usuário autenticado"""
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = request_with_retries("GET", url, headers=headers)
    if response is not None and response.status_code == 200:
        return response.json().get('id')
    return None

def create_playlist(name, token, is_public=True):
    """Cria uma nova playlist no usuário autenticado (dispensa USER_ID)."""
    url = "https://api.spotify.com/v1/me/playlists"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "public": is_public,
        "description": f"Playlist gerada automaticamente - Gênero: {name}"
    }
    response = request_with_retries("POST", url, headers=headers, json=data)
    if response is not None and response.status_code == 201:
        return response.json().get('id')
    return None

def add_tracks_to_playlist(playlist_id, track_uris, token):
    """Adiciona músicas a uma playlist (máximo 100 por vez)"""
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Spotify permite adicionar até 100 músicas por vez
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        data = {"uris": batch}
        response = request_with_retries("POST", url, headers=headers, json=data)
        if response is None or response.status_code not in [200, 201]:
            return False
    return True


def get_artist_genre(artist_id, headers, cache):
    if artist_id in cache:
        return cache[artist_id]
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    resp = request_with_retries("GET", url, headers=headers)
    if resp is not None and resp.status_code == 200:
        genres = resp.json().get('genres', [])
        cache[artist_id] = genres
        return genres
    return []

def loading_bar(progress, total, bar_length=40):
    percent = float(progress) / total
    arrow = '=' * int(round(percent * bar_length) - 1) + '>' if percent > 0 else ''
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f'\rCarregando músicas: [{arrow}{spaces}] {int(percent*100)}%')
    sys.stdout.flush()

def get_playlist_name(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    response = request_with_retries("GET", url, headers=headers)
    if response is not None and response.status_code == 200:
        return response.json().get('name', 'playlist')
    return 'playlist'

def get_playlist_tracks(playlist_url):
    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    tracks = []
    params = {"limit": 100, "offset": 0}
    artist_genre_cache = {}

    # Descobrir o total de faixas para a barra de progresso
    total_tracks = None
    first_response = request_with_retries("GET", url, headers=headers, params=params)
    if first_response is None:
        print("\nErro na requisição! Sem resposta da API. Verifique sua conexão ou token.")
        return []
    try:
        data = first_response.json()
    except Exception:
        print("\nErro ao decodificar resposta da API. Verifique seu token ou o link da playlist.")
        return []
    if 'items' not in data:
        print("\nErro na requisição! Verifique seu token ou o link da playlist.")
        return []
    total_tracks = data.get('total', 0)
    next_url = data.get('next')
    items = data.get('items', [])
    processed = 0

    while True:
        for item in items:
            track = item['track']
            if track:
                name = track['name']
                artist = track['artists'][0]['name']
                artist_id = track['artists'][0]['id']
                track_uri = track['uri']  # Adicionar URI da música
                genres = get_artist_genre(artist_id, headers, artist_genre_cache)
                generos_principais = choose_main_genres(genres, max_categories=2)
                tracks.append({
                    "musica": f"{name} - {artist}",
                    "artista": artist,
                    "generos": genres,
                    "generos_principais": generos_principais,
                    "uri": track_uri  # Guardar URI para criar playlists
                })
            processed += 1
            loading_bar(processed, total_tracks)
        if next_url:
            response = request_with_retries("GET", next_url, headers=headers)
            if response is None:
                print("\nErro ao requisitar página seguinte. Interrompendo leitura de faixas.")
                break
            try:
                data = response.json()
            except Exception as e:
                print("\nErro ao decodificar resposta da API. Possível token expirado ou limite atingido.")
                print("Detalhes:", e)
                break
            items = data.get('items', [])
            next_url = data.get('next')
        else:
            break
    print("\nCarregando músicas da playlist... Pronto!")
    return tracks

class CallbackHandler(BaseHTTPRequestHandler):
    """Servidor HTTP simples para capturar o código OAuth"""
    def do_GET(self):
        global auth_code_received, auth_received_time, auth_status, auth_error_message

        requested_path = self.path.split('?', 1)[0]

        # Servir arquivos estáticos de /screens/
        if requested_path.startswith('/screens/'):
            asset_name = requested_path[len('/screens/'):]
            asset_path = Path('screens') / asset_name
            if asset_path.exists() and asset_path.is_file():
                ext = asset_path.suffix.lower()
                content_type = 'application/octet-stream'
                if ext == '.css':
                    content_type = 'text/css; charset=utf-8'
                elif ext == '.html':
                    content_type = 'text/html; charset=utf-8'
                elif ext == '.js':
                    content_type = 'application/javascript; charset=utf-8'

                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.end_headers()
                with open(asset_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # Callback OAuth padrão
        if requested_path.startswith('/callback'):
            query = self.path.split('?', 1)[-1]
            params = parse_qs(query)
            if 'code' in params:
                auth_code_received = params['code'][0]
                auth_received_time = time.time()
                auth_status = 'pending'
                auth_error_message = ''

                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()

                html_path = Path('screens') / 'auth_success.html'
                try:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        self.wfile.write(f.read().encode('utf-8'))
                except Exception:
                    fallback_html = '<html><body><h1>Autenticação iniciada...</h1></body></html>'
                    self.wfile.write(fallback_html.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'Missing authorization code')
            return

        # Status do fluxo de autenticação
        if requested_path.startswith('/oauth-status'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            result = {
                'status': auth_status,
                'error': auth_error_message,
            }
            self.wfile.write(str(result).replace("'", '"').encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        # Suprimir logs do servidor
        pass

def start_callback_server():
    """Inicia servidor para receber callback OAuth"""
    server = HTTPServer(('127.0.0.1', 8888), CallbackHandler)
    server.timeout = 1

    def serve_until_authorized():
        global auth_status, auth_received_time, auth_error_message
        # Permite servir callback + assets/CSS enquanto a autenticação estiver em progresso
        while True:
            server.handle_request()

            if auth_status in ['success', 'error']:
                # espera um pouco para última requisição de client-side (ajax polling)
                if auth_received_time and time.time() - auth_received_time > 2:
                    break
            else:
                # Mantém vivo por até 60s esperando o fluxo de callback e token
                if auth_received_time and time.time() - auth_received_time > 60:
                    auth_status = 'error'
                    auth_error_message = 'Tempo de autenticação esgotado.'
                    break

        server.server_close()

    thread = threading.Thread(target=serve_until_authorized)
    thread.daemon = True
    thread.start()
    return server

def parse_access_token(url_or_token: str):
    """Aceita a URL completa ou só o token e devolve o access_token"""
    s = url_or_token.strip()
    if 'access_token=' in s:
        # Fragmento vem após '#'
        frag = s.split('#', 1)[-1]
        params = parse_qs(frag)
        return params.get('access_token', [None])[0]
    return s or None

def open_in_browser(url: str):
    """Abre o navegador no Windows e copia o link se não conseguir abrir."""
    try:
        webbrowser.open(url, new=1, autoraise=True)
        print("Abrindo o navegador automaticamente...")
        return
    except Exception:
        pass
    try:
        os.startfile(url)  # Windows
        print("Abrindo via startfile...")
        return
    except Exception:
        pass
    try:
        os.system(f'start "" "{url}"')  # Fallback Windows
        print("Abrindo via start...")
        return
    except Exception:
        pass
    try:
        pyperclip.copy(url)
        print("Link copiado para a área de transferência. Cole no navegador.")
    except Exception:
        print("Copie e cole o link manualmente no navegador.")

if __name__ == "__main__":
    print("\n=== SPOTIFY PLAYLIST ORGANIZER ===\n")

    # Verifica se credenciais estão configuradas
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Erro: Credenciais do Spotify não encontradas!")
        print("\nPor favor, configure o arquivo .env:")
        print("  1. Copie: .env.example → .env")
        print("  2. Preencha com suas credenciais do Spotify")
        print("  3. Execute novamente\n")
        sys.exit(1)

    # Authorization Code Flow
    auth_url = get_auth_url()  # usa response_type=code
    print("Autorização necessária. O navegador será aberto.")
    print("Após autorizar, uma página 'Autenticacao concluida!' aparecerá.\n")

    # Inicia servidor local e abre o navegador
    start_callback_server()
    open_in_browser(auth_url)

    # Espera receber o code (até 120s)
    print("Aguardando autorização no navegador...")
    t0 = time.time()
    while auth_code_received is None and time.time() - t0 < 120:
        time.sleep(0.3)

    if auth_code_received:
        auth_status = 'pending'
        TOKEN = get_token_from_code(auth_code_received)
        if TOKEN:
            auth_status = 'success'
            USER_ID = get_user_id(TOKEN)  # opcional, só para validar
            if USER_ID:
                print(f"✅ Autenticado! User ID: {USER_ID}\n")
            else:
                print("✅ Autenticado!\n")
            usar_oauth = 's'
        else:
            auth_status = 'error'
            auth_error_message = 'Falha ao obter token. Verifique CLIENT_SECRET e Redirect URI.'
            print("❌ Erro ao obter token. Verifique CLIENT_SECRET e Redirect URI.\n")
            # Aguarde o browser atualizar a página e exibir o erro
            time.sleep(5)
            sys.exit(1)
    else:
        auth_status = 'error'
        auth_error_message = 'Não recebi o código (timeout).'
        print("❌ Não recebi o código (timeout).")
        time.sleep(5)
        sys.exit(1)

    url = input("Cole o link da playlist do Spotify: ")
    playlist_name = get_playlist_name(url)
    musicas_info = get_playlist_tracks(url)
    musicas = [m["musica"] for m in musicas_info]

    # Organiza por gêneros principais (até 2 categorias por música)
    estilos_dict = {}
    estilos_dict_uris = {}  # Guardar URIs também
    seen_uris = set()
    for m in musicas_info:
        if m["uri"] in seen_uris:
            continue
        seen_uris.add(m["uri"])

        generos_principais = m.get("generos_principais") or ["Outros"]
        adicionados = set()
        for genero_principal in generos_principais[:2]:
            if genero_principal in adicionados:
                continue
            adicionados.add(genero_principal)
            estilos_dict.setdefault(genero_principal, []).append(m["musica"])
            estilos_dict_uris.setdefault(genero_principal, []).append(m["uri"])

    # Exibe por ordem alfabética
    lista_final = []
    estilos_ordenados = sorted(estilos_dict)
    for estilo in estilos_ordenados:
        lista_final.append(f"\n-------------({estilo.upper()})-------------")
        for musica in estilos_dict[estilo]:
            lista_final.append(musica)

    for linha in lista_final:
        print(linha)
    print(f"\nTotal de músicas: {len(musicas)}")

    # Modificando as opções de exportação
    print("\nEscolha uma opção:")
    print("1 - Copiar lista completa (com categorias) para área de transferência")
    print("2 - Salvar lista em arquivo texto")
    print("3 - Copiar + Salvar")
    if usar_oauth == 's' and TOKEN:
        print("4 - Criar playlists no Spotify (uma para cada gênero)")
        print("5 - Sair")
        opcoes_validas = ['1', '2', '3', '4', '5']
    else:
        print("4 - Sair")
        opcoes_validas = ['1', '2', '3', '4']
    
    opcao = input("Digite sua escolha: ").strip()
    
    if opcao == '1' or opcao == '3':
        pyperclip.copy('\n'.join(lista_final))
        print("Lista completa copiada para a área de transferência!")
        
    if opcao == '2' or opcao == '3':
        # Criar pasta 'playlists' se não existir
        pasta_playlist = Path("playlists")
        pasta_playlist.mkdir(exist_ok=True)
        
        # Salvar arquivo com nome da playlist
        nome_arquivo = pasta_playlist / f"{playlist_name}.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lista_final))
        print(f"Lista salva no arquivo: {nome_arquivo}")
    
    if opcao == '4' and usar_oauth == 's' and TOKEN:
        print("\n🎵 Criando playlists no Spotify...")
        print("Isso pode levar alguns minutos dependendo do número de gêneros...\n")
        
        prefixo = input("Prefixo para as playlists (ex: '[Rock]', deixe vazio para sem prefixo): ").strip()
        playlist_publica = input("Playlists públicas? (s/n, padrão: n): ").strip().lower() == 's'
        
        playlists_criadas = 0
        for genero in estilos_ordenados:
            track_uris = estilos_dict_uris.get(genero, [])
            if len(track_uris) == 0:
                continue
            
            nome_playlist = f"{prefixo} {genero.title()}" if prefixo else genero.title()
            print(f"Criando playlist: {nome_playlist} ({len(track_uris)} músicas)...")
            
            playlist_id = create_playlist(nome_playlist, TOKEN, playlist_publica)  # sem USER_ID
            if playlist_id:
                if add_tracks_to_playlist(playlist_id, track_uris, TOKEN):
                    playlists_criadas += 1
                    print("  ✅ Criada com sucesso!")
                else:
                    print("  ❌ Erro ao adicionar músicas")
            else:
                print("  ❌ Erro ao criar playlist")
        
        print(f"\n🎉 Concluído! {playlists_criadas} playlists criadas no seu Spotify!")
    
    if opcao not in opcoes_validas:
        print("Opção inválida!")