# Örnek: 1 Şubat 2004, Afyonkarahisar, 07:30

> **Nasıl üretildi:** `prompts.py` v3.2.0 sistem promptu ve motorun gerçek
> çıktısı kullanılarak Claude tarafından elle yazıldı (projede API anahtarı
> tanımlı olmadığı için `/api/hikaye` canlı çalıştırılamıyor). Bu dosya,
> aynı haritayı GPT'nin nasıl anlattığıyla karşılaştırmak için var.

## Karşılaştırma: GPT ne dedi, gerçek ne

| GPT'nin iddiası | Motorun hesabı | Durum |
|---|---|---|
| Güneş Kova | Kova 11°41' | ✅ doğru (tarihten bilinir) |
| Ay **Balık** | **İkizler 13°51'** | ❌ yanlış |
| Yükselen **Oğlak** | **Kova 18,8°** | ❌ yanlış |
| Venüs özgürlükçü burçta | **Balık 21°09'** | ❌ yanlış |

GPT metninin en kişisel hissettiren üç paragrafı — Balık Ay'ı, Oğlak
Yükselen'i, özgürlükçü Venüs — **başka bir haritayı** anlatıyor.

## Gerçek harita

```
Güneş    Kova 11°41'     12. ev      Ay       İkizler 13°51'   4. ev
Merkür   Oğlak 21°18'    12. ev      Venüs    Balık 21°09'     1. ev
Mars     Koç 28°37'       2. ev      Jüpiter  Başak 17°39' R   7. ev
Satürn   Yengeç 7°25' R   5. ev      Uranüs   Balık 1°36'      1. ev
Neptün   Kova 12°49'     12. ev      Plüton   Yay 21°30'      10. ev

Yükselen : Kova 18,8°     Tepe : Yay 5,7°
Element  : Ateş 2, Toprak 2, Hava 3, Su 3   (dengeli — eksik element yok)
```

**Motorun bulduğu ender yapılar:**

| Belirginlik | Yapı |
|---|---|
| **çok belirgin** | Merkür–Venüs altmışlığı neredeyse tam: sapma **0,16°** |
| **çok belirgin** | Venüs–Plüton karesi neredeyse tam: sapma **0,36°** |
| belirgin | Güneş, Yükselen'e 7,1° — **gün doğumunda doğmuş** |
| belirgin | Neptün, Yükselen'e 6,0° ve Güneş'e **1,1°** — görünmez |
| belirgin | 12. evde üç gök cismi: Güneş, Merkür, Neptün |
| belirgin | Harita yöneticisi Satürn, 5. evde, gerilemede |

---

## IŞIĞIN İÇİNDE DOĞAN

1 Şubat 2004 sabahı, Afyonkarahisar üzerinde. Yerel saat yedi buçuk,
evrensel zamanda beş buçuk.

O dakikada Güneş yeni doğmuştu. Doğu ufkunun yedi derece üstündeydi; yani
birkaç dakika önce çıkmıştı ve ışık henüz her yere yayılmamıştı. Kova
burcunun on birinci derecesindeydi.

Onunla birlikte bir tane daha yükselmişti. Neptün, ufkun altı derece
üstünde, Güneş'e yalnızca bir derece uzakta. Bu şu demek: Neptün o sabah
tam olarak oradaydı ve tam olarak görülemezdi. Bir derece, Güneş'in
kendi genişliğinin iki katı bile değildir. O hafta boyunca gökyüzüne
bakan hiç kimse Neptün'ü göremedi, çünkü Güneş onu yutmuştu.

Ay, İkizler burcunun on dördüncü derecesindeydi ve dolunaya doğru
büyüyordu. Dünya'ya en yakın gezegen Venüs'tü: bir nokta on iki astronomi
birimi.

Buraya kadarı ölçümdür; her satırı başka bir efemeris yazılımıyla
doğrulanabilir. Bundan sonrası değildir. Ama anlatılacak olan başka bir
gökyüzü değil — aynı diziliş, ikinci kez bakılmış hâli.

---

Şimdi o on gök cismini bir ülkenin sakinleri say. Sen o ülkeye kapı tam
açılırken girdin.

Çoğu kişi ülkeye girdiğinde kapı çoktan açıktır ya da hâlâ kapalıdır.
Seninki tam o anda açıldı. Güneş de aynı anda içeri giriyordu, ufkun yedi
derece üstünde, senden birkaç adım önde. İkiniz aynı eşikten geçtiniz ve
ışık ikinizin de üstündeydi.

Ama yalnız değildiniz. Bir üçüncü vardı ve onu görmedin.

Neptün seninle aynı dakikada geçti eşiği — Güneş'e bir derece uzakta,
o kadar yakın ki kendi gölgesi bile yoktu. Sen içeri girerken o da
giriyordu. Yıllarca ülkede yürüdün ve arkanda birinin daha yürüdüğünü
duydun. Döndüğünde kimseyi göremedin. Bu, orada kimse olmadığı anlamına
gelmiyordu; ışığın fazla olduğu yerde bazı şeylerin görünmediği anlamına
geliyordu.

Kapının hemen arkasında bir oda vardı: geri çekilme odası. İçeride üç
kişi oturuyordu — Güneş, Merkür ve o görünmeyen. Ülkenin ağırlık merkezi
kapıda değil, kapının arkasındaki bu odadaydı. Dışarıdan gelen kapıyı
görüyordu, odayı görmüyordu. Sen odaya her girdiğinde kimse başını
kaldırmadı; senin gelmen odanın bir parçasıydı, olay değildi.

Odadan çıkıp ülkenin geri kalanına yürüdün.

Yolda ikisine rastladın ve birbirlerini nasıl bu kadar kolay anladıklarına
şaştın. Merkür — Oğlak burcunun yirmi birinci derecesinde — ve Venüs —
Balık burcunun yirmi birinci derecesinde. Aralarındaki açı tam altmış
dereceydi; sapma bir derecenin altıda birinden azdı. Ülkedeki en düzgün
şey buydu. Biri bir şey söylüyor, öteki daha cümle bitmeden başını
sallıyordu. Aralarında hiç tartışma çıkmadı, çünkü tartışacak bir mesafe
yoktu.

Sonra aynı Venüs'ün başka biriyle hiç anlaşamadığını gördün.

Plüton, ülkenin en yüksek yerinde oturuyordu — Yay burcunun yirmi birinci
derecesinde, her şeyi parçalarına ayırıp yeniden kuran kişi. Venüs ile
arasındaki açı tam doksan dereceydi ve sapma bir derecenin üçte birinden
azdı. Bu ikisi aynı anda haklı olamazdı ve ikisi de bunu biliyordu. Venüs
bir şeyi saklamaya değer buluyor, Plüton onu söküyordu. Her karşılaşmada
biri diğerini yavaşlattı.

Tuhaf olan şuydu: Venüs iki ilişkiyi de aynı anda taşıyordu. Merkür'le
kusursuz anlaşan kişiyle, Plüton'la hiç anlaşamayan kişi aynı kişiydi.
Ülkede bunu garipseyen olmadı; garipseyen sendin.

Ülkeyi yönetenin Satürn olduğunu söylediler — kapı Kova işaretini
taşıyordu ve yönetim ona düşmüştü. Onu aramaya gittin ve tahtta bulamadın.
Yengeç burcunun yedinci derecesindeydi, yani ülkenin oyun bölgesinde;
sayan, ölçen, gerektiğinde hayır diyen kişi orada bir şeyler yapıyordu.
Üstelik geri yürüyordu. Neden yönetmediğini sorduğunda cevap vermedi, bir
adım geriledi ve elindeki işe devam etti.

Ülkede hiçbir madde eksik değildi. Ateş iki, toprak iki, hava üç, su üç.
Çoğu ülkede biri hiç bulunmaz ve o ülkenin bütün hikâyesi eksik olanın
etrafında döner. Seninkinde dördü de vardı. Bu kolaylık gibi görünür ama
değildi: eksik bir şey olmadığı için aranacak bir şey de yoktu, ve
aranacak bir şeyi olmayan biri nereye gideceğine kendi karar vermek
zorundadır.

Sen de ülkenin ortasında durdun ve kimse sana ne yapman gerektiğini
söylemedi.

Sabah oldu. Işık ufuktan yayıldı ve önce Güneş'i, sonra seni, sonra
görünmeyeni aydınlattı. Üçünüz aynı eşikten geçmiştiniz ve ikiniz
görünüyordunuz.

---

*Bu masal kurgudur. Yukarıdaki gök cismi konumları gerçek astronomik
hesaplamadır; onlara yüklenen anlam değildir.*

---

## Ne yapıldı, ne yapılmadı

| GPT metni | Bu metin |
|---|---|
| "Sıradan bir yolcu olarak değil, bilgelikle donanmış bir gezgin olarak gelmişti" | *(övgü — yazılmadı)* |
| "Kaderinde insanlığa ilham olmak vardı" | *(kehanet — yazılmadı)* |
| "Belki bir gün ona eşlik edebilecek biriyle tanışacak" | *(kehanet — yazılmadı)* |
| "Bir masal değil, yıldızların yazdığı bir hakikat" | *(doğrudan yanlış — yazılmadı)* |
| "Balık Ay'ı kalbini deniz kadar derin yapmıştı" | Ay gerçekte İkizler'de; o paragraf hiç kurulmadı |
| "Zihni çağlarının ötesindeydi" | *(aynı burçtaki herkes için yazılabilir — yazılmadı)* |

Buna karşılık **sıcaklıktan vazgeçilmedi**. Metin doğrudan kişiye
konuşuyor, duyulara yazıyor, ve duygusal olarak açık:

- "Seninki tam o anda açıldı."
- "Arkanda birinin daha yürüdüğünü duydun. Döndüğünde kimseyi göremedin."
- "Garipseyen sendin."
- "Kimse sana ne yapman gerektiğini söylemedi."

Bunların hiçbiri kişi hakkında **hüküm** değil; hepsi bir **sahne**. Ve
her biri veriden çıkıyor:

| Cümle | Dayanağı |
|---|---|
| "Kapı tam açılırken girdin" | Güneş Yükselen'e 7,1°, gün doğumu |
| "Arkanda birinin yürüdüğünü duydun" | Neptün Güneş'e 1,1° — görünmez |
| "Ülkenin ağırlık merkezi kapının arkasındaki oda" | 12. evde üç gök cismi |
| "Tartışacak bir mesafe yoktu" | Merkür–Venüs 0,16° |
| "Aynı anda haklı olamazlardı" | Venüs–Plüton 0,36° kare |
| "Aranacak bir şey yoktu" | Element dengesi 2/2/3/3, eksik yok |
| "Tahtta bulamadın" | Yönetici Satürn 5. evde, gerilemede |
