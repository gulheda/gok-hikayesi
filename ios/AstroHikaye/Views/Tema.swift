import SwiftUI

/// Uygulamanın görsel dili tek yerde.
///
/// İki karar tasarımın tamamını belirliyor: arka plan bir gece göğü, ve
/// hikâye metni serif. Serif tercihi süs değil — metin edebî bir anlatı ve
/// uzun okunuyor; sistem sans-serif'i onu bir bildirim gibi gösteriyordu.
enum Tema {

    // MARK: Renkler

    /// Gece göğünün üst ve alt tonu. Düz siyah yerine maviye çalan koyu bir
    /// zemin, altın vurgunun üzerinde durabilmesi için gerekli.
    static let gokUst = Color(red: 0.04, green: 0.05, blue: 0.11)
    static let gokAlt = Color(red: 0.02, green: 0.02, blue: 0.05)

    static let altin = Color(red: 0.90, green: 0.72, blue: 0.42)
    static let altinSolgun = Color(red: 0.72, green: 0.60, blue: 0.40)
    static let metin = Color(red: 0.93, green: 0.92, blue: 0.88)
    static let metinIkincil = Color(red: 0.62, green: 0.62, blue: 0.66)
    static let cizgi = Color.white.opacity(0.12)

    /// Açı türlerinin rengi. Uyumlu açılar mavi-yeşil, gergin olanlar kızıl;
    /// nötr kavuşum altın. Renkler doygun değil, çünkü çarkın merkezinde
    /// onlarca çizgi üst üste biniyor.
    static func aciRengi(_ dogas: String) -> Color {
        switch dogas {
        case "uyumlu": return Color(red: 0.42, green: 0.72, blue: 0.78)
        case "gergin": return Color(red: 0.85, green: 0.42, blue: 0.40)
        default:       return altinSolgun
        }
    }

    static let gokZemin = LinearGradient(
        colors: [gokUst, gokAlt],
        startPoint: .top,
        endPoint: .bottom
    )

    // MARK: Tipografi
    //
    // Punto sabit verilmiyor, metin stiline bağlanıyor. `.system(size:)`
    // kullanıcının yazı boyutu ayarını yok sayar; 800 kelimelik bir metni
    // okunamaz punto ile sabitlemek erişilebilirlik açısından kabul edilemez.
    // Stil tabanlı fontlar Dynamic Type ile birlikte ölçeklenir ve ayar
    // değiştiğinde SwiftUI görünümü kendiliğinden yeniden çizer.

    /// Hikâye ve genel metin: serif.
    static func govde(_ stil: Font.TextStyle = .body) -> Font {
        .system(stil, design: .serif)
    }

    static func baslik(_ stil: Font.TextStyle = .largeTitle) -> Font {
        .system(stil, design: .serif).weight(.semibold)
    }

    /// Sayısal veri: rakamların hizalanması için tek aralıklı.
    static func veri(_ stil: Font.TextStyle = .caption) -> Font {
        .system(stil, design: .monospaced)
    }

    /// Küçük büyük harfli etiketler.
    static func etiket(_ stil: Font.TextStyle = .caption2) -> Font {
        .system(stil, design: .default).weight(.medium)
    }

    static let satirAraligi: CGFloat = 9
}

/// Astrolojik semboller. Unicode'da tanımlı oldukları için ek yazı tipi
/// gerekmiyor; yine de sistemde bulunmayan bir sembol olursa (Chiron bazı
/// sürümlerde eksik) adın ilk harfine düşüyoruz.
enum Sembol {
    static let gokCismi: [String: String] = [
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆",
        "Pluto": "♇", "TrueNode": "☊", "Chiron": "⚷",
    ]

    /// Koç'tan Balık'a burç sembolleri.
    ///
    /// U+2648–U+2653 aralığı Unicode'da varsayılan olarak EMOJI sunumuna
    /// sahiptir; iOS bunları renkli rozet olarak çizer ve çark bir anda
    /// oyuncak gibi görünür. U+FE0E (variation selector-15) sembolü metin
    /// sunumuna zorlar, böylece yazı tipinin rengini ve boyutunu alır.
    private static let metinSunumu = "\u{FE0E}"

    static let burclar = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]
        .map { $0 + metinSunumu }

    static func cisim(_ anahtar: String, ad: String) -> String {
        guard let sembol = gokCismi[anahtar] else { return String(ad.prefix(1)) }
        return sembol + metinSunumu
    }

    static func burc(boylamDerece: Double) -> String {
        let idx = Int((boylamDerece.truncatingRemainder(dividingBy: 360) + 360)
            .truncatingRemainder(dividingBy: 360) / 30)
        return burclar[min(idx, 11)]
    }
}
