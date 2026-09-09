"""Uygulama ayarları. Sırlar ortam değişkenlerinden okunur, koda gömülmez."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Hikâye üretiminde kullanılan model. Anthropic fiyatlandırması
# (1M token başına, USD) maliyet raporlaması için burada tutulur.
MODEL_PRICING_USD = {
    "claude-opus-5": {"input": 5.00, "output": 25.00},
    "claude-sonnet-5": {"input": 2.00, "output": 10.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
}

DEFAULT_MODEL = "claude-opus-5"


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: Optional[str]
    story_model: str
    max_output_tokens: int
    tts_provider: str
    elevenlabs_api_key: Optional[str]
    elevenlabs_voice_id: Optional[str]
    google_tts_api_key: Optional[str]
    google_tts_voice: str

    @property
    def llm_available(self) -> bool:
        # Anahtar ortamda yoksa SDK `ant auth login` profilini de deneyebilir;
        # bu yüzden yokluğu kesin bir engel değil, yalnızca bir ipucu.
        return bool(self.anthropic_api_key)

    @property
    def tts_available(self) -> bool:
        if self.tts_provider == "elevenlabs":
            return bool(self.elevenlabs_api_key and self.elevenlabs_voice_id)
        if self.tts_provider == "google":
            return bool(self.google_tts_api_key)
        return False


def get_settings() -> Settings:
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        story_model=os.getenv("STORY_MODEL", DEFAULT_MODEL),
        max_output_tokens=int(os.getenv("STORY_MAX_TOKENS", "8000")),
        tts_provider=os.getenv("TTS_PROVIDER", "google"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        google_tts_api_key=os.getenv("GOOGLE_TTS_API_KEY"),
        google_tts_voice=os.getenv("GOOGLE_TTS_VOICE", "tr-TR-Chirp3-HD-Achernar"),
    )
