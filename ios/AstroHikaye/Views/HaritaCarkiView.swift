import SwiftUI

/// Doğum haritası çarkı.
///
/// Yerleşim geleneksel kurala uyar: Yükselen solda (saat 9 yönünde) durur ve
/// burçlar oradan saat yönünün TERSİNE ilerler. Ekran koordinatlarında y aşağı
/// büyüdüğü için dönüşüm şu: t = boylam - Yükselen iken
///     x = merkez.x - r·cos(t),  y = merkez.y + r·sin(t)
/// Bu, t=0'ı sola, t=90'ı aşağı, t=180'i sağa, t=270'i yukarı taşır.
///
/// Doğum saati bilinmiyorsa ev çemberi ve Yükselen yoktur; çark bu durumda
/// Koç'un sıfır derecesi solda olacak biçimde çizilir ve ev halkası hiç
/// gösterilmez. Olmayan veriyi çizmemek, olmayan veriyi raporlamakla aynı kural.
struct HaritaCarkiView: View {
    let harita: Harita

    /// Aynı dereceye yakın gök cisimleri üst üste binmesin diye uygulanan
    /// en küçük görsel ayrım.
    private let enAzAyrimDerece: Double = 7.0

    var body: some View {
        Canvas { baglam, boyut in
            let merkez = CGPoint(x: boyut.width / 2, y: boyut.height / 2)
            let R = min(boyut.width, boyut.height) / 2 - 2

            cizBurcHalkasi(baglam, merkez: merkez, R: R)
            if harita.evler.mevcut {
                cizEvler(baglam, merkez: merkez, R: R)
            }
            cizAcilar(baglam, merkez: merkez, R: R)
            cizGokCisimleri(baglam, merkez: merkez, R: R)
            if harita.evler.mevcut {
                cizAcisalEtiketler(baglam, merkez: merkez, R: R)
            }
        }
        .aspectRatio(1, contentMode: .fit)
        // Canvas VoiceOver için tamamen görünmezdir; içeriği sözlü bir özete
        // çevirmezsek çark ekran okuyucu kullanan biri için hiç yok demektir.
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(sesliTanim)
    }

    /// Çarkın ekran okuyucuya okunacak özeti.
    ///
    /// Tüm gök cisimlerini tek tek saymıyoruz - onlar zaten çarkın altındaki
    /// listede ayrı ayrı okunabiliyor. Burada yalnızca çarkın bir bakışta
    /// verdiği bilgi var: yerleşimin genel şekli.
    private var sesliTanim: String {
        var parcalar = ["Doğum haritası çarkı."]
        if harita.evler.mevcut, let yukselen = harita.evler.yukselenBurc {
            parcalar.append("Yükselen \(yukselen).")
            if let mc = harita.evler.mcBurc { parcalar.append("Tepe noktası \(mc).") }
            parcalar.append("Ev sistemi \(harita.evler.sistem).")
        } else {
            parcalar.append("Doğum saati bilinmediği için ev çemberi çizilmedi.")
        }
        parcalar.append("\(harita.gokCisimleri.count) gök cismi ve "
                        + "\(harita.acilar.count) açı gösteriliyor.")
        parcalar.append("Ayrıntılar aşağıdaki listede.")
        return parcalar.joined(separator: " ")
    }

    // MARK: - Geometri

    /// Çarkın döndürüleceği referans: Yükselen varsa o, yoksa Koç 0°.
    private var referans: Double {
        harita.evler.yukselen ?? 0
    }

    private func nokta(_ boylam: Double, _ merkez: CGPoint, _ r: CGFloat) -> CGPoint {
        let t = (boylam - referans) * .pi / 180
        return CGPoint(x: merkez.x - r * cos(t), y: merkez.y + r * sin(t))
    }

    private func cizgi(
        _ baglam: GraphicsContext, _ merkez: CGPoint,
        boylam: Double, ic: CGFloat, dis: CGFloat,
        renk: Color, kalinlik: CGFloat = 1
    ) {
        var yol = Path()
        yol.move(to: nokta(boylam, merkez, ic))
        yol.addLine(to: nokta(boylam, merkez, dis))
        baglam.stroke(yol, with: .color(renk), lineWidth: kalinlik)
    }

    private func cember(
        _ baglam: GraphicsContext, _ merkez: CGPoint, r: CGFloat,
        renk: Color, kalinlik: CGFloat = 1
    ) {
        let kutu = CGRect(x: merkez.x - r, y: merkez.y - r, width: r * 2, height: r * 2)
        baglam.stroke(Path(ellipseIn: kutu), with: .color(renk), lineWidth: kalinlik)
    }

    // MARK: - Katmanlar

    private func cizBurcHalkasi(_ baglam: GraphicsContext, merkez: CGPoint, R: CGFloat) {
        let dis = R
        let ic = R * 0.82

        cember(baglam, merkez, r: dis, renk: Tema.altinSolgun.opacity(0.55))
        cember(baglam, merkez, r: ic, renk: Tema.altinSolgun.opacity(0.35))

        for burcIndeks in 0..<12 {
            let baslangic = Double(burcIndeks) * 30

            // Burç sınırı
            cizgi(baglam, merkez, boylam: baslangic, ic: ic, dis: dis,
                  renk: Tema.altinSolgun.opacity(0.35))

            // Ateş/toprak/hava/su döngüsüne göre çok hafif dolgu — halkanın
            // on iki parçaya bölündüğü tek bakışta anlaşılsın diye.
            if burcIndeks % 2 == 0 {
                var dilim = Path()
                let adim = 1.0
                dilim.move(to: nokta(baslangic, merkez, ic))
                for a in stride(from: 0.0, through: 30.0, by: adim) {
                    dilim.addLine(to: nokta(baslangic + a, merkez, ic))
                }
                for a in stride(from: 30.0, through: 0.0, by: -adim) {
                    dilim.addLine(to: nokta(baslangic + a, merkez, dis))
                }
                dilim.closeSubpath()
                baglam.fill(dilim, with: .color(.white.opacity(0.035)))
            }

            // Her burcun ortasına sembolü
            let sembol = Sembol.burclar[burcIndeks]
            let yer = nokta(baslangic + 15, merkez, (ic + dis) / 2)
            baglam.draw(
                Text(sembol)
                    .font(.system(size: R * 0.085))
                    .foregroundStyle(Tema.altin.opacity(0.85)),
                at: yer
            )

            // Her on derecede bir çentik
            for onluk in stride(from: 10.0, to: 30.0, by: 10.0) {
                cizgi(baglam, merkez, boylam: baslangic + onluk,
                      ic: ic, dis: ic + R * 0.03,
                      renk: Tema.altinSolgun.opacity(0.25))
            }
        }
    }

    private func cizEvler(_ baglam: GraphicsContext, merkez: CGPoint, R: CGFloat) {
        let disHalka = R * 0.82
        let icHalka = R * 0.34

        cember(baglam, merkez, r: icHalka, renk: Tema.cizgi)

        for ev in harita.evler.evListesi {
            // Birinci, dördüncü, yedinci ve onuncu ev başlangıçları haritanın
            // eksenleridir; daha belirgin çizilir.
            let eksen = [1, 4, 7, 10].contains(ev.no)
            cizgi(baglam, merkez, boylam: ev.boylam, ic: icHalka, dis: disHalka,
                  renk: eksen ? Tema.altin.opacity(0.55) : Tema.cizgi,
                  kalinlik: eksen ? 1.4 : 0.7)

            // Ev numarası, evin ortasına
            let sonraki = harita.evler.evListesi
                .first { $0.no == (ev.no % 12) + 1 }?.boylam ?? ev.boylam
            let genislik = ((sonraki - ev.boylam).truncatingRemainder(dividingBy: 360) + 360)
                .truncatingRemainder(dividingBy: 360)
            let orta = ev.boylam + genislik / 2
            baglam.draw(
                Text("\(ev.no)")
                    .font(.system(size: R * 0.055, weight: .medium))
                    .foregroundStyle(Tema.metinIkincil.opacity(0.7)),
                at: nokta(orta, merkez, icHalka + R * 0.05)
            )
        }
    }

    private func cizAcilar(_ baglam: GraphicsContext, merkez: CGPoint, R: CGFloat) {
        let r = harita.evler.mevcut ? R * 0.34 : R * 0.55
        let konumlar = Dictionary(
            uniqueKeysWithValues: harita.gokCisimleri.map { ($0.ad, $0.boylam) }
        )

        for aci in harita.acilar {
            guard let a = konumlar[aci.a], let b = konumlar[aci.b] else { continue }
            var yol = Path()
            yol.move(to: nokta(a, merkez, r))
            yol.addLine(to: nokta(b, merkez, r))
            // Dar açı daha görünür: güç zaten orb'un tersiyle orantılı.
            baglam.stroke(
                yol,
                with: .color(Tema.aciRengi(aci.dogas).opacity(0.25 + 0.5 * aci.guc)),
                lineWidth: 0.6 + 1.2 * aci.guc
            )
        }
    }

    private func cizGokCisimleri(_ baglam: GraphicsContext, merkez: CGPoint, R: CGFloat) {
        let halka = R * 0.82
        let sembolYaricap = R * 0.66

        for (cisim, gosterimBoylam) in yerlestirilmisCisimler() {
            // Gerçek konumu gösteren çentik her zaman doğru derecede kalır;
            // yalnızca sembol çakışmayı önlemek için kaydırılır.
            cizgi(baglam, merkez, boylam: cisim.boylam,
                  ic: halka - R * 0.04, dis: halka,
                  renk: Tema.metin.opacity(0.55))

            // Çentik ile sembol arasında ince bağlantı
            var bag = Path()
            bag.move(to: nokta(cisim.boylam, merkez, halka - R * 0.04))
            bag.addLine(to: nokta(gosterimBoylam, merkez, sembolYaricap + R * 0.045))
            baglam.stroke(bag, with: .color(Tema.metin.opacity(0.2)), lineWidth: 0.5)

            let yer = nokta(gosterimBoylam, merkez, sembolYaricap)
            baglam.draw(
                Text(Sembol.cisim(cisim.anahtar, ad: cisim.ad))
                    .font(.system(size: R * 0.085))
                    .foregroundStyle(Tema.metin),
                at: yer
            )

            if cisim.gerileme {
                baglam.draw(
                    Text("R")
                        .font(.system(size: R * 0.04, weight: .bold))
                        .foregroundStyle(Tema.aciRengi("gergin").opacity(0.9)),
                    at: CGPoint(x: yer.x + R * 0.055, y: yer.y + R * 0.045)
                )
            }
        }
    }

    private func cizAcisalEtiketler(
        _ baglam: GraphicsContext, merkez: CGPoint, R: CGFloat
    ) {
        guard let asc = harita.evler.yukselen, let mc = harita.evler.mc else { return }
        for (etiket, boylam) in [("ASC", asc), ("MC", mc)] {
            baglam.draw(
                Text(etiket)
                    .font(.system(size: R * 0.05, weight: .semibold))
                    .foregroundStyle(Tema.altin),
                at: nokta(boylam, merkez, R * 1.0 - R * 0.04)
            )
        }
    }

    // MARK: - Çakışma çözümü

    /// Birbirine çok yakın duran gök cisimlerinin sembollerini görsel olarak
    /// ayırır. Gerçek boylam değiştirilmez; yalnızca sembolün çizileceği açı
    /// kaydırılır, ve gerçek konum ayrıca çentikle gösterilir.
    private func yerlestirilmisCisimler() -> [(GokCismi, Double)] {
        let sirali = harita.gokCisimleri.sorted {
            gorunumAcisi($0.boylam) < gorunumAcisi($1.boylam)
        }
        var acilar = sirali.map { gorunumAcisi($0.boylam) }

        // Birkaç geçişte komşuları iterek ayırıyoruz; tek geçiş üç ve daha
        // fazla cismin yığıldığı yerlerde yetmiyor.
        for _ in 0..<24 {
            var degisti = false
            for i in 0..<acilar.count {
                let j = (i + 1) % acilar.count
                var fark = acilar[j] - acilar[i]
                if j == 0 { fark += 360 }
                if fark < enAzAyrimDerece {
                    let itme = (enAzAyrimDerece - fark) / 2
                    acilar[i] -= itme
                    acilar[j] += itme
                    degisti = true
                }
            }
            if !degisti { break }
        }

        return zip(sirali, acilar).map { ($0, referans + $1) }
    }

    private func gorunumAcisi(_ boylam: Double) -> Double {
        let t = (boylam - referans).truncatingRemainder(dividingBy: 360)
        return t < 0 ? t + 360 : t
    }
}
