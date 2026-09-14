"""Ölçülmüş seyreklik: bir yapının gerçekte kaç haritada göründüğü.

Önceki sürümde yapılar "çok belirgin / belirgin / yaygın" diye ELLE
etiketlenmişti ve etiketlerin çoğu yanlış çıktı. Ölçüm (2500 rastgele
harita) şunu gösterdi:

- "Bir gök cismi açısal noktaya 8 derece yakın" -> haritaların %61'i.
  Elle "çok belirgin, çoğu haritada bulunmaz" yazılmıştı.
- "0,2 dereceden dar açı" -> %37,5. Elle "çok ender" sanılıyordu.
- "Gün doğumunda doğmak" -> %0,6. Hiç yakalanmıyordu bile.

Yanlış etiket doğrudan ürün hatasıdır: yaygın bir özelliği ender sanmak,
hikâyeyi milyonlarca kişiye uyan bir şeyin üzerine kurar - yani tam da
kaçınılmaya çalışılan burç yorumunu üretir.

Oranlar `backend/data/nadirlik.json` dosyasından okunur; dosya
`backend/tools/imza-kalibrasyon.py` ile üretilir. Dosya yoksa motor
çalışmaya devam eder ama sıralama elle konmuş varsayılanlara döner.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional

VERI_YOLU = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "nadirlik.json",
)

# Sınıf eşikleri. Sayılar keyfi değil: %5 altı "yüzde birkaç kişi",
# %20 altı "azınlık", %50 altı "yarıdan az", üstü "çoğunluk" demek.
COK_ENDER = 0.05
ENDER = 0.20
ORTA = 0.50

ETIKET_COK_ENDER = "çok ender"
ETIKET_ENDER = "ender"
ETIKET_ORTA = "seyrek değil"
ETIKET_YAYGIN = "yaygın"


# Bu eşiğin üstünde oynayan yapılar, doğum saati dağılımı varsayımına
# fazla bağlıdır ve oranları tek bir sayıyla sunulamaz.
DUYARLILIK_ESIGI = 0.35


@dataclass(frozen=True)
class Olcum:
    anahtar: str
    oran: Optional[float]       # None: ölçülmemiş
    oynama: Optional[float] = None   # senaryolar arası göreli oynama

    @property
    def senaryoya_duyarli(self) -> bool:
        """Oran, doğum saati dağılımı varsayımına aşırı bağlı mı.

        Türkiye için doğumların gün içindeki dağılımı bilinmiyor. Üç ayrı
        varsayımla ölçüldüğünde çoğu yapının oranı %5'ten az oynuyor ama
        "gün doğumunda doğmak" ailesi üç buçuk kat değişiyor - çünkü o
        yapı tamamen saate bağlı. Böyle bir oranı "her 150 kişiden
        birinde" diye sunmak, dayanağı olmayan bir kesinlik iddiasıdır.
        """
        return self.oynama is not None and self.oynama > DUYARLILIK_ESIGI

    @property
    def etiket(self) -> str:
        if self.oran is None:
            return ETIKET_ORTA
        if self.oran < COK_ENDER:
            return ETIKET_COK_ENDER
        if self.oran < ENDER:
            return ETIKET_ENDER
        if self.oran < ORTA:
            return ETIKET_ORTA
        return ETIKET_YAYGIN

    @property
    def agirlik(self) -> float:
        """Sıralama ağırlığı: seyrek olan öne çıkar.

        Ölçülmemiş yapılar orta bir ağırlık alır; bilinmeyeni ne en öne
        ne en sona koymak doğru olur.
        """
        if self.oran is None:
            return 40.0
        if self.oran <= 0:
            return 100.0
        # Oran küçüldükçe ağırlık büyür. Logaritmik olmasının sebebi
        # %1 ile %2 arasındaki farkın, %40 ile %41 arasındakinden çok
        # daha anlamlı olması.
        import math

        return min(100.0, -20.0 * math.log10(self.oran))

    @property
    def insan_ifadesi(self) -> str:
        """Oranı kullanıcının anlayacağı bir cümleye çevirir."""
        if self.oran is None or self.oran <= 0:
            return "ölçülmedi"
        if self.senaryoya_duyarli:
            # Kesin sayı verilmiyor: oran, doğum saati dağılımı
            # varsayımına göre kat kat değişiyor.
            return (f"{self.etiket} — kesin oran doğum saati dağılımına "
                    "bağlı olduğu için verilmiyor")
        if self.oran >= 0.5:
            return f"haritaların yaklaşık %{self.oran * 100:.0f}'inde"
        kisi = round(1 / self.oran)
        return f"yaklaşık her {kisi} kişiden birinde"

    @property
    def yaygin_mi(self) -> bool:
        return self.etiket == ETIKET_YAYGIN


@lru_cache(maxsize=1)
def _veri() -> Dict:
    try:
        with open(VERI_YOLU, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        # Kalibrasyon dosyası yoksa motor çalışmaya devam etmeli.
        return {}


def _oranlar() -> Dict[str, float]:
    return _veri().get("oranlar", {})


def _oynamalar() -> Dict[str, float]:
    return _veri().get("duyarlilik", {})


def olc(anahtar: str) -> Olcum:
    return Olcum(
        anahtar=anahtar,
        oran=_oranlar().get(anahtar),
        oynama=_oynamalar().get(anahtar),
    )


def kademe_anahtari(taban: str, deger: float, kademeler) -> str:
    """Sürekli bir değeri ölçüm kademesine eşler.

    Kalibrasyon aynı kademeleri kullandığı için anahtarlar birebir
    örtüşür; kademe listesi iki yerde ayrı tutulursa arama sessizce
    boşa düşer ve her yapı "ölçülmemiş" görünür.

    Bilinen sınır: kalibrasyon "haritada bu kademeye düşen EN AZ BİR yapı
    var mı" diye sayıyor; buradaki arama ise tek bir yapının seyrekliğini
    soruyor. İkisi tam olarak aynı soru değil. Sıralama için yeterli bir
    yaklaşım, ama oranı "bu tam konfigürasyon şu kadar kişide görülür"
    diye okumak yanlış olur.
    """
    for kademe in kademeler:
        if deger <= kademe:
            return f"{taban}_{kademe:g}"
    return f"{taban}_{kademeler[-1]:g}"


# Kalibrasyon aracıyla aynı kademeler (bkz. tools/imza-kalibrasyon.py)
ACISAL_KADEMELER = (1.0, 2.0, 4.0, 8.0)
ACI_KADEMELERI = (0.2, 0.5, 1.0, 2.0)


def ornek_sayisi() -> int:
    return int(_veri().get("ornek_sayisi", 0))
