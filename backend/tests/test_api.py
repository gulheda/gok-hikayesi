"""API uç noktası testleri (LLM çağrısı içermeyenler)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_saglik_ucu_efemeris_durumunu_bildirir():
    r = client.get("/saglik")
    assert r.status_code == 200
    d = r.json()
    assert d["durum"] == "calisiyor"
    assert d["efemeris_dosyalari_var"] is True
    assert "placidus" in d["desteklenen_ev_sistemleri"]


def test_harita_ucu_saatli_girdiyi_hesaplar():
    r = client.post("/api/harita", json={
        "ad": "Test", "tarih": "2003-07-03", "saat": "09:00", "yer": "Denizli",
    })
    assert r.status_code == 200
    d = r.json()
    assert d["yer"]["kaynak"] == "offline_tr"   # ağa çıkmadan çözülmeli
    assert d["harita"]["evler"]["mevcut"] is True
    assert d["harita"]["evler"]["yukselen_burc"] == "Aslan"
    assert len(d["harita"]["gok_cisimleri"]) == 12


def test_harita_ucu_saatsiz_girdide_ev_uretmez():
    r = client.post("/api/harita", json={"tarih": "2003-07-03", "yer": "Denizli"})
    assert r.status_code == 200
    harita = r.json()["harita"]
    assert harita["evler"]["mevcut"] is False
    assert harita["evler"]["yukselen_burc"] is None
    assert harita["meta"]["uyarilar"]


@pytest.mark.parametrize("govde,beklenen_sebep", [
    ({"tarih": "2015-03-29", "saat": "03:30", "yer": "Denizli"}, "yaşanmadı"),
    ({"tarih": "2015-11-08", "saat": "03:30", "yer": "Denizli"}, "iki kez"),
])
def test_yaz_saati_gecisleri_422_dondurur(govde, beklenen_sebep):
    r = client.post("/api/harita", json=govde)
    assert r.status_code == 422
    assert beklenen_sebep in r.json()["detail"]


@pytest.mark.parametrize("govde", [
    {"tarih": "1750-01-01", "yer": "Denizli"},            # efemeris aralığı dışı
    {"tarih": "2003-07-03", "yer": "D"},                   # çok kısa yer adı
    {"tarih": "2003-07-03", "yer": "Denizli", "ev_sistemi": "yok"},
    {"yer": "Denizli"},                                    # tarih eksik
])
def test_gecersiz_girdiler_reddedilir(govde):
    assert client.post("/api/harita", json=govde).status_code == 422


def test_bulunamayan_yer_422_dondurur():
    r = client.post("/api/harita", json={
        "tarih": "2003-07-03",
        "yer": "Qxzvbnm Olmayan Sehir 12345",
    })
    assert r.status_code == 422
