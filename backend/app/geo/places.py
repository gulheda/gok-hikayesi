"""Türkiye il merkezleri için çevrimdışı koordinat tablosu.

Kullanıcıların büyük çoğunluğu doğum yerini il olarak girer. Bu tablo o
durumda ağ isteğini tamamen ortadan kaldırır: Nominatim'in saniyede bir
istek sınırı ve çevrimdışı kalma riski, en sık kullanılan yolu etkilemez.

Hassasiyet notu: değerler il merkezidir. Doğum yerindeki 10 km'lik bir
sapma Yükselen'i ~0.03° kaydırır - açı dakikasının altında, yani
astrolojik yorum için önemsiz.
"""
from __future__ import annotations

from typing import Dict, Tuple

# il adı (küçük harf, aksansız normalize edilmiş) -> (enlem, boylam)
TURKIYE_IL_MERKEZLERI: Dict[str, Tuple[float, float]] = {
    "adana": (37.0000, 35.3213), "adiyaman": (37.7648, 38.2786),
    "afyonkarahisar": (38.7507, 30.5567), "agri": (39.7191, 43.0503),
    "aksaray": (38.3687, 34.0370), "amasya": (40.6499, 35.8353),
    "ankara": (39.9334, 32.8597), "antalya": (36.8969, 30.7133),
    "ardahan": (41.1105, 42.7022), "artvin": (41.1828, 41.8183),
    "aydin": (37.8560, 27.8416), "balikesir": (39.6484, 27.8826),
    "bartin": (41.6344, 32.3375), "batman": (37.8812, 41.1351),
    "bayburt": (40.2552, 40.2249), "bilecik": (40.1451, 29.9799),
    "bingol": (38.8853, 40.4983), "bitlis": (38.4006, 42.1095),
    "bolu": (40.7392, 31.6089), "burdur": (37.7204, 30.2908),
    "bursa": (40.1826, 29.0665), "canakkale": (40.1553, 26.4142),
    "cankiri": (40.6013, 33.6134), "corum": (40.5506, 34.9556),
    "denizli": (37.7765, 29.0864), "diyarbakir": (37.9144, 40.2306),
    "duzce": (40.8438, 31.1565), "edirne": (41.6818, 26.5623),
    "elazig": (38.6810, 39.2264), "erzincan": (39.7500, 39.5000),
    "erzurum": (39.9000, 41.2700), "eskisehir": (39.7767, 30.5206),
    "gaziantep": (37.0662, 37.3833), "giresun": (40.9128, 38.3895),
    "gumushane": (40.4386, 39.5086), "hakkari": (37.5744, 43.7408),
    "hatay": (36.2025, 36.1606), "igdir": (39.9237, 44.0450),
    "isparta": (37.7648, 30.5566), "istanbul": (41.0082, 28.9784),
    "izmir": (38.4237, 27.1428), "kahramanmaras": (37.5858, 36.9371),
    "karabuk": (41.2061, 32.6204), "karaman": (37.1759, 33.2287),
    "kars": (40.6013, 43.0975), "kastamonu": (41.3887, 33.7827),
    "kayseri": (38.7312, 35.4787), "kilis": (36.7184, 37.1212),
    "kirikkale": (39.8468, 33.5153), "kirklareli": (41.7333, 27.2167),
    "kirsehir": (39.1425, 34.1709), "kocaeli": (40.8533, 29.8815),
    "konya": (37.8746, 32.4932), "kutahya": (39.4242, 29.9833),
    "malatya": (38.3552, 38.3095), "manisa": (38.6191, 27.4289),
    "mardin": (37.3212, 40.7245), "mersin": (36.8121, 34.6415),
    "mugla": (37.2153, 28.3636), "mus": (38.9462, 41.7539),
    "nevsehir": (38.6939, 34.6857), "nigde": (37.9667, 34.6833),
    "ordu": (40.9839, 37.8764), "osmaniye": (37.0742, 36.2464),
    "rize": (41.0201, 40.5234), "sakarya": (40.7569, 30.3783),
    "samsun": (41.2867, 36.3300), "sanliurfa": (37.1591, 38.7969),
    "siirt": (37.9333, 41.9500), "sinop": (42.0231, 35.1531),
    "sivas": (39.7477, 37.0179), "sirnak": (37.4187, 42.4918),
    "tekirdag": (40.9833, 27.5167), "tokat": (40.3167, 36.5500),
    "trabzon": (41.0015, 39.7178), "tunceli": (39.1079, 39.5401),
    "usak": (38.6823, 29.4082), "van": (38.4891, 43.4089),
    "yalova": (40.6500, 29.2667), "yozgat": (39.8181, 34.8147),
    "zonguldak": (41.4564, 31.7987),
}

# Kullanıcıların sık yazdığı alternatif adlar
TAKMA_ADLAR: Dict[str, str] = {
    "afyon": "afyonkarahisar",
    "maras": "kahramanmaras",
    "urfa": "sanliurfa",
    "antep": "gaziantep",
    "izmit": "kocaeli",
    "adapazari": "sakarya",
    "mersin": "mersin",
    "icel": "mersin",
    "constantinople": "istanbul",
}


def normalize(text: str) -> str:
    """Türkçe karakterleri sadeleştirip aramaya uygun anahtar üretir.

    `str.lower()` Türkçe'de 'I' harfini 'i' yapar ama biz aksansız
    karşılıkları ('ı' -> 'i') da eşlemek istediğimiz için harf harf
    dönüştürüyoruz.
    """
    eslesme = str.maketrans({
        "ı": "i", "İ": "i", "I": "i", "i": "i",
        "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g",
        "ü": "u", "Ü": "u", "ö": "o", "Ö": "o",
        "ç": "c", "Ç": "c", "â": "a", "î": "i", "û": "u",
    })
    return text.translate(eslesme).lower().strip()


def lookup(place: str) -> Tuple[float, float]:
    """İl adından koordinat döndürür; bulunamazsa KeyError atar."""
    key = normalize(place)
    key = TAKMA_ADLAR.get(key, key)
    return TURKIYE_IL_MERKEZLERI[key]


# Yoğun Türk nüfuslu yurtdışı büyük şehirler (şehir merkezi).
# anahtar -> (enlem, boylam, ülke). Anahtar normalize edilmiş, Türkçe yazım.
YURTDISI_SEHIRLER: Dict[str, Tuple[float, float, str]] = {
    "berlin": (52.5200, 13.4050, "Almanya"),
    "hamburg": (53.5511, 9.9937, "Almanya"),
    "munih": (48.1351, 11.5820, "Almanya"),
    "koln": (50.9375, 6.9603, "Almanya"),
    "frankfurt": (50.1109, 8.6821, "Almanya"),
    "stuttgart": (48.7758, 9.1829, "Almanya"),
    "dusseldorf": (51.2277, 6.7735, "Almanya"),
    "dortmund": (51.5136, 7.4653, "Almanya"),
    "essen": (51.4556, 7.0116, "Almanya"),
    "bremen": (53.0793, 8.8017, "Almanya"),
    "hannover": (52.3759, 9.7320, "Almanya"),
    "nurnberg": (49.4521, 11.0767, "Almanya"),
    "duisburg": (51.4344, 6.7623, "Almanya"),
    "londra": (51.5074, -0.1278, "Birleşik Krallık"),
    "amsterdam": (52.3676, 4.9041, "Hollanda"),
    "rotterdam": (51.9244, 4.4777, "Hollanda"),
    "paris": (48.8566, 2.3522, "Fransa"),
    "bruksel": (50.8503, 4.3517, "Belçika"),
    "viyana": (48.2082, 16.3738, "Avusturya"),
    "zurih": (47.3769, 8.5417, "İsviçre"),
    "stockholm": (59.3293, 18.0686, "İsveç"),
    "kopenhag": (55.6761, 12.5683, "Danimarka"),
    "new york": (40.7128, -74.0060, "ABD"),
    "baku": (40.4093, 49.8671, "Azerbaycan"),
    "lefkosa": (35.1856, 33.3823, "Kıbrıs"),
    "sofya": (42.6977, 23.3219, "Bulgaristan"),
    "pristine": (42.6629, 21.1655, "Kosova"),
    "uskup": (41.9981, 21.4254, "Kuzey Makedonya"),
    "saraybosna": (43.8563, 18.4131, "Bosna-Hersek"),
    "atina": (37.9838, 23.7275, "Yunanistan"),
    "moskova": (55.7558, 37.6173, "Rusya"),
    # GeoNames (geonamescache) ile doğrulanmış eklemeler
    "madrid": (40.4165, -3.7026, "İspanya"),
    "roma": (41.8919, 12.5113, "İtalya"),
    "milano": (45.4643, 9.1895, "İtalya"),
    "lizbon": (38.7251, -9.1498, "Portekiz"),
    "prag": (50.0880, 14.4208, "Çekya"),
    "varsova": (52.2298, 21.0118, "Polonya"),
    "budapeste": (47.4984, 19.0404, "Macaristan"),
    "bukres": (44.4323, 26.1063, "Romanya"),
    "belgrad": (44.8040, 20.4651, "Sırbistan"),
    "zagreb": (45.8144, 15.9780, "Hırvatistan"),
    "tiran": (41.3274, 19.8187, "Arnavutluk"),
    "toronto": (43.7064, -79.3986, "Kanada"),
    "los angeles": (34.0522, -118.2437, "ABD"),
    "sidney": (-33.8679, 151.2073, "Avustralya"),
    "dubai": (25.0772, 55.3093, "BAE"),
    "tiflis": (41.6914, 44.8341, "Gürcistan"),
    "bagdat": (33.3406, 44.4009, "Irak"),
    "kahire": (30.0626, 31.2497, "Mısır"),
}

# Yurtdışı şehirlerin yaygın yabancı yazımları
YURTDISI_TAKMA_ADLAR: Dict[str, str] = {
    "munchen": "munih", "munich": "munih", "cologne": "koln",
    "nuremberg": "nurnberg", "london": "londra", "vienna": "viyana",
    "zurich": "zurih", "brussels": "bruksel", "copenhagen": "kopenhag",
    "newyork": "new york", "nyc": "new york", "baku": "baku",
    "nicosia": "lefkosa", "sofia": "sofya", "pristina": "pristine",
    "skopje": "uskup", "sarajevo": "saraybosna", "athens": "atina",
    "moscow": "moskova", "dusseldorf": "dusseldorf",
    "rome": "roma", "milan": "milano", "lisbon": "lizbon", "prague": "prag",
    "warsaw": "varsova", "bucharest": "bukres", "belgrade": "belgrad",
    "sydney": "sidney", "tbilisi": "tiflis", "baghdad": "bagdat",
    "cairo": "kahire", "la": "los angeles",
}

# Ülke adı yazımları (normalize) -> tablodaki ülke adı
_ULKE_YAZIMLARI: Dict[str, str] = {
    "germany": "Almanya", "deutschland": "Almanya", "almanya": "Almanya",
    "uk": "Birleşik Krallık", "united kingdom": "Birleşik Krallık",
    "ingiltere": "Birleşik Krallık", "birlesik krallik": "Birleşik Krallık",
    "england": "Birleşik Krallık", "netherlands": "Hollanda",
    "hollanda": "Hollanda", "france": "Fransa", "fransa": "Fransa",
    "belgium": "Belçika", "belcika": "Belçika", "austria": "Avusturya",
    "avusturya": "Avusturya", "switzerland": "İsviçre", "isvicre": "İsviçre",
    "sweden": "İsveç", "isvec": "İsveç", "denmark": "Danimarka",
    "danimarka": "Danimarka", "usa": "ABD", "abd": "ABD", "us": "ABD",
    "united states": "ABD", "azerbaycan": "Azerbaycan",
    "azerbaijan": "Azerbaycan", "kibris": "Kıbrıs", "cyprus": "Kıbrıs",
    "kktc": "Kıbrıs", "bulgaria": "Bulgaristan", "bulgaristan": "Bulgaristan",
    "kosova": "Kosova", "kosovo": "Kosova", "kuzey makedonya": "Kuzey Makedonya",
    "north macedonia": "Kuzey Makedonya", "bosna-hersek": "Bosna-Hersek",
    "bosna hersek": "Bosna-Hersek", "bosnia": "Bosna-Hersek",
    "yunanistan": "Yunanistan", "greece": "Yunanistan", "rusya": "Rusya",
    "russia": "Rusya", "spain": "İspanya", "ispanya": "İspanya",
    "italy": "İtalya", "italya": "İtalya", "portugal": "Portekiz",
    "portekiz": "Portekiz", "czechia": "Çekya", "czech republic": "Çekya",
    "cekya": "Çekya", "poland": "Polonya", "polonya": "Polonya",
    "hungary": "Macaristan", "macaristan": "Macaristan", "romania": "Romanya",
    "romanya": "Romanya", "serbia": "Sırbistan", "sirbistan": "Sırbistan",
    "croatia": "Hırvatistan", "hirvatistan": "Hırvatistan",
    "albania": "Arnavutluk", "arnavutluk": "Arnavutluk", "canada": "Kanada",
    "kanada": "Kanada", "australia": "Avustralya", "avustralya": "Avustralya",
    "uae": "BAE", "bae": "BAE", "birlesik arap emirlikleri": "BAE",
    "georgia": "Gürcistan", "gurcistan": "Gürcistan", "iraq": "Irak",
    "irak": "Irak", "egypt": "Mısır", "misir": "Mısır",
}


def lookup_yurtdisi(query: str) -> Tuple[float, float, str, str]:
    """'Berlin' veya 'Berlin, Almanya' gibi girdiyi çözer.

    (enlem, boylam, şehir adı, ülke) döndürür; bulunamazsa ya da girilen
    ülke tablodakiyle uyuşmuyorsa (örn. 'Paris, Texas') KeyError atar -
    böyle durumda çağıran taraf Nominatim'e düşmelidir.
    """
    parcalar = [p for p in (x.strip() for x in query.split(",")) if p]
    if not parcalar:
        raise KeyError(query)
    key = normalize(parcalar[0])
    key = YURTDISI_TAKMA_ADLAR.get(key, key)
    lat, lon, ulke = YURTDISI_SEHIRLER[key]
    for ek in parcalar[1:]:
        if _ULKE_YAZIMLARI.get(normalize(ek)) != ulke:
            raise KeyError(query)
    return lat, lon, parcalar[0], ulke
