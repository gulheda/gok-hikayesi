# Durum

Son güncelleme: 9 Eylül 2026

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
doğrulandı (istek gitti, hata yolu doğru ekranı gösterdi).

## Kod hazır, canlı çalıştırılmadı

**Hikâye üretimi.** `ANTHROPIC_API_KEY` tanımlı olmadığı için `/api/hikaye`
canlı çağrılmadı. Anahtar eklendiğinde çalışması gerekir; hata yolu test
edildi (503 + temiz kullanıcı mesajı).

**Seslendirme.** TTS anahtarı yok. Parçalama ve maliyet hesabı test edildi;
gerçek ses üretilmedi, yani ses kalitesi hakkında hiçbir şey bilinmiyor.

## Yapılmadı

- Veri kalıcılığı (şu an API durumsuz, hiçbir şey saklanmıyor)
- Ses dosyası depolama (S3/R2)
- Rate limiting ve maliyet koruması — **yayına çıkmadan önce şart**, aksi
  hâlde tek bir döngüsel istemci fatura üretir
- Doğum haritası çarkı görselleştirmesi
- KVKK aydınlatma metni, gizlilik politikası, "eğlence amaçlıdır" ibaresi
- Kapalı beta

## Sıradaki en değerli üç iş

1. **`ANTHROPIC_API_KEY` ekle ve beş farklı haritayla hikâye üret.**
   Projenin doğrulanmamış tek varsayımı hikâye kalitesi; geri kalan her şey
   çalışıyor. Karşılaştırma ölçütü [ornek-hikaye.md](ornek-hikaye.md).
   Çıktılar zayıfsa prompt üzerinde çalışılır; hâlâ zayıfsa ürün fikri
   burada durur — ki bu, 100+ saat kurtarır.
2. **Rate limiting.** `/api/hikaye` şu an sınırsız; her çağrı para harcıyor.
3. **İş modeli / platform çelişkisini çöz** (bkz. kararlar.md, madde 8).
   Hediye ürünü mü, iOS uygulaması mı — ikisi aynı anda tutarlı değil.
