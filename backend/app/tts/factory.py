"""Ayarlardan yapılandırılmış TTS sağlayıcısı kurar."""
from __future__ import annotations

from ..config import Settings
from .base import TTSError
from .providers import ElevenLabsProvider, GoogleTTSProvider


def build_provider(settings: Settings):
    if settings.tts_provider == "elevenlabs":
        if not settings.elevenlabs_voice_id:
            raise TTSError("ELEVENLABS_VOICE_ID ayarlı değil.")
        return ElevenLabsProvider(
            voice_id=settings.elevenlabs_voice_id,
            api_key=settings.elevenlabs_api_key,
        )
    if settings.tts_provider == "google":
        return GoogleTTSProvider(
            voice_name=settings.google_tts_voice,
            api_key=settings.google_tts_api_key,
        )
    raise TTSError(
        f"Bilinmeyen TTS sağlayıcı: {settings.tts_provider}. "
        "TTS_PROVIDER 'google' veya 'elevenlabs' olmalı."
    )
