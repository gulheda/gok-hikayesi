"""Şablon motorunun içerik sözlüğü.

Buradaki her madde elle yazılmış Türkçe metindir; dışarıdan hiçbir dil
modeli çağrılmaz.

Tasarımın tek kuralı şu: **hiçbir parça doğrudan burç adına bağlanmaz.**
"Güneş Yengeç'te olduğu için duygusalsın" cümlesi aynı burçtaki yüz
milyonlarca insan için de geçerlidir, yani kişiselleştirme taklididir.
Bunun yerine burçlar birer MEKÂN, gezegenler birer KARAKTER olarak
tanımlanıyor; hikâyenin kendisi ise haritanın ender yapılarından
(bkz. story/signature.py) kuruluyor. Aynı burç iki farklı haritada aynı
mekâna açılır ama o mekânda olan şey farklıdır.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Karakter:
    """Bir gök cisminin kurgu evrenindeki karşılığı.

    Fiiller çekimli biçimleriyle saklanıyor. Türkçe fiil çekimini kod
    üzerinden üretmek (kip, kişi, olumsuzluk, ünlü uyumu) ayrı bir iş ve
    hataya çok açık; anlatıda ihtiyaç duyulan iki biçimi elle yazmak hem
    daha güvenli hem daha doğal.
    """

    unvan: str          # anlatıda kullanılan ad
    rol: str            # ne yapan biri
    fiil: str           # geniş zaman: "yönetir"
    fiil_anlati: str    # anlatı geçmişi: "yönetirdi"
    yalnizken: str
    gerilerken: str


KARAKTERLER: Dict[str, Karakter] = {
    "Sun": Karakter(
        unvan="Güneş",
        rol="ülkenin adını taşıyan, doğrudan bakılamayan kişi",
        fiil="yönetir",
        fiil_anlati="yönetirdi",
        yalnizken="kimseye danışmadan karar verir, çünkü danışacak kimsesi yoktur",
        gerilerken="",
    ),
    "Moon": Karakter(
        unvan="Ay",
        rol="gelenin yüzüne bakan, her ay biçim değiştiren kişi",
        fiil="izler",
        fiil_anlati="izlerdi",
        yalnizken="baktığı şeyi kimseye anlatmaz",
        gerilerken="",
    ),
    "Mercury": Karakter(
        unvan="Merkür",
        rol="haber taşıyan, cümlelerini hep birine bitirten kişi",
        fiil="taşır",
        fiil_anlati="taşırdı",
        yalnizken="taşıdığı haberi verecek kimse bulamaz",
        gerilerken="götürdüğü haberi yolun yarısından geri getirir",
    ),
    "Venus": Karakter(
        unvan="Venüs",
        rol="neyin saklanmaya değer olduğuna karar veren kişi",
        fiil="seçer",
        fiil_anlati="seçerdi",
        yalnizken="seçtiklerini kendine saklar",
        gerilerken="bir kez verdiği kararı sessizce geri alır",
    ),
    "Mars": Karakter(
        unvan="Mars",
        rol="beklemeyen, kapıyı çalmadan giren kişi",
        fiil="gelir",
        fiil_anlati="gelirdi",
        yalnizken="geldiği yerde kimseyi bulamaz",
        gerilerken="vardığı yerden geri döner, ama neden döndüğünü söylemez",
    ),
    "Jupiter": Karakter(
        unvan="Jüpiter",
        rol="ülkenin büyüklüğünden yüksek sesle söz eden kişi",
        fiil="anlatır",
        fiil_anlati="anlatırdı",
        yalnizken="anlattığını doğrulayacak kimse yoktur",
        gerilerken="anlattığı ülkeye kendi de inanmamaya başlar",
    ),
    "Saturn": Karakter(
        unvan="Satürn",
        rol="sayan, ölçen ve gerektiğinde hayır diyen kişi",
        fiil="sayar",
        fiil_anlati="sayardı",
        yalnizken="saydığı şeyi kimseye bildirmez",
        gerilerken="verdiği sözün süresini uzatır",
    ),
    "Uranus": Karakter(
        unvan="Uranüs",
        rol="kurulu düzeni sebepsiz bozan kişi",
        fiil="bozar",
        fiil_anlati="bozardı",
        yalnizken="bozacak bir düzen bulamaz",
        gerilerken="yüzü ileriye dönüktür ama adımları geriye gider",
    ),
    "Neptune": Karakter(
        unvan="Neptün",
        rol="sınırları belirsiz, uzaktan bakınca başka görünen kişi",
        fiil="dağılır",
        fiil_anlati="dağılırdı",
        yalnizken="kimse onun orada olduğundan emin olamaz",
        gerilerken="her sabah aynı işe başlar, her akşam biraz geriden bırakır",
    ),
    "Pluto": Karakter(
        unvan="Plüton",
        rol="her şeyi parçalarına ayırıp yeniden kuran kişi",
        fiil="söker",
        fiil_anlati="sökerdi",
        yalnizken="söktüğü şeyi yeniden kuracak kimsesi yoktur",
        gerilerken="bitirmeden bırakır ve bir öncekine döner",
    ),
}


@dataclass(frozen=True)
class Mekan:
    """Bir burcun kurgu evrenindeki coğrafi karşılığı.

    `iyelikli`, adın zaten üçüncü tekil iyelik eki taşıyıp taşımadığını
    söyler ('gelgit kıyısı' taşır, 'meydan' taşımaz). Bulunma eki bu ikisine
    farklı ekleniyor; işaret olmadan 'kıyısısında' gibi bozuk biçimler çıkar.
    """

    ad: str
    nitelik: str
    iyelikli: bool = False


# Burçlar mekândır. Aynı mekân farklı haritalarda aynı görünür; orada
# olan şey farklıdır. Bu yüzden mekân tanımları kişilik değil, coğrafyadır.
MEKANLAR: Dict[int, Mekan] = {
    0:  Mekan("yeni açılmış yol", "kimsenin iki kez geçmediği"),
    1:  Mekan("taş ocağı", "her şeyin ağır olduğu, yerinden oynatılmasının güç olduğu", True),
    2:  Mekan("iki nehrin ayrıldığı çatal", "hangi kolun nereye gittiğinin bilinmediği"),
    3:  Mekan("gelgit kıyısı", "sınırın günde iki kez yer değiştirdiği", True),
    4:  Mekan("meydan", "herkesin birbirini gördüğü, gölgenin az olduğu"),
    5:  Mekan("ölçülmüş tarla", "her sıranın sayıldığı, fazlalığın ayıklandığı"),
    6:  Mekan("köprü", "iki yakanın da eşit ağırlıkta olması gereken"),
    7:  Mekan("derin su", "dibinin görünmediği, altında ne olduğu bilinmeyen"),
    8:  Mekan("dağ geçidi", "ötesinin merak edildiği, dönüşü zor olan", True),
    9:  Mekan("sarp yamaç", "yukarı çıkmanın uzun sürdüğü, düşmenin kısa olduğu"),
    10: Mekan("rüzgârlı düzlük", "hiçbir şeyin uzun süre aynı yerde durmadığı"),
    11: Mekan("sisli göl", "kıyının nerede bittiğinin belli olmadığı"),
}


# Elementler ülkenin yapıldığı maddedir.
ELEMENT_MADDESI: Dict[str, Tuple[str, str]] = {
    "Ateş":   ("ışık", "çabuk yanar ve çabuk söner"),
    "Toprak": ("taş",  "ağırdır ve yerinden oynamaz"),
    "Hava":   ("söz",  "elle tutulmaz ama duyulur"),
    "Su":     ("akış", "hep aynı yataktan geçer ama hiç aynı değildir"),
}

# Eksik element, motorun elindeki en güçlü malzeme: ülkenin sahip OLMADIĞI
# şey. Her element için ne eksikliğinin ne demek olduğu ayrı yazıldı.
EKSIK_ELEMENT: Dict[str, List[str]] = {
    "Ateş": [
        "Ülkede hiç ateş yoktu. Bu, hiçbir şeyin kendiliğinden başlamadığı "
        "anlamına geliyordu; her hareket birinin onu itmesiyle olurdu.",
        "Ateşin hiç payı yoktu bu ülkede. Işık dışarıdan gelirdi ve geldiği "
        "kadar kalırdı.",
    ],
    "Toprak": [
        "Bütün ülkede tek bir taş yoktu. Tek bir tarla, tek bir temel, tek "
        "bir duran şey. Yollar vardı ama yolların altında zemin yoktu.",
        "Toprak hiç bulunmuyordu. Bu yüzden hiçbir yapı iki kez aynı yerde "
        "kurulamadı; kurulan her şey biraz kayardı.",
    ],
    "Hava": [
        "Ülkede söz yoktu. Anlaşmalar konuşularak değil, yapılarak kurulurdu; "
        "bu yüzden yanlış anlaşılmalar hiç düzeltilemezdi.",
        "Havanın hiç payı yoktu. İki kişi arasındaki mesafe kelimeyle değil, "
        "yalnızca adımla kapanırdı.",
    ],
    "Su": [
        "Ülkede akış yoktu. Hiçbir şey kendiliğinden bir yerden bir yere "
        "gitmezdi; her taşıma birinin sırtındaydı.",
        "Suyun hiç payı yoktu. Geçmiş biriktirilemiyordu, çünkü biriktirecek "
        "bir yatak yoktu.",
    ],
}


# Açı türlerinin iki karakter arasındaki ilişkiye çevrilmesi.
ACI_ILISKISI: Dict[str, List[str]] = {
    "conjunction": [
        "{a} ile {b} yan yana oturuyordu, o kadar yakın ki biri cümleye "
        "başladığında öteki bitiriyordu; hangisinin ne söylediğini kimse ayıramazdı",
        "{a} ile {b} birbirinden ayrılmıyordu. İkisini ayrı ayrı çağıran "
        "olmadı, çünkü ayrı ayrı gelmezlerdi",
    ],
    "trine": [
        "{a} ile {b} arasında kimsenin çekmediği düz bir hat vardı ve o hat "
        "hiç eğrilmedi",
        "{a} ile {b} hiç buluşmadılar. Buluşmalarına gerek yoktu; aralarındaki "
        "yol zaten açıktı",
    ],
    "sextile": [
        "{a} ile {b} birbirini uzaktan tanırdı; biri bir şey isteyince öteki "
        "duyardı ama koşarak gelmezdi",
        "{a} ile {b} arasında ince bir bağ vardı, kullanıldıkça güçlenen türden",
    ],
    "square": [
        "{a} ile {b} aynı anda haklı olamazdı ve ikisi de bunu biliyordu",
        "{a} ile {b} her karşılaşmada birbirini yavaşlattı. Bu yavaşlama "
        "ülkenin tek freniydi",
    ],
    "opposition": [
        "{a} ile {b} ülkenin iki ucunda dururdu ve biri konuşurken öteki susardı",
        "{a} ile {b} birbirini görmeden aynı şeye bakıyordu, ters yönlerden",
    ],
}


# Bir cismin açısal noktalara yakınlığı - motorun elindeki en ender yapı.
ACISAL_NOKTA_ADI: Dict[str, str] = {
    "Yükselen": "kapı",
    "Tepe noktası": "kule",
    "Batan": "arka kapı",
    "Dip nokta": "bodrum",
}


KAPANISLAR: List[str] = [
    "O sabah, {yer} üstünde, bunların hiçbiri görünmüyordu. Gökyüzü açıktı ve "
    "boştu. Ama diziliş oradaydı ve bir daha hiç aynı olmayacaktı.",
    "Bu ülke o sabah kuruldu ve kurulduğu gibi kaldı. Gök bir daha aynı "
    "biçimde dizilmedi; dizilseydi bile aynı yerden bakan kimse olmayacaktı.",
    "{yer} üstünde gündüzdü ve hiçbiri görünmüyordu. Görünmemesi, olmadıkları "
    "anlamına gelmiyordu.",
]
