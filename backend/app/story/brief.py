"""Haritayı iki ayrı katmana böler: olgusal özet ve LLM'e verilecek brifing.

Ürünün merkezî iddiası "gezegen konumları gerçek astronomik hesaplamadan
gelir, anlam yüklemesi kurgudur" olduğuna göre bu ayrım yapısal olmalı,
sadece ekranın altına iliştirilen bir uyarı olmamalı. Bu yüzden:

- `olgusal_panel()` doğrudan hesaplamadan, kod tarafından üretilir.
  Kullanıcıya gösterilen sayıların hiçbiri modelden gelmez, dolayısıyla
  uydurulamaz.
- `llm_brifingi()` yalnızca modelin kurgulaştıracağı veriyi taşır ve
  bilinmeyen alanları açıkça bilinmiyor olarak işaretler; böylece model
  olmayan bir Yükselen hakkında yazmaya çekilmez.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from ..astro.chart import NatalChart
from .omurga import kur as omurga_kur
from .signature import collect as collect_signatures, common_traits

# Hikâyeye girecek açı sayısı. Tümü verilirse model önemsiz açılara da
# eşit ağırlık verip anlatıyı dağıtıyor; en güçlü birkaçı odak sağlıyor.
MAX_ASPECTS_IN_BRIEF = 8


def yas_hesapla(birth_date: date, bugun: Optional[date] = None) -> int:
    bugun = bugun or date.today()
    yas = bugun.year - birth_date.year
    if (bugun.month, bugun.day) < (birth_date.month, birth_date.day):
        yas -= 1
    return max(yas, 0)


def olgusal_panel(chart: NatalChart) -> str:
    """Kullanıcıya gösterilen "gerçekte ne hesaplandı" paneli.

    Tamamen deterministiktir; aynı girdi her zaman aynı metni verir.
    """
    b = chart.birth
    i = chart.instant
    satirlar: List[str] = []

    satirlar.append("HESAPLANAN VERİ (astronomik)")
    satirlar.append("")
    satirlar.append(f"Tarih ve yer : {b.birth_date.strftime('%d.%m.%Y')}, {b.place_name}")
    if b.time_known:
        satirlar.append(
            f"Yerel saat   : {b.birth_time.strftime('%H:%M')} "
            f"(UTC{i.utc_offset_hours:+g}{', yaz saati' if i.is_dst else ''})"
        )
    else:
        satirlar.append("Yerel saat   : bilinmiyor")
    satirlar.append(f"Evrensel saat: {i.utc.strftime('%d.%m.%Y %H:%M')} UTC")
    satirlar.append(f"Julian Day   : {i.julian_day_ut:.5f}")
    satirlar.append(f"Efemeris     : Swiss Ephemeris ({chart.ephemeris_mode})")
    satirlar.append("")

    satirlar.append("Gök cismi konumları (geosentrik ekliptik boylam):")
    for body in chart.bodies:
        ev = f"  {body.house:>2}. ev" if body.house else ""
        satirlar.append(
            f"  {body.name_tr:<18} {body.display_position:<16} "
            f"{body.longitude:7.3f}°{ev}"
        )
    satirlar.append("")

    if chart.houses.available:
        satirlar.append(f"Ev sistemi   : {chart.houses.system_name}")
        satirlar.append(
            f"Yükselen     : {chart.houses.ascendant_sign_tr} "
            f"{chart.houses.ascendant % 30:.2f}°"
        )
        satirlar.append(
            f"Tepe (MC)    : {chart.houses.midheaven_sign_tr} "
            f"{chart.houses.midheaven % 30:.2f}°"
        )
    else:
        satirlar.append("Ev sistemi   : hesaplanmadı")
        satirlar.append(f"Sebep        : {chart.houses.unavailable_reason}")
    satirlar.append("")

    if chart.aspects:
        satirlar.append("Açılar (tam açıdan sapma = orb):")
        for a in chart.aspects[:MAX_ASPECTS_IN_BRIEF]:
            satirlar.append(
                f"  {a.name_a_tr} – {a.name_b_tr}: {a.type_name_tr} "
                f"({a.exact_angle:.0f}°, orb {a.orb:.2f}°)"
            )
        satirlar.append("")

    e = chart.balance.elements
    m = chart.balance.modalities
    satirlar.append(
        "Element dengesi: " + ", ".join(f"{k} {v}" for k, v in e.items())
    )
    satirlar.append(
        "Nitelik dengesi: " + ", ".join(f"{k} {v}" for k, v in m.items())
    )

    if chart.warnings:
        satirlar.append("")
        satirlar.append("Notlar:")
        for w in chart.warnings:
            satirlar.append(f"  • {w}")
    if chart.instant.note:
        satirlar.append(f"  • {chart.instant.note}")

    return "\n".join(satirlar)


def llm_brifingi(chart: NatalChart) -> str:
    """Modele verilecek yapılandırılmış veri özeti.

    Bilinmeyen alanlar açıkça işaretlenir; modelin elinde olmayan veriyi
    uydurmasının önündeki en etkili engel, o verinin yokluğunu görmesidir.
    """
    b = chart.birth
    satirlar: List[str] = []

    satirlar.append(f"Doğum tarihi: {b.birth_date.strftime('%d %B %Y')}")
    satirlar.append(f"Doğum yeri: {b.place_name}")
    if b.time_known:
        satirlar.append(f"Doğum saati: {b.birth_time.strftime('%H:%M')} (yerel)")
    else:
        satirlar.append(
            "Doğum saati: BİLİNMİYOR. Bu yüzden Yükselen burç ve ev "
            "yerleşimleri HESAPLANMADI. Hikâyede Yükselen'den, evlerden "
            "veya 'doğduğun anda ufukta yükselen' türü ifadelerden hiç "
            "söz etme; elinde olmayan veriyi ima etme."
        )
    satirlar.append("")

    satirlar.append("GÖK CİSİMLERİ:")
    for body in chart.bodies:
        parcalar = [f"- {body.name_tr}: {body.sign_name_tr} burcu {body.degree_in_sign:.1f}°"]
        parcalar.append(f"({body.element_tr} elementi, {body.modality_tr} nitelik)")
        if body.house and body.house_theme_tr:
            parcalar.append(f", {body.house}. ev — {body.house_theme_tr}")
        if body.is_retrograde:
            parcalar.append(", GERİLEME hareketinde")
        satirlar.append(" ".join(parcalar))
    satirlar.append("")

    if chart.houses.available:
        satirlar.append(
            f"YÜKSELEN: {chart.houses.ascendant_sign_tr} "
            f"({chart.houses.ascendant % 30:.1f}°)"
        )
        satirlar.append(
            f"TEPE NOKTASI (MC): {chart.houses.midheaven_sign_tr} "
            f"({chart.houses.midheaven % 30:.1f}°)"
        )
        satirlar.append("")

    if chart.aspects:
        satirlar.append("AÇILAR (en güçlüden zayıfa, ilk sıradakiler baskın):")
        for a in chart.aspects[:MAX_ASPECTS_IN_BRIEF]:
            satirlar.append(
                f"- {a.name_a_tr} ile {a.name_b_tr} arasında {a.type_name_tr} "
                f"({a.nature} nitelikte, güç {a.strength:.2f})"
            )
        satirlar.append("")

    e = chart.balance.elements
    satirlar.append(
        "ELEMENT DAĞILIMI: " + ", ".join(f"{k}: {v}" for k, v in e.items())
    )
    if chart.balance.dominant_element:
        satirlar.append(f"Baskın element: {chart.balance.dominant_element}")
    if chart.balance.missing_elements:
        satirlar.append(
            "Hiç yerleşim almayan element(ler): "
            + ", ".join(chart.balance.missing_elements)
        )
    satirlar.append("")

    # Ayırt edici yapılar. Hikâyenin kişiye ait hissettirmesi buradan gelir:
    # model yaygın olana değil, ender olana tutunmalı.
    imzalar = collect_signatures(chart)

    # Anlatı omurgası: yapıları sıralamak yetmiyor, hangilerinin BİRLİKTE
    # bir sahne kurduğunu da söylemek gerekiyor. Sıralı bir liste hikâye
    # değildir; olgular birbirine değdiğinde hikâye olur.
    if imzalar:
        from ..astro.constants import BODY_BY_KEY

        omurga = omurga_kur(chart, imzalar=imzalar)
        omurga_satirlari = omurga.brifing_satirlari(
            {k: v.name_tr for k, v in BODY_BY_KEY.items()}
        )
        if omurga_satirlari:
            satirlar.extend(omurga_satirlari)
            satirlar.append("")

    if imzalar:
        from .nadirlik import ornek_sayisi

        satirlar.append(
            "BU HARİTAYA ÖZGÜ YAPILAR — seyreklik sırasına göre. Oranlar "
            f"{ornek_sayisi()} rastgele harita üzerinden ÖLÇÜLDÜ, tahmin "
            "edilmedi. Omurgada geçmeyen yapıları arka planda kullanabilirsin "
            "ama durak yapma."
        )
        for imza in imzalar:
            oran = (f"%{imza.oran * 100:.1f} — {imza.insan_ifadesi}"
                    if imza.oran is not None else "ölçülmedi")
            satirlar.append(f"- [{imza.rarity} | {oran}] {imza.label}")
            if imza.note:
                satirlar.append(f"  ({imza.note})")
        satirlar.append("")

    yaygin = common_traits(chart)
    if yaygin:
        satirlar.append(
            "ÜZERİNE HİKÂYE KURULMAMASI GEREKENLER — bunlar milyonlarca "
            "insanla paylaşılıyor, dolayısıyla kişiye ait hissettirmez:"
        )
        for t in yaygin:
            satirlar.append(f"- {t}")

    return "\n".join(satirlar)
