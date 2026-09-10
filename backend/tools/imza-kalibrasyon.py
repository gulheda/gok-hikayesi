"""İmza yapılarının gerçek seyrekliğini ölçer.

ÖNEMLİ: Ölçüm KATEGORİ değil ÖRNEK düzeyinde yapılır. "Bir gök cismi
açısal noktaya 8 derece yakın" haritaların %87'sinde görülür - yani
yaygındır. Ama "Jüpiter Yükselen'e 1,1 derece yakın" seyrektir. Kategori
ölçmek, hikâyeyi yaygın bir şeyin üzerine kurmaya yol açar; bu yüzden
her yapı orb/sayı kademelerine bölünerek sayılıyor.

`signature.py` yapıları "çok belirgin / belirgin / yaygın" diye
etiketliyor ama bu etiketler ELLE yazıldı - yani tahmin. Tahmin yanlışsa
hikâye yanlış şeyin üzerine kurulur: yaygın bir özelliği ender sanmak,
metni milyonlarca kişiye uyan bir şeye çevirir.

Bu araç rastgele doğum anları üretip her yapının kaç haritada göründüğünü
sayar. Çıkan oranlar `data/nadirlik.json` dosyasına yazılır ve motor
etiket yerine ÖLÇÜLMÜŞ oranı kullanır.

Kullanım:
    .venv/bin/python backend/tools/imza-kalibrasyon.py --ornek 3000
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from datetime import date, time, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.astro.chart import BirthInput, calculate_chart
from app.astro.timeutil import TimeResolutionError
from app.geo.places import TURKIYE_IL_MERKEZLERI
from app.story.desenler import hepsi as desenleri_bul

CIKTI = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "nadirlik.json",
)


def rastgele_dogum(uretec: random.Random) -> BirthInput:
    """Türkiye'de rastgele bir doğum anı.

    Örneklem gerçek kullanıcı dağılımına benzesin diye yer Türkiye
    illeriyle, tarih de yaşayan nüfusun doğum aralığıyla sınırlı.
    """
    baslangic = date(1950, 1, 1)
    gun = uretec.randrange((date(2012, 12, 31) - baslangic).days)
    d = baslangic + timedelta(days=gun)
    t = time(uretec.randrange(24), uretec.randrange(60))
    lat, lon = uretec.choice(list(TURKIYE_IL_MERKEZLERI.values()))
    return BirthInput(birth_date=d, birth_time=t, latitude=lat,
                      longitude=lon, place_name="örneklem")


# Kademeler: her yapı, ne kadar uç olduğuna göre ayrı ayrı sayılır.
ACISAL_KADEMELER = (1.0, 2.0, 4.0, 8.0)
ACI_KADEMELERI = (0.2, 0.5, 1.0, 2.0)
YIGIN_KADEMELERI = (3, 4, 5)


def olcum_anahtarlari(chart) -> set:
    """Bir haritada bulunan tüm kademeli yapı anahtarları."""
    from app.astro.aspects import angular_separation

    bulunan = set()

    # Açısal noktalara yakınlık, derece kademesine göre
    if chart.houses.available and chart.houses.ascendant is not None:
        noktalar = {
            "asc": chart.houses.ascendant,
            "mc": chart.houses.midheaven,
            "dsc": (chart.houses.ascendant + 180) % 360,
            "ic": (chart.houses.midheaven + 180) % 360,
        }
        for body in chart.bodies:
            if body.key not in CEKIRDEK:
                continue
            for nokta_adi, nokta in noktalar.items():
                if nokta is None:
                    continue
                fark = abs((body.longitude - nokta + 180) % 360 - 180)
                for kademe in ACISAL_KADEMELER:
                    if fark <= kademe:
                        bulunan.add(f"acisal_{kademe:g}")
                        if nokta_adi == "asc" and body.key == "Sun":
                            bulunan.add(f"gun_dogumu_{kademe:g}")
                        break

    # Açı darlığı
    for aci in chart.aspects:
        for kademe in ACI_KADEMELERI:
            if aci.orb <= kademe:
                bulunan.add(f"dar_aci_{kademe:g}")
                break

    # Yığılma büyüklüğü
    from collections import Counter as _C
    ev_sayimi = _C(b.house for b in chart.bodies
                   if b.key in CEKIRDEK and b.house)
    burc_sayimi = _C(b.sign_index for b in chart.bodies if b.key in CEKIRDEK)
    for sayim, etiket in ((ev_sayimi, "ev"), (burc_sayimi, "burc")):
        en_cok = max(sayim.values()) if sayim else 0
        for kademe in reversed(YIGIN_KADEMELERI):
            if en_cok >= kademe:
                bulunan.add(f"yigin_{etiket}_{kademe}")
                break

    # Harita yöneticisi her haritada vardır; ölçüme dahil edilmesinin
    # sebebi %100 olduğunun kayda geçmesi - sıralamada en sona düşsün.
    if chart.houses.available:
        bulunan.add("chart_ruler")

    # Baskın element (tek elementte 5+ yerleşim)
    sayilar = chart.balance.elements
    if sayilar and max(sayilar.values()) >= 5:
        bulunan.add("dominant_element")

    # Element dengesi
    if chart.balance.missing_elements:
        bulunan.add("eksik_element")
        if len(chart.balance.missing_elements) > 1:
            bulunan.add("iki_eksik_element")
    else:
        bulunan.add("dengeli_element")

    # Açısız gök cismi
    bagli = {a.body_a for a in chart.aspects} | {a.body_b for a in chart.aspects}
    yalniz = [b for b in chart.bodies if b.key in CEKIRDEK and b.key not in bagli]
    if yalniz:
        bulunan.add("acisiz_cisim")

    # İç gezegen gerilemesi
    if any(b.is_retrograde for b in chart.bodies
           if b.key in ("Mercury", "Venus", "Mars")):
        bulunan.add("ic_gezegen_gerileme")

    # Geometrik ve klasik desenler (tutulma, T-kare, büyük üçgen,
    # kâse şekli, kendi burcunda gezegen, Güneş'e gömülülük, ay evresi)
    for desen in desenleri_bul(chart):
        bulunan.add(desen.anahtar)

    return bulunan


CEKIRDEK = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter",
            "Saturn", "Uranus", "Neptune", "Pluto")


def olc(ornek_sayisi: int, tohum: int = 20030703) -> dict:
    uretec = random.Random(tohum)
    sayac: Counter = Counter()
    ek_sayac: Counter = Counter()
    gecerli = 0
    atlanan = 0

    while gecerli < ornek_sayisi:
        try:
            chart = calculate_chart(rastgele_dogum(uretec))
        except TimeResolutionError:
            # Yaz saati geçişindeki belirsiz/olmayan saatler; örneklemden düşer.
            atlanan += 1
            continue

        gecerli += 1
        for anahtar in olcum_anahtarlari(chart):
            sayac[anahtar] += 1

    return {
        "ornek_sayisi": gecerli,
        "atlanan": atlanan,
        "oranlar": {k: round(v / gecerli, 5) for k, v in sorted(sayac.items())},
    }


def main() -> int:
    p = argparse.ArgumentParser(description="İmza seyrekliğini ölçer")
    p.add_argument("--ornek", type=int, default=2000)
    p.add_argument("--yaz", action="store_true", help="Sonucu data/nadirlik.json'a yaz")
    args = p.parse_args()

    print(f"{args.ornek} rastgele harita üretiliyor…", file=sys.stderr)
    sonuc = olc(args.ornek)

    print(f"\nÖrneklem: {sonuc['ornek_sayisi']} harita "
          f"({sonuc['atlanan']} atlandı)\n")
    print(f"{'yapı':24s} {'oran':>8s}  yorum")
    print("-" * 58)
    hepsi = sonuc["oranlar"]
    for anahtar, oran in sorted(hepsi.items(), key=lambda x: x[1]):
        if oran < 0.05:
            yorum = "çok ender"
        elif oran < 0.20:
            yorum = "ender"
        elif oran < 0.50:
            yorum = "seyrek değil"
        else:
            yorum = "YAYGIN"
        print(f"{anahtar:24s} {oran*100:7.2f}%  {yorum}")

    if args.yaz:
        os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
        with open(CIKTI, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2)
        print(f"\n{CIKTI} yazıldı", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
