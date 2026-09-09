"""Hikâye üretimi: haritayı Claude'a verip metni alır.

Üretilen her hikâyeyle birlikte model adı, prompt sürümü ve token
sayıları saklanır. Bunlar olmadan iki şey yapılamaz: prompt değişikliğinin
çıktıyı iyileştirip iyileştirmediğini karşılaştırmak, ve hikâye başına
gerçek maliyeti bilmek. İkisi de ürün kararlarının dayanağı.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import anthropic

from ..astro.chart import NatalChart
from ..config import MODEL_PRICING_USD, get_settings
from .brief import llm_brifingi, olgusal_panel, yas_hesapla
from .prompts import PROMPT_VERSION, SYSTEM_PROMPT, ToneProfile, build_user_prompt, tone_for_age


class StoryGenerationError(RuntimeError):
    pass


class StoryServiceNotConfigured(StoryGenerationError):
    """Kimlik bilgisi eksik olduğu için hikâye servisi kullanılamıyor.

    Bu durum "yukarıdaki servis çöktü"den farklıdır: kurulum eksikliğidir
    ve farklı bir HTTP durumu ile farklı bir kullanıcı mesajı hak eder.
    SDK bu hatayı istek anında `TypeError` olarak atıyor; genel bir
    `except` ile yutulursa 500'e dönüşüp gerçek sebebi gizliyor.
    """


@dataclass
class Story:
    title: str
    body: str
    factual_panel: str        # koddan üretilen, modelin dokunmadığı olgusal panel
    tone_key: str
    age: int
    model: str
    prompt_version: str
    input_tokens: int
    output_tokens: int
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def word_count(self) -> int:
        return len(self.body.split())

    @property
    def cost_usd(self) -> Optional[float]:
        fiyat = MODEL_PRICING_USD.get(self.model)
        if not fiyat:
            return None
        return (
            self.input_tokens / 1_000_000 * fiyat["input"]
            + self.output_tokens / 1_000_000 * fiyat["output"]
        )

    @property
    def character_count(self) -> int:
        """TTS maliyeti karakter başına faturalandığı için ölçülüyor."""
        return len(self.body)


_TITLE_PATTERN = re.compile(r"^\s*BAŞLIK\s*:\s*(.+?)\s*$", re.MULTILINE)


def _split_title_and_body(raw: str) -> tuple:
    """Modelin döndürdüğü metinden başlığı ayırır.

    Model biçimi tutturamazsa hata vermek yerine ilk satırı başlık kabul
    ediyoruz; kullanıcının eline hiç metin geçmemesindense biçimi bozuk
    ama okunabilir bir metin geçmesi yeğdir.
    """
    match = _TITLE_PATTERN.search(raw)
    if match:
        title = match.group(1).strip()
        body = raw[match.end():].strip()
        return title, body

    lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    if not lines:
        raise StoryGenerationError("Model boş yanıt döndürdü.")
    return lines[0], "\n\n".join(lines[1:]).strip() or lines[0]


def generate_story(
    chart: NatalChart,
    name: Optional[str] = None,
    model: Optional[str] = None,
    client: Optional[anthropic.Anthropic] = None,
    today: Optional[object] = None,
) -> Story:
    """Doğum haritasından hikâye üretir."""
    settings = get_settings()
    model = model or settings.story_model
    try:
        client = client or anthropic.Anthropic()
    except anthropic.AnthropicError as exc:
        raise StoryServiceNotConfigured(
            "Hikâye servisi yapılandırılmamış: ANTHROPIC_API_KEY tanımlı değil."
        ) from exc

    age = yas_hesapla(chart.birth.birth_date, today)
    tone: ToneProfile = tone_for_age(age)
    brief = llm_brifingi(chart)
    user_prompt = build_user_prompt(brief, tone, name or chart.birth.name)

    try:
        # Uzun metin üretiliyor; akış kullanmak HTTP zaman aşımını önler.
        with client.messages.stream(
            model=model,
            max_tokens=settings.max_output_tokens,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            message = stream.get_final_message()
    except anthropic.APIStatusError as exc:
        raise StoryGenerationError(
            f"Hikâye üretilemedi (HTTP {exc.status_code}): {exc.message}"
        ) from exc
    except anthropic.APIConnectionError as exc:
        raise StoryGenerationError(
            f"Hikâye servisine ulaşılamadı: {exc}"
        ) from exc
    except TypeError as exc:
        # SDK kimlik bilgisi çözemediğinde istek anında TypeError atıyor.
        if "authentication method" in str(exc):
            raise StoryServiceNotConfigured(
                "Hikâye servisi yapılandırılmamış: ANTHROPIC_API_KEY tanımlı "
                "değil. Ortam değişkenini ayarlayın veya .env dosyasına ekleyin."
            ) from exc
        raise

    if message.stop_reason == "refusal":
        raise StoryGenerationError(
            "Model bu isteği yanıtlamayı reddetti. Girdiyi gözden geçirin."
        )

    raw = "\n".join(
        block.text for block in message.content if block.type == "text"
    ).strip()
    if not raw:
        raise StoryGenerationError("Model metin bloğu döndürmedi.")

    title, body = _split_title_and_body(raw)

    return Story(
        title=title,
        body=body,
        factual_panel=olgusal_panel(chart),
        tone_key=tone.key,
        age=age,
        model=model,
        prompt_version=PROMPT_VERSION,
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
    )
