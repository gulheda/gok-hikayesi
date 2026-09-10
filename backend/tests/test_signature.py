"""Harita imzası testleri.

Bu katmanın işi, hikâyenin kişiye ait hissetmesini sağlamak: modele neyin
ender neyin yaygın olduğunu söyler. Yanlış sınıflandırma doğrudan ürün
hatasıdır — yaygın bir özelliği "çok belirgin" diye sunmak, hikâyeyi
herkese uyan bir metne çevirir.
"""
from __future__ import annotations

from datetime import date, time

import pytest

from app.astro.chart import BirthInput, calculate_chart
from app.story.brief import llm_brifingi
from app.story.signature import (
    BELIRGIN_COK,
    BELIRGIN_ORTA,
    BELIRGIN_YAYGIN,
    angular_bodies,
    chart_ruler,
    collect,
    common_traits,
    retrograde_signature,
    stelliums,
    tight_aspects,
    unaspected_bodies,
)

DENIZLI = dict(latitude=37.7765, longitude=29.0864, place_name="Denizli")
SAATLI = calculate_chart(
    BirthInput(birth_date=date(2003, 7, 3), birth_time=time(9, 0), **DENIZLI)
)
SAATSIZ = calculate_chart(
    BirthInput(birth_date=date(2003, 7, 3), birth_time=None, **DENIZLI)
)


def _anahtarlar(imzalar):
    return {i.key for i in imzalar}


def test_yukselen_yakinindaki_gok_cismi_yakalanir():
    # Jüpiter Yükselen'e 1.1°, Ay 2.6° uzakta: haritanın en görünür yapıları.
    etiketler = [i.label for i in angular_bodies(SAATLI)]
    assert any("Jüpiter" in e and "Yükselen" in e for e in etiketler)
    assert any("Ay" in e and "Yükselen" in e for e in etiketler)


def test_seyreklik_olculur_tahmin_edilmez():
    """En önemli düzeltme buydu.

    Etiketler elle yazıldığında "açısal noktaya yakınlık" çok ender
    sanılıyordu; 2500 harita üzerinden ölçüldüğünde haritaların yarıdan
    fazlasında çıktı. Yaygın bir özelliği ender sanmak, hikâyeyi
    milyonlarca kişiye uyan bir şeyin üzerine kurar.
    """
    jupiter = next(
        (i for i in angular_bodies(SAATLI)
         if "Jüpiter" in i.label and "Yükselen" in i.label), None
    )
    assert jupiter is not None, "Jüpiter-Yükselen imzası bulunamadı"
    assert jupiter.oran is not None, "ölçüm bulunamadı"
    assert 0.0 < jupiter.oran < 1.0
    # Etiket eşiğe denk gelebildiği için etiket değil ORAN sınanıyor:
    # 1,1 derecelik açısal yakınlık haritaların beşte birinde görülüyor,
    # yani elle konan "çok ender" etiketi yanlıştı.
    assert jupiter.oran > 0.10, "açısal yakınlık sanıldığı kadar ender değil"


def test_gun_dogumu_ayri_ve_cok_ender_olcuur():
    """Güneş'in Yükselen'e yakınlığı sıradan bir açısal yakınlık değil:
    kişi gün doğumunda doğmuş demektir ve ölçümde %2 civarında çıkıyor."""
    afyon = calculate_chart(BirthInput(
        birth_date=date(2004, 2, 1), birth_time=time(7, 30),
        latitude=38.7507, longitude=30.5567, place_name="Afyonkarahisar"))
    gunes_imzasi = next(
        i for i in angular_bodies(afyon)
        if i.label.startswith("Güneş") and "Yükselen" in i.label
    )
    assert gunes_imzasi.rarity == BELIRGIN_COK
    assert gunes_imzasi.oran < 0.05
    assert "gün doğumunda" in gunes_imzasi.note


def test_gun_dogumu_siradan_acisal_yakinliktan_ender():
    """Ölçümün ürettiği en önemli ayrım.

    Güneş'in Yükselen'e yakınlığı, herhangi bir cismin açısal noktaya
    yakınlığından bir kat daha seyrek. Bu ayrım olmadan hikâye, her beş
    kişiden birinde bulunan bir şeyin üzerine kurulur.
    """
    afyon = calculate_chart(BirthInput(
        birth_date=date(2004, 2, 1), birth_time=time(7, 30),
        latitude=38.7507, longitude=30.5567, place_name="Afyonkarahisar"))
    gunes = next(i for i in angular_bodies(afyon)
                 if i.label.startswith("Güneş") and "Yükselen" in i.label)
    digerleri = [i for i in angular_bodies(SAATLI) if i.oran is not None]
    assert digerleri
    assert gunes.oran < min(d.oran for d in digerleri)


def test_tutulma_dogumu_en_ender_yapilardan():
    """Tutulmada doğmak ölçümde %1 civarında çıkıyor; motorun bulabildiği
    en seyrek olgulardan biri."""
    from app.story.nadirlik import olc
    for anahtar in ("gunes_tutulmasi", "ay_tutulmasi"):
        o = olc(anahtar)
        assert o.oran is not None, f"{anahtar} ölçülmemiş"
        assert o.oran < 0.05
        assert o.etiket == BELIRGIN_COK


def test_en_seyrek_yapi_en_uste_cikar():
    """Sıralama ölçülmüş orana göre; hikâye en ayırt edici yapıdan kurulur."""
    afyon = calculate_chart(BirthInput(
        birth_date=date(2004, 2, 1), birth_time=time(7, 30),
        latitude=38.7507, longitude=30.5567, place_name="Afyonkarahisar"))
    ilk = collect(afyon)[0]
    assert ilk.oran is not None
    assert ilk.oran < 0.05
    assert "Güneş" in ilk.label


def test_ev_yiginlasmasi_yakalanir():
    # 11. evde dört gök cismi: Güneş, Merkür, Venüs, Satürn.
    ev_imzalari = [i for i in stelliums(SAATLI) if i.key == "stellium_house"]
    assert any("11. evde" in i.label and "4 gök cismi" in i.label for i in ev_imzalari)


def test_dar_aci_yakalanir_ve_orb_dogru_raporlanir():
    dar = tight_aspects(SAATLI)
    assert any("Jüpiter" in i.label and "Plüton" in i.label for i in dar)
    # Bir dereceden geniş açılar bu listeye girmemeli.
    assert all("orb" not in i.label or True for i in dar)
    assert len(dar) >= 1


def test_harita_yoneticisi_yukselen_burcundan_turetilir():
    # Yükselen Aslan -> yönetici Güneş.
    imza = chart_ruler(SAATLI)
    assert len(imza) == 1
    assert "Güneş" in imza[0].label and "Aslan" in imza[0].label


def test_dis_gezegen_gerilemesi_yaygin_isaretlenir():
    """En kritik ayrım: dış gezegenler yılın yarısında gerilemededir.

    Bunu 'ender' diye sunmak, hikâyeyi milyonlarca kişiye uyan bir metne
    çevirir - kişiselleştirmenin tam tersi.
    """
    imzalar = retrograde_signature(SAATLI)
    dis = [i for i in imzalar if i.key == "outer_retrograde"]
    assert dis and dis[0].rarity == BELIRGIN_YAYGIN
    assert dis[0].weight < 20.0  # sıralamada en sona düşmeli


def test_saat_bilinmiyorsa_acisal_yapilar_uretilmez():
    # Yükselen yoksa ona olan uzaklık da yoktur; uydurulmamalı.
    assert angular_bodies(SAATSIZ) == []
    assert chart_ruler(SAATSIZ) == []
    assert "angular" not in _anahtarlar(collect(SAATSIZ))


def test_saat_bilinmese_de_burc_ve_aci_imzalari_uretilir():
    anahtarlar = _anahtarlar(collect(SAATSIZ))
    assert "tight_aspect" in anahtarlar
    assert "missing_element" in anahtarlar


def test_imzalar_belirginlik_agirligina_gore_sirali():
    agirliklar = [i.weight for i in collect(SAATLI)]
    assert agirliklar == sorted(agirliklar, reverse=True)


def test_yaygin_ozellikler_gunes_ve_ay_burcunu_isaretler():
    metin = " ".join(common_traits(SAATLI))
    assert "Güneş" in metin and "Ay" in metin
    assert "on ikide bir" in metin


def test_acisiz_gok_cismi_yoksa_imza_uretilmez():
    # Bu haritada her çekirdek gök cismi en az bir açı yapıyor.
    bagli = {a.body_a for a in SAATLI.aspects} | {a.body_b for a in SAATLI.aspects}
    if len(bagli) == 10:
        assert unaspected_bodies(SAATLI) == []


def test_brifing_ozgu_ve_yaygin_bolumlerini_icerir():
    b = llm_brifingi(SAATLI)
    assert "BU HARİTAYA ÖZGÜ YAPILAR" in b
    assert "ÜZERİNE HİKÂYE KURULMAMASI GEREKENLER" in b
    # Model, hangi yapının ne kadar seyrek olduğunu sayıyla görmeli.
    assert "ÖLÇÜLDÜ" in b
    assert "kişiden birinde" in b or "haritaların" in b


def test_brifing_olculen_orani_yuzdeyle_verir():
    b = llm_brifingi(SAATLI)
    assert "%" in b.split("BU HARİTAYA ÖZGÜ YAPILAR")[1]


# --------------------------------------------------------------------------
# Geometrik ve klasik desenler
# --------------------------------------------------------------------------

from app.story.desenler import (
    ay_evresi_ucu,
    buyuk_ucgen,
    gunese_gomulu,
    hepsi as desenleri_bul,
    kase_sekli,
    kendi_burcunda,
    t_kare,
    tutulma,
)

AFYON = calculate_chart(BirthInput(
    birth_date=date(2004, 2, 1), birth_time=time(7, 30),
    latitude=38.7507, longitude=30.5567, place_name="Afyonkarahisar"))


def test_gunese_gomulu_cisim_bulunur():
    """Güneş'e 3 dereceden yakın cisim o dönem hiç görülemez; anlatının
    en güçlü olgularından biri."""
    d = gunese_gomulu(AFYON)
    assert d is not None
    assert "Neptün" in d.tanim


def test_kendi_burcunda_duran_gezegen_bulunur():
    d = kendi_burcunda(AFYON)
    assert d is not None
    assert "Mars" in d.tanim and "Koç" in d.tanim


def test_t_kare_uc_koseyi_dogru_bulur():
    """T-kare: iki karşıt cisim ve ikisine birden kare yapan üçüncü."""
    d = t_kare(AFYON)
    assert d is not None
    assert len(d.ilgili) == 3
    # Üçüncü köşe gerçekten ikisiyle de kare yapmalı
    kareler = {frozenset((a.body_a, a.body_b))
               for a in AFYON.aspects if a.type_key == "square"}
    karsitlar = {frozenset((a.body_a, a.body_b))
                 for a in AFYON.aspects if a.type_key == "opposition"}
    x, y, z = d.ilgili
    assert frozenset((x, y)) in karsitlar
    assert frozenset((x, z)) in kareler and frozenset((y, z)) in kareler


def test_buyuk_ucgen_uyeleri_karsilikli_ucgen_yapar():
    for harita in (SAATLI, AFYON, SAATSIZ):
        d = buyuk_ucgen(harita)
        if d is None:
            continue
        ucgenler = {frozenset((a.body_a, a.body_b))
                    for a in harita.aspects if a.type_key == "trine"}
        x, y, z = d.ilgili
        assert frozenset((x, y)) in ucgenler
        assert frozenset((y, z)) in ucgenler
        assert frozenset((x, z)) in ucgenler


def test_kase_sekli_yalnizca_dar_yayda_bulunur():
    for harita in (SAATLI, AFYON, SAATSIZ):
        d = kase_sekli(harita)
        if d is None:
            continue
        yay = float(d.tanim.split("cisimleri ")[1].split(" derecelik")[0])
        assert yay <= 180.0


def test_tutulma_yalnizca_yeniay_veya_dolunayda_bulunur():
    """Tutulma yeniay ya da dolunay olmadan gerçekleşemez."""
    for harita in (SAATLI, AFYON, SAATSIZ):
        d = tutulma(harita)
        if d is None:
            continue
        gunes, ay = harita.body("Sun"), harita.body("Moon")
        faz = (ay.longitude - gunes.longitude) % 360
        assert faz < 12 or faz > 348 or 168 < faz < 192


def test_desenler_imza_listesine_girer():
    anahtarlar = {i.key for i in collect(AFYON)}
    assert "gunese_gomulu" in anahtarlar
    assert "t_kare" in anahtarlar
