"""Efemeris (gök cismi konumu) katmanı.

Swiss Ephemeris'e doğrudan bağlanmak yerine dar bir arayüzün arkasına
alıyoruz. Sebep lisans: pyswisseph AGPL-3.0 altında; kapalı kaynak ticari
bir servis için Astrodienst'ten profesyonel lisans alınması gerekir
(bkz. docs/kararlar.md, madde 1). O karar ertelenebilir olsun diye sağlayıcı
değiştirilebilir tutuluyor - Skyfield tabanlı bir sağlayıcı aynı arayüzü
uygulayarak devreye girebilir.
"""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional

import swisseph as swe

from .constants import BODIES, BODY_BY_KEY, Body

# Efemeris veri dosyalarının (.se1) bulunduğu dizin
DEFAULT_EPHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "ephe",
)

_init_lock = threading.Lock()
_ephe_path_set: Optional[str] = None


@dataclass(frozen=True)
class BodyPosition:
    """Bir gök cisminin belirli bir andaki geosentrik ekliptik konumu."""

    key: str
    name_tr: str
    longitude: float        # ekliptik boylam, derece (0-360)
    latitude: float         # ekliptik enlem, derece
    distance_au: float      # Dünya'ya uzaklık, astronomi birimi
    speed_longitude: float  # boylamdaki günlük değişim, derece/gün
    is_retrograde: bool     # boylam hızı negatifse gerileme hareketi


class EphemerisError(RuntimeError):
    pass


class SwissEphemerisProvider:
    """pyswisseph tabanlı sağlayıcı.

    Veri dosyaları (sepl_18.se1 vb.) mevcutsa tam Swiss Ephemeris
    doğruluğu; yoksa kütüphane sessizce yerleşik Moshier modeline düşer.
    Bu fark astroloji toleransları içinde önemsizdir ama hangi modun
    kullanıldığını `mode` alanında açıkça raporluyoruz.
    """

    def __init__(self, ephe_path: Optional[str] = None) -> None:
        self.ephe_path = ephe_path or DEFAULT_EPHE_PATH
        self._ensure_initialised()

    def _ensure_initialised(self) -> None:
        global _ephe_path_set
        with _init_lock:
            if _ephe_path_set != self.ephe_path:
                swe.set_ephe_path(self.ephe_path)
                _ephe_path_set = self.ephe_path

    @property
    def has_data_files(self) -> bool:
        return os.path.isfile(os.path.join(self.ephe_path, "sepl_18.se1"))

    @property
    def mode(self) -> str:
        return "swiss_ephemeris_files" if self.has_data_files else "moshier_builtin"

    def position(self, julian_day_ut: float, body: Body) -> BodyPosition:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        try:
            values, ret_flag = swe.calc_ut(julian_day_ut, body.swe_id, flags)
        except swe.Error as exc:  # pragma: no cover - kütüphane hatası
            raise EphemerisError(f"{body.key} hesaplanamadı: {exc}") from exc

        longitude, latitude, distance, speed_long = values[0], values[1], values[2], values[3]
        return BodyPosition(
            key=body.key,
            name_tr=body.name_tr,
            longitude=longitude % 360.0,
            latitude=latitude,
            distance_au=distance,
            speed_longitude=speed_long,
            is_retrograde=speed_long < 0,
        )

    def positions(
        self, julian_day_ut: float, bodies: Optional[List[Body]] = None
    ) -> Dict[str, BodyPosition]:
        selected = bodies if bodies is not None else BODIES
        return {b.key: self.position(julian_day_ut, b) for b in selected}


def get_provider(ephe_path: Optional[str] = None) -> SwissEphemerisProvider:
    """Uygulamanın kullandığı varsayılan efemeris sağlayıcısı."""
    return SwissEphemerisProvider(ephe_path)


def body_from_key(key: str) -> Body:
    if key not in BODY_BY_KEY:
        raise KeyError(f"Bilinmeyen gök cismi: {key}")
    return BODY_BY_KEY[key]
