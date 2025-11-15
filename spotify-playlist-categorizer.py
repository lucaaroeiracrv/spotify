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

# CONFIGURAÇÃO
# Preencha as credenciais inline abaixo APENAS para uso local
#   - Preencha e use normalmente
#   - ANTES de fazer commit, LIMPE estes valores (deixe strings vazias)
# link do dashboard: https://developer.spotify.com/dashboard/821ef4e9cf754b4aa26b4537fe2b0f34
INLINE_CLIENT_ID = '' 
INLINE_CLIENT_SECRET = '' 
INLINE_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

# As credenciais são lidas daqui; REDIRECT_URI padrão: http://127.0.0.1:8888/callback
CLIENT_ID = (INLINE_CLIENT_ID or os.getenv('SPOTIFY_CLIENT_ID', '')).strip()
CLIENT_SECRET = (INLINE_CLIENT_SECRET or os.getenv('SPOTIFY_CLIENT_SECRET', '')).strip()
REDIRECT_URI = (INLINE_REDIRECT_URI or os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')).strip()

TOKEN = None
USER_ID = None
auth_code_received = None

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
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"\n⚠️  Erro ao obter token. Status: {response.status_code}")
        print(f"Resposta: {response.text}")
    return None

def get_user_id(token):
    """Obtém o ID do usuário autenticado"""
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
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
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()['id']
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
        response = requests.post(url, headers=headers, json=data)
        if response.status_code not in [200, 201]:
            return False
    return True


def get_artist_genre(artist_id, headers, cache):
    if artist_id in cache:
        return cache[artist_id]
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        genres = resp.json().get('genres', [])
        genre = ', '.join(genres) if genres else "outros"
        cache[artist_id] = genre
        return genre
    return "outros"

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
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
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
    first_response = requests.get(url, headers=headers, params=params)
    data = first_response.json()
    if 'items' not in data:
        print("\nErro na requisição! Verifique seu token ou o link da playlist.")
        return []
    total_tracks = data.get('total', 0)
    next_url = data['next']
    items = data['items']
    processed = 0

    while True:
        for item in items:
            track = item['track']
            if track:
                name = track['name']
                artist = track['artists'][0]['name']
                artist_id = track['artists'][0]['id']
                track_uri = track['uri']  # Adicionar URI da música
                genre = get_artist_genre(artist_id, headers, artist_genre_cache)
                tracks.append({
                    "musica": f"{name} - {artist}",
                    "artista": artist,
                    "genero": genre,
                    "uri": track_uri  # Guardar URI para criar playlists
                })
            processed += 1
            loading_bar(processed, total_tracks)
        if next_url:
            response = requests.get(next_url, headers=headers)
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
        global auth_code_received
        # Extrair o código da URL
        query = self.path.split('?')[-1]
        params = parse_qs(query)
        
        if 'code' in params:
            auth_code_received = params['code'][0]
            # Enviar resposta de sucesso
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Autenticacao concluida!</h1><p>Voce pode fechar esta janela e voltar ao terminal.</p></body></html>')
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suprimir logs do servidor
        pass

def start_callback_server():
    """Inicia servidor para receber callback OAuth"""
    server = HTTPServer(('127.0.0.1', 8888), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
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
        TOKEN = get_token_from_code(auth_code_received)
        if TOKEN:
            USER_ID = get_user_id(TOKEN)  # opcional, só para validar
            if USER_ID:
                print(f"✅ Autenticado! User ID: {USER_ID}\n")
            else:
                print("✅ Autenticado!\n")
            usar_oauth = 's'
        else:
            print("❌ Erro ao obter token. Verifique CLIENT_SECRET e Redirect URI.\n")
            sys.exit(1)
    else:
        print("❌ Não recebi o código (timeout).")
        sys.exit(1)

    url = input("Cole o link da playlist do Spotify: ")
    playlist_name = get_playlist_name(url)
    musicas_info = get_playlist_tracks(url)
    musicas = [m["musica"] for m in musicas_info]

    # Organiza por gênero
    estilos_dict = {}
    estilos_dict_uris = {}  # Guardar URIs também
    for m in musicas_info:
        for genero in m["genero"].split(", "):
            estilos_dict.setdefault(genero, []).append(m["musica"])
            estilos_dict_uris.setdefault(genero, []).append(m["uri"])

    # Exibe por ordem alfabética dos estilos, separando melhor as características
    lista_final = []
    for estilo in sorted(estilos_dict):
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
        for genero, track_uris in estilos_dict_uris.items():  # corrigido .items()
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