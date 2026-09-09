"""Ortak test kurulumu."""
from __future__ import annotations

import pytest

from app.api.koruma import gunluk_tavan, pahali_pencere, ucuz_pencere


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
