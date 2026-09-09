# Kararlar

Proje planındaki (`PROJE-PLANI.md`) açık kararların bugünkü durumu ve
geliştirme sırasında ortaya çıkan yeni kararlar.

---

## 1. Efemeris: Swiss Ephemeris — **karar verildi**

**Seçim:** pyswisseph (Swiss Ephemeris), veri dosyalarıyla birlikte.

**Neden Skyfield değil:** Skyfield gezegen konumlarını mükemmel hesaplıyor
(bunu doğruladık — 0,15 açı saniyesi uyum), ama **ev sistemi hesabı yok**.
Placidus, Koch, Regiomontanus gibi sistemleri sıfırdan yazmak gerekirdi; bu
hem ciddi bir emek hem de sessiz hata kaynağı. Swiss Ephemeris'te `swe_houses`
hazır geliyor.

**Karar bloke edici değildi.** Plan bunu "önce çözülmeli" diye işaretlemişti;
aslında değildi. Efemeris çağrıları `app/astro/ephemeris.py` içinde dar bir
arayüzün arkasında; sağlayıcı değiştirmek tek dosyalık iş.

### Lisans — **açık, ama ertelenebilir**

Swiss Ephemeris çift lisanslı: **AGPL-3.0** veya **ticari lisans**.

- **AGPL:** Ağ üzerinden servis verirseniz backend kaynak kodunuzu açmak
  zorundasınız. Kapalı kaynak bir iOS uygulaması + kapalı backend bunu
  karşılamaz.
- **Ticari (Astrodienst):** İlk lisans **750 CHF** (tek seferlik, proje
  başına). Aynı lisans sahibine ek lisans 400 CHF; sınırsız lisans 1550 CHF.

**Ne zaman gerekli:** Yalnızca ticari yayına çıkarken. Prototip, test ve
kapalı beta için engel yok.

**Not:** Ücretli lisans alınırsa `pyswisseph` sarmalayıcısının kendisi
AGPL olduğu için ayrıca değerlendirilmeli — bu durumda Swiss Ephemeris'in C
kütüphanesine kendi bağlayıcınızı yazmak ya da Astrodienst'e sormak gerekebilir.

---

## 2. Doğum saati bilinmiyorsa ne olacak — **karar verildi (yeni)**

Planda yoktu; geliştirme sırasında ortaya çıktı ve ürünün çekirdeğini
ilgilendiriyor.

**Karar:** Ev sistemi ve Yükselen **üretilmez**.

**Neden:** Yükselen dört dakikada bir derece ilerler. Planın önerdiği "öğlen
12:00 varsayımı" Yükselen'i rastgele bir burca atar. Türkiye'de nüfus
kayıtlarında doğum saati bulunmadığı için bu kullanıcıların büyük bölümünü
etkiler. Uydurma Yükselen'i hikâyede gerçekmiş gibi kullanmak, ürünün
"gerçek astronomik veri" iddiasını çürütür.

**Uygulanışı:** `HouseResult.available = False`, açık bir sebep metni, prompta
"Yükselen'den söz etme" talimatı, ve arayüzde kullanıcıya *önceden* uyarı.
Gezegen burçları hesaplanmaya devam eder (yavaş gezegenler gün içinde burç
değiştirmez); Ay için yaklaşıklık uyarısı verilir.

---

## 3. Hedef kitle ve ton — **plandaki karar korundu**

MVP tek segment: yetişkin, Türkçe. Kod üç tonu da (çocuk/genç/yetişkin)
destekliyor ve yaştan otomatik seçiyor, ama çocuk segmenti KVKK karmaşıklığı
nedeniyle yayına dahil edilmemeli.

---

## 4. iOS minimum sürüm — **karar verildi**

**iOS 17.0.** Gerekçe: `@Observable` makrosu (iOS 17) durum yönetimini
belirgin biçimde sadeleştiriyor, `ContentUnavailableView` hata ekranını
hazır veriyor. iOS 16'ya inmek bu ikisinin elle yazılması demek.

---

## 5. LLM sağlayıcı — **karar verildi**

**Claude (`claude-opus-5`).** Uzun soluklu, kural-yoğun yaratıcı metin
promptlarında talimatlara uyum belirleyici; hikâye promptu yedi mutlak kural
içeriyor ve bunların ihlali doğrudan ürün hatası.

Maliyet: 1M girdi token 5 USD, 1M çıktı token 25 USD. Bir hikâye ~1500 girdi
+ ~2500 çıktı token → **hikâye başına ~0,07 USD**. Model `STORY_MODEL` ortam
değişkeniyle değiştirilebilir.

---

## 6. TTS sağlayıcı — **AÇIK**

Ölçülen maliyet (6.000 karakterlik bir hikâye, ~6,7 dakika ses):

| Sağlayıcı | Hikâye başına |
|---|---|
| Google Standard | 0,02 USD |
| Google Chirp3 HD | 0,18 USD |
| ElevenLabs Flash v2.5 | 0,30 USD |
| ElevenLabs Multilingual v2 | 0,61 USD |

**Karar için gereken:** Aynı Türkçe metni dört seste de dinlemek. Kalite farkı
maliyet farkını haklı çıkarıyor mu sorusunun cevabı kulakla verilir, tabloyla
değil. İkisi de `app/tts/providers.py` içinde hazır.

**Dikkat:** Hikâye başına LLM maliyeti ~0,07 USD, TTS maliyeti 0,18–0,61 USD.
Yani **maliyetin %70–90'ı sesten geliyor** ve ses henüz hiçbir kullanıcı
tarafından istenmedi. Bu, seslendirmenin MVP'den çıkarılması için somut bir
gerekçe (bkz. madde 7).

---

## 7. Seslendirme MVP'de olmalı mı — **AÇIK, çıkarılması öneriliyor**

Ses, birim maliyetin çoğunu oluşturan ve değeri henüz doğrulanmamış tek
bileşen. Kullanıcının metni okumaya razı olup olmadığı ölçülmeden ses
maliyeti üstlenmek erken. Kod hazır; yayına açılması bir ortam değişkeni
meselesi. Öneri: kapalı betada ses kapalı başlasın, talep gelirse açılsın.

---

## 8. İş modeli ve platform — **AÇIK, planla çelişki var**

Plan iki karar öneriyor ve bunlar birbiriyle uyuşmuyor:

- Bölüm 13: "tek seferlik ücretli hediye ürünü"
- Bölüm 2: "sadece iOS, native Swift"

App Store'da dijital içerik satışı IAP zorunluluğu getirir (%15–30 komisyon),
hediye alan kişinin uygulama indirmesini gerektirir ve planın öngördüğü tek
moat olan viral paylaşımı zorlaştırır. Hediye modeli seçilirse web + Stripe
daha uygun kanal.

**Bu karar verilene kadar:** Backend her iki senaryoya da hazır — API
istemciden bağımsız, iOS uygulaması yalnızca bir istemci.

---

## 9. Prompt sürümleme — **karar verildi (yeni)**

Her hikâyeyle model adı, `PROMPT_VERSION` ve token sayıları saklanıyor.
Bunlar olmadan prompt değişikliğinin çıktıyı iyileştirip iyileştirmediği
ölçülemez ve hikâye başına gerçek maliyet bilinemez.

---

## 10. Veri kalıcılığı — **HENÜZ YAPILMADI**

Plan PostgreSQL + S3 öngörüyordu. Şu an hiçbir şey saklanmıyor; API durumsuz.
Hesap zorunlu olmadığı sürece `User` tablosuna gerek yok. Kapalı beta için
SQLite + yerel dosya yeterli; PostgreSQL ancak eşzamanlı kullanıcı sayısı
anlamlı hale gelince gerekir.
