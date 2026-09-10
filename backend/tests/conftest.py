"""Ortak test kurulumu."""
from __future__ import annotations

import pytest

import pytest

from app.api.koruma import gunluk_tavan, pahali_pencere, ucuz_pencere

# Sağlayıcı seçimini etkileyen ortam değişkenleri. Bunlar temizlenmezse
# testler geliştiricinin .env dosyasına bağımlı hale gelir: makinede
# LLM_SAGLAYICI=sablon yazıyorsa "yapılandırılmamış" testi geçemez.
_LLM_ORTAMI = (
    "LLM_SAGLAYICI", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
    "GEMINI_API_KEY", "LLM_TEMEL_ADRES", "LLM_API_KEY", "STORY_MODEL",
)


@pytest.fixture(autouse=True)
def _sinirlari_sifirla():
    """Her testten önce sayaçları temizler.

    Sayaçlar süreç belleğinde yaşadığı için testler arasında sızar: bir
    testin yaptığı istekler sonraki testi 429'a düşürebilir. Bu, testleri
    çalışma sırasına bağımlı kılar ki hata ayıklaması en zor kırılganlık
    türlerinden biridir.
    """
    ucuz_pencere.sifirla()
    pahali_pencere.sifirla()
    gunluk_tavan.sifirla()
    yield


@pytest.fixture(autouse=True)
def _llm_ortamini_yalit(monkeypatch):
    """Testleri .env dosyasından yalıtır.

    `config.load_dotenv()` içe aktarma anında .env'i os.environ'a
    yüklüyor. Bu, testin sonucunu makinedeki yapılandırmaya bağlar -
    aynı test bir makinede geçip diğerinde kalır. Sağlayıcıya ihtiyacı
    olan testler onu kendisi ayarlasın.
    """
    for anahtar in _LLM_ORTAMI:
        monkeypatch.delenv(anahtar, raising=False)
    yield
