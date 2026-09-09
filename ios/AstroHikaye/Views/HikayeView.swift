import SwiftUI

struct HikayeView: View {
    let yanit: HikayeYaniti
    let basaDon: () -> Void

    enum Sekme: String, CaseIterable, Identifiable {
        case hikaye = "Hikâye"
        case harita = "Harita"
        case veri = "Veri"
        var id: String { rawValue }

        /// Açılışta gösterilecek sekme. Tasarım üzerinde çalışırken belirli
        /// bir sekmeyi doğrudan açabilmek için ortamdan okunur.
        static var baslangic: Sekme {
            #if DEBUG
            if let ad = ProcessInfo.processInfo.environment["ON_DOLDUR_SEKME"],
               let s = Sekme.allCases.first(where: {
                   $0.rawValue.lowercased().hasPrefix(ad.lowercased())
               }) {
                return s
            }
            #endif
            return .hikaye
        }
    }

    @State private var sekme: Sekme = Sekme.baslangic

    var body: some View {
        // Hikâye sekmesinde yıldız yoğunluğu düşük: metnin arkasındaki
        // hareketli noktalar uzun okumada dikkat dağıtıyor.
        GokZeminView(yildizSayisi: sekme == .hikaye ? 34 : 130) {
            VStack(spacing: 0) {
                SekmeCubugu(secili: $sekme)
                    .padding(.horizontal, 24)
                    .padding(.bottom, 4)

                switch sekme {
                case .hikaye: hikayeGovdesi
                case .harita: HaritaCarkiSayfasi(yanit: yanit)
                case .veri:   HaritaDetayView(yanit: yanit)
                }
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button {
                    basaDon()
                } label: {
                    Image(systemName: "chevron.left")
                }
                .tint(Tema.altin)
            }
            ToolbarItem(placement: .principal) {
                Text(yanit.baslik)
                    .font(.system(size: 15, weight: .medium, design: .serif))
                    .foregroundStyle(Tema.metin)
                    .lineLimit(1)
            }
            ToolbarItem(placement: .topBarTrailing) {
                ShareLink(item: paylasimMetni) {
                    Image(systemName: "square.and.arrow.up")
                }
                .tint(Tema.altin)
            }
        }
        .toolbarBackground(Tema.gokUst, for: .navigationBar)
        .toolbarBackground(.visible, for: .navigationBar)
    }

    // MARK: Hikâye

    private var hikayeGovdesi: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                basligiSayfasi

                ForEach(Array(paragraflar.enumerated()), id: \.offset) { indeks, p in
                    if p == "—" || p == "---" {
                        BolumAyraci().padding(.vertical, 26)
                    } else {
                        Text(p)
                            .font(Tema.govde(18))
                            .foregroundStyle(Tema.metin)
                            .lineSpacing(Tema.satirAraligi)
                            .padding(.bottom, 20)
                    }
                }

                KurguRozeti().padding(.top, 18)
            }
            .padding(.horizontal, 26)
            .padding(.bottom, 60)
            .textSelection(.enabled)
        }
    }

    private var basligiSayfasi: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text(yanit.baslik)
                .font(Tema.baslik(32))
                .foregroundStyle(Tema.metin)
                .lineSpacing(4)

            HStack(spacing: 8) {
                Text(yanit.yer.cozumlenenAd.components(separatedBy: ",").first
                     ?? yanit.yer.cozumlenenAd)
                Text("·")
                Text("\(yanit.kelimeSayisi) kelime")
            }
            .font(Tema.etiket(12))
            .tracking(0.8)
            .foregroundStyle(Tema.metinIkincil)

            BolumAyraci()
        }
        .padding(.top, 20)
        .padding(.bottom, 30)
    }

    /// Metni paragraflara ayırır.
    ///
    /// Bölme boş satırda yapılır, her satır sonunda değil: kaynak metin sert
    /// sarmalanmış olabilir ve her satırı ayrı paragraf saymak, aralıkları
    /// rastgele gösterip okuma ritmini bozar. Paragraf içindeki tek satır
    /// sonları boşluğa çevrilir.
    private var paragraflar: [String] {
        yanit.metin
            .components(separatedBy: "\n\n")
            .map { blok in
                blok.components(separatedBy: "\n")
                    .map { $0.trimmingCharacters(in: .whitespaces) }
                    .filter { !$0.isEmpty }
                    .joined(separator: " ")
            }
            .filter { !$0.isEmpty }
    }

    private var paylasimMetni: String {
        "\(yanit.baslik)\n\n\(yanit.metin)"
    }
}

// MARK: - Yardımcı görünümler

private struct SekmeCubugu: View {
    @Binding var secili: HikayeView.Sekme

    var body: some View {
        HStack(spacing: 0) {
            ForEach(HikayeView.Sekme.allCases) { s in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) { secili = s }
                } label: {
                    VStack(spacing: 7) {
                        Text(s.rawValue)
                            .font(Tema.etiket(12))
                            .tracking(1.0)
                            .foregroundStyle(secili == s ? Tema.altin : Tema.metinIkincil)
                        Rectangle()
                            .fill(secili == s ? Tema.altin : .clear)
                            .frame(height: 1.5)
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.top, 6)
    }
}

/// Bölümler arası ince altın ayraç.
struct BolumAyraci: View {
    var body: some View {
        HStack(spacing: 10) {
            Rectangle().fill(Tema.cizgi).frame(height: 1)
            Text("✦")
                .font(.system(size: 9))
                .foregroundStyle(Tema.altinSolgun.opacity(0.8))
            Rectangle().fill(Tema.cizgi).frame(height: 1)
        }
    }
}

/// Hikâyenin kurgu olduğunu söyleyen rozet. Ekranın altına iliştirilmiş
/// küçük punto bir feragatname değil, metnin bir parçası.
struct KurguRozeti: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 7) {
            HStack(spacing: 6) {
                Image(systemName: "sparkles").font(.system(size: 11))
                Text("KURGUSAL KATMAN").tracking(1.3)
            }
            .font(Tema.etiket(11))
            .foregroundStyle(Tema.altinSolgun)

            Text(BilgiMetinleri.katmanAyrimi)
                .font(Tema.govde(13))
                .foregroundStyle(Tema.metinIkincil)
                .lineSpacing(4)
        }
        .padding(15)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(Tema.altin.opacity(0.06))
                .overlay(
                    RoundedRectangle(cornerRadius: 12, style: .continuous)
                        .strokeBorder(Tema.altin.opacity(0.15), lineWidth: 1)
                )
        )
    }
}

// MARK: - Çark sayfası

private struct HaritaCarkiSayfasi: View {
    let yanit: HikayeYaniti

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                HaritaCarkiView(harita: yanit.harita)
                    .padding(.horizontal, 14)
                    .padding(.top, 12)

                if !yanit.harita.evler.mevcut {
                    Text(yanit.harita.evler.yoklugoSebebi ?? "")
                        .font(Tema.govde(13))
                        .foregroundStyle(Tema.metinIkincil)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 30)
                }

                // Çark okunaklı olsun diye semboller çarkta, adlar burada.
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())],
                          spacing: 10) {
                    ForEach(yanit.harita.gokCisimleri) { cisim in
                        HStack(spacing: 9) {
                            Text(Sembol.cisim(cisim.anahtar, ad: cisim.ad))
                                .font(.system(size: 17))
                                .foregroundStyle(Tema.altin)
                                .frame(width: 22)
                            VStack(alignment: .leading, spacing: 1) {
                                Text(cisim.ad)
                                    .font(Tema.etiket(12))
                                    .foregroundStyle(Tema.metin)
                                Text(cisim.gosterim)
                                    .font(Tema.veri(11))
                                    .foregroundStyle(Tema.metinIkincil)
                            }
                            Spacer(minLength: 0)
                        }
                    }
                }
                .padding(.horizontal, 22)
                .padding(.bottom, 50)
            }
        }
    }
}
