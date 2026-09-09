"""Gök cisimleri arası açı (aspect) hesaplaması.

Açı, iki cismin ekliptik boylamları arasındaki fark belirli bir değere
(0°, 60°, 90°, 120°, 180°) tolerans dahilinde yaklaştığında oluşur.
Tolerans (orb) sabit değildir: Güneş ve Ay dahil olduğunda daha geniş
tutulur, çünkü klasik yorumda bu iki cisim daha güçlü kabul edilir.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .constants import ASPECT_TYPES, BODY_BY_KEY, AspectType
from .ephemeris import BodyPosition


@dataclass(frozen=True)
class Aspect:
    body_a: str              # gök cismi anahtarı
    body_b: str
    name_a_tr: str
    name_b_tr: str
    type_key: str            # "conjunction" | "sextile" | ...
    type_name_tr: str
    exact_angle: float       # açının tam değeri (0/60/90/120/180)
    actual_angle: float      # iki cisim arasındaki gerçek açısal mesafe
    orb: float               # tam açıdan sapma, derece
    max_orb: float           # bu çift için kullanılan tolerans
    nature: str              # "uyumlu" | "gergin" | "nötr"
    is_applying: bool        # açı sıkılaşıyor mu (yaklaşan) yoksa gevşiyor mu

    @property
    def strength(self) -> float:
        """0-1 arası güç: orb sıfıra yaklaştıkça açı güçlenir."""
        if self.max_orb <= 0:
            return 0.0
        return max(0.0, 1.0 - (self.orb / self.max_orb))


def angular_separation(lon_a: float, lon_b: float) -> float:
    """İki boylam arasındaki en kısa açısal mesafe (0-180)."""
    diff = abs(lon_a - lon_b) % 360.0
    return 360.0 - diff if diff > 180.0 else diff


def _max_orb(aspect: AspectType, key_a: str, key_b: str) -> float:
    body_a = BODY_BY_KEY.get(key_a)
    body_b = BODY_BY_KEY.get(key_b)
    involves_luminary = bool(
        (body_a and body_a.is_luminary) or (body_b and body_b.is_luminary)
    )
    return aspect.luminary_orb if involves_luminary else aspect.base_orb


def _is_applying(pos_a: BodyPosition, pos_b: BodyPosition, exact_angle: float) -> bool:
    """Açı yaklaşıyor mu: bir gün sonraki ayrımın bugünkünden küçük olması."""
    current = abs(angular_separation(pos_a.longitude, pos_b.longitude) - exact_angle)
    future = abs(
        angular_separation(
            pos_a.longitude + pos_a.speed_longitude,
            pos_b.longitude + pos_b.speed_longitude,
        )
        - exact_angle
    )
    return future < current


def find_aspects(
    positions: Dict[str, BodyPosition],
    body_keys: Optional[List[str]] = None,
    aspect_types: Optional[List[AspectType]] = None,
) -> List[Aspect]:
    """Verilen konumlar arasındaki tüm açıları güçten zayıfa sıralı döndürür."""
    keys = body_keys if body_keys is not None else list(positions.keys())
    types = aspect_types if aspect_types is not None else ASPECT_TYPES

    found: List[Aspect] = []
    for i, key_a in enumerate(keys):
        for key_b in keys[i + 1:]:
            pos_a, pos_b = positions[key_a], positions[key_b]
            separation = angular_separation(pos_a.longitude, pos_b.longitude)

            for aspect in types:
                orb = abs(separation - aspect.angle)
                max_orb = _max_orb(aspect, key_a, key_b)
                if orb > max_orb:
                    continue
                found.append(
                    Aspect(
                        body_a=key_a,
                        body_b=key_b,
                        name_a_tr=pos_a.name_tr,
                        name_b_tr=pos_b.name_tr,
                        type_key=aspect.key,
                        type_name_tr=aspect.name_tr,
                        exact_angle=aspect.angle,
                        actual_angle=separation,
                        orb=orb,
                        max_orb=max_orb,
                        nature=aspect.nature,
                        is_applying=_is_applying(pos_a, pos_b, aspect.angle),
                    )
                )
                break  # bir çift aynı anda birden fazla açı yapamaz

    found.sort(key=lambda a: a.strength, reverse=True)
    return found
