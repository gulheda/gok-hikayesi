import SwiftUI

struct HikayeView: View {
    let yanit: HikayeYaniti
    let basaDon: () -> Void

    private enum Sekme: String, CaseIterable, Identifiable {
        case hikaye = "Hikâye"
        case veri = "Hesaplanan veri"
        var id: String { rawValue }
    }

    @State private var sekme: Sekme = .hikaye

    var body: some View {
        VStack(spacing: 0) {
            Picker("Görünüm", selection: $sekme) {
                ForEach(Sekme.allCases) { s in Text(s.rawValue).tag(s) }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)
            .padding(.bottom, 8)

            switch sekme {
            case .hikaye: hikayeGovdesi
            case .veri: HaritaDetayView(yanit: yanit)
            }
        }
        .navigationTitle(yanit.baslik)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button("Yeniden", action: basaDon)
            }
            ToolbarItem(placement: .topBarTrailing) {
                ShareLink(item: paylasimMetni) {
                    Image(systemName: "square.and.arrow.up")
                }
            }
        }
    }

    private var hikayeGovdesi: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(yanit.baslik)
                    .font(.largeTitle.weight(.semibold))
                    .padding(.top, 8)

                ForEach(Array(paragraflar.enumerated()), id: \.offset) { _, p in
                    Text(p)
                        .font(.body)
                        .lineSpacing(6)
                }

                KurguRozeti()
                    .padding(.top, 12)
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 40)
            .textSelection(.enabled)
        }
    }

    private var paragraflar: [String] {
        yanit.metin
            .components(separatedBy: "\n")
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }
    }

    private var paylasimMetni: String {
        "\(yanit.baslik)\n\n\(yanit.metin)"
    }
}

/// Hikâyenin kurgu olduğunu söyleyen rozet. Ekranın altına iliştirilmiş
/// küçük punto bir feragatname değil, metnin bir parçası olarak duruyor.
struct KurguRozeti: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Label("Kurgusal katman", systemImage: "sparkles")
                .font(.footnote.weight(.semibold))
            Text(BilgiMetinleri.katmanAyrimi)
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.quaternary.opacity(0.4), in: RoundedRectangle(cornerRadius: 12))
    }
}
