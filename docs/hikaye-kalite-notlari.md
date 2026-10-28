# Hikâye kalite notları

Şablon motoru (`--sablon`) için günlük inceleme kaydı. Aynı haritayı tekrar deneme.

## 24 Ekim 2026

Denenen haritalar (tarih saat il):
- 1980-07-15 13:30 Mersin
- 2001-01-19 02:15 Sivas
- 1994-04-06 18:40 Denizli

Bulgu: Gündüz kapanışı "Gökyüzü açıktı ve boştu" hava durumu iddiası kuruyordu
(19 ve 21 Ekim'de de not edilmişti) ve gündüz için "boş" yanlış. Düzeltme:
`KAPANISLAR[0]` artık "Gün ışığı hepsini örtmüştü" diyor. Test:
`test_kapanislar_hava_durumu_iddiasi_kurmaz`.

Açık gözlemler:
- Sivas 2001: Ay ufkun altındayken "Kapıda Ay da vardı" denirken Ay'ın henüz
  doğmadığı açılışta söylenmişti; ikisi birbirine çarpmıyor ama sahne "ikisini
  aynı bakışta göremezdin" ile çelişmeyecek şekilde kalıyor.
- Sivas/Denizli: "Ülkeden geçen dümdüz bir yol" sahnesi iki hikayede aynı
  iskeleti taşıyor (orb 0.4 "yarım dereceden azdı").
- Mersin: "Mars ... Geldiği yerde kimseyi bulamaz" geniş zaman, anlatı geçmişte.

## 23 Ekim 2026

Denenen haritalar (tarih saat il):
- 1988-03-14 07:20 Kars
- 1999-08-11 11:05 Rize
- 1976-11-02 22:10 Edirne
- 2010-05-27 16:40 Antalya (genç ton)

Bulgu: Kars'ta "Mars yine oradaydı" cümlesi geliyordu ama Mars önceki sahnede
(kâse) hiç anılmamıştı; zincir bağlantısı dayanaksızdı.
Düzeltme: `motor.uret` "yine/tekrar" girişini yalnızca cisim önceki sahnenin
metninde geçiyorsa ekliyor. Test: `test_yine_baglantisi_anilmamis_cisim_icin_yazilmaz`.

Açık gözlemler:
- "Gökyüzünde Plüton gerileme hareketindeydi: ... görünüyorlardı" — tek cisimde
  çoğul fiil.
- Gündüz haritalarında (Rize 11:05, Antalya 16:40) kapanış "Gökyüzü açıktı ve
  boştu" diyor; Güneş yukarıdayken boş demek tuhaf.
- Edirne: "Merkür, Uranüs ile Mars Güneş'e o kadar yakındı" — virgül/ile karışık
  sayım okunuşu bulandırıyor.
- Antalya T-kare: Güneş–Neptün karesi üstteki açı listesinde görünmüyor, sahne
  Neptün'ün "ikisiyle birden" çekiştiğini söylüyor; orb eşiği doğrulanmalı.

## 21 Ekim 2026

Denenen haritalar (tarih saat il):
- 1982-11-11 08:25 Sinop
- 1977-04-23 12:50 Adana
- 2019-07-07 20:10 Hatay (çocuk tonu)
- 1950-12-01 04:40 Çorum
- 1993-03-30 15:35 Tekirdağ

Bulgu: Sinop 1982'de birden çok cisim Güneş'in ışığında kaybolduğunda cümle
"Haritada tam olarak oradaydılar ve gökyüzünde tam olarak görünmüyorlardı"
diye bitiyordu (19 Ekim'de Samsun'da da görülen yapay kalıp). Düzeltme:
`gokyuzu.gorunmeyenler` artık "Haritada yerlerinde duruyorlardı; gökyüzünde ise
hiçbiri seçilemiyordu" yazar. Test: `test_gorunmeyen_cisimler_bozuk_kalibi_kullanmaz`.

Açık gözlemler:
- Sinop 1982: gökyüzünün 258 derecelik kısmı boşken "Ülkenin bir yarısında
  kimse yoktu" deniyor; boşluk yarıdan çok büyükse "yarısında" yanlış.
- Kapanış "Gökyüzü açıktı ve boştu" (sözlük.py) hava durumu iddiası; Sinop ve
  Tekirdağ'da yine çıktı.
- "Ay ile Plüton hiç buluşmadılar" (Hatay, Ay–Plüton üçgen) ile "ikisinin
  arasından geçtin" gibi kapı/yol kalıpları üç hikayede de aynı iskeleti taşıyor.
- Çorum 1950: Ay–Plüton kavuşumu hem yol bölümünde hem kapıda (Ay Tepe'de)
  tekrar anlatılıyor.

## 20 Ekim 2026

Denenen haritalar (tarih saat il):
- 1991-05-27 10:35 Trabzon
- 1965-09-14 19:50 Konya
- 2012-03-02 05:15 Mardin
- 1989-01-08 21:40 Bursa
- 2004-08-19 15:05 Malatya

Bulgu: Malatya 2004'te Ay Tepe'de, Plüton Yükselen'deydi; metin "Plüton da
oradaydı, birkaç adım ötede" diyordu (Konya 1965'te Ay Yükselen, Venüs Batan:
aynı hata). Düzeltme: `bolum_kapi`, ikinci cisim başka açısal noktadaysa
"Yalnız değildi. Kapıda Plüton da vardı; ikisini aynı bakışta göremezdin"
yazar. Test: `test_farkli_acisal_noktalardaki_ikinci_cisim_orada_denmez`.

Açık gözlemler:
- Konya 1965: Ay "doğu ufkunun 2 derece üstünde" (olgusal bölüm) ile "1,5
  derece ötede" (kapı bölümü) farklı yuvarlanıyor.
- Malatya 2004: Merkür toplantının üyesi, sonra "Bir de Merkür vardı" ve
  "Merkür ile tekrar karşılaştın" ile üç kez geçiyor (retro sahnesi toplantıya
  bakmıyor).
- Bursa 1989: hikâye çok kısa (188 kelime), yalnızca meclis + kapanış.

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

## 22 Ekim 2026

Denenen haritalar (tarih saat il):
- 1985-06-18 14:30 Şanlıurfa
- 1970-10-29 09:15 Ordu
- 2005-02-08 20:45 Balıkesir
- 1992-12-03 03:50 Hakkari

Bulgu: Hakkari 1992'de büyük üçgen sahnesi "Ay, Mars, Plüton birbirine üçgen
açı yapıyor" diyordu; geçmiş zamanlı anlatıda şimdiki zaman kopukluğu.
Düzeltme: `motor.bolum_ucgen` etiketi "açı yapıyordu"ya çeviriyor. Test:
`test_buyuk_ucgen_sahnesi_gecmis_zamanda_anlatir`.

Açık gözlemler:
- Meclis sahnesi "göğün aynı dar diliminde" diyor ama Hakkari'de Venüs–Satürn
  arası ~20° (dar değil); sıkılık eşiği gözden geçirilmeli.
- "gökyüzündekilerin hepsi görünmüyordu" (gece sahnesi) belirsiz okunuyor.

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

## 25 Ekim 2026

Denenen haritalar (tarih saat il):
- 1978-09-23 11:25 Kırklareli
- 2000-04-14 21:55 Giresun
- 1963-01-07 06:45 Niğde

Bulgu: Kırklareli'de Satürn önce kulede anılıyor, sonra yalnız-cisim sahnesi
"Yolun kenarında birine rastladın: Satürn" diyerek aynı kişiyi ikinci kez
tanıtıyordu. Düzeltme: `Baglam.onceki_metin` eklendi; `bolum_yalniz` cisim
önceden anıldıysa "Satürn'ü daha önce görmüştün; ama…" diyor. Test:
`test_yalniz_cisim_daha_once_anildiysa_yolda_rastlanmaz`.

Açık gözlemler:
- Giresun'da "Ülkede akış yoktu… Yolun geri kalanında onu aradın" (su yok)
  belirsiz; "Yol" önceki sahnede kurulmadığı için kopuk.
- Kırklareli: Venüs "kapıda" ama Satürn'ün kuledeki sahnesine eklemlenme
  cümlesi ("ikisini aynı bakışta göremezdin") okuru yorabiliyor.
- LLM kıyası bu çalışmada yapılmadı (GEMINI_API_KEY yok).

## 26 Ekim 2026

Denenen haritalar (tarih saat il):
- 1974-02-17 09:50 Kütahya
- 2006-10-05 23:20 Zonguldak
- 1986-06-29 05:35 Bitlis

Bulgu: Eksik element paragrafı "Yolun geri kalanında onu aradın" diyordu;
"Yol" sonraki sahnelerde kuruluyor, bu yüzden Zonguldak ve Bitlis'te kopuk
okunuyordu (25 Ekim açık gözlemi). Düzeltme: "Ülkeyi baştan sona dolaşıp onu
aradın." Test: `test_eksik_element_henuz_kurulmamis_yola_gonderme_yapmaz`.

Açık gözlemler:
- Kütahya'da "kapalı devre" Satürn, Jüpiter, Uranüs diye anılıyor; açı listesinde
  gerçek üçgen Güneş-Satürn-Uranüs (Jüpiter-Satürn sapması ~2.4°); tutarlılık
  kontrol edilmeli.
- Zonguldak ve Bitlis'te "Ay ile Plüton / Neptün ile Plüton" sahnesinde Ay'ın
  ve Neptün'ün derece cümlesi bire bir aynı kalıpta (tekrar eden şablon).
- LLM kıyası yapılmadı (GEMINI_API_KEY yok).

## 27 Ekim 2026

Denenen haritalar (tarih saat il):
- 1981-03-11 16:10 Erzurum
- 1997-08-25 01:40 Mardin
- 2010-11-30 12:05 Edirne
- 1968-05-02 19:30 Sivas

Bulgu: Sivas 1968'de Mars Alçalan'da, Neptün Yükselen'de (zıt uçlar) olduğu
hâlde metin "Yalnız değildi. Kapıda Neptün de vardı" diyordu; Edirne'de de
Güneş kulede, Neptün kapıda iken aynı kalıp, hemen ardından "Güneş'in
ülkeyle hiçbir bağı yoktu" ile çelişiyordu. Düzeltme: farklı açısal noktada
"Başka bir noktada da biri bekliyordu." Test:
`test_farkli_acisal_noktadaki_ikinci_cisim_yalniz_degildi_demez`.

Açık gözlemler:
- Edirne: "Güneş'i daha önce görmüştün" ardından hemen "Güneş yine oradaydı"
  art arda iki gönderme.
- Edirne açılışında Neptün ve Chiron için "henüz doğmamıştı… ufkun 5 derece
  altında" kalıbı iki kez bire bir tekrar ediyor.
- Mardin: Merkür gerileme sahnesinde "peşinden gitmedin" sonra "yanına
  oturdun" çelişkili.
- LLM kıyası yapılmadı (GEMINI_API_KEY yok).

## 28 Ekim 2026

Denenen haritalar (tarih saat il):
- 1989-07-14 03:20 Van
- 1972-12-09 14:40 Antalya
- 2003-02-21 22:05 Samsun
- 1994-09-01 07:15 Hatay

Bulgu: Hatay'da en dar açı (Mars–Jüpiter üçgeni) önce "kapalı devre"
sahnesinde, sonra "dümdüz yol" sahnesinde aynı iki cisimle yeniden
anlatılıyordu. Düzeltme: `bolum_bag`, çift önceki metindeki "kapalı bir devre
buldun" cümlesinde geçiyorsa sahneyi atlıyor. Test:
`test_kapali_devredeki_cift_yol_sahnesinde_ikinci_kez_anlatilmaz`.

Açık gözlemler:
- Van/Antalya: yönetici/ağırlık merkezi sahnesinde, kapıda zaten tanıtılan
  cisim (Uranüs, Mars) "Ortaklık bölgesinde toplanmıştı" listesinde yeniden
  sayılıyor; tanıtılmış kişi yabancı gibi tekrar anılıyor.
- Samsun: "Venüs'ü daha önce görmüştün" — Venüs yalnızca açılıştaki "en
  yakın gezegen" cümlesinde geçiyor, sahnede değil.
- LLM kıyası yapılmadı (GEMINI_API_KEY yok).
