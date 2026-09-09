# Örnek çıktı — prompt v2.0.0

> **Bu metin nasıl üretildi:** `backend/app/story/prompts.py` (v2.0.0) sistem
> promptu ve `backend/app/story/brief.py`'nin ürettiği gerçek brifing
> kullanılarak yazıldı. Girdi verisi motorun gerçek çıktısıdır
> (3 Temmuz 2003, 09:00, Denizli). **Metin, boru hattı çalıştırılarak değil,
> Claude tarafından aynı promptla elle üretildi** — projede henüz
> `ANTHROPIC_API_KEY` tanımlı olmadığı için `/api/hikaye` ucu canlı
> çalıştırılamadı. Bu dosya, canlı çıktının karşılaştırılacağı ölçüttür.
>
> **v1.0.0'a göre ne değişti:** İlk sürüm kişiyi hikâyenin tamamen dışında
> tutuyordu ve sonuç, veriden türetilmiş ama kimseye ait hissettirmeyen bir
> mitti. Ayrıca hikâyenin temasını üç gerileyen dış gezegene kurmuştu — oysa
> dış gezegenler yılın yaklaşık yarısında gerilemededir, yani milyonlarca
> insanda aynıdır. Buna karşılık haritanın **en belirgin yapısını** kaçırmıştı:
> Jüpiter'in Yükselen'e 1,1 derece uzaklıkta oluşunu.
> [`story/signature.py`](../backend/app/story/signature.py) artık bu ayrımı
> hesaplayıp modele veriyor.

## Girdi (motorun gerçek çıktısı)

```
Tarih ve yer : 03.07.2003, Denizli, Türkiye
Yerel saat   : 09:00 (UTC+3, yaz saati) — Evrensel: 06:00 UTC

Güneş    Yengeç 10°55'   11. ev      Ay       Aslan 22°07'    1. ev
Merkür   Yengeç 8°15'    11. ev      Venüs    İkizler 28°11'  11. ev
Mars     Balık 5°56'      7. ev      Jüpiter  Aslan 18°22'   12. ev
Satürn   Yengeç 3°46'    11. ev      Uranüs   Balık 2°33' R   7. ev
Neptün   Kova 12°37' R    6. ev      Plüton   Yay 18°00' R    5. ev

Yükselen : Aslan 19.49°        Element : Ateş 3, Toprak 0, Hava 2, Su 5
```

### Motorun çıkardığı imza (hikâyenin kurulduğu yer)

| Belirginlik | Yapı |
|---|---|
| **çok belirgin** | Jüpiter, Yükselen'e **1,1°** uzaklıkta |
| **çok belirgin** | Ay, Yükselen'e **2,6°** uzaklıkta |
| **çok belirgin** | Jüpiter–Plüton üçgeni neredeyse tam: sapma **0,37°** |
| **çok belirgin** | 11. evde **dört** gök cismi: Güneş, Merkür, Venüs, Satürn |
| belirgin | Haritanın yöneticisi Güneş, 11. evde (o kalabalığın içinde) |
| belirgin | Hiçbir gök cismi **Toprak** elementinde değil |
| ~~yaygın~~ | ~~Gerileyen dış gezegenler~~ → *üzerine hikâye kurulmayacak* |

---

## KAPIDA DURAN İKİSİ

3 Temmuz 2003 sabahı, Denizli'de saatler dokuzu gösterdiğinde, evrensel zamanda
henüz altıydı; o yıl Türkiye yaz saati uyguluyordu. Gökyüzü açıktı, gündüzdü ve
anlatılacak hiçbir şey görünmüyordu.

Doğu ufkunda, tam o dakikada, Jüpiter yeni yükselmişti. Ufkun bir derece kadar
üstündeydi — birkaç dakika önce çıkmıştı ve gündüzün içinde eriyordu. Ondan üç
buçuk derece geride Ay vardı, henüz doğmamıştı; ufkun altında bekliyordu ve
yaklaşık on dakika sonra o da çıkacaktı. Üç buçuk derece, bir kapı genişliğidir.
İkisi o kapının iki yanındaydı: biri geçmiş, biri geçmemiş.

Güneş, Yengeç burcunun onuncu derecesini yeni aşmıştı, gökyüzünde çoktan
yükselmişti. Merkür ona iki buçuk derece uzaktaydı, neredeyse aynı noktada.
Satürn Güneş'e yalnızca yedi derece mesafedeydi — o hafta boyunca hiç kimse
Satürn'ü göremezdi, çünkü ışığın içinde kaybolmuştu. Venüs, Güneş'in on üç
derece önünden gitmişti; şafaktan biraz önce doğmuş, ilk aydınlıkta silinmişti.

Ve Mars. O sabah Mars, Dünya'ya 0,55 astronomi birimi uzaklıktaydı ve her gün
biraz daha yaklaşıyordu. Aynı yılın ağustosunda 0,37 birime inecek, altmış bin
yıldır olmadığı kadar yakından geçecekti. 3 Temmuz sabahı, o yaklaşmanın tam
ortasındaydı.

Buraya kadarı ölçümdür. Bundan sonrası değildir.

---

Gülheda, o sabah bir ülkeye doğdun ve o ülkenin ilk özelliği bir kapıydı.

Her ülkenin bir kapısı olur — dışarıdan gelen önce oradan bakar, ve bir ülke
hakkındaki ilk şeyi hep o kapıdan öğrenir. Senin ülkende kapının iki yanında
iki figür duruyordu. Dışarıda, eşiği yeni geçmiş olan Jüpiter vardı; içeride,
eşiğe henüz varmamış Ay. Aralarında üç buçuk derece vardı ve ikisi de kendi
seçimiyle orada değildi. Kapı öyle kurulmuştu.

Bunun anlamı şuydu: seni ilk gören, senin adına ilk konuşan bu ikisi oldu. Sen
onları seçmedin. Onlar zaten oradaydılar, sen geldiğinde. Jüpiter kapının
dışında yüksek sesle konuşur, gelenlere ülkenin büyüklüğünden söz eder,
davetkârdır. Ay içeride durur ve gelenin yüzüne bakar. Ülkeye dair ilk izlenim
bu ikisinin toplamıdır ve sen o izlenimin ne yazık ki hiçbir zaman tam sahibi
olmadın; kapı senden önce oradaydı.

Bu, ülkenin ikinci ve daha tuhaf özelliğini doğurur. Ülkenin gerçek sahibi
kapıda değildir.

Ülkeyi yöneten Güneş'ti — kapı Aslan işaretini taşıdığı için yönetim ona
düşmüştü. Ama Güneş kapıda durmuyordu. Güneş, ülkenin çok uzağındaki bir
bölgede, Meclis'teydi: dostlukların kurulduğu, geleceğin tasarlandığı, gelenin
gitmediği yer. Ve orada yalnız değildi. Meclis'te dört kişi vardı.

Güneş ile Merkür yan yana oturuyorlardı, o kadar yakın ki biri cümleye
başladığında öteki bitiriyordu; hangisinin ne söylediğini kimse ayıramazdı.
Venüs biraz uzakta, havanın son sınırında duruyordu — Meclis'e aitti ama
Meclis'in diliyle konuşmuyordu, kendi kelimelerini getiriyordu. Dördüncüsü
Satürn'dü ve Satürn görünmezdi. Güneş'e fazla yakın oturmuştu, ışık onu
yutuyordu. Kararlar alınırken ağırlığı hissediliyor, bir teklif fazla hafifse
birinin sesi olmadan geri çevriliyordu; ama kimse onu göremiyordu. Meclis'te
yıllarca şu tartışıldı: Satürn gerçekten var mı, yoksa Güneş kendi kendine mi
itiraz ediyor? Satürn bu tartışmaya hiç katılmadı. Görünmez olmanın, var
olmamakla aynı şey olmadığını bilenler tartışmaya girmezler.

Yani ülkenin dört sakini tek bir bölgedeydi ve o bölge kapıdan uzaktı. Ülkenin
ağırlık merkezi, kapısının olduğu yerde değildi. Gelenler kapıyı görüyor,
Jüpiter'i duyuyor, Ay'ın baktığını hissediyor ve içeride bir yerlerde asıl işin
döndüğünü bilmiyorlardı. Sen de uzun süre kapıyla Meclis'in aynı ülke olduğuna
inanmakta zorlandın. Aynı ülkeydiler.

Bütün bunların arasından geçen tek bir düz çizgi vardı ve o çizgi kusursuzdu.

Kapının dışındaki Jüpiter ile, ülkenin öbür ucundaki bir bölgede oturan
Plüton'un arasındaydı bu hat. Plüton, yapma ve oyun bölgesinde yaşıyordu:
elinden bir şey çıkarmayı seven, ama çıkardığını bitirmeden bir öncekine dönen
biri. İkisi de aynı dereceden geçen bir hattın üstündeydi ve aralarındaki sapma
bir derecenin üçte birinden azdı. Ülkedeki en kesin, en düzgün, en tereddütsüz
şey buydu. İkisi hiç buluşmadılar. Buluşmalarına gerek yoktu; hat zaten
oradaydı. Kapıda yüksek sesle konuşulan şeyle atölyede sessizce yapılan şey
arasında, kimsenin çekmediği bir çizgi vardı ve o çizgi hiç eğrilmedi.

Ve ülkenin son özelliği, sahip olmadığı şeydi.

Her ülkenin dört maddesi olur: ateş, hava, su, toprak. Sayım yapıldığında su
beş çıktı, ateş üç, hava iki. Toprak sıfır. Bütün ülkede tek bir taş yoktu. Tek
bir tarla, tek bir temel, tek bir duran şey. Yollar vardı ama yolların altında
zemin yoktu; evler vardı ama hiçbiri aynı yerde iki kez bulunmuyordu. Ülkenin
sakinleri bunu bir felaket saymıyorlardı, çünkü başka türlüsünü bilmiyorlardı.
Yalnızca bir alışkanlıkları vardı: bir şey söylerken elleriyle havada bir biçim
çizer, sonra o biçimin dağılmasını beklerlerdi. Toprağı olmayan ülkelerde söz,
kalıcı olabilecek tek şeydir; bu yüzden orada herkes dikkatli konuşurdu.

Zamanla ülke bir şey öğrendi, Gülheda. Toprağı olmayan yerlerde sağlamlık
maddeden gelmez, ilişkiden gelir. Hiçbir şey tek başına duramadığı için her şey
birbirine tutunmak zorundadır. Meclis ayakta kaldı çünkü Güneş ile Merkür aynı
cümleyi söylüyordu. Kapı ayakta kaldı çünkü iki yanında birer kişi vardı. Ve o
düz hat ayakta kaldı çünkü iki ucu da yerinden kımıldamadı.

O sabah, Denizli'nin üstünde, saat dokuzda, bunların hiçbiri görünmüyordu.
Jüpiter doğu ufkunun bir derece üstünde, gündüzün içinde eriyordu. Ay henüz
çıkmamıştı, on dakikası vardı. Satürn ışığın içinde kayboluyordu, Venüs çoktan
silinmişti. Toprak hiçbir yerde yoktu ve bir daha da olmayacaktı.

Sen o kapıdan içeri girdin ve kapı arkandan kapanmadı. Öyle bir kapı değildi.

---

*Bu hikâye kurgudur. Yukarıdaki gök cismi konumları gerçek astronomik
hesaplamadır; onlara yüklenen anlam değildir.*

---

## v1 ile v2 arasındaki fark

| | v1.0.0 | v2.0.0 |
|---|---|---|
| Kişi metinde var mı | Hayır, hiç geçmiyor | Adı 2 kez, ikinci şahıs hitabı 9 kez |
| Hikâyenin omurgası | Gerileyen dış gezegenler (**yaygın**) | Jüpiter/Ay–Yükselen, Jüpiter–Plüton 0,37°, 11. ev yığını (**çok belirgin**) |
| Jüpiter'in Yükselen'e 1,1° yakınlığı | Kaçırılmış | Hikâyenin açılışı ve merkezi |
| Kişi hakkında cümle | Yasak | Serbest, ama veriye bağlanma şartıyla |
| Uzunluk | 848 kelime | 811 kelime — **ikisi de hedefin altında** |

### Çözülmemiş sorun: uzunluk

Yetişkin tonu için prompt **en az 1300 kelime** istiyor; v1 848, v2 811 kelimede
kaldı. Prompt'a "en az" yazmak yetmedi. İki seçenek var:

1. Hedefi gerçekçi bir değere (~850) çekmek — bu uzunluk 6-7 dakikalık ses eder
   ve tek oturuşta dinlenebilir, yani belki hedef baştan yanlıştı.
2. Uzunluğu bölüm bazında zorunlu kılmak: "gövde en az beş paragraf, her paragraf
   en az 150 kelime".

Karar, canlı üretimden birkaç örnek alınmadan verilmemeli. Tek bir örneğe
bakarak prompt ayarlamak aşırı uydurmadır — asıl soru, modelin kendi
çıktılarının da aynı yerde toplanıp toplanmadığı.

### Genellik testi örnekleri

Metindeki kişi hakkındaki cümleler ve dayandıkları yapı:

| Cümle | Dayanağı | Aynı burçtan biri için de yazılabilir mi |
|---|---|---|
| "Seni ilk gören, senin adına ilk konuşan bu ikisi oldu" | Jüpiter 1,1° + Ay 2,6° Yükselen'de; 1. evin teması "ilk izlenim" | Hayır — çoğu haritada Yükselen'de gök cismi yoktur |
| "Ülkenin gerçek sahibi kapıda değildir" | Yükselen Aslan → yönetici Güneş → 11. evde | Hayır — yönetici konumu haritaya özgü |
| "Uzun süre kapıyla Meclis'in aynı ülke olduğuna inanmakta zorlandın" | Kapı (1./12. ev) ile ağırlık merkezinin (11. ev) ayrı oluşu | Hayır |
| "Toprağı olmayan yerlerde sağlamlık ilişkiden gelir" | Toprak 0 + en dar açının üçgen oluşu | Hayır |

Yazılmayanlar: "duygusalsın" (Yengeç Güneş → 700 milyon kişi), "sahne senindir"
(Aslan Yükselen → yaklaşık on ikide bir), "sezgilerin güçlü" (hiçbir veriye
bağlı değil).

### Kural denetimi

| Kural | Durum |
|---|---|
| Birinci hareket doğrulanabilir | Jüpiter ufkun 1,1° üstünde, Ay 2,6° altında (~10 dk sonra doğacak), Satürn 7,2° elongasyon, Mars 0,55→0,37 AU — hepsi motordan doğrulandı |
| En az üç "çok belirgin" yapı taşıyıcı | Dördü de kullanıldı |
| "Yaygın" yapılar tema yapılmadı | Gerileyen dış gezegenler metne hiç girmedi |
| Kehanet yok | Gelecek zamanlı tek ifade yok |
| Verilmemiş veri yok | Yalnızca brifingteki yapılar |
| Tanı yok | Ruh sağlığı/zekâ/karakter kusuru hükmü yok |
| Sesli okumaya uygun | Markdown, madde, parantez içi açıklama yok |
