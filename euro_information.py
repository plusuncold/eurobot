
COUNTRY_FLAGS = {
    "norway": "🇳🇴", "malta": "🇲🇹", "serbia": "🇷🇸", "latvia": "🇱🇻", "portugal": "🇵🇹", "ireland": "🇮🇪", "croatia": "🇭🇷",
    "switzerland": "🇨🇭", "israel": "🇮🇱", "moldova": "🇲🇩", "sweden": "🇸🇪", "azerbaijan": "🇦🇿", "czechia": "🇨🇿",
    "netherlands": "🇳🇱", "finland": "🇫🇮", "denmark": "🇩🇰", "armenia": "🇦🇲", "romania": "🇷🇴", "estonia": "🇪🇪",
    "belgium": "🇧🇪", "cyprus": "🇨🇾", "iceland": "🇮🇸", "greece": "🇬🇷", "poland": "🇵🇱", "slovenia": "🇸🇮", "georgia": "🇬🇪", 
    "san marino": "🇸🇲", "austria": "🇦🇹", "albania": "🇦🇱", "lithuania": "🇱🇹", "australia": "🇦🇺", "france": "🇫🇷", 
    "germany": "🇩🇪", "italy": "🇮🇹", "spain": "🇪🇸", "ukraine": "🇺🇦", "united kingdom": "🇬🇧", "luxembourg": "🇱🇺",
     "montenegro": "🇲🇪"
}

SEMI_FINAL_ONE = [
    "Croatia",
    "Finland",
    "Georgia",
    "Greece",
    "Moldova",
    "Portugal",
    "Sweden",
    "Belgium",
    "Estonia",
    "Israel",
    "Lithuania",
    "Montenegro",
    "Poland",
    "San Marino",
    "Serbia"
]

SEMI_FINAL_TWO = [
    "Armenia",
    "Azerbaijan",
    "Bulgaria",
    "Czechia",
    "Luxembourg",
    "Romania",
    "Switzerland",
    "Albania",
    "Australia",
    "Cyprus",
    "Denmark",
    "Latvia",
    "Malta",
    "Norway",
    "Ukraine"
]
SEMI_FINAL_ONE_ELIMINATED = []
SEMI_FINAL_TWO_ELIMINATED = []
RESULTS = {}

# eurovision 2026
SONGS = {
    "albania": "Nân",
    "armenia": "Paloma rumba",
    "australia": "Eclipse",
    "austria": "Tanzschein",
    "azerbaijan": "Just Go",
    "belgium": "Dancing on the Ice",
    "bulgaria": "Bangaranga",
    "croatia": "Andromeda",
    "cyprus": "Jalia",
    "czechia": "Crossroads",
    "denmark": "Før vi går hjem",
    "estonia": "Too Epic to Be True",
    "finland": "Liekinheitin",
    "france": "Regarde !",
    "georgia": "On Replay",
    "germany": "Fire",
    "greece": "Φέρτο",
    "israel": "Michelle",
    "italy": "Per sempre si",
    "latvia": "Ēnā",
    "lithuania": "Sólo quiero más",
    "luxembourg": "Mother Nature",
    "malta": "Bella",
    "moldova": "Viva, Moldova!",
    "montenegro": "Нова зора",
    "norway": "Ya Ya Ya",
    "poland": "Pray",
    "portugal": "Rosa",
    "romania": "Choke Me",
    "san marino": "Superstar",
    "serbia": "Крај мене",
    "sweden": "My System",
    "switzerland": "Alice",
    "ukraine": "Рідним",
    "united kingdom": "Eins, zwei, drei"
}
SONG_URLS = {
}
COUNTRIES = list(SONGS.keys())
CURRENT_YEAR = 2026

def get_current_year():
    return CURRENT_YEAR

def get_country_count():
    return len(COUNTRIES)

def convert_possible_emoji_to_country(possible_emoji):
    for country, country_emoji in COUNTRY_FLAGS.items():
        if country_emoji == possible_emoji:
            return country
    return possible_emoji

def convert_first_word_to_country(possible_country):
    if possible_country == "czech" or possible_country == "czech republic":
        return "czechia"
    if possible_country == "united" or possible_country == "uk" or possible_country == "britain" or possible_country == "british":
        return "united kingdom"
    if possible_country == "san":
        return "san marino"
    return possible_country


def get_song_detail(country):
    return None