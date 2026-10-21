# Canlıya alma

Backend'i tek bir `Dockerfile` ile paketler; Railway, Render veya Fly'ın
herhangi birinde aynı şekilde çalışır. Kod tarafı hazır — geri kalanı
birkaç tıklamalık hesap/konfigürasyon işi, aşağıda adım adım.

## Railway ile (önerilen, en basit)

1. railway.app adresine git, GitHub hesabınla giriş yap.
2. "New Project" → "Deploy from GitHub repo" → `gulheda/gok-hikayesi` seç.
   Railway kökteki `Dockerfile`'ı otomatik bulur, başka ayar istemez.
3. Deploy bitince "Settings → Networking → Generate Domain" ile sana
   `https://....up.railway.app` gibi bir adres verir.
4. "Variables" sekmesinden şu ortam değişkenlerini ekle (hepsi opsiyonel,
   eklemezsen uygulama şablon motoruyla ücretsiz çalışmaya devam eder):

   | Değişken | Değer | Not |
   |---|---|---|
   | `LLM_SAGLAYICI` | `sablon` veya `gemini` | `gemini` seçersen `GEMINI_API_KEY` de gerekir |
   | `GEMINI_API_KEY` | aistudio.google.com'dan alınan anahtar | yalnızca `gemini` seçtiysen |
   | `STORY_MODEL` | `gemini-3.5-flash` | yalnızca `gemini` seçtiysen |

5. `curl https://<senin-adresin>/saglik` ile doğrula — `"durum":"calisiyor"`
   dönmeli.

## Sonra yapılacaklar (deploy'dan SONRA)

- **iOS tarafı:** `Info.plist`'teki yerel-ağ (ATS) istisnasını kaldır,
  backend adresini gerçek HTTPS adresinle değiştir (bkz. docs/durum.md).
- **CORS:** `backend/app/api/main.py`'deki `allow_origins=["*"]` satırı
  MVP notuyla işaretli; native iOS istemcisi tarayıcı olmadığı için pratikte
  risk düşük, ama ileride bir web istemcisi eklenirse daraltılmalı.

## Neden Docker (buildpack değil)

`pyswisseph` gibi C uzantılı bir paket var; Docker, Python sürümünü
(3.11) ve derleme ortamını sabitleyerek platformlar arası sürpriz
çıkmasını engeller. Efemeris veri dosyaları (`backend/data/ephe/*.se1`)
zaten repoya gömülü, ayrıca indirme adımı gerekmez.
