"""Komut satırından harita ve hikâye üretir.

    .venv/bin/python backend/tools/cli.py --tarih 2003-07-03 --saat 09:00 \
        --yer Denizli --ad Gülheda

`--sadece-harita` LLM çağrısı yapmaz; API anahtarı gerektirmez.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, time
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.astro.chart import BirthInput, calculate_chart
from app.astro.timeutil import TimeResolutionError
from app.geo.geocode import GeocodingError, geocode
from app.story.brief import olgusal_panel
from app.story.generator import (
    StoryGenerationError,
    generate_story,
    prompt_ciftini_uret,
    story_from_text,
)


def _saat_ayristir(deger: Optional[str]) -> Optional[time]:
    if not deger or deger.lower() in ("bilinmiyor", "yok", "-"):
        return None
    return datetime.strptime(deger, "%H:%M").time()


def _panoya_kopyala(metin: str) -> bool:
    """macOS panosuna kopyalar. Başarısız olursa sessizce vazgeçer."""
    import subprocess

    try:
        subprocess.run(["pbcopy"], input=metin.encode("utf-8"), check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _hikaye_bolumu(story) -> list:
    maliyet = (f"{story.cost_usd:.4f} USD" if story.cost_usd is not None
               else "bilinmiyor")
    return [
        "",
        "=" * 72,
        "",
        story.title.upper(),
        "",
        story.body,
        "",
        "=" * 72,
        f"kaynak: {story.provider} | model: {story.model} | "
        f"prompt: v{story.prompt_version} | ton: {story.tone_key}",
        f"{story.word_count} kelime, {story.character_count} karakter",
        f"token: {story.input_tokens} girdi + {story.output_tokens} çıktı "
        f"| maliyet: {maliyet}",
    ]


def _ios_ornegi_yaz(chart, story, yer) -> str:
    """iOS uygulamasının paketlediği örnek yanıtı günceller.

    Böylece elle üretilmiş bir hikâye, uygulamada API çağrısı olmadan
    gerçek ekranında görülebiliyor.
    """
    import json

    kok = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    yol = os.path.join(kok, "ios", "AstroHikaye", "Resources", "ornek-yanit.json")
    govde = {
        "yer": {
            "sorgu": yer.query, "cozumlenen_ad": yer.display_name,
            "enlem": yer.latitude, "boylam": yer.longitude, "kaynak": yer.source,
        },
        "harita": chart.to_dict(),
        "baslik": story.title,
        "metin": story.body,
        "olgusal_panel": story.factual_panel,
        "ton": story.tone_key,
        "yas": story.age,
        "model": story.model,
        "prompt_surumu": story.prompt_version,
        "kelime_sayisi": story.word_count,
        "karakter_sayisi": story.character_count,
        "girdi_token": story.input_tokens,
        "cikti_token": story.output_tokens,
        "maliyet_usd": story.cost_usd,
    }
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(govde, f, ensure_ascii=False, indent=1)
    return yol


def main() -> int:
    p = argparse.ArgumentParser(description="Doğum haritası ve hikâye üretici")
    p.add_argument("--tarih", required=True, help="YYYY-AA-GG")
    p.add_argument("--saat", help="SS:DD (bilinmiyorsa boş bırakın)")
    p.add_argument("--yer", required=True, help="Doğum yeri, örn. Denizli")
    p.add_argument("--ad", help="Hikâyede geçecek ad")
    p.add_argument("--ev-sistemi", default="placidus")
    p.add_argument("--model", help="Kullanılacak model (varsayılan: claude-opus-5)")
    p.add_argument("--sadece-harita", action="store_true",
                   help="Hikâye üretme, yalnızca hesaplamayı göster")
    p.add_argument("--prompt-yaz", action="store_true",
                   help="Model çağırmadan promptu yazdır ve panoya kopyala. "
                        "Herhangi bir ücretsiz sohbete yapıştırmak için.")
    p.add_argument("--hikaye-oku", metavar="DOSYA",
                   help="Elle üretilmiş hikâye metnini bu dosyadan oku "
                        "(model çağrısı yapılmaz)")
    p.add_argument("--sablon", action="store_true",
                   help="Hikâyeyi şablon motoruyla üret: dil modeli çağrılmaz, "
                        "ağ gerekmez, maliyet sıfır")
    p.add_argument("--ios-ornek", action="store_true",
                   help="Sonucu iOS uygulamasının örnek yanıt dosyasına yaz")
    p.add_argument("--kaydet", help="Çıktıyı bu dosyaya yaz")
    args = p.parse_args()

    try:
        yer = geocode(args.yer)
    except GeocodingError as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        return 1

    birth = BirthInput(
        birth_date=date.fromisoformat(args.tarih),
        birth_time=_saat_ayristir(args.saat),
        latitude=yer.latitude,
        longitude=yer.longitude,
        place_name=yer.display_name,
        name=args.ad,
        house_system=args.ev_sistemi,
    )

    try:
        chart = calculate_chart(birth)
    except TimeResolutionError as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        return 1

    # Prompt yazdırma: model çağrısı yok, anahtar gerekmez.
    if args.prompt_yaz:
        sistem, kullanici = prompt_ciftini_uret(chart, name=args.ad)
        tam = f"{sistem}\n\n{'=' * 70}\n\n{kullanici}"
        print(tam)
        if _panoya_kopyala(tam):
            print("\n[Prompt panoya kopyalandı. Herhangi bir sohbet arayüzüne "
                  "yapıştırıp çıkan metni bir dosyaya kaydedin, sonra "
                  "--hikaye-oku ile geri okuyun.]", file=sys.stderr)
        return 0

    parcalar = [olgusal_panel(chart)]

    if args.sablon:
        from app.story.sablon.motor import SABLON_SURUMU, uret as sablon_uret
        from app.story.generator import story_from_text

        baslik, govde = sablon_uret(chart, ad=args.ad)
        story = story_from_text(chart, "BAŞLIK: " + baslik + "\n\n" + govde,
                                model="sablon-v" + SABLON_SURUMU)
        parcalar.extend(_hikaye_bolumu(story))
        if args.ios_ornek:
            yol = _ios_ornegi_yaz(chart, story, yer)
            print("\n[iOS örneği güncellendi: " + yol + "]", file=sys.stderr)

    elif args.hikaye_oku:
        try:
            with open(args.hikaye_oku, encoding="utf-8") as f:
                ham = f.read()
        except OSError as exc:
            print(f"Dosya okunamadı: {exc}", file=sys.stderr)
            return 1
        try:
            story = story_from_text(chart, ham)
        except StoryGenerationError as exc:
            print(f"Hata: {exc}", file=sys.stderr)
            return 1
        parcalar.extend(_hikaye_bolumu(story))
        if args.ios_ornek:
            yol = _ios_ornegi_yaz(chart, story, yer)
            print(f"\n[iOS örneği güncellendi: {yol}]", file=sys.stderr)

    elif not args.sadece_harita:
        try:
            story = generate_story(chart, name=args.ad, model=args.model)
        except StoryGenerationError as exc:
            print(f"\nHikâye üretilemedi: {exc}", file=sys.stderr)
            print("(Harita hesaplandı; yalnızca hikâye adımı başarısız.)",
                  file=sys.stderr)
            print(parcalar[0])
            return 2

        parcalar.extend(_hikaye_bolumu(story))
        if args.ios_ornek:
            yol = _ios_ornegi_yaz(chart, story, yer)
            print(f"\n[iOS örneği güncellendi: {yol}]", file=sys.stderr)

    cikti = "\n".join(parcalar)
    print(cikti)
    if args.kaydet:
        with open(args.kaydet, "w", encoding="utf-8") as f:
            f.write(cikti + "\n")
        print(f"\n[{args.kaydet} dosyasına yazıldı]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
