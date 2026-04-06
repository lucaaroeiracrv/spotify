import base64
import os
import re
import sys
import time
import unicodedata
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv

try:
    import pyperclip
except Exception:
    pyperclip = None


load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback").strip()
PLAYLIST_NAME = os.getenv("SPOTIFY_TEST_PLAYLIST_NAME", "Playlist Teste - Todas as Músicas").strip()
REQUEST_TIMEOUT = 10

parsed_redirect = urlparse(REDIRECT_URI)
CALLBACK_HOST = parsed_redirect.hostname or "127.0.0.1"
CALLBACK_PORT = parsed_redirect.port or 8888
CALLBACK_PATH = parsed_redirect.path or "/callback"

TOKEN = None
auth_code_received = None


sertanejo_tradicional = (
    "Evidências",
    "Fio de Cabelo",
    "Boate Azul",
    "Ainda Ontem Chorei de Saudade",
    "Telefone Mudo",
    "Menino da Porteira",
    "Chico Mineiro",
    "Pagode em Brasília",
    "Cabocla Tereza",
    "Estrada da Vida",
    "Saudade da Minha Terra",
    "A Majestade o Sabiá",
    "Galopeira",
    "Franguinho na Panela",
    "O Menino da Porteira",
    "Rei do Gado",
    "Índia",
    "Nuvem de Lágrimas",
    "Mercedita",
    "Fogão de Lenha",
)

sertanejo_universitario = (
    "Ai Se Eu Te Pego",
    "Camaro Amarelo",
    "Zuar e Beber",
    "Balada Boa",
    "Inventor dos Amores",
    "Voa Beija-Flor",
    "Amo Noite e Dia",
    "Meteoro",
    "Te Esperando",
    "Flor e o Beija-Flor",
    "Cuida Bem Dela",
    "Cê Topa",
    "Sosseguei",
    "10%",
    "Medo Bobo",
    "Propaganda",
    "Todo Seu",
    "Vidinha de Balada",
    "Largado às Traças",
    "Notificação Preferida",
)

sertanejo = (
    "Leão",
    "Infiel",
    "Troca de Calçada",
    "Arranhão",
    "Cuida Bem Dela",
    "Bloqueado",
    "Ficha Limpa",
    "A Maior Saudade",
    "Haja Colírio",
    "Seu Brilho Sumiu",
    "Cobaia",
    "Esqueça-Me Se For Capaz",
    "Eu Gosto Assim",
    "Solteiro Forçado",
    "Boiadeira",
    "Bombonzinho",
    "Mal Feito",
    "Termina Comigo Antes",
    "Narcisista",
    "Nosso Quadro",
)

samba = (
    "Não Deixe o Samba Morrer",
    "Trem das Onze",
    "Aquarela Brasileira",
    "O Show Tem Que Continuar",
    "Canta Canta Minha Gente",
    "Vou Festejar",
    "Zé do Caroço",
    "Coisinha do Pai",
    "Foi um Rio que Passou em Minha Vida",
    "Tiro ao Álvaro",
    "As Rosas Não Falam",
    "O Mundo é um Moinho",
    "Disritmia",
    "Do Leme ao Pontal",
    "Coração em Desalinho",
    "Deixa a Vida Me Levar",
    "Verdade",
    "Insensato Destino",
    "Lucidez",
    "Conselho",
)

pagode = (
    "Temporal",
    "Telegrama",
    "Livre Pra Voar",
    "Tchau e Bença",
    "Lancinho",
    "Coração Radiante",
    "Tá Escrito",
    "Melhor Eu Ir",
    "Até Que Durou",
    "Insegurança",
    "Nem de Graça",
    "Faz Falta",
    "Reinventar",
    "Depois do Prazer",
    "Que Se Chama Amor",
    "Me Apaixonei Pela Pessoa Errada",
    "Dom de Sonhar",
    "Cheia de Manias",
    "Cigana",
    "Marrom Bombom",
)

trap = (
    "goosebumps",
    "Mask Off",
    "Bad and Boujee",
    "XO Tour Llif3",
    "The Box",
    "SICKO MODE",
    "Highest in the Room",
    "Tunnel Vision",
    "Love Sosa",
    "Faneto",
    "Bank Account",
    "Ric Flair Drip",
    "Rockstar",
    "Magnolia",
    "Shoota",
    "Money Longer",
    "Drip Too Hard",
    "Yes Indeed",
    "Lemonade",
    "Flex Up",
)

trap_nacional = (
    "Kenny G",
    "Máquina do Tempo",
    "Vampiro",
    "Flow Espacial",
    "M4",
    "Mustang Preto",
    "Amor de Fim de Noite",
    "Balão",
    "Novo Balanço",
    "Clickbait",
    "Portugal",
    "Michael Jackson",
    "Jordan",
    "212",
    "Freio da Blazer",
    "Poesia Acústica 13",
    "Coração de Gelo",
    "Felina",
    "Pitbullzada",
    "A Cara do Crime",
)

rap = (
    "Lose Yourself",
    "Stan",
    "HUMBLE.",
    "DNA.",
    "God’s Plan",
    "Still D.R.E.",
    "The Real Slim Shady",
    "N.Y. State of Mind",
    "Juicy",
    "Changes",
    "Without Me",
    "In Da Club",
    "Power",
    "Gold Digger",
    "Alright",
    "Ms. Jackson",
    "C.R.E.A.M.",
    "Empire State of Mind",
    "Sicko Mode",
    "Shook Ones Pt. II",
)

boom_bap = (
    "Mun'Ra",
    "Um Bom Lugar",
    "País da Fome",
    "Diário de um Detento",
    "Vida Loka Pt. 1",
    "Negro Drama",
    "A Vida é Desafio",
    "Fórmula Mágica da Paz",
    "Levanta e Anda",
    "Boa Esperança",
    "Mil Faces de um Homem Leal",
    "Vivão e Vivendo",
    "Oitavo Anjo",
    "Triunfo",
    "Cartier Santos Dumont",
    "Poetas no Topo 3",
    "Favela Vive 3",
    "Teimosia",
    "Sagrado",
    "Conquistas",
)

funk = (
    "Olha a Explosão",
    "Bum Bum Tam Tam",
    "Baile de Favela",
    "Vai Malandra",
    "SentaDONA",
    "Envolvimento",
    "Cerol na Mão",
    "Rap da Felicidade",
    "Dança do Créu",
    "Tá Tranquilo Tá Favorável",
    "Tô Tranquilão",
    "Te Botei no Paredão",
    "Vamos Pra Gaiola",
    "Rebolando Devagarinho",
    "Desenrola Bate Joga de Ladin",
    "Medley da Gaiola",
    "Fuleragem",
    "Verdinha",
    "Surtada",
    "Ela Só Quer Paz",
)

rock = (
    "Smells Like Teen Spirit",
    "Bohemian Rhapsody",
    "Sweet Child O’ Mine",
    "Hotel California",
    "Wonderwall",
    "In the End",
    "Numb",
    "Back in Black",
    "Dream On",
    "Enter Sandman",
    "Highway to Hell",
    "Zombie",
    "Seven Nation Army",
    "Creep",
    "Californication",
    "Come As You Are",
    "Basket Case",
    "Paradise City",
    "Livin’ on a Prayer",
    "Radioactive",
)

rock_nacional = (
    "Tempo Perdido",
    "Pais e Filhos",
    "Pro Dia Nascer Feliz",
    "Exagerado",
    "Primeiros Erros",
    "À Sua Maneira",
    "Anna Júlia",
    "Dias de Luta, Dias de Glória",
    "Proibida Pra Mim",
    "Mulher de Fases",
    "Meu Erro",
    "Lanterna dos Afogados",
    "O Segundo Sol",
    "Por Enquanto",
    "Flores",
    "Epitáfio",
    "Inútil",
    "Pelados em Santos",
    "Metamorfose Ambulante",
    "À Francesa",
)

metal = (
    "Roots Bloody Roots",
    "Ratamahatta",
    "Refuse/Resist",
    "Carry On",
    "Nova Era",
    "Angels and Demons",
    "Blood of Lions",
    "Apocalyptic Victory",
    "Troops of Doom",
    "Dead Embryonic Cells",
    "Master of Puppets",
    "Enter Sandman",
    "Fear of the Dark",
    "The Trooper",
    "Chop Suey!",
    "Toxicity",
    "Duality",
    "Holy Wars",
    "Cowboys From Hell",
    "Raining Blood",
)

pop = (
    "Bad Romance",
    "Blinding Lights",
    "Shape of You",
    "Billie Jean",
    "Levitating",
    "Firework",
    "Rolling in the Deep",
    "As It Was",
    "Flowers",
    "Shake It Off",
    "Sorry",
    "Halo",
    "Roar",
    "Treasure",
    "Toxic",
    "Poker Face",
    "Call Me Maybe",
    "Happy",
    "Die With A Smile",
    "Can’t Stop the Feeling",
)

eletronica = (
    "Animals",
    "Levels",
    "Wake Me Up",
    "Titanium",
    "Clarity",
    "Faded",
    "Lean On",
    "Don’t You Worry Child",
    "Summer",
    "One Kiss",
    "Turn Down for What",
    "Taki Taki",
    "Scary Monsters and Nice Sprites",
    "Bangarang",
    "Tremor",
    "The Business",
    "Adagio for Strings",
    "Satisfaction",
    "Piece of Your Heart",
    "Heads Will Roll Remix",
)

reggae = (
    "Is This Love",
    "Three Little Birds",
    "One Love",
    "Could You Be Loved",
    "Sorri, Sou Rei",
    "Quero Ser Feliz Também",
    "Natiruts Reggae Power",
    "A Sombra da Maldade",
    "Onde Você Mora",
    "Girassol",
    "Pescador de Ilusões",
    "Anjos",
    "My Girl",
    "Badfish",
    "Sweat",
    "Here I Am",
    "Red Red Wine",
    "Roots Radical",
    "Kingston Town",
    "So Jah Jah Sbaoth",
)

mpb = (
    "Águas de Março",
    "Garota de Ipanema",
    "Como Nossos Pais",
    "Romaria",
    "Tocando em Frente",
    "Admirável Gado Novo",
    "Chão de Giz",
    "O Leãozinho",
    "Sozinho",
    "Apesar de Você",
    "Cálice",
    "Sina",
    "Oceano",
    "Flor de Lis",
    "Gostava Tanto de Você",
    "Azul da Cor do Mar",
    "Velha Infância",
    "Anna Júlia",
    "Sangue Latino",
    "Metade",
)

GRUPOS_DE_MUSICAS = {
    "sertanejo_tradicional": sertanejo_tradicional,
    "sertanejo_universitario": sertanejo_universitario,
    "sertanejo": sertanejo,
    "samba": samba,
    "pagode": pagode,
    "trap": trap,
    "trap_nacional": trap_nacional,
    "rap": rap,
    "boom_bap": boom_bap,
    "funk": funk,
    "rock": rock,
    "rock_nacional": rock_nacional,
    "metal": metal,
    "pop": pop,
    "eletronica": eletronica,
    "reggae": reggae,
    "mpb": mpb,
}


def request_with_retries(method, url, **kwargs):
    timeout = kwargs.pop("timeout", REQUEST_TIMEOUT)
    attempts = kwargs.pop("attempts", 3)

    for attempt in range(1, attempts + 1):
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
        except requests.RequestException as exc:
            if attempt == attempts:
                print(f"❌ Falha de rede ao acessar {url}: {exc}")
                return None
            time.sleep(min(0.5 * attempt, 2))
            continue

        if response.status_code == 429 and attempt < attempts:
            retry_after = response.headers.get("Retry-After", "1")
            try:
                wait_seconds = float(retry_after)
            except ValueError:
                wait_seconds = 1.0
            wait_seconds = max(0.5, min(wait_seconds, 5.0))
            print(f"⏳ Limite temporário do Spotify. Aguardando {wait_seconds:.1f}s...")
            time.sleep(wait_seconds)
            continue

        return response

    return None


def normalize_text(value):
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return value.strip()


def get_auth_url():
    scopes = "playlist-modify-public playlist-modify-private"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": scopes,
    }
    return f"https://accounts.spotify.com/authorize?{urlencode(params)}"


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code_received

        requested_path = self.path.split("?", 1)[0]
        if requested_path != CALLBACK_PATH:
            self.send_response(404)
            self.end_headers()
            return

        query = self.path.split("?", 1)[-1]
        params = parse_qs(query)
        auth_code_received = params.get("code", [None])[0]

        if auth_code_received:
            html = """
            <html>
              <head><meta charset='utf-8'><title>Spotify</title></head>
              <body style='font-family: Arial; padding: 24px;'>
                <h1>✅ Autorização concluída</h1>
                <p>Você já pode voltar para o terminal.</p>
              </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"Authorization code not received.")

    def log_message(self, format, *args):
        return


def start_callback_server():
    server = HTTPServer((CALLBACK_HOST, CALLBACK_PORT), CallbackHandler)
    server.timeout = 1
    return server


def open_in_browser(url):
    try:
        webbrowser.open(url, new=1, autoraise=True)
        return True
    except Exception:
        pass

    if pyperclip is not None:
        try:
            pyperclip.copy(url)
            print("🔗 Link copiado para a área de transferência.")
        except Exception:
            pass

    print("Abra este link no navegador para autorizar:")
    print(url)
    return False


def wait_for_auth_code(server, timeout_seconds=120):
    started_at = time.time()
    while auth_code_received is None and (time.time() - started_at) < timeout_seconds:
        server.handle_request()
    server.server_close()
    return auth_code_received


def get_token_from_code(auth_code):
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }

    response = request_with_retries(
        "POST",
        "https://accounts.spotify.com/api/token",
        headers=headers,
        data=data,
    )
    if response is not None and response.status_code == 200:
        return response.json().get("access_token")

    if response is not None:
        print(f"❌ Erro ao obter token ({response.status_code}): {response.text}")
    return None


def create_playlist(name, token, is_public=False, description=""):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": name,
        "public": is_public,
        "description": description or "Playlist criada automaticamente pelo gerarPlaylistTeste.py",
    }

    response = request_with_retries(
        "POST",
        "https://api.spotify.com/v1/me/playlists",
        headers=headers,
        json=payload,
    )
    if response is not None and response.status_code == 201:
        return response.json().get("id"), response.json().get("external_urls", {}).get("spotify")

    if response is not None:
        print(f"❌ Erro ao criar playlist ({response.status_code}): {response.text}")
    return None, None


def choose_best_track(song_name, items):
    target = normalize_text(song_name)
    for item in items:
        if normalize_text(item.get("name", "")) == target:
            return item

    for item in items:
        normalized_name = normalize_text(item.get("name", ""))
        if target in normalized_name or normalized_name in target:
            return item

    return items[0] if items else None


def search_track_uri(song_name, token):
    headers = {"Authorization": f"Bearer {token}"}
    attempts = [
        {"q": f'track:"{song_name}"', "type": "track", "limit": 10, "market": "BR"},
        {"q": song_name, "type": "track", "limit": 10, "market": "BR"},
    ]

    for params in attempts:
        response = request_with_retries(
            "GET",
            "https://api.spotify.com/v1/search",
            headers=headers,
            params=params,
        )
        if response is None or response.status_code != 200:
            continue

        items = response.json().get("tracks", {}).get("items", [])
        selected = choose_best_track(song_name, items)
        if selected:
            artists = ", ".join(artist.get("name", "") for artist in selected.get("artists", []))
            label = f"{selected.get('name', song_name)} - {artists}".strip(" -")
            return selected.get("uri"), label

    return None, None


def add_tracks_to_playlist(playlist_id, track_uris, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i + 100]
        response = request_with_retries(
            "POST",
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            headers=headers,
            json={"uris": batch},
        )
        if response is None or response.status_code not in (200, 201):
            if response is not None:
                print(f"❌ Erro ao adicionar músicas ({response.status_code}): {response.text}")
            return False
    return True


def get_all_tracks_unique():
    all_tracks = []
    for tracks in GRUPOS_DE_MUSICAS.values():
        all_tracks.extend(tracks)

    seen = set()
    unique_tracks = []
    for track in all_tracks:
        key = normalize_text(track)
        if key not in seen:
            seen.add(key)
            unique_tracks.append(track)
    return all_tracks, unique_tracks


def run_dry_mode():
    all_tracks, unique_tracks = get_all_tracks_unique()
    print(f"Grupos carregados: {len(GRUPOS_DE_MUSICAS)}")
    print(f"Total informado: {len(all_tracks)} músicas")
    print(f"Únicas para buscar no Spotify: {len(unique_tracks)} músicas")
    print("Primeiras 15 músicas:")
    for song in unique_tracks[:15]:
        print(f"- {song}")


def main():
    global TOKEN

    if "--dry-run" in sys.argv:
        run_dry_mode()
        return 0

    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Credenciais do Spotify não encontradas no arquivo .env")
        print("Defina SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET e SPOTIFY_REDIRECT_URI.")
        return 1

    all_tracks, unique_tracks = get_all_tracks_unique()

    print("\n=== GERADOR DE PLAYLIST DE TESTE ===\n")
    print(f"Playlist alvo: {PLAYLIST_NAME}")
    print(f"Total de músicas recebidas: {len(all_tracks)}")
    print(f"Músicas únicas após remover repetidas: {len(unique_tracks)}\n")
    print("O navegador será aberto para autorizar no Spotify.\n")

    auth_url = get_auth_url()
    server = start_callback_server()
    open_in_browser(auth_url)

    code = wait_for_auth_code(server)
    if not code:
        print("❌ Não foi possível capturar o código de autorização.")
        return 1

    TOKEN = get_token_from_code(code)
    if not TOKEN:
        return 1

    found_uris = []
    not_found = []

    print("🔎 Buscando músicas no Spotify...")
    for index, song_name in enumerate(unique_tracks, start=1):
        track_uri, label = search_track_uri(song_name, TOKEN)
        if track_uri:
            found_uris.append(track_uri)
            print(f"[{index:03d}/{len(unique_tracks)}] ✅ {song_name} -> {label}")
        else:
            not_found.append(song_name)
            print(f"[{index:03d}/{len(unique_tracks)}] ❌ {song_name}")

    if not found_uris:
        print("❌ Nenhuma música foi localizada. A playlist não foi criada.")
        return 1

    description = (
        f"Playlist criada automaticamente com {len(found_uris)} faixas "
        f"a partir de uma lista teste em gerarPlaylistTeste.py"
    )
    playlist_id, playlist_url = create_playlist(
        PLAYLIST_NAME,
        TOKEN,
        is_public=False,
        description=description,
    )

    if not playlist_id:
        return 1

    if not add_tracks_to_playlist(playlist_id, found_uris, TOKEN):
        return 1

    print("\n🎉 Playlist criada com sucesso!")
    print(f"Faixas adicionadas: {len(found_uris)}")
    if playlist_url:
        print(f"Abrir no Spotify: {playlist_url}")

    if not_found:
        print(f"\n⚠️ {len(not_found)} músicas não foram encontradas:")
        for song in not_found:
            print(f"- {song}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
