"""Doğum haritası (natal chart) üretimi - hesaplama katmanının giriş noktası.

Girdi: doğum tarihi, saati (opsiyonel), yeri.
Çıktı: gezegen konumları, evler, açılar ve element/nitelik dengesini
içeren yapılandırılmış bir `NatalChart`. Bu nesne hikâye katmanına
olduğu gibi beslenir.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, time
from typing import Any, Dict, List, Optional

from .aspects import Aspect, find_aspects
from .constants import (
    BODIES,
    BODY_BY_KEY,
    CORE_BODY_KEYS,
    DEFAULT_HOUSE_SYSTEM,
    HOUSE_THEMES_TR,
    SIGN_NAMES_EN,
    SIGN_NAMES_TR,
    sign_element_tr,
    sign_index,
    sign_modality_tr,
)
from .ephemeris import BodyPosition, get_provider
from .houses import HouseResult, calculate_houses, house_of_longitude, unavailable
from .timeutil import ResolvedInstant, resolve_instant

# Doğum saati bilinmediğinde hesaplama için kullanılan varsayılan an.
# Bu SADECE gezegen konumlarını üretmek içindir; ev/Yükselen üretilmez.
ASSUMED_TIME_WHEN_UNKNOWN = time(12, 0)


@dataclass(frozen=True)
class BirthInput:
    """Kullanıcının girdiği ham doğum bilgisi."""

    birth_date: date
    latitude: float
    longitude: float
    place_name: str
    birth_time: Optional[time] = None    # None => saat bilinmiyor
    name: Optional[str] = None
    timezone_name: Optional[str] = None
    house_system: str = DEFAULT_HOUSE_SYSTEM

    @property
    def time_known(self) -> bool:
        return self.birth_time is not None


@dataclass(frozen=True)
class PlacedBody:
    """Bir gök cismi + burç/ev yerleşimi."""

    key: str
    name_tr: str
    longitude: float
    sign_index: int
    sign_name_tr: str
    sign_name_en: str
    degree_in_sign: float
    element_tr: str
    modality_tr: str
    house: Optional[int]         # doğum saati bilinmiyorsa None
    house_theme_tr: Optional[str]
    is_retrograde: bool
    speed_longitude: float
    latitude: float

    @property
    def display_position(self) -> str:
        deg = int(self.degree_in_sign)
        minute = int(round((self.degree_in_sign - deg) * 60))
        if minute == 60:
            deg, minute = deg + 1, 0
        suffix = " R" if self.is_retrograde else ""
        return f"{self.sign_name_tr} {deg}°{minute:02d}'{suffix}"


@dataclass
class ChartBalance:
    """Element ve nitelik dağılımı - hikâyenin genel tonunu belirler."""

    elements: Dict[str, int] = field(default_factory=dict)
    modalities: Dict[str, int] = field(default_factory=dict)

    @property
    def dominant_element(self) -> Optional[str]:
        return max(self.elements, key=self.elements.get) if self.elements else None

    @property
    def dominant_modality(self) -> Optional[str]:
        return max(self.modalities, key=self.modalities.get) if self.modalities else None

    @property
    def missing_elements(self) -> List[str]:
        return [e for e, n in self.elements.items() if n == 0]


@dataclass
class NatalChart:
    """Tam doğum haritası."""

    birth: BirthInput
    instant: ResolvedInstant
    bodies: List[PlacedBody]
    houses: HouseResult
    aspects: List[Aspect]
    balance: ChartBalance
    ephemeris_mode: str
    warnings: List[str] = field(default_factory=list)

    def body(self, key: str) -> Optional[PlacedBody]:
        return next((b for b in self.bodies if b.key == key), None)

    @property
    def sun_sign_tr(self) -> Optional[str]:
        b = self.body("Sun")
        return b.sign_name_tr if b else None

    @property
    def moon_sign_tr(self) -> Optional[str]:
        b = self.body("Moon")
        return b.sign_name_tr if b else None

    @property
    def rising_sign_tr(self) -> Optional[str]:
        return self.houses.ascendant_sign_tr

    def to_dict(self) -> Dict[str, Any]:
        """Hikâye katmanına ve API'ye verilecek JSON uyumlu sözlük."""
        return {
            "giris": {
                "ad": self.birth.name,
                "tarih": self.birth.birth_date.isoformat(),
                "saat": self.birth.birth_time.isoformat() if self.birth.birth_time else None,
                "saat_biliniyor": self.birth.time_known,
                "yer": self.birth.place_name,
                "enlem": round(self.birth.latitude, 6),
                "boylam": round(self.birth.longitude, 6),
            },
            "zaman": {
                "saat_dilimi": self.instant.timezone_name,
                "utc_ofset_saat": self.instant.utc_offset_hours,
                "yaz_saati": self.instant.is_dst,
                "utc": self.instant.utc.isoformat(),
                "julian_day": self.instant.julian_day_ut,
            },
            "gok_cisimleri": [
                {
                    "anahtar": b.key,
                    "ad": b.name_tr,
                    "boylam": round(b.longitude, 4),
                    "burc": b.sign_name_tr,
                    "burc_derece": round(b.degree_in_sign, 4),
                    "gosterim": b.display_position,
                    "element": b.element_tr,
                    "nitelik": b.modality_tr,
                    "ev": b.house,
                    "ev_temasi": b.house_theme_tr,
                    "gerileme": b.is_retrograde,
                }
                for b in self.bodies
            ],
            "evler": {
                "mevcut": self.houses.available,
                "sistem": self.houses.system_name,
                "yukselen": round(self.houses.ascendant, 4) if self.houses.ascendant else None,
                "yukselen_burc": self.houses.ascendant_sign_tr,
                "mc": round(self.houses.midheaven, 4) if self.houses.midheaven else None,
                "mc_burc": self.houses.midheaven_sign_tr,
                "yoklugu_sebebi": self.houses.unavailable_reason,
                "sistem_degisim_sebebi": self.houses.fallback_reason,
                "ev_listesi": [
                    {
                        "no": h.number,
                        "boylam": round(h.cusp_longitude, 4),
                        "burc": h.sign_name_tr,
                        "tema": h.theme_tr,
                    }
                    for h in self.houses.houses
                ],
            },
            "acilar": [
                {
                    "a": a.name_a_tr,
                    "b": a.name_b_tr,
                    "tur": a.type_name_tr,
                    "tur_anahtar": a.type_key,
                    "orb": round(a.orb, 3),
                    "guc": round(a.strength, 3),
                    "dogas": a.nature,
                    "yaklasan": a.is_applying,
                }
                for a in self.aspects
            ],
            "denge": {
                "elementler": self.balance.elements,
                "nitelikler": self.balance.modalities,
                "baskin_element": self.balance.dominant_element,
                "baskin_nitelik": self.balance.dominant_modality,
                "eksik_elementler": self.balance.missing_elements,
            },
            "meta": {
                "efemeris_modu": self.ephemeris_mode,
                "uyarilar": self.warnings,
            },
        }


def _compute_balance(bodies: List[PlacedBody]) -> ChartBalance:
    """Element/nitelik dengesini yalnızca çekirdek kadro üzerinden sayar."""
    elements = {"Ateş": 0, "Toprak": 0, "Hava": 0, "Su": 0}
    modalities = {"Öncü": 0, "Sabit": 0, "Değişken": 0}
    for b in bodies:
        if b.key not in CORE_BODY_KEYS:
            continue
        elements[b.element_tr] += 1
        modalities[b.modality_tr] += 1
    return ChartBalance(elements=elements, modalities=modalities)


def calculate_chart(birth: BirthInput) -> NatalChart:
    """Doğum bilgisinden tam natal haritayı üretir."""
    warnings: List[str] = []

    effective_time = birth.birth_time or ASSUMED_TIME_WHEN_UNKNOWN
    if not birth.time_known:
        warnings.append(
            "Doğum saati bilinmediği için gezegen konumları yerel saat 12:00 "
            "varsayımıyla hesaplandı. Yükselen burç ve ev yerleşimleri "
            "üretilmedi; bu veriler saat bilinmeden anlamlı olmaz. Ay burcu "
            "gün içinde değişebileceği için yaklaşık kabul edilmelidir."
        )

    instant = resolve_instant(
        birth_date=birth.birth_date,
        birth_time=effective_time,
        latitude=birth.latitude,
        longitude=birth.longitude,
        timezone_name=birth.timezone_name,
    )

    provider = get_provider()
    raw_positions: Dict[str, BodyPosition] = provider.positions(instant.julian_day_ut)

    if birth.time_known:
        houses = calculate_houses(
            instant.julian_day_ut, birth.latitude, birth.longitude, birth.house_system
        )
        if houses.fallback_reason:
            warnings.append(houses.fallback_reason)
    else:
        houses = unavailable(
            "Doğum saati bilinmiyor. Yükselen yaklaşık her 4 dakikada bir "
            "derece ilerlediği için saat olmadan ev sistemi hesaplanamaz.",
            birth.house_system,
        )

    placed: List[PlacedBody] = []
    for body in BODIES:
        pos = raw_positions[body.key]
        idx = sign_index(pos.longitude)
        house_no = house_of_longitude(pos.longitude, houses)
        placed.append(
            PlacedBody(
                key=body.key,
                name_tr=body.name_tr,
                longitude=pos.longitude,
                sign_index=idx,
                sign_name_tr=SIGN_NAMES_TR[idx],
                sign_name_en=SIGN_NAMES_EN[idx],
                degree_in_sign=pos.longitude % 30.0,
                element_tr=sign_element_tr(idx),
                modality_tr=sign_modality_tr(idx),
                house=house_no,
                house_theme_tr=HOUSE_THEMES_TR[house_no] if house_no else None,
                is_retrograde=pos.is_retrograde,
                speed_longitude=pos.speed_longitude,
                latitude=pos.latitude,
            )
        )

    aspects = find_aspects(raw_positions, CORE_BODY_KEYS)

    return NatalChart(
        birth=birth,
        instant=instant,
        bodies=placed,
        houses=houses,
        aspects=aspects,
        balance=_compute_balance(placed),
        ephemeris_mode=provider.mode,
        warnings=warnings,
    )
