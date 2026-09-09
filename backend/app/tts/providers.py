"""Somut TTS sağlayıcıları: ElevenLabs ve Google Cloud Text-to-Speech."""
from __future__ import annotations

import base64
import os
from typing import Optional

import httpx

from .base import SynthesisResult, TTSError, TTSProvider, synthesize_long_text
from .pricing import estimate

# --------------------------------------------------------------------------
# ElevenLabs
# --------------------------------------------------------------------------

ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

# Türkçe destekleyen modeller. Flash daha ucuz ve hızlı; Multilingual v2
# duygusal tonlamada daha iyi. Uzun anlatım için ikisi de dinlenmeli.
ELEVENLABS_MODELS = {
    "eleven_multilingual_v2": "elevenlabs_multilingual_v2",
    "eleven_flash_v2_5": "elevenlabs_flash_v2_5",
}


class ElevenLabsProvider:
    name = "elevenlabs"
    max_chars_per_request = 4500

    def __init__(
        self,
        voice_id: str,
        api_key: Optional[str] = None,
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise TTSError(
                "ELEVENLABS_API_KEY ayarlı değil. Ortam değişkenini tanımlayın "
                "veya api_key parametresini geçin."
            )
        if model_id not in ELEVENLABS_MODELS:
            raise TTSError(
                f"Bilinmeyen model: {model_id}. "
                f"Seçenekler: {sorted(ELEVENLABS_MODELS)}"
            )
        self.voice_id = voice_id
        self.model_id = model_id
        self.output_format = output_format
        self.timeout = timeout

    @property
    def pricing_key(self) -> str:
        return ELEVENLABS_MODELS[self.model_id]

    def synthesize_chunk(self, text: str) -> bytes:
        response = httpx.post(
            ELEVENLABS_URL.format(voice_id=self.voice_id),
            params={"output_format": self.output_format},
            headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
            json={"text": text, "model_id": self.model_id},
            timeout=self.timeout,
        )
        if response.status_code != 200:
            raise TTSError(
                f"ElevenLabs hatası (HTTP {response.status_code}): "
                f"{response.text[:300]}"
            )
        return response.content


# --------------------------------------------------------------------------
# Google Cloud Text-to-Speech
# --------------------------------------------------------------------------

GOOGLE_TTS_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"

# Chirp 3 HD ses adları <yerel>-Chirp3-HD-<ses> kalıbındadır.
DEFAULT_GOOGLE_VOICE = "tr-TR-Chirp3-HD-Achernar"


class GoogleTTSProvider:
    name = "google"
    max_chars_per_request = 4500

    def __init__(
        self,
        voice_name: str = DEFAULT_GOOGLE_VOICE,
        api_key: Optional[str] = None,
        language_code: str = "tr-TR",
        speaking_rate: float = 1.0,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_TTS_API_KEY")
        if not self.api_key:
            raise TTSError(
                "GOOGLE_TTS_API_KEY ayarlı değil. Ortam değişkenini tanımlayın "
                "veya api_key parametresini geçin."
            )
        self.voice_name = voice_name
        self.language_code = language_code
        self.speaking_rate = speaking_rate
        self.timeout = timeout

    @property
    def pricing_key(self) -> str:
        return "google_chirp3_hd" if "Chirp3" in self.voice_name else "google_standard"

    def synthesize_chunk(self, text: str) -> bytes:
        response = httpx.post(
            GOOGLE_TTS_URL,
            params={"key": self.api_key},
            json={
                "input": {"text": text},
                "voice": {
                    "languageCode": self.language_code,
                    "name": self.voice_name,
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": self.speaking_rate,
                },
            },
            timeout=self.timeout,
        )
        if response.status_code != 200:
            raise TTSError(
                f"Google TTS hatası (HTTP {response.status_code}): "
                f"{response.text[:300]}"
            )
        payload = response.json()
        if "audioContent" not in payload:
            raise TTSError("Google TTS yanıtında ses verisi yok.")
        return base64.b64decode(payload["audioContent"])


# --------------------------------------------------------------------------

def synthesize(provider, text: str, voice: str) -> SynthesisResult:
    """Sağlayıcıyla uzun metni seslendirir ve maliyeti hesaba katar."""
    maliyet = estimate(len(text), provider.pricing_key).usd
    return synthesize_long_text(
        provider=provider, text=text, voice=voice, cost_usd=maliyet
    )
