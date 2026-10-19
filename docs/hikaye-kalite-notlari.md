# Hikâye kalite notları

Şablon motoru (`--sablon`) için günlük inceleme kaydı. Aynı haritayı tekrar deneme.

## 19 Ekim 2026

Denenen haritalar (tarih saat il):
- 1983-04-09 14:20 Kayseri
- 2008-12-25 22:05 Samsun
- 1972-06-17 07:40 Diyarbakır
- 1996-10-03 17:15 Eskişehir
- 1958-02-28 01:30 Aydın

Bulgu: Diyarbakır 1972'de Venüs önce toplantının (Güneş, Merkür, Venüs, Satürn)
üyesi olarak, sonra "Ülkede bir kişi daha vardı ve onu hiç göremedin: Venüs"
diye geçiyordu (tekrar + çelişki). Düzeltme: `bolum_gomulu`, cisim meclis
üyesiyse bölümü yazmaz. Test: `test_toplantidaki_cisim_gomulu_kisi_olarak_ikinci_kez_anilmaz`.

Açık gözlemler:
- Samsun 2008: "Yolun burasında Jüpiter ile tekrar karşılaştın" — Jüpiter
  metinde daha önce anılmamıştı (zincir girişi yalnızca omurga ortaklığına bakıyor).
- Samsun 2008: "Haritada tam olarak oradaydılar ve gökyüzünde tam olarak
  görünmüyorlardı" kalıbı yapay.
- Eskişehir 1996 (17:15, Ekim): "Gökyüzü açıktı ve boştu" kapanışı gündüz için
  belirsiz bir iddia (hava durumu uydurma).

## 18 Ekim 2026

Denenen haritalar (tarih saat il):
- 1999-12-31 00:10 Antalya
- 1975-05-05 12:00 Van
- 2015-02-14 16:50 Gaziantep
- 1968-08-22 03:30 Erzurum

Bulgu: Erzurum 1968'de Merkür–Jüpiter kavuşumu "Biri Başak burcunun 12.
derecesinde, öteki Başak burcunun 12. derecesinde duruyordu" diyordu (aynı burç
ve derece iki kez). Düzeltme: `motor._iki_konum`; aynı burçta "İkisi de Başak
burcunun 12. derecesinde", farklı derecede "İkisi de X burcundaydı: biri a.,
öteki b. derecesinde". Test: `test_ayni_burctaki_kavusum_tekrarlanan_konum_yazmaz`.

Açık gözlem: "Tam açıdan sapma yarım dereceden azdı" kalıbı 0.05° ile 0.49° için
aynı; çok dar açıda (örn. <0.1°) daha çarpıcı bir ifade seçilebilir.

## 17 Ekim 2026

Denenen haritalar (tarih saat il):
- 1987-03-14 06:20 Rize
- 1994-11-02 23:45 Kars
- 2001-07-21 13:10 Muğla
- 1979-01-30 04:05 Sivas (üretildi, okunmadı)
- 2010-09-09 18:30 Edirne (üretildi, okunmadı)

Bulgu: Kars 23:45 (Güneş 3. evde, ufkun altında) hikâyesi "o sabah dördü birden",
"Kars üstünde gündüzdü ve hiçbiri görünmüyordu" ve "gündüz kısa bir süre karardı"
diyordu. Gece doğanlar için astronomik olarak yanlış. Ayrıca "Sabah onu
gökyüzünde görebilseydin" ifadesi her saat için sabit "sabah" varsayıyordu.

Düzeltme: `Baglam.gunduz` (Güneş 7-12. evde mi; saat yoksa None) ve `Baglam.an`
eklendi. Kapanışlar gündüz/gece/belirsiz olarak üç havuza ayrıldı, başlık
yedeği ve tutulma sahnesi de buna bağlandı. Testler: `test_sablon.py` sonu.

Açık gözlemler (sonraki günler):
- Tutulma sahnesi "Ay Güneş'in önünden geçti" diyor ama desen yalnızca ±12°
  yeniay + düğüm yakınlığına bakıyor; gerçek tutulma anı saatlerce kayabilir.
- "Muğla 2001" hikâyesinde Jüpiter üç kişilik toplantıdan sonra tekrar anılıyor
  (zincir girişi var ama "Jüpiter yine oradaydı" ardından Merkür'ün gelmesi kopuk).

## LLM kıyası — 17 Ekim 2026 (elle, bir kerelik)

Harita: 2003-07-03 09:00 Denizli, ad "Elif". Aynı haritadan hem `--sablon`
hem gerçek Gemini (`gemini-3.5-flash`, ücretsiz katman) hikâyesi üretildi.

- **Şablon:** 339 kelime, tam, "Topraksız Ülke" metaforuyla kurulu bir
  anlatı (omurga zinciri, kapanış, vb). Tamamlandı.
- **Gemini:** 109 kelime, **yarım cümlede kesildi**, gerçek bir hikâye
  kurmadı — haritadaki konumları düz liste gibi art arda saydı ("Güneş
  Yengeç burcunun 10.9 derecesinde, Ay Aslan burcunun...").
- **İlk sonuç (YANLIŞ ÇIKTI, bkz. düzeltme aşağıda):** Tek örnekten "şablon
  LLM'den iyi" sonucuna varıldı. Bu hatalıydı — tek örnekle model kalitesi
  hakkında hüküm verilemez, model rastgeleliği var.
- **Yan bulgu (düzeltildi, commit 3b073e1):** `config.py`'deki varsayılan
  Gemini modeli (`gemini-3-flash`) artık mevcut değildi, `gemini-3.5-flash`
  ile değiştirildi.

### Düzeltme ve ikinci tur (aynı gün, 17 Ekim 2026)

İlk denemenin yarım kesilme sebebi ham httpx isteğiyle teşhis edildi:
`finishReason` ve `usageMetadata` doğrudan okundu. İkinci çağrı (AYNI
harita, AYNI prompt) `finishReason: STOP` ile TAM, 1000+ kelimelik,
"ANLATI OMURGASI" zincirini doğru kullanan, gerçek dereceleri dokuyan
düzgün bir masal üretti. Yani ilk kesilme model rastgeleliğiydi (Gemini
3.5 "düşünme" modunda ~5000-6000 `thoughtsTokenCount` harcıyor ama bu
görünmez token bütçesi değil, `candidatesTokenCount` ayrı sayılıyor —
sistemik bir token-limiti sorunu yoktu).

Gerçek, tekrarlanabilir zayıflık: model "BİRİNCİ HAREKET" (gerçek
gökyüzü) bölümünde 12 gök cisminin TAMAMINI yazıyla hecelenmiş
derece/dakikayla ("Aslan burcunun on dokuz derece beşinci dakikası")
tek tek sayıyordu — şablon motorunun aksine seçici değildi, veri
dökümü gibi okunuyordu.

**Düzeltme (prompt sürüm 3.3.0, commit sonrası):** `SYSTEM_PROMPT`'a
"SEÇİCİ OL" talimatı eklendi: ilk hareket yalnızca omurga duraklarından
2-3'ünü ve Yükselen'i anıp 3-4 cümleyi geçmesin. İkinci bir haritayla
(Trabzon, 1991-11-20) test edildi: açılış artık 12 değil 4 gök cismiyle
sınırlı — iyileşme var ama tam hedefe ulaşmadı (hâlâ "nokta dört
derecesi" gibi hecelenmiş ondalık kullanıyor). Sonraki günlerde daha
fazla örnekle izlenmeli.

**Güncel sonuç:** Gerçek LLM (doğru promptla) şablon motoruna kıyasla
rakip, hatta bazı yönlerden (gerçek dil akıcılığı, çeşitlilik) daha
güçlü olabilir. Kesin hüküm için daha fazla örnek gerekir; bulut
rutinine anahtar eklenemediği için bu örnekleme şimdilik elle
sürdürülmeli.
- **Not:** Bulut rutinine API anahtarı secret olarak eklenemiyor
  ("trigger configs are persisted and replayed on every fire" - RemoteTrigger
  API'si bunu açıkça reddediyor). Yani bu kıyas otomatikleşmedi, kullanıcı
  isterse elle tekrarlayabilir (`LLM_SAGLAYICI=gemini GEMINI_API_KEY=... 
  STORY_MODEL=gemini-3.5-flash python backend/tools/cli.py ...`).
