import SwiftUI

/// Yükleme ekranı.
///
/// Hikâye üretimi bir model çağrısını beklediği için uzun sürebilir. Boş bir
/// spinner yerine dönen bir burç halkası ve hangi adımın sürdüğünü söyleyen
/// bir satır, bekleyişi hem anlaşılır hem ürünün diline ait kılıyor.
struct YukleniyorView: View {
    private let adimlar = [
        "Gökyüzü o an için hesaplanıyor",
        "Gezegenler burçlara ve evlere yerleşiyor",
        "Aralarındaki açılar çıkarılıyor",
        "Hikâyen yazılıyor",
    ]

    @State private var adimIndeksi = 0
    private let zamanlayici = Timer.publish(every: 4, on: .main, in: .common)
        .autoconnect()

    var body: some View {
        GokZeminView(yildizSayisi: 200) {
            VStack(spacing: 44) {
                DonenHalka()
                    .frame(width: 190, height: 190)
                    .accessibilityHidden(true)

                VStack(spacing: 14) {
                    Text(adimlar[adimIndeksi])
                        .font(Tema.govde(.callout))
                        .foregroundStyle(Tema.metin)
                        .multilineTextAlignment(.center)
                        .frame(maxWidth: 260)
                        .id(adimIndeksi)
                        .transition(.opacity.combined(with: .move(edge: .bottom)))

                    // Kaç adım geçildiğini gösteren noktalar: ilerleme
                    // yüzdesi uyduramayız, ama sürecin aşamaları gerçek.
                    HStack(spacing: 7) {
                        ForEach(adimlar.indices, id: \.self) { i in
                            Circle()
                                .fill(i <= adimIndeksi
                                      ? Tema.altin
                                      : Tema.metinIkincil.opacity(0.3))
                                .frame(width: 5, height: 5)
                        }
                    }
                }
                // Adım metni ve noktalar tek bir duyuru olarak okunsun.
                .accessibilityElement(children: .ignore)
                .accessibilityLabel(
                    "\(adimlar[adimIndeksi]). Adım \(adimIndeksi + 1) / \(adimlar.count)."
                )
                .accessibilityAddTraits(.updatesFrequently)
            }
        }
        .onReceive(zamanlayici) { _ in
            // Son adımda durur; sayaç metnin bitmesini değil, işin sürdüğünü anlatır.
            if adimIndeksi < adimlar.count - 1 {
                withAnimation(.easeInOut(duration: 0.4)) { adimIndeksi += 1 }
            }
        }
        .navigationBarBackButtonHidden()
    }
}

/// Yavaşça dönen burç halkası.
private struct DonenHalka: View {
    @Environment(\.accessibilityReduceMotion) private var hareketAzalt

    var body: some View {
        TimelineView(.animation) { zaman in
            Canvas { baglam, boyut in
                let merkez = CGPoint(x: boyut.width / 2, y: boyut.height / 2)
                let R = min(boyut.width, boyut.height) / 2
                let t = zaman.date.timeIntervalSinceReferenceDate
                let donme = hareketAzalt ? 0 : t * 6 // saniyede 6 derece

                func nokta(_ derece: Double, _ r: CGFloat) -> CGPoint {
                    let a = (derece + donme) * .pi / 180
                    return CGPoint(x: merkez.x - r * cos(a), y: merkez.y + r * sin(a))
                }

                for r in [R, R * 0.78] {
                    let kutu = CGRect(x: merkez.x - r, y: merkez.y - r,
                                      width: r * 2, height: r * 2)
                    baglam.stroke(Path(ellipseIn: kutu),
                                  with: .color(Tema.altinSolgun.opacity(0.3)),
                                  lineWidth: 1)
                }

                for i in 0..<12 {
                    let derece = Double(i) * 30
                    var ayrac = Path()
                    ayrac.move(to: nokta(derece, R * 0.78))
                    ayrac.addLine(to: nokta(derece, R))
                    baglam.stroke(ayrac,
                                  with: .color(Tema.altinSolgun.opacity(0.25)),
                                  lineWidth: 0.8)

                    // Dönerken öne gelen sembol parlar.
                    let ekranAcisi = (derece + donme)
                        .truncatingRemainder(dividingBy: 360)
                    let onde = cos((ekranAcisi - 270) * .pi / 180)
                    baglam.draw(
                        Text(Sembol.burclar[i])
                            .font(.system(size: R * 0.15))
                            .foregroundStyle(Tema.altin.opacity(0.35 + 0.55 * max(0, onde))),
                        at: nokta(derece + 15, R * 0.89)
                    )
                }

                // Merkezdeki soluk çekirdek
                let ic = R * 0.30
                baglam.fill(
                    Path(ellipseIn: CGRect(x: merkez.x - ic, y: merkez.y - ic,
                                           width: ic * 2, height: ic * 2)),
                    with: .radialGradient(
                        Gradient(colors: [Tema.altin.opacity(0.28), .clear]),
                        center: merkez, startRadius: 0, endRadius: ic
                    )
                )
            }
        }
    }
}

#Preview {
    NavigationStack { YukleniyorView() }
}
