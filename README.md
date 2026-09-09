# Gök Hikâyesi

Doğum anındaki gerçek gök cismi konumlarını hesaplayan ve bu veriyi
kişiselleştirilmiş bir hikâyeye dönüştüren uygulama.

Ürünün merkezî iddiası: **gezegen konumları ölçümdür, anlam yüklemesi
kurgudur.** Bu ayrım ekranın altına iliştirilmiş bir feragatname değil,
mimarinin bir parçası — kullanıcıya gösterilen olgusal panel koddan
deterministik üretilir, dil modeli yalnızca kurguyu yazar ve tek bir sayıya
dokunmaz.

## Durum

| Faz | Kapsam | Durum |
|---|---|---|
| 1 | Astronomik hesaplama motoru | ✅ Tamam, üç bağımsız çıpayla doğrulandı |
| 2 | Hikâye üretim katmanı | ✅ Kod tamam — canlı çalıştırma `ANTHROPIC_API_KEY` bekliyor |
| 3 | Seslendirme katmanı | ✅ Kod tamam — canlı çalıştırma TTS anahtarı bekliyor |
| 4 | Backend API (FastAPI) | ✅ Tamam, uçtan uca test edildi |
| 5 | iOS uygulaması (SwiftUI) | ✅ Simülatörde derlenip çalıştırıldı |
| 6 | Kapalı beta, KVKK metinleri | ⬜ Yapılmadı |

75 test geçiyor. Ayrıntı: [docs/durum.md](docs/durum.md)

## Hızlı başlangıç

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt

# Testler (ağ ve API anahtarı gerektirmez)
.venv/bin/python -m pytest backend/tests -q -c backend/pytest.ini --rootdir backend

# Sadece harita, anahtarsız
.venv/bin/python backend/tools/cli.py --tarih 2003-07-03 --saat 09:00 \
    --yer Denizli --sadece-harita

# Sunucu
.venv/bin/python -m uvicorn app.api.main:app --app-dir backend --reload
# http://127.0.0.1:8000/docs
```

Hikâye ve ses için `.env` dosyası:

```
ANTHROPIC_API_KEY=sk-ant-...
TTS_PROVIDER=google          # veya elevenlabs
GOOGLE_TTS_API_KEY=...
```

iOS uygulaması: `open ios/AstroHikaye.xcodeproj` — simülatörde çalışması için
backend'in `127.0.0.1:8000` üzerinde ayakta olması gerekir.

## Yapı

```
backend/
  app/astro/      hesaplama motoru (efemeris, zaman, ev, açı)
  app/geo/        doğum yeri → koordinat (81 il çevrimdışı + Nominatim)
  app/story/      brifing + prompt + üretim
  app/tts/        seslendirme + maliyet
  app/api/        FastAPI uçları
  tools/          CLI ve bağımsız efemeris çapraz kontrolü
  tests/          75 test
  data/ephe/      Swiss Ephemeris veri dosyaları (1800–2399)
  data/jpl/       JPL DE440s (yalnızca doğrulama için)
ios/AstroHikaye/  SwiftUI uygulaması
docs/             kararlar, lisans notu, örnek çıktı
```

## Hesaplama doğruluğu

Faz 1'in hatalı olması sonraki her şeyi bozar, bu yüzden doğrulama üç
bağımsız çıpaya dayanıyor:

1. **Ekinoks ve gündönümü anları.** Güneş'in boylamının tanım gereği tam
   0°/90° olduğu on ayrı an (Espenak/NASA yayını). Sapma < 0,002°.
2. **Referans harita.** Einstein (Rodden AA, doğum belgesi). Dokuz gezegen
   astro.com'un yayınladığı değerlerle eşleşiyor.
3. **Bağımsız yığın çapraz kontrolü.** Skyfield + JPL DE440s — tamamen ayrı
   bir kod tabanı. Dört farklı çağda en büyük sapma **0,15 açı saniyesi**
   (astrolojik yorumun ihtiyacı ~60 açı saniyesi).

```bash
.venv/bin/python backend/tools/crosscheck_skyfield.py
```

## Kayda değer iki ayrıntı

**Doğum saati bilinmiyorsa ev sistemi üretilmez.** Yükselen dört dakikada bir
derece ilerler; "öğlen 12:00 varsayalım" demek Yükselen'i rastgele bir burca
atamaktır. Uydurma bir Yükselen'i hikâyede gerçekmiş gibi kullanmak ürünün
tek iddiasını çürütür. Bunun yerine veri yokluğu hem API'de hem arayüzde
adıyla raporlanır, ve prompt modele Yükselen'den söz etmemesini söyler.

**Standart saat öncesi doğumlarda gerçek yerel ortalama saat kullanılır.**
IANA tz veritabanı 1893 öncesi Almanya için Berlin'in LMT'sini (+0:53:28)
verir; Ulm'de doğan biri için bu 13,5 dakika yanlıştır ve Yükselen'i 3,4
derece kaydırır. Bu dönemde ofset doğum boylamından hesaplanır.

## Açık kararlar

[docs/kararlar.md](docs/kararlar.md) — özellikle Swiss Ephemeris lisansı
(ticari kullanımda CHF 750) ve seslendirmenin MVP'de yer alıp almayacağı.
