"""Ev sistemi hesaplaması: Yükselen (ASC), Tepe Noktası (MC) ve ev başlangıçları.

ÖNEMLİ ÜRÜN KURALI: Ev hesabı doğum saatine aşırı duyarlıdır - Yükselen
yaklaşık her 4 dakikada 1 derece ilerler, yani 2 saatlik bir belirsizlik
Yükselen burcunu tamamen değiştirir. Doğum saati bilinmiyorsa ev verisi
üretmiyoruz; uydurma bir "öğlen 12:00" varsayımıyla ev üretip bunu
hikâyede gerçekmiş gibi kullanmak, ürünün "gerçek astronomik veri"
iddiasını çürütür. Bkz. `HouseResult.available`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import swisseph as swe

from .constants import (
    DEFAULT_HOUSE_SYSTEM,
    HOUSE_SYSTEMS,
    HOUSE_THEMES_TR,
    PLACIDUS_LATITUDE_LIMIT,
    SIGN_NAMES_TR,
    sign_index,
)


@dataclass(frozen=True)
class House:
    number: int          # 1-12
    cusp_longitude: float
    sign_index: int
    sign_name_tr: str
    degree_in_sign: float
    theme_tr: str


@dataclass(frozen=True)
class HouseResult:
    available: bool                  # doğum saati bilinmiyorsa False
    system_key: str
    system_name: str
    houses: List[House]
    ascendant: Optional[float]       # Yükselen, ekliptik boylam
    midheaven: Optional[float]       # MC
    vertex: Optional[float]
    fallback_reason: Optional[str] = None   # sistem değiştirildiyse sebebi
    unavailable_reason: Optional[str] = None

    @property
    def ascendant_sign_tr(self) -> Optional[str]:
        if self.ascendant is None:
            return None
        return SIGN_NAMES_TR[sign_index(self.ascendant)]

    @property
    def midheaven_sign_tr(self) -> Optional[str]:
        if self.midheaven is None:
            return None
        return SIGN_NAMES_TR[sign_index(self.midheaven)]


def unavailable(reason: str, system_key: str = DEFAULT_HOUSE_SYSTEM) -> HouseResult:
    """Doğum saati bilinmediğinde döndürülen boş ev sonucu."""
    return HouseResult(
        available=False,
        system_key=system_key,
        system_name=HOUSE_SYSTEMS.get(system_key, (b"P", system_key))[1],
        houses=[],
        ascendant=None,
        midheaven=None,
        vertex=None,
        unavailable_reason=reason,
    )


def calculate_houses(
    julian_day_ut: float,
    latitude: float,
    longitude: float,
    system_key: str = DEFAULT_HOUSE_SYSTEM,
) -> HouseResult:
    """Ev başlangıçlarını, Yükselen ve MC'yi hesaplar.

    Placidus kutup dairelerine yakın enlemlerde tanımsızlaşır; bu durumda
    sessizce yanlış sonuç vermek yerine Whole Sign'a düşer ve sebebi
    `fallback_reason` alanında bildirir.
    """
    if system_key not in HOUSE_SYSTEMS:
        raise ValueError(
            f"Bilinmeyen ev sistemi: {system_key}. "
            f"Geçerli seçenekler: {sorted(HOUSE_SYSTEMS)}"
        )

    fallback_reason: Optional[str] = None
    effective_key = system_key
    if system_key in ("placidus", "koch") and abs(latitude) > PLACIDUS_LATITUDE_LIMIT:
        fallback_reason = (
            f"{HOUSE_SYSTEMS[system_key][1]} sistemi {PLACIDUS_LATITUDE_LIMIT}° "
            f"enlemin ötesinde tanımsızdır (doğum enlemi {latitude:.2f}°); "
            "Whole Sign sistemine geçildi."
        )
        effective_key = "whole_sign"

    hsys_code, system_name = HOUSE_SYSTEMS[effective_key]
    cusps, ascmc = swe.houses(julian_day_ut, latitude, longitude, hsys_code)

    # swe.houses 12 elemanlı cusp dizisi döndürür (1. ev ilk sırada).
    house_list: List[House] = []
    for i, cusp in enumerate(cusps[:12], start=1):
        lon = cusp % 360.0
        idx = sign_index(lon)
        house_list.append(
            House(
                number=i,
                cusp_longitude=lon,
                sign_index=idx,
                sign_name_tr=SIGN_NAMES_TR[idx],
                degree_in_sign=lon % 30.0,
                theme_tr=HOUSE_THEMES_TR[i],
            )
        )

    return HouseResult(
        available=True,
        system_key=effective_key,
        system_name=system_name,
        houses=house_list,
        ascendant=ascmc[0] % 360.0,
        midheaven=ascmc[1] % 360.0,
        vertex=ascmc[3] % 360.0,
        fallback_reason=fallback_reason,
    )


def house_of_longitude(longitude: float, result: HouseResult) -> Optional[int]:
    """Bir ekliptik boylamın hangi eve düştüğünü bulur.

    Evler eşit genişlikte değildir ve 360°'yi sarar; bu yüzden her evi
    kendi başlangıcından bir sonrakine kadar uzanan yay olarak ölçüyoruz.
    """
    if not result.available or not result.houses:
        return None

    lon = longitude % 360.0
    for i, house in enumerate(result.houses):
        start = house.cusp_longitude
        end = result.houses[(i + 1) % 12].cusp_longitude
        span = (end - start) % 360.0
        offset = (lon - start) % 360.0
        if offset < span:
            return house.number
    return None  # pragma: no cover - evler 360°'yi tam kaplar
