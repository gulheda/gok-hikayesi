# YouTube Shorts senaryoları

Üç senaryo. Üçü de aynı ilkeye dayanıyor: **reklamın kancası ürünün gerçek
farklılaştırıcısı olmalı.** Bu ürünün farkı güzel bir arayüz değil —
piyasada onlarca astroloji uygulaması var ve hepsi güzel. Fark, gösterilen
verinin **gerçekten ölçüm olması** ve hikâyenin o ölçümden çıkması.

"Burcunu öğren" diyen bir reklam, ürünü rakiplerin arasına gömer. "Doğduğun
anda Ay henüz doğmamıştı, 11 dakikası vardı" diyen bir reklam ise başka
hiçbir uygulamanın söyleyemeyeceği bir cümle.

**Teknik not:** Shorts dikey (9:16), en fazla 60 saniye. İzleyicilerin
çoğunluğu sessiz izler — her şey ekranda yazıyla da anlaşılmalı.

---

## Senaryo 1 — "11 Dakika" (önerilen)

En güçlüsü. Tek bir gerçek olguyu kanca yapıyor ve o olgu doğrulanabilir.

| Süre | Görüntü | Ekran yazısı | Ses/anlatım |
|---|---|---|---|
| 0–2 sn | Siyah ekran, tek yıldız belirir | **Doğduğun gün** | — (sessizlik) |
| 2–5 sn | Yıldız alanı açılır | **Ay henüz doğmamıştı.** | "Doğduğun gün, Ay henüz doğmamıştı." |
| 5–7 sn | Uygulamadaki gerçek cümle büyütülmüş | **11 dakikası vardı.** | "On bir dakikası vardı." |
| 7–11 sn | Doğum haritası çarkı çizilir, gezegenler yerine oturur | *Bu bir tahmin değil.* | "Bu bir tahmin değil. Hesaplama." |
| 11–16 sn | Hikâye metni akar, bir cümle vurgulanır | **"İlk durağın kapı oldu. Onu sen açtın."** | metinden okuma |
| 16–22 sn | Giriş ekranı: tarih/saat/yer girilir | **Kendi masalın.** | "Doğduğun anın gökyüzünden, sana ait bir masal." |
| 22–26 sn | Uygulama ikonu + ad | **Gök Hikâyesi** | — |

**Neden işe yarıyor:** İlk üç saniyede kimse "astroloji uygulaması"
görmüyor; bir bilgi görüyor. Merak kancası "11 dakika" — çok spesifik
olduğu için gerçek olduğu hissediliyor.

---

## Senaryo 2 — "Bu bir burç yorumu değil"

Doğrudan konumlandırma. Rakiplerden ayrışmayı açıkça yapıyor.

| Süre | Görüntü | Ekran yazısı |
|---|---|---|
| 0–2 sn | Siyah | **Bu bir burç yorumu değil.** |
| 2–6 sn | Uygulamanın "Veri" sekmesi: dereceler, açılar, Julian Day | **Bunlar ölçüm.** Swiss Ephemeris. NASA/JPL ile 0,15 açı saniyesi uyum. |
| 6–10 sn | Çark döner, açı çizgileri belirir | **Doğduğun andaki gerçek gökyüzü.** |
| 10–16 sn | Hikâye ekranına geçiş, metin akar | **Bundan sonrası kurgu. Ve biz bunu söylüyoruz.** |
| 16–22 sn | Hikâyeden bir paragraf | **Senin masalın.** |
| 22–26 sn | İkon + ad | **Gök Hikâyesi** |

**Riski:** "Burç yorumu değil" demek, burç yorumu arayan kitleyi
uzaklaştırabilir. Kime satmak istediğine bağlı.

---

## Senaryo 3 — "Toprak" (duygusal)

Hikâyenin kendisini öne çıkarır. En yavaş ama en akılda kalıcı olabilir.

| Süre | Görüntü | Ekran yazısı |
|---|---|---|
| 0–3 sn | Yıldız alanı, yavaş yakınlaşma | **Doğduğun gün gökyüzünde dört madde vardı.** |
| 3–6 sn | Element çubukları belirir: Ateş 3, Hava 2, Su 5 | Ateş. Hava. Su. |
| 6–9 sn | Toprak çubuğu boş kalır, vurgulanır | **Toprak: 0** |
| 9–14 sn | Hikâye metni: "Bütün ülkede tek bir taş yoktu." | metinden okuma |
| 14–19 sn | Kapanış paragrafı | **"Aradığın şeyi bulamadın. Çıkarken, onu içeri kendinin getirmiş olduğunu fark ettin."** |
| 19–24 sn | İkon + ad | **Gök Hikâyesi** |

**Neden işe yarıyor:** Eksik element ürünün en güçlü anlatı malzemesi ve
her haritada farklı çıkıyor. Bu senaryo farklı kişiler için farklı
çekilebilir — seri yapılabilir.

---

## Çekim nasıl yapılır

Ekran görüntüsü simülatörden alınabilir:

```bash
# Kayda başla (Ctrl+C ile durdurulur)
xcrun simctl io "iPhone 17" recordVideo --codec h264 akis.mp4

# Başka bir terminalde uygulamayı örnek veriyle aç
SIMCTL_CHILD_ON_DOLDUR_YER="Denizli" \
SIMCTL_CHILD_ON_DOLDUR_AD="Gülheda" \
SIMCTL_CHILD_ON_DOLDUR_TARIH="2003-07-03" \
SIMCTL_CHILD_ON_DOLDUR_SAAT="09:00" \
SIMCTL_CHILD_ON_DOLDUR_GONDER="1" \
xcrun simctl launch "iPhone 17" com.gulheda.astrohikaye
```

Gerçek telefonda daha iyi görünür (iOS: Ayarlar → Denetim Merkezi → Ekran
Kaydı). Simülatörde yıldız animasyonu kare düşürebiliyor.

---

## Reklamda söylenmemesi gerekenler

Bunlar hem doğru değil hem de yanıltıcı reklam sorunu yaratır:

- ❌ "Geleceğini öğren" — ürün kehanet yapmıyor, prompt bunu yasaklıyor.
- ❌ "Kişiliğini analiz et" — ürün kişilik analizi yapmıyor.
- ❌ "Bilimsel olarak kanıtlanmış" — gezegen konumları ölçüm, ama onlara
  yüklenen anlam bilimsel bir bulgu değil.
- ❌ Gerçek bir kişinin haritasını izni olmadan göstermek.

Söylenebilecekler:

- ✅ "Doğduğun andaki gerçek gök cismi konumları"
- ✅ "Astronomik hesaplama" / "Swiss Ephemeris"
- ✅ "Sana özel bir masal"
- ✅ "Eğlence amaçlıdır" (uygulamada zaten yazıyor)

---

## Hazır kanca cümleleri

Her biri gerçek veriden çıkıyor ve haritaya göre değişiyor — yani her
kullanıcı için farklı bir Short çekilebilir:

- "Doğduğun anda Ay henüz doğmamıştı. On bir dakikası vardı."
- "O gün Satürn gökyüzündeydi ama kimse onu göremiyordu."
- "Doğduğun yaz Mars, altmış bin yıldır olmadığı kadar yakındı."
- "Haritanda toprak yok. Tek bir taş bile."
- "Jüpiter, doğduğun dakikada ufkun bir derece üstündeydi."
