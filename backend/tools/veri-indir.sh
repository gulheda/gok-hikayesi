#!/usr/bin/env bash
# Efemeris veri dosyalarını indirir.
#
# .se1 dosyaları çalışma zamanında gereklidir (Swiss Ephemeris tam doğruluk;
# yoksa kütüphane yerleşik Moshier modeline düşer). de440s.bsp yalnızca
# bağımsız çapraz doğrulama içindir ve 32 MB olduğu için depoda tutulmaz.
set -euo pipefail

KOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Swiss Ephemeris veri dosyaları…"
mkdir -p "$KOK/data/ephe"
for f in sepl_18.se1 semo_18.se1 seas_18.se1; do
    if [ -f "$KOK/data/ephe/$f" ]; then
        echo "  $f zaten var"
    else
        curl -sS -L -f -o "$KOK/data/ephe/$f" \
            "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/$f"
        echo "  $f indirildi"
    fi
done

echo "JPL DE440s (32 MB, yalnızca doğrulama için)…"
mkdir -p "$KOK/data/jpl"
if [ -f "$KOK/data/jpl/de440s.bsp" ]; then
    echo "  de440s.bsp zaten var"
else
    curl -# -L -f -o "$KOK/data/jpl/de440s.bsp" \
        "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp"
    echo "  de440s.bsp indirildi"
fi

echo "Tamam."
