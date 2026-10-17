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
