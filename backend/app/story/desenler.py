"""Haritadaki geometrik ve klasik desenler.

`signature.py` tek tek yerleşimleri buluyor; bu modül ise cisimler
ARASINDAKİ ilişkilerden doğan yapıları arıyor. Anlatı değeri yüksek
olanlar bunlar: tek bir gezegenin nerede durduğu bir cümledir, üç
gezegenin bir üçgen kurması bir sahnedir.

Hepsi ölçülebilir tanımlara dayanıyor; "yorum" değil geometri.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..astro.aspects import angular_separation
from ..astro.chart import NatalChart, PlacedBody
from ..astro.constants import CORE_BODY_KEYS, SIGN_NAMES_TR, SIGN_RULERS


@dataclass(frozen=True)
class Desen:
    anahtar: str          # ölçüm anahtarı
    tanim: str            # anlatıya girecek tek satır
    ilgili: Tuple[str, ...] = ()


def _cekirdek(chart: NatalChart) -> List[PlacedBody]:
    return [b for b in chart.bodies if b.key in CORE_BODY_KEYS]


# --------------------------------------------------------------------------
# Tutulma
# --------------------------------------------------------------------------

# Güneş tutulması, yeniayın Ay düğümüne yaklaşık 15,4 dereceden yakın
# olmasını gerektirir; Ay tutulması için dolunayda sınır ~10,6 derece.
# Bunlar geometrik eşiklerdir, yorum değil.
GUNES_TUTULMA_SINIRI = 15.4
AY_TUTULMA_SINIRI = 10.6


def tutulma(chart: NatalChart) -> Optional[Desen]:
    """Doğum bir tutulmaya denk geliyor mu.

    Tutulma mevsiminde doğmak seyrektir ve gökyüzünde gerçekten
    olağandışı bir şeyin olduğu anlamına gelir - anlatı için en güçlü
    olgulardan biri.
    """
    gunes, ay, dugum = chart.body("Sun"), chart.body("Moon"), chart.body("TrueNode")
    if not (gunes and ay and dugum):
        return None

    faz = (ay.longitude - gunes.longitude) % 360.0
    yeniay = faz < 12.0 or faz > 348.0
    dolunay = 168.0 < faz < 192.0
    if not (yeniay or dolunay):
        return None

    # Güneş'in düğüm eksenine uzaklığı (iki düğüm de sayılır)
    dugume_uzaklik = min(
        angular_separation(gunes.longitude, dugum.longitude),
        angular_separation(gunes.longitude, (dugum.longitude + 180.0) % 360.0),
    )

    if yeniay and dugume_uzaklik <= GUNES_TUTULMA_SINIRI:
        return Desen(
            "gunes_tutulmasi",
            f"Doğum bir Güneş tutulmasına denk geliyor: yeniay, Ay düğümüne "
            f"{dugume_uzaklik:.1f} derece uzaklıkta gerçekleşmiş.",
            ("Sun", "Moon", "TrueNode"),
        )
    if dolunay and dugume_uzaklik <= AY_TUTULMA_SINIRI:
        return Desen(
            "ay_tutulmasi",
            f"Doğum bir Ay tutulmasına denk geliyor: dolunay, Ay düğümüne "
            f"{dugume_uzaklik:.1f} derece uzaklıkta gerçekleşmiş.",
            ("Sun", "Moon", "TrueNode"),
        )
    return None


def ay_evresi_ucu(chart: NatalChart) -> Optional[Desen]:
    """Yeniay ya da dolunay doğumu (tutulma olmasa bile)."""
    gunes, ay = chart.body("Sun"), chart.body("Moon")
    if not (gunes and ay):
        return None
    faz = (ay.longitude - gunes.longitude) % 360.0
    if faz < 12.0 or faz > 348.0:
        return Desen(
            "yeni_ay_dogumu",
            "Doğum yeniaya denk geliyor: Ay ile Güneş neredeyse aynı "
            "noktadaydı, yani o gece gökyüzünde Ay hiç görünmüyordu.",
            ("Sun", "Moon"),
        )
    if 168.0 < faz < 192.0:
        return Desen(
            "dolunay_dogumu",
            "Doğum dolunaya denk geliyor: Ay ile Güneş gökyüzünün iki "
            "ucundaydı, biri doğarken öteki batıyordu.",
            ("Sun", "Moon"),
        )
    return None


# --------------------------------------------------------------------------
# Güneş'e gömülü cisimler
# --------------------------------------------------------------------------

GOMULU_SINIRI = 3.0


def gunese_gomulu(chart: NatalChart) -> Optional[Desen]:
    """Güneş'e çok yakın olduğu için o dönem hiç görülemeyen cisimler."""
    gunes = chart.body("Sun")
    if not gunes:
        return None
    gomulular = [
        b for b in _cekirdek(chart)
        if b.key not in ("Sun", "Moon")
        and angular_separation(b.longitude, gunes.longitude) <= GOMULU_SINIRI
    ]
    if not gomulular:
        return None
    adlar = ", ".join(b.name_tr for b in gomulular)
    en_yakin = min(
        gomulular, key=lambda b: angular_separation(b.longitude, gunes.longitude)
    )
    uzaklik = angular_separation(en_yakin.longitude, gunes.longitude)
    return Desen(
        "gunese_gomulu",
        f"Güneş'e gömülü gök cismi/cisimleri: {adlar}. En yakını "
        f"{en_yakin.name_tr}, yalnızca {uzaklik:.1f} derece uzakta — "
        "haritada tam olarak orada, gökyüzünde tam olarak görünmez.",
        tuple(b.key for b in gomulular),
    )


# --------------------------------------------------------------------------
# Klasik güç: kendi burcunda olan gezegen
# --------------------------------------------------------------------------

def kendi_burcunda(chart: NatalChart) -> Optional[Desen]:
    """Bir gezegenin yönettiği burçta bulunması.

    Klasik astrolojide bir gezegen kendi burcundayken "evinde" sayılır.
    Buradaki iddia yalnızca geometriktir: gezegen, o burcun klasik
    yöneticisidir ve o burçta durmaktadır.
    """
    evinde = [
        b for b in _cekirdek(chart)
        if SIGN_RULERS[b.sign_index][0] == b.key
    ]
    if not evinde:
        return None
    parcalar = ", ".join(f"{b.name_tr} ({b.sign_name_tr})" for b in evinde)
    return Desen(
        "kendi_burcunda",
        f"Kendi yönettiği burçta duran gök cismi/cisimleri: {parcalar}. "
        "Klasik yorumda bu, o cismin kendi evinde olması demektir.",
        tuple(b.key for b in evinde),
    )


# --------------------------------------------------------------------------
# Açı desenleri
# --------------------------------------------------------------------------

def t_kare(chart: NatalChart) -> Optional[Desen]:
    """İki karşıt cismin ikisine birden kare yapan üçüncü bir cisim.

    Üç köşeli, gergin bir yapı: iki taraf birbirine karşı durur ve
    üçüncü kişi ikisiyle de çekişir. Anlatıda doğrudan bir sahne verir.
    """
    karsitlar = [a for a in chart.aspects if a.type_key == "opposition"]
    kareler = [a for a in chart.aspects if a.type_key == "square"]
    if not karsitlar or len(kareler) < 2:
        return None

    for karsit in karsitlar:
        uclar = {karsit.body_a, karsit.body_b}
        adaylar = {}
        for kare in kareler:
            for uc in uclar:
                if kare.body_a == uc:
                    adaylar.setdefault(kare.body_b, set()).add(uc)
                elif kare.body_b == uc:
                    adaylar.setdefault(kare.body_a, set()).add(uc)
        for aday, baglar in adaylar.items():
            if baglar == uclar:
                cisim = chart.body(aday)
                return Desen(
                    "t_kare",
                    f"T-kare deseni: {karsit.name_a_tr} ile {karsit.name_b_tr} "
                    f"karşı karşıya, ve {cisim.name_tr if cisim else aday} "
                    "ikisiyle birden çekişiyor.",
                    (karsit.body_a, karsit.body_b, aday),
                )
    return None


def buyuk_ucgen(chart: NatalChart) -> Optional[Desen]:
    """Birbirine üçgen açı yapan üç cisim: kapalı, akıcı bir devre."""
    ucgenler = [a for a in chart.aspects if a.type_key == "trine"]
    if len(ucgenler) < 3:
        return None

    baglar = {}
    for a in ucgenler:
        baglar.setdefault(a.body_a, set()).add(a.body_b)
        baglar.setdefault(a.body_b, set()).add(a.body_a)

    for x, komsular in baglar.items():
        for y in komsular:
            for z in komsular:
                if y >= z:
                    continue
                if z in baglar.get(y, set()):
                    adlar = [chart.body(k) for k in (x, y, z)]
                    isimler = ", ".join(b.name_tr for b in adlar if b)
                    return Desen(
                        "buyuk_ucgen",
                        f"Büyük üçgen deseni: {isimler} birbirine üçgen açı "
                        "yapıyor; üçü kapalı bir devre kuruyor.",
                        (x, y, z),
                    )
    return None


# --------------------------------------------------------------------------
# Haritanın genel şekli
# --------------------------------------------------------------------------

def kase_sekli(chart: NatalChart) -> Optional[Desen]:
    """Tüm cisimlerin gökyüzünün bir yarısında toplanması.

    Cisimler 180 dereceden dar bir yaya sıkışmışsa haritanın bir "boş
    tarafı" vardır. Anlatıda bu, ülkenin yarısının hiç yerleşilmemiş
    olması demektir.
    """
    cisimler = _cekirdek(chart)
    if len(cisimler) < 10:
        return None

    boylamlar = sorted(b.longitude for b in cisimler)
    en_buyuk_bosluk = 0.0
    for i in range(len(boylamlar)):
        sonraki = boylamlar[(i + 1) % len(boylamlar)]
        bosluk = (sonraki - boylamlar[i]) % 360.0
        en_buyuk_bosluk = max(en_buyuk_bosluk, bosluk)

    yay = 360.0 - en_buyuk_bosluk
    if yay > 180.0:
        return None
    return Desen(
        "kase_sekli",
        f"Bütün gök cisimleri {yay:.0f} derecelik bir yaya sıkışmış; "
        f"gökyüzünün {en_buyuk_bosluk:.0f} derecelik kısmı bomboş.",
        tuple(b.key for b in cisimler),
    )


def hepsi(chart: NatalChart) -> List[Desen]:
    """Haritada bulunan tüm desenler."""
    bulunanlar = []
    for uretici in (tutulma, ay_evresi_ucu, gunese_gomulu, kendi_burcunda,
                    t_kare, buyuk_ucgen, kase_sekli):
        desen = uretici(chart)
        if desen:
            bulunanlar.append(desen)
    return bulunanlar
