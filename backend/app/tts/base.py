"""Seslendirme katmanı ortak arayüzü.

Sağlayıcı değiştirilebilir tutuluyor çünkü seçim henüz kesinleşmedi ve
maliyet farkı büyük: aynı hikâye için Google Standard ile ElevenLabs
Multilingual v2 arasında yirmi beş kat fark var (bkz. tts/pricing.py).
Karar ancak gerçek Türkçe çıktılar dinlenerek verilebilir, o yüzden ikisi
de aynı arayüzün arkasında duruyor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Protocol

from .chunking import chunk_text
from .pricing import CHARS_PER_SECOND


class TTSError(RuntimeError):
    pass


@dataclass
class SynthesisResult:
    audio: bytes
    mime_type: str
    provider: str
    voice: str
    characters: int
    chunk_count: int
    cost_usd: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def estimated_seconds(self) -> float:
        return self.characters / CHARS_PER_SECOND

    def save(self, path: str) -> str:
        with open(path, "wb") as f:
            f.write(self.audio)
        return path


class TTSProvider(Protocol):
    name: str
    max_chars_per_request: int

    def synthesize_chunk(self, text: str) -> bytes:
        """Tek bir parçayı seslendirip ham ses baytlarını döndürür."""
        ...


def synthesize_long_text(
    provider: TTSProvider,
    text: str,
    voice: str,
    mime_type: str = "audio/mpeg",
    cost_usd: Optional[float] = None,
) -> SynthesisResult:
    """Uzun metni parçalayıp seslendirir ve tek ses akışında birleştirir.

    Parçalar MP3 akışı olarak arka arkaya ekleniyor. Bu, çoğu oynatıcının
    sorunsuz çaldığı geçerli bir MP3 akışı üretir; ancak toplam süre
    bilgisi bazı oynatıcılarda yanlış görünebilir. Yayına çıkarken
    parçaları ffmpeg ile yeniden kodlamak (`concat` demuxer) bu izi
    tamamen kaldırır - şu an ffmpeg bağımlılığı eklemiyoruz.
    """
    parcalar = chunk_text(text, provider.max_chars_per_request)
    if not parcalar:
        raise TTSError("Seslendirilecek metin boş.")

    ses_parcalari: List[bytes] = []
    for i, parca in enumerate(parcalar, start=1):
        try:
            ses_parcalari.append(provider.synthesize_chunk(parca))
        except TTSError:
            raise
        except Exception as exc:  # sağlayıcıya özgü beklenmedik hatalar
            raise TTSError(
                f"{provider.name}: {i}. parça seslendirilemedi ({exc})"
            ) from exc

    uyarilar: List[str] = []
    if len(parcalar) > 1:
        uyarilar.append(
            f"Metin {len(parcalar)} parçada seslendirilip birleştirildi. "
            "Parça geçişlerinde çok kısa bir duraklama duyulabilir."
        )

    return SynthesisResult(
        audio=b"".join(ses_parcalari),
        mime_type=mime_type,
        provider=provider.name,
        voice=voice,
        characters=len(text),
        chunk_count=len(parcalar),
        cost_usd=cost_usd,
        warnings=uyarilar,
    )
