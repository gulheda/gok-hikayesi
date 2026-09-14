"""Türkçe ek çekimi.

Şablonla Türkçe metin üretmenin asıl zorluğu burada. Türkçe eklemeli bir
dil: ek, eklendiği kelimenin son ünlüsüne ve son ünsüzüne göre değişir.
Metni düz birleştirirsen "Toprakı", "Ay de", "kıyısıdeydi" gibi bozuk
biçimler çıkar - ve bozuk dilbilgisi, içerik ne kadar iyi olursa olsun
metni anında ucuzlatır.

Uygulanan kurallar:

- **Büyük ünlü uyumu** (a/e): son ünlü kalınsa a, inceyse e.
- **Küçük ünlü uyumu** (ı/i/u/ü): son ünlünün düzlük/yuvarlaklığına göre.
- **Ünsüz benzeşmesi**: sert ünsüzle biten kelimede ekin d'si t olur
  (Denizli'de ama Sinop'ta).
- **Ünsüz yumuşaması**: p/ç/t/k ile biten kelimeye ünlüyle başlayan ek
  gelince b/c/d/ğ olur (toprak → toprağı). Tek heceli kelimelerin çoğu
  yumuşamaz (at → atı), bu yüzden hece sayısı kontrol ediliyor.
- **Kaynaştırma**: ünlüyle biten kelimeye ünlüyle başlayan ek gelince
  araya y veya n girer (kapı → kapıya, kapı → kapının).
"""
from __future__ import annotations

from typing import Optional

KALIN_UNLULER = "aıou"
INCE_UNLULER = "eiöü"
UNLULER = KALIN_UNLULER + INCE_UNLULER
DUZ_UNLULER = "aeıi"
SERT_UNSUZLER = "fstkçşhp"

# Tek heceli olup da yumuşayan kelimeler kuralın istisnasıdır; listesi
# kısa olduğu için kural yerine liste tutmak daha doğru.
TEK_HECE_YUMUSAYANLAR = {
    "uc", "dip", "kap", "kurt", "yurt", "çok", "gök",
    # Sayılar: dört -> dördü. Tek heceli olmasına rağmen yumuşar.
    "dört",
}

YUMUSAMA = {"p": "b", "ç": "c", "t": "d", "k": "ğ"}


def _kucult(harf: str) -> str:
    """Türkçeye duyarlı küçültme: I -> ı, İ -> i."""
    return harf.replace("I", "ı").replace("İ", "i").lower()


def buyuk_harf(metin: str) -> str:
    """Türkçeye duyarlı ilk harf büyütme.

    Python'un `str.capitalize()` metodu 'i' harfini 'I' yapar; Türkçede
    doğrusu 'İ'dir. "içsel" -> "Içsel" gibi çıktılar metni anında
    yabancı gösterir ve bu hata sessizdir - hiçbir şey patlamaz.
    """
    if not metin:
        return metin
    ilk = metin[0]
    if ilk == "i":
        return "İ" + metin[1:]
    if ilk == "ı":
        return "I" + metin[1:]
    return ilk.upper() + metin[1:]


def son_unlu(kelime: str) -> Optional[str]:
    for harf in reversed(_kucult(kelime)):
        if harf in UNLULER:
            return harf
    return None


def hece_sayisi(kelime: str) -> int:
    return sum(1 for h in _kucult(kelime) if h in UNLULER)


def kalin_mi(kelime: str) -> bool:
    """Kelimenin son ünlüsü kalın mı. Ünlü yoksa kalın varsayılır."""
    u = son_unlu(kelime)
    return u is None or u in KALIN_UNLULER


def _dort_yonlu(kelime: str) -> str:
    """Küçük ünlü uyumuna göre ı/i/u/ü seçer."""
    u = son_unlu(kelime) or "a"
    if u in "aı":
        return "ı"
    if u in "ei":
        return "i"
    if u in "ou":
        return "u"
    return "ü"


def _iki_yonlu(kelime: str) -> str:
    return "a" if kalin_mi(kelime) else "e"


def _sert_bitiyor(kelime: str) -> bool:
    temiz = _kucult(kelime).rstrip("'")
    return bool(temiz) and temiz[-1] in SERT_UNSUZLER


def _unluyle_bitiyor(kelime: str) -> bool:
    temiz = _kucult(kelime).rstrip("'")
    return bool(temiz) and temiz[-1] in UNLULER


def yumusat(kelime: str) -> str:
    """Ünlüyle başlayan ek almadan önce son ünsüzü yumuşatır.

    'toprak' + ünlü ek -> 'toprağ...'. Tek heceli kelimelerin çoğu
    yumuşamaz ('at' -> 'atı'), o yüzden hece sayısı kontrol ediliyor.
    """
    if not kelime:
        return kelime
    kucuk = _kucult(kelime)
    son = kucuk[-1]
    if son not in YUMUSAMA:
        return kelime
    if hece_sayisi(kelime) < 2 and kucuk not in TEK_HECE_YUMUSAYANLAR:
        return kelime
    # Özgün büyük/küçük harfi koru: yalnızca son harfi değiştiriyoruz.
    return kelime[:-1] + YUMUSAMA[son]


# --------------------------------------------------------------------------
# Durum ekleri
# --------------------------------------------------------------------------

def bulunma(kelime: str, ozel_ad: bool = False) -> str:
    """Bulunma hâli: -de / -da / -te / -ta  (Denizli'de, Sinop'ta)."""
    ek = ("t" if _sert_bitiyor(kelime) else "d") + _iki_yonlu(kelime)
    return f"{kelime}'{ek}" if ozel_ad else f"{kelime}{ek}"


def ayrilma(kelime: str, ozel_ad: bool = False) -> str:
    """Ayrılma hâli: -den / -dan / -ten / -tan."""
    ek = ("t" if _sert_bitiyor(kelime) else "d") + _iki_yonlu(kelime) + "n"
    return f"{kelime}'{ek}" if ozel_ad else f"{kelime}{ek}"


def yonelme(kelime: str, ozel_ad: bool = False) -> str:
    """Yönelme hâli: -e / -a  (kapıya, eve)."""
    govde = kelime if _unluyle_bitiyor(kelime) else yumusat(kelime)
    tampon = "y" if _unluyle_bitiyor(kelime) else ""
    ek = tampon + _iki_yonlu(kelime)
    return f"{govde}'{ek}" if ozel_ad else f"{govde}{ek}"


def belirtme(kelime: str, ozel_ad: bool = False) -> str:
    """Belirtme hâli: -ı / -i / -u / -ü  (toprağı, kapıyı)."""
    govde = kelime if _unluyle_bitiyor(kelime) else yumusat(kelime)
    tampon = "y" if _unluyle_bitiyor(kelime) else ""
    ek = tampon + _dort_yonlu(kelime)
    return f"{govde}'{ek}" if ozel_ad else f"{govde}{ek}"


def tamlayan(kelime: str, ozel_ad: bool = False) -> str:
    """Tamlayan hâli: -ın / -in / -un / -ün  (Jüpiter'in, kapının)."""
    govde = kelime if _unluyle_bitiyor(kelime) else yumusat(kelime)
    tampon = "n" if _unluyle_bitiyor(kelime) else ""
    ek = tampon + _dort_yonlu(kelime) + "n"
    return f"{govde}'{ek}" if ozel_ad else f"{govde}{ek}"


def iyelik3(kelime: str) -> str:
    """3. tekil iyelik: -ı / -i / -sı / -si  (kıyısı, toprağı)."""
    if _unluyle_bitiyor(kelime):
        return f"{kelime}s{_dort_yonlu(kelime)}"
    return f"{yumusat(kelime)}{_dort_yonlu(kelime)}"


def mekan_bulunma(ad: str, zaten_iyelikli: bool = False) -> str:
    """Bir yer adının bulunma hâli.

    Ayrım şurada: 'gelgit kıyısı' gibi belirtisiz isim tamlamaları zaten
    üçüncü tekil iyelik eki taşır ve bulunma eki araya n alır
    ('kıyısında'). 'Meydan' gibi yalın adlar almaz ('meydanda'). Bu ayrım
    kelimeye bakarak güvenilir biçimde çıkarılamadığı için sözlükte
    işaretleniyor - tahmin etmeye çalışmak 'kıyısısında' üretir.
    """
    if zaten_iyelikli:
        return f"{ad}nd{_iki_yonlu(ad)}"
    return bulunma(ad)


def gecmis_kopula(kelime: str, ozel_ad: bool = False) -> str:
    """Geçmiş zaman ek-fiili: -dı/-di/-du/-dü, sert ünsüzden sonra -tı/-ti.

    'Güneş'ti' ama 'Ay'dı', 'Merkür'dü'. Ekin ünsüzünü sabitlemek
    ('ti' yazmak) özel adların çoğunda bozuk biçim üretir.
    """
    ek = ("t" if _sert_bitiyor(kelime) else "d") + _dort_yonlu(kelime)
    return f"{kelime}'{ek}" if ozel_ad else f"{kelime}{ek}"


def de_baglaci(kelime: str) -> str:
    """Ayrı yazılan 'de/da' bağlacı. Ünsüz benzeşmesi UYGULANMAZ."""
    return "da" if kalin_mi(kelime) else "de"


def sayi_sifat(sayi: int) -> str:
    """Sayıyı anlatıda kullanılacak sözcüğe çevirir."""
    yazi = {
        0: "hiç", 1: "bir", 2: "iki", 3: "üç", 4: "dört", 5: "beş",
        6: "altı", 7: "yedi", 8: "sekiz", 9: "dokuz", 10: "on",
        11: "on bir", 12: "on iki",
    }
    return yazi.get(sayi, str(sayi))


AY_ADLARI = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]


def tarih_yazi(tarih) -> str:
    """'3 Temmuz 2003' biçiminde tarih."""
    return f"{tarih.day} {AY_ADLARI[tarih.month - 1]} {tarih.year}"


def gunun_vakti(saat: int) -> str:
    """Saatten günün vaktini verir; anlatıya 'sabahı', 'akşamı' diye girer."""
    if 5 <= saat < 11:
        return "sabahı"
    if 11 <= saat < 15:
        return "öğlesi"
    if 15 <= saat < 19:
        return "ikindisi"
    if 19 <= saat < 23:
        return "akşamı"
    return "gecesi"
