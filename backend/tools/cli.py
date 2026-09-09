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
from app.story.generator import StoryGenerationError, generate_story


def _saat_ayristir(deger: Optional[str]) -> Optional[time]:
    if not deger or deger.lower() in ("bilinmiyor", "yok", "-"):
        return None
    return datetime.strptime(deger, "%H:%M").time()


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

    parcalar = [olgusal_panel(chart)]

    if not args.sadece_harita:
        try:
            story = generate_story(chart, name=args.ad, model=args.model)
        except StoryGenerationError as exc:
            print(f"\nHikâye üretilemedi: {exc}", file=sys.stderr)
            print("(Harita hesaplandı; yalnızca hikâye adımı başarısız.)",
                  file=sys.stderr)
            print(parcalar[0])
            return 2

        maliyet = (f"{story.cost_usd:.4f} USD" if story.cost_usd is not None
                   else "bilinmiyor")
        parcalar.extend([
            "",
            "=" * 72,
            "",
            story.title.upper(),
            "",
            story.body,
            "",
            "=" * 72,
            f"model: {story.model} | prompt: v{story.prompt_version} | "
            f"ton: {story.tone_key} | yaş: {story.age}",
            f"{story.word_count} kelime, {story.character_count} karakter",
            f"token: {story.input_tokens} girdi + {story.output_tokens} çıktı "
            f"| maliyet: {maliyet}",
        ])

    cikti = "\n".join(parcalar)
    print(cikti)
    if args.kaydet:
        with open(args.kaydet, "w", encoding="utf-8") as f:
            f.write(cikti + "\n")
        print(f"\n[{args.kaydet} dosyasına yazıldı]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
