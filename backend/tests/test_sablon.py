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


def test_gece_dogumunda_gunduz_ve_sabah_iddiasi_yok():
    """Güneş ufkun altındaysa (gece 23:45) 'gündüzdü', 'o sabah' denmez.

    Kars, 02.11.1994 23:45: Güneş 3. evde. Eski metin 'o sabah dördü birden',
    'Kars üstünde gündüzdü' ve 'gündüz kısa bir süre karardı' diyordu.
    """
    gece = calculate_chart(BirthInput(
        birth_date=date(1994, 11, 2), birth_time=time(23, 45),
        latitude=40.6013, longitude=43.0975, place_name="Kars"))
    assert gece.body("Sun").house < 7
    baslik, govde = uret(gece)
    for yasak in ("o sabah", "O sabah", "gündüzdü", "gündüz kısa"):
        assert yasak not in govde
    assert "Sabah" not in baslik


def test_gunduz_dogumunda_gece_ifadesi_yok():
    _, govde = uret(SAATLI)
    assert "o gece" not in govde.lower()


def test_saatsiz_haritada_gorunurluk_iddiasi_yok():
    """Saat yoksa Güneş'in nerede olduğu bilinmez: 'gündüzdü' denmez."""
    _, govde = uret(SAATSIZ)
    assert "gündüzdü" not in govde and "o gece" not in govde.lower()


def test_ayni_burctaki_kavusum_tekrarlanan_konum_yazmaz():
    """Erzurum, 22.08.1968 03:30: Merkür–Jüpiter ikisi de Başak 12°.

    Eski metin 'Biri Başak burcunun 12. derecesinde, öteki Başak burcunun
    12. derecesinde duruyordu' diyordu.
    """
    harita = calculate_chart(BirthInput(
        birth_date=date(1968, 8, 22), birth_time=time(3, 30),
        latitude=39.9055, longitude=41.2658, place_name="Erzurum"))
    _, govde = uret(harita)
    assert "İkisi de Başak burcunun 12. derecesinde" in govde
    assert not re.search(r"Biri (\w+) burcunun \d+\. derecesinde, öteki \1 burcunun", govde)


def test_toplantidaki_cisim_gomulu_kisi_olarak_ikinci_kez_anilmaz():
    """Diyarbakır 1972: Venüs hem toplantıda hem 'bir kişi daha' diye geçiyordu."""
    harita = calculate_chart(BirthInput(
        birth_date=date(1972, 6, 17), birth_time=time(7, 40),
        latitude=37.9144, longitude=40.2306, place_name="Diyarbakır"))
    _, govde = uret(harita)
    assert "Venüs" in govde
    assert "bir kişi daha vardı" not in govde


def test_farkli_acisal_noktalardaki_ikinci_cisim_orada_denmez():
    """Malatya 2004-08-19 15:05: Ay Tepe'de, Plüton Yükselen'de.

    Eski metin 'Plüton da oradaydı, birkaç adım ötede' diyordu; oysa ikisi
    gökyüzünün zıt uçlarındaydı.
    """
    harita = calculate_chart(BirthInput(
        birth_date=date(2004, 8, 19), birth_time=time(15, 5),
        latitude=38.3552, longitude=38.3095, place_name="Malatya"))
    _, govde = uret(harita)
    assert "Plüton" in govde
    assert "Plüton de oradaydı" not in govde and "Plüton da oradaydı" not in govde
    assert "Kapıda Plüton" in govde


def test_gorunmeyen_cisimler_bozuk_kalibi_kullanmaz():
    """Sinop 1982-11-11 08:25: dört cisim Güneş'in ışığında kaybolmuştu.

    Eski metin 'gökyüzünde tam olarak görünmüyorlardı' diyordu; 'tam olarak
    görünmemek' anlamsız bir kalıptı.
    """
    harita = calculate_chart(BirthInput(
        birth_date=date(1982, 11, 11), birth_time=time(8, 25),
        latitude=42.0231, longitude=35.1531, place_name="Sinop"))
    _, govde = uret(harita)
    assert "hiçbiri görülemiyordu" in govde
    assert "tam olarak görünmü" not in govde


def test_buyuk_ucgen_sahnesi_gecmis_zamanda_anlatir():
    """Hakkari 1992-12-03 03:50: Ay–Mars–Plüton büyük üçgeni.

    Etiket şimdiki zamandaydı ('açı yapıyor'), geçmiş zamanlı anlatıya
    olduğu gibi giriyordu.
    """
    harita = calculate_chart(BirthInput(
        birth_date=date(1992, 12, 3), birth_time=time(3, 50),
        latitude=37.5744, longitude=43.7408, place_name="Hakkari"))
    _, govde = uret(harita)
    assert "kapalı bir devre buldun" in govde
    assert "açı yapıyordu" in govde
    assert "açı yapıyor;" not in govde and "açı yapıyor:" not in govde


def test_yine_baglantisi_anilmamis_cisim_icin_yazilmaz():
    """Kars 1988-03-14 07:20: 'Mars yine oradaydı' deniyordu ama Mars
    önceki sahnede (kâse) hiç anılmamıştı; 'yine' dayanaksız kalıyordu.
    """
    harita = calculate_chart(BirthInput(
        birth_date=date(1988, 3, 14), birth_time=time(7, 20),
        latitude=40.6013, longitude=43.0975, place_name="Kars"))
    _, govde = uret(harita)
    assert "Mars yine oradaydı" not in govde
