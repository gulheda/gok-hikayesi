"""Swiss Ephemeris çıktısını Skyfield + JPL DE440s ile çapraz doğrular.

Bu iki yığın tamamen bağımsız kod tabanlarıdır (Astrodienst'in C kütüphanesi
ve NASA/JPL'in SPK çekirdeğini okuyan saf Python). Aynı sonucu vermeleri,
hatanın tek bir kütüphanenin kendine özgü hatası olmadığını gösterir.

Kullanım:  .venv/bin/python backend/tools/crosscheck_skyfield.py
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from skyfield.api import load_file
from skyfield.framelib import ecliptic_frame
from skyfield.timelib import Timescale
from skyfield import api as sky_api

from app.astro.constants import BODIES
from app.astro.ephemeris import get_provider
from app.astro.timeutil import julian_day_from_utc

KERNEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "jpl", "de440s.bsp"
)

# Swiss Ephemeris anahtarı -> DE440s içindeki hedef adı.
# Merkür ve Venüs'te barycenter ile gövde pratikte aynıdır; dış gezegenlerde
# DE440s yalnızca barycenter içerir - uydu kütlelerinin yarattığı sapma
# ekliptik boylamda milisaniye mertebesindedir, astroloji için önemsizdir.
SKYFIELD_TARGETS: Dict[str, str] = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury barycenter",
    "Venus": "venus barycenter",
    "Mars": "mars barycenter",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}

TEST_INSTANTS: List[Tuple[str, datetime]] = [
    ("Einstein 1879", datetime(1879, 3, 14, 10, 50, 2, tzinfo=timezone.utc)),
    ("J2000 dönümü", datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
    ("2003 örneği", datetime(2003, 7, 3, 6, 0, 0, tzinfo=timezone.utc)),
    ("2026 güncel", datetime(2026, 9, 9, 12, 0, 0, tzinfo=timezone.utc)),
]

# Kabul eşiği: 1 açı saniyesi. Astroloji yorumu için gereken hassasiyet
# ~1 açı DAKİKASI olduğundan bu 60 kat daha sıkı bir sınırdır.
TOLERANCE_DEGREES = 1.0 / 3600.0


def skyfield_longitudes(ts: Timescale, eph, when: datetime) -> Dict[str, float]:
    # `ts.from_datetime` girdiyi UTC sayar ve 1972 öncesi için sabit bir
    # TAI-UTC ofseti uygular; bu tarihsel doğumlarda ~45 saniyelik hataya
    # yol açar (Ay'da ~26 açı saniyesi sapma). Doğrusu, anı UT1 olarak
    # verip ΔT dönüşümünü Skyfield'in kendi modeline bırakmaktır - böylece
    # iki kütüphane de kendi ΔT modelini kullanır ve karşılaştırma adil olur.
    t = ts.ut1_jd(julian_day_from_utc(when))
    earth = eph["earth"]
    out: Dict[str, float] = {}
    for key, target in SKYFIELD_TARGETS.items():
        astrometric = earth.at(t).observe(eph[target]).apparent()
        _, lon, _ = astrometric.frame_latlon(ecliptic_frame)
        out[key] = lon.degrees % 360.0
    return out


def main() -> int:
    if not os.path.isfile(KERNEL_PATH):
        print(f"HATA: JPL çekirdeği bulunamadı: {KERNEL_PATH}")
        return 2

    ts = sky_api.load.timescale()
    eph = load_file(KERNEL_PATH)
    provider = get_provider()
    print(f"Swiss Ephemeris modu: {provider.mode}")
    print(f"Tolerans: {TOLERANCE_DEGREES * 3600:.1f} açı saniyesi\n")

    worst = 0.0
    failures = 0
    for label, when in TEST_INSTANTS:
        jd = julian_day_from_utc(when)
        sky = skyfield_longitudes(ts, eph, when)
        print(f"--- {label}  ({when:%Y-%m-%d %H:%M} UTC) ---")
        header_diff = 'fark (as)'
        print(f"{'cisim':10s} {'SwissEph':>12s} {'Skyfield':>12s} {header_diff:>11s}")
        for body in BODIES:
            if body.key not in sky:
                continue
            swiss = provider.position(jd, body).longitude
            diff = abs(swiss - sky[body.key])
            if diff > 180.0:
                diff = 360.0 - diff
            arcsec = diff * 3600.0
            worst = max(worst, diff)
            flag = "" if diff <= TOLERANCE_DEGREES else "  <== ESIK ASILDI"
            if diff > TOLERANCE_DEGREES:
                failures += 1
            print(
                f"{body.name_tr:10s} {swiss:12.6f} {sky[body.key]:12.6f} "
                f"{arcsec:11.3f}{flag}"
            )
        print()

    print(f"En büyük sapma: {worst * 3600:.3f} açı saniyesi")
    if failures:
        print(f"SONUÇ: {failures} ölçüm eşiği aştı.")
        return 1
    print("SONUÇ: İki bağımsız efemeris uyumlu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
