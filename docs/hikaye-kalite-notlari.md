# Hikâye kalite notları

Şablon motoru (`--sablon`) için günlük inceleme kaydı. Aynı haritayı tekrar deneme.

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
- **Sonuç:** Bu denemede şablon motoru gerçek LLM'den daha iyi bir metin
  üretti. `GEMINI_API_KEY` otomatik gunluk rutine eklenemiyor (bkz. not
  asagida), yani bu kiyas şimdilik elle yapılmalı. `prompts.py`'nin
  omurga/nadirlik ile seçilmiş olguları LLM'e ne kadar iyi aktardığı
  incelenmeli — ham harita listesi vermek yerine şablon motorunun
  kullandığı "sahne" yapısını prompt'a taşımak gerekebilir.
- **Yan bulgu (düzeltildi, commit 3b073e1):** `config.py`'deki varsayılan
  Gemini modeli (`gemini-3-flash`) artık mevcut değildi, `gemini-3.5-flash`
  ile değiştirildi.
- **Not:** Bulut rutinine API anahtarı secret olarak eklenemiyor
  ("trigger configs are persisted and replayed on every fire" - RemoteTrigger
  API'si bunu açıkça reddediyor). Yani bu kıyas otomatikleşmedi, kullanıcı
  isterse elle tekrarlayabilir (`LLM_SAGLAYICI=gemini GEMINI_API_KEY=... 
  STORY_MODEL=gemini-3.5-flash python backend/tools/cli.py ...`).
