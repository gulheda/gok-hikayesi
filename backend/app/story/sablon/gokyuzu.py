"""Hikâyenin olgusal bölümü için anlatılabilir astronomik olgular.

Bu modül yorum yapmaz; yalnızca haritadan doğrudan çıkan, başka bir
efemeris yazılımıyla doğrulanabilecek gerçekleri toplar. Ürünün "gerçek
astronomik veri" iddiası burada yaşadığı için bu bölüm hiçbir zaman bir
dil modeline bırakılmamalı - model bir sayıyı yanlış yazarsa iddia çöker.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ...astro.aspects import angular_separation
from ...astro.chart import NatalChart, PlacedBody
from .turkce import gecmis_kopula

# Güneş'e bu açıdan yakın bir gök cismi gündüz ışığında kaybolur ve o
# dönem boyunca hiç görülemez. Sınır kabaca 10 derecedir; cismin
# parlaklığına göre değişir, o yüzden "yaklaşık" diye anlatılıyor.
GORUNMEZLIK_SINIRI = 10.0


@dataclass(frozen=True)
class GokOlgusu:
    """Anlatıya girecek tek bir doğrulanabilir olgu."""

    anahtar: str
    cumle: str
    onem: float                 # büyük olan önce anlatılır
    ilgili: tuple = ()          # cümlenin değindiği gök cismi anahtarları


def _derece_yazi(derece: float) -> str:
    """Dereceyi anlatıya uygun sözcüklere çevirir."""
    tam = int(round(derece))
    if tam == 0:
        return "yarım dereceden az"
    if tam == 1:
        return "bir derece kadar"
    return f"{tam} derece"


def gunes_konumu(chart: NatalChart) -> Optional[GokOlgusu]:
    gunes = chart.body("Sun")
    if not gunes:
        return None
    return GokOlgusu(
        "gunes",
        f"Güneş, {gunes.sign_name_tr} burcunun "
        f"{int(gunes.degree_in_sign)}. derecesindeydi.",
        onem=50.0, ilgili=("Sun",),
    )


def gorunmeyenler(chart: NatalChart) -> List[GokOlgusu]:
    """Güneş'e çok yakın olduğu için o dönem görülemeyen cisimler.

    Anlatının en çarpıcı olgusu genelde budur: haritada tam olarak orada
    duran ama gökyüzünde tam olarak görünmeyen bir cisim.
    """
    gunes = chart.body("Sun")
    if not gunes:
        return []

    yakinlar = []
    for body in chart.bodies:
        if body.key in ("Sun", "Moon", "TrueNode", "Chiron"):
            continue
        ayrim = angular_separation(body.longitude, gunes.longitude)
        if ayrim <= GORUNMEZLIK_SINIRI:
            yakinlar.append((body, ayrim))

    if not yakinlar:
        return []

    yakinlar.sort(key=lambda p: p[1])

    # Birden fazla cisim görünmezse aynı kalıbı arka arkaya tekrarlamak
    # yerine tek cümlede birleştiriyoruz; tekrar eden kalıp, şablonla
    # üretildiğini ele veren ilk şeydir.
    if len(yakinlar) == 1:
        body, ayrim = yakinlar[0]
        cumle = (
            f"{body.name_tr} Güneş'e yalnızca {_derece_yazi(ayrim)} "
            f"uzaktaydı; o dönem boyunca hiç kimse onu göremezdi, çünkü "
            "ışığın içinde kaybolmuştu."
        )
    else:
        adlar = [b.name_tr for b, _ in yakinlar]
        liste = ", ".join(adlar[:-1]) + " ile " + adlar[-1]
        en_yakin = yakinlar[0]
        cumle = (
            f"{liste} Güneş'e o kadar yakındı ki hiçbiri görülemiyordu; "
            f"en yakını {en_yakin[0].name_tr}, yalnızca "
            f"{_derece_yazi(en_yakin[1])} uzakta. Haritada tam olarak "
            "oradaydılar ve gökyüzünde tam olarak görünmüyorlardı."
        )

    return [GokOlgusu(
        "gorunmezler", cumle,
        onem=80.0 - yakinlar[0][1],
        ilgili=tuple(b.key for b, _ in yakinlar),
    )]


def ay_evresi(chart: NatalChart) -> Optional[GokOlgusu]:
    gunes, ay = chart.body("Sun"), chart.body("Moon")
    if not gunes or not ay:
        return None

    faz = (ay.longitude - gunes.longitude) % 360.0
    gun = faz / 360.0 * 29.53

    if faz < 15 or faz > 345:
        ad, ek = "yeni ay", "gökyüzünde hiç görünmüyordu"
    elif faz < 90:
        ad, ek = "büyüyen hilal", f"yaklaşık {gun:.0f} günlüktü"
    elif faz < 105:
        ad, ek = "ilk dördün", "yarısı aydınlıktı"
    elif faz < 175:
        ad, ek = "büyüyen ay", "dolunaya yaklaşıyordu"
    elif faz < 190:
        ad, ek = "dolunay", "tamamı aydınlıktı"
    elif faz < 265:
        ad, ek = "küçülen ay", "her gece biraz daha inceliyordu"
    elif faz < 280:
        ad, ek = "son dördün", "yarısı karanlıktı"
    else:
        ad, ek = "küçülen hilal", "yeni aya birkaç gün kalmıştı"

    return GokOlgusu(
        "ay_evresi",
        f"Ay {ay.sign_name_tr} burcundaydı ve {ad} evresindeydi; {ek}.",
        onem=60.0, ilgili=("Moon",),
    )


def ufuktakiler(chart: NatalChart) -> List[GokOlgusu]:
    """Yükselen'e yakın cisimler: o anda doğu ufkunda ne vardı.

    On ikinci evdeki bir cisim ufkun ÜSTÜNDEDİR (yeni doğmuştur), birinci
    evdeki ise ALTINDA (henüz doğmamıştır). Bu ayrım anlatının en somut
    görüntüsünü verir ve gökyüzüne bakan biri tarafından doğrulanabilir.
    """
    if not chart.houses.available or chart.houses.ascendant is None:
        return []

    asc = chart.houses.ascendant
    olgular: List[GokOlgusu] = []
    for body in chart.bodies:
        fark = (body.longitude - asc + 180.0) % 360.0 - 180.0
        if abs(fark) > 8.0:
            continue
        if fark < 0:
            # Boylamı Yükselen'den küçük: çoktan doğmuş, ufkun üstünde.
            durum = (
                f"{body.name_tr} doğu ufkunun {_derece_yazi(abs(fark))} "
                "üstündeydi; birkaç dakika önce yükselmişti"
            )
        else:
            dakika = int(round(fark / 15.0 * 60))
            durum = (
                f"{body.name_tr} henüz doğmamıştı; ufkun "
                f"{_derece_yazi(fark)} altında bekliyordu ve yaklaşık "
                f"{dakika} dakika sonra çıkacaktı"
            )
        olgular.append(GokOlgusu(
            f"ufuk_{body.key}", durum + ".", onem=95.0 - abs(fark),
            ilgili=(body.key,),
        ))
    return olgular


def en_yakin_gezegen(chart: NatalChart) -> Optional[GokOlgusu]:
    """Dünya'ya en yakın gezegen ve o andaki uzaklığı."""
    adaylar = [
        b for b in chart.bodies
        if b.key in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn")
    ]
    if not adaylar:
        return None
    en_yakin = min(adaylar, key=lambda b: b.distance_au)
    return GokOlgusu(
        "en_yakin",
        f"O gün Dünya'ya en yakın gezegen "
        f"{gecmis_kopula(en_yakin.name_tr, ozel_ad=True)}: "
        f"{en_yakin.distance_au:.2f} astronomi birimi uzaklıkta.",
        onem=40.0, ilgili=(en_yakin.key,),
    )


def gerileyenler(chart: NatalChart) -> Optional[GokOlgusu]:
    """Gerileme hareketindeki cisimler.

    Dış gezegenlerin gerilemesi yaygındır; bu yüzden olgu olarak anlatılır
    ama önemi düşük tutulur - üzerine anlatı kurulmaz.
    """
    geri = [b.name_tr for b in chart.bodies if b.is_retrograde and b.key not in ("TrueNode",)]
    if not geri:
        return None
    liste = ", ".join(geri[:-1]) + " ve " + geri[-1] if len(geri) > 1 else geri[0]
    return GokOlgusu(
        "gerileyen",
        f"Gökyüzünde {liste} gerileme hareketindeydi: Dünya'dan bakınca "
        "burçlar boyunca geriye doğru ilerliyor gibi görünüyorlardı.",
        onem=20.0,
    )


def topla(chart: NatalChart, en_fazla: int = 5) -> List[GokOlgusu]:
    """Tüm olguları toplayıp önem sırasına dizer."""
    hepsi: List[GokOlgusu] = []
    for olgu in (gunes_konumu(chart), ay_evresi(chart),
                 en_yakin_gezegen(chart), gerileyenler(chart)):
        if olgu:
            hepsi.append(olgu)
    hepsi.extend(gorunmeyenler(chart))
    hepsi.extend(ufuktakiler(chart))
    hepsi.sort(key=lambda o: o.onem, reverse=True)
    return hepsi[:en_fazla]
