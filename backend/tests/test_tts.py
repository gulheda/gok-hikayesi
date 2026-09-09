"""Seslendirme katmanı testleri (ağa çıkmaz - sahte sağlayıcı kullanır)."""
from __future__ import annotations

import pytest

from app.tts.base import TTSError, synthesize_long_text
from app.tts.chunking import chunk_text, split_sentences
from app.tts.pricing import compare_all, estimate


class SahteSaglayici:
    name = "sahte"
    max_chars_per_request = 100

    def __init__(self):
        self.cagrilar = []

    def synthesize_chunk(self, text: str) -> bytes:
        self.cagrilar.append(text)
        return text.encode("utf-8")


def test_kisa_metin_tek_parca_kalir():
    assert chunk_text("Tek cümle.", 100) == ["Tek cümle."]


def test_bos_metin_bos_liste_dondurur():
    assert chunk_text("   ") == []


def test_parcalar_sinirin_altinda_kalir():
    metin = " ".join(f"Bu {i} numaralı cümledir." for i in range(200))
    for parca in chunk_text(metin, 300):
        assert len(parca) <= 300


def test_bolme_cumle_ortasinda_yapilmaz():
    metin = " ".join(f"Cümle numarası {i}." for i in range(80))
    for parca in chunk_text(metin, 200):
        assert parca.rstrip().endswith(".")


def test_paragraflar_mumkun_oldugunca_birlestirilir():
    metin = "Birinci paragraf.\n\nİkinci paragraf.\n\nÜçüncü paragraf."
    assert len(chunk_text(metin, 500)) == 1


def test_cumle_ayirici_kisaltmalarda_bolmez():
    # Ardından büyük harf gelmediği için "vb." bölme noktası olmamalı.
    assert len(split_sentences("Kitap, defter vb. şeyler vardı.")) == 1


def test_tek_cumle_siniri_asarsa_sert_bolunur():
    uzun = "a" * 500
    parcalar = chunk_text(uzun, 100)
    assert len(parcalar) == 5
    assert all(len(p) <= 100 for p in parcalar)
    assert "".join(parcalar) == uzun


def test_uzun_metin_parcalanip_birlestirilir():
    saglayici = SahteSaglayici()
    metin = " ".join(f"Cümle {i}." for i in range(60))
    sonuc = synthesize_long_text(saglayici, metin, voice="test")
    assert sonuc.chunk_count == len(saglayici.cagrilar) > 1
    assert sonuc.characters == len(metin)
    assert sonuc.warnings, "çok parçalı seslendirmede uyarı verilmeli"


def test_bos_metin_seslendirilemez():
    with pytest.raises(TTSError, match="boş"):
        synthesize_long_text(SahteSaglayici(), "  ", voice="test")


def test_maliyet_karakterle_dogru_orantili():
    tek = estimate(1000, "google_chirp3_hd").usd
    cift = estimate(2000, "google_chirp3_hd").usd
    assert cift == pytest.approx(tek * 2)


def test_saglayici_karsilastirmasi_ucuzdan_pahaliya_sirali():
    liste = compare_all(8500)
    assert [e.usd for e in liste] == sorted(e.usd for e in liste)
    assert liste[0].provider == "google_standard"


def test_bilinmeyen_saglayici_hata_verir():
    with pytest.raises(KeyError):
        estimate(1000, "yok-boyle-bir-servis")
