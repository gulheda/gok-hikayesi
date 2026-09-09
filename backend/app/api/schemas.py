"""API istek/yanıt şemaları."""
from __future__ import annotations

from datetime import date, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from ..astro.constants import HOUSE_SYSTEMS


class DogumGirdisi(BaseModel):
    """Kullanıcının girdiği doğum bilgisi."""

    ad: Optional[str] = Field(None, max_length=80, description="Hikâyede geçecek ad")
    tarih: date = Field(..., description="Doğum tarihi")
    saat: Optional[time] = Field(
        None,
        description=(
            "Yerel doğum saati. Bilinmiyorsa boş bırakın; bu durumda "
            "Yükselen ve ev yerleşimleri hesaplanmaz."
        ),
    )
    yer: str = Field(..., min_length=2, max_length=120, description="Doğum yeri")
    ev_sistemi: str = Field("placidus", description="Ev sistemi anahtarı")

    @field_validator("ev_sistemi")
    @classmethod
    def _ev_sistemi_gecerli(cls, v: str) -> str:
        if v not in HOUSE_SYSTEMS:
            raise ValueError(
                f"Geçersiz ev sistemi. Seçenekler: {', '.join(sorted(HOUSE_SYSTEMS))}"
            )
        return v

    @field_validator("tarih")
    @classmethod
    def _tarih_efemeris_araliginda(cls, v: date) -> date:
        # İndirilen efemeris dosyaları 1800-2399 aralığını kapsıyor.
        if not (1800 <= v.year <= 2399):
            raise ValueError(
                "Doğum tarihi 1800-2399 aralığında olmalı (efemeris veri sınırı)."
            )
        return v


class YerBilgisi(BaseModel):
    sorgu: str
    cozumlenen_ad: str
    enlem: float
    boylam: float
    kaynak: str


class HaritaYaniti(BaseModel):
    yer: YerBilgisi
    harita: Dict[str, Any]


class HikayeYaniti(BaseModel):
    yer: YerBilgisi
    harita: Dict[str, Any]
    baslik: str
    metin: str
    olgusal_panel: str
    ton: str
    yas: int
    model: str
    prompt_surumu: str
    kelime_sayisi: int
    karakter_sayisi: int
    girdi_token: int
    cikti_token: int
    maliyet_usd: Optional[float]


class SeslendirmeIstegi(BaseModel):
    metin: str = Field(..., min_length=1, max_length=40000)


class SeslendirmeYaniti(BaseModel):
    ses_base64: str
    mime_turu: str
    saglayici: str
    ses_karakteri: str
    karakter_sayisi: int
    parca_sayisi: int
    tahmini_sure_saniye: float
    maliyet_usd: Optional[float]
    uyarilar: List[str]


class MaliyetTahminiYaniti(BaseModel):
    karakter_sayisi: int
    tahmini_sure_dakika: float
    saglayicilar: List[Dict[str, Any]]


class HataYaniti(BaseModel):
    hata: str
    detay: Optional[str] = None


class SaglikYaniti(BaseModel):
    durum: str
    efemeris_modu: str
    efemeris_dosyalari_var: bool
    llm_yapilandirildi: bool
    tts_yapilandirildi: bool
    tts_saglayici: str
    desteklenen_ev_sistemleri: List[str]
    gunluk_tavan: Dict[str, Any]
