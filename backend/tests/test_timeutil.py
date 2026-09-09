"""Zaman çevirisi testleri.

Buradaki hatalar sessizdir: yanlış saat dilimi yanlış bir harita üretir
ama hiçbir şey patlamaz. Bu yüzden tarihsel DST kuralları ve standart
saat öncesi dönem açıkça test edilir.
"""
from __future__ import annotations

from datetime import date, time

import pytest

from app.astro.timeutil import (
    TimeResolutionError,
    local_mean_time_offset_hours,
    resolve_instant,
    timezone_for_coordinates,
)

DENIZLI = (37.7765, 29.0864)
ULM = (48.3984, 9.9916)


def test_koordinattan_saat_dilimi():
    assert timezone_for_coordinates(*DENIZLI) == "Europe/Istanbul"


def test_turkiye_2003te_yaz_saati_uyguluyordu():
    # Türkiye 2016 Eylül'üne kadar yaz saati uygulardı: temel UTC+2, yazın +3.
    r = resolve_instant(date(2003, 7, 3), time(9, 0), *DENIZLI)
    assert r.utc_offset_hours == 3.0
    assert r.is_dst is True
    assert r.utc.hour == 6


def test_turkiye_kisin_utc_arti_iki_idi():
    r = resolve_instant(date(2003, 1, 15), time(9, 0), *DENIZLI)
    assert r.utc_offset_hours == 2.0
    assert r.is_dst is False


def test_turkiye_2016_sonrasi_kalici_utc_arti_uc():
    # 2016'dan sonra yaz saati kaldırıldı: yıl boyu UTC+3, DST yok.
    yaz = resolve_instant(date(2020, 7, 3), time(9, 0), *DENIZLI)
    kis = resolve_instant(date(2020, 1, 15), time(9, 0), *DENIZLI)
    assert yaz.utc_offset_hours == kis.utc_offset_hours == 3.0
    assert yaz.is_dst is False and kis.is_dst is False


def test_standart_saat_oncesi_dogumda_yerel_ortalama_saat_kullanilir():
    # Almanya 1893'te CET'e geçti. Öncesi için tz veritabanı Berlin'in
    # LMT'sini (+0:53:28) verir; Ulm'de doğan biri için bu 13.5 dakika
    # yanlıştır ve Yükselen'i ~3.4 derece kaydırır.
    r = resolve_instant(date(1879, 3, 14), time(11, 30), *ULM)
    assert r.time_standard == "lmt"
    assert r.utc_offset_hours == pytest.approx(ULM[1] / 15.0, abs=1e-9)
    assert r.note is not None


def test_standart_saat_sonrasi_dogumda_bolge_saati_kullanilir():
    r = resolve_instant(date(1950, 3, 14), time(11, 30), *ULM)
    assert r.time_standard == "zone"


def test_yaz_saatinde_hic_yasanmamis_saat_hata_verir():
    # Türkiye 29 Mart 2015'te 03:00'ten 04:00'e atladı; 03:30 hiç yaşanmadı.
    with pytest.raises(TimeResolutionError, match="hiç yaşanmadı"):
        resolve_instant(date(2015, 3, 29), time(3, 30), *DENIZLI)


def test_yaz_saati_bitisinde_belirsiz_saat_hata_verir():
    # 2015'in yaz saati bitişi genel seçim nedeniyle ertelenmişti: her zamanki
    # ekim sonu yerine 8 Kasım 2015'te saatler 04:00'ten 03:00'e alındı,
    # yani 03:30 iki kez yaşandı. Kural değil, tz veritabanı esas alınmalı.
    with pytest.raises(TimeResolutionError, match="iki kez yaşandı"):
        resolve_instant(date(2015, 11, 8), time(3, 30), *DENIZLI)


def test_2016_ekiminde_artik_gecis_yok():
    # Son geçiş 27 Mart 2016; sonrasında kalıcı UTC+3, dolayısıyla eskiden
    # sorunlu olan ekim sonu saatleri artık sorunsuz çözülür.
    r = resolve_instant(date(2016, 10, 30), time(3, 30), *DENIZLI)
    assert r.utc_offset_hours == 3.0


def test_lmt_ofseti_boylamla_orantili():
    assert local_mean_time_offset_hours(0.0) == 0.0
    assert local_mean_time_offset_hours(15.0) == 1.0
    assert local_mean_time_offset_hours(-30.0) == -2.0
