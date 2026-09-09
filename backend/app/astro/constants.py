"""Astrolojik sabitler: burçlar, gök cisimleri, açılar, ev sistemleri.

Kod içi tanımlayıcılar İngilizce (kütüphane uyumu için), kullanıcıya
gösterilen adlar Türkçe.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import swisseph as swe

# --------------------------------------------------------------------------
# Burçlar
# --------------------------------------------------------------------------

SIGN_NAMES_TR: List[str] = [
    "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
    "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık",
]

SIGN_NAMES_EN: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Elementler Koç'tan itibaren ateş-toprak-hava-su döngüsünde ilerler.
ELEMENTS_TR: List[str] = ["Ateş", "Toprak", "Hava", "Su"]
MODALITIES_TR: List[str] = ["Öncü", "Sabit", "Değişken"]

# Her burcun yöneticisi (klasik + modern yönetici)
SIGN_RULERS: Dict[int, Tuple[str, Optional[str]]] = {
    0: ("Mars", None),
    1: ("Venus", None),
    2: ("Mercury", None),
    3: ("Moon", None),
    4: ("Sun", None),
    5: ("Mercury", None),
    6: ("Venus", None),
    7: ("Mars", "Pluto"),
    8: ("Jupiter", None),
    9: ("Saturn", None),
    10: ("Saturn", "Uranus"),
    11: ("Jupiter", "Neptune"),
}


def sign_index(longitude: float) -> int:
    """Ekliptik boylamı (0-360) 12 burçtan birine eşler."""
    return int(longitude % 360.0) // 30


def sign_element_tr(idx: int) -> str:
    return ELEMENTS_TR[idx % 4]


def sign_modality_tr(idx: int) -> str:
    return MODALITIES_TR[idx % 3]


# --------------------------------------------------------------------------
# Gök cisimleri
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Body:
    key: str            # kod içi kimlik
    name_tr: str        # kullanıcıya gösterilen ad
    swe_id: int         # Swiss Ephemeris gövde kimliği
    is_luminary: bool = False   # Güneş/Ay: daha geniş açı toleransı
    is_core: bool = True        # MVP hikâyesinde kullanılacak çekirdek kadro


BODIES: List[Body] = [
    Body("Sun",     "Güneş",   swe.SUN,     is_luminary=True),
    Body("Moon",    "Ay",      swe.MOON,    is_luminary=True),
    Body("Mercury", "Merkür",  swe.MERCURY),
    Body("Venus",   "Venüs",   swe.VENUS),
    Body("Mars",    "Mars",    swe.MARS),
    Body("Jupiter", "Jüpiter", swe.JUPITER),
    Body("Saturn",  "Satürn",  swe.SATURN),
    Body("Uranus",  "Uranüs",  swe.URANUS),
    Body("Neptune", "Neptün",  swe.NEPTUNE),
    Body("Pluto",   "Plüton",  swe.PLUTO),
    Body("TrueNode", "Kuzey Ay Düğümü", swe.TRUE_NODE, is_core=False),
    Body("Chiron",  "Chiron",  swe.CHIRON, is_core=False),
]

BODY_BY_KEY: Dict[str, Body] = {b.key: b for b in BODIES}
CORE_BODY_KEYS: List[str] = [b.key for b in BODIES if b.is_core]


# --------------------------------------------------------------------------
# Açılar (aspects)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class AspectType:
    key: str
    name_tr: str
    angle: float
    base_orb: float          # normal gök cisimleri için tolerans
    luminary_orb: float      # Güneş/Ay dahilse tolerans
    nature: str              # "uyumlu" | "gergin" | "nötr" -> hikâye tonu için


ASPECT_TYPES: List[AspectType] = [
    AspectType("conjunction", "Kavuşum",  0.0,   8.0, 10.0, "nötr"),
    AspectType("sextile",     "Altmışlık", 60.0,  4.0,  6.0, "uyumlu"),
    AspectType("square",      "Kare",      90.0,  6.0,  8.0, "gergin"),
    AspectType("trine",       "Üçgen",    120.0,  6.0,  8.0, "uyumlu"),
    AspectType("opposition",  "Karşıt",   180.0,  7.0,  9.0, "gergin"),
]


# --------------------------------------------------------------------------
# Ev sistemleri
# --------------------------------------------------------------------------

# Swiss Ephemeris tek harfli ev sistemi kodları
HOUSE_SYSTEMS: Dict[str, Tuple[bytes, str]] = {
    "placidus":   (b"P", "Placidus"),
    "koch":       (b"K", "Koch"),
    "whole_sign": (b"W", "Whole Sign (Tam Burç)"),
    "equal":      (b"A", "Eşit Ev"),
    "porphyry":   (b"O", "Porphyry"),
    "regiomontanus": (b"R", "Regiomontanus"),
}

DEFAULT_HOUSE_SYSTEM = "placidus"

# Placidus kutup dairelerine yakın enlemlerde matematiksel olarak bozulur;
# bu sınırın ötesinde Whole Sign'a düşeriz.
PLACIDUS_LATITUDE_LIMIT = 66.0

# Evlerin Türkçe temaları -> hikâye katmanında "bölge/krallık" metaforuna girer
HOUSE_THEMES_TR: Dict[int, str] = {
    1: "kimlik, dışa vuruş, ilk izlenim",
    2: "kaynaklar, değerler, sahip olunanlar",
    3: "iletişim, yakın çevre, öğrenme",
    4: "kök, aile, yuva",
    5: "yaratıcılık, oyun, kendini ifade",
    6: "gündelik düzen, emek, sağlık",
    7: "ortaklık, ilişki, öteki",
    8: "dönüşüm, ortak kaynaklar, derinlik",
    9: "anlam arayışı, uzak ufuklar, inanç",
    10: "kamusal rol, hedef, iz bırakma",
    11: "topluluk, gelecek tasavvuru, dostluk",
    12: "içsel dünya, geri çekilme, bilinçdışı",
}
