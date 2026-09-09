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

# Ücretsiz katmanda ya da yerel çalışan sağlayıcılar. Bunlar için maliyet
# sıfır raporlanır; günlük harcama tavanı da doğal olarak devreye girmez.
UCRETSIZ_SAGLAYICILAR = {"gemini_ucretsiz", "openai_uyumlu"}

VARSAYILAN_MODELLER = {
    "anthropic": "claude-opus-5",
    # Gemini model adları zamanla değişiyor; kullanılabilir listeyi görmek için:
    #   curl "https://generativelanguage.googleapis.com/v1beta/models?key=ANAHTAR"
    "gemini": "gemini-3-flash",
    "openai_uyumlu": "llama3.1:8b",
}


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: Optional[str]
    llm_saglayici: str
    gemini_api_key: Optional[str]
    llm_temel_adres: Optional[str]
    llm_api_key: Optional[str]
    story_model: str
    max_output_tokens: int
    tts_provider: str
    elevenlabs_api_key: Optional[str]
    elevenlabs_voice_id: Optional[str]
    google_tts_api_key: Optional[str]
    google_tts_voice: str
    # Sınırlama ayarları
    hikaye_saatlik_limit: int
    hikaye_gunluk_limit: int
    harita_dakikalik_limit: int
    gunluk_toplam_istek: int
    gunluk_toplam_usd: float
    proxy_arkasinda: bool

    @property
    def llm_available(self) -> bool:
        """Sağlayıcının kurulu görünüp görünmediği.

        Kesin değil, ipucu: Anthropic SDK anahtar ortamda yokken `ant auth
        login` profilini de deneyebilir, yerel bir uç anahtar istemez.
        """
        if self.llm_saglayici == "gemini":
            return bool(self.gemini_api_key)
        if self.llm_saglayici == "openai_uyumlu":
            return bool(self.llm_temel_adres)
        return bool(self.anthropic_api_key)

    @property
    def ucretsiz_saglayici(self) -> bool:
        """Sağlayıcı ücretsiz katmanda ya da yerel mi çalışıyor."""
        return self.llm_saglayici in ("gemini", "openai_uyumlu")

    @property
    def tts_available(self) -> bool:
        if self.tts_provider == "elevenlabs":
            return bool(self.elevenlabs_api_key and self.elevenlabs_voice_id)
        if self.tts_provider == "google":
            return bool(self.google_tts_api_key)
        return False


def get_settings() -> Settings:
    saglayici = os.getenv("LLM_SAGLAYICI", "anthropic").strip().lower()
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        llm_saglayici=saglayici,
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        llm_temel_adres=os.getenv("LLM_TEMEL_ADRES"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        story_model=os.getenv(
            "STORY_MODEL", VARSAYILAN_MODELLER.get(saglayici, DEFAULT_MODEL)
        ),
        max_output_tokens=int(os.getenv("STORY_MAX_TOKENS", "8000")),
        tts_provider=os.getenv("TTS_PROVIDER", "google"),
        elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        google_tts_api_key=os.getenv("GOOGLE_TTS_API_KEY"),
        google_tts_voice=os.getenv("GOOGLE_TTS_VOICE", "tr-TR-Chirp3-HD-Achernar"),
        hikaye_saatlik_limit=int(os.getenv("HIKAYE_SAATLIK_LIMIT", "5")),
        hikaye_gunluk_limit=int(os.getenv("HIKAYE_GUNLUK_LIMIT", "15")),
        harita_dakikalik_limit=int(os.getenv("HARITA_DAKIKALIK_LIMIT", "30")),
        gunluk_toplam_istek=int(os.getenv("GUNLUK_TOPLAM_ISTEK", "300")),
        gunluk_toplam_usd=float(os.getenv("GUNLUK_TOPLAM_USD", "25")),
        # X-Forwarded-For yalnızca güvenilen bir vekil sunucunun arkasındayken
        # dikkate alınır; aksi hâlde herkes bu başlığı uydurup kaynak başına
        # sınırı atlayabilir.
        proxy_arkasinda=os.getenv("PROXY_ARKASINDA", "").lower() in ("1", "true", "evet"),
    )
