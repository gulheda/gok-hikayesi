"""Haritanın "imzası": bu haritayı başkalarından ayıran yapılar.

Bir hikâyenin kişisel hissettirmemesinin sebebi genellikle şudur: metin,
aynı Güneş burcundaki herkes için geçerli şeyler söyler. Güneş burcu tek
başına insanlığın on ikide birini tarif eder; hikâyenin kişiye ait olması
için modelin *ender* olana tutunması gerekir.

Bu modül haritadaki yapıları çıkarıp belirginliklerine göre sıralar. Amaç
modele "şunlar herkeste var, şunlar bu haritaya özgü" demek — böylece
anlatı yaygın olanın değil, ayırt edicinin üzerine kurulur.

Belirginlik ÖLÇÜLMÜŞTÜR, tahmin edilmemiştir. Oranlar 2500 rastgele
harita üzerinden sayıldı (bkz. tools/imza-kalibrasyon.py, data/nadirlik.json).

Bu ayrım önemli, çünkü ilk sürümde etiketler elle yazılmıştı ve çoğu
yanlıştı: "açısal noktaya yakınlık" çok ender sanılıyordu, ölçüldüğünde
haritaların %61'inde çıktı. Yaygın bir özelliği ender sanmak, hikâyeyi
milyonlarca kişiye uyan bir şeyin üzerine kurar - yani tam da kaçınılmak
istenen burç yorumunu üretir.

Ölçüm KATEGORİ değil ÖRNEK düzeyindedir: "bir cisim açısal noktaya 8
derece yakın" ayrı, "1 derece yakın" ayrı sayılır.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..astro.aspects import angular_separation
from ..astro.chart import NatalChart, PlacedBody
from ..astro.constants import CORE_BODY_KEYS, SIGN_NAMES_TR, SIGN_RULERS, sign_index
from .desenler import hepsi as desenleri_bul
from .nadirlik import (
    ACI_KADEMELERI,
    ACISAL_KADEMELER,
    ETIKET_COK_ENDER,
    ETIKET_ENDER,
    ETIKET_ORTA,
    ETIKET_YAYGIN,
    Olcum,
    kademe_anahtari,
    olc,
)

# Açısal noktalara (Yükselen, Tepe ve karşıtları) bu kadar yakın bir gök
# cismi haritanın en görünür yapısıdır.
ANGULAR_ORB = 8.0

# Bir açının bu kadar dar olması ender; anlatının omurgası olmaya adaydır.
TIGHT_ASPECT_ORB = 1.0

# Geriye dönük adlar; artık ölçümden gelen etiketlere eşleniyorlar.
BELIRGIN_COK = ETIKET_COK_ENDER
BELIRGIN_ORTA = ETIKET_ENDER
BELIRGIN_YAYGIN = ETIKET_YAYGIN


@dataclass(frozen=True)
class Signature:
    """Haritada bulunan tek bir ayırt edici yapı."""

    key: str
    label: str                    # modele verilecek tek satırlık tanım
    olcum: Olcum                  # ölçülmüş seyreklik
    note: Optional[str] = None    # gerekçe
    ilgili: Tuple[str, ...] = ()  # yapının değindiği gök cismi anahtarları

    # `ilgili` anlatı omurgasını kurmak için: iki yapı aynı cisme
    # değiyorsa aralarında anlatısal bir bağ vardır ve arka arkaya
    # anlatıldıklarında tek bir sahne olurlar. Bu alan olmadan hikâye,
    # birbirine değmeyen ilginç olgular listesine dönüşüyor.

    @property
    def rarity(self) -> str:
        return self.olcum.etiket

    @property
    def weight(self) -> float:
        return self.olcum.agirlik

    @property
    def oran(self) -> Optional[float]:
        return self.olcum.oran

    @property
    def insan_ifadesi(self) -> str:
        return self.olcum.insan_ifadesi


def _core_bodies(chart: NatalChart) -> List[PlacedBody]:
    return [b for b in chart.bodies if b.key in CORE_BODY_KEYS]


def angular_bodies(chart: NatalChart) -> List[Signature]:
    """Yükselen/Tepe noktasına yakın gök cisimleri.

    Doğum saati bilinmiyorsa açısal noktalar yoktur; bu yapı da yoktur.
    """
    if not chart.houses.available or chart.houses.ascendant is None:
        return []

    noktalar = {
        "Yükselen": chart.houses.ascendant,
        "Tepe noktası": chart.houses.midheaven,
        "Batan": (chart.houses.ascendant + 180.0) % 360.0,
        "Dip nokta": (chart.houses.midheaven + 180.0) % 360.0,
    }

    bulunanlar: List[Signature] = []
    for body in _core_bodies(chart):
        for nokta_adi, nokta in noktalar.items():
            if nokta is None:
                continue
            fark = abs((body.longitude - nokta + 180.0) % 360.0 - 180.0)
            if fark > ANGULAR_ORB:
                continue
            # Güneş'in Yükselen'e yakınlığı ayrı bir olgudur: kişi gün
            # doğumunda doğmuş demektir ve ölçümde çok ender çıkıyor.
            taban = ("gun_dogumu" if (body.key == "Sun" and nokta_adi == "Yükselen")
                     else "acisal")
            olcum = olc(kademe_anahtari(taban, fark, ACISAL_KADEMELER))
            ek = ""
            if taban == "gun_dogumu":
                ek = " Bu, kişinin gün doğumunda doğduğu anlamına gelir."
            bulunanlar.append(
                Signature(
                    key="angular",
                    label=(
                        f"{body.name_tr}, {nokta_adi} noktasına {fark:.1f} derece "
                        f"uzaklıkta duruyor ({body.sign_name_tr} "
                        f"{body.degree_in_sign:.1f}°)"
                    ),
                    olcum=olcum,
                    note=(
                        f"Ölçüm: {olcum.insan_ifadesi} görülüyor.{ek}"
                    ),
                    ilgili=(body.key,),
                )
            )
    return bulunanlar


def stelliums(chart: NatalChart) -> List[Signature]:
    """Aynı burçta veya aynı evde toplanmış üç ve daha fazla gök cismi."""
    bulunanlar: List[Signature] = []

    burca_gore: Dict[int, List[PlacedBody]] = {}
    eve_gore: Dict[int, List[PlacedBody]] = {}
    for body in _core_bodies(chart):
        burca_gore.setdefault(body.sign_index, []).append(body)
        if body.house:
            eve_gore.setdefault(body.house, []).append(body)

    for idx, grup in burca_gore.items():
        if len(grup) >= 3:
            adlar = ", ".join(b.name_tr for b in grup)
            olcum = olc(f"yigin_burc_{min(len(grup), 5)}")
            bulunanlar.append(
                Signature(
                    key="stellium_sign",
                    label=(
                        f"{SIGN_NAMES_TR[idx]} burcunda {len(grup)} gök cismi "
                        f"toplanmış: {adlar}"
                    ),
                    olcum=olcum,
                    note=f"Ölçüm: {olcum.insan_ifadesi} görülüyor.",
                    ilgili=tuple(b.key for b in grup),
                )
            )

    for ev, grup in eve_gore.items():
        if len(grup) >= 3:
            adlar = ", ".join(b.name_tr for b in grup)
            tema = grup[0].house_theme_tr or ""
            olcum = olc(f"yigin_ev_{min(len(grup), 5)}")
            bulunanlar.append(
                Signature(
                    key="stellium_house",
                    label=(
                        f"{ev}. evde ({tema}) {len(grup)} gök cismi toplanmış: "
                        f"{adlar}. Haritanın ağırlık merkezi burası."
                    ),
                    olcum=olcum,
                    note=f"Ölçüm: {olcum.insan_ifadesi} görülüyor.",
                    ilgili=tuple(b.key for b in grup),
                )
            )

    return bulunanlar


def tight_aspects(chart: NatalChart) -> List[Signature]:
    """Tam açıya çok yakın bağlantılar."""
    bulunanlar: List[Signature] = []
    for a in chart.aspects:
        if a.orb > TIGHT_ASPECT_ORB:
            continue
        olcum = olc(kademe_anahtari("dar_aci", a.orb, ACI_KADEMELERI))
        bulunanlar.append(
            Signature(
                key="tight_aspect",
                label=(
                    f"{a.name_a_tr} ile {a.name_b_tr} arasındaki {a.type_name_tr} "
                    f"neredeyse tam: sapma yalnızca {a.orb:.2f} derece "
                    f"({a.nature} nitelikte)"
                ),
                olcum=olcum,
                note=f"Ölçüm: {olcum.insan_ifadesi} görülüyor.",
                ilgili=(a.body_a, a.body_b),
            )
        )
    return bulunanlar


def chart_ruler(chart: NatalChart) -> List[Signature]:
    """Yükselen burcun yöneticisi ve o gök cisminin yerleşimi.

    Klasik yorumda haritanın "sahibi" sayılan gök cismi budur; hikâyenin
    başrolü için doğal aday.
    """
    if not chart.houses.available or chart.houses.ascendant is None:
        return []

    asc_idx = sign_index(chart.houses.ascendant)
    yonetici_key = SIGN_RULERS[asc_idx][0]
    yonetici = chart.body(yonetici_key)
    if yonetici is None:
        return []

    ev_bilgisi = (
        f", {yonetici.house}. evde ({yonetici.house_theme_tr})"
        if yonetici.house else ""
    )
    return [
        Signature(
            key="chart_ruler",
            label=(
                f"Yükselen {SIGN_NAMES_TR[asc_idx]} olduğu için haritanın "
                f"yöneticisi {yonetici.name_tr}. Bu gök cismi "
                f"{yonetici.sign_name_tr} {yonetici.degree_in_sign:.1f}°"
                f"{ev_bilgisi} konumunda"
                + (", ve gerileme hareketinde" if yonetici.is_retrograde else "")
                + "."
            ),
            olcum=olc("chart_ruler"),
            note="Her haritada vardır; anlatının başrolü için doğal aday "
                 "ama tek başına ayırt edici değildir.",
            ilgili=(yonetici_key,),
        )
    ]


def element_signature(chart: NatalChart) -> List[Signature]:
    bulunanlar: List[Signature] = []
    eksik = chart.balance.missing_elements
    if eksik:
        olcum = olc("iki_eksik_element" if len(eksik) > 1 else "eksik_element")
        bulunanlar.append(
            Signature(
                key="missing_element",
                label=(
                    "Hiçbir gök cismi şu element(ler)de yerleşmemiş: "
                    + ", ".join(eksik)
                ),
                olcum=olcum,
                note=f"Ölçüm: {olcum.insan_ifadesi} görülüyor. Eksik olan, "
                     "anlatıda aranan şey olarak kullanılabilir.",
            )
        )

    sayilar = chart.balance.elements
    baskin = chart.balance.dominant_element
    if baskin and sayilar.get(baskin, 0) >= 5:
        bulunanlar.append(
            Signature(
                key="dominant_element",
                label=(
                    f"{baskin} elementi {sayilar[baskin]} yerleşimle ezici "
                    "çoğunlukta"
                ),
                olcum=olc("dominant_element"),
            )
        )
    return bulunanlar


def retrograde_signature(chart: NatalChart) -> List[Signature]:
    """Gerileme hareketindeki gök cisimleri.

    Dış gezegenler yılın büyük bölümünde gerilemededir; bu yüzden yalnızca
    iç gezegenlerin (Merkür, Venüs, Mars) gerilemesi ayırt edicidir ve
    ikisi ayrı ayrı raporlanır.
    """
    ic_gezegenler = {"Mercury", "Venus", "Mars"}
    ic_gerileyen = [
        b for b in _core_bodies(chart)
        if b.is_retrograde and b.key in ic_gezegenler
    ]
    dis_gerileyen = [
        b for b in _core_bodies(chart)
        if b.is_retrograde and b.key not in ic_gezegenler
    ]

    bulunanlar: List[Signature] = []
    if ic_gerileyen:
        olcum = olc("ic_gezegen_gerileme")
        bulunanlar.append(
            Signature(
                key="inner_retrograde",
                label=(
                    "Gerileme hareketindeki iç gezegen(ler): "
                    + ", ".join(f"{b.name_tr} ({b.sign_name_tr})" for b in ic_gerileyen)
                ),
                olcum=olcum,
                note=f"Ölçüm: {olcum.insan_ifadesi} görülüyor.",
                ilgili=tuple(b.key for b in ic_gerileyen),
            )
        )
    if dis_gerileyen:
        bulunanlar.append(
            Signature(
                key="outer_retrograde",
                label=(
                    "Gerileme hareketindeki dış gezegen(ler): "
                    + ", ".join(b.name_tr for b in dis_gerileyen)
                ),
                olcum=Olcum("outer_retrograde", 0.835),
                ilgili=tuple(b.key for b in dis_gerileyen),
                note=(
                    "Dış gezegenler yılın yaklaşık yarısında gerilemededir; "
                    "bunu ayırt edici bir özellik gibi anlatma."
                ),
            )
        )
    return bulunanlar


def unaspected_bodies(chart: NatalChart) -> List[Signature]:
    """Hiçbir açı yapmayan gök cisimleri — haritanın yalnızları."""
    bagli = {a.body_a for a in chart.aspects} | {a.body_b for a in chart.aspects}
    yalnizlar = [b for b in _core_bodies(chart) if b.key not in bagli]
    if not yalnizlar:
        return []
    olcum = olc("acisiz_cisim")
    return [
        Signature(
            key="unaspected",
            label=(
                "Hiçbir açı yapmayan gök cismi/cisimleri: "
                + ", ".join(f"{b.name_tr} ({b.sign_name_tr})" for b in yalnizlar)
            ),
            olcum=olcum,
            note=f"Ölçüm: {olcum.insan_ifadesi} görülüyor. Haritanın geri "
                 "kalanıyla bağlantısız; anlatıda yalnız bir figür.",
            ilgili=tuple(b.key for b in yalnizlar),
        )
    ]


def patterns(chart: NatalChart) -> List[Signature]:
    """Geometrik ve klasik desenleri imzaya çevirir.

    Bunlar tek bir yerleşim değil, cisimler arasındaki ilişkiden doğan
    yapılardır: tutulma, T-kare, büyük üçgen, kâse şekli, Güneş'e
    gömülülük, kendi burcunda duran gezegen. Anlatı değerleri yüksek
    olduğu için ayrı toplanıyorlar - bir gezegenin nerede durduğu bir
    cümledir, üç gezegenin bir üçgen kurması bir sahnedir.
    """
    bulunanlar: List[Signature] = []
    for desen in desenleri_bul(chart):
        olcum = olc(desen.anahtar)
        bulunanlar.append(
            Signature(
                key=desen.anahtar,
                label=desen.tanim,
                olcum=olcum,
                note=f"Ölçüm: {olcum.insan_ifadesi} görülüyor.",
                ilgili=desen.ilgili,
            )
        )
    return bulunanlar


def common_traits(chart: NatalChart) -> List[str]:
    """Yaygın olduğu için üzerine hikâye kurulmaması gereken özellikler."""
    satirlar: List[str] = []
    gunes = chart.body("Sun")
    if gunes:
        satirlar.append(
            f"Güneş'in {gunes.sign_name_tr} burcunda olması: insanlığın "
            "yaklaşık on ikide biriyle paylaşılan bir özellik."
        )
    ay = chart.body("Moon")
    if ay:
        satirlar.append(
            f"Ay'ın {ay.sign_name_tr} burcunda olması: yine yaklaşık on ikide bir."
        )
    return satirlar


def collect(chart: NatalChart) -> List[Signature]:
    """Tüm imzaları toplayıp belirginlik ağırlığına göre sıralar."""
    hepsi: List[Signature] = []
    for uretici in (
        patterns,
        angular_bodies,
        unaspected_bodies,
        tight_aspects,
        chart_ruler,
        retrograde_signature,
        stelliums,
        element_signature,
    ):
        hepsi.extend(uretici(chart))
    hepsi.sort(key=lambda s: s.weight, reverse=True)
    return hepsi
