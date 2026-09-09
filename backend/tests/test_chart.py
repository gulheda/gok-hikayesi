"""Harita yapısı, ev sistemi ve açı mantığı testleri."""
from __future__ import annotations

from datetime import date, time

import pytest

from app.astro.aspects import angular_separation, find_aspects
from app.astro.chart import BirthInput, calculate_chart
from app.astro.constants import CORE_BODY_KEYS
from app.astro.houses import calculate_houses, house_of_longitude

DENIZLI = dict(latitude=37.7765, longitude=29.0864, place_name="Denizli, Türkiye")

SAATLI = BirthInput(birth_date=date(2003, 7, 3), birth_time=time(9, 0), **DENIZLI)
SAATSIZ = BirthInput(birth_date=date(2003, 7, 3), birth_time=None, **DENIZLI)


# --------------------------------------------------------------------------
# Ev sistemi
# --------------------------------------------------------------------------

def test_karsit_ev_baslangiclari_tam_180_derece_karsida():
    h = calculate_houses(2452823.75, 37.7765, 29.0864)
    for i in range(6):
        fark = angular_separation(
            h.houses[i].cusp_longitude, h.houses[i + 6].cusp_longitude
        )
        assert fark == pytest.approx(180.0, abs=1e-9)


def test_yukselen_birinci_ev_baslangicina_esit():
    h = calculate_houses(2452823.75, 37.7765, 29.0864)
    assert h.ascendant == pytest.approx(h.houses[0].cusp_longitude, abs=1e-9)


def test_her_boylam_tam_olarak_bir_eve_dusue():
    h = calculate_houses(2452823.75, 37.7765, 29.0864)
    for tam_derece in range(360):
        ev = house_of_longitude(float(tam_derece), h)
        assert ev is not None and 1 <= ev <= 12


def test_kutup_bolgesinde_placidus_yerine_whole_sign_kullanilir():
    # Placidus 66° enlemin ötesinde matematiksel olarak tanımsızlaşır;
    # sessizce anlamsız sayı üretmek yerine sistem değiştirilmeli.
    h = calculate_houses(2452823.75, 69.6, 18.9, "placidus")
    assert h.system_key == "whole_sign"
    assert h.fallback_reason is not None


def test_bilinmeyen_ev_sistemi_hata_verir():
    with pytest.raises(ValueError, match="Bilinmeyen ev sistemi"):
        calculate_houses(2452823.75, 37.7765, 29.0864, "yok-boyle-bir-sistem")


# --------------------------------------------------------------------------
# Doğum saati bilinmiyorsa dürüst bozunma
# --------------------------------------------------------------------------

def test_saat_bilinmiyorsa_ev_ve_yukselen_uretilmez():
    # Ürünün "gerçek astronomik veri" iddiasının korunduğu yer burası:
    # uydurma bir saatten türetilmiş Yükselen üretip bunu hikâyede
    # gerçekmiş gibi kullanmak iddiayı çürütür.
    c = calculate_chart(SAATSIZ)
    assert c.houses.available is False
    assert c.rising_sign_tr is None
    assert c.houses.unavailable_reason is not None
    assert all(b.house is None for b in c.bodies)
    assert all(b.house_theme_tr is None for b in c.bodies)


def test_saat_bilinmiyorsa_kullanici_uyarilir():
    c = calculate_chart(SAATSIZ)
    assert c.warnings, "saat bilinmiyorken uyarı üretilmeli"
    assert "Yükselen" in c.warnings[0]


def test_saat_bilinmese_de_gezegen_burclari_uretilir():
    # Yavaş gezegenler gün içinde burç değiştirmez; bu veri hâlâ geçerlidir.
    c = calculate_chart(SAATSIZ)
    assert c.sun_sign_tr == "Yengeç"
    assert c.body("Pluto").sign_name_tr == "Yay"


def test_saatli_haritada_ev_verisi_tam():
    c = calculate_chart(SAATLI)
    assert c.houses.available is True
    assert c.rising_sign_tr == "Aslan"
    assert all(b.house is not None for b in c.bodies)
    assert not c.warnings


# --------------------------------------------------------------------------
# Açılar
# --------------------------------------------------------------------------

def test_acisal_mesafe_hep_0_180_arasinda_ve_simetrik():
    for a, b in [(10.0, 350.0), (0.0, 180.0), (359.0, 1.0), (90.0, 270.0)]:
        d = angular_separation(a, b)
        assert 0.0 <= d <= 180.0
        assert d == pytest.approx(angular_separation(b, a))
    assert angular_separation(10.0, 350.0) == pytest.approx(20.0)


def test_bir_cift_en_fazla_bir_aci_yapar():
    c = calculate_chart(SAATLI)
    ciftler = [frozenset((a.body_a, a.body_b)) for a in c.aspects]
    assert len(ciftler) == len(set(ciftler))


def test_aci_gucu_orb_kucuklukce_artar():
    c = calculate_chart(SAATLI)
    for a in c.aspects:
        assert 0.0 <= a.strength <= 1.0
        assert a.orb <= a.max_orb
    # liste güçten zayıfa sıralı olmalı
    gucler = [a.strength for a in c.aspects]
    assert gucler == sorted(gucler, reverse=True)


def test_isiklarda_daha_genis_tolerans_kullanilir():
    c = calculate_chart(SAATLI)
    isikli = [a for a in c.aspects if "Sun" in (a.body_a, a.body_b)]
    isiksiz = [a for a in c.aspects if "Sun" not in (a.body_a, a.body_b)
               and "Moon" not in (a.body_a, a.body_b)]
    for a in isikli:
        for b in isiksiz:
            if a.type_key == b.type_key:
                assert a.max_orb > b.max_orb


def test_acilar_sadece_cekirdek_kadro_arasinda_aranir():
    c = calculate_chart(SAATLI)
    for a in c.aspects:
        assert a.body_a in CORE_BODY_KEYS and a.body_b in CORE_BODY_KEYS


# --------------------------------------------------------------------------
# Denge ve serileştirme
# --------------------------------------------------------------------------

def test_element_dagilimi_cekirdek_kadro_sayisina_esit():
    c = calculate_chart(SAATLI)
    assert sum(c.balance.elements.values()) == len(CORE_BODY_KEYS)
    assert sum(c.balance.modalities.values()) == len(CORE_BODY_KEYS)


def test_gerileme_bayragi_hizla_tutarli():
    c = calculate_chart(SAATLI)
    for b in c.bodies:
        assert b.is_retrograde == (b.speed_longitude < 0)
    # Güneş ve Ay Dünya'dan bakınca hiçbir zaman gerilemez.
    assert not c.body("Sun").is_retrograde
    assert not c.body("Moon").is_retrograde


def test_sozluk_ciktisi_json_uyumlu():
    import json

    for girdi in (SAATLI, SAATSIZ):
        d = calculate_chart(girdi).to_dict()
        json.dumps(d, ensure_ascii=False)  # serileştirilemezse patlar
        assert d["giris"]["saat_biliniyor"] is girdi.time_known
        assert d["evler"]["mevcut"] is girdi.time_known
        assert len(d["gok_cisimleri"]) == 12
