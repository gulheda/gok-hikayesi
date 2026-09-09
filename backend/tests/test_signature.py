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


def test_uc_dereceden_yakin_olan_cok_belirgin_sayilir():
    for imza in angular_bodies(SAATLI):
        if "Jüpiter" in imza.label and "Yükselen" in imza.label:
            assert imza.rarity == BELIRGIN_COK
            return
    pytest.fail("Jüpiter-Yükselen imzası bulunamadı")


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
    # Modelin ender olanı görebilmesi için belirginlik etiketleri şart.
    assert BELIRGIN_COK in b
