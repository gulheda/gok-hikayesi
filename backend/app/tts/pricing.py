"""TTS maliyet tahmini.

Bu modül bilerek API anahtarı gerektirmiyor: birim ekonomisi kararı
(hangi sağlayıcı, sesli anlatım MVP'de olmalı mı) hesap açmadan önce
verilebilmeli. Hikâye başına maliyetin ezici çoğunluğu TTS'ten gelir -
LLM çağrısı sent mertebesindeyken TTS dolar mertebesine çıkabilir.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

# 1000 karakter başına USD. Kaynaklar Eylül 2026 itibarıyla yayımlanmış
# liste fiyatlarıdır; abonelik paketlerinde efektif fiyat düşebilir.
TTS_PRICING_USD_PER_1K_CHARS: Dict[str, float] = {
    "elevenlabs_multilingual_v2": 0.10,
    "elevenlabs_flash_v2_5": 0.05,
    "google_chirp3_hd": 0.03,
    "google_standard": 0.004,
}

# Türkçe seslendirmede yaklaşık okuma hızı. Metin uzunluğundan süre
# tahmini için kullanılır (ortalama ~15 karakter/saniye).
CHARS_PER_SECOND = 15.0


@dataclass(frozen=True)
class CostEstimate:
    provider: str
    characters: int
    usd: float
    estimated_seconds: float

    @property
    def estimated_minutes(self) -> float:
        return self.estimated_seconds / 60.0


def estimate(characters: int, provider: str) -> CostEstimate:
    if provider not in TTS_PRICING_USD_PER_1K_CHARS:
        raise KeyError(
            f"Bilinmeyen TTS sağlayıcı: {provider}. "
            f"Seçenekler: {sorted(TTS_PRICING_USD_PER_1K_CHARS)}"
        )
    birim = TTS_PRICING_USD_PER_1K_CHARS[provider]
    return CostEstimate(
        provider=provider,
        characters=characters,
        usd=characters / 1000.0 * birim,
        estimated_seconds=characters / CHARS_PER_SECOND,
    )


def compare_all(characters: int) -> List[CostEstimate]:
    """Tüm sağlayıcıları ucuzdan pahalıya sıralar."""
    return sorted(
        (estimate(characters, p) for p in TTS_PRICING_USD_PER_1K_CHARS),
        key=lambda e: e.usd,
    )
