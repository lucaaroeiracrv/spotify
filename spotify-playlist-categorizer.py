import requests
import pyperclip
import sys
import time

TOKEN = ''

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
                genre = get_artist_genre(artist_id, headers, artist_genre_cache)
                tracks.append({
                    "musica": f"{name} - {artist}",
                    "artista": artist,
                    "genero": genre
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

if __name__ == "__main__":
    url = input("Cole o link da playlist do Spotify: ")
    musicas_info = get_playlist_tracks(url)
    musicas = [m["musica"] for m in musicas_info]

    # Organiza por gênero
    estilos_dict = {}
    for m in musicas_info:
        for genero in m["genero"].split(", "):
            estilos_dict.setdefault(genero, []).append(m["musica"])

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
    print("3 - Ambos")
    print("4 - Sair")
    
    opcao = input("Digite sua escolha (1-4): ").strip()
    
    if opcao in ['1', '3']:
        pyperclip.copy('\n'.join(lista_final))
        print("Lista completa copiada para a área de transferência!")
        
    if opcao in ['2', '3']:
        nome_arquivo = "playlist_categorizada.txt"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lista_final))
        print(f"Lista salva no arquivo: {nome_arquivo}")
    
    if opcao not in ['1', '2', '3', '4']:
        print("Opção inválida!")

