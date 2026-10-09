"""Çevrimdışı yer tablosu: il merkezleri ve yurtdışı büyük şehirler."""
import pytest

from app.geo import geocode as gc
from app.geo import places


def test_yurtdisi_tablo_koordinatlari_gecerli():
    for ad, (lat, lon, ulke) in places.YURTDISI_SEHIRLER.items():
        assert -90 <= lat <= 90 and -180 <= lon <= 180, ad
        assert ulke
        assert ad == places.normalize(ad)


def test_takma_adlar_tabloda_bir_sehre_gider():
    for takma, hedef in places.YURTDISI_TAKMA_ADLAR.items():
        assert hedef in places.YURTDISI_SEHIRLER, takma


def test_ulke_yazimlari_tabloda_kullanilan_ulkelere_gider():
    ulkeler = {v[2] for v in places.YURTDISI_SEHIRLER.values()}
    assert set(places._ULKE_YAZIMLARI.values()) <= ulkeler


def test_berlin_ve_yabanci_yazimlar():
    lat, lon, sehir, ulke = places.lookup_yurtdisi("Berlin")
    assert (round(lat), round(lon), ulke) == (53, 13, "Almanya")
    assert places.lookup_yurtdisi("München, Germany")[:2] == places.lookup_yurtdisi("Münih")[:2]
    assert places.lookup_yurtdisi("London, UK")[3] == "Birleşik Krallık"


def test_yanlis_ulke_nominatim_icin_dusurulur():
    with pytest.raises(KeyError):
        places.lookup_yurtdisi("Paris, Texas")
    with pytest.raises(KeyError):
        places.lookup_yurtdisi("Bilinmeyen")


def test_geocode_yurtdisi_agsiz(monkeypatch):
    def yasak(*a, **k):
        raise AssertionError("ağa çıkılmamalıydı")
    monkeypatch.setattr(gc, "_geocode_nominatim", yasak)
    p = gc.geocode("Amsterdam, Hollanda")
    assert p.source == "offline_yurtdisi"
    assert p.display_name == "Amsterdam, Hollanda"
    assert abs(p.latitude - 52.37) < 0.01


def test_il_tablosu_degismedi():
    assert len(places.TURKIYE_IL_MERKEZLERI) == 81
