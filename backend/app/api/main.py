"""FastAPI uygulaması.

Ağır işler (efemeris, LLM, TTS) burada orkestre edilir; istemci hiçbir
API anahtarı taşımaz.
"""
from __future__ import annotations

import base64
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
from ..tts.base import TTSError
from ..tts.factory import build_provider
from ..tts.pricing import CHARS_PER_SECOND, compare_all
from ..tts.providers import synthesize
from .schemas import (
    DogumGirdisi,
    HaritaYaniti,
    HikayeYaniti,
    MaliyetTahminiYaniti,
    SaglikYaniti,
    SeslendirmeIstegi,
    SeslendirmeYaniti,
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
        tts_yapilandirildi=settings.tts_available,
        tts_saglayici=settings.tts_provider,
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


@app.post("/api/seslendir", response_model=SeslendirmeYaniti, tags=["ses"])
def seslendir(istek: SeslendirmeIstegi) -> SeslendirmeYaniti:
    """Metni sese çevirir.

    Ses, base64 olarak JSON içinde döner. Bir hikâye yaklaşık 10 dakikalık
    ses ediyor; kalıcı depolama (S3/R2) devreye girene kadar bu yeterli,
    ama dosya büyüdükçe akış tabanlı bir uca geçmek gerekecek.
    """
    settings = get_settings()
    try:
        provider = build_provider(settings)
        sonuc = synthesize(provider, istek.metin, voice=getattr(
            provider, "voice_name", getattr(provider, "voice_id", "varsayilan")))
    except TTSError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return SeslendirmeYaniti(
        ses_base64=base64.b64encode(sonuc.audio).decode("ascii"),
        mime_turu=sonuc.mime_type,
        saglayici=sonuc.provider,
        ses_karakteri=sonuc.voice,
        karakter_sayisi=sonuc.characters,
        parca_sayisi=sonuc.chunk_count,
        tahmini_sure_saniye=round(sonuc.estimated_seconds, 1),
        maliyet_usd=sonuc.cost_usd,
        uyarilar=sonuc.warnings,
    )


@app.get("/api/ses-maliyeti", response_model=MaliyetTahminiYaniti, tags=["ses"])
def ses_maliyeti(karakter: int) -> MaliyetTahminiYaniti:
    """Verilen uzunluk için TTS sağlayıcılarının maliyetini karşılaştırır.

    Hiçbir API anahtarı gerektirmez; sağlayıcı seçimi hesap açmadan
    değerlendirilebilsin diye ayrı bir uç olarak duruyor.
    """
    if karakter <= 0:
        raise HTTPException(status_code=422, detail="karakter pozitif olmalı")
    return MaliyetTahminiYaniti(
        karakter_sayisi=karakter,
        tahmini_sure_dakika=round(karakter / CHARS_PER_SECOND / 60.0, 2),
        saglayicilar=[
            {
                "saglayici": e.provider,
                "maliyet_usd": round(e.usd, 4),
                "dakika": round(e.estimated_minutes, 2),
            }
            for e in compare_all(karakter)
        ],
    )
