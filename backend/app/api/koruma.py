"""Uç noktalara uygulanan sınırlama bağımlılıkları."""
from __future__ import annotations

from fastapi import HTTPException, Request

from ..config import get_settings
from .limits import GunlukTavan, KayanPencere, Kural, LimitAsildi

_ayar = get_settings()

# Pahalı uçlar: her çağrı bir model veya TTS çağrısı demek.
pahali_pencere = KayanPencere((
    Kural("saatlik", _ayar.hikaye_saatlik_limit, 3600),
    Kural("gunluk", _ayar.hikaye_gunluk_limit, 86_400),
))

# Ucuz uç: yalnızca hesaplama, ama yine de kötüye kullanıma açık olmamalı.
ucuz_pencere = KayanPencere((
    Kural("dakikalik", _ayar.harita_dakikalik_limit, 60),
))

gunluk_tavan = GunlukTavan(
    gunluk_istek=_ayar.gunluk_toplam_istek,
    gunluk_usd=_ayar.gunluk_toplam_usd,
)


def istemci_anahtari(request: Request) -> str:
    """İsteğin sayılacağı kaynak anahtarı.

    `X-Forwarded-For` istemci tarafından serbestçe uydurulabilen bir
    başlıktır. Doğrudan internete açık bir sunucuda ona güvenmek, kaynak
    başına sınırı tamamen etkisiz kılar: saldırgan her istekte farklı bir
    değer yollar. Bu yüzden yalnızca vekil sunucu arkasında olduğumuz
    açıkça belirtildiğinde okunur.
    """
    if _ayar.proxy_arkasinda:
        iletilen = request.headers.get("x-forwarded-for")
        if iletilen:
            # En soldaki, vekilin gördüğü asıl istemcidir.
            return iletilen.split(",")[0].strip()
    return request.client.host if request.client else "bilinmeyen"


def _uygula(pencere: KayanPencere, request: Request, tavan_uygula: bool) -> None:
    try:
        pencere.dogrula(istemci_anahtari(request))
        if tavan_uygula:
            gunluk_tavan.dogrula()
    except LimitAsildi as hata:
        raise HTTPException(
            status_code=429,
            detail=hata.mesaj,
            headers={"Retry-After": str(hata.tekrar_dene_saniye)},
        ) from hata


def pahali_uc(request: Request) -> None:
    """Model/TTS çağrısı yapan uçlar için: kaynak sınırı + günlük tavan."""
    _uygula(pahali_pencere, request, tavan_uygula=True)


def ucuz_uc(request: Request) -> None:
    """Yalnızca hesaplama yapan uçlar için: sadece kaynak sınırı."""
    _uygula(ucuz_pencere, request, tavan_uygula=False)
