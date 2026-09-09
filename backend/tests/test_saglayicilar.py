"""Dil modeli sağlayıcı seçimi ve elle üretim yolu testleri.

Hikâye üretiminin tek bir ücretli servise kilitli olmaması bir ürün
kararı: proje henüz doğrulanmamış bir varsayımın üzerinde duruyor ve o
varsayımı sınamak para harcamayı gerektirmemeli.
"""
from __future__ import annotations

from datetime import date, time

import pytest

from app.astro.chart import BirthInput, calculate_chart
from app.config import get_settings
from app.story.generator import (
    Story,
    StoryGenerationError,
    StoryServiceNotConfigured,
    generate_story,
    prompt_ciftini_uret,
    saglayici_kur,
    story_from_text,
)
from app.story.saglayicilar import (
    AnthropicSaglayici,
    GeminiSaglayici,
    OpenAIUyumluSaglayici,
    SaglayiciHatasi,
    UretimSonucu,
    YapilandirmaEksik,
)

HARITA = calculate_chart(BirthInput(
    birth_date=date(2003, 7, 3), birth_time=time(9, 0),
    latitude=37.7765, longitude=29.0864, place_name="Denizli", name="Gülheda",
))


class SahteSaglayici:
    ad = "sahte"
    model = "sahte-model"

    def __init__(self, metin: str = "BAŞLIK: Deneme\n\nGövde metni.",
                 reddedildi: bool = False) -> None:
        self.metin = metin
        self.reddedildi = reddedildi
        self.cagrilar = []

    def uret(self, sistem, kullanici, en_fazla_token):
        self.cagrilar.append((sistem, kullanici, en_fazla_token))
        return UretimSonucu(
            metin=self.metin, girdi_token=100, cikti_token=200,
            model=self.model, saglayici=self.ad, reddedildi=self.reddedildi,
        )


# --------------------------------------------------------------------------
# Sağlayıcı seçimi
# --------------------------------------------------------------------------

def test_varsayilan_saglayici_anthropic(monkeypatch):
    monkeypatch.delenv("LLM_SAGLAYICI", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-deneme")
    assert isinstance(saglayici_kur(get_settings()), AnthropicSaglayici)


def test_gemini_secilebilir(monkeypatch):
    monkeypatch.setenv("LLM_SAGLAYICI", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "deneme")
    s = saglayici_kur(get_settings())
    assert isinstance(s, GeminiSaglayici)


def test_yerel_uc_secilebilir(monkeypatch):
    monkeypatch.setenv("LLM_SAGLAYICI", "openai_uyumlu")
    monkeypatch.setenv("LLM_TEMEL_ADRES", "http://localhost:11434/v1")
    monkeypatch.setenv("STORY_MODEL", "llama3.1:8b")
    s = saglayici_kur(get_settings())
    assert isinstance(s, OpenAIUyumluSaglayici)
    assert s.model == "llama3.1:8b"


def test_bilinmeyen_saglayici_acik_hata_verir(monkeypatch):
    monkeypatch.setenv("LLM_SAGLAYICI", "yok-boyle")
    with pytest.raises(StoryServiceNotConfigured, match="Bilinmeyen sağlayıcı"):
        saglayici_kur(get_settings())


def test_gemini_anahtarsiz_yapilandirma_hatasi_verir():
    with pytest.raises(YapilandirmaEksik, match="GEMINI_API_KEY"):
        GeminiSaglayici("gemini-3-flash", None)


def test_yerel_uc_adressiz_yapilandirma_hatasi_verir():
    with pytest.raises(YapilandirmaEksik, match="LLM_TEMEL_ADRES"):
        OpenAIUyumluSaglayici("model", "")


def test_saglayici_secimi_varsayilan_modeli_belirler(monkeypatch):
    monkeypatch.delenv("STORY_MODEL", raising=False)
    monkeypatch.setenv("LLM_SAGLAYICI", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "deneme")
    assert get_settings().story_model.startswith("gemini")


# --------------------------------------------------------------------------
# Üretim akışı
# --------------------------------------------------------------------------

def test_saglayici_disaridan_verilebilir():
    s = SahteSaglayici()
    hikaye = generate_story(HARITA, name="Gülheda", provider=s)
    assert hikaye.title == "Deneme"
    assert hikaye.provider == "sahte"
    assert len(s.cagrilar) == 1


def test_saglayiciya_verilen_prompt_imza_bolumunu_icerir():
    s = SahteSaglayici()
    generate_story(HARITA, name="Gülheda", provider=s)
    _, kullanici, _ = s.cagrilar[0]
    assert "BU HARİTAYA ÖZGÜ YAPILAR" in kullanici
    assert "Gülheda" in kullanici


def test_reddedilen_yanit_hata_verir():
    with pytest.raises(StoryGenerationError, match="reddetti"):
        generate_story(HARITA, provider=SahteSaglayici(reddedildi=True))


def test_bos_yanit_hata_verir():
    with pytest.raises(StoryGenerationError, match="metin"):
        generate_story(HARITA, provider=SahteSaglayici(metin="   "))


def test_saglayici_hatasi_uretim_hatasina_cevrilir():
    class Patlayan:
        ad, model = "patlayan", "m"
        def uret(self, *a):
            raise SaglayiciHatasi("ağ koptu")

    with pytest.raises(StoryGenerationError, match="ağ koptu"):
        generate_story(HARITA, provider=Patlayan())


# --------------------------------------------------------------------------
# Elle üretim (API'siz yol)
# --------------------------------------------------------------------------

def test_prompt_cifti_model_cagirmadan_uretilir():
    sistem, kullanici = prompt_ciftini_uret(HARITA, name="Gülheda")
    assert "MUTLAK KURALLAR" in sistem
    assert "BU HARİTAYA ÖZGÜ YAPILAR" in kullanici


def test_elle_metin_hikayeye_cevrilir():
    h = story_from_text(HARITA, "BAŞLIK: Elle Yazılmış\n\nBirinci paragraf.")
    assert h.title == "Elle Yazılmış"
    assert h.provider == "elle"
    assert h.word_count > 0
    # Olgusal panel yine koddan üretilir; metnin kaynağı onu etkilemez.
    assert "HESAPLANAN VERİ" in h.factual_panel


def test_elle_metin_bos_olamaz():
    with pytest.raises(StoryGenerationError, match="boş"):
        story_from_text(HARITA, "   ")


@pytest.mark.parametrize("saglayici", ["gemini", "openai_uyumlu", "elle"])
def test_ucretsiz_kaynaklarda_maliyet_sifir(saglayici):
    h = Story(
        title="x", body="y", factual_panel="", tone_key="yetiskin", age=20,
        model="m", prompt_version="2.0.0", input_tokens=1000,
        output_tokens=2000, provider=saglayici,
    )
    assert h.cost_usd == 0.0


def test_ucretli_saglayicida_maliyet_hesaplanir():
    h = Story(
        title="x", body="y", factual_panel="", tone_key="yetiskin", age=20,
        model="claude-opus-5", prompt_version="2.0.0",
        input_tokens=1_000_000, output_tokens=1_000_000, provider="anthropic",
    )
    assert h.cost_usd == pytest.approx(30.0)  # 5 USD girdi + 25 USD çıktı
