"""İl nüfusları — kalibrasyon örneklemini ağırlıklandırmak için.

İlleri eşit olasılıkla seçmek Türkiye'yi tarif etmez: İstanbul tek başına
nüfusun altıda birinden fazlasını barındırıyor, Bayburt yüz binde birinden
azını. Eşit örnekleme, küçük illeri yüz kat fazla temsil eder.

ÖLÇÜLEN ETKİ KÜÇÜK. Bu ağırlıklandırmanın ev yapılarının seyrekliğini
belirgin biçimde düzelteceğini varsaymıştım; ölçünce öyle olmadığı
görüldü. Nüfus ağırlığı ortalama enlemi yalnızca 0,016 derece kaydırıyor,
çünkü Türkiye nüfusu zaten enlem aralığına yayılmış durumda: İstanbul
41. paralelde, Ankara 39,9'da, İzmir 38,4'te, Antalya 36,9'da. Dağılımın
şekli biraz değişiyor (standart sapma 1,52'den 1,59'a çıkıyor) ama
merkezi neredeyse aynı kalıyor.

Yine de ağırlıklandırma korunuyor: doğrusu bu ve maliyeti yok. Ama
"bu düzeltme önemli" diye sunulmamalı - seyreklik ölçümünde fark
yaratan tek şey doğum saati dağılımıdır (bkz. story/ornekleme.py).

Değerler TÜİK 2023 adrese dayalı nüfus kayıt sistemi mertebesindedir ve
binlik basamağa yuvarlanmıştır. Amaç kesin nüfus değil, doğru orandır;
%2-3'lük sapmalar örnekleme ağırlığını anlamlı biçimde etkilemez.
"""
from __future__ import annotations

from typing import Dict

IL_NUFUSU: Dict[str, int] = {
    "istanbul": 15_655_000, "ankara": 5_803_000, "izmir": 4_479_000,
    "bursa": 3_214_000, "antalya": 2_696_000, "konya": 2_320_000,
    "adana": 2_270_000, "sanliurfa": 2_213_000, "gaziantep": 2_164_000,
    "kocaeli": 2_130_000, "mersin": 1_916_000, "diyarbakir": 1_818_000,
    "hatay": 1_544_000, "manisa": 1_475_000, "kayseri": 1_441_000,
    "samsun": 1_371_000, "balikesir": 1_257_000, "kahramanmaras": 1_178_000,
    "van": 1_128_000, "aydin": 1_161_000, "denizli": 1_060_000,
    "sakarya": 1_090_000, "tekirdag": 1_142_000, "mugla": 1_066_000,
    "eskisehir": 906_000, "mardin": 888_000, "malatya": 742_000,
    "trabzon": 819_000, "erzurum": 749_000, "ordu": 776_000,
    "afyonkarahisar": 751_000, "sivas": 634_000, "agri": 511_000,
    "tokat": 613_000, "sirnak": 570_000, "zonguldak": 588_000,
    "kutahya": 580_000, "batman": 647_000, "elazig": 596_000,
    "adiyaman": 668_000, "corum": 525_000, "canakkale": 566_000,
    "osmaniye": 559_000, "isparta": 447_000, "mus": 408_000,
    "giresun": 450_000, "kirklareli": 373_000, "duzce": 409_000,
    "edirne": 414_000, "bitlis": 353_000, "aksaray": 435_000,
    "nevsehir": 310_000, "yozgat": 418_000, "amasya": 336_000,
    "usak": 377_000, "kastamonu": 391_000, "rize": 344_000,
    "hakkari": 287_000, "siirt": 332_000, "bolu": 320_000,
    "nigde": 365_000, "kirsehir": 245_000, "kilis": 155_000,
    "karaman": 260_000, "kars": 274_000, "yalova": 296_000,
    "bingol": 283_000, "sinop": 220_000, "cankiri": 194_000,
    "burdur": 273_000, "karabuk": 254_000, "igdir": 201_000,
    "artvin": 169_000, "erzincan": 240_000, "bilecik": 228_000,
    "kirikkale": 277_000, "gumushane": 144_000, "ardahan": 83_000,
    "bartin": 205_000, "bayburt": 85_000, "tunceli": 88_000,
}


def toplam() -> int:
    return sum(IL_NUFUSU.values())
