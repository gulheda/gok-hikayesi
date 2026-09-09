"""FastAPI uygulaması.

Ağır işler (efemeris, LLM, TTS) burada orkestre edilir; istemci hiçbir
API anahtarı taşımaz.
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ..astro.chart import BirthInput, calculate_chart
from ..astro.constants import HOUSE_SYSTEMS
from ..astro.ephemeris import get_provider
from ..astro.timeutil import TimeResolutionError
from ..config import get_settings
from ..geo.geocode import GeocodingError, geocode
from ..story.brief import olgusal_panel
from ..story.generator import StoryGenerationError, generate_story
from .schemas import (
    DogumGirdisi,
    HaritaYaniti,
    HikayeYaniti,
    SaglikYaniti,
    YerBilgisi,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Doğum Haritası Hikâye API",
    version="0.1.0",
    description=(
        "Gerçek astronomik hesaplamayla doğum haritası üretir ve bu haritayı "
        "kişiselleştirilmiş bir hikâyeye dönüştürür. Gezegen konumları "
        "ölçümdür; hikâye kurgudur."
    ),
)

# MVP'de istemci yalnızca iOS uygulaması; yayına çıkarken bu liste daraltılmalı.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _harita_kur(girdi: DogumGirdisi):
    """Girdiyi coğrafi olarak çözer ve haritayı hesaplar."""
    try:
        yer = geocode(girdi.yer)
    except GeocodingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    birth = BirthInput(
        birth_date=girdi.tarih,
        birth_time=girdi.saat,
        latitude=yer.latitude,
        longitude=yer.longitude,
        place_name=yer.display_name,
        name=girdi.ad,
        house_system=girdi.ev_sistemi,
    )

    try:
        chart = calculate_chart(birth)
    except TimeResolutionError as exc:
        # Yaz saati geçişindeki belirsiz/olmayan saatler kullanıcı hatasıdır,
        # sunucu hatası değil.
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    yer_bilgisi = YerBilgisi(
        sorgu=yer.query,
        cozumlenen_ad=yer.display_name,
        enlem=yer.latitude,
        boylam=yer.longitude,
        kaynak=yer.source,
    )
    return yer_bilgisi, chart


@app.get("/saglik", response_model=SaglikYaniti, tags=["sistem"])
def saglik() -> SaglikYaniti:
    provider = get_provider()
    settings = get_settings()
    return SaglikYaniti(
        durum="calisiyor",
        efemeris_modu=provider.mode,
        efemeris_dosyalari_var=provider.has_data_files,
        llm_yapilandirildi=settings.llm_available,
        desteklenen_ev_sistemleri=sorted(HOUSE_SYSTEMS),
    )


@app.post("/api/harita", response_model=HaritaYaniti, tags=["hesaplama"])
def harita_hesapla(girdi: DogumGirdisi) -> HaritaYaniti:
    """Yalnızca astronomik hesaplama yapar; LLM çağrısı içermez."""
    yer, chart = _harita_kur(girdi)
    return HaritaYaniti(yer=yer, harita=chart.to_dict())


@app.post("/api/hikaye", response_model=HikayeYaniti, tags=["hikaye"])
def hikaye_uret(girdi: DogumGirdisi) -> HikayeYaniti:
    """Haritayı hesaplar ve hikâyeye dönüştürür."""
    yer, chart = _harita_kur(girdi)

    try:
        story = generate_story(chart, name=girdi.ad)
    except StoryGenerationError as exc:
        logger.exception("Hikâye üretimi başarısız")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return HikayeYaniti(
        yer=yer,
        harita=chart.to_dict(),
        baslik=story.title,
        metin=story.body,
        olgusal_panel=story.factual_panel,
        ton=story.tone_key,
        yas=story.age,
        model=story.model,
        prompt_surumu=story.prompt_version,
        kelime_sayisi=story.word_count,
        karakter_sayisi=story.character_count,
        girdi_token=story.input_tokens,
        cikti_token=story.output_tokens,
        maliyet_usd=story.cost_usd,
    )
