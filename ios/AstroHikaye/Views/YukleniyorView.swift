import SwiftUI

struct YukleniyorView: View {
    // Hikâye üretimi model çağrısını beklediği için uzun sürebilir; boş bir
    // spinner yerine hangi adımın sürdüğünü göstermek bekleyişi anlaşılır kılar.
    private let adimlar = [
        "Gökyüzü o an için hesaplanıyor…",
        "Gezegen konumları burçlara ve evlere yerleştiriliyor…",
        "Aralarındaki açılar çıkarılıyor…",
        "Hikâyen yazılıyor…"
    ]

    @State private var adimIndeksi = 0

    private let zamanlayici = Timer.publish(every: 3.5, on: .main, in: .common)
        .autoconnect()

    var body: some View {
        VStack(spacing: 24) {
            ProgressView()
                .controlSize(.large)

            Text(adimlar[adimIndeksi])
                .font(.callout)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .frame(maxWidth: 280)
                .transition(.opacity)
                .id(adimIndeksi)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .onReceive(zamanlayici) { _ in
            // Son adımda durur; sayaç metnin bitmesini değil, işin sürdüğünü anlatır.
            if adimIndeksi < adimlar.count - 1 {
                withAnimation { adimIndeksi += 1 }
            }
        }
        .navigationBarBackButtonHidden()
    }
}

#Preview {
    NavigationStack { YukleniyorView() }
}
