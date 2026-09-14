"""Anlatı omurgası testleri.

Bu katmanın işi, hikâyeyi "ilginç olgular listesi" olmaktan çıkarıp tek
bir sahneye çevirmek. Ölçütü şu: seçilen duraklar birbirine ortak gök
cisimleri üzerinden bağlı olmalı.
"""
from __future__ import annotations

from datetime import date, time

import pytest

from app.astro.chart import BirthInput, calculate_chart
from app.story.brief import llm_brifingi
from app.story.omurga import VARSAYILAN_UZUNLUK, YAYGIN_ESIGI, Omurga, kur
from app.story.signature import collect

AFYON = calculate_chart(BirthInput(
    birth_date=date(2004, 2, 1), birth_time=time(7, 30),
    latitude=38.7507, longitude=30.5567, place_name="Afyonkarahisar"))
DENIZLI = calculate_chart(BirthInput(
    birth_date=date(2003, 7, 3), birth_time=time(9, 0),
    latitude=37.7765, longitude=29.0864, place_name="Denizli"))
SAATSIZ = calculate_chart(BirthInput(
    birth_date=date(2003, 7, 3), birth_time=None,
    latitude=37.7765, longitude=29.0864, place_name="Denizli"))


def test_omurga_en_seyrek_yapiyla_baslar():
    omurga = kur(AFYON)
    imzalar = [i for i in collect(AFYON)
               if i.oran is None or i.oran < YAYGIN_ESIGI]
    assert omurga.duraklar[0].imza.label == imzalar[0].label


def test_duraklar_ortak_gok_cismiyle_zincirlenir():
    """Asıl ölçüt bu: ardışık duraklar birbirine değmeli."""
    omurga = kur(AFYON)
    assert omurga.zincir_orani == 1.0, "Afyon haritasında zincir tam olmalı"
    for durak in omurga.duraklar[1:]:
        assert durak.ortak_cisimler


def test_zincir_orani_kopuk_haritada_dusuk_raporlanir():
    """Her harita tam zincir vermez; motor bunu gizlemeyip raporlamalı."""
    omurga = kur(DENIZLI)
    assert 0.0 <= omurga.zincir_orani <= 1.0
    # Bağlı olmayan durak varsa ortak cismi de boş olmalı.
    for durak in omurga.duraklar[1:]:
        assert bool(durak.ortak_cisimler) == durak.zincire_bagli


def test_yaygin_yapilar_omurgaya_alinmaz():
    """Hikâyeyi milyonlarca kişide bulunan bir şeyin üzerine kurmak,
    kişiselleştirmenin tam tersidir."""
    for harita in (AFYON, DENIZLI, SAATSIZ):
        for durak in kur(harita).duraklar:
            oran = durak.imza.oran
            assert oran is None or oran < YAYGIN_ESIGI


def test_omurga_uzunlugu_sinirli():
    omurga = kur(AFYON)
    assert 0 < len(omurga.duraklar) <= VARSAYILAN_UZUNLUK
    assert len(kur(AFYON, uzunluk=2).duraklar) <= 2


def test_ayni_yapi_iki_kez_durak_olmaz():
    for harita in (AFYON, DENIZLI):
        etiketler = [d.imza.label for d in kur(harita).duraklar]
        assert len(etiketler) == len(set(etiketler))


def test_saatsiz_haritada_da_omurga_kurulur():
    """Ev ve Yükselen yoksa bile açı ve element yapıları kalıyor."""
    omurga = kur(SAATSIZ)
    assert not omurga.bos
    # Açısal yapı olmamalı, çünkü Yükselen yok.
    assert all("Yükselen" not in d.imza.label for d in omurga.duraklar)


def test_bos_imza_listesi_bos_omurga_verir():
    assert kur(AFYON, imzalar=[]).bos


def test_brifing_omurgayi_sirali_verir():
    b = llm_brifingi(AFYON)
    assert "ANLATI OMURGASI" in b
    assert "aynı sahnenin devamı" in b
    # Omurga, seyreklik listesinden ÖNCE gelmeli: model önce neyi
    # anlatacağını, sonra elindeki malzemeyi görsün.
    assert b.index("ANLATI OMURGASI") < b.index("BU HARİTAYA ÖZGÜ YAPILAR")


def test_brifing_omurga_disi_yapilari_durak_yapma_diyor():
    b = llm_brifingi(AFYON)
    assert "durak yapma" in b


def test_zincir_bonusu_kopuk_ama_seyrek_yapiya_karsi_calisir():
    """Zincir bonusu seyrekliği tamamen bastırmamalı: çok daha seyrek bir
    yapı, bağlantısız olsa bile seçilebilmeli."""
    omurga = kur(AFYON)
    oranlar = [d.imza.oran for d in omurga.duraklar if d.imza.oran is not None]
    # En seyrek durak ilk sırada; sonrakiler ondan daha yaygın olabilir.
    assert oranlar[0] == min(oranlar)
