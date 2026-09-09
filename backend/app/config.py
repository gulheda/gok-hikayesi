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

    @property
    def llm_available(self) -> bool:
        # Anahtar ortamda yoksa SDK `ant auth login` profilini de deneyebilir;
        # bu yüzden yokluğu kesin bir engel değil, yalnızca bir ipucu.
        return bool(self.anthropic_api_key)


def get_settings() -> Settings:
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        story_model=os.getenv("STORY_MODEL", DEFAULT_MODEL),
        max_output_tokens=int(os.getenv("STORY_MAX_TOKENS", "8000")),
    )
