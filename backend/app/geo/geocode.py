"""Doğum yeri adını koordinata çeviren katman.

Sıra: önce çevrimdışı Türkiye il tablosu, bulunamazsa Nominatim
(OpenStreetMap). Nominatim ücretsizdir ama saniyede bir istek sınırı ve
tanımlayıcı bir User-Agent zorunluluğu vardır; bu kurallara uymayan
istemciler engellenir.
"""
from __future__ import annotations

import time as _time
import threading
from dataclasses import dataclass
from typing import Optional

import httpx

from . import places

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "dogum-haritasi-hikaye/0.1 (iletisim: kizilhangulheda@gmail.com)"
MIN_REQUEST_INTERVAL_SECONDS = 1.1  # Nominatim kullanım şartı

_rate_lock = threading.Lock()
_last_request_at = 0.0


class GeocodingError(RuntimeError):
    pass


@dataclass(frozen=True)
class Place:
    query: str            # kullanıcının yazdığı hâli
    display_name: str     # çözümlenmiş tam ad
    latitude: float
    longitude: float
    source: str           # "offline_tr" | "offline_yurtdisi" | "nominatim"


def _respect_rate_limit() -> None:
    global _last_request_at
    with _rate_lock:
        elapsed = _time.monotonic() - _last_request_at
        if elapsed < MIN_REQUEST_INTERVAL_SECONDS:
            _time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)
        _last_request_at = _time.monotonic()


def geocode(query: str, timeout: float = 10.0) -> Place:
    """Yer adını koordinata çevirir.

    Türkiye il adları ağa çıkılmadan çözülür; geri kalanı Nominatim'e gider.
    """
    if not query or not query.strip():
        raise GeocodingError("Doğum yeri boş olamaz.")

    # Kullanıcı "Denizli, Türkiye" gibi yazmış olabilir; ilk parça il adıdır.
    first_part = query.split(",")[0].strip()
    try:
        lat, lon = places.lookup(first_part)
        return Place(
            query=query,
            display_name=f"{first_part.strip()}, Türkiye",
            latitude=lat,
            longitude=lon,
            source="offline_tr",
        )
    except KeyError:
        pass

    try:
        lat, lon, sehir, ulke = places.lookup_yurtdisi(query)
        return Place(
            query=query,
            display_name=f"{sehir}, {ulke}",
            latitude=lat,
            longitude=lon,
            source="offline_yurtdisi",
        )
    except KeyError:
        pass

    return _geocode_nominatim(query, timeout)


def _geocode_nominatim(query: str, timeout: float) -> Place:
    _respect_rate_limit()
    try:
        response = httpx.get(
            NOMINATIM_URL,
            params={"q": query, "format": "jsonv2", "limit": 1, "accept-language": "tr"},
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )
        response.raise_for_status()
        results = response.json()
    except httpx.HTTPError as exc:
        raise GeocodingError(
            f"Yer arama servisine ulaşılamadı: {exc}"
        ) from exc

    if not results:
        raise GeocodingError(
            f"'{query}' için yer bulunamadı. Şehir ve ülke şeklinde yazmayı deneyin."
        )

    top = results[0]
    return Place(
        query=query,
        display_name=top.get("display_name", query),
        latitude=float(top["lat"]),
        longitude=float(top["lon"]),
        source="nominatim",
    )
