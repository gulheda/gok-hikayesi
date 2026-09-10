"""Türkçe ek çekimi testleri.

Şablonla Türkçe metin üretmenin asıl zorluğu burada: ek, eklendiği
kelimenin son ünlüsüne ve son ünsüzüne göre değişir. Bozuk bir ek
("Topraki", "Ay'ti", "kıyısıda") içerik ne kadar iyi olursa olsun metni
anında ucuzlatır, ve bu hatalar sessizdir - hiçbir şey patlamaz.
"""
from __future__ import annotations

from datetime import date

import pytest

from app.story.sablon.turkce import (
    belirtme,
    bulunma,
    de_baglaci,
    gecmis_kopula,
    gunun_vakti,
    hece_sayisi,
    iyelik3,
    kalin_mi,
    mekan_bulunma,
    sayi_sifat,
    son_unlu,
    tamlayan,
    tarih_yazi,
    yonelme,
    yumusat,
)


@pytest.mark.parametrize("kelime,beklenen", [
    ("toprak", "a"), ("ateş", "e"), ("su", "u"), ("köprü", "ü"),
    ("İstanbul", "u"), ("Ay", "a"),
])
def test_son_unlu(kelime, beklenen):
    assert son_unlu(kelime) == beklenen


@pytest.mark.parametrize("kelime,kalin", [
    ("toprak", True), ("ateş", False), ("Jüpiter", False), ("Mars", True),
])
def test_buyuk_unlu_uyumu(kelime, kalin):
    assert kalin_mi(kelime) is kalin


# --------------------------------------------------------------------------
# Ünsüz yumuşaması
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kelime,beklenen", [
    ("toprak", "toprağı"),      # çok heceli, k -> ğ
    ("kitap", "kitabı"),        # p -> b
    ("ağaç", "ağacı"),          # ç -> c
    ("kanat", "kanadı"),        # t -> d
])
def test_cok_heceli_kelimeler_yumusar(kelime, beklenen):
    assert belirtme(kelime) == beklenen


@pytest.mark.parametrize("kelime,beklenen", [
    ("at", "atı"), ("saç", "saçı"), ("ok", "oku"), ("üst", "üstü"),
])
def test_tek_heceli_kelimeler_genelde_yumusamaz(kelime, beklenen):
    assert belirtme(kelime) == beklenen


def test_hece_sayisi():
    assert hece_sayisi("toprak") == 2
    assert hece_sayisi("at") == 1
    assert hece_sayisi("gökyüzü") == 3


def test_yumusatma_buyuk_harfi_bozmaz():
    assert yumusat("Toprak").startswith("T")


# --------------------------------------------------------------------------
# Durum ekleri
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kelime,beklenen", [
    ("meydan", "meydanda"),     # yumuşak ünsüz -> d
    ("düzlük", "düzlükte"),     # sert ünsüz -> t
    ("kapı", "kapıda"),
    ("köprü", "köprüde"),
    ("yamaç", "yamaçta"),
])
def test_bulunma_hali(kelime, beklenen):
    assert bulunma(kelime) == beklenen


def test_ozel_adlarda_kesme_isareti():
    assert bulunma("Denizli", ozel_ad=True) == "Denizli'de"
    assert bulunma("Sinop", ozel_ad=True) == "Sinop'ta"


@pytest.mark.parametrize("kelime,beklenen", [
    ("kapı", "kapıya"), ("ev", "eve"), ("toprak", "toprağa"),
])
def test_yonelme_hali(kelime, beklenen):
    assert yonelme(kelime) == beklenen


@pytest.mark.parametrize("kelime,beklenen", [
    ("Jüpiter", "Jüpiter'in"), ("Satürn", "Satürn'ün"),
    ("Ay", "Ay'ın"), ("Mars", "Mars'ın"),
])
def test_tamlayan_hali(kelime, beklenen):
    assert tamlayan(kelime, ozel_ad=True) == beklenen


@pytest.mark.parametrize("kelime,beklenen", [
    ("kapı", "kapısı"), ("kule", "kulesi"),
    ("bodrum", "bodrumu"), ("toprak", "toprağı"),
])
def test_iyelik_eki(kelime, beklenen):
    assert iyelik3(kelime) == beklenen


# --------------------------------------------------------------------------
# Geçmiş zaman ek-fiili — en sık hata yapılan yer
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ad,beklenen", [
    ("Güneş", "Güneş'ti"),     # ş sert -> t
    ("Ay", "Ay'dı"),           # y yumuşak -> d
    ("Merkür", "Merkür'dü"),
    ("Mars", "Mars'tı"),        # s sert
    ("Venüs", "Venüs'tü"),
    ("Jüpiter", "Jüpiter'di"),
])
def test_gecmis_kopula(ad, beklenen):
    assert gecmis_kopula(ad, ozel_ad=True) == beklenen


# --------------------------------------------------------------------------
# İyelikli yer adları
# --------------------------------------------------------------------------

def test_zaten_iyelikli_yer_adina_ikinci_iyelik_eklenmez():
    """'gelgit kıyısı' zaten iyelik eki taşır; düz birleştirme
    'kıyısısında' üretirdi."""
    assert mekan_bulunma("gelgit kıyısı", zaten_iyelikli=True) == "gelgit kıyısında"
    assert mekan_bulunma("dağ geçidi", zaten_iyelikli=True) == "dağ geçidinde"


def test_yalin_yer_adi_dogrudan_bulunma_alir():
    assert mekan_bulunma("meydan") == "meydanda"
    assert mekan_bulunma("köprü") == "köprüde"


# --------------------------------------------------------------------------
# Bağlaç ve yardımcılar
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kelime,beklenen", [
    ("Ay", "da"), ("Jüpiter", "de"), ("Mars", "da"), ("Venüs", "de"),
])
def test_de_baglaci_unsuz_benzesmesine_ugramaz(kelime, beklenen):
    """Ayrı yazılan 'de/da' bağlacı sertleşmez: 'Mars da', 'Mars ta' değil."""
    assert de_baglaci(kelime) == beklenen


def test_sayi_sifat():
    assert sayi_sifat(4) == "dört"
    assert sayi_sifat(0) == "hiç"
    assert sayi_sifat(99) == "99"


def test_tarih_yazi():
    assert tarih_yazi(date(2003, 7, 3)) == "3 Temmuz 2003"


@pytest.mark.parametrize("saat,beklenen", [
    (9, "sabahı"), (12, "öğlesi"), (17, "ikindisi"), (21, "akşamı"), (3, "gecesi"),
])
def test_gunun_vakti(saat, beklenen):
    assert gunun_vakti(saat) == beklenen
