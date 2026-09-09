"""Uzun metni TTS istekleri için parçalara böler.

TTS servisleri istek başına karakter sınırı koyar (ElevenLabs ~5000,
Google ~5000 bayt). Metni ortasından kesmek cümleyi bölerek seslendirmeyi
bozar; bu yüzden bölme her zaman cümle sınırında yapılır. Paragraf
sınırları tercih edilir çünkü paragraf arası doğal duraklama zaten vardır
ve parçalar birleştirildiğinde ek dikiş izi bırakmaz.
"""
from __future__ import annotations

import re
from typing import List

DEFAULT_MAX_CHARS = 4500

# Cümle sonu: nokta/soru/ünlem + boşluk + büyük harf ya da tırnak.
# Türkçe kısaltmalar (Dr., vb., Prof.) yanlış bölmeye yol açmasın diye
# ardından büyük harf gelmesi şartı aranıyor.
_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+(?=[A-ZÇĞİÖŞÜ\"“'])")


def split_sentences(text: str) -> List[str]:
    parcalar = _SENTENCE_END.split(text.strip())
    return [p.strip() for p in parcalar if p.strip()]


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> List[str]:
    """Metni `max_chars`'ı aşmayan, cümle sınırında bölünmüş parçalara ayırır."""
    if max_chars <= 0:
        raise ValueError("max_chars pozitif olmalı")

    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    parcalar: List[str] = []
    for paragraf in [p.strip() for p in text.split("\n\n") if p.strip()]:
        if parcalar and len(parcalar[-1]) + 2 + len(paragraf) <= max_chars:
            parcalar[-1] = parcalar[-1] + "\n\n" + paragraf
            continue
        if len(paragraf) <= max_chars:
            parcalar.append(paragraf)
            continue

        # Paragraf tek başına sınırı aşıyor: cümlelere in.
        gecerli = ""
        for cumle in split_sentences(paragraf):
            if not gecerli:
                gecerli = cumle
            elif len(gecerli) + 1 + len(cumle) <= max_chars:
                gecerli = gecerli + " " + cumle
            else:
                parcalar.append(gecerli)
                gecerli = cumle
            # Tek cümle bile sınırı aşıyorsa (çok nadir) sert bölmek zorundayız.
            while len(gecerli) > max_chars:
                parcalar.append(gecerli[:max_chars])
                gecerli = gecerli[max_chars:]
        if gecerli:
            parcalar.append(gecerli)

    return parcalar
