# Gizlilik Politikası ve KVKK Aydınlatma Metni — TASLAK

> **Bu bir taslaktır, hukuki görüş değildir.** Yayınlanmadan önce bir avukat
> tarafından gözden geçirilmeli; `[KÖŞELİ]` alanlar doldurulmalıdır.
> Taslak, kodun **bugünkü** davranışına göre yazıldı (bkz. docs/durum.md);
> davranış değişirse (veri kalıcılığı, hesap, ödeme) metin de güncellenmelidir.

Son güncelleme: [TARİH]

## 1. Veri sorumlusu

[ŞİRKET/KİŞİ ADI], [ADRES], [E-POSTA]. 6698 sayılı KVKK kapsamında veri
sorumlusu budur.

## 2. "Eğlence amaçlıdır" ibaresi (uygulama içinde görünür yerde de yer almalı)

Gök Hikâyesi bir eğlence ve kişisel anlatı uygulamasıdır. Gezegen konumları
astronomik hesapla bulunur; ancak bu konumlara bağlanan yorumlar ve hikâyeler
kurgudur. Uygulama tıbbi, psikolojik, hukuki ya da mali tavsiye vermez; hiçbir
karar için dayanak alınmamalıdır.

## 3. İşlenen kişisel veriler

| Veri | Ne için | Şu an saklanıyor mu? |
|---|---|---|
| Doğum tarihi, saati (varsa), yeri | Gök cisimleri konumunu hesaplamak ve hikâye yazmak | Hayır — API durumsuz, istek bitince atılır |
| Ad / hitap (girildiyse) | Hikâyeyi kişiselleştirmek | Hayır |
| IP adresi (veya vekil başlığı) | İstek sınırlama, kötüye kullanımı önleme | Yalnızca bellekte, kayan pencere süresince |
| Uygulama içi tercihler (yazı boyutu) | Arayüz | Yalnızca cihazda |

Doğum bilgileri, kişiyle ilişkilendirilebildiği için kişisel veridir. Doğum saati
ve yeri birlikte hassas kabul edilebilecek ölçüde kimliklendirici olabilir;
özel nitelikli veri (sağlık vb.) toplanmaz.

## 4. İşleme amacı ve hukuki sebep

- Haritayı hesaplamak ve hikâyeyi üretmek: sözleşmenin ifası / istenen hizmetin
  sunulması (KVKK m.5/2-c). [AVUKAT: açık rıza gerekip gerekmediğini teyit etsin]
- İstek sınırlama ve güvenlik: meşru menfaat (m.5/2-f).

## 5. Üçüncü taraflara aktarım

Kod bunları kullanabilir; yayında hangileri açıksa metinde kalmalı:

- **Hikâye üretimi (dil modeli sağlayıcısı, ör. Anthropic):** hesaplanmış harita
  değerleri ve varsa ad, hikâye yazılması için gönderilir. [Sağlayıcının veri
  saklama/eğitim politikası ve yurt dışı aktarım dayanağı eklenecek — KVKK m.9.]
- **Seslendirme (TTS sağlayıcısı):** yalnızca üretilmiş hikâye metni. [Sağlayıcı.]
- **Yer çözümleme:** Türkiye il adları çevrimdışı çözülür; diğer yerler
  OpenStreetMap Nominatim'e arama metni olarak gider.
- **Barındırma:** [Railway/Render/Fly — bölge ve yurt dışı aktarım notu.]

Veriler satılmaz, reklam amacıyla paylaşılmaz.

## 6. Saklama süresi

Şu an kalıcı depolama yoktur. Veri kalıcılığı eklendiğinde (docs/kararlar.md,
madde 10) bu bölüm güncellenmeli: neyin, ne kadar süre, neden saklandığı ve
silme yolu yazılmalı. IP bazlı sayaçlar bellekte tutulur ve sunucu yeniden
başlayınca silinir.

## 7. Haklarınız (KVKK m.11)

Verilerinizin işlenip işlenmediğini öğrenme, bilgi talep etme, amacına uygun
kullanılıp kullanılmadığını öğrenme, aktarıldığı kişileri bilme, düzeltme,
silme/yok etme, itiraz etme ve zarara uğrarsanız tazminat talep etme haklarına
sahipsiniz. Başvuru: [E-POSTA]. En geç 30 gün içinde yanıtlanır.

## 8. Çocuklar

Uygulama 13 yaş altı çocuklara yönelik değildir. [Kararlar.md'deki çocuk
segmenti kararı verilirse veli onayı süreci eklenmeli.]

## 9. Yayın öncesi kontrol listesi

- [ ] Köşeli alanlar dolduruldu
- [ ] Avukat incelemesi (özellikle m.9 yurt dışı aktarım, açık rıza)
- [ ] VERBİS kaydı gerekip gerekmediği kontrol edildi
- [ ] "Eğlence amaçlıdır" ibaresi uygulamada hikâye ekranında görünür
- [ ] App Store gizlilik "besin etiketi" bu tabloyla tutarlı
