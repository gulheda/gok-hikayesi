"""Dil modeli sağlayıcıları.

Hikâye üretimi tek bir servise kilitlenmemeli. Sebep ücret: proje henüz
doğrulanmamış bir varsayımın (hikâye kalitesi) üzerinde duruyor ve o
varsayımı sınamak için para harcamak gerekmiyor. Ücretsiz katmanı olan
servisler ya da makinede çalışan yerel bir model aynı promptu çalıştırabilir.

Üç sağlayıcı var ve üçü de aynı arayüzü uyguluyor:

- `AnthropicSaglayici`   — Claude. Ücretli, talimatlara uyumu en iyi.
- `GeminiSaglayici`      — Google. Ücretsiz katmanı var, fatura gerekmez.
- `OpenAIUyumluSaglayici`— /chat/completions konuşan her şey: yerel Ollama,
                           OpenRouter'ın ücretsiz modelleri, Groq, LM Studio.
- `SablonSaglayici`      — hiçbir model çağırmaz; metni şablon motoru üretir.
                           Ağ gerekmez, maliyet sıfır, kota yok.

Yeni bağımlılık eklemiyoruz; Gemini ve OpenAI uyumlu uçlar doğrudan HTTP
ile konuşuluyor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

import httpx


class SaglayiciHatasi(RuntimeError):
    pass


class YapilandirmaEksik(SaglayiciHatasi):
    """Kimlik bilgisi ya da ayar eksik. Arıza değil, kurulum eksikliği."""


@dataclass(frozen=True)
class UretimSonucu:
    metin: str
    girdi_token: int
    cikti_token: int
    model: str
    saglayici: str
    reddedildi: bool = False


class LLMSaglayici(Protocol):
    ad: str
    model: str

    def uret(self, sistem: str, kullanici: str, en_fazla_token: int) -> UretimSonucu:
        ...


# --------------------------------------------------------------------------
# Anthropic
# --------------------------------------------------------------------------

class AnthropicSaglayici:
    ad = "anthropic"

    def __init__(self, model: str, api_key: Optional[str] = None) -> None:
        self.model = model
        self._api_key = api_key
        self._istemci = None

    def _client(self):
        import anthropic

        if self._istemci is None:
            try:
                self._istemci = (
                    anthropic.Anthropic(api_key=self._api_key)
                    if self._api_key
                    else anthropic.Anthropic()
                )
            except anthropic.AnthropicError as exc:
                raise YapilandirmaEksik(
                    "ANTHROPIC_API_KEY tanımlı değil."
                ) from exc
        return self._istemci

    def uret(self, sistem: str, kullanici: str, en_fazla_token: int) -> UretimSonucu:
        import anthropic

        try:
            with self._client().messages.stream(
                model=self.model,
                max_tokens=en_fazla_token,
                system=sistem,
                thinking={"type": "adaptive"},
                messages=[{"role": "user", "content": kullanici}],
            ) as akis:
                mesaj = akis.get_final_message()
        except anthropic.APIStatusError as exc:
            raise SaglayiciHatasi(
                f"Anthropic hatası (HTTP {exc.status_code}): {exc.message}"
            ) from exc
        except anthropic.APIConnectionError as exc:
            raise SaglayiciHatasi(f"Anthropic'e ulaşılamadı: {exc}") from exc
        except TypeError as exc:
            # SDK kimlik bilgisi çözemediğinde istek anında TypeError atıyor.
            if "authentication method" in str(exc):
                raise YapilandirmaEksik("ANTHROPIC_API_KEY tanımlı değil.") from exc
            raise

        metin = "\n".join(b.text for b in mesaj.content if b.type == "text").strip()
        return UretimSonucu(
            metin=metin,
            girdi_token=mesaj.usage.input_tokens,
            cikti_token=mesaj.usage.output_tokens,
            model=self.model,
            saglayici=self.ad,
            reddedildi=mesaj.stop_reason == "refusal",
        )


# --------------------------------------------------------------------------
# Google Gemini
# --------------------------------------------------------------------------

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiSaglayici:
    """Google Gemini, REST üzerinden.

    Ücretsiz katman fatura açmadan kullanılabilir; günlük istek sınırı var.
    ÖNEMLİ: Projede faturalandırma açılırsa ücretsiz katman o proje için
    tamamen kalkar ve ilk tokendan itibaren ücretlendirilir - deneme için
    ayrı bir proje kullanmak güvenlidir.

    Kullanılabilir model adlarını görmek için:
        curl "https://generativelanguage.googleapis.com/v1beta/models?key=ANAHTAR"
    """

    ad = "gemini"

    def __init__(self, model: str, api_key: Optional[str], timeout: float = 180.0) -> None:
        if not api_key:
            raise YapilandirmaEksik(
                "GEMINI_API_KEY tanımlı değil. Anahtar aistudio.google.com "
                "üzerinden ücretsiz alınır."
            )
        self.model = model
        self._api_key = api_key
        self._timeout = timeout

    def uret(self, sistem: str, kullanici: str, en_fazla_token: int) -> UretimSonucu:
        try:
            yanit = httpx.post(
                GEMINI_URL.format(model=self.model),
                params={"key": self._api_key},
                json={
                    "system_instruction": {"parts": [{"text": sistem}]},
                    "contents": [{"role": "user", "parts": [{"text": kullanici}]}],
                    "generationConfig": {"maxOutputTokens": en_fazla_token},
                },
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise SaglayiciHatasi(f"Gemini'ye ulaşılamadı: {exc}") from exc

        if yanit.status_code == 429:
            raise SaglayiciHatasi(
                "Gemini ücretsiz katman kotası doldu. Kota Pasifik saatiyle "
                "gece yarısı sıfırlanır."
            )
        if yanit.status_code != 200:
            raise SaglayiciHatasi(
                f"Gemini hatası (HTTP {yanit.status_code}): {yanit.text[:300]}"
            )

        govde = yanit.json()
        adaylar = govde.get("candidates") or []
        if not adaylar:
            # Güvenlik süzgeci ya da boş yanıt.
            sebep = govde.get("promptFeedback", {}).get("blockReason")
            raise SaglayiciHatasi(
                f"Gemini yanıt döndürmedi{f' (sebep: {sebep})' if sebep else ''}."
            )

        parcalar = adaylar[0].get("content", {}).get("parts", [])
        metin = "".join(p.get("text", "") for p in parcalar).strip()
        kullanim = govde.get("usageMetadata", {})
        return UretimSonucu(
            metin=metin,
            girdi_token=kullanim.get("promptTokenCount", 0),
            cikti_token=kullanim.get("candidatesTokenCount", 0),
            model=self.model,
            saglayici=self.ad,
            reddedildi=adaylar[0].get("finishReason") == "SAFETY",
        )


# --------------------------------------------------------------------------
# OpenAI uyumlu uçlar (Ollama, OpenRouter, Groq, LM Studio…)
# --------------------------------------------------------------------------

class OpenAIUyumluSaglayici:
    """`/chat/completions` konuşan herhangi bir servis.

    Yerel model için (tamamen ücretsiz, ağ gerektirmez):
        LLM_SAGLAYICI=openai_uyumlu
        LLM_TEMEL_ADRES=http://localhost:11434/v1
        LLM_MODEL=llama3.1:8b
        LLM_API_KEY=ollama            # Ollama anahtarı yok sayar

    Uyarı: küçük yerel modeller bu promptun yedi mutlak kuralına genellikle
    uyamaz; sonuç burç yorumuna kayar. Boru hattını sınamak için uygundur,
    hikâye kalitesini yargılamak için değil.
    """

    ad = "openai_uyumlu"

    def __init__(
        self,
        model: str,
        temel_adres: str,
        api_key: Optional[str] = None,
        timeout: float = 300.0,
    ) -> None:
        if not temel_adres:
            raise YapilandirmaEksik("LLM_TEMEL_ADRES tanımlı değil.")
        self.model = model
        self._adres = temel_adres.rstrip("/") + "/chat/completions"
        self._api_key = api_key
        self._timeout = timeout

    def uret(self, sistem: str, kullanici: str, en_fazla_token: int) -> UretimSonucu:
        basliklar = {"Content-Type": "application/json"}
        if self._api_key:
            basliklar["Authorization"] = f"Bearer {self._api_key}"

        try:
            yanit = httpx.post(
                self._adres,
                headers=basliklar,
                json={
                    "model": self.model,
                    "max_tokens": en_fazla_token,
                    "messages": [
                        {"role": "system", "content": sistem},
                        {"role": "user", "content": kullanici},
                    ],
                },
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise SaglayiciHatasi(f"{self._adres} adresine ulaşılamadı: {exc}") from exc

        if yanit.status_code != 200:
            raise SaglayiciHatasi(
                f"Sağlayıcı hatası (HTTP {yanit.status_code}): {yanit.text[:300]}"
            )

        govde = yanit.json()
        secenekler = govde.get("choices") or []
        if not secenekler:
            raise SaglayiciHatasi("Sağlayıcı yanıt döndürmedi.")

        metin = (secenekler[0].get("message", {}).get("content") or "").strip()
        kullanim = govde.get("usage") or {}
        return UretimSonucu(
            metin=metin,
            girdi_token=kullanim.get("prompt_tokens", 0),
            cikti_token=kullanim.get("completion_tokens", 0),
            model=self.model,
            saglayici=self.ad,
        )


# --------------------------------------------------------------------------
# Şablon motoru
# --------------------------------------------------------------------------

class SablonSaglayici:
    """Şablon motorunu bir sağlayıcı gibi sunar.

    Diğer sağlayıcılardan farkı, aldığı promptu KULLANMAMASI: metni
    haritadan doğrudan üretir. Yine de aynı arayüzü uyguluyor, çünkü
    böylece uygulamanın geri kalanı (API ucu, iOS istemcisi, maliyet
    hesabı) metnin nereden geldiğini bilmek zorunda kalmıyor. Anahtarı
    olmayan bir kurulumda ürünün uçtan uca çalışmasını sağlayan yol budur.
    """

    ad = "sablon"

    def __init__(self, chart, name: Optional[str] = None) -> None:
        self._chart = chart
        self._name = name
        from .sablon.motor import SABLON_SURUMU

        self.model = f"sablon-v{SABLON_SURUMU}"

    def uret(self, sistem: str, kullanici: str, en_fazla_token: int) -> UretimSonucu:
        from .sablon.motor import uret as sablon_uret

        baslik, govde = sablon_uret(self._chart, ad=self._name)
        return UretimSonucu(
            metin=f"BAŞLIK: {baslik}\n\n{govde}",
            girdi_token=0,
            cikti_token=0,
            model=self.model,
            saglayici=self.ad,
        )
