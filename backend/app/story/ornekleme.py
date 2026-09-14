"""Kalibrasyon örneklemi: doğum anları nasıl dağıtılıyor.

Seyreklik oranları hangi doğum evreni üzerinden sayıldığına bağlı. Tek
düze örneklem (her saat, her gün, her il eşit) hesaplaması kolaydır ama
gerçek nüfusu tarif etmez.

Bilinen ve bilinmeyen:

- **Ay dağılımı biliniyor.** TÜİK verisine göre Türkiye'de doğumlar
  yaza kayar: Temmuz ve Ağustos zirve, Şubat ve Aralık dip. 2023'te
  958.408 doğumun 90.318'i Temmuz'da.
- **İl dağılımı biliniyor.** Nüfus illere göre çok dengesiz; İstanbul
  tek başına nüfusun altıda birinden fazlasını barındırıyor.
- **Saat dağılımı BİLİNMİYOR.** Türkiye için doğumların gün içindeki
  dağılımına dair yayımlanmış veri bulunamadı. Bu en kritik eksik,
  çünkü Yükselen doğrudan saate bağlı: saatler bir yere yığılırsa
  açısal yapıların seyrekliği kayar.

Saat için uydurma bir dağılım kullanmak, tek düze varsayımdan daha
kötü olurdu: sayılar hassas görünür ama dayanağı olmaz. Onun yerine
birkaç SENARYO tanımlanıyor ve kalibrasyon her biri için ayrı
çalıştırılıp sonuçların ne kadar oynadığına bakılıyor. Oynama küçükse
tek düze varsayım güvenli; büyükse oran tek bir sayı olarak
sunulmamalı.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

# TÜİK 2023 doğum istatistiklerinin ay dağılımı (göreli ağırlık).
# Temmuz zirve, Şubat dip. Değerler yaklaşık orandır; amaç kesin sayı
# değil, mevsimsel eğilimi örnekleme yansıtmak.
AY_AGIRLIKLARI: Sequence[float] = (
    0.96,  # Ocak
    0.88,  # Şubat (en düşük; ay 28 gün olduğu için de düşük)
    0.97,  # Mart
    0.96,  # Nisan
    1.00,  # Mayıs
    1.02,  # Haziran
    1.13,  # Temmuz (zirve)
    1.09,  # Ağustos
    1.05,  # Eylül
    1.02,  # Ekim
    0.96,  # Kasım
    0.96,  # Aralık
)


@dataclass(frozen=True)
class SaatSenaryosu:
    """Doğumların gün içindeki dağılımına dair bir varsayım.

    `agirliklar` 24 elemanlı; her saat diliminin göreli ağırlığı.
    """

    anahtar: str
    aciklama: str
    agirliklar: Sequence[float]

    def sec(self, uretec: random.Random) -> int:
        return uretec.choices(range(24), weights=self.agirliklar, k=1)[0]


def _duz() -> Sequence[float]:
    return tuple([1.0] * 24)


def _mesai_yigini() -> Sequence[float]:
    """Planlı sezaryenlerin mesai saatlerine yığıldığı senaryo.

    Türkiye OECD'nin en yüksek sezaryen oranına sahip (2023'te binde 615).
    Planlı ameliyatlar tipik olarak sabah başlar. Bu senaryo 08-12 arasını
    ağırlıklandırır. Ağırlıkların kendisi ölçüm değil, varsayımdır.
    """
    a = [0.5] * 24
    for saat in range(8, 13):
        a[saat] = 3.0
    for saat in range(13, 17):
        a[saat] = 1.5
    return tuple(a)


def _gece_zirvesi() -> Sequence[float]:
    """Kendiliğinden doğumların gece/sabaha karşı yoğunlaştığı senaryo.

    Kendiliğinden başlayan eylemin gece saatlerine kaydığı literatürde
    yaygın bir bulgudur. Bu senaryo 01-07 arasını ağırlıklandırır.
    """
    a = [0.8] * 24
    for saat in range(1, 8):
        a[saat] = 2.0
    return tuple(a)


SENARYOLAR: Dict[str, SaatSenaryosu] = {
    "duz": SaatSenaryosu(
        "duz", "Her saat eşit (varsayılan; en az varsayım içeren)", _duz()
    ),
    "mesai": SaatSenaryosu(
        "mesai", "Planlı sezaryen ağırlıklı, 08-12 yığını", _mesai_yigini()
    ),
    "gece": SaatSenaryosu(
        "gece", "Kendiliğinden doğum ağırlıklı, 01-07 yığını", _gece_zirvesi()
    ),
}

VARSAYILAN_SENARYO = "duz"


def ay_sec(uretec: random.Random) -> int:
    """1-12 arası ay numarası, TÜİK eğilimine göre ağırlıklı."""
    return uretec.choices(range(1, 13), weights=AY_AGIRLIKLARI, k=1)[0]


def il_agirliklari(iller: Dict[str, tuple], nufus: Dict[str, int]) -> List[float]:
    """İlleri nüfusa göre ağırlıklandırır; nüfusu bilinmeyen il 1 sayılır."""
    return [float(nufus.get(il, 1)) for il in iller]
