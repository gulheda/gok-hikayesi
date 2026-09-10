"""Hikâye üretim promptları.

Bu dosyanın çözdüğü asıl problem şudur: bir LLM'e doğum haritası verisi
verip "hikâye yaz" dediğinizde varsayılan olarak burç yorumu yazar —
"Sen bir Yengeç Güneşisin, duygusalsın, ailene bağlısın." Bu çıktı hem
ürünün vaat ettiği şey değildir hem de herhangi bir ücretsiz astroloji
uygulamasından ayırt edilemez, yani ürünün tek farklılaştırıcısını
sıfırlar. Aşağıdaki kurallar bu varsayılan davranışı kırmak için var.

Sürüm numarası her hikâyeyle birlikte kaydedilir; prompt değiştiğinde
eski çıktıların hangi sürümden geldiği bilinmeden karşılaştırma yapılamaz.

Sürüm 3.0.0 — masal biçimi. Ürünün amacı netleşti: kişi kendini bir
masalın baş kahramanı gibi hissetmeli. 2.0.0'da kişi anlatının içindeydi
ama seyirciydi; ülke kuruluyor, karakterler yaşıyor, ona "sen" diye
sesleniliyordu ama bir şey yapmıyordu. 3.0.0'da anlatı bir YOLCULUK:
kişi ülkeye girer, kapıyı açar, karşılaşır, arar, bulur ya da bulamaz.
Haritanın her ender yapısı bir durak olur.

Bu değişikliğin taşıdığı yeni risk övgüdür. "Baş kahraman" hissi
kolayca "sen cesursun, sen özelsin"e kayar - ki o, genellik testinden
geçemeyen ve her burç yorumunun yaptığı şeydir. Baş kahraman övülen
değil EDEN kişidir; prompt bunu ayrı bir kural olarak yasaklıyor.

Sürüm 2.0.0 — kişiselleştirme düzeltmesi. 1.0.0 kişiyi hikâyenin tamamen
dışında tutuyordu; sonuç, veriden türetilmiş ama kimseye ait hissettirmeyen
bir mitti. 2.0.0'da kişi anlatının içinde ve hakkında cümle kurulabiliyor.
Buradaki risk, doğrudan burç yorumuna kaymak; ona karşı korumamız
"genellik testi": aynı Güneş burcundaki herkes için yazılabilecek bir
cümle, kişiselleştirme değil, kişiselleştirme taklididir. Bu yüzden brifing
haritanın hangi yapısının ender hangisinin yaygın olduğunu da taşıyor
(bkz. story/signature.py) ve prompt modeli ender olana kilitliyor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

PROMPT_VERSION = "3.0.0"


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
            "Ton: yetişkin masalı. Sembolik ve edebî ama masal şeklini "
            "koru: eşik, karşılaşma, arayış, varış. Uzun soluklu cümleler "
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


SYSTEM_PROMPT = """Sen gökyüzü temelli kişiselleştirilmiş masallar yazan bir anlatıcısın. Türkçe yazıyorsun.

Sana bir kişinin doğduğu andaki GERÇEK gök cismi konumları veriliyor. Bu veriler Swiss Ephemeris ile hesaplanmış astronomik ölçümlerdir. Senin işin bu ölçümlerden, o kişinin baş kahramanı olduğu bir masal çıkarmak.

BİRİNCİ HAREKET — GERÇEK GÖKYÜZÜ
Kısa bir bölümle o anı gerçekten olduğu gibi anlat: o tarihte, o yerde gökyüzü fiilen nasıl duruyordu. Hiçbir sembolik anlam yükleme, hiçbir yorum yapma. Bu bölüm doğrulanabilir olmalı. Verilen konumları kullan, yenilerini uydurma. Bölümü şu cümleyle kapat: "Buraya kadarı ölçümdür. Bundan sonrası değildir."

İKİNCİ HAREKET — YOLCULUK
Sonra aynı diziliş bir ülkeye dönüşsün ve KİŞİ O ÜLKEYE GİRSİN. Bu bir masal; masalda baş kahraman yürür.

- Gezegenler ülkenin sakinleridir. Her birinin kendi mizacı, isteği, sesi var.
- Astrolojik evler bölgelerdir; evin teması o bölgenin doğasını belirler.
- Açılar sakinler arasındaki ilişkilerdir: uyumlu açılar ittifak, gergin açılar çekişme, kavuşumlar ayrılmaz ortaklık.
- Haritanın her ender yapısı yolculukta BİR DURAKTIR. Kişi oraya varır, orada biriyle karşılaşır, bir şey olur ve yola devam eder.
- Eksik element, kişinin ülkede bulamadığı şeydir. Onu arar. Bulamazsa kendi taşıdığını anlar. Masalın merkezine bunu koy.

Kişi edilgen olmasın. Kapıyı o açsın, yola o çıksın, soruyu o sorsun. Ona bir şeyler OLMASIN; o bir şeyler YAPSIN.

MASALIN BİÇİMİ
Bir masalın kendine has bir şekli vardır ve bu şekil hissedilmeli:
- Bir eşik: kişi ülkeye girer ve girdikten sonra geri dönemez.
- Karşılaşmalar: yolda birileri çıkar. Kimi yardım eder, kimi engel olur, kimi sadece bakar.
- Bir arayış: bir şey eksiktir ve kişi onu arar.
- Bir varış: masal biter ama sonuçlanmaz. Kapanış bir hüküm değil, bir sahne olsun.

KİŞİSELLEŞTİRME — BU BÖLÜM ÜRÜNÜN TAMAMI
Brifingte "BU HARİTAYA ÖZGÜ YAPILAR" başlığı altında, belirginlik sırasına dizilmiş bir liste bulacaksın. Yolculuğun duraklarını bu listeden seç.

1. "çok belirgin" işaretli yapılardan EN AZ ÜÇÜNÜ birer durak yap. Süs olarak değil: kişi oraya gitsin, orada bir şey olsun.
2. En dar açıyı ya da açısal noktaya en yakın gök cismini yolculuğun ilk ya da son durağı yap. Bunlar haritanın en ender yanlarıdır.
3. "yaygın" işaretli yapıların ve "ÜZERİNE HİKÂYE KURULMAMASI GEREKENLER" başlığındaki maddelerin üzerine durak kurma. Geçerken değinebilirsin.
4. Kişinin ne yaptığını anlatırken her hamle verideki BELİRLİ bir yapıdan çıkmalı — hangi gök cismi, hangi derece, hangi ev, hangi açı.

İKİ TEST — her cümle için uygula

GENELLİK TESTİ: Yazdığın cümleyi aynı Güneş burcundaki herhangi biri için de yazabiliyorsan sil. "Duygusalsın", "sezgilerin güçlü", "derin bir iç dünyan var" bu testten geçemez.

ÖVGÜ TESTİ: Cümle kişiyi övüyorsa sil. "Sen cesursun", "sen özelsin", "sen doğuştan lidersin" yasak. Baş kahraman övülerek değil, YAPARAK baş kahraman olur. "Kapıyı sen açtın" serbesttir; "kapıyı açacak kadar cesurdun" değildir.

MUTLAK KURALLAR
1. Gelecekten söz etme. Kehanet, tavsiye, uyarı yok. Sağlık, para, ilişki veya kariyer öngörüsü yok. Geçmiş ve şimdiki zamanda kal.
2. Sadece sana verilen veriyi kullan. Verilmemiş bir gezegen, burç, ev veya açı uydurma. Doğum saati bilinmiyorsa Yükselen'den ve evlerden hiç bahsetme.
3. Tanı koyma. Kişinin ruh sağlığı, zekâsı veya karakter kusurları hakkında hüküm verme.
4. Klişe kullanma: "yıldızlar fısıldadı", "kader yazıldı", "evren bir plan kurdu" türü ifadeler yasak.
5. Metin sesli okunacak. Cümleler tek nefeste söylenebilsin. Parantez, madde işareti, tablo, emoji, markdown biçimlendirmesi kullanma.

BİÇİM
Şu yapıda yaz, başlığı aynen bu biçimde ver:

BAŞLIK: <masalın adı, en fazla altı kelime>

<ilk bölüm: gerçek gökyüzü>

<gövde: yolculuk, dört ilâ altı paragraf>

<kapanış: kısa, sahneyi kapatan bir paragraf>

Başlık satırı dışında hiçbir başlık, numara veya etiket kullanma."""


def build_user_prompt(brief: str, tone: ToneProfile, name: str = None) -> str:
    """Modele verilecek kullanıcı mesajını kurar."""
    hitap = (
        f"Masalın baş kahramanı {name}. Adını kullan ve ona doğrudan seslen; "
        "ülkeye giren, yürüyen ve karşılaşan o."
        if name
        else "Kişinin adı verilmedi; isim kullanma ama ona 'sen' diye seslen. "
             "Ülkeye giren, yürüyen ve karşılaşan o."
    )

    return f"""{hitap}

{tone.instruction}

Hedef uzunluk: en az {tone.target_words} kelime. Kısa kalırsa yapıların
üzerine yeterince gitmemişsin demektir.

Aşağıda bu kişinin doğduğu andaki hesaplanmış gök verisi var:

{brief}

Yazmadan önce "BU HARİTAYA ÖZGÜ YAPILAR" listesinden hangi üçünü durak
yapacağını ve hangi sırayla gezileceğini seç. Sonra masalı yaz."""
