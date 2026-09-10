"""Şablon hikâye motoru testleri."""
from __future__ import annotations

import re
from datetime import date, time

import pytest

from app.astro.chart import BirthInput, calculate_chart
from app.story.sablon.gokyuzu import topla
from app.story.sablon.motor import uret

SAATLI = calculate_chart(BirthInput(
    birth_date=date(2003, 7, 3), birth_time=time(9, 0),
    latitude=37.7765, longitude=29.0864, place_name="Denizli", name="Gülheda"))
SAATSIZ = calculate_chart(BirthInput(
    birth_date=date(2003, 7, 3), birth_time=None,
    latitude=37.7765, longitude=29.0864, place_name="Denizli"))
BASKA = calculate_chart(BirthInput(
    birth_date=date(1995, 12, 21), birth_time=time(23, 45),
    latitude=41.0082, longitude=28.9784, place_name="İstanbul", name="Deneme"))


def test_ayni_harita_ayni_hikayeyi_verir():
    """Kişi ikinci kez baktığında metin değişmemeli."""
    assert uret(SAATLI) == uret(SAATLI)


def test_farkli_haritalar_farkli_hikaye_verir():
    assert uret(SAATLI)[1] != uret(BASKA)[1]


def test_saatsiz_haritada_kapi_bolumu_yazilmaz():
    """Yükselen yoksa açısal yapı da yoktur; uydurulmamalı."""
    _, govde = uret(SAATSIZ)
    assert "Her ülkenin bir kapısı" not in govde
    assert "Doğum saati bilinmiyor" in govde


def test_iskelet_haritaya_gore_degisir():
    """Bölümlerin varlığı haritaya bağlı; sabit dizi kullanılmıyor."""
    a = uret(SAATLI)[1].split("\n\n")
    b = uret(BASKA)[1].split("\n\n")
    assert len(a) != len(b) or a[3] != b[3]


def test_olgusal_bolum_dogrulanabilir_sayilar_icerir():
    _, govde = uret(SAATLI)
    acilis = govde.split("Buraya kadarı ölçümdür")[0]
    assert "09:00" in acilis and "06:00" in acilis
    assert "3 Temmuz 2003" in acilis


def test_olgusal_bolum_sembolik_bolumden_ayrilir():
    _, govde = uret(SAATLI)
    assert "Buraya kadarı ölçümdür. Bundan sonrası değildir." in govde


def test_ad_verilirse_hikayede_gecer():
    _, govde = uret(SAATLI)
    assert "Gülheda" in govde


def test_ad_verilmezse_isim_uydurulmaz():
    _, govde = uret(SAATSIZ)
    assert "Gülheda" not in govde


def test_gorunmez_cisimler_tek_cumlede_birlestirilir():
    """Aynı kalıbı arka arkaya tekrarlamak şablon kokusudur."""
    olgular = topla(SAATLI, en_fazla=8)
    gorunmez = [o for o in olgular if o.anahtar == "gorunmezler"]
    assert len(gorunmez) <= 1


def test_ayni_olgu_iki_kez_anlatilmaz():
    """Olgusal bölümde anlatılan cisim, sembolik bölümde tekrarlanmamalı."""
    _, govde = uret(SAATLI)
    # "ışığın içinde kaybolmuştu" kalıbı yalnızca bir kez geçmeli
    assert govde.count("ışığın içinde") <= 1


def test_dilbilgisi_bilinen_bozuk_bicimleri_uretmiyor():
    """Şablonla Türkçe üretimin tipik kırılmaları."""
    # Kalıp değil, KESİN yanlış biçimler aranıyor. "Jüpiter de" ve
    # "Güneş'ti" doğru biçimlerdir; onları yakalayan bir desen testi
    # kullanılamaz hale getirir.
    bozuklar = [
        "Topraki", "Havai", "Suı",              # yumuşama/uyum hataları
        "Ay'ti", "Merkür'ti", "Jüpiter'tı",     # yanlış ek-fiil
        "Mars de", "Ay de", "Venüs da",         # yanlış de/da
        "sısında", "sıda", "geçidide",          # çift iyelik
        "olan olan", "değildir olan",           # şablon artığı
        "bodrumsı", "kapısı olur; dışarıdan gelen önce oradan bakar ve ülke "
        "hakkındaki ilk şeyi hep oradan öğrenir. Senin ülkende kapısıda",
    ]
    for harita in (SAATLI, SAATSIZ, BASKA):
        _, govde = uret(harita)
        for bozuk in bozuklar:
            assert bozuk not in govde, f"bozuk biçim: {bozuk}"


def test_cumleler_buyuk_harfle_baslar():
    for harita in (SAATLI, SAATSIZ, BASKA):
        _, govde = uret(harita)
        for cumle in re.split(r"(?<=[.!?])\s+", govde.replace("\n", " ")):
            c = cumle.strip()
            if len(c) > 20 and c[0].isalpha():
                assert c[0].isupper(), f"küçük harfle başlıyor: {c[:40]}"


def test_hicbir_ag_cagrisi_yapilmaz(monkeypatch):
    """Motor tamamen çevrimdışı olmalı."""
    import httpx

    def patla(*a, **k):
        raise AssertionError("şablon motoru ağa çıkmamalı")

    monkeypatch.setattr(httpx, "post", patla)
    monkeypatch.setattr(httpx, "get", patla)
    uret(SAATLI)
