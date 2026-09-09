# Durum

Son güncelleme: 9 Eylül 2026 (2. tur)

## Çalışan ve doğrulanmış

**Hesaplama motoru.** Doğum anı → UTC → Julian Day → gezegen konumları →
ev sistemi → açılar. Tarihsel DST kuralları (Türkiye'nin 2016'ya kadarki yaz
saati, 2015'in seçim nedeniyle ertelenen geçişi) ve standart saat öncesi
yerel ortalama saat doğru uygulanıyor. Yaz saatinde hiç yaşanmamış ve iki kez
yaşanmış saatler sessizce kaydırılmak yerine hata olarak bildiriliyor.

**Doğrulama.** 75 test. Ekinoks/gündönümü çıpaları, Einstein referans
haritası, Skyfield + JPL DE440s çapraz kontrolü (en büyük sapma 0,15 açı
saniyesi).

**Geocoding.** 81 il çevrimdışı tablodan (ağa çıkmadan), gerisi Nominatim'den.

**API.** `/saglik`, `/api/harita`, `/api/hikaye`, `/api/seslendir`,
`/api/ses-maliyeti`. Doğrulama hataları 422, yapılandırma eksikliği 503,
yukarı akış arızası 502.

**iOS.** Simülatörde derlenip çalıştırıldı. iOS → backend zinciri uçtan uca
doğrulandı. Doğum haritası çarkı SwiftUI Canvas ile çiziliyor; saat
bilinmiyorsa ev halkası hiç çizilmiyor.

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

## Kod hazır, canlı çalıştırılmadı

**Hikâye üretimi.** `ANTHROPIC_API_KEY` tanımlı olmadığı için `/api/hikaye`
canlı çağrılmadı. Anahtar eklendiğinde çalışması gerekir; hata yolu test
edildi (503 + temiz kullanıcı mesajı).

**Seslendirme.** TTS anahtarı yok. Parçalama ve maliyet hesabı test edildi;
gerçek ses üretilmedi, yani ses kalitesi hakkında hiçbir şey bilinmiyor.

## Yapılmadı

- Veri kalıcılığı (şu an API durumsuz, hiçbir şey saklanmıyor)
- Ses dosyası depolama (S3/R2)
- Doğum haritası çarkı görselleştirmesi
- KVKK aydınlatma metni, gizlilik politikası, "eğlence amaçlıdır" ibaresi
- Kapalı beta

## Sıradaki en değerli üç iş

1. **`ANTHROPIC_API_KEY` ekle ve beş farklı haritayla hikâye üret.**
   Projenin doğrulanmamış tek varsayımı hikâye kalitesi; geri kalan her şey
   çalışıyor. Karşılaştırma ölçütü [ornek-hikaye.md](ornek-hikaye.md).
   Çıktılar zayıfsa prompt üzerinde çalışılır; hâlâ zayıfsa ürün fikri
   burada durur — ki bu, 100+ saat kurtarır.
2. **Backend'i bir yere deploy et** (Railway/Render/Fly). Şu an yalnızca
   `localhost`; gerçek iPhone'da uygulama çalışamaz. HTTPS gelince
   Info.plist'teki ATS istisnası kaldırılmalı.
3. **İş modeli / platform çelişkisini çöz** (bkz. kararlar.md, madde 8).
   Hediye ürünü mü, iOS uygulaması mı — ikisi aynı anda tutarlı değil.

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
