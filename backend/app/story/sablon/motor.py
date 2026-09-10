"""Şablon hikâye motoru: dil modeli çağırmadan metin üretir.

Tasarımın iki ilkesi var.

**Birincisi: iskelet haritaya göre değişir.** Sabit bir bölüm dizisi
kullanmak, iki farklı kullanıcının hikâyesini yan yana koyduğunda aynı
hamleleri göstermek demektir - ki "bu hikâye sana özel" iddiasını en hızlı
çürüten şey budur. Bunun yerine bölümler haritada BULUNAN yapılara göre
seçiliyor: yığınlaşması olmayan bir haritada "meclis" bölümü hiç yok,
açısız gök cismi olan bir haritada "yalnız" bölümü var.

**İkincisi: kişi yürür.** Bölümler birer durak; kişi ülkeye girer,
kapıyı açar, karşılaşır, arar. Masalın baş kahramanı edilgen olamaz -
ona bir şeyler olmaz, o bir şeyler yapar. Buna karşılık ÖVÜLMEZ de:
"sen cesursun" cümlesi hem genellik testinden geçemez hem de baş
kahramanlığı yapmaktan değil sıfattan türetir.

**Üçüncüsü: rastgelelik haritadan türetilir.** Aynı harita her zaman aynı
hikâyeyi verir (kişi ikinci kez baktığında metin değişmemeli), ama farklı
haritalar farklı ifadeler seçer.

Bu motorun bilinen sınırı: parça havuzu sonlu. Yeterince çok hikâye yan
yana konursa tekrar eden kalıplar görünür hale gelir. Dil modeli her
seferinde gerçekten yeniden kurar; bu motor kurmaz, birleştirir.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from ...astro.chart import NatalChart
from ..signature import Signature, collect as imzalari_topla
from . import gokyuzu
from .turkce import (
    belirtme,
    bulunma,
    de_baglaci,
    gecmis_kopula,
    gunun_vakti,
    iyelik3,
    mekan_bulunma,
    sayi_sifat,
    tarih_yazi,
)
from .sozluk import (
    ACI_ILISKISI,
    ACISAL_NOKTA_ADI,
    EKSIK_ELEMENT,
    ELEMENT_MADDESI,
    KARAKTERLER,
    KAPANISLAR,
    MEKANLAR,
)

SABLON_SURUMU = "2.0.0"


@dataclass
class Baglam:
    """Bölüm yazarlarının paylaştığı durum."""

    chart: NatalChart
    ad: Optional[str]
    rastgele: random.Random
    imzalar: Dict[str, List[Signature]]

    # Olgusal bölümde hangi gök cisimleri hakkında ne anlatıldığının
    # defteri. Sembolik bölümler aynı olguyu ikinci kez anlatmasın diye:
    # bir hikâyede aynı şeyin iki kez söylenmesi, metnin parçalardan
    # birleştirildiğini ele veren en belirgin işarettir.
    anlatilanlar: set = None

    def __post_init__(self):
        if self.anlatilanlar is None:
            self.anlatilanlar = set()

    def sec(self, secenekler: List[str]) -> str:
        return self.rastgele.choice(secenekler)

    def karakter(self, anahtar: str) -> str:
        k = KARAKTERLER.get(anahtar)
        return k.unvan if k else anahtar

    def olcumle(self, ad: str) -> str:
        """Bir gök cismini ölçümüyle birlikte anar.

        Masalın ölçümden KOPMAMASI için var. Karakterden her söz edildiğinde
        gerçek konumu da anılırsa okuyucu kendi gökyüzüyle bağını
        kaybetmiyor; aksi hâlde ikinci hareket bağımsız bir masala dönüşüyor
        ve ürünün tek iddiası ("bu senin gökyüzün") görünmez oluyor.
        """
        cisim = next((c for c in self.chart.bodies if c.name_tr == ad), None)
        if cisim is None:
            return ad
        derece = int(cisim.degree_in_sign)
        dakika = int(round((cisim.degree_in_sign - derece) * 60))
        if dakika == 60:
            derece, dakika = derece + 1, 0
        return f"{ad} — {cisim.sign_name_tr} burcunun {derece} derece {dakika} dakikası —"

    @property
    def yer_kisa(self) -> str:
        return self.chart.birth.place_name.split(",")[0].strip()

    def hitapla(self, devam: str) -> str:
        """Cümleyi kişiye seslenerek ya da doğrudan başlatır.

        Ad yoksa devam cümlesi başa geçtiği için büyük harfle başlamalı;
        düz birleştirme küçük harfle başlayan bir cümle üretiyordu.
        """
        if self.ad:
            return f"{self.ad}, {devam}"
        return devam[0].upper() + devam[1:] if devam else devam


def _tohum(chart: NatalChart) -> int:
    """Haritadan türetilen sabit tohum.

    Julian Day ve koordinatlar birlikte kullanılıyor; aynı anda farklı
    yerlerde doğan iki kişi farklı ifadeler alsın diye.
    """
    return (
        int(chart.instant.julian_day_ut * 100_000)
        ^ int(abs(chart.birth.latitude) * 10_000)
        ^ int(abs(chart.birth.longitude) * 10_000)
    )


def _imzalari_gruplat(chart: NatalChart) -> Dict[str, List[Signature]]:
    gruplar: Dict[str, List[Signature]] = {}
    for imza in imzalari_topla(chart):
        gruplar.setdefault(imza.key, []).append(imza)
    return gruplar


# --------------------------------------------------------------------------
# Bölümler
# --------------------------------------------------------------------------

def bolum_gokyuzu(b: Baglam) -> List[str]:
    """Olgusal açılış. Hiçbir sembolik anlam yok, hepsi doğrulanabilir."""
    ch = b.chart
    i = ch.instant

    if ch.birth.time_known:
        vakit = gunun_vakti(ch.birth.birth_time.hour)
        yaz = " O yıl yaz saati uygulanıyordu." if i.is_dst else ""
        acilis = (
            f"{tarih_yazi(ch.birth.birth_date)} {vakit}, {b.yer_kisa} "
            f"üzerinde. Yerel saat {ch.birth.birth_time.strftime('%H:%M')}, "
            f"evrensel zamanda {i.utc.strftime('%H:%M')}.{yaz}"
        )
    else:
        acilis = (
            f"{tarih_yazi(ch.birth.birth_date)}, {b.yer_kisa} üzerinde. "
            "Doğum saati bilinmiyor; bu yüzden gökyüzünün o gün nasıl "
            "döndüğü değil, nerede durduğu anlatılabilir."
        )

    olgular = gokyuzu.topla(ch, en_fazla=5)
    for olgu in olgular:
        b.anlatilanlar.update(olgu.ilgili)

    cumleler = [o.cumle for o in olgular]
    paragraflar = [acilis + " " + " ".join(cumleler[:2])]
    if len(cumleler) > 2:
        paragraflar.append(" ".join(cumleler[2:]))
    paragraflar.append(
        "Buraya kadarı ölçümdür; her satırı başka bir efemeris yazılımıyla "
        "doğrulanabilir. Bundan sonrası değildir. Ama anlatılacak olan, "
        "başka bir gökyüzü değil: aynı diziliş, başka türlü bakılmış hâli."
    )
    return paragraflar


def bolum_ulke(b: Baglam) -> List[str]:
    """Ülkenin maddesi: element dengesi ve eksik element."""
    denge = b.chart.balance
    baskin = denge.dominant_element
    madde, nitelik = ELEMENT_MADDESI.get(baskin or "Su", ("akış", ""))

    sayim = ", ".join(f"{k.lower()} {v}" for k, v in denge.elements.items())
    ilk = b.hitapla(
        f"şimdi o on gök cismini bir ülkenin sakinleri say; durdukları "
        f"burçları da o ülkenin bölgeleri. Sen o ülkeye girdin ve eşiği "
        f"geçtikten sonra geri dönmedin. Sayım yapıldığında {sayim} "
        f"çıkıyordu, yani ülkenin ağırlığı {madde} tarafındaydı; {madde} "
        f"{nitelik}."
    )

    paragraflar = [ilk]
    for eksik in denge.missing_elements:
        secenekler = EKSIK_ELEMENT.get(eksik)
        if secenekler:
            paragraflar.append(
                b.sec(secenekler) + " Yolun geri kalanında onu aradın."
            )
    return paragraflar


def bolum_kapi(b: Baglam) -> List[str]:
    """Açısal noktalara yakın cisimler: dışarıdan ilk görünen."""
    acisal = b.imzalar.get("angular", [])
    if not acisal:
        return []

    # En yakın iki cismi al; hangi noktaya yakın olduklarını ayrıştır.
    satirlar: List[str] = []
    kullanilan = []
    for imza in acisal[:2]:
        for nokta_adi, kurgu_adi in ACISAL_NOKTA_ADI.items():
            if nokta_adi in imza.label:
                kullanilan.append((imza, kurgu_adi))
                break

    if not kullanilan:
        return []

    imza, kurgu = kullanilan[0]
    cisim_adi = imza.label.split(",")[0]
    karakter = KARAKTERLER.get(
        next((k for k, v in KARAKTERLER.items() if v.unvan == cisim_adi), ""),
        None,
    )
    rol = karakter.rol if karakter else "orada duran kişi"

    # Ölçüm cümlesini masala taşı: bu cismin ufka olan gerçek uzaklığı
    # zaten olgusal bölümde geçti, burada aynı görüntüye geri dönülüyor.
    derece = ""
    if "uzaklıkta" in imza.label:
        derece = imza.label.split("noktasına")[1].split("uzaklıkta")[0].strip()
        derece = derece.replace(".", ",")   # Türkçe ondalık ayracı

    satirlar.append(
        f"İlk durağın {kurgu} oldu. Onu sen açtın; içeriden açan olmadı. "
        f"{bulunma(kurgu).capitalize()} {b.olcumle(cisim_adi)} bekliyordu"
        + (f", ufuktan yalnızca {derece} ötede" if derece else "")
        + f": {rol}. Sabah onu gökyüzünde görebilseydin, tam orada duruyordu."
    )

    if len(kullanilan) > 1:
        ikinci_adi = kullanilan[1][0].label.split(",")[0]
        satirlar.append(
            f"Yalnız değildi. {ikinci_adi} {de_baglaci(ikinci_adi)} oradaydı, "
            "birkaç adım ötede. İkisinin arasından geçtin. Hangisinin sana "
            "yol gösterdiğini, hangisinin yalnızca baktığını sonradan da "
            "ayıramadın."
        )
    else:
        satirlar.append(
            f"{cisim_adi} yol gösterdi ama peşinden gitmedi. Ülkeye tek "
            "başına girdin."
        )
    return satirlar


def bolum_meclis(b: Baglam) -> List[str]:
    """Yığınlaşma: ülkenin ağırlık merkezi."""
    yiginlar = b.imzalar.get("stellium_house", []) or b.imzalar.get("stellium_sign", [])
    if not yiginlar:
        return []

    imza = yiginlar[0]
    # İmza etiketinden gök cisimlerini çıkar.
    if ":" in imza.label:
        ham = imza.label.split(":", 1)[1]
        # İmza etiketi anlatıya ait olmayan bir cümle taşıyabiliyor
        # ("Haritanın ağırlık merkezi burası."); ilk cümleden sonrası atılır.
        ham = ham.split(".")[0]
        adlar = [a.strip() for a in ham.split(",")]
    else:
        adlar = []
    adlar = [a for a in adlar if a][:4]
    if len(adlar) < 3:
        return []

    # İmza etiketi "11. evde (topluluk, gelecek tasavvuru, dostluk) ..."
    # biçiminde; ev temasını parantez içinden alıyoruz.
    tema = ""
    if "evde (" in imza.label:
        tema = imza.label.split("evde (")[1].split(")")[0].split(",")[0].strip()

    yer_tarifi = (
        f"{tema} bölgesinde" if tema else "tek bir bölgede"
    )
    satirlar = [
        f"Yürüdün ve ülkenin ağırlık merkezine vardın; kapıda değildi. "
        f"{yer_tarifi.capitalize()} "
        f"{sayi_sifat(len(adlar))} kişi toplanmıştı: {', '.join(adlar)}. "
        "Gökyüzünde de öyleydiler: o sabah dördü birden, göğün aynı dar "
        "diliminde duruyordu. Kapıyı çalmadan girdin ve konuşma kesilmedi."
    ]

    # Yığındaki cisimlerden birinin görünmez olması en güçlü ayrıntıdır.
    gunes = b.chart.body("Sun")
    if gunes:
        from ...astro.aspects import angular_separation

        for body in b.chart.bodies:
            # Olgusal bölümde bu cismin görünmezliği zaten anlatıldıysa
            # burada tekrarlamıyoruz.
            if body.key in b.anlatilanlar:
                continue
            if body.name_tr in adlar and body.key != "Sun":
                ayrim = angular_separation(body.longitude, gunes.longitude)
                if ayrim <= gokyuzu.GORUNMEZLIK_SINIRI:
                    k = KARAKTERLER.get(body.key)
                    eylem = k.fiil_anlati if k else "karar verirdi"
                    satirlar.append(
                        f"İçlerinden birini göremedin: {body.name_tr}. "
                        "Güneş'e fazla yakın oturmuştu ve ışık onu yutuyordu. "
                        f"Ağırlığını hissettin, {eylem}; ama yüzünü hiç "
                        "görmedin. Odadan çıkarken orada olup olmadığını "
                        "sordun ve kimse cevap vermedi."
                    )
                    break
    return satirlar


def bolum_yonetici(b: Baglam) -> List[str]:
    """Haritanın yöneticisi: ülkeyi kimin yönettiği."""
    yon = b.imzalar.get("chart_ruler", [])
    if not yon:
        return []

    etiket = yon[0].label
    # "haritanın yöneticisi X. Bu gök cismi ..." kalıbından adı çıkar.
    if "yöneticisi " not in etiket:
        return []
    ad = etiket.split("yöneticisi ")[1].split(".")[0].strip()
    anahtar = next((k for k, v in KARAKTERLER.items() if v.unvan == ad), None)
    if not anahtar:
        return []

    body = b.chart.body(anahtar)
    if not body:
        return []

    mekan = MEKANLAR.get(body.sign_index)
    if not mekan:
        return []
    k = KARAKTERLER[anahtar]
    nerede = mekan_bulunma(mekan.ad, mekan.iyelikli)
    return [
        f"Ülkeyi yönetenin {ad} olduğunu söylediler; ülkenin kapısı onun "
        f"işaretini taşıyordu. Onu aramaya gittin. Gökyüzünde "
        f"{body.sign_name_tr} burcunun {int(body.degree_in_sign)}. "
        f"derecesindeydi; ülkede bunun karşılığı "
        f"{nerede} olmaktı — {mekan.nitelik} bir yer. "
        f"Ülkeyi oradan, uzaktan {k.fiil_anlati}. Neden kapıda durmadığını "
        "sorduğunda, kapının kendisini görmediğini söyledi."
    ]


def bolum_bag(b: Baglam) -> List[str]:
    """En dar açı: ülkedeki en kesin şey."""
    dar = b.imzalar.get("tight_aspect", [])
    if not dar:
        return []

    # En dar açıyı haritadan doğrudan al; etiket ayrıştırmaya gerek yok.
    en_dar = min(b.chart.aspects, key=lambda a: a.orb) if b.chart.aspects else None
    if not en_dar or en_dar.orb > 1.0:
        return []

    kalip = b.sec(ACI_ILISKISI.get(en_dar.type_key, ACI_ILISKISI["conjunction"]))
    iliski = kalip.format(a=en_dar.name_a_tr, b=en_dar.name_b_tr)
    sapma = (
        "yarım dereceden azdı"
        if en_dar.orb < 0.5
        else f"{en_dar.orb:.2f} dereceydi"
    )
    a_cisim = next((c for c in b.chart.bodies if c.name_tr == en_dar.name_a_tr), None)
    b_cisim = next((c for c in b.chart.bodies if c.name_tr == en_dar.name_b_tr), None)
    konumlar = ""
    if a_cisim and b_cisim:
        konumlar = (
            f" Biri {a_cisim.sign_name_tr} burcunun "
            f"{int(a_cisim.degree_in_sign)}. derecesinde, öteki "
            f"{b_cisim.sign_name_tr} burcunun "
            f"{int(b_cisim.degree_in_sign)}. derecesinde duruyordu."
        )
    return [
        f"Ülkeden geçen dümdüz bir yol vardı ve o yolu yürüdün: {iliski}."
        + konumlar
        + f" Tam açıdan sapma {sapma}; ülkedeki hiçbir şey bu kadar düzgün "
        "değildi. Yolun iki ucu da yerinden kımıldamadığı için yürümek "
        "kolaydı — zor olan, nereye gittiğini bilmemekti."
    ]


def bolum_yalniz(b: Baglam) -> List[str]:
    """Hiç açı yapmayan gök cismi: ülkenin yalnızı."""
    yalniz = b.imzalar.get("unaspected", [])
    if not yalniz:
        return []

    adlar = [a.strip() for a in yalniz[0].label.split(":")[1].split(",")]
    ad = adlar[0].split("(")[0].strip()
    anahtar = next((k for k, v in KARAKTERLER.items() if v.unvan == ad), None)
    k = KARAKTERLER.get(anahtar or "", None)
    if not k:
        return []
    return [
        f"Yolun kenarında birine rastladın: {ad}. Ülkenin geri kalanıyla "
        f"hiçbir bağı yoktu; ne bir ittifakı, ne bir çekişmesi. "
        f"{k.yalnizken.capitalize()}. Yanına oturdun ve bir şey sormadın. "
        "Ülkede onunla konuşan ilk kişi sendin."
    ]


def bolum_geri(b: Baglam) -> List[str]:
    """Gerileyen iç gezegen — ender olan tek gerileme türü."""
    ic = b.imzalar.get("inner_retrograde", [])
    if not ic:
        return []

    parca = ic[0].label.split(":")[1].strip()
    ad = parca.split("(")[0].strip()
    anahtar = next((k for k, v in KARAKTERLER.items() if v.unvan == ad), None)
    k = KARAKTERLER.get(anahtar or "", None)
    if not k or not k.gerilerken:
        return []
    return [
        f"Bir de {ad} vardı ve sen ona yaklaştıkça o uzaklaşıyordu. Yüzü "
        f"ileriye dönüktü ama adımları geriye gidiyordu: {k.gerilerken}. "
        "Sebebini sormaya kalktığında bir adım daha geriledi. Peşinden "
        "gitmedin; ülkede kovalanmayı istemeyen birinin olduğunu öğrendin."
    ]


def bolum_kapanis(b: Baglam) -> List[str]:
    """Varış. Masal biter ama sonuçlanmaz; kapanış hüküm değil, sahnedir."""
    eksik = b.chart.balance.missing_elements
    if eksik:
        kapanis = (
            f"Aradığın şeyi ülkede bulamadın. {eksik[0]} hiçbir yerde yoktu "
            "ve olmayacaktı. Çıkarken, onu içeri kendinin getirmiş olduğunu "
            "fark ettin."
        )
    else:
        kapanis = b.sec(KAPANISLAR).format(yer=b.yer_kisa)
    return [kapanis]


# Bölümlerin sırası ve hangi imzaya bağlı oldukları. Sıra sabit ama
# BÖLÜMLERİN VARLIĞI haritaya bağlı: yığınlaşması olmayan bir haritada
# "meclis" hiç yazılmaz.
BOLUM_SIRASI: List[Callable[[Baglam], List[str]]] = [
    bolum_gokyuzu,
    bolum_ulke,
    bolum_kapi,
    bolum_meclis,
    bolum_yonetici,
    bolum_bag,
    bolum_yalniz,
    bolum_geri,
    bolum_kapanis,
]


def _baslik(b: Baglam) -> str:
    """Başlığı haritanın en belirgin yapısından türetir."""
    denge = b.chart.balance
    if denge.missing_elements:
        eksik = denge.missing_elements[0]
        # "Toprak" + belirtme -> "Toprağı"; düz birleştirme "Topraki" verirdi.
        return f"{belirtme(eksik)} Olmayan Ülke"
    if b.imzalar.get("angular"):
        return "Kapıda Duranlar"
    if b.imzalar.get("stellium_house") or b.imzalar.get("stellium_sign"):
        return "Tek Bir Bölgede Toplananlar"
    if b.imzalar.get("unaspected"):
        return "Kimseyle Konuşmayan"
    return "O Sabah Gökyüzü"


def uret(chart: NatalChart, ad: Optional[str] = None) -> tuple:
    """Haritadan (başlık, gövde) üretir. Hiçbir ağ çağrısı yapmaz."""
    baglam = Baglam(
        chart=chart,
        ad=ad or chart.birth.name,
        rastgele=random.Random(_tohum(chart)),
        imzalar=_imzalari_gruplat(chart),
    )

    paragraflar: List[str] = []
    for bolum in BOLUM_SIRASI:
        paragraflar.extend(p for p in bolum(baglam) if p)

    return _baslik(baglam), "\n\n".join(paragraflar)
