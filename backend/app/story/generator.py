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

from ..astro.chart import NatalChart
from ..config import MODEL_PRICING_USD, get_settings
from .saglayicilar import (
    AnthropicSaglayici,
    GeminiSaglayici,
    LLMSaglayici,
    OpenAIUyumluSaglayici,
    SablonSaglayici,
    SaglayiciHatasi,
    YapilandirmaEksik,
)
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
    provider: str = "anthropic"
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def word_count(self) -> int:
        return len(self.body.split())

    @property
    def cost_usd(self) -> Optional[float]:
        # Ücretsiz katman ya da yerel model: maliyet sıfır, tahmin değil.
        if self.provider in ("gemini", "openai_uyumlu", "elle", "sablon"):
            return 0.0
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


def prompt_ciftini_uret(
    chart: NatalChart,
    name: Optional[str] = None,
    today: Optional[object] = None,
) -> tuple:
    """Hikâye için (sistem promptu, kullanıcı promptu) çiftini döndürür.

    Model çağrısı yapmaz. Promptu herhangi bir sohbet arayüzüne elle
    yapıştırmak için kullanılır - hikâye kalitesini sınamak API erişimi
    gerektirmemeli.
    """
    age = yas_hesapla(chart.birth.birth_date, today)
    tone = tone_for_age(age)
    return SYSTEM_PROMPT, build_user_prompt(
        llm_brifingi(chart), tone, name or chart.birth.name
    )


def story_from_text(
    chart: NatalChart,
    raw: str,
    today: Optional[object] = None,
    model: str = "elle",
) -> Story:
    """Elle üretilmiş bir metni Story nesnesine çevirir.

    Boru hattının geri kalanı (olgusal panel, iOS örneği, uzunluk ölçümü)
    metnin nereden geldiğini bilmek zorunda değil; bu yüzden elle yapıştırılan
    çıktı da otomatik üretilen çıktıyla aynı yoldan akıyor.
    """
    if not raw or not raw.strip():
        raise StoryGenerationError("Metin boş.")

    age = yas_hesapla(chart.birth.birth_date, today)
    tone = tone_for_age(age)
    title, body = _split_title_and_body(raw)
    return Story(
        title=title,
        body=body,
        factual_panel=olgusal_panel(chart),
        tone_key=tone.key,
        age=age,
        model=model,
        prompt_version=PROMPT_VERSION,
        input_tokens=0,
        output_tokens=0,
        provider="elle",
    )


def saglayici_kur(settings=None, chart=None, name=None) -> LLMSaglayici:
    """Ayarlardan yapılandırılmış hikâye sağlayıcısını kurar.

    `chart` yalnızca şablon motoru için gerekli: o, promptu kullanmaz,
    metni doğrudan haritadan üretir.
    """
    settings = settings or get_settings()
    secim = settings.llm_saglayici

    if secim == "sablon":
        if chart is None:
            raise StoryServiceNotConfigured(
                "Şablon sağlayıcısı harita olmadan kurulamaz."
            )
        return SablonSaglayici(chart, name)
    if secim == "gemini":
        return GeminiSaglayici(settings.story_model, settings.gemini_api_key)
    if secim == "openai_uyumlu":
        return OpenAIUyumluSaglayici(
            settings.story_model, settings.llm_temel_adres or "", settings.llm_api_key
        )
    if secim == "anthropic":
        return AnthropicSaglayici(settings.story_model, settings.anthropic_api_key)

    raise StoryServiceNotConfigured(
        f"Bilinmeyen sağlayıcı: {secim}. LLM_SAGLAYICI şunlardan biri olmalı: "
        "anthropic, gemini, openai_uyumlu, sablon."
    )


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
    provider: Optional[LLMSaglayici] = None,
    today: Optional[object] = None,
) -> Story:
    """Doğum haritasından hikâye üretir."""
    settings = get_settings()
    if provider is None:
        try:
            provider = saglayici_kur(
                settings, chart=chart, name=name or chart.birth.name
            )
        except YapilandirmaEksik as exc:
            raise StoryServiceNotConfigured(
                f"Hikâye servisi yapılandırılmamış: {exc}"
            ) from exc

    age = yas_hesapla(chart.birth.birth_date, today)
    tone: ToneProfile = tone_for_age(age)
    brief = llm_brifingi(chart)
    user_prompt = build_user_prompt(brief, tone, name or chart.birth.name)

    try:
        sonuc = provider.uret(SYSTEM_PROMPT, user_prompt, settings.max_output_tokens)
    except YapilandirmaEksik as exc:
        raise StoryServiceNotConfigured(
            f"Hikâye servisi yapılandırılmamış: {exc}"
        ) from exc
    except SaglayiciHatasi as exc:
        raise StoryGenerationError(str(exc)) from exc

    if sonuc.reddedildi:
        raise StoryGenerationError(
            "Model bu isteği yanıtlamayı reddetti. Girdiyi gözden geçirin."
        )
    # Kırparak kontrol: yalnızca boşluktan oluşan bir yanıt da boş sayılır.
    # Sağlayıcıların hepsi kırpılmış metin döndürmüyor olabilir.
    ham = sonuc.metin.strip()
    if not ham:
        raise StoryGenerationError("Model metin bloğu döndürmedi.")

    title, body = _split_title_and_body(ham)

    return Story(
        title=title,
        body=body,
        factual_panel=olgusal_panel(chart),
        tone_key=tone.key,
        age=age,
        model=sonuc.model,
        prompt_version=PROMPT_VERSION,
        input_tokens=sonuc.girdi_token,
        output_tokens=sonuc.cikti_token,
        provider=sonuc.saglayici,
    )
