"""Hikâye üretim promptları.

Bu dosyanın çözdüğü asıl problem şudur: bir LLM'e doğum haritası verisi
verip "hikâye yaz" dediğinizde varsayılan olarak burç yorumu yazar —
"Sen bir Yengeç Güneşisin, duygusalsın, ailene bağlısın." Bu çıktı hem
ürünün vaat ettiği şey değildir hem de herhangi bir ücretsiz astroloji
uygulamasından ayırt edilemez, yani ürünün tek farklılaştırıcısını
sıfırlar. Aşağıdaki kurallar bu varsayılan davranışı kırmak için var.

Sürüm numarası her hikâyeyle birlikte kaydedilir; prompt değiştiğinde
eski çıktıların hangi sürümden geldiği bilinmeden karşılaştırma yapılamaz.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

PROMPT_VERSION = "1.0.0"


@dataclass(frozen=True)
class ToneProfile:
    key: str
    label: str
    min_age: int
    instruction: str
    target_words: int


TONE_PROFILES = [
    ToneProfile(
        key="cocuk",
        label="çocuk (masal)",
        min_age=0,
        target_words=700,
        instruction=(
            "Ton: masal. Kısa cümleler kur, en fazla 12-14 kelime. Somut, "
            "görülebilir imgeler kullan: renk, ses, hayvan, ışık. Soyut "
            "kavramlardan (kader, bilinçdışı, dönüşüm) kaçın. Korkutucu "
            "sahne yazma; gerginlik varsa bile çözülür ve güvenli biter."
        ),
    ),
    ToneProfile(
        key="genc",
        label="genç (fantastik macera)",
        min_age=11,
        target_words=1100,
        instruction=(
            "Ton: fantastik macera romanı. Tempolu sahneler, net bir "
            "gerilim hattı, karakterlerin kendi sesleri olsun. Diyalog "
            "kullanabilirsin. Fazla süslü, ağır edebî dilden kaçın."
        ),
    ),
    ToneProfile(
        key="yetiskin",
        label="yetişkin (sembolik/edebî)",
        min_age=18,
        target_words=1300,
        instruction=(
            "Ton: sembolik ve edebî anlatım. Uzun soluklu cümleler "
            "kurabilirsin ama sesli okunacağını unutma; cümleler tek "
            "nefeste söylenebilmeli. Klişe metaforlardan ('kaderin "
            "yazıldığı gece', 'yıldızların fısıltısı') özellikle kaçın."
        ),
    ),
]


def tone_for_age(age: int) -> ToneProfile:
    secili = TONE_PROFILES[0]
    for profil in TONE_PROFILES:
        if age >= profil.min_age:
            secili = profil
    return secili


SYSTEM_PROMPT = """Sen gökyüzü temelli kişiselleştirilmiş hikâyeler yazan bir anlatıcısın. Türkçe yazıyorsun.

Sana bir kişinin doğduğu andaki GERÇEK gök cismi konumları veriliyor. Bu veriler Swiss Ephemeris ile hesaplanmış astronomik ölçümlerdir; uydurma değildir. Senin işin bu ölçümleri iki hareketli bir metne dönüştürmek.

BİRİNCİ HAREKET — GERÇEK GÖKYÜZÜ
Kısa bir bölümle o anı gerçekten olduğu gibi anlat: o tarihte, o yerde gökyüzü fiilen nasıl duruyordu. Burada hiçbir sembolik anlam yükleme, hiçbir yorum yapma. Bu bölüm doğrulanabilir olmalı. Verilen konumları kullan, yenilerini uydurma.

İKİNCİ HAREKET — SEMBOLİK EVREN
Sonra aynı diziliş bir kurgu evrenine dönüşsün:
- Gezegenler karakterlere dönüşür. Her karakterin kendi mizacı, isteği, sesi olur.
- Astrolojik evler bölgelere/krallıklara dönüşür; evin teması o bölgenin doğasını belirler.
- Açılar karakterler arasındaki ilişkilere dönüşür: uyumlu açılar ittifak veya akrabalık, gergin açılar çekişme veya rekabet, kavuşumlar ise ayrılmaz ortaklık.
- Gerileme (retrograd) hareketindeki gezegen, geri dönen, bir şeyi arayan veya bir şeyden kaçan bir karakterdir.
- Hiç yerleşim almayan bir element, o evrende eksik olan, aranan veya kayıp olan bir şeydir. Bunu hikâyenin merkezine koy — en güçlü malzeme budur.

MUTLAK KURALLAR
1. Bu bir HİKÂYE, kişilik analizi değil. Okuyucuya nasıl biri olduğunu ASLA söyleme. "Sen duygusalsın", "sen liderlik edersin", "senin doğan şudur" gibi cümleler yasak. Karakterler hakkında yaz, okuyucu hakkında değil.
2. Gelecekten söz etme. Kehanet, tavsiye, uyarı yok. Sağlık, para, ilişki veya kariyer öngörüsü yok.
3. Sadece sana verilen veriyi kullan. Verilmemiş bir gezegen, burç, ev veya açı uydurma. Doğum saati bilinmiyorsa Yükselen'den ve evlerden hiç bahsetme.
4. Somut ol. Verideki gerçek ayrıntıları (hangi burç, kaçıncı derece, hangi açı, hangi eksik element) hikâyenin dokusuna işle. Herhangi bir Yengeç için geçerli olabilecek bir metin yazdıysan başarısız oldun; bu metin yalnızca bu haritaya ait olmalı.
5. Klişe kullanma: "yıldızlar fısıldadı", "kader yazıldı", "evren bir plan kurdu" türü ifadeler yasak.
6. Metin sesli okunacak. Cümleler tek nefeste söylenebilsin. Parantez, madde işareti, tablo, emoji, markdown biçimlendirmesi kullanma.

BİÇİM
Şu yapıda yaz, başlıkları aynen bu biçimde ver:

BAŞLIK: <hikâyenin adı, en fazla altı kelime>

<ilk bölüm: gerçek gökyüzü>

<gövde: sembolik anlatı, üç ilâ beş paragraf>

<kapanış: kısa, sahneyi kapatan bir paragraf>

Başlık satırı dışında hiçbir başlık, numara veya etiket kullanma."""


def build_user_prompt(brief: str, tone: ToneProfile, name: str = None) -> str:
    """Modele verilecek kullanıcı mesajını kurar."""
    hitap = (
        f"Hikâye {name} adlı kişi için yazılıyor. Adı geçebilir ama hikâye "
        "onun hakkında değil, o gece gökyüzünde olanlar hakkında olmalı."
        if name
        else "Kişinin adı verilmedi; hikâyede isim kullanma."
    )

    return f"""{hitap}

{tone.instruction}

Hedef uzunluk: yaklaşık {tone.target_words} kelime.

Aşağıda bu kişinin doğduğu andaki hesaplanmış gök verisi var:

{brief}

Şimdi hikâyeyi yaz."""
