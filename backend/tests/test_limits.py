"""İstek sınırlama ve harcama tavanı testleri.

Bu katmanın işi faturayı korumak. Sessizce çalışmaması, ancak fatura
geldiğinde fark edilir; bu yüzden davranışı açıkça sabitleniyor.
"""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.api.koruma import gunluk_tavan, pahali_pencere, ucuz_pencere
from app.api.limits import GunlukTavan, KayanPencere, Kural, LimitAsildi
from app.api.main import app

client = TestClient(app)
GECERLI = {"tarih": "2003-07-03", "saat": "09:00", "yer": "Denizli"}


# --------------------------------------------------------------------------
# Kayan pencere
# --------------------------------------------------------------------------

def test_limit_dolunca_engellenir():
    p = KayanPencere((Kural("test", 3, 60),))
    for i in range(3):
        p.dogrula("a", simdi=100.0 + i)
    with pytest.raises(LimitAsildi):
        p.dogrula("a", simdi=103.0)


def test_kaynaklar_birbirini_etkilemez():
    p = KayanPencere((Kural("test", 2, 60),))
    p.dogrula("a", simdi=100.0)
    p.dogrula("a", simdi=101.0)
    p.dogrula("b", simdi=101.0)  # başka kaynak, kendi kotası


def test_pencere_kayinca_yeniden_izin_verilir():
    p = KayanPencere((Kural("test", 2, 60),))
    p.dogrula("a", simdi=100.0)
    p.dogrula("a", simdi=101.0)
    with pytest.raises(LimitAsildi):
        p.dogrula("a", simdi=110.0)
    p.dogrula("a", simdi=161.0)  # ilk vuruş pencereden çıktı


def test_kayan_pencere_sinira_yiginmayi_engeller():
    """Sabit pencerede istemci sınırın iki yanına yığılıp limitin iki katını
    kısa sürede harcayabilir; kayan pencere buna izin vermemeli."""
    p = KayanPencere((Kural("test", 3, 60),))
    for t in (55.0, 56.0, 57.0):
        p.dogrula("a", simdi=t)
    # Sabit pencere olsaydı 61. saniyede sayaç sıfırlanır ve 3 istek daha geçerdi.
    with pytest.raises(LimitAsildi):
        p.dogrula("a", simdi=61.0)


def test_birden_fazla_kural_ayni_anda_uygulanir():
    p = KayanPencere((Kural("dakikalik", 5, 60), Kural("saatlik", 6, 3600)))
    for i in range(5):
        p.dogrula("a", simdi=float(i))
    with pytest.raises(LimitAsildi, match="dakikada"):
        p.dogrula("a", simdi=5.0)
    p.dogrula("a", simdi=70.0)          # dakikalık pencere kaydı
    with pytest.raises(LimitAsildi, match="saatte"):
        p.dogrula("a", simdi=71.0)      # ama saatlik doldu


def test_tekrar_dene_suresi_pozitif_ve_pencereyi_asmaz():
    p = KayanPencere((Kural("test", 1, 60),))
    p.dogrula("a", simdi=100.0)
    with pytest.raises(LimitAsildi) as bilgi:
        p.dogrula("a", simdi=110.0)
    assert 1 <= bilgi.value.tekrar_dene_saniye <= 60


# --------------------------------------------------------------------------
# Günlük tavan
# --------------------------------------------------------------------------

def test_istek_tavani_dolunca_engellenir():
    t = GunlukTavan(gunluk_istek=2, gunluk_usd=100.0)
    t.dogrula(); t.dogrula()
    with pytest.raises(LimitAsildi, match="kapasite"):
        t.dogrula()


def test_harcama_tavani_gerceklesen_maliyetle_isler():
    """Tavan istek sayısıyla değil, gerçekleşen dolarla da sınırlamalı;
    hikâye başına maliyet uzunluğa göre değiştiği için istek saymak yetmez."""
    t = GunlukTavan(gunluk_istek=1000, gunluk_usd=1.0)
    t.dogrula()
    t.harcama_ekle(1.2)
    with pytest.raises(LimitAsildi, match="harcama"):
        t.dogrula()


def test_gun_degisince_sayaclar_sifirlanir():
    t = GunlukTavan(gunluk_istek=1, gunluk_usd=1.0)
    t.dogrula(bugun=date(2026, 1, 1))
    with pytest.raises(LimitAsildi):
        t.dogrula(bugun=date(2026, 1, 1))
    t.dogrula(bugun=date(2026, 1, 2))  # yeni gün, yeni kota


def test_bos_maliyet_tavani_etkilemez():
    t = GunlukTavan(gunluk_istek=10, gunluk_usd=1.0)
    t.harcama_ekle(None)
    t.harcama_ekle(0.0)
    assert t.durum()["kullanilan_usd"] == 0.0


# --------------------------------------------------------------------------
# Uç noktalar
# --------------------------------------------------------------------------

def test_ucuz_uc_sinira_ulasinca_429_dondurur():
    limit = ucuz_pencere.kurallar[0].limit
    for _ in range(limit):
        assert client.post("/api/harita", json=GECERLI).status_code == 200
    yanit = client.post("/api/harita", json=GECERLI)
    assert yanit.status_code == 429
    # Retry-After olmadan istemci ne zaman tekrar deneyeceğini bilemez.
    assert int(yanit.headers["Retry-After"]) >= 1


def test_pahali_uc_ucuz_uctan_daha_dar_sinirli():
    """Model çağrısı yapan uç, saf hesaplama yapan uçtan daha dar olmalı."""
    assert pahali_pencere.kurallar[0].limit < ucuz_pencere.kurallar[0].limit


def test_pahali_uc_limitten_sonra_429_dondurur():
    saatlik = pahali_pencere.kurallar[0].limit
    for _ in range(saatlik):
        # Anahtar olmadığı için 503; sınırlama yine de sayıyor.
        assert client.post("/api/hikaye", json=GECERLI).status_code == 503
    assert client.post("/api/hikaye", json=GECERLI).status_code == 429


def test_saglik_ucu_tavan_durumunu_bildirir():
    d = client.get("/saglik").json()["gunluk_tavan"]
    assert {"kullanilan_istek", "istek_tavani", "kullanilan_usd", "usd_tavani"} <= set(d)


def test_gecersiz_istek_de_kotadan_dusulur():
    """Doğrulama hatası veren istekler de sayılmalı; aksi hâlde saldırgan
    bozuk gövdelerle sınırsız istek atarak sunucuyu meşgul edebilir."""
    onceki = ucuz_pencere.kurallar[0].limit
    for _ in range(onceki):
        client.post("/api/harita", json={"yer": "x"})  # 422
    assert client.post("/api/harita", json=GECERLI).status_code == 429
