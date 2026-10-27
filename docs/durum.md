# Durum

Son güncelleme: 27 Ekim 2026 (şablon motoru: farklı açısal noktalardaki ikinci cisim için "Yalnız değildi" denmiyor)

## Çalışan ve doğrulanmış

**Hesaplama motoru.** Doğum anı → UTC → Julian Day → gezegen konumları →
ev sistemi → açılar. Tarihsel DST kuralları (Türkiye'nin 2016'ya kadarki yaz
saati, 2015'in seçim nedeniyle ertelenen geçişi) ve standart saat öncesi
yerel ortalama saat doğru uygulanıyor. Yaz saatinde hiç yaşanmamış ve iki kez
yaşanmış saatler sessizce kaydırılmak yerine hata olarak bildiriliyor.

**Doğrulama.** 75 test. Ekinoks/gündönümü çıpaları, Einstein referans
haritası, Skyfield + JPL DE440s çapraz kontrolü (en büyük sapma 0,15 açı
saniyesi).

**Geocoding.** 81 il ve 173 yurtdışı büyük şehir (toplam 254 yer; Tokyo, Pekin, Mumbai, São Paulo, Cape Town vb. dahil; Berlin, Londra, Madrid, Roma, Toronto, Sidney vb.; `YURTDISI_SEHIRLER`) çevrimdışı tablodan (ağa çıkmadan), gerisi Nominatim'den. Ülke belirtilip tabloyla uyuşmazsa ("Paris, Texas") Nominatim'e düşer. Sıradaki genişletme: nüfusu yüksek ilçe merkezleri.

**API.** `/saglik`, `/api/harita`, `/api/hikaye`, `/api/seslendir`,
`/api/ses-maliyeti`. Doğrulama hataları 422, yapılandırma eksikliği 503,
yukarı akış arızası 502.

**iOS.** Simülatörde derlenip çalıştırıldı. iOS → backend zinciri uçtan uca
doğrulandı. Doğum haritası çarkı SwiftUI Canvas ile çiziliyor; saat
bilinmiyorsa ev halkası hiç çizilmiyor. İş modeli kararından sonra (bkz.
kararlar.md madde 8) birincil istemci artık web; iOS kodu duruyor ama
öncelik değil.

**Web istemcisi.** `web/index.html` — bağımlılıksız, tek sayfalık form
(yer/tarih/saat/ad), aynı FastAPI uygulaması tarafından statik olarak
sunuluyor. Yerelde uçtan uca test edildi (sunucu ayakta, `/api/hikaye`
çağrısı ve yanıt gösterimi çalışıyor).

**İstek sınırlama.** İki katmanlı: kaynak başına kayan pencere (hikâye için
saatte 5, günde 15; harita için dakikada 30) ve günlük genel tavan (300 istek
veya 25 USD). Genel tavan gerçekleşen maliyeti izler, tahmini değil - hikâye
başına maliyet uzunluğa göre değişir. Aşıldığında `Retry-After` başlıklı 429.

**Erişilebilirlik.** Tüm tipografi Dynamic Type ile ölçekleniyor; hikâye
ekranında ayrıca kullanıcı kontrollü punto (kalıcı). Hareket azaltma ayarı
açıksa yıldızlar sabit, yükleme halkası dönmüyor. Çark ve satırlar VoiceOver
için etiketli. Erişilebilirlik puntolarında saat anahtarı dikey yerleşiyor.

**Uygulama ikonu.** CoreGraphics ile üretiliyor (`backend/tools/ikon-uret.swift`),
asset kataloğunda ve derlenmiş pakette doğrulandı.

**Hikâye kalitesi.** Şablon motoru gece/gündüz farkındalığı kazandı: Güneş ufkun altındaysa anlatı "gündüzdü", "o sabah" demiyor. Günlük inceleme kaydı: [hikaye-kalite-notlari.md](hikaye-kalite-notlari.md). Aynı burçtaki kavuşumlarda konum cümlesi artık tekrar etmiyor ("İkisi de Başak burcunun 12. derecesinde"). Güneş'e gömülü cisim meclis üyesiyse "bir kişi daha vardı" diye ikinci kez anılmıyor. Kapı bölümünde ikinci cisim başka bir açısal noktadaysa (örn. Tepe ve Yükselen) "oradaydı, birkaç adım ötede" denmiyor. Güneş'te kaybolan birden çok cisim artık "tam olarak görünmüyorlardı" gibi anlamsız kalıpla anlatılmıyor. Büyük üçgen sahnesi geçmiş zamanda anlatılıyor. Gündüz kapanışı artık "gökyüzü açıktı ve boştu" gibi hava durumu iddiası kurmuyor.

## Kod hazır, canlı çalıştırılmadı

**Hikâye üretimi (gerçek LLM).** Gemini ücretsiz katmanıyla elle test
edildi (bkz. [hikaye-kalite-notlari.md](hikaye-kalite-notlari.md), 17 Ekim),
sonuçlar umut verici ama az sayıda örnekle. Üretim varsayılanı hâlâ şablon
motoru — ücretsiz, deterministik, günlük rutinle sürekli iyileşiyor.
`ANTHROPIC_API_KEY` hiç denenmedi (bütçe ayrılmadı, 21 Ekim kararı).

**Seslendirme.** TTS anahtarı yok. Parçalama ve maliyet hesabı test edildi;
gerçek ses üretilmedi. Hediye ürünü kararıyla öncelik düşük.

## Yapılmadı

- Ses dosyası depolama (S3/R2) — hediye ürününde gerekmeyebilir, TTS
  açılmadıkça anlamsız
- KVKK/gizlilik metni: taslak yazıldı ([docs/hukuk/](hukuk/gizlilik-aydinlatma-taslagi.md)),
  avukat incelemesi hâlâ yapılmadı. "Eğlence amaçlıdır" ibaresi artık
  `/api/hikaye` yanıtının `uyari` alanında gerçekten dönüyor (21 Ekim).
- Kapalı beta / gerçek kullanıcı testi

**Veri kalıcılığı artık ihtiyaç değil:** iş modeli "tek seferlik hediye
ürünü" olarak karara bağlandı (hesap yok, geçmiş saklanmıyor) — bkz.
kararlar.md madde 8. Mimari zaten buna uygundu, ekstra iş gerekmedi.

## Sıradaki en değerli üç iş

1. **Deploy'u fiilen yap.** Kod hazır ([DEPLOY.md](../DEPLOY.md), Dockerfile
   yerelde uçtan uca test edildi) — eksik olan tek şey bir Railway/Render
   hesabı açıp GitHub reponu bağlamak. Bu olmadan ne web sayfası ne iOS
   uygulaması gerçek bir adrese sahip olur.
2. **Hikâye kalitesini daha fazla örnekle gözle.** Şablon motoru her gün
   iyileşiyor (bkz. hikaye-kalite-notlari.md); Gemini kıyası tek seferlik
   kaldı. İkisi arasında üretimde hangisinin varsayılan olacağına
   (`LLM_SAGLAYICI`) daha fazla örnekten sonra karar vermek gerekiyor.
3. **KVKK metnini bir avukata gösterip kapalı betaya çık.** Kod tarafı
   artık buna hazır (web istemcisi var, uyarı metni API'de); eksik olan
   hukuki onay ve gerçek kullanıcıya açmak.

## Sınırlama ayarları

Hepsi ortam değişkeniyle değiştirilebilir; varsayılanlar tek kişilik bir
kapalı beta için seçildi.

| Değişken | Varsayılan | Ne yapar |
|---|---|---|
| `HIKAYE_SAATLIK_LIMIT` | 5 | Kaynak başına saatlik hikâye |
| `HIKAYE_GUNLUK_LIMIT` | 15 | Kaynak başına günlük hikâye |
| `HARITA_DAKIKALIK_LIMIT` | 30 | Kaynak başına dakikalık harita |
| `GUNLUK_TOPLAM_ISTEK` | 300 | Günlük genel istek tavanı |
| `GUNLUK_TOPLAM_USD` | 25 | Günlük genel harcama tavanı |
| `PROXY_ARKASINDA` | kapalı | Vekil arkasındaysa `X-Forwarded-For` okunur |

`PROXY_ARKASINDA` **yalnızca** güvenilen bir vekil sunucunun arkasındayken
açılmalı. Doğrudan internete açık bir sunucuda açılırsa herkes bu başlığı
uydurup kaynak başına sınırı tamamen atlayabilir.
