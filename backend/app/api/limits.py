"""İstek sınırlama ve harcama tavanı.

Buradaki asıl risk istek hacmi değil, faturadır: `/api/hikaye` her çağrıda
bir model çağrısı, `/api/seslendir` her çağrıda bir TTS çağrısı yapar.
Bu yüzden iki ayrı katman var ve ikisi farklı saldırıya karşı korur:

1. **Kaynak başına pencere.** Tek bir istemcinin ucu döngüye sokmasını
   engeller. Dağıtık bir kötüye kullanımı durdurmaz.
2. **Günlük genel tavan.** Kaç kaynaktan gelirse gelsin, günlük toplam
   harcamayı sabit bir üst sınırda tutar. Faturayı gerçekten koruyan
   katman budur; birincisi tek başına yeterli değildir.

Tavan hem istek sayısını hem *gerçekleşen* dolar maliyetini izler, çünkü
hikâye başına maliyet metin uzunluğuna göre değişir; yalnızca istek saymak
maliyeti eksik tahmin eder.

Durum süreç belleğinde tutulur. Tek süreçli dağıtımda (MVP) bu yeterlidir;
birden fazla işçiye geçildiğinde ortak bir sayaca (Redis) taşınmalıdır,
aksi hâlde her işçi kendi tavanını uygular ve gerçek tavan işçi sayısıyla
çarpılır.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date
from typing import Deque, Dict, Optional, Tuple


@dataclass(frozen=True)
class Kural:
    """Belirli bir pencerede izin verilen en fazla istek sayısı."""

    ad: str
    limit: int
    pencere_saniye: int

    @property
    def insan_okunur_pencere(self) -> str:
        if self.pencere_saniye % 3600 == 0:
            saat = self.pencere_saniye // 3600
            return "saatte" if saat == 1 else f"{saat} saatte"
        if self.pencere_saniye % 60 == 0:
            dakika = self.pencere_saniye // 60
            return "dakikada" if dakika == 1 else f"{dakika} dakikada"
        return f"{self.pencere_saniye} saniyede"


class LimitAsildi(Exception):
    """Sınır aşıldığında atılır. `tekrar_dene_saniye` HTTP Retry-After olur."""

    def __init__(self, mesaj: str, tekrar_dene_saniye: int) -> None:
        super().__init__(mesaj)
        self.mesaj = mesaj
        self.tekrar_dene_saniye = max(1, int(tekrar_dene_saniye))


class KayanPencere:
    """Kaynak başına kayan pencere sayacı.

    Sabit pencere yerine kayan pencere kullanıyoruz: sabit pencerede
    istemci pencere sınırının iki yanına yığılarak limitin iki katını
    kısa sürede harcayabilir.
    """

    def __init__(self, kurallar: Tuple[Kural, ...]) -> None:
        self.kurallar = kurallar
        self._kilit = threading.Lock()
        self._vurus: Dict[str, Deque[float]] = defaultdict(deque)
        # En uzun pencereden eski kayıtlar hiçbir kurala girmez, atılabilir.
        self._en_uzun = max((k.pencere_saniye for k in kurallar), default=0)

    def dogrula(self, anahtar: str, simdi: Optional[float] = None) -> None:
        simdi = simdi if simdi is not None else time.monotonic()
        with self._kilit:
            kuyruk = self._vurus[anahtar]
            while kuyruk and simdi - kuyruk[0] > self._en_uzun:
                kuyruk.popleft()

            for kural in self.kurallar:
                sinir = simdi - kural.pencere_saniye
                sayi = sum(1 for t in kuyruk if t > sinir)
                if sayi >= kural.limit:
                    en_eski = next(t for t in kuyruk if t > sinir)
                    bekle = kural.pencere_saniye - (simdi - en_eski)
                    raise LimitAsildi(
                        f"Çok fazla istek. {kural.insan_okunur_pencere} en fazla "
                        f"{kural.limit} istek yapılabilir. "
                        f"Lütfen {int(bekle) + 1} saniye sonra tekrar deneyin.",
                        tekrar_dene_saniye=bekle,
                    )

            kuyruk.append(simdi)

    def sifirla(self) -> None:
        with self._kilit:
            self._vurus.clear()


@dataclass
class GunlukTavan:
    """Günlük genel istek ve harcama tavanı.

    `dogrula` isteği kabul etmeden önce çağrılır; `harcama_ekle` ise çağrı
    tamamlandıktan sonra gerçekleşen maliyetle. Böylece tavan tahminle
    değil, gerçekleşen tutarla işler.
    """

    gunluk_istek: int
    gunluk_usd: float
    _kilit: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _gun: date = field(default_factory=date.today)
    _istek: int = 0
    _usd: float = 0.0

    def _gunu_tazele(self, bugun: Optional[date] = None) -> None:
        bugun = bugun or date.today()
        if bugun != self._gun:
            self._gun = bugun
            self._istek = 0
            self._usd = 0.0

    def dogrula(self, bugun: Optional[date] = None) -> None:
        with self._kilit:
            self._gunu_tazele(bugun)
            if self._istek >= self.gunluk_istek:
                raise LimitAsildi(
                    "Bugünkü genel kapasite doldu. Lütfen yarın tekrar deneyin.",
                    tekrar_dene_saniye=self._gun_sonuna_saniye(),
                )
            if self._usd >= self.gunluk_usd:
                raise LimitAsildi(
                    "Bugünkü genel harcama tavanına ulaşıldı. "
                    "Lütfen yarın tekrar deneyin.",
                    tekrar_dene_saniye=self._gun_sonuna_saniye(),
                )
            self._istek += 1

    def harcama_ekle(self, usd: Optional[float]) -> None:
        if not usd:
            return
        with self._kilit:
            self._gunu_tazele()
            self._usd += usd

    def durum(self) -> Dict[str, float]:
        with self._kilit:
            self._gunu_tazele()
            return {
                "gun": self._gun.isoformat(),
                "kullanilan_istek": self._istek,
                "istek_tavani": self.gunluk_istek,
                "kullanilan_usd": round(self._usd, 4),
                "usd_tavani": self.gunluk_usd,
            }

    def sifirla(self) -> None:
        with self._kilit:
            self._gun = date.today()
            self._istek = 0
            self._usd = 0.0

    @staticmethod
    def _gun_sonuna_saniye() -> int:
        import datetime as _dt

        simdi = _dt.datetime.now()
        yarin = _dt.datetime.combine(
            simdi.date() + _dt.timedelta(days=1), _dt.time.min
        )
        return int((yarin - simdi).total_seconds())
