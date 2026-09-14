"""Kalibrasyon örnekleminin ağırlıklandırılması.

Seyreklik oranları hangi doğum evreni üzerinden sayıldığına bağlı. Tek
düze örneklem hesaplaması kolaydır ama Türkiye'yi tarif etmez ve
oranları sessizce kaydırır.
"""
from __future__ import annotations

import random
from collections import Counter

import pytest

from app.geo.nufus import IL_NUFUSU, toplam
from app.geo.places import TURKIYE_IL_MERKEZLERI
from app.story.ornekleme import (
    AY_AGIRLIKLARI,
    SENARYOLAR,
    VARSAYILAN_SENARYO,
    ay_sec,
)


# --------------------------------------------------------------------------
# Nüfus verisi
# --------------------------------------------------------------------------

def test_her_ilin_nufusu_var():
    """Koordinat tablosuyla nüfus tablosu birebir örtüşmeli; biri
    eksik kalırsa o il örneklemde ağırlık 1 alır ve sessizce yok sayılır."""
    assert set(IL_NUFUSU) == set(TURKIYE_IL_MERKEZLERI)


def test_toplam_nufus_makul_aralikta():
    assert 80_000_000 < toplam() < 90_000_000


def test_istanbul_payi_gercekcidir():
    """İstanbul nüfusun yaklaşık altıda biri. Eşit örnekleme onu
    seksen birde bire düşürür - enlem dağılımını bozan asıl hata budur."""
    pay = IL_NUFUSU["istanbul"] / toplam()
    assert 0.15 < pay < 0.22


def test_nufus_agirliginin_enleme_etkisi_kucuk():
    """Ölçülen gerçek: nüfus ağırlığı ortalama enlemi neredeyse hiç
    kaydırmıyor.

    Bu ağırlıklandırmanın ev yapılarını belirgin biçimde düzelteceğini
    varsaymıştım; ölçünce yanlış çıktı. Türkiye nüfusu zaten enlem
    aralığına yayılmış (İstanbul 41°, Ankara 39,9°, İzmir 38,4°,
    Antalya 36,9°), dolayısıyla merkez kaymıyor. Test bu bulguyu
    sabitliyor ki gelecekte yine "önemli düzeltme" diye sunulmasın.
    """
    import statistics

    u = random.Random(7)
    adlar = list(TURKIYE_IL_MERKEZLERI)
    agirliklar = [IL_NUFUSU[a] for a in adlar]

    duz = [TURKIYE_IL_MERKEZLERI[u.choice(adlar)][0] for _ in range(20000)]
    agirlikli = [
        TURKIYE_IL_MERKEZLERI[il][0]
        for il in u.choices(adlar, weights=agirliklar, k=20000)
    ]
    ortalama_farki = abs(
        sum(duz) / len(duz) - sum(agirlikli) / len(agirlikli)
    )
    assert ortalama_farki < 0.15, "beklenenden büyük kayma; bulgu değişmiş olabilir"
    # Dağılımın şekli yine de değişiyor: büyük iller uçlara dağılmış.
    assert statistics.pstdev(agirlikli) > statistics.pstdev(duz)


# --------------------------------------------------------------------------
# Ay dağılımı
# --------------------------------------------------------------------------

def test_ay_agirliklari_on_iki_ay():
    assert len(AY_AGIRLIKLARI) == 12


def test_temmuz_subattan_daha_agir():
    """TÜİK verisi: Temmuz zirve, Şubat dip."""
    assert AY_AGIRLIKLARI[6] > AY_AGIRLIKLARI[1]


def test_ay_secimi_gecerli_aralikta_ve_yaza_kayik():
    u = random.Random(3)
    aylar = Counter(ay_sec(u) for _ in range(20000))
    assert set(aylar) <= set(range(1, 13))
    assert aylar[7] > aylar[2]


# --------------------------------------------------------------------------
# Saat senaryoları
# --------------------------------------------------------------------------

def test_varsayilan_senaryo_en_az_varsayim_iceren():
    """Türkiye için saat dağılımı bilinmiyor; varsayılan tek düze olmalı.
    Uydurma bir dağılımı varsayılan yapmak, sayıları dayanaksız biçimde
    hassas gösterir."""
    assert VARSAYILAN_SENARYO == "duz"
    assert len(set(SENARYOLAR["duz"].agirliklar)) == 1


@pytest.mark.parametrize("anahtar", sorted(SENARYOLAR))
def test_senaryolar_yirmi_dort_saat_kapsar(anahtar):
    s = SENARYOLAR[anahtar]
    assert len(s.agirliklar) == 24
    assert all(a > 0 for a in s.agirliklar), "sıfır ağırlık saati imkânsız kılar"


def test_mesai_senaryosu_sabaha_yigiyor():
    u = random.Random(5)
    c = Counter(SENARYOLAR["mesai"].sec(u) for _ in range(20000))
    sabah = sum(c[h] for h in range(8, 13)) / 20000
    assert sabah > 0.40


def test_gece_senaryosu_sabaha_karsi_yigiyor():
    u = random.Random(5)
    c = Counter(SENARYOLAR["gece"].sec(u) for _ in range(20000))
    gece = sum(c[h] for h in range(1, 8)) / 20000
    assert gece > 0.40


def test_senaryolar_birbirinden_gercekten_farkli():
    """Duyarlılık analizi ancak senaryolar farklıysa anlamlı."""
    u = random.Random(11)
    dagilimlar = {}
    for anahtar, s in SENARYOLAR.items():
        c = Counter(s.sec(u) for _ in range(10000))
        dagilimlar[anahtar] = [c[h] / 10000 for h in range(24)]
    duz, mesai = dagilimlar["duz"], dagilimlar["mesai"]
    fark = sum(abs(a - b) for a, b in zip(duz, mesai))
    assert fark > 0.30, "senaryolar yeterince ayrışmıyor"
