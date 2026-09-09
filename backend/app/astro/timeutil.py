"""Yerel doğum anını UTC'ye ve Julian Day'e çeviren katman.

Hesaplama doğruluğunun en sık kırıldığı yer burasıdır: doğum tarihinde
geçerli olan saat dilimi ve yaz saati (DST) kuralı, bugünkü kuralla aynı
olmak zorunda değildir. Örnek: Türkiye 2016 Eylül'üne kadar yaz saati
uyguluyordu, o tarihten sonra kalıcı UTC+3'e geçti. IANA tz veritabanı
(zoneinfo) tarihsel kuralları içerir; bu yüzden sabit ofset yerine
her zaman zone adı üzerinden çeviri yapıyoruz.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

import swisseph as swe
from timezonefinder import TimezoneFinder

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9
    from backports.zoneinfo import ZoneInfo  # type: ignore

# TimezoneFinder örneği pahalı (veri dosyalarını belleğe alır) -> tekil tut.
_tf: Optional[TimezoneFinder] = None


def _finder() -> TimezoneFinder:
    global _tf
    if _tf is None:
        _tf = TimezoneFinder()
    return _tf


class TimeResolutionError(ValueError):
    """Saat dilimi çözülemediğinde veya belirsiz/olmayan yerel saatte atılır."""


@dataclass(frozen=True)
class ResolvedInstant:
    """Bir doğum anının hesaplamaya hazır tüm zaman gösterimleri."""

    local_naive: datetime      # kullanıcının girdiği yerel saat (tz bilgisi yok)
    timezone_name: str         # IANA zone adı, örn. "Europe/Istanbul"
    utc_offset_hours: float    # doğum anında geçerli olan ofset (DST dahil)
    is_dst: bool               # o anda yaz saati uygulanıyor muydu
    utc: datetime              # UTC karşılığı
    julian_day_ut: float       # Swiss Ephemeris'in beklediği JD (Universal Time)
    time_standard: str         # "zone" (standart saat) | "lmt" (yerel ortalama saat)
    note: Optional[str] = None # çeviriyle ilgili kullanıcıya iletilecek açıklama


def timezone_for_coordinates(latitude: float, longitude: float) -> str:
    """Enlem/boylamdan IANA saat dilimi adını bulur."""
    name = _finder().timezone_at(lat=latitude, lng=longitude)
    if name is None:
        # Okyanus gibi kara dışı noktalarda en yakın zone'a düşer.
        name = _finder().closest_timezone_at(lat=latitude, lng=longitude)
    if name is None:
        raise TimeResolutionError(
            f"Saat dilimi çözülemedi (lat={latitude}, lon={longitude})"
        )
    return name


def resolve_instant(
    birth_date: date,
    birth_time: time,
    latitude: float,
    longitude: float,
    timezone_name: Optional[str] = None,
) -> ResolvedInstant:
    """Yerel doğum anını UTC ve Julian Day'e çevirir.

    `timezone_name` verilmezse koordinatlardan bulunur. DST geçişlerinde
    oluşan belirsiz (saat iki kez yaşanır) ve olmayan (saat hiç yaşanmaz)
    yerel saatler açıkça hata olarak bildirilir; sessizce yanlış bir ana
    kaymaktansa kullanıcıya sormak doğrudur.
    """
    tz_name = timezone_name or timezone_for_coordinates(latitude, longitude)
    tz = ZoneInfo(tz_name)

    naive = datetime.combine(birth_date, birth_time)
    aware = naive.replace(tzinfo=tz)

    # DST geçişlerinde iki ayrı patoloji var ve ikisi de fold=0/fold=1
    # ofsetlerini farklılaştırır; bu yüzden önce hangisi olduğunu ayırmak
    # gerekir. Saat ileri alınırken atlanan aralık ("boşluk") UTC'ye gidip
    # geri dönüldüğünde başka bir yerel saate düşer - ayırt edici sınav bu.
    # Geri alınırken tekrarlanan aralık ("belirsizlik") ise gidiş-dönüşü
    # geçer ama iki farklı UTC anına karşılık gelir.
    utc = aware.astimezone(timezone.utc)
    if utc.astimezone(tz).replace(tzinfo=None) != naive:
        raise TimeResolutionError(
            f"{naive} yerel saati {tz_name} bölgesinde hiç yaşanmadı "
            "(yaz saati başlangıcında atlanan saat). Doğum saatini kontrol edin."
        )

    if aware.replace(fold=0).utcoffset() != aware.replace(fold=1).utcoffset():
        raise TimeResolutionError(
            f"{naive} yerel saati {tz_name} bölgesinde iki kez yaşandı "
            "(yaz saati bitişi). Hangi saatin kastedildiği belirsiz."
        )

    offset = aware.utcoffset()
    assert offset is not None  # zoneinfo her zaman ofset döndürür
    offset_hours = offset.total_seconds() / 3600.0
    dst = aware.dst()
    is_dst = bool(dst) and dst.total_seconds() != 0

    # Standart saat dilimlerinin benimsenmesinden önceki doğumlar:
    # tz veritabanı bu dönem için bölgenin REFERANS ŞEHRİNİN yerel ortalama
    # saatini verir (örn. 1893 öncesi Almanya için Berlin'in +0:53:28'i).
    # Doğum yeri o şehir değilse bu ofset yanlıştır - Ulm için 13.5 dakika
    # sapar, ki bu Yükselen'de ~3.4 derecelik hataya karşılık gelir.
    # Astrolojik yerleşik kural: bu dönemde doğum boylamından türetilen
    # gerçek yerel ortalama saat kullanılır.
    note: Optional[str] = None
    time_standard = "zone"
    if aware.tzname() == "LMT":
        time_standard = "lmt"
        offset_hours = local_mean_time_offset_hours(longitude)
        is_dst = False
        utc = naive.replace(tzinfo=timezone.utc) - _hours_to_timedelta(offset_hours)
        note = (
            f"{birth_date.isoformat()} tarihinde {tz_name} bölgesi henüz standart "
            "saat dilimine geçmemişti; doğum boylamından hesaplanan yerel "
            f"ortalama saat (UTC{offset_hours:+.4f} sa) kullanıldı."
        )

    return ResolvedInstant(
        local_naive=naive,
        timezone_name=tz_name,
        utc_offset_hours=offset_hours,
        is_dst=is_dst,
        utc=utc,
        julian_day_ut=julian_day_from_utc(utc),
        time_standard=time_standard,
        note=note,
    )


def _hours_to_timedelta(hours: float) -> timedelta:
    return timedelta(seconds=round(hours * 3600.0))


def local_mean_time_offset_hours(longitude: float) -> float:
    """Boylamdan yerel ortalama saat (LMT) ofseti: her 15° = 1 saat."""
    return longitude / 15.0


def julian_day_from_utc(utc_dt: datetime) -> float:
    """UTC datetime -> Julian Day (Universal Time)."""
    fractional_hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + (utc_dt.second + utc_dt.microsecond / 1e6) / 3600.0
    )
    return swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day, fractional_hour, swe.GREG_CAL
    )
