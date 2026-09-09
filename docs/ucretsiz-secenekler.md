# Para harcamadan hikâye üretmek

Projenin doğrulanmamış tek varsayımı hikâye kalitesi. O varsayımı sınamak
için API'ye abone olmak gerekmiyor. Üç yol var, ucuzdan pahalıya değil,
**doğrulama için işe yararlıktan** sıraya dizili.

---

## 1. Kopyala-yapıştır (0 TL, kurulum yok) — önerilen

Boru hattı promptu üretir, sen herhangi bir ücretsiz sohbet arayüzüne
yapıştırırsın, çıkan metni geri okutursun. Uygulamanın geri kalanı metnin
nereden geldiğini bilmiyor, dolayısıyla akış bozulmuyor.

```bash
# 1) Promptu üret — panoya da kopyalanır
.venv/bin/python backend/tools/cli.py \
    --tarih 2003-07-03 --saat 09:00 --yer Denizli --ad Gülheda --prompt-yaz

# 2) claude.ai, gemini.google.com veya chatgpt.com'a yapıştır.
#    Çıkan metni bir dosyaya kaydet, örn. hikaye.txt

# 3) Geri oku — tam çıktı + iOS uygulamasının örnek verisi güncellenir
.venv/bin/python backend/tools/cli.py \
    --tarih 2003-07-03 --saat 09:00 --yer Denizli --ad Gülheda \
    --hikaye-oku hikaye.txt --ios-ornek
```

`--ios-ornek` verirsen hikâye uygulamanın içine gömülür ve simülatörde
gerçek ekranında görürsün.

**Neden bu yol en iyisi:** Sınamak istediğin şey promptun kalitesi. Aynı
prompt, aynı model, aynı çıktı — tek fark, çağrının senin elinle yapılması.
Beş harita için beş kopyala-yapıştır, yaklaşık 20 dakika.

**Sınırı:** Otomatik değil. Uygulama kendi başına hikâye üretemez, yani
gerçek kullanıcıya açılamaz. Doğrulama için yeter, ürün için yetmez.

---

## 2. Gemini ücretsiz katmanı (0 TL, otomatik)

Google AI Studio'dan ücretsiz anahtar alınır; kredi kartı istemez.

```bash
# .env dosyasına
LLM_SAGLAYICI=gemini
GEMINI_API_KEY=...
STORY_MODEL=gemini-3-flash
```

Model adlarını görmek için:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=ANAHTAR"
```

**Dikkat edilecek iki şey:**

- **Faturalandırmayı açma.** Bir Google Cloud projesinde faturalandırma
  açılırsa ücretsiz katman o proje için tamamen kalkar ve ilk tokendan
  itibaren ücretlendirilir. Deneme için ayrı bir proje kullan.
- Günlük istek sınırı var ve Pasifik saatiyle gece yarısı sıfırlanır.
  Kota dolduğunda sağlayıcı bunu açık bir mesajla bildirir.

**Sınırı:** Prompt yedi mutlak kural içeriyor ve bunlara uyum modelden
modele değişir. Çıktı Claude ile aynı olmayabilir; karşılaştırma ölçütü
[ornek-hikaye.md](ornek-hikaye.md).

---

## 3. Yerel model (0 TL, internet bile gerekmez)

Ollama gibi bir araçla model kendi bilgisayarında çalışır.

```bash
# ollama.com'dan indirip kurduktan sonra
ollama pull llama3.1:8b

# .env dosyasına
LLM_SAGLAYICI=openai_uyumlu
LLM_TEMEL_ADRES=http://localhost:11434/v1
LLM_API_KEY=ollama
STORY_MODEL=llama3.1:8b
```

Aynı ayarlarla OpenRouter'ın ücretsiz modelleri, Groq veya LM Studio da
kullanılabilir; hepsi `/chat/completions` konuşuyor.

**Sınırı — ve bu ciddi:** 8 milyar parametreli bir yerel modelin Türkçe
edebî metin üretme ve yedi kurala aynı anda uyma becerisi düşüktür. Büyük
ihtimalle burç yorumuna kayar, yani tam olarak kaçınmaya çalıştığımız
çıktıyı verir. **Boru hattını sınamak için uygundur, hikâye kalitesini
yargılamak için değildir.** Bu yolla aldığın kötü bir çıktıya bakıp "fikir
tutmuyor" sonucuna varma.

---

## Karşılaştırma

| | Ücret | Otomatik | Kalite yargısı için güvenilir |
|---|---|---|---|
| Kopyala-yapıştır | 0 | Hayır | **Evet** |
| Gemini ücretsiz | 0 | Evet | Kısmen |
| Yerel model | 0 | Evet | Hayır |
| Anthropic API | ~0,07 USD/hikâye | Evet | Evet |

## Ne zaman ücretli API gerekir

Yalnızca uygulama gerçek kullanıcılara açıldığında. O noktada zaten para
kazanıyor ya da kazanmaya çalışıyor olacaksın; hikâye başına 0,07 dolar
o aşamada anlamlı bir maliyet değil. Doğrulama aşamasında ise gereksiz.
