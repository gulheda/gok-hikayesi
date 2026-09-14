"""Anlatı omurgası: hangi yapılar birlikte iyi hikâye eder.

`signature.py` haritadaki yapıları seyrekliğe göre sıralıyor. Ama sıralı
bir liste hikâye değildir. Bir metin, ilginç olgular arka arkaya
dizildiğinde değil, olgular BİRBİRİNE DEĞDİĞİNDE hikâye olur.

Somut örnek: bir haritada "Güneş yeni doğmuştu", "Neptün de yeni
doğmuştu" ve "Neptün Güneş'in ışığında görünmüyordu" yapıları vardı.
Üçü de aynı iki cisme değiyor, dolayısıyla arka arkaya anlatıldıklarında
tek bir sahne oluyorlar: "ikiniz aynı eşikten geçtiniz ve biriniz
görünmüyordu." Aynı haritadaki dördüncü bir yapı (Venüs ile Plüton'un
karesi) daha seyrek olsa bile o sahneye ait değil, çünkü hiçbir ortak
cismi yok.

Bu modül yapıları bir çizge olarak ele alıyor: düğümler yapılar, kenarlar
ortak gök cisimleri. Sonra seyreklik ile bağlılığı birlikte gözeten bir
yol seçiyor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..astro.chart import NatalChart
from .signature import Signature, collect

# Omurgada kaç durak olacağı. Üçten az olursa metin tek bir yapıya
# yaslanıp tekrara düşüyor; beşten fazlası bir masalın taşıyabileceğinden
# çok ve sahneler yüzeyselleşiyor.
VARSAYILAN_UZUNLUK = 4

# Bir önceki durakla ortak cismi olan aday bu kadar avantaj alır.
# Değer seyreklik ağırlığıyla aynı ölçekte (bkz. nadirlik.Olcum.agirlik):
# ~%1 seyreklik 40 puan, ~%50 seyreklik 6 puan getiriyor. 18 puanlık bağ
# bonusu, "biraz daha yaygın ama zincire ait" bir yapıyı "daha seyrek ama
# kopuk" bir yapıya tercih ettirecek kadar büyük, seyrekliği tamamen
# bastıracak kadar değil.
ZINCIR_BONUSU = 18.0
UZAK_BAG_BONUSU = 7.0

# Yaygın yapılar omurgaya alınmaz: hikâyeyi milyonlarca kişide bulunan
# bir şeyin üzerine kurmak, kişiselleştirmenin tam tersidir.
YAYGIN_ESIGI = 0.55


@dataclass
class Durak:
    """Omurgadaki tek bir durak."""

    imza: Signature
    ortak_cisimler: Tuple[str, ...] = ()   # bir önceki durakla paylaşılanlar

    @property
    def zincire_bagli(self) -> bool:
        return bool(self.ortak_cisimler)


@dataclass
class Omurga:
    duraklar: List[Durak] = field(default_factory=list)
    disarida_kalanlar: List[Signature] = field(default_factory=list)

    @property
    def bos(self) -> bool:
        return not self.duraklar

    @property
    def zincir_orani(self) -> float:
        """Duraklardan kaçı bir öncekine bağlı.

        1.0 ise metin tek bir sahne gibi akar; 0.0 ise birbirine değmeyen
        olgular listesi olur.
        """
        if len(self.duraklar) < 2:
            return 0.0
        bagli = sum(1 for d in self.duraklar[1:] if d.zincire_bagli)
        return bagli / (len(self.duraklar) - 1)

    def brifing_satirlari(self, cisim_adlari: Dict[str, str]) -> List[str]:
        """Omurgayı modele anlatan satırlar."""
        if self.bos:
            return []

        satirlar = [
            "ANLATI OMURGASI — yolculuğun durakları, bu sırayla. Bunlar "
            "haritanın hem en seyrek hem birbirine en bağlı yapıları; "
            "hikâyeyi bu zincir üzerine kur."
        ]
        for i, durak in enumerate(self.duraklar, start=1):
            oran = (f"%{durak.imza.oran * 100:.1f}"
                    if durak.imza.oran is not None else "ölçülmedi")
            satirlar.append(f"{i}. [{oran}] {durak.imza.label}")
            if durak.ortak_cisimler:
                adlar = ", ".join(
                    cisim_adlari.get(k, k) for k in durak.ortak_cisimler
                )
                satirlar.append(
                    f"   ↳ Bir önceki durakla ortak: {adlar}. Bu ikisini ayrı "
                    "sahneler gibi değil, aynı sahnenin devamı gibi anlat."
                )
        return satirlar


def _paylasilan(a: Signature, b: Signature) -> Tuple[str, ...]:
    return tuple(sorted(set(a.ilgili) & set(b.ilgili)))


def kur(
    chart: NatalChart,
    uzunluk: int = VARSAYILAN_UZUNLUK,
    imzalar: Optional[List[Signature]] = None,
) -> Omurga:
    """Haritadan anlatı omurgasını seçer.

    Açgözlü bir seçim: en seyrek yapıyla başlar, sonra her adımda
    "seyreklik + zincire bağlılık" toplamı en yüksek adayı ekler.
    En iyi yolu bulmayı garanti etmez; dört durak için tam arama da
    yapılabilirdi ama aradaki fark, hikâye kalitesinde karşılığı olmayan
    bir karmaşıklık getirirdi.
    """
    adaylar = [
        i for i in (imzalar if imzalar is not None else collect(chart))
        if i.oran is None or i.oran < YAYGIN_ESIGI
    ]
    if not adaylar:
        return Omurga()

    # `collect` zaten seyreklikten sıralı geliyor; ilki açılış olur.
    secilen: List[Durak] = [Durak(adaylar[0])]
    kalan = adaylar[1:]
    kullanilan_cisimler: Set[str] = set(adaylar[0].ilgili)

    while len(secilen) < uzunluk and kalan:
        son = secilen[-1].imza
        en_iyi, en_iyi_puan, en_iyi_ortak = None, float("-inf"), ()

        for aday in kalan:
            ortak_son = _paylasilan(son, aday)
            ortak_hepsi = set(aday.ilgili) & kullanilan_cisimler

            puan = aday.olcum.agirlik
            if ortak_son:
                puan += ZINCIR_BONUSU
            elif ortak_hepsi:
                puan += UZAK_BAG_BONUSU

            if puan > en_iyi_puan:
                en_iyi, en_iyi_puan, en_iyi_ortak = aday, puan, ortak_son

        if en_iyi is None:
            break
        secilen.append(Durak(en_iyi, ortak_cisimler=en_iyi_ortak))
        kullanilan_cisimler.update(en_iyi.ilgili)
        kalan = [a for a in kalan if a is not en_iyi]

    return Omurga(duraklar=secilen, disarida_kalanlar=kalan)
