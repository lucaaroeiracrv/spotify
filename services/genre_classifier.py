from __future__ import annotations

import json
import os
import re
import threading
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable, Iterable

RequestFunction = Callable[..., Any]

CLASSIFIER_CACHE_VERSION = "2026-04-06-prototype-v11"
REFERENCE_LIBRARY_FILENAME = "genre_reference_library.json"

CANONICAL_LABELS = [
    "Sertanejo Tradicional",
    "Sertanejo Universitário",
    "Sertanejo",
    "Samba",
    "Pagode",
    "Trap",
    "Trap Nacional",
    "Rap",
    "Boom Bap",
    "Funk",
    "Rock",
    "Rock Nacional",
    "Metal",
    "Pop",
    "Eletrônica",
    "Reggae",
    "MPB",
    "Outros",
]

CANONICAL_ALIASES = {
    "sertanejo tradicional": "Sertanejo Tradicional",
    "sertanejo raiz": "Sertanejo Tradicional",
    "modao": "Sertanejo Tradicional",
    "moda de viola": "Sertanejo Tradicional",
    "sertanejo universitario": "Sertanejo Universitário",
    "sertanejo universitario pop": "Sertanejo Universitário",
    "sertanejo": "Sertanejo",
    "samba": "Samba",
    "pagode": "Pagode",
    "trap nacional": "Trap Nacional",
    "brazilian trap": "Trap Nacional",
    "trap brasileiro": "Trap Nacional",
    "trap": "Trap",
    "trap rap": "Trap",
    "country trap": "Trap",
    "country rap": "Trap",
    "latin trap": "Trap",
    "drill": "Trap",
    "rage": "Trap",
    "cloud rap": "Trap",
    "rap": "Rap",
    "hip hop": "Rap",
    "hiphop": "Rap",
    "hip-hop": "Rap",
    "melodic rap": "Rap",
    "alternative hip hop": "Rap",
    "southern hip hop": "Rap",
    "west coast hip hop": "Rap",
    "gangster rap": "Rap",
    "g-funk": "Rap",
    "trap soul": "Trap",
    "boom bap": "Boom Bap",
    "boombap": "Boom Bap",
    "boom-bap": "Boom Bap",
    "old school hip hop": "Rap",
    "old school rap": "Rap",
    "classic hip hop": "Rap",
    "golden age hip hop": "Rap",
    "east coast hip hop": "Rap",
    "funk": "Funk",
    "funk carioca": "Funk",
    "funk brasileiro": "Funk",
    "baile funk": "Funk",
    "rock nacional": "Rock Nacional",
    "rock brasileiro": "Rock Nacional",
    "rock": "Rock",
    "modern rock": "Rock",
    "alternative rock": "Rock",
    "indie rock": "Rock",
    "hard rock": "Rock",
    "classic rock": "Rock",
    "post grunge": "Rock",
    "pop punk": "Rock",
    "punk rock": "Rock",
    "emo rock": "Rock",
    "metal": "Metal",
    "heavy metal": "Metal",
    "thrash metal": "Metal",
    "nu metal": "Metal",
    "metalcore": "Metal",
    "pop": "Pop",
    "dance pop": "Pop",
    "synth pop": "Pop",
    "indie pop": "Pop",
    "electropop": "Pop",
    "teen pop": "Pop",
    "soft pop": "Pop",
    "mainstream pop": "Pop",
    "commercial pop": "Pop",
    "radio pop": "Pop",
    "art pop": "Pop",
    "hyperpop": "Pop",
    "k-pop": "Pop",
    "afropop": "Pop",
    "acoustic pop": "Pop",
    "adult contemporary": "Pop",
    "pop rap": "Pop",
    "hip pop": "Pop",
    "christian pop": "Pop",
    "r&b": "Pop",
    "rnb": "Pop",
    "contemporary r&b": "Pop",
    "alternative r&b": "Pop",
    "neo soul": "Pop",
    "soul": "Pop",
    "pop rock": "Pop",
    "eletronica": "Eletrônica",
    "electronic": "Eletrônica",
    "electronica": "Eletrônica",
    "eletronica pop": "Eletrônica",
    "edm": "Eletrônica",
    "house": "Eletrônica",
    "techno": "Eletrônica",
    "trance": "Eletrônica",
    "tropical house": "Eletrônica",
    "deep house": "Eletrônica",
    "progressive house": "Eletrônica",
    "big room house": "Eletrônica",
    "slap house": "Eletrônica",
    "eurodance": "Eletrônica",
    "italo dance": "Eletrônica",
    "moombahton": "Eletrônica",
    "french house": "Eletrônica",
    "reggae": "Reggae",
    "roots reggae": "Reggae",
    "reggae pop": "Reggae",
    "dancehall": "Reggae",
    "dub": "Reggae",
    "mpb": "MPB",
    "musica popular brasileira": "MPB",
    "bossa nova": "MPB",
    "samba cancao": "MPB",
    "outros": "Outros",
}

MAINSTREAM_POP_PRIORITY_ARTISTS = {
    "maroon 5",
    "imagine dragons",
    "panic at the disco",
    "panic! at the disco",
    "onerepublic",
    "one republic",
    "coldplay",
    "jonas brothers",
    "katy perry",
    "taylor swift",
    "miley cyrus",
    "dua lipa",
    "ariana grande",
    "olivia rodrigo",
    "billie eilish",
    "harry styles",
    "sabrina carpenter",
    "lady gaga",
    "bruno mars",
    "the weeknd",
    "doja cat",
    "realestk",
    "forrest frank",
}

ELECTRONIC_PRIORITY_ARTISTS = {
    "calvin harris",
    "david guetta",
    "avicii",
    "zedd",
    "kygo",
    "marshmello",
    "martin garrix",
    "swedish house mafia",
    "major lazer",
    "dj snake",
    "tiesto",
    "tiësto",
    "galantis",
    "jonas blue",
    "regard",
    "seeb",
    "meduza",
    "alan walker",
    "skrillex",
    "hardwell",
    "armin van buuren",
}

METAL_PRIORITY_ARTISTS = {
    "metallica",
    "sepultura",
    "iron maiden",
    "slayer",
    "pantera",
    "megadeth",
    "slipknot",
    "angra",
    "krisiun",
    "system of a down",
    "judas priest",
    "black sabbath",
    "korn",
    "lamb of god",
    "gojira",
    "death",
    "cannibal corpse",
    "behemoth",
    "children of bodom",
    "killswitch engage",
}

BOOM_BAP_PRIORITY_ARTISTS = {
    "racionais mc's",
    "racionais mc s",
    "sabotage",
    "facção central",
    "faccao central",
    "mv bill",
    "rzo",
    "realidade cruel",
    "trilha sonora do gueto",
    "snj",
    "pentagono",
    "pentágono",
    "mamelo",
}

SERTANEJO_UNIVERSITARIO_PRIORITY_ARTISTS = {
    "michel telo",
    "michel teló",
    "munhoz mariano",
    "luan santana",
    "jorge mateus",
}

SERTANEJO_MODERNO_PRIORITY_ARTISTS = {
    "marilia mendonca",
    "marília mendonça",
    "henrique juliano",
    "gusttavo lima",
    "ana castela",
    "lauana prado",
    "israel rodolffo",
    "maiara maraisa",
    "ze neto cristiano",
    "zé neto cristiano",
    "guilherme benuto",
    "hugo guilherme",
    "agroplay",
}

PRIORITY_FEEDBACK_EXAMPLES = [
    {
        "track_name": "Roar",
        "artist_names": ["Katy Perry"],
        "album_name": "PRISM",
        "labels": ["Pop"],
        "weight": 4.5,
        "hints": ["radio mainstream", "dance pop", "anthemic chorus", "global chart hit"],
    },
    {
        "track_name": "Maps",
        "artist_names": ["Maroon 5"],
        "album_name": "V",
        "labels": ["Pop"],
        "weight": 4.3,
        "hints": ["mainstream pop", "pop rock leve", "radio hit", "catchy hook"],
    },
    {
        "track_name": "Payphone",
        "artist_names": ["Maroon 5"],
        "album_name": "Overexposed",
        "labels": ["Pop"],
        "weight": 4.4,
        "hints": ["mainstream pop", "radio hit", "pop crossover", "hook forte"],
    },
    {
        "track_name": "High Hopes",
        "artist_names": ["Panic! At The Disco"],
        "album_name": "Pray for the Wicked",
        "labels": ["Pop"],
        "weight": 4.0,
        "hints": ["mainstream pop anthem", "charts", "bright pop production"],
    },
    {
        "track_name": "Flowers",
        "artist_names": ["Miley Cyrus"],
        "album_name": "Endless Summer Vacation",
        "labels": ["Pop"],
        "weight": 4.6,
        "hints": ["dance pop", "mainstream pop", "global chart hit"],
    },
    {
        "track_name": "Blank Space",
        "artist_names": ["Taylor Swift"],
        "album_name": "1989",
        "labels": ["Pop"],
        "weight": 4.6,
        "hints": ["pure pop", "mainstream pop", "chart hit", "synth pop"],
    },
    {
        "track_name": "Firework",
        "artist_names": ["Katy Perry"],
        "album_name": "Teenage Dream",
        "labels": ["Pop"],
        "weight": 4.5,
        "hints": ["anthemic pop", "radio mainstream", "commercial pop"],
    },
    {
        "track_name": "Counting Stars",
        "artist_names": ["OneRepublic"],
        "album_name": "Native",
        "labels": ["Pop"],
        "weight": 3.8,
        "hints": ["mainstream pop", "pop rock leve", "radio hit"],
    },
    {
        "track_name": "Sucker",
        "artist_names": ["Jonas Brothers"],
        "album_name": "Happiness Begins",
        "labels": ["Pop"],
        "weight": 3.9,
        "hints": ["mainstream pop", "radio hit", "pop band"],
    },
    {
        "track_name": "Rather Be",
        "artist_names": ["Clean Bandit", "Jess Glynne"],
        "album_name": "New Eyes",
        "labels": ["Eletrônica"],
        "weight": 4.4,
        "hints": ["electronic production", "dancefloor", "house pop", "club crossover"],
    },
    {
        "track_name": "Don't Let Me Down",
        "artist_names": ["The Chainsmokers", "Daya"],
        "album_name": "Collage",
        "labels": ["Eletrônica"],
        "weight": 4.3,
        "hints": ["edm pop", "drop", "festival", "electronic duo"],
    },
    {
        "track_name": "Enter Sandman",
        "artist_names": ["Metallica"],
        "album_name": "Metallica",
        "labels": ["Metal"],
        "weight": 4.7,
        "hints": ["heavy metal", "riff pesado", "distorcao intensa", "headbang"],
    },
    {
        "track_name": "Wonderwall",
        "artist_names": ["Oasis"],
        "album_name": "(What's The Story) Morning Glory?",
        "labels": ["Rock"],
        "weight": 4.1,
        "hints": ["britpop", "guitarras", "banda", "rock"],
    },
    {
        "track_name": "Vida Loka Pt. 2",
        "artist_names": ["Racionais MC's"],
        "album_name": "Nada Como Um Dia Após o Outro Dia",
        "labels": ["Boom Bap"],
        "weight": 4.8,
        "hints": ["boom bap", "old school", "sample-based", "rap brasileiro classico"],
    },
    {
        "track_name": "Bilhete 2.0",
        "artist_names": ["Rashid"],
        "album_name": "Portal",
        "labels": ["Rap"],
        "weight": 4.2,
        "hints": ["rap brasileiro moderno", "flow", "lyrical", "hip hop"],
    },
    {
        "track_name": "Ai Se Eu Te Pego",
        "artist_names": ["Michel Teló"],
        "album_name": "Na Balada",
        "labels": ["Sertanejo Universitário"],
        "weight": 4.4,
        "hints": ["sertanejo universitario", "festa", "refrão chiclete", "radio hit"],
    },
    {
        "track_name": "Leão",
        "artist_names": ["Marília Mendonça"],
        "album_name": "Decretos Reais",
        "labels": ["Sertanejo"],
        "weight": 4.6,
        "hints": ["sofrencia", "sertanejo moderno", "romântico", "feminejo"],
    },
    {
        "track_name": "Cuida Bem Dela",
        "artist_names": ["Henrique & Juliano"],
        "album_name": "Ao Vivo em Brasília",
        "labels": ["Sertanejo"],
        "weight": 4.4,
        "hints": ["sertanejo moderno", "sofrência", "romântico", "dupla brasileira"],
    },
    {
        "track_name": "Rude",
        "artist_names": ["MAGIC!"],
        "album_name": "Don't Kill the Magic",
        "labels": ["Pop"],
        "weight": 4.1,
        "hints": ["mainstream pop", "radio hit", "pop reggae crossover", "commercial pop"],
    },
]

GENRE_PROTOTYPE_HINTS: dict[str, dict[str, Any]] = {
    "Sertanejo Tradicional": {
        "summary": "modão caipira/raiz, acústico, viola e sanfona, dueto emotivo e temática rural ou de saudade.",
        "keywords": ["sertanejo raiz", "modao", "modão", "caipira", "moda de viola", "guarania"],
        "instrumental": ["viola caipira", "violão", "sanfona", "acordeon"],
        "rhythm": ["toada", "guarânia", "balada lenta", "arrasta-pé"],
        "timbres": ["acústico", "orgânico", "rural"],
        "vocal": ["dueto", "dupla", "voz sofrida", "interpretação sentimental"],
        "themes": ["saudade", "amor sofrido", "interior", "estrada", "roça"],
        "production": ["clássica", "analógica", "simples"],
        "era": ["anos 70", "anos 80", "anos 90"],
    },
    "Sertanejo Universitário": {
        "summary": "sertanejo romântico e festivo dos anos 2000/2010, refrão fácil, violão pop e produção radiofônica.",
        "keywords": ["sertanejo universitario", "sertanejo universitário", "arrocha universitario", "agrofunk sertanejo"],
        "instrumental": ["violão pop", "guitarra limpa", "percussão leve"],
        "rhythm": ["midtempo", "balada romântica", "batida dançante"],
        "timbres": ["brilhante", "comercial", "pop sertanejo"],
        "vocal": ["dupla jovem", "refrão chiclete", "voz romântica"],
        "themes": ["balada", "bebida", "paquera", "sofrência"],
        "production": ["radiofônica", "polida", "mainstream"],
        "era": ["anos 2000", "anos 2010"],
    },
    "Sertanejo": {
        "summary": "sertanejo moderno dominante, sofrência, narrativa amorosa, mistura de raiz com pop e produção atual brasileira.",
        "keywords": ["sertanejo", "sofrencia", "sofrência", "feminejo", "agronejo"],
        "instrumental": ["violão", "guitarra clean", "sanfona pop"],
        "rhythm": ["midtempo", "balada sertaneja", "batida contemporânea"],
        "timbres": ["romântico", "brasileiro", "melódico"],
        "vocal": ["dupla", "voz emotiva", "interpretação intensa"],
        "themes": ["relacionamento", "término", "ciúme", "bar"],
        "production": ["atual", "polida", "comercial"],
        "era": ["anos 2010", "anos 2020"],
    },
    "Samba": {
        "summary": "samba de raiz com cavaquinho, pandeiro e suingue orgânico, foco em roda, tradição e malemolência.",
        "keywords": ["samba", "samba de raiz", "partido alto", "roda de samba"],
        "instrumental": ["cavaquinho", "pandeiro", "surdo", "tamborim"],
        "rhythm": ["síncope", "suingue", "roda"],
        "timbres": ["percussivo", "orgânico", "brasileiro"],
        "vocal": ["canto coletivo", "interpretação malandra", "resposta de coro"],
        "themes": ["boemia", "comunidade", "resistência", "cotidiano"],
        "production": ["orgânica", "ao vivo", "tradicional"],
        "era": ["clássico", "tradicional"],
    },
    "Pagode": {
        "summary": "pagode romântico e urbano, swing suave, refrões sentimentais e produção mais polida que o samba raiz.",
        "keywords": ["pagode", "pagode romantico", "pagode romântico", "samba romântico"],
        "instrumental": ["tantan", "banjo", "cavaquinho", "pandeiro"],
        "rhythm": ["swing", "groove romântico", "midtempo"],
        "timbres": ["leve", "romântico", "urbano"],
        "vocal": ["lead melódico", "coro suave", "refrão sentimental"],
        "themes": ["amor", "relacionamento", "saudade", "superação"],
        "production": ["polida", "radiofônica"],
        "era": ["anos 90", "anos 2000", "anos 2010"],
    },
    "Trap": {
        "summary": "trap internacional com 808 forte, hi-hats rápidos, clima sombrio e flow moderno com autotune.",
        "keywords": ["trap", "trap soul", "drill", "rage", "cloud rap", "country rap", "latin trap"],
        "instrumental": ["808", "sub bass", "hi-hat triplado", "synth escuro"],
        "rhythm": ["halftime", "140 bpm", "swing trap"],
        "timbres": ["sombrio", "minimalista", "grave"],
        "vocal": ["autotune", "flow arrastado", "melodic rap"],
        "themes": ["flex", "lifestyle", "rua", "noite"],
        "production": ["digital", "minimal", "moderna"],
        "era": ["anos 2010", "anos 2020"],
    },
    "Trap Nacional": {
        "summary": "trap brasileiro com estética urbana BR, 808 pesado, autotune e linguagem/cultura nacional.",
        "keywords": ["trap nacional", "brazilian trap", "trap brasileiro", "br trap"],
        "instrumental": ["808", "grave pesado", "synth sombrio"],
        "rhythm": ["halftime", "groove arrastado", "batida trap"],
        "timbres": ["escuro", "digital", "urbano"],
        "vocal": ["autotune", "flow melódico", "português"],
        "themes": ["favela", "luxo", "vivência", "ascensão"],
        "production": ["moderna", "brasileira", "polida"],
        "era": ["anos 2010", "anos 2020"],
    },
    "Rap": {
        "summary": "rap/hip-hop dominante com foco em rima e flow, batida moderna ou clássica sem cair no boom bap brasileiro tradicional.",
        "keywords": ["rap", "hip hop", "hip-hop", "conscious hip hop", "alternative hip hop", "melodic rap"],
        "instrumental": ["beat hip hop", "drum machine", "sample"],
        "rhythm": ["boom", "groove rap", "midtempo"],
        "timbres": ["seco", "grave", "urbano"],
        "vocal": ["flow", "rimas", "versos falados"],
        "themes": ["vivência", "crítica", "autoafirmação", "narrativa urbana"],
        "production": ["sampleada", "moderna", "street"],
        "era": ["anos 90", "anos 2000", "anos 2010", "anos 2020"],
    },
    "Boom Bap": {
        "summary": "rap brasileiro old school com bateria seca, samples clássicos, densidade lírica e estética 90s/2000s.",
        "keywords": ["boom bap", "boombap", "boom-bap", "old school hip hop", "classic hip hop", "golden age hip hop"],
        "instrumental": ["sample de soul", "bateria seca", "loop clássico"],
        "rhythm": ["head-nod", "groove old school", "batida quadrada"],
        "timbres": ["poeirento", "áspero", "cru"],
        "vocal": ["rima densa", "flow clássico", "narrativa consciente"],
        "themes": ["consciência", "favela", "crítica social", "resistência"],
        "production": ["sample-based", "old school", "analógica"],
        "era": ["anos 90", "anos 2000"],
    },
    "Funk": {
        "summary": "funk brasileiro/baile funk com tamborzão, batida de pista, MC em destaque e energia corporal.",
        "keywords": ["funk carioca", "baile funk", "funk brasileiro", "mandelão", "proibidão"],
        "instrumental": ["tamborzão", "beat de baile", "sirene", "sub grave"],
        "rhythm": ["130 bpm", "batidão", "dançante"],
        "timbres": ["seco", "pesado", "percussivo"],
        "vocal": ["mc", "chamada de baile", "canto falado"],
        "themes": ["festa", "dança", "favela", "ostentação"],
        "production": ["crua", "club", "urbana"],
        "era": ["anos 2000", "anos 2010", "anos 2020"],
    },
    "Rock": {
        "summary": "rock internacional guiado por guitarras, bateria acústica, riffs e identidade de banda mais forte que o apelo pop.",
        "keywords": ["rock", "alternative rock", "hard rock", "classic rock", "indie rock", "post grunge", "pop punk"],
        "instrumental": ["guitarra distorcida", "baixo elétrico", "bateria acústica", "riff"],
        "rhythm": ["4/4 rock", "drive", "groove de banda"],
        "timbres": ["guitarrudo", "orgânico", "cru"],
        "vocal": ["voz rasgada", "banda", "refrão explosivo"],
        "themes": ["angústia", "rebeldia", "intensidade"],
        "production": ["ao vivo", "de banda", "guitarrista"],
        "era": ["anos 70", "anos 80", "anos 90", "anos 2000", "anos 2010"],
    },
    "Rock Nacional": {
        "summary": "rock brasileiro com linguagem e estética nacional, guitarras de banda e forte contexto BR.",
        "keywords": ["rock nacional", "rock brasileiro", "brazilian rock"],
        "instrumental": ["guitarra", "baixo", "bateria acústica"],
        "rhythm": ["rock de banda", "midtempo", "drive"],
        "timbres": ["brasileiro", "guitarrudo", "orgânico"],
        "vocal": ["português", "banda", "refrão cantado"],
        "themes": ["juventude", "cidade", "existencialismo", "cotidiano"],
        "production": ["banda", "nacional", "orgânica"],
        "era": ["anos 80", "anos 90", "anos 2000"],
    },
    "Metal": {
        "summary": "metal guiado por riffs pesados, distorção intensa, agressividade e performance vocal extrema ou épica.",
        "keywords": ["metal", "heavy metal", "thrash metal", "nu metal", "metalcore", "death metal"],
        "instrumental": ["riff pesado", "guitarra distorcida", "duplo pedal", "baixo pesado"],
        "rhythm": ["rápido", "quebrado", "groove pesado"],
        "timbres": ["agressivo", "denso", "pesado"],
        "vocal": ["gutural", "rasgado", "épico"],
        "themes": ["força", "caos", "conflito", "fantasia"],
        "production": ["pesada", "saturada", "high gain"],
        "era": ["anos 80", "anos 90", "anos 2000", "anos 2010"],
    },
    "Pop": {
        "summary": "pop mainstream guiado por refrão, melodia forte, produção polida, apelo radiofônico e estética acessível.",
        "keywords": ["pop", "dance pop", "synth pop", "electropop", "commercial pop", "radio pop", "mainstream pop"],
        "instrumental": ["synth pop", "beat dançante", "camadas brilhantes"],
        "rhythm": ["uptempo", "dançante", "midtempo radiofônico"],
        "timbres": ["brilhante", "limpo", "chiclete"],
        "vocal": ["hook forte", "refrão marcante", "lead melódico"],
        "themes": ["amor", "superação", "autoconfiança", "relacionamento"],
        "production": ["polida", "mainstream", "global chart"],
        "era": ["anos 2000", "anos 2010", "anos 2020"],
    },
    "Eletrônica": {
        "summary": "eletrônica/EDM com synths e drops em destaque, construção de pista e produção predominantemente eletrônica.",
        "keywords": ["edm", "electronic", "electronica", "house", "techno", "trance", "big room house", "slap house"],
        "instrumental": ["synth lead", "drop", "build-up", "kick de pista"],
        "rhythm": ["4-on-the-floor", "festival", "clubbing"],
        "timbres": ["digital", "sintético", "pulsante"],
        "vocal": ["vocal sample", "drop instrumental", "feature pop"],
        "themes": ["euforia", "noite", "pista", "festival"],
        "production": ["eletrônica", "dancefloor", "producer-driven"],
        "era": ["anos 2000", "anos 2010", "anos 2020"],
    },
    "Reggae": {
        "summary": "reggae com contratempo, baixo redondo, ambiência relaxada e identidade jamaicana/brasileira de roots ou pop reggae.",
        "keywords": ["reggae", "roots reggae", "reggae pop", "dancehall", "dub"],
        "instrumental": ["skank guitar", "baixo redondo", "órgão", "percussão leve"],
        "rhythm": ["contratempo", "laid-back", "one drop"],
        "timbres": ["quente", "solar", "relaxado"],
        "vocal": ["canto suave", "coral", "toque jamaicano"],
        "themes": ["paz", "natureza", "espiritualidade", "amor"],
        "production": ["orgânica", "grooveada"],
        "era": ["clássico", "roots", "anos 90", "anos 2000"],
    },
    "MPB": {
        "summary": "MPB com riqueza harmônica, letra poética, sofisticação melódica e forte identidade brasileira autoral.",
        "keywords": ["mpb", "musica popular brasileira", "música popular brasileira", "bossa", "canção brasileira"],
        "instrumental": ["violão", "piano", "sopros leves", "percussão sutil"],
        "rhythm": ["balada brasileira", "bossa", "samba-canção"],
        "timbres": ["sofisticado", "orgânico", "brasileiro"],
        "vocal": ["interpretação delicada", "poética", "cante autoral"],
        "themes": ["poesia", "amor", "tempo", "brasilidade", "reflexão"],
        "production": ["refinada", "acústica", "autoral"],
        "era": ["anos 60", "anos 70", "anos 80", "anos 90", "anos 2000"],
    },
}

TF_IMPORT_ERROR: Exception | None = None
try:
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    import tensorflow as tf  # type: ignore
    try:
        tf.get_logger().setLevel("ERROR")
    except Exception:
        pass
except Exception as exc:  # pragma: no cover - depends on environment
    tf = None  # type: ignore
    TF_IMPORT_ERROR = exc


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text.strip().lower())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = re.sub(r"[^a-z0-9\s/&-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def prepare_text_for_model(text: str | None) -> str:
    prepared = normalize_text(text)
    return prepared or "unknown"


def unique_non_empty(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        cleaned = value.strip()
        key = normalize_text(cleaned)
        if not cleaned or key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


class TensorFlowGenreLearner:
    """Incremental local learner fed by AI-labelled samples."""

    def __init__(
        self,
        labels: list[str],
        data_dir: Path,
        model_dir: Path,
        logger: Callable[[str, str], None],
    ) -> None:
        self.labels = labels
        self.label_to_index = {label: index for index, label in enumerate(labels)}
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.logger = logger
        self.enabled = tf is not None
        self.dataset_path = self.data_dir / "genre_learning_samples.json"
        self.model_path = self.model_dir / "genre_classifier.keras"
        self.meta_path = self.model_dir / "genre_classifier_meta.json"
        self.min_samples = max(6, int(os.getenv("GENRE_TF_MIN_SAMPLES", "8")))
        self.train_every = max(3, int(os.getenv("GENRE_TF_TRAIN_EVERY", "10")))
        self.epochs = max(2, int(os.getenv("GENRE_TF_EPOCHS", "4")))
        self.batch_size = max(4, int(os.getenv("GENRE_TF_BATCH_SIZE", "16")))
        self.prediction_threshold = min(0.99, max(0.5, float(os.getenv("GENRE_TF_CONFIDENCE", "0.86"))))
        self.min_distinct_labels = max(4, int(os.getenv("GENRE_TF_MIN_DISTINCT_LABELS", "4")))
        self.max_dominant_label_ratio = min(0.95, max(0.45, float(os.getenv("GENRE_TF_MAX_DOMINANT_RATIO", "0.72"))))
        self.samples_by_key: dict[str, dict[str, Any]] = {}
        self.pending_samples = 0
        self.dataset_dirty = 0
        self.model = None
        self.training_lock = threading.Lock()
        self.training_thread: threading.Thread | None = None
        self.last_train_summary: dict[str, Any] = {}
        self.model_version = CLASSIFIER_CACHE_VERSION

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self._load_dataset()
        self._seed_priority_examples()
        self._load_model()
        if self.enabled and len(self.samples_by_key) >= self.min_samples and self.model is None:
            self.maybe_train(force=True, background=True)

        if not self.enabled:
            reason = type(TF_IMPORT_ERROR).__name__ if TF_IMPORT_ERROR else "não instalado"
            self.logger(
                f"TensorFlow indisponível no ambiente atual ({reason}). O aprendizado local será ativado assim que a biblioteca estiver instalada.",
                level="WARN",
            )

    def _read_json_file(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return default

    def _write_json_file(self, path: Path, payload: Any) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def _load_dataset(self) -> None:
        payload = self._read_json_file(self.dataset_path, {"samples": []})
        for sample in payload.get("samples", []):
            sample_key = str(sample.get("key", "")).strip()
            if sample_key:
                self.samples_by_key[sample_key] = sample

    def _save_dataset(self, force: bool = False) -> None:
        if not force and self.dataset_dirty <= 0:
            return
        payload = {"samples": list(self.samples_by_key.values())}
        self._write_json_file(self.dataset_path, payload)
        self.dataset_dirty = 0

    def _load_model(self) -> None:
        if not self.enabled or not self.model_path.exists():
            return
        meta = self._read_json_file(self.meta_path, {})
        saved_labels = meta.get("labels") if isinstance(meta, dict) else None
        saved_version = str(meta.get("version", "")) if isinstance(meta, dict) else ""
        if saved_version != self.model_version or saved_labels != self.labels:
            self.logger("Modelo TensorFlow antigo detectado; será recriado com as regras atuais.", level="INFO")
            self.model = None
            return
        try:
            self.model = tf.keras.models.load_model(self.model_path)  # type: ignore[attr-defined]
        except Exception as exc:
            self.logger(f"Não foi possível carregar o modelo TensorFlow salvo: {exc}", level="WARN")
            self.model = None

    def _label_stats(self) -> tuple[dict[str, int], int, float]:
        counts: dict[str, int] = {}
        total = 0
        for sample in self.samples_by_key.values():
            for label in sample.get("labels", []):
                if label not in self.label_to_index:
                    continue
                counts[label] = counts.get(label, 0) + 1
                total += 1
        distinct_count = len(counts)
        dominant_ratio = (max(counts.values()) / total) if counts and total else 1.0
        return counts, distinct_count, dominant_ratio

    def is_ready(self) -> bool:
        if not self.enabled or self.model is None or len(self.samples_by_key) < self.min_samples:
            return False
        _, distinct_count, dominant_ratio = self._label_stats()
        return distinct_count >= self.min_distinct_labels and dominant_ratio <= self.max_dominant_label_ratio

    def record_example(
        self,
        sample_key: str,
        text: str,
        labels: list[str],
        source: str,
        confidence: float,
        weight: float = 1.0,
    ) -> bool:
        if not sample_key or not text:
            return False

        clean_labels = [label for label in labels if label in self.label_to_index]
        if not clean_labels:
            return False

        entry = {
            "key": sample_key,
            "text": text,
            "labels": clean_labels,
            "source": source,
            "confidence": round(float(confidence), 4),
            "weight": round(min(max(float(weight), 0.25), 8.0), 3),
            "updated_at": int(time.time()),
        }
        previous = self.samples_by_key.get(sample_key)
        if previous == entry:
            return False

        self.samples_by_key[sample_key] = entry
        self.pending_samples += 1
        self.dataset_dirty += 1
        if self.dataset_dirty >= 3:
            self._save_dataset(force=True)
        return True

    def _build_priority_example_text(self, example: dict[str, Any]) -> str:
        labels = unique_non_empty([str(label) for label in example.get("labels", [])]) or ["Outros"]
        artists = unique_non_empty([str(name) for name in example.get("artist_names", [])])
        hints = unique_non_empty([str(hint) for hint in example.get("hints", [])])
        album_name = str(example.get("album_name", "")).strip()
        parts = [
            f"Track title: {example.get('track_name', '')}",
            f"Artist(s): {', '.join(artists) if artists else 'unknown'}",
            f"Album: {album_name}" if album_name else "",
            f"Confirmed predominant labels: {', '.join(labels)}",
            "Rule: prioritize Pop over Rock for radio-mainstream, commercial pop, pop-rock leve, synth-pop or dance-pop tracks.",
            f"Signals: {', '.join(hints)}" if hints else "",
        ]
        return "\n".join(part for part in parts if part)

    def _seed_priority_examples(self) -> None:
        seeded = 0
        for example in PRIORITY_FEEDBACK_EXAMPLES:
            track_name = str(example.get("track_name", "")).strip()
            artist_names = unique_non_empty([str(name) for name in example.get("artist_names", [])])
            if not track_name:
                continue
            sample_key = f"feedback::{normalize_text(track_name)}::{normalize_text(' '.join(artist_names))}"
            if self.record_example(
                sample_key=sample_key,
                text=self._build_priority_example_text(example),
                labels=[str(label) for label in example.get("labels", [])],
                source="feedback-seed",
                confidence=0.99,
                weight=safe_float(example.get("weight"), 4.0),
            ):
                seeded += 1
        if seeded:
            self._save_dataset(force=True)
            self.logger(f"Exemplos prioritários carregados para o TensorFlow | novos={seeded}", level="INFO")

    def maybe_train(self, force: bool = False, background: bool = True) -> bool:
        if not self.enabled:
            return False
        if len(self.samples_by_key) < self.min_samples:
            return False
        _, distinct_count, dominant_ratio = self._label_stats()
        if distinct_count < self.min_distinct_labels or dominant_ratio > self.max_dominant_label_ratio:
            return False
        if not force and self.pending_samples < self.train_every and self.model is not None:
            return False
        if self.training_thread and self.training_thread.is_alive():
            return False

        if background:
            self.training_thread = threading.Thread(target=self._train_model_impl, daemon=True)
            self.training_thread.start()
            self.logger(
                f"Treino incremental TensorFlow agendado | amostras={len(self.samples_by_key)} | novas={self.pending_samples}",
                level="INFO",
            )
            return True

        return self._train_model_impl()

    def _train_model_impl(self) -> bool:
        if not self.enabled:
            return False

        with self.training_lock:
            if len(self.samples_by_key) < self.min_samples:
                return False

            self._save_dataset(force=True)
            started_at = time.perf_counter()
            samples = list(self.samples_by_key.values())
            texts = [prepare_text_for_model(str(sample.get("text", ""))) for sample in samples]
            sample_weights = [min(max(safe_float(sample.get("weight"), 1.0), 0.25), 8.0) for sample in samples]
            labels_matrix: list[list[float]] = []
            for sample in samples:
                row = [0.0] * len(self.labels)
                for label in sample.get("labels", []):
                    index = self.label_to_index.get(label)
                    if index is not None:
                        row[index] = 1.0
                labels_matrix.append(row)

            try:
                tf.keras.backend.clear_session()  # type: ignore[attr-defined]
                text_tensor = tf.constant(texts, dtype=tf.string)  # type: ignore[attr-defined]
                label_tensor = tf.constant(labels_matrix, dtype=tf.float32)  # type: ignore[attr-defined]
                weight_tensor = tf.constant(sample_weights, dtype=tf.float32)  # type: ignore[attr-defined]

                vectorizer = tf.keras.layers.TextVectorization(  # type: ignore[attr-defined]
                    max_tokens=6000,
                    ngrams=2,
                    output_mode="tf-idf",
                )
                vectorizer.adapt(text_tensor)

                model = tf.keras.Sequential(  # type: ignore[attr-defined]
                    [
                        tf.keras.Input(shape=(1,), dtype=tf.string),  # type: ignore[attr-defined]
                        vectorizer,
                        tf.keras.layers.Dense(128, activation="relu"),  # type: ignore[attr-defined]
                        tf.keras.layers.Dropout(0.15),  # type: ignore[attr-defined]
                        tf.keras.layers.Dense(64, activation="relu"),  # type: ignore[attr-defined]
                        tf.keras.layers.Dense(len(self.labels), activation="sigmoid"),  # type: ignore[attr-defined]
                    ]
                )
                model.compile(optimizer="adam", loss="binary_crossentropy")
                model.fit(
                    text_tensor,
                    label_tensor,
                    sample_weight=weight_tensor,
                    epochs=self.epochs,
                    batch_size=min(self.batch_size, max(1, len(texts))),
                    verbose=0,
                )
                model.save(self.model_path, include_optimizer=False)
                self._write_json_file(
                    self.meta_path,
                    {
                        "sample_count": len(samples),
                        "labels": self.labels,
                        "updated_at": int(time.time()),
                        "version": self.model_version,
                    },
                )
                self.model = model
                self.pending_samples = 0
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                self.last_train_summary = {
                    "sample_count": len(samples),
                    "elapsed_ms": round(elapsed_ms, 2),
                }
                self.logger(
                    f"Treino incremental TensorFlow executado | amostras={len(samples)} | epochs={self.epochs} | tempo={elapsed_ms:.0f}ms",
                    level="INFO",
                )
                return True
            except Exception as exc:
                self.logger(f"Falha no treino TensorFlow: {exc}", level="ERROR")
                return False

    def predict(self, text: str) -> dict[str, Any] | None:
        prepared_text = prepare_text_for_model(text)
        if not self.is_ready() or not prepared_text:
            return None
        try:
            inference_tensor = tf.constant([prepared_text], dtype=tf.string)  # type: ignore[attr-defined]
            raw_scores = self.model.predict(inference_tensor, verbose=0)[0].tolist()
        except Exception as exc:
            self.logger(f"Falha na inferência TensorFlow: {exc}", level="ERROR")
            return None

        ranked = sorted(zip(self.labels, raw_scores), key=lambda item: item[1], reverse=True)
        labels = [label for label, score in ranked if score >= 0.35][:2]
        if not labels and ranked:
            labels = [ranked[0][0]]
        confidence = round(float(ranked[0][1]) if ranked else 0.0, 4)
        return {
            "labels": labels or ["Outros"],
            "confidence": confidence,
            "scores": {label: round(float(score), 4) for label, score in ranked[:4]},
        }

    def flush(self, wait: bool = False) -> None:
        self._save_dataset(force=True)
        started = self.maybe_train(force=False, background=not wait)
        if wait and self.training_thread and self.training_thread.is_alive():
            self.training_thread.join(timeout=20)
        elif wait and not started:
            self.maybe_train(force=False, background=False)


class HybridGenreClassifier:
    """AI-first music classifier with persistent cache and optional TensorFlow learning."""

    def __init__(
        self,
        request_func: RequestFunction,
        lastfm_api_key: str = "",
        huggingface_api_key: str = "",
        openai_api_key: str = "",
        provider: str = "auto",
        openai_model: str | None = None,
        always_use_ai: bool = False,
        verbose: bool | None = None,
    ) -> None:
        self.request = request_func
        self.lastfm_api_key = lastfm_api_key.strip()
        self.huggingface_api_key = huggingface_api_key.strip()
        self.openai_api_key = openai_api_key.strip()
        self.provider = self._normalize_provider(provider)
        self.openai_model = (openai_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")).strip()
        self.always_use_ai = always_use_ai
        self.verbose = (
            bool(verbose)
            if verbose is not None
            else os.getenv("GENRE_CLASSIFIER_VERBOSE", "true").strip().lower() in {"1", "true", "yes", "y", "s"}
        )
        self.base_dir = Path(__file__).resolve().parents[1]
        self.data_dir = self.base_dir / "data"
        self.model_dir = self.base_dir / "models"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.data_dir / "genre_prediction_cache.json"
        self.reference_path = self.data_dir / REFERENCE_LIBRARY_FILENAME
        self.reference_entries = self._load_reference_library()
        self.reference_lookup, self.reference_track_only = self._build_reference_lookup(self.reference_entries)
        self.reference_profiles = self._build_reference_profiles(self.reference_entries)
        self.reference_prompt = self._build_reference_prompt()
        self.lastfm_cache: dict[str, list[str]] = {}
        self.ai_cache: dict[str, dict[str, float]] = {}
        self.session_cache: dict[str, dict[str, Any]] = self._load_prediction_cache()
        self.cache_dirty = 0
        self.cache_flush_every = max(1, int(os.getenv("GENRE_CACHE_FLUSH_EVERY", "5")))
        self.provider_state: dict[str, dict[str, float | int]] = {
            "openai": {"failures": 0, "disabled_until": 0.0},
            "huggingface": {"failures": 0, "disabled_until": 0.0},
        }
        self.provider_metrics: dict[str, dict[str, float | int]] = {
            "openai": {"calls": 0, "successes": 0, "failures": 0, "avg_ms": 0.0, "last_confidence": 0.0},
            "huggingface": {"calls": 0, "successes": 0, "failures": 0, "avg_ms": 0.0, "last_confidence": 0.0},
        }
        self.tf_learner = TensorFlowGenreLearner(CANONICAL_LABELS, self.data_dir, self.model_dir, self._log)
        seeded_reference_examples = self._seed_reference_examples()
        if seeded_reference_examples and self.tf_learner.model is None:
            self.tf_learner.maybe_train(force=True, background=True)
        self.tf_revalidation_threshold = self.tf_learner.prediction_threshold
        self.ai_request_timeout = max(2.0, float(os.getenv("GENRE_AI_TIMEOUT", "4")))
        self.ai_request_retries = max(0, int(os.getenv("GENRE_AI_MAX_RETRIES", "0")))
        self.provider_failure_threshold = max(1, int(os.getenv("GENRE_PROVIDER_FAILURE_THRESHOLD", "2")))
        self.provider_cooldown_seconds = max(30, int(os.getenv("GENRE_PROVIDER_COOLDOWN_SECONDS", "300")))
        self.remote_confidence_threshold = min(0.99, max(0.4, float(os.getenv("GENRE_AI_PROVIDER_THRESHOLD", "0.58"))))

        configured = ", ".join(self._available_providers()) or "nenhuma"
        tf_status = "ativo" if self.tf_learner.is_ready() else ("coletando dados" if self.tf_learner.enabled else "indisponível")
        self._log(
            f"Classificador IA pronto | provider={self.provider} | IAs ativas: {configured} | TensorFlow={tf_status}",
            level="CONFIG",
        )

    def _normalize_provider(self, provider: str | None) -> str:
        raw = (provider or "auto").strip().lower()
        normalized = re.sub(r"[\s_-]+", "", raw)
        if normalized in {"openai", "gpt", "chatgpt"}:
            return "openai"
        if normalized in {"huggingface", "hf"}:
            return "huggingface"
        if normalized in {"auto", "ai", "hybrid"}:
            return "auto"
        return "auto"

    def _log(self, message: str, level: str = "INFO") -> None:
        if not self.verbose:
            return
        print(f"\n[IA:{level}] {message}", flush=True)

    def _load_prediction_cache(self) -> dict[str, dict[str, Any]]:
        if not self.cache_path.exists():
            return {}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as file:
                payload = json.load(file)
            if isinstance(payload, dict):
                items = payload.get("items", payload)
                if isinstance(items, dict):
                    return {
                        key: value
                        for key, value in items.items()
                        if isinstance(value, dict)
                        and not self._is_low_value_result(value)
                        and str((value.get("metadata") or {}).get("classifier_version", "")) == CLASSIFIER_CACHE_VERSION
                    }
        except Exception:
            pass
        return {}

    def _persist_prediction_cache(self, force: bool = False) -> None:
        if not force and self.cache_dirty < self.cache_flush_every:
            return
        with open(self.cache_path, "w", encoding="utf-8") as file:
            json.dump({"items": self.session_cache}, file, ensure_ascii=False, indent=2)
        self.cache_dirty = 0

    def _is_low_value_result(self, payload: dict[str, Any] | None) -> bool:
        if not isinstance(payload, dict):
            return True
        labels = payload.get("labels") if isinstance(payload.get("labels"), list) else []
        normalized_labels = [self._canonicalize_label(str(label)) or str(label).strip() for label in labels]
        confidence = safe_float(payload.get("confidence"), 0.0)
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        provider = str(metadata.get("provider", "")).strip().lower()
        provider_scores = metadata.get("provider_scores") if isinstance(metadata.get("provider_scores"), dict) else {}
        return normalized_labels == ["Outros"] and confidence <= 0.05 and provider in {"", "none", "cache"} and not provider_scores

    def _parse_reference_item(self, item: Any) -> tuple[str, list[str]]:
        if isinstance(item, dict):
            track_name = str(item.get("track_name", "")).strip()
            artist_names = unique_non_empty([str(name) for name in item.get("artist_names", [])])
            artist_label = str(item.get("artist", "")).strip()
            if artist_label and not artist_names:
                artist_names = unique_non_empty(re.split(r"\s*,\s*|\s*&\s*", artist_label))
            return track_name, artist_names

        text = str(item or "").strip()
        if not text:
            return "", []
        parts = re.split(r"\s+[—-]\s+", text, maxsplit=1)
        track_name = parts[0].strip()
        if len(parts) == 1:
            return track_name, []
        artist_label = parts[1].strip()
        artist_names = unique_non_empty(re.split(r"\s*,\s*|\s*&\s*", artist_label))
        if not artist_names and artist_label:
            artist_names = [artist_label]
        return track_name, artist_names

    def _load_reference_library(self) -> dict[str, dict[str, Any]]:
        if not self.reference_path.exists():
            return {}
        try:
            with open(self.reference_path, "r", encoding="utf-8") as file:
                payload = json.load(file)
        except Exception as exc:
            self._log(f"Falha ao carregar biblioteca de referência: {exc}", level="WARN")
            return {}

        entries: dict[str, dict[str, Any]] = {}
        if not isinstance(payload, dict):
            return entries

        for raw_label, items in payload.items():
            canonical_label = self._canonicalize_label(str(raw_label))
            if canonical_label not in CANONICAL_LABELS or not isinstance(items, list):
                continue
            for item in items:
                track_name, artist_names = self._parse_reference_item(item)
                if not track_name:
                    continue
                entry_key = f"{normalize_text(track_name)}::{normalize_text(' '.join(artist_names))}"
                entry = entries.setdefault(
                    entry_key,
                    {
                        "track_name": track_name,
                        "artist_names": artist_names,
                        "labels": [],
                    },
                )
                if canonical_label not in entry["labels"]:
                    entry["labels"].append(canonical_label)
        if entries:
            self._log(f"Biblioteca de referência carregada | exemplos={len(entries)}", level="INFO")
        return entries

    def _build_reference_lookup(
        self,
        entries: dict[str, dict[str, Any]],
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        by_track_artist = dict(entries)
        grouped_by_track: dict[str, list[dict[str, Any]]] = {}
        for entry in entries.values():
            track_key = normalize_text(entry.get("track_name", ""))
            if not track_key:
                continue
            grouped_by_track.setdefault(track_key, []).append(entry)

        by_track_only = {
            track_key: matches[0]
            for track_key, matches in grouped_by_track.items()
            if len(matches) == 1 and len(matches[0].get("labels", [])) == 1
        }
        return by_track_artist, by_track_only

    def _build_reference_profiles(self, entries: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        profiles: dict[str, dict[str, Any]] = {
            label: {"artists": set(), "tracks": set(), "samples": []}
            for label in CANONICAL_LABELS
            if label != "Outros"
        }
        for entry in entries.values():
            track_name = str(entry.get("track_name", "")).strip()
            artists = unique_non_empty([str(name) for name in entry.get("artist_names", [])])
            sample_label = f"{track_name} — {', '.join(artists)}" if track_name and artists else track_name
            for label in entry.get("labels", []):
                if label not in profiles:
                    continue
                profile = profiles[label]
                if track_name:
                    profile["tracks"].add(normalize_text(track_name))
                    if sample_label and sample_label not in profile["samples"] and len(profile["samples"]) < 4:
                        profile["samples"].append(sample_label)
                for artist_name in artists:
                    artist_key = normalize_text(artist_name)
                    if artist_key:
                        profile["artists"].add(artist_key)
        return profiles

    def _build_reference_prompt(self, max_examples_per_genre: int = 3) -> str:
        lines = [
            "Classification rules:",
            "1. Compare the song against the user reference lists and choose only the single most probable dominant genre.",
            "2. Consider instrumental palette, rhythm/BPM feel, predominant timbres, vocal structure, lyrical theme, production style, era and sonic aesthetics.",
            "3. Do not rely only on the artist name; use it as a weak supporting clue only when the sound and cultural context agree.",
            "4. In hybrid cases, prefer the sonically and culturally dominant style rather than the official marketing tag.",
            "Reference prototypes by genre:",
        ]
        for label in CANONICAL_LABELS:
            if label == "Outros":
                continue
            hints = GENRE_PROTOTYPE_HINTS.get(label, {})
            summary = str(hints.get("summary", "")).strip()
            samples = self.reference_profiles.get(label, {}).get("samples", [])[:max_examples_per_genre]
            sample_text = "; ".join(samples)
            line = f"- {label}: {summary}"
            if sample_text:
                line += f" Exemplos: {sample_text}."
            lines.append(line.strip())
        return "\n".join(lines)

    def _build_reference_example_text(self, entry: dict[str, Any]) -> str:
        labels = unique_non_empty([str(label) for label in entry.get("labels", [])]) or ["Outros"]
        artists = unique_non_empty([str(name) for name in entry.get("artist_names", [])])
        parts = [
            f"Track title: {entry.get('track_name', '')}",
            f"Artist(s): {', '.join(artists) if artists else 'unknown'}",
            f"Allowed labels: {', '.join(CANONICAL_LABELS)}",
            f"Curated predominant labels: {', '.join(labels)}",
            "This is a trusted reference example provided by the user to calibrate genre predominance.",
        ]
        return "\n".join(part for part in parts if part)

    def _seed_reference_examples(self) -> int:
        if not self.reference_entries:
            return 0
        seeded = 0
        for entry_key, entry in self.reference_entries.items():
            labels = [label for label in entry.get("labels", []) if label in self.tf_learner.label_to_index]
            if not labels:
                continue
            weight = 2.2 if len(labels) == 1 else 1.3
            if self.tf_learner.record_example(
                sample_key=f"reference::{entry_key}",
                text=self._build_reference_example_text(entry),
                labels=labels,
                source="reference-library",
                confidence=0.985,
                weight=weight,
            ):
                seeded += 1
        if seeded:
            self._log(f"Referências musicais incorporadas ao treino | novas={seeded}", level="INFO")
        return seeded

    def _lookup_reference_match(self, track_name: str, artist_names: list[str]) -> dict[str, Any] | None:
        track_key = normalize_text(track_name)
        normalized_artists = {normalize_text(name) for name in unique_non_empty(artist_names) if normalize_text(name)}
        artist_key = normalize_text(" ".join(unique_non_empty(artist_names)))
        combined_key = f"{track_key}::{artist_key}"
        entry = self.reference_lookup.get(combined_key)
        if entry and len(entry.get("labels", [])) == 1:
            return entry

        if track_key and normalized_artists:
            for candidate in self.reference_lookup.values():
                if normalize_text(candidate.get("track_name", "")) != track_key:
                    continue
                candidate_artists = {
                    normalize_text(name)
                    for name in candidate.get("artist_names", [])
                    if normalize_text(name)
                }
                if candidate_artists.intersection(normalized_artists) and len(candidate.get("labels", [])) == 1:
                    return candidate

        if not normalized_artists:
            fallback = self.reference_track_only.get(track_key)
            if fallback and len(fallback.get("labels", [])) == 1:
                return fallback
        return None

    def _metadata_candidates(self, value: str) -> list[tuple[str, float]]:
        normalized = normalize_text(value)
        if not normalized:
            return []

        tokens = [token for token in re.split(r"[\s/&-]+", normalized) if token]
        candidates: list[tuple[str, float]] = [(normalized, 1.0)]
        max_ngram = min(3, len(tokens))
        for size in range(max_ngram, 0, -1):
            base_weight = {3: 0.78, 2: 0.62, 1: 0.44}.get(size, 0.4)
            for index in range(0, len(tokens) - size + 1):
                phrase = " ".join(tokens[index:index + size]).strip()
                if phrase and phrase != normalized:
                    candidates.append((phrase, base_weight))
        return candidates

    def _lookup_priority_feedback(self, track_name: str, artist_names: list[str]) -> dict[str, Any] | None:
        normalized_track = normalize_text(track_name)
        normalized_artists = {normalize_text(name) for name in artist_names if normalize_text(name)}
        if not normalized_track:
            return None

        for example in PRIORITY_FEEDBACK_EXAMPLES:
            if normalize_text(str(example.get("track_name", ""))) != normalized_track:
                continue
            example_artists = {
                normalize_text(str(name))
                for name in example.get("artist_names", [])
                if normalize_text(str(name))
            }
            if not example_artists or normalized_artists.intersection(example_artists):
                return example
        return None

    def _is_brazilian_context(
        self,
        track_name: str,
        artist_names: list[str],
        album_name: str,
        spotify_genres: list[str],
        lastfm_tags: list[str],
    ) -> bool:
        context = normalize_text(" ".join(artist_names + spotify_genres + lastfm_tags + [track_name, album_name]))
        brazilian_terms = {
            "brasil", "brazil", "brazilian", "mpb", "sertanejo", "pagode", "samba",
            "funk carioca", "funk brasileiro", "rock nacional", "trap nacional", "brazilian reggae",
            "brazilian pop", "brazilian hip hop", "brazilian trap",
        }
        portuguese_markers = {
            " amor ", " saudade ", " voce ", " vc ", " pra ", " meu ", " minha ",
            " tempo ", " noite ", " coracao ", " exodo ", " baile ", " favela ",
        }
        padded = f" {context} "
        return any(term in context for term in brazilian_terms) or any(marker in padded for marker in portuguese_markers)

    def _should_trust_tf_prediction(
        self,
        tf_prediction: dict[str, Any] | None,
        metadata_scores: dict[str, float],
        max_labels: int = 2,
    ) -> bool:
        if not tf_prediction or not self.tf_learner.is_ready():
            return False

        tf_labels = [self._canonicalize_label(label) or str(label) for label in tf_prediction.get("labels", [])]
        tf_confidence = safe_float(tf_prediction.get("confidence"), 0.0)
        if tf_confidence < self.tf_revalidation_threshold or not tf_labels:
            return False
        if tf_labels[0] == "Outros":
            return False

        if metadata_scores:
            metadata_labels, metadata_confidence, _ = self._scores_to_labels(metadata_scores, max_labels=max_labels)
            if metadata_confidence >= 0.68:
                if tf_labels[0] not in metadata_labels:
                    return False
                if "Outros" in tf_labels and "Outros" not in metadata_labels:
                    return False
                if tf_labels[0] == "Eletrônica" and metadata_labels[0] in {"Rap", "Boom Bap", "Reggae", "MPB", "Pop", "Rock", "Rock Nacional", "Trap", "Trap Nacional"}:
                    return False

        return True

    def _should_accept_tf_fallback(self, tf_prediction: dict[str, Any] | None) -> bool:
        if not tf_prediction:
            return False
        tf_labels = [self._canonicalize_label(label) or str(label) for label in tf_prediction.get("labels", [])]
        tf_confidence = safe_float(tf_prediction.get("confidence"), 0.0)
        min_confidence = max(0.55, min(self.tf_revalidation_threshold, 0.72))
        return bool(tf_labels) and tf_labels[0] != "Outros" and tf_confidence >= min_confidence

    def _classify_from_reference_prototypes(
        self,
        track_name: str,
        artist_names: list[str],
        album_name: str,
        spotify_genres: list[str],
        lastfm_tags: list[str],
    ) -> tuple[dict[str, float], dict[str, list[str]]]:
        metadata_context = normalize_text(" ".join(unique_non_empty(spotify_genres + lastfm_tags + [album_name])))
        cultural_context = normalize_text(" ".join(unique_non_empty(spotify_genres + lastfm_tags + [album_name, track_name])))
        artist_keys = {normalize_text(name) for name in artist_names if normalize_text(name)}
        if not metadata_context and not cultural_context and not artist_keys:
            return {}, {}

        aspect_weights = {
            "keywords": 0.34,
            "instrumental": 0.22,
            "rhythm": 0.22,
            "timbres": 0.18,
            "vocal": 0.17,
            "themes": 0.14,
            "production": 0.16,
            "era": 0.08,
        }
        scores: dict[str, float] = {}
        evidence: dict[str, list[str]] = {}

        for label, hints in GENRE_PROTOTYPE_HINTS.items():
            label_score = 0.0
            label_evidence: list[str] = []
            for aspect_name, weight in aspect_weights.items():
                target_context = cultural_context if aspect_name == "themes" else metadata_context
                if not target_context:
                    continue
                matched_terms = []
                for term in hints.get(aspect_name, []):
                    term_key = normalize_text(term)
                    if term_key and term_key in target_context:
                        matched_terms.append(term)
                if matched_terms:
                    label_score += weight + (0.03 * max(0, len(matched_terms) - 1))
                    label_evidence.append(f"{aspect_name}: {', '.join(matched_terms[:2])}")

            profile = self.reference_profiles.get(label, {})
            reference_artists = profile.get("artists", set())
            if artist_keys and reference_artists:
                overlaps = sorted(artist_keys.intersection(reference_artists))
                if overlaps:
                    boost = 0.14 if label_score > 0 else 0.05
                    label_score += boost
                    matched_artist = next((artist for artist in artist_names if normalize_text(artist) in overlaps), overlaps[0])
                    label_evidence.append(f"artista de referência: {matched_artist}")

            if label_score > 0:
                scores[label] = min(0.99, round(label_score, 4))
                evidence[label] = label_evidence

        return scores, evidence

    def _apply_style_guardrails(
        self,
        scores: dict[str, float],
        evidence: dict[str, list[str]],
        track_name: str,
        artist_names: list[str],
        album_name: str,
        spotify_genres: list[str],
        lastfm_tags: list[str],
    ) -> dict[str, float]:
        adjusted = {label: round(safe_float(score), 4) for label, score in scores.items() if safe_float(score) > 0}
        if not adjusted:
            return adjusted

        context = normalize_text(" ".join(artist_names + spotify_genres + lastfm_tags + [track_name, album_name]))
        is_brazilian_context = self._is_brazilian_context(track_name, artist_names, album_name, spotify_genres, lastfm_tags)
        pop_values = [normalize_text(value) for value in evidence.get("Pop", [])]
        rock_values = [normalize_text(value) for value in evidence.get("Rock", [])]
        rap_values = [normalize_text(value) for value in evidence.get("Rap", []) + evidence.get("Boom Bap", [])]

        pop_terms = {
            "dance pop", "synth pop", "indie pop", "soft pop", "electropop",
            "mainstream pop", "commercial pop", "radio pop", "pop rock", "chart hit",
        }
        weak_rock_terms = {"rock", "modern rock", "pop rock", "soft rock"}
        strong_rock_terms = {
            "alternative rock", "hard rock", "classic rock", "indie rock", "post grunge",
            "grunge", "emo", "emo rock", "pop punk", "punk rock", "garage rock",
        }
        boom_bap_terms = {
            "boom bap", "boombap", "old school hip hop", "old school rap", "classic hip hop",
            "golden age hip hop", "east coast hip hop", "sample-based",
        }
        modern_rap_terms = {"trap", "drill", "melodic rap", "pluggnb", "rage", "cloud rap"}
        trap_terms = {"trap", "trap soul", "country rap", "country trap", "drill", "rage", "cloud rap", "808"}
        trap_national_terms = {"trap nacional", "trap brasileiro", "brazilian trap", "br trap"}
        electronic_terms = {
            "edm", "electronic", "electronica", "house", "techno", "trance",
            "dubstep", "brostep", "electro house", "progressive house", "big room",
            "slap house", "festival", "club",
        }
        funk_terms = {
            "funk carioca", "baile funk", "mandelao", "mandelão", "tamborzao", "tamborzão",
            "gaiola", "medley da gaiola", "vapo", "rebola", "rebolando", "sentadona",
            "paredao", "paredão", "novinha", "rabetao", "rabetão",
        }
        forro_terms = {"forro", "forró", "piseiro", "pisadinha", "arrocha", "seresta", "vaquejada"}

        pop_friendly = any(any(term in value for term in pop_terms) for value in pop_values) or any(term in context for term in pop_terms)
        mainstream_band = any(artist in context for artist in MAINSTREAM_POP_PRIORITY_ARTISTS)
        strong_rock = any(any(term in value for term in strong_rock_terms) for value in rock_values) or any(term in context for term in strong_rock_terms)
        weak_rock_only = bool(rock_values) and not strong_rock and all(any(term in value for term in weak_rock_terms) for value in rock_values)
        electronic_signal = any(term in context for term in electronic_terms)
        funk_signal = is_brazilian_context and any(term in context for term in funk_terms)
        forro_signal = any(term in context for term in forro_terms)
        metal_terms = {
            "heavy metal", "thrash metal", "nu metal", "metalcore", "death metal",
            "black metal", "power metal", "groove metal", "progressive metal",
        }
        sertanejo_universitario_terms = {
            "sertanejo universitario", "sertanejo universitário", "balada boa", "camaro amarelo",
            "ai se eu te pego", "meteoro", "te esperando", "universitario pop",
        }
        sertanejo_moderno_terms = {
            "sofrencia", "sofrência", "feminejo", "agronejo", "leao", "leão",
            "infiel", "bloqueado", "boiadeira", "bombonzinho", "arranhao", "arranhão",
        }
        electronic_artist_signal = any(artist in context for artist in ELECTRONIC_PRIORITY_ARTISTS)
        metal_artist_signal = any(artist in context for artist in METAL_PRIORITY_ARTISTS) or any(term in context for term in metal_terms)
        boom_bap_artist_signal = is_brazilian_context and any(artist in context for artist in BOOM_BAP_PRIORITY_ARTISTS)
        sertanejo_universitario_signal = any(artist in context for artist in SERTANEJO_UNIVERSITARIO_PRIORITY_ARTISTS) or any(term in context for term in sertanejo_universitario_terms)
        sertanejo_moderno_signal = any(artist in context for artist in SERTANEJO_MODERNO_PRIORITY_ARTISTS) or any(term in context for term in sertanejo_moderno_terms)

        if pop_friendly or mainstream_band:
            adjusted["Pop"] = min(0.99, max(adjusted.get("Pop", 0.0), 0.76 if mainstream_band else 0.68) + (0.18 if mainstream_band else 0.1))
            if adjusted.get("Rock", 0.0) > 0 and (weak_rock_only or adjusted["Pop"] >= adjusted.get("Rock", 0.0)):
                adjusted["Rock"] = min(adjusted["Rock"], 0.22 if (mainstream_band or adjusted["Pop"] >= 0.86) else 0.27)

        if adjusted.get("Pop", 0.0) >= 0.85 and adjusted.get("Rock", 0.0) > 0 and not strong_rock:
            adjusted["Rock"] = min(adjusted["Rock"], 0.24)

        if (electronic_signal or electronic_artist_signal) and not mainstream_band:
            adjusted["Eletrônica"] = min(0.99, max(adjusted.get("Eletrônica", 0.0), 0.74 if electronic_artist_signal else adjusted.get("Eletrônica", 0.0)))
            if adjusted.get("Pop", 0.0) > 0 and adjusted.get("Eletrônica", 0.0) >= adjusted.get("Pop", 0.0):
                adjusted["Pop"] = min(adjusted["Pop"], 0.58)

        if adjusted.get("Rock", 0.0) > 0 and (adjusted.get("Metal", 0.0) > 0 or metal_artist_signal):
            adjusted["Metal"] = min(0.99, max(adjusted.get("Metal", 0.0), adjusted.get("Rock", 0.0) + 0.12, 0.78 if metal_artist_signal else 0.0))
            adjusted["Rock"] = min(adjusted["Rock"], 0.38 if metal_artist_signal else 0.52)

        if adjusted.get("Sertanejo", 0.0) > 0 or adjusted.get("Sertanejo Universitário", 0.0) > 0:
            if sertanejo_universitario_signal and not sertanejo_moderno_signal:
                adjusted["Sertanejo Universitário"] = min(0.99, max(adjusted.get("Sertanejo Universitário", 0.0), adjusted.get("Sertanejo", 0.0) + 0.1, 0.74))
                if adjusted.get("Sertanejo", 0.0) > 0:
                    adjusted["Sertanejo"] = min(adjusted["Sertanejo"], 0.44)
            elif sertanejo_moderno_signal:
                adjusted["Sertanejo"] = min(0.99, max(adjusted.get("Sertanejo", 0.0), adjusted.get("Sertanejo Universitário", 0.0) + 0.1, 0.76))
                if adjusted.get("Sertanejo Universitário", 0.0) > 0:
                    adjusted["Sertanejo Universitário"] = min(adjusted["Sertanejo Universitário"], 0.46)

        if adjusted.get("Eletrônica", 0.0) > 0 and not electronic_signal:
            competing_non_electronic = max(
                adjusted.get("Pop", 0.0),
                adjusted.get("Rap", 0.0),
                adjusted.get("Trap", 0.0),
                adjusted.get("Trap Nacional", 0.0),
                adjusted.get("Funk", 0.0),
                adjusted.get("Rock", 0.0),
                adjusted.get("Rock Nacional", 0.0),
                adjusted.get("Pagode", 0.0),
                adjusted.get("Samba", 0.0),
                adjusted.get("MPB", 0.0),
            )
            if competing_non_electronic >= 0.32:
                adjusted["Eletrônica"] = min(adjusted["Eletrônica"], 0.24)

        if adjusted.get("Reggae", 0.0) > 0 and adjusted.get("Pop", 0.0) > 0 and (pop_friendly or mainstream_band or electronic_signal):
            adjusted["Pop"] = min(0.99, max(adjusted["Pop"], adjusted["Reggae"] + 0.08))
            adjusted["Reggae"] = min(adjusted["Reggae"], 0.34)

        if funk_signal:
            adjusted["Funk"] = min(0.99, max(adjusted.get("Funk", 0.0), 0.72) + 0.08)
            if adjusted.get("Pagode", 0.0) > 0:
                adjusted["Pagode"] = min(adjusted["Pagode"], 0.26)
            if adjusted.get("Samba", 0.0) > 0:
                adjusted["Samba"] = min(adjusted["Samba"], 0.22)

        if forro_signal and not funk_signal:
            for label in ("Samba", "Pagode", "Sertanejo", "Sertanejo Universitário", "MPB"):
                if adjusted.get(label, 0.0) > 0:
                    adjusted[label] = min(adjusted[label], 0.18)
            if max(adjusted.values(), default=0.0) < 0.28:
                return {}

        trap_signal = any(term in context for term in trap_terms)
        trap_national_signal = is_brazilian_context and any(term in context for term in trap_national_terms)
        boom_bap_signal = any(any(term in value for term in boom_bap_terms) for value in rap_values) or any(term in context for term in boom_bap_terms)
        modern_rap_signal = any(any(term in value for term in modern_rap_terms) for value in rap_values) or any(term in context for term in modern_rap_terms)

        if boom_bap_artist_signal and not modern_rap_signal:
            adjusted["Boom Bap"] = min(0.99, max(adjusted.get("Boom Bap", 0.0), adjusted.get("Rap", 0.0) + 0.12, 0.74))
            if adjusted.get("Rap", 0.0) > 0:
                adjusted["Rap"] = min(adjusted["Rap"], 0.46)

        if adjusted.get("Trap", 0.0) > 0 and adjusted.get("Rap", 0.0) > 0 and trap_signal:
            adjusted["Trap"] = min(0.99, max(adjusted["Trap"], adjusted["Rap"] + 0.08))
            adjusted["Rap"] = min(adjusted["Rap"], 0.58)

        if adjusted.get("Trap Nacional", 0.0) > 0 and (adjusted.get("Trap", 0.0) > 0 or adjusted.get("Rap", 0.0) > 0) and trap_national_signal:
            dominant_base = max(adjusted.get("Trap", 0.0), adjusted.get("Rap", 0.0), adjusted.get("Trap Nacional", 0.0))
            adjusted["Trap Nacional"] = min(0.99, dominant_base + 0.1)
            if adjusted.get("Trap", 0.0) > 0:
                adjusted["Trap"] = min(adjusted["Trap"], 0.64)
            if adjusted.get("Rap", 0.0) > 0:
                adjusted["Rap"] = min(adjusted["Rap"], 0.52)

        if adjusted.get("Boom Bap", 0.0) > 0 and (modern_rap_signal or not is_brazilian_context) and not boom_bap_signal:
            adjusted["Rap"] = min(0.99, max(adjusted.get("Rap", 0.0), adjusted.get("Boom Bap", 0.0) + 0.16))
            adjusted["Boom Bap"] = min(adjusted["Boom Bap"], 0.24)
        elif adjusted.get("Rap", 0.0) > 0 and boom_bap_signal and not modern_rap_signal and is_brazilian_context:
            adjusted["Boom Bap"] = min(0.99, max(adjusted.get("Boom Bap", 0.0), adjusted.get("Rap", 0.0) + 0.08))
            adjusted["Rap"] = min(adjusted["Rap"], 0.42)

        return {label: round(score, 4) for label, score in adjusted.items() if score > 0}

    def _classify_from_metadata(
        self,
        track_name: str,
        artist_names: list[str],
        album_name: str,
        spotify_genres: list[str],
        lastfm_tags: list[str],
    ) -> tuple[dict[str, float], dict[str, list[str]]]:
        scores: dict[str, float] = {}
        evidence: dict[str, list[str]] = {}
        brazilian_context = normalize_text(" ".join(artist_names + spotify_genres + lastfm_tags + [track_name, album_name]))
        is_brazilian_context = self._is_brazilian_context(track_name, artist_names, album_name, spotify_genres, lastfm_tags)
        grouped_sources = [
            (spotify_genres, 1.0),
            (lastfm_tags, 0.82),
            (artist_names, 0.35),
            ([album_name], 0.18),
            ([track_name], 0.12),
        ]

        for values, source_weight in grouped_sources:
            for raw_value in unique_non_empty(values):
                for phrase, phrase_weight in self._metadata_candidates(raw_value):
                    canonical = self._canonicalize_label(phrase)
                    if not canonical or canonical == "Outros":
                        continue
                    if canonical == "Trap Nacional" and not is_brazilian_context:
                        canonical = "Trap"
                    elif canonical == "Boom Bap" and not is_brazilian_context:
                        canonical = "Rap"
                    elif canonical == "Rock Nacional" and not is_brazilian_context:
                        canonical = "Rock"
                    elif canonical in {"Sertanejo Tradicional", "Sertanejo Universitário", "Sertanejo", "Samba", "Pagode", "MPB"} and not is_brazilian_context:
                        continue
                    if canonical == "Funk" and not any(term in brazilian_context for term in {"brasil", "brazil", "carioca", "mandelao", "favela", "funk brasileiro"}):
                        continue
                    increment = round(source_weight * phrase_weight, 4)
                    scores[canonical] = min(0.99, scores.get(canonical, 0.0) + increment)
                    evidence.setdefault(canonical, []).append(raw_value)

        prototype_scores, prototype_evidence = self._classify_from_reference_prototypes(
            track_name=track_name,
            artist_names=artist_names,
            album_name=album_name,
            spotify_genres=spotify_genres,
            lastfm_tags=lastfm_tags,
        )
        for label, score in prototype_scores.items():
            scores[label] = min(0.99, scores.get(label, 0.0) + score)
            evidence.setdefault(label, []).extend(prototype_evidence.get(label, []))

        guarded_scores = self._apply_style_guardrails(
            scores,
            evidence,
            track_name=track_name,
            artist_names=artist_names,
            album_name=album_name,
            spotify_genres=spotify_genres,
            lastfm_tags=lastfm_tags,
        )
        cleaned_scores = {label: round(score, 4) for label, score in sorted(guarded_scores.items(), key=lambda item: item[1], reverse=True)}
        cleaned_evidence = {label: unique_non_empty(values)[:4] for label, values in evidence.items()}
        return cleaned_scores, cleaned_evidence

    def _update_provider_metrics(self, provider_name: str, success: bool, elapsed_ms: float, confidence: float = 0.0) -> None:
        metrics = self.provider_metrics.setdefault(
            provider_name,
            {"calls": 0, "successes": 0, "failures": 0, "avg_ms": 0.0, "last_confidence": 0.0},
        )
        previous_calls = int(metrics.get("calls", 0))
        metrics["calls"] = previous_calls + 1
        metrics["avg_ms"] = round(((safe_float(metrics.get("avg_ms", 0.0)) * previous_calls) + elapsed_ms) / max(1, previous_calls + 1), 2)
        metrics["last_confidence"] = round(confidence, 4)
        if success:
            metrics["successes"] = int(metrics.get("successes", 0)) + 1
        else:
            metrics["failures"] = int(metrics.get("failures", 0)) + 1

    def _available_providers(self) -> list[str]:
        now = time.time()
        providers: list[str] = []
        if self.provider in {"auto", "huggingface"} and self.huggingface_api_key:
            state = self.provider_state.get("huggingface", {})
            if float(state.get("disabled_until", 0.0)) <= now:
                providers.append("huggingface")
        if self.provider in {"auto", "openai"} and self.openai_api_key:
            state = self.provider_state.get("openai", {})
            if float(state.get("disabled_until", 0.0)) <= now:
                providers.append("openai")

        if self.provider == "auto":
            providers.sort(key=self._provider_sort_key)
        return providers

    def _provider_sort_key(self, provider_name: str) -> tuple[float, float, int]:
        metrics = self.provider_metrics.get(provider_name, {})
        calls = int(metrics.get("calls", 0))
        successes = int(metrics.get("successes", 0))
        success_rate = successes / calls if calls else 0.5
        avg_ms = safe_float(metrics.get("avg_ms", 999.0), 999.0) if calls else 999.0
        base_priority = 0 if provider_name == "huggingface" else 1
        return (-success_rate, avg_ms, base_priority)

    def _mark_provider_success(self, provider_name: str) -> None:
        state = self.provider_state.setdefault(provider_name, {"failures": 0, "disabled_until": 0.0})
        state["failures"] = 0
        state["disabled_until"] = 0.0

    def _mark_provider_failure(self, provider_name: str, reason: str = "", cooldown_seconds: int | None = None) -> None:
        state = self.provider_state.setdefault(provider_name, {"failures": 0, "disabled_until": 0.0})
        state["failures"] = int(state.get("failures", 0)) + 1
        if cooldown_seconds is None and int(state["failures"]) >= self.provider_failure_threshold:
            cooldown_seconds = self.provider_cooldown_seconds
        if cooldown_seconds:
            state["disabled_until"] = time.time() + cooldown_seconds
            reason_text = f" Motivo: {reason}." if reason else ""
            self._log(
                f"Provider {provider_name} ficará em pausa por {int(cooldown_seconds)}s.{reason_text}",
                level="WARN",
            )

    def _canonicalize_label(self, label: str | None) -> str | None:
        normalized = normalize_text(label)
        if not normalized:
            return None

        if normalized in CANONICAL_ALIASES:
            return CANONICAL_ALIASES[normalized]

        compact = normalized.replace(" ", "").replace("-", "")
        for candidate in CANONICAL_LABELS:
            candidate_normalized = normalize_text(candidate)
            if normalized == candidate_normalized or compact == candidate_normalized.replace(" ", "").replace("-", ""):
                return candidate
        return None

    def _scores_to_labels(self, scores: dict[str, float], max_labels: int = 2) -> tuple[list[str], float, dict[str, float]]:
        cleaned: dict[str, float] = {}
        for label, score in scores.items():
            canonical = self._canonicalize_label(label)
            numeric_score = min(max(safe_float(score), 0.0), 1.0)
            if canonical and numeric_score > 0:
                cleaned[canonical] = max(cleaned.get(canonical, 0.0), round(numeric_score, 4))

        ranked = sorted(cleaned.items(), key=lambda item: item[1], reverse=True)
        labels = [label for label, score in ranked if score >= 0.28][:max_labels]
        if not labels and ranked:
            labels = [ranked[0][0]]
        if not labels:
            labels = ["Outros"]
        confidence = round(ranked[0][1], 4) if ranked else 0.0
        return labels, confidence, cleaned

    def _format_track_label(self, track_name: str, artist_names: list[str]) -> str:
        artist_label = ", ".join(artist_names) if artist_names else "Artista desconhecido"
        return f"{track_name} - {artist_label}"

    def _make_track_cache_key(
        self,
        track_name: str,
        artist_names: list[str],
        album_name: str,
        spotify_genres: list[str],
    ) -> str:
        parts = [
            normalize_text(track_name),
            normalize_text(" ".join(artist_names)),
            normalize_text(album_name),
            normalize_text(" ".join(spotify_genres)),
        ]
        return "||".join(parts)

    def _build_context(
        self,
        track_name: str,
        artist_names: list[str],
        album_name: str,
        spotify_genres: list[str],
        lastfm_tags: list[str],
        preview_url: str | None,
        lyrics: str | None = None,
    ) -> str:
        taxonomy_rules = (
            "Taxonomy rules: choose only the single dominant genre by comparing the track with the curated reference lists as sonic/cultural prototypes; "
            "consider instrumental palette, rhythm/BPM feel, predominant timbres, vocal structure, lyrical theme, production style, era and overall aesthetic; "
            "Trap Nacional only for Brazilian Portuguese trap; Trap for international trap; Rap for general rap that is not dominantly boom bap; "
            "Boom Bap for classic BR rap with dry drums, classic samples and old-school aesthetics; Funk only for Brazilian funk; "
            "Rock Nacional only for Brazilian rock; Rock only for international rock when the song itself has clear rock identity; "
            "prioritize Pop over Rock for mainstream radio songs, chart hits, dance-pop, synth-pop, commercial pop and light pop-rock; "
            "generic guitars, live drums or band format alone are not enough to classify as Rock; analyze the song itself, not the artist history."
        )
        parts = [
            f"Track title: {track_name}",
            f"Artist(s): {', '.join(artist_names) if artist_names else 'unknown'}",
            f"Allowed labels: {', '.join(CANONICAL_LABELS)}",
            taxonomy_rules,
            self.reference_prompt,
        ]
        if album_name:
            parts.append(f"Album: {album_name}")
        if spotify_genres:
            parts.append(f"Spotify genres: {', '.join(spotify_genres)}")
        if lastfm_tags:
            parts.append(f"Last.fm tags: {', '.join(lastfm_tags)}")
        if lyrics:
            parts.append(f"Lyrics excerpt: {lyrics[:700]}")
        parts.append(f"Preview available: {'yes' if preview_url else 'no'}")
        return "\n".join(parts)

    def _get_lastfm_tags(self, track_name: str, artist_names: list[str]) -> list[str]:
        if not self.lastfm_api_key or not track_name or not artist_names:
            return []

        cache_key = f"{normalize_text(track_name)}::{normalize_text(' '.join(artist_names))}"
        if cache_key in self.lastfm_cache:
            return self.lastfm_cache[cache_key]

        tags = self._fetch_lastfm_track_tags(track_name, artist_names[0])
        if not tags:
            tags = self._fetch_lastfm_artist_tags(artist_names[0])

        tags = unique_non_empty(tags)
        self.lastfm_cache[cache_key] = tags
        return tags

    def _fetch_lastfm_track_tags(self, track_name: str, artist_name: str) -> list[str]:
        response = self.request(
            "GET",
            "https://ws.audioscrobbler.com/2.0/",
            params={
                "method": "track.getTopTags",
                "api_key": self.lastfm_api_key,
                "artist": artist_name,
                "track": track_name,
                "format": "json",
                "autocorrect": 1,
            },
            _request_label="Last.fm track tags",
            _max_retries=1,
            _timeout=3,
        )
        if response is None or response.status_code != 200:
            return []
        try:
            payload = response.json()
            tags = payload.get("toptags", {}).get("tag", [])
            return [tag.get("name", "") for tag in tags[:8] if isinstance(tag, dict)]
        except Exception:
            return []

    def _fetch_lastfm_artist_tags(self, artist_name: str) -> list[str]:
        response = self.request(
            "GET",
            "https://ws.audioscrobbler.com/2.0/",
            params={
                "method": "artist.getTopTags",
                "api_key": self.lastfm_api_key,
                "artist": artist_name,
                "format": "json",
                "autocorrect": 1,
            },
            _request_label="Last.fm artist tags",
            _max_retries=1,
            _timeout=3,
        )
        if response is None or response.status_code != 200:
            return []
        try:
            payload = response.json()
            tags = payload.get("toptags", {}).get("tag", [])
            return [tag.get("name", "") for tag in tags[:8] if isinstance(tag, dict)]
        except Exception:
            return []

    def _extract_json_payload(self, content: str) -> dict[str, Any]:
        text = (content or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?", "", text).strip()
            text = re.sub(r"```$", "", text).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return {}

    def _scores_from_payload(self, payload: Any) -> dict[str, float]:
        output: dict[str, float] = {}
        if isinstance(payload, list):
            for index, item in enumerate(payload):
                if not isinstance(item, dict):
                    continue
                label = str(item.get("label", "")).strip()
                score = safe_float(item.get("score", 1.0 - (index * 0.15)), 0.0)
                output[label] = max(output.get(label, 0.0), score)
            return output

        if not isinstance(payload, dict):
            return output

        raw_scores = payload.get("scores")
        if isinstance(raw_scores, dict):
            for label, score in raw_scores.items():
                output[str(label).strip()] = max(output.get(str(label).strip(), 0.0), safe_float(score, 0.0))

        raw_labels = payload.get("labels")
        if isinstance(raw_labels, list):
            if raw_labels and isinstance(raw_labels[0], dict):
                for index, item in enumerate(raw_labels):
                    label = str(item.get("label", "")).strip()
                    score = safe_float(item.get("score", 1.0 - (index * 0.15)), 0.0)
                    output[label] = max(output.get(label, 0.0), score)
            else:
                score_list = payload.get("scores") if isinstance(payload.get("scores"), list) else []
                for index, label in enumerate(raw_labels):
                    score = safe_float(score_list[index], 1.0 - (index * 0.15)) if index < len(score_list) else 1.0 - (index * 0.15)
                    output[str(label).strip()] = max(output.get(str(label).strip(), 0.0), score)

        primary = payload.get("primary") or payload.get("genre") or payload.get("main_genre")
        secondary = payload.get("secondary") or payload.get("secondary_genre") or payload.get("style")
        if primary:
            output[str(primary).strip()] = max(output.get(str(primary).strip(), 0.0), safe_float(payload.get("primary_score"), 0.92) or 0.92)
        if secondary:
            output[str(secondary).strip()] = max(output.get(str(secondary).strip(), 0.0), safe_float(payload.get("secondary_score"), 0.68) or 0.68)
        return output

    def _classify_with_ai(
        self,
        context: str,
        track_name: str = "",
        artist_names: list[str] | None = None,
    ) -> tuple[dict[str, float], str]:
        cache_key = normalize_text(context)
        providers = self._available_providers()
        track_label = self._format_track_label(track_name or "Faixa desconhecida", artist_names or [])

        if cache_key in self.ai_cache:
            self._log(f"Usando resposta em cache de IA para: {track_label}", level="DEBUG")
            return self.ai_cache[cache_key], "cache"

        best_scores: dict[str, float] = {}
        best_provider = ""
        best_confidence = 0.0

        for provider_name in providers:
            provider_started = time.perf_counter()
            self._log(f"Iniciando requisição para IA ({provider_name}) | música: {track_label}")

            if provider_name == "openai":
                scores = self._classify_with_openai(context)
            else:
                scores = self._classify_with_huggingface(context)

            elapsed_ms = (time.perf_counter() - provider_started) * 1000
            labels, confidence, normalized_scores = self._scores_to_labels(scores)
            self._update_provider_metrics(provider_name, bool(normalized_scores), elapsed_ms, confidence)

            if normalized_scores:
                preview = ", ".join(f"{label}={score:.2f}" for label, score in list(normalized_scores.items())[:3])
                self._mark_provider_success(provider_name)
                self._log(
                    f"Resposta da IA recebida ({provider_name}) para {track_label} em {elapsed_ms:.0f}ms: {preview}",
                    level="INFO",
                )
                if confidence > best_confidence:
                    best_scores = normalized_scores
                    best_provider = provider_name
                    best_confidence = confidence
                if confidence >= self.remote_confidence_threshold:
                    self.ai_cache[cache_key] = normalized_scores
                    return normalized_scores, provider_name
                self._log(
                    f"Confiança do provider {provider_name} ficou em {confidence:.3f}; tentando próximo provider para revalidação.",
                    level="DEBUG",
                )
            else:
                self._log(
                    f"O provedor {provider_name} não retornou classificação válida para {track_label} ({elapsed_ms:.0f}ms).",
                    level="WARN",
                )

        if best_scores:
            self.ai_cache[cache_key] = best_scores
        return best_scores, best_provider

    def _classify_with_huggingface(self, context: str) -> dict[str, float]:
        response = self.request(
            "POST",
            "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli",
            headers={
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "inputs": context,
                "parameters": {
                    "candidate_labels": CANONICAL_LABELS,
                    "multi_label": True,
                    "hypothesis_template": "This track is mainly {} music.",
                },
            },
            _timeout=self.ai_request_timeout,
            _max_retries=self.ai_request_retries,
            _respect_retry_after=False,
            _max_backoff_wait=0.5,
            _request_label="Hugging Face zero-shot",
        )
        if response is None:
            self._mark_provider_failure("huggingface", "falha de rede")
            self._log("Falha de rede ao consultar o Hugging Face.", level="ERROR")
            return {}
        if response.status_code != 200:
            details = getattr(response, "text", "")[:240].strip()
            cooldown = 1800 if response.status_code in {401, 403, 404, 410} else (
                self.provider_cooldown_seconds if response.status_code == 429 else None
            )
            self._mark_provider_failure("huggingface", f"HTTP {response.status_code}", cooldown_seconds=cooldown)
            self._log(f"Hugging Face respondeu {response.status_code}. {details}", level="ERROR")
            return {}
        try:
            return self._scores_from_payload(response.json())
        except Exception as exc:
            self._mark_provider_failure("huggingface", "resposta inválida")
            self._log(f"Erro ao interpretar resposta do Hugging Face: {exc}", level="ERROR")
            return {}

    def _classify_with_openai(self, context: str) -> dict[str, float]:
        guidance_examples = (
            "Brazilian taxonomy rules:\n"
            "- Trap Nacional => only Brazilian Portuguese trap songs\n"
            "- Trap => international trap only\n"
            "- Rap => modern BR rap or general rap/hip-hop that is not boom bap\n"
            "- Boom Bap => classic BR rap with old school aesthetic, dry drums, sample-based beat\n"
            "- Funk => only Brazilian funk\n"
            "- Rock Nacional => Brazilian rock artists only\n"
            "- Rock => international rock only when the track has clear rock identity\n"
            "- Pop must win over Rock for mainstream radio tracks, pop-rock leve, commercial pop, chart hits, dance-pop, synth-pop and hook-driven songs\n"
            "- Do not classify as Rock just because there is guitar, acoustic drums, a band lineup, or because the artist once belonged to rock playlists\n"
            "- Analyze the specific song, not the artist career\n"
            "- Outros => songs outside all listed classes\n\n"
            "Examples:\n"
            "- Roar - Katy Perry => Pop\n"
            "- Maps - Maroon 5 => Pop\n"
            "- Payphone - Maroon 5 => Pop\n"
            "- High Hopes - Panic! At The Disco => Pop\n"
            "- Flowers - Miley Cyrus => Pop\n"
            "- Blank Space - Taylor Swift => Pop\n"
            "- Firework - Katy Perry => Pop\n"
            "- Counting Stars - OneRepublic => Pop\n"
            "- Wake Me Up - Avicii => Eletrônica, Pop\n"
            "- Take Me To Church - Hozier => Rock\n"
            "- Tokyo Drift - Teriyaki Boyz => Rap, Boom Bap\n"
            "- Old Town Road - Lil Nas X => Trap\n"
            "- BK => Rap\n"
            "- Racionais MC's => Boom Bap\n"
            "- Matuê => Trap Nacional\n"
            "- MC Ryan SP => Funk\n"
            "- Charlie Brown Jr. => Rock Nacional\n"
        )
        response = self.request(
            "POST",
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.openai_model,
                "temperature": 0.0,
                "max_tokens": 180,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a precise music genre classifier focused on Brazilian context, era, language and sonic aesthetics. "
                            "Use only the allowed labels and return JSON only. Respect the BR taxonomy rules exactly."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Allowed labels: {', '.join(CANONICAL_LABELS)}.\n"
                            f"{guidance_examples}\n"
                            "Return JSON in one of these formats:\n"
                            "{\"primary\":\"Pop\",\"secondary\":\"Eletrônica\",\"scores\":{\"Pop\":0.94,\"Eletrônica\":0.62}}\n"
                            "or\n"
                            "{\"labels\":[{\"label\":\"Pop\",\"score\":0.94},{\"label\":\"Eletrônica\",\"score\":0.62}]}\n\n"
                            f"Track context:\n{context}"
                        ),
                    },
                ],
            },
            _timeout=self.ai_request_timeout,
            _max_retries=self.ai_request_retries,
            _respect_retry_after=False,
            _max_backoff_wait=0.5,
            _request_label="OpenAI music classifier",
        )
        if response is None:
            self._mark_provider_failure("openai", "falha de rede")
            self._log("Falha de rede ao consultar a OpenAI.", level="ERROR")
            return {}
        if response.status_code != 200:
            details = getattr(response, "text", "")[:240].strip()
            cooldown = self.provider_cooldown_seconds if response.status_code == 429 else (
                1800 if response.status_code in {401, 403, 404} else None
            )
            self._mark_provider_failure("openai", f"HTTP {response.status_code}", cooldown_seconds=cooldown)
            self._log(f"OpenAI respondeu {response.status_code}. {details}", level="ERROR")
            return {}

        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            parsed = self._extract_json_payload(content)
            scores = self._scores_from_payload(parsed)
            if not scores:
                self._mark_provider_failure("openai", "resposta sem labels")
            return scores
        except Exception as exc:
            self._mark_provider_failure("openai", "resposta inválida")
            self._log(f"Erro ao interpretar resposta da OpenAI: {exc}", level="ERROR")
            return {}

    def _build_result(
        self,
        labels: list[str],
        confidence: float,
        source: str,
        provider_used: str,
        spotify_genres: list[str],
        lastfm_tags: list[str],
        preview_url: str | None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        primary_label = labels[0] if labels else "Outros"
        secondary_label = labels[1] if len(labels) > 1 else primary_label
        metadata = {
            "provider": provider_used,
            "spotify_genres": spotify_genres,
            "lastfm_tags": lastfm_tags,
            "audio_preview_available": bool(preview_url),
            "classifier_version": CLASSIFIER_CACHE_VERSION,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        return {
            "genre": primary_label,
            "style": primary_label,
            "subgenre": secondary_label,
            "labels": labels or ["Outros"],
            "confidence": round(confidence, 4),
            "source": source,
            "metadata": metadata,
        }

    def classify_track(
        self,
        track_name: str,
        artist_names: list[str],
        spotify_genres: list[str] | None = None,
        album_name: str = "",
        lyrics: str | None = None,
        preview_url: str | None = None,
        max_labels: int = 1,
    ) -> dict[str, Any]:
        started_at = time.perf_counter()
        spotify_genres = unique_non_empty(spotify_genres or [])
        artist_names = unique_non_empty(artist_names or [])
        track_label = self._format_track_label(track_name, artist_names)
        track_cache_key = self._make_track_cache_key(track_name, artist_names, album_name, spotify_genres)

        priority_feedback = self._lookup_priority_feedback(track_name, artist_names)
        if priority_feedback:
            feedback_labels = [label for label in priority_feedback.get("labels", []) if label in self.tf_learner.label_to_index] or ["Outros"]
            feedback_context = self._build_context(
                track_name=track_name,
                artist_names=artist_names,
                album_name=album_name,
                spotify_genres=spotify_genres,
                lastfm_tags=unique_non_empty([str(hint) for hint in priority_feedback.get("hints", [])]),
                preview_url=preview_url,
                lyrics=lyrics,
            )
            self.tf_learner.record_example(
                sample_key=f"feedback::{track_cache_key}",
                text=feedback_context,
                labels=feedback_labels,
                source="feedback",
                confidence=0.995,
                weight=safe_float(priority_feedback.get("weight"), 4.0),
            )
            result = self._build_result(
                labels=feedback_labels[:max_labels],
                confidence=0.995,
                source="Feedback",
                provider_used="feedback",
                spotify_genres=spotify_genres,
                lastfm_tags=unique_non_empty([str(hint) for hint in priority_feedback.get("hints", [])]),
                preview_url=preview_url,
                extra_metadata={
                    "feedback_priority": True,
                    "feedback_weight": safe_float(priority_feedback.get("weight"), 4.0),
                    "feedback_album": priority_feedback.get("album_name", ""),
                },
            )
            self.session_cache[track_cache_key] = result
            self.cache_dirty += 1
            self._persist_prediction_cache()
            self._log(f"Feedback prioritário aplicado: {track_label} -> {', '.join(result['labels'])}", level="RESULT")
            return result

        reference_match = self._lookup_reference_match(track_name, artist_names)
        if reference_match and not self.always_use_ai:
            reference_labels = reference_match.get("labels", ["Outros"])
            result = self._build_result(
                labels=reference_labels[:max_labels],
                confidence=0.985,
                source="Referência",
                provider_used="reference",
                spotify_genres=spotify_genres,
                lastfm_tags=[],
                preview_url=preview_url,
                extra_metadata={
                    "reference_match": True,
                    "reference_artists": reference_match.get("artist_names", []),
                },
            )
            self.tf_learner.record_example(
                sample_key=f"reference-runtime::{track_cache_key}",
                text=self._build_context(
                    track_name=track_name,
                    artist_names=artist_names,
                    album_name=album_name,
                    spotify_genres=spotify_genres,
                    lastfm_tags=[],
                    preview_url=preview_url,
                    lyrics=lyrics,
                ),
                labels=reference_labels,
                source="reference-runtime",
                confidence=0.985,
                weight=2.4,
            )
            self.session_cache[track_cache_key] = result
            self.cache_dirty += 1
            self._persist_prediction_cache()
            self._log(f"Referência curada aplicada: {track_label} -> {', '.join(result['labels'])}", level="RESULT")
            return result

        if track_cache_key in self.session_cache:
            cached = dict(self.session_cache[track_cache_key])
            if self._is_low_value_result(cached):
                self.session_cache.pop(track_cache_key, None)
                self.cache_dirty += 1
                self._log(f"Ignorando cache antigo sem confiança para: {track_label}", level="DEBUG")
            else:
                cached_metadata = dict(cached.get("metadata") or {})
                cached_metadata["cache_hit"] = True
                cached_metadata.setdefault("cached_source", cached.get("source"))
                cached["metadata"] = cached_metadata
                cached["source"] = "cache"
                self._log(f"Cache hit: {track_label} -> {', '.join(cached.get('labels', []))}", level="DEBUG")
                return cached

        self._log(f"Analisando música: {track_label}")
        base_context = self._build_context(
            track_name=track_name,
            artist_names=artist_names,
            album_name=album_name,
            spotify_genres=spotify_genres,
            lastfm_tags=[],
            preview_url=preview_url,
            lyrics=lyrics,
        )

        quick_metadata_scores, quick_metadata_evidence = self._classify_from_metadata(
            track_name=track_name,
            artist_names=artist_names,
            album_name=album_name,
            spotify_genres=spotify_genres,
            lastfm_tags=[],
        )
        quick_metadata_labels, quick_metadata_confidence, quick_metadata_scores = self._scores_to_labels(
            quick_metadata_scores,
            max_labels=max_labels,
        )
        if quick_metadata_scores and quick_metadata_confidence >= 0.9 and not self.always_use_ai:
            result = self._build_result(
                labels=quick_metadata_labels,
                confidence=quick_metadata_confidence,
                source="Metadados",
                provider_used="metadata",
                spotify_genres=spotify_genres,
                lastfm_tags=[],
                preview_url=preview_url,
                extra_metadata={
                    "metadata_scores": quick_metadata_scores,
                    "metadata_evidence": quick_metadata_evidence,
                    "fast_path": True,
                },
            )
            self.session_cache[track_cache_key] = result
            self.cache_dirty += 1
            self._persist_prediction_cache()
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            self._log(
                f"Categoria definida: {track_label} -> {', '.join(result['labels'])} | confiança={result['confidence']:.3f} | fonte=Metadados | tempo={elapsed_ms:.0f}ms",
                level="RESULT",
            )
            return result

        tf_prediction = self.tf_learner.predict(base_context)
        if tf_prediction:
            self._log(
                f"Inferência TensorFlow: {track_label} -> {', '.join(tf_prediction['labels'])} | confiança={tf_prediction['confidence']:.3f}",
                level="DEBUG",
            )
            if self._should_trust_tf_prediction(tf_prediction, quick_metadata_scores, max_labels=max_labels) and not self.always_use_ai:
                result = self._build_result(
                    labels=tf_prediction["labels"][:max_labels],
                    confidence=tf_prediction["confidence"],
                    source="TensorFlow",
                    provider_used="tensorflow",
                    spotify_genres=spotify_genres,
                    lastfm_tags=[],
                    preview_url=preview_url,
                    extra_metadata={
                        "tf_confidence": tf_prediction["confidence"],
                        "tf_scores": tf_prediction.get("scores", {}),
                        "validated_with_metadata": True,
                    },
                )
                self.session_cache[track_cache_key] = result
                self.cache_dirty += 1
                self._persist_prediction_cache()
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                self._log(
                    f"Categoria definida: {track_label} -> {', '.join(result['labels'])} | confiança={result['confidence']:.3f} | fonte=TensorFlow | tempo={elapsed_ms:.0f}ms",
                    level="RESULT",
                )
                return result

        lastfm_tags = self._get_lastfm_tags(track_name, artist_names)
        full_context = self._build_context(
            track_name=track_name,
            artist_names=artist_names,
            album_name=album_name,
            spotify_genres=spotify_genres,
            lastfm_tags=lastfm_tags,
            preview_url=preview_url,
            lyrics=lyrics,
        )

        ai_scores, provider_used = self._classify_with_ai(full_context, track_name=track_name, artist_names=artist_names)
        labels, confidence, normalized_scores = self._scores_to_labels(ai_scores, max_labels=max_labels)

        if normalized_scores:
            result = self._build_result(
                labels=labels,
                confidence=confidence,
                source="IA",
                provider_used=provider_used,
                spotify_genres=spotify_genres,
                lastfm_tags=lastfm_tags,
                preview_url=preview_url,
                extra_metadata={"provider_scores": normalized_scores},
            )
            self.tf_learner.record_example(track_cache_key, full_context, labels, provider_used or "IA", confidence)
        else:
            metadata_scores, metadata_evidence = self._classify_from_metadata(
                track_name=track_name,
                artist_names=artist_names,
                album_name=album_name,
                spotify_genres=spotify_genres,
                lastfm_tags=lastfm_tags,
            )
            metadata_labels, metadata_confidence, metadata_scores = self._scores_to_labels(metadata_scores, max_labels=max_labels)

            if metadata_scores:
                result = self._build_result(
                    labels=metadata_labels,
                    confidence=metadata_confidence,
                    source="Metadados",
                    provider_used="metadata",
                    spotify_genres=spotify_genres,
                    lastfm_tags=lastfm_tags,
                    preview_url=preview_url,
                    extra_metadata={
                        "metadata_scores": metadata_scores,
                        "metadata_evidence": metadata_evidence,
                        "ai_unavailable": True,
                    },
                )
            elif tf_prediction and self._should_accept_tf_fallback(tf_prediction):
                result = self._build_result(
                    labels=tf_prediction["labels"][:max_labels],
                    confidence=tf_prediction["confidence"],
                    source="TensorFlow",
                    provider_used="tensorflow",
                    spotify_genres=spotify_genres,
                    lastfm_tags=lastfm_tags,
                    preview_url=preview_url,
                    extra_metadata={
                        "tf_confidence": tf_prediction["confidence"],
                        "tf_scores": tf_prediction.get("scores", {}),
                        "revalidated_with_ai": False,
                    },
                )
            else:
                result = self._build_result(
                    labels=["Outros"],
                    confidence=0.0,
                    source="IA",
                    provider_used=provider_used or "none",
                    spotify_genres=spotify_genres,
                    lastfm_tags=lastfm_tags,
                    preview_url=preview_url,
                    extra_metadata={"provider_scores": normalized_scores},
                )

        if self._is_low_value_result(result):
            self.session_cache.pop(track_cache_key, None)
        else:
            self.session_cache[track_cache_key] = result
            self.cache_dirty += 1
            self._persist_prediction_cache()
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        provider_note = f" | provider={provider_used}" if provider_used else ""
        self._log(
            f"Categoria definida: {track_label} -> {', '.join(result['labels'])} | confiança={result['confidence']:.3f} | fonte={result['source']}{provider_note} | tempo={elapsed_ms:.0f}ms",
            level="RESULT",
        )
        return result

    def flush_learning(self, wait: bool = False) -> None:
        self._persist_prediction_cache(force=True)
        self.tf_learner.flush(wait=wait)

