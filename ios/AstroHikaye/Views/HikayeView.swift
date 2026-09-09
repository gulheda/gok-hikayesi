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

    /// Okuma puntosu çarpanı. Dynamic Type'ın üstüne biner: sistem ayarı
    /// tüm uygulamayı ölçekler, bu ise yalnızca hikâye metnini - uzun metin
    /// okurken kullanıcı yazıyı arayüzün geri kalanından bağımsız
    /// büyütebilmeli. Seçim cihazda kalıcı.
    @AppStorage("okumaPuntoCarpani") private var okumaCarpani: Double = 1.0

    /// Dynamic Type ile ölçeklenen temel punto; çarpan bunun üstüne uygulanır.
    @ScaledMetric(relativeTo: .body) private var temelPunto: CGFloat = 18

    private let carpanAraligi: ClosedRange<Double> = 0.85...1.6
    private let carpanAdimi: Double = 0.15

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
                .accessibilityLabel("Giriş ekranına dön")
            }
            ToolbarItem(placement: .principal) {
                Text(yanit.baslik)
                    .font(.system(size: 15, weight: .medium, design: .serif))
                    .foregroundStyle(Tema.metin)
                    .lineLimit(1)
            }
            if sekme == .hikaye {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Button {
                            okumaCarpani = min(carpanAraligi.upperBound,
                                               okumaCarpani + carpanAdimi)
                        } label: { Label("Yazıyı büyüt", systemImage: "textformat.size.larger") }
                        .disabled(okumaCarpani >= carpanAraligi.upperBound)

                        Button {
                            okumaCarpani = max(carpanAraligi.lowerBound,
                                               okumaCarpani - carpanAdimi)
                        } label: { Label("Yazıyı küçült", systemImage: "textformat.size.smaller") }
                        .disabled(okumaCarpani <= carpanAraligi.lowerBound)

                        Divider()
                        Button {
                            okumaCarpani = 1.0
                        } label: { Label("Varsayılan boyut", systemImage: "arrow.counterclockwise") }
                    } label: {
                        Image(systemName: "textformat.size")
                    }
                    .tint(Tema.altin)
                    .accessibilityLabel("Yazı boyutu")
                }
            }
            ToolbarItem(placement: .topBarTrailing) {
                ShareLink(item: paylasimMetni) {
                    Image(systemName: "square.and.arrow.up")
                }
                .tint(Tema.altin)
                .accessibilityLabel("Hikâyeyi paylaş")
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
                            .font(.system(size: temelPunto * okumaCarpani,
                                          design: .serif))
                            .foregroundStyle(Tema.metin)
                            .lineSpacing(Tema.satirAraligi * okumaCarpani)
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
                .font(Tema.baslik(.largeTitle))
                .foregroundStyle(Tema.metin)
                .lineSpacing(4)

            HStack(spacing: 8) {
                Text(yanit.yer.cozumlenenAd.components(separatedBy: ",").first
                     ?? yanit.yer.cozumlenenAd)
                Text("·")
                Text("\(yanit.kelimeSayisi) kelime")
            }
            .font(Tema.etiket(.caption))
            .tracking(0.8)
            .foregroundStyle(Tema.metinIkincil)
            .accessibilityElement(children: .combine)

            BolumAyraci().accessibilityHidden(true)
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
                            .font(Tema.etiket(.caption))
                            .tracking(1.0)
                            .foregroundStyle(secili == s ? Tema.altin : Tema.metinIkincil)
                            // Büyük puntolarda üç etiket yan yana sığmayınca
                            // kesilmek yerine biraz küçülsün.
                            .lineLimit(1)
                            .minimumScaleFactor(0.65)
                        Rectangle()
                            .fill(secili == s ? Tema.altin : .clear)
                            .frame(height: 1.5)
                    }
                }
                .frame(maxWidth: .infinity)
                .accessibilityLabel(s.rawValue)
                .accessibilityAddTraits(secili == s ? [.isButton, .isSelected] : .isButton)
            }
        }
        .padding(.top, 6)
        .accessibilityElement(children: .contain)
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
                .accessibilityHidden(true)
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
            .font(Tema.etiket(.caption2))
            .foregroundStyle(Tema.altinSolgun)

            Text(BilgiMetinleri.katmanAyrimi)
                .font(Tema.govde(.footnote))
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
                        .font(Tema.govde(.footnote))
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
                                    .font(Tema.etiket(.caption))
                                    .foregroundStyle(Tema.metin)
                                Text(cisim.gosterim)
                                    .font(Tema.veri(.caption2))
                                    .foregroundStyle(Tema.metinIkincil)
                            }
                            Spacer(minLength: 0)
                        }
                        // Sembol + ad + konum ayrı ayrı değil, tek bilgi olarak.
                        .accessibilityElement(children: .ignore)
                        .accessibilityLabel("\(cisim.ad), \(cisim.gosterim)"
                            + (cisim.ev.map { ", \($0). ev" } ?? ""))
                    }
                }
                .padding(.horizontal, 22)
                .padding(.bottom, 50)
            }
        }
    }
}
