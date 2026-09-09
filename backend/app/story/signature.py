"""Haritanın "imzası": bu haritayı başkalarından ayıran yapılar.

Bir hikâyenin kişisel hissettirmemesinin sebebi genellikle şudur: metin,
aynı Güneş burcundaki herkes için geçerli şeyler söyler. Güneş burcu tek
başına insanlığın on ikide birini tarif eder; hikâyenin kişiye ait olması
için modelin *ender* olana tutunması gerekir.

Bu modül haritadaki yapıları çıkarıp belirginliklerine göre sıralar. Amaç
modele "şunlar herkeste var, şunlar bu haritaya özgü" demek — böylece
anlatı yaygın olanın değil, ayırt edicinin üzerine kurulur.

Belirginlik etiketleri niteldir. Kesin yüzdeler vermiyoruz çünkü gerçek
dağılımlar doğum tarihi dağılımına, ev sistemine ve orb seçimine bağlıdır;
uydurma bir istatistik, yokluğundan daha kötüdür.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..astro.chart import NatalChart, PlacedBody
from ..astro.constants import CORE_BODY_KEYS, SIGN_NAMES_TR, SIGN_RULERS, sign_index

# Açısal noktalara (Yükselen, Tepe ve karşıtları) bu kadar yakın bir gök
# cismi haritanın en görünür yapısıdır.
ANGULAR_ORB = 8.0

# Bir açının bu kadar dar olması ender; anlatının omurgası olmaya adaydır.
TIGHT_ASPECT_ORB = 1.0

BELIRGIN_COK = "çok belirgin"
BELIRGIN_ORTA = "belirgin"
BELIRGIN_YAYGIN = "yaygın"


@dataclass(frozen=True)
class Signature:
    """Haritada bulunan tek bir ayırt edici yapı."""

    key: str
    label: str          # modele verilecek tek satırlık tanım
    rarity: str
    weight: float       # sıralama için; büyük olan önce
    note: Optional[str] = None   # neden ender/yaygın olduğunun kısa gerekçesi


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
            cok_yakin = fark <= 3.0
            bulunanlar.append(
                Signature(
                    key="angular",
                    label=(
                        f"{body.name_tr}, {nokta_adi} noktasına {fark:.1f} derece "
                        f"uzaklıkta duruyor ({body.sign_name_tr} "
                        f"{body.degree_in_sign:.1f}°)"
                    ),
                    rarity=BELIRGIN_COK if cok_yakin else BELIRGIN_ORTA,
                    weight=100.0 - fark,
                    note=(
                        "Açısal noktaya bu kadar yakın bir gök cismi haritanın "
                        "en görünür yapısıdır; çoğu haritada bulunmaz."
                    ),
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
            bulunanlar.append(
                Signature(
                    key="stellium_sign",
                    label=(
                        f"{SIGN_NAMES_TR[idx]} burcunda {len(grup)} gök cismi "
                        f"toplanmış: {adlar}"
                    ),
                    rarity=BELIRGIN_COK if len(grup) >= 4 else BELIRGIN_ORTA,
                    weight=60.0 + len(grup) * 5,
                    note="Tek bir burçta bu yoğunlukta toplanma seyrektir.",
                )
            )

    for ev, grup in eve_gore.items():
        if len(grup) >= 3:
            adlar = ", ".join(b.name_tr for b in grup)
            tema = grup[0].house_theme_tr or ""
            bulunanlar.append(
                Signature(
                    key="stellium_house",
                    label=(
                        f"{ev}. evde ({tema}) {len(grup)} gök cismi toplanmış: "
                        f"{adlar}. Haritanın ağırlık merkezi burası."
                    ),
                    rarity=BELIRGIN_COK if len(grup) >= 4 else BELIRGIN_ORTA,
                    weight=65.0 + len(grup) * 5,
                    note="Hayatın tek bir alanında bu yoğunlukta toplanma seyrektir.",
                )
            )

    return bulunanlar


def tight_aspects(chart: NatalChart) -> List[Signature]:
    """Tam açıya çok yakın bağlantılar."""
    bulunanlar: List[Signature] = []
    for a in chart.aspects:
        if a.orb > TIGHT_ASPECT_ORB:
            continue
        bulunanlar.append(
            Signature(
                key="tight_aspect",
                label=(
                    f"{a.name_a_tr} ile {a.name_b_tr} arasındaki {a.type_name_tr} "
                    f"neredeyse tam: sapma yalnızca {a.orb:.2f} derece "
                    f"({a.nature} nitelikte)"
                ),
                rarity=BELIRGIN_COK if a.orb <= 0.5 else BELIRGIN_ORTA,
                weight=90.0 - a.orb * 10,
                note="Bu kadar dar bir açı seyrektir ve anlatının omurgası olabilir.",
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
            rarity=BELIRGIN_ORTA,
            weight=80.0,
            note="Anlatının başrolü için doğal aday.",
        )
    ]


def element_signature(chart: NatalChart) -> List[Signature]:
    bulunanlar: List[Signature] = []
    eksik = chart.balance.missing_elements
    if eksik:
        bulunanlar.append(
            Signature(
                key="missing_element",
                label=(
                    "Hiçbir gök cismi şu element(ler)de yerleşmemiş: "
                    + ", ".join(eksik)
                ),
                rarity=BELIRGIN_ORTA,
                weight=70.0,
                note="Eksik olan, anlatıda aranan/olmayan şey olarak kullanılabilir.",
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
                rarity=BELIRGIN_ORTA,
                weight=55.0,
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
        bulunanlar.append(
            Signature(
                key="inner_retrograde",
                label=(
                    "Gerileme hareketindeki iç gezegen(ler): "
                    + ", ".join(f"{b.name_tr} ({b.sign_name_tr})" for b in ic_gerileyen)
                ),
                rarity=BELIRGIN_COK,
                weight=75.0,
                note="İç gezegenlerin gerilemesi seyrektir, dış gezegenlerinki değil.",
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
                rarity=BELIRGIN_YAYGIN,
                weight=10.0,
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
    return [
        Signature(
            key="unaspected",
            label=(
                "Hiçbir açı yapmayan gök cismi/cisimleri: "
                + ", ".join(f"{b.name_tr} ({b.sign_name_tr})" for b in yalnizlar)
            ),
            rarity=BELIRGIN_COK,
            weight=85.0,
            note="Haritanın geri kalanıyla bağlantısız; anlatıda yalnız bir figür.",
        )
    ]


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
