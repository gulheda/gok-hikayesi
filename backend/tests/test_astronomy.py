"""Astronomik doğruluk testleri.

Doğrulama üç bağımsız çıpaya dayanır:

1. Ekinoks ve gündönümü anları. Bunlar tanım gereği Güneş'in görünen
   ekliptik boylamının tam 0°, 90°, 180°, 270° olduğu anlardır. Yayımlanmış
   değerler (Espenak/NASA, astropixels.com) JPL efemerislerinden türetilir
   ve hiçbir astroloji yazılımına bağlı değildir - bu yüzden en güçlü çıpa.
2. Rodden AA dereceli referans harita (doğum belgesiyle kanıtlanmış saat).
3. Tamamen bağımsız bir yığınla (Skyfield + JPL DE440s) çapraz kontrol.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone

import pytest

from app.astro.chart import BirthInput, calculate_chart
from app.astro.constants import BODY_BY_KEY
from app.astro.ephemeris import get_provider
from app.astro.timeutil import julian_day_from_utc

# Kaynak: https://www.astropixels.com/ephemeris/soleq2001.html (Fred Espenak)
# (yıl, ay, gün, saat, dakika UTC, Güneş'in o andaki tam boylamı)
EQUINOX_SOLSTICE_ANCHORS = [
    (2001, 3, 20, 13, 31, 0.0),
    (2001, 6, 21, 7, 38, 90.0),
    (2005, 3, 20, 12, 34, 0.0),
    (2005, 6, 21, 6, 46, 90.0),
    (2010, 3, 20, 17, 32, 0.0),
    (2010, 6, 21, 11, 28, 90.0),
    (2015, 3, 20, 22, 45, 0.0),
    (2015, 6, 21, 16, 38, 90.0),
    (2020, 3, 20, 3, 50, 0.0),
    (2020, 6, 20, 21, 43, 90.0),
]

# Yayımlanmış anlar dakikaya yuvarlıdır (±30 sn). Güneş saatte ~0.041°
# ilerlediğinden bu ±0.0004°'lik bir belirsizlik demektir. 0.002°'lik
# eşik bu yuvarlamayı rahatça kapsar ama gerçek bir hatayı yakalar.
EQUINOX_TOLERANCE_DEG = 0.002


@pytest.mark.parametrize("year,month,day,hour,minute,expected", EQUINOX_SOLSTICE_ANCHORS)
def test_ekinoks_ve_gundonumlerinde_gunes_tam_konumda(
    year, month, day, hour, minute, expected
):
    when = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    jd = julian_day_from_utc(when)
    longitude = get_provider().position(jd, BODY_BY_KEY["Sun"]).longitude

    # 0° civarında 359.99 ile 0.01 arasındaki sarmayı hesaba kat.
    delta = (longitude - expected + 180.0) % 360.0 - 180.0
    assert abs(delta) < EQUINOX_TOLERANCE_DEG, (
        f"{when:%Y-%m-%d %H:%M} UTC'de Güneş {expected}° olmalıydı, "
        f"{longitude:.5f}° hesaplandı (sapma {delta * 60:.2f} açı dakikası)"
    )


# --------------------------------------------------------------------------
# Referans harita: Albert Einstein, 14 Mart 1879 11:30, Ulm (48°24'K, 10°00'D)
# Rodden AA - doğum belgesine dayanır. Beklenen değerler astro.com
# Astro-Databank yayınından alınmıştır.
# --------------------------------------------------------------------------

EINSTEIN = BirthInput(
    birth_date=date(1879, 3, 14),
    birth_time=time(11, 30),
    latitude=48.3984,
    longitude=9.9916,
    place_name="Ulm, Almanya",
    name="Albert Einstein",
)

# (gök cismi, beklenen burç, burç içi derece, gerileme)
EINSTEIN_REFERANS = [
    ("Sun", "Balık", 23.50, False),
    ("Mercury", "Koç", 3.12, False),
    ("Venus", "Koç", 16.97, False),
    ("Mars", "Oğlak", 26.90, False),
    ("Jupiter", "Kova", 27.48, False),
    ("Saturn", "Koç", 4.18, False),
    ("Uranus", "Başak", 1.28, True),
    ("Neptune", "Boğa", 7.87, False),
    ("Pluto", "Boğa", 24.73, False),
]

# Yavaş gezegenlerde yayımlanmış değer açı dakikasına yuvarlıdır; 0.05°
# (3 açı dakikası) eşiği yuvarlamayı ve saniye mertebesindeki zaman
# belirsizliğini kapsar.
REFERANS_TOLERANS_DEG = 0.05


@pytest.mark.parametrize("key,burc,derece,gerileme", EINSTEIN_REFERANS)
def test_referans_harita_gezegen_konumlari(key, burc, derece, gerileme):
    chart = calculate_chart(EINSTEIN)
    body = chart.body(key)
    assert body is not None
    assert body.sign_name_tr == burc, f"{key} burcu {burc} olmalıydı"
    assert body.degree_in_sign == pytest.approx(derece, abs=REFERANS_TOLERANS_DEG)
    assert body.is_retrograde is gerileme


def test_referans_haritada_ay_ve_yukselen():
    # Ay saatte ~0.55° ilerler ve Yükselen ~15°; ikisi de doğum saatinin
    # dakika hassasiyetine duyarlıdır. "11:30" zaten yuvarlanmış bir kayıt
    # olduğundan burç düzeyinde doğrulamak dürüst olanıdır.
    chart = calculate_chart(EINSTEIN)
    assert chart.moon_sign_tr == "Yay"
    assert chart.rising_sign_tr == "Yengeç"
    assert chart.body("Moon").degree_in_sign == pytest.approx(14.5, abs=0.5)


def test_referans_haritada_yerel_ortalama_saat_kullanildi():
    chart = calculate_chart(EINSTEIN)
    assert chart.instant.time_standard == "lmt"


# --------------------------------------------------------------------------
# Bağımsız yığınla çapraz kontrol
# --------------------------------------------------------------------------

CROSSCHECK_INSTANTS = [
    datetime(1879, 3, 14, 10, 50, 2, tzinfo=timezone.utc),
    datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc),
    datetime(2003, 7, 3, 6, 0, tzinfo=timezone.utc),
    datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc),
]

CROSSCHECK_TOLERANCE_DEG = 1.0 / 3600.0  # 1 açı saniyesi


@pytest.mark.slow
@pytest.mark.parametrize("when", CROSSCHECK_INSTANTS)
def test_skyfield_ile_capraz_kontrol(when):
    skyfield = pytest.importorskip("skyfield")
    import os

    from skyfield.api import load, load_file
    from skyfield.framelib import ecliptic_frame

    kernel = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "jpl", "de440s.bsp",
    )
    if not os.path.isfile(kernel):
        pytest.skip("JPL DE440s çekirdeği indirilmemiş")

    targets = {
        "Sun": "sun", "Moon": "moon", "Mercury": "mercury barycenter",
        "Venus": "venus barycenter", "Mars": "mars barycenter",
        "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
        "Uranus": "uranus barycenter", "Neptune": "neptune barycenter",
        "Pluto": "pluto barycenter",
    }

    ts = load.timescale()
    eph = load_file(kernel)
    jd = julian_day_from_utc(when)
    # Anı UT1 olarak veriyoruz ki her iki kütüphane de kendi ΔT modelini
    # uygulasın; `from_datetime` 1972 öncesinde ~45 sn hata verir.
    t = ts.ut1_jd(jd)
    earth = eph["earth"]
    provider = get_provider()

    for key, target in targets.items():
        _, lon, _ = earth.at(t).observe(eph[target]).apparent().frame_latlon(
            ecliptic_frame
        )
        swiss = provider.position(jd, BODY_BY_KEY[key]).longitude
        delta = abs((swiss - lon.degrees % 360.0 + 180.0) % 360.0 - 180.0)
        assert delta < CROSSCHECK_TOLERANCE_DEG, (
            f"{key} @ {when}: SwissEph {swiss:.6f}° vs Skyfield "
            f"{lon.degrees % 360.0:.6f}° -> {delta * 3600:.3f} açı saniyesi fark"
        )
