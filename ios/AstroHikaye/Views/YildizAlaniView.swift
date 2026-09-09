import SwiftUI

/// Arka plandaki yıldız alanı.
///
/// Yıldızlar her çizimde yeniden rastgele üretilseydi ekran her yenilemede
/// titrerdi; bu yüzden sabit bir tohumla bir kez üretilip saklanıyorlar.
struct YildizAlaniView: View {
    var yildizSayisi: Int = 140
    var parlama: Bool = true

    private let yildizlar: [Yildiz]

    init(yildizSayisi: Int = 140, parlama: Bool = true, tohum: UInt64 = 20030703) {
        self.yildizSayisi = yildizSayisi
        self.parlama = parlama
        var uretec = SabitUretec(tohum: tohum)
        self.yildizlar = (0..<yildizSayisi).map { _ in
            Yildiz(
                x: Double.random(in: 0...1, using: &uretec),
                y: Double.random(in: 0...1, using: &uretec),
                yaricap: Double.random(in: 0.4...1.5, using: &uretec),
                parlaklik: Double.random(in: 0.15...0.75, using: &uretec),
                faz: Double.random(in: 0...(2 * .pi), using: &uretec)
            )
        }
    }

    var body: some View {
        TimelineView(.animation(minimumInterval: parlama ? 1.0 / 12.0 : nil)) { zaman in
            Canvas { baglam, boyut in
                let t = zaman.date.timeIntervalSinceReferenceDate
                for yildiz in yildizlar {
                    // Her yıldız kendi fazında, çok hafif nefes alıyor.
                    let salinim = parlama
                        ? 0.75 + 0.25 * sin(t * 0.7 + yildiz.faz)
                        : 1.0
                    let nokta = CGRect(
                        x: yildiz.x * boyut.width - yildiz.yaricap,
                        y: yildiz.y * boyut.height - yildiz.yaricap,
                        width: yildiz.yaricap * 2,
                        height: yildiz.yaricap * 2
                    )
                    baglam.fill(
                        Path(ellipseIn: nokta),
                        with: .color(.white.opacity(yildiz.parlaklik * salinim))
                    )
                }
            }
        }
        .allowsHitTesting(false)
    }

    private struct Yildiz {
        let x, y, yaricap, parlaklik, faz: Double
    }
}

/// Tohumlanabilir üreteç — aynı tohum her zaman aynı gökyüzünü verir.
struct SabitUretec: RandomNumberGenerator {
    private var durum: UInt64

    init(tohum: UInt64) { self.durum = tohum &+ 0x9E3779B97F4A7C15 }

    mutating func next() -> UInt64 {
        durum &+= 0x9E3779B97F4A7C15
        var z = durum
        z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
        z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
        return z ^ (z >> 31)
    }
}

/// Gece göğü zemini + yıldızlar. Her ekranın altına konur.
struct GokZeminView<Icerik: View>: View {
    var yildizSayisi: Int = 140
    @ViewBuilder var icerik: () -> Icerik

    var body: some View {
        ZStack {
            Tema.gokZemin.ignoresSafeArea()
            YildizAlaniView(yildizSayisi: yildizSayisi).ignoresSafeArea()
            icerik()
        }
    }
}
