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
    assert "Buraya kadarı ölçümdür" in govde
    assert "Bundan sonrası değildir" in govde


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
    # Ayırıcı, ardından büyük harf gelmesini şart koşuyor: "10. derecesinde"
    # gibi sıra sayıları cümle sonu değildir. TTS parçalayıcısı da aynı
    # kuralı kullanıyor (bkz. app/tts/chunking.py).
    ayirici = r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ])"
    for harita in (SAATLI, SAATSIZ, BASKA):
        _, govde = uret(harita)
        for cumle in re.split(ayirici, govde.replace("\n", " ")):
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


# --------------------------------------------------------------------------
# Masal biçimi (v2.0.0): kişi baş kahraman
# --------------------------------------------------------------------------

def test_kisi_edilgen_degil_eden_taraf():
    """Masalın baş kahramanı bir şeyler YAPAR; ona bir şeyler olmaz."""
    _, govde = uret(SAATLI)
    eylemler = ["girdin", "açtın", "yürüdün", "vardın", "gittin", "geçtin"]
    bulunan = [e for e in eylemler if e in govde]
    assert len(bulunan) >= 3, f"kişi yeterince eylemde bulunmuyor: {bulunan}"


def test_kisi_ovulmez():
    """Övgü hem genellik testinden geçemez hem baş kahramanlığı sıfattan
    türetir. Baş kahraman överek değil yaparak baş kahraman olur."""
    ovguler = ["cesursun", "özelsin", "güçlüsün", "lidersin", "duygusalsın",
               "sezgilerin güçlü", "yeteneklisin", "zekisin"]
    for harita in (SAATLI, SAATSIZ, BASKA):
        _, govde = uret(harita)
        for ovgu in ovguler:
            assert ovgu not in govde, f"övgü bulundu: {ovgu}"


def test_masal_esikle_baslar_varisla_biter():
    _, govde = uret(SAATLI)
    paragraflar = govde.split("\n\n")
    olgusal_son = next(i for i, p in enumerate(paragraflar)
                       if "Buraya kadarı ölçümdür" in p)
    yolculuk = "\n".join(paragraflar[olgusal_son + 1:])
    assert "girdin" in yolculuk        # eşik
    assert paragraflar[-1]             # varış paragrafı var


def test_eksik_element_arayisa_donusur():
    """Eksik element motorun elindeki en güçlü malzeme: aranan şey."""
    _, govde = uret(SAATLI)   # bu haritada Toprak eksik
    assert "aradın" in govde
    assert "bulamadın" in govde


def test_gelecekten_soz_edilmez():
    """Kehanet yok: masal geçmiş ve şimdiki zamanda kalmalı."""
    gelecek = ["olacaksın", "yapacaksın", "bulacaksın", "göreceksin",
               "kazanacaksın", "seni bekliyor"]
    for harita in (SAATLI, SAATSIZ, BASKA):
        _, govde = uret(harita)
        for kalip in gelecek:
            assert kalip not in govde, f"gelecek zaman ifadesi: {kalip}"


def test_masal_olcumden_kopmaz():
    """Ürünün tek iddiası 'bu senin gökyüzün'. Masal ölçümden koparsa
    geriye herhangi bir masal kalır ve iddia görünmez olur."""
    _, govde = uret(SAATLI)
    yolculuk = govde.split("Bundan sonrası değildir")[1]
    # Sembolik bölümde de gerçek derece/burç bilgisi geçmeli
    assert "derece" in yolculuk
    assert any(burc in yolculuk for burc in
               ["Aslan", "Yengeç", "İkizler", "Balık", "Kova", "Yay"])


def test_gecis_ayni_gokyuzune_isaret_eder():
    """Geçiş bir duvar değil menteşe: 'şimdi uydurma başlıyor' değil,
    'aynı gökyüzü, ikinci kez'."""
    _, govde = uret(SAATLI)
    assert "aynı diziliş" in govde


def test_acisal_nokta_referansi_astronomik_olarak_dogru():
    """Yükselen ufuktadır ama Tepe noktası ufuk değil, gökyüzünün en
    yüksek yeridir. Hepsine 'ufuktan' demek metni yanlış yapar."""
    from app.story.sablon.sozluk import ACISAL_NOKTA_ADI
    assert "ufk" in ACISAL_NOKTA_ADI["Yükselen"].referans
    assert "ufk" not in ACISAL_NOKTA_ADI["Tepe noktası"].referans
    assert "tepe" in ACISAL_NOKTA_ADI["Tepe noktası"].referans


def test_mekan_fiil_ve_edat_uyumlu():
    """Kapı AÇILIR (onu), kuleye ÇIKILIR (oraya).

    Edatı sabitleyip yalnızca fiili değiştirmek "oraya sen açtın" gibi
    bozuk cümleler üretiyordu; bu yüzden tam cümle saklanıyor.
    """
    from app.story.sablon.sozluk import ACISAL_NOKTA_ADI
    assert ACISAL_NOKTA_ADI["Yükselen"].varis == "Onu sen açtın"
    assert ACISAL_NOKTA_ADI["Tepe noktası"].varis == "Oraya sen çıktın"
    assert ACISAL_NOKTA_ADI["Dip nokta"].varis == "Oraya sen indin"


def test_bolum_sirasi_omurgadan_gelir():
    """Sabit bir sıra, her haritada aynı hamleleri tekrarlamak demekti."""
    from app.story.omurga import kur as omurga_kur
    from app.story.sablon.motor import BOLUM_KAYDI

    for harita in (SAATLI, BASKA):
        omurga = omurga_kur(harita)
        beklenen = []
        for durak in omurga.duraklar:
            bolum = BOLUM_KAYDI.get(durak.imza.key)
            if bolum and bolum not in beklenen:
                beklenen.append(bolum)
        assert beklenen, "omurgadan hiç bölüm türetilemedi"


def test_turkce_buyuk_harf_hatasi_metne_sizmaz():
    """'Içsel' gibi biçimler metni anında yabancı gösterir."""
    for harita in (SAATLI, SAATSIZ, BASKA):
        _, govde = uret(harita)
        for bozuk in ("Içsel", "Ilişki", "Iki ", "Ilk "):
            assert bozuk not in govde, f"yanlış büyük harf: {bozuk}"


def test_zincir_girisi_gereksiz_tekrar_etmez():
    """Bölüm ortak cismi zaten anıyorsa bağlantı cümlesi eklenmemeli."""
    for harita in (SAATLI, BASKA):
        _, govde = uret(harita)
        assert govde.count("bir kez daha karşına çıktı") <= 1


def test_sablon_motorunda_python_capitalize_kullanilmaz():
    """Gizli tuzak: capitalize() bugün zararsız olabilir ama sözlüğe
    'i' ile başlayan bir metin eklendiği an sessizce bozulur. Türkçe
    metin üreten hiçbir yerde kullanılmamalı."""
    import pathlib

    kok = pathlib.Path(__file__).resolve().parents[1] / "app" / "story"
    suclular = []
    for yol in kok.rglob("*.py"):
        icerik = yol.read_text(encoding="utf-8")
        for no, satir in enumerate(icerik.splitlines(), start=1):
            if ".capitalize()" in satir and not satir.lstrip().startswith("#"):
                # Açıklama metinlerinde geçmesi serbest.
                if "`str.capitalize()`" in satir or "Python'un" in satir:
                    continue
                suclular.append(f"{yol.name}:{no}")
    assert not suclular, f"capitalize() kullanımı: {suclular}"
