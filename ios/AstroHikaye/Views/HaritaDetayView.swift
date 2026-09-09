import SwiftUI

/// Hesaplamanın çıktısı ham hâliyle.
///
/// Ürünün "bilimsel katman" iddiasının denetlenebilir olduğu yer burası:
/// kullanıcı sayıları görüp başka bir efemeris yazılımıyla karşılaştırabilir.
/// Bu yüzden `List` yerine, sayıların hizalandığı tek aralıklı bir düzen.
struct HaritaDetayView: View {
    let yanit: HikayeYaniti

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 26) {
                if !yanit.harita.meta.uyarilar.isEmpty {
                    bolum("NOTLAR") {
                        ForEach(yanit.harita.meta.uyarilar, id: \.self) { u in
                            HStack(alignment: .top, spacing: 8) {
                                Text("•").foregroundStyle(Tema.altinSolgun)
                                Text(u)
                                    .font(Tema.govde(13))
                                    .foregroundStyle(Tema.metinIkincil)
                                    .lineSpacing(3)
                            }
                        }
                    }
                }

                bolum("GÖK CİSİMLERİ") {
                    ForEach(yanit.harita.gokCisimleri) { cisim in
                        HStack(spacing: 10) {
                            Text(Sembol.cisim(cisim.anahtar, ad: cisim.ad))
                                .font(.system(size: 15))
                                .foregroundStyle(Tema.altin)
                                .frame(width: 20, alignment: .center)

                            Text(cisim.ad)
                                .font(Tema.govde(14))
                                .foregroundStyle(Tema.metin)

                            Spacer(minLength: 8)

                            Text(cisim.gosterim)
                                .font(Tema.veri(12))
                                .foregroundStyle(Tema.metinIkincil)

                            Text(cisim.ev.map { "\($0)" } ?? "–")
                                .font(Tema.veri(11))
                                .foregroundStyle(Tema.altinSolgun.opacity(0.8))
                                .frame(width: 18, alignment: .trailing)
                        }
                        .padding(.vertical, 3)
                    }
                }

                bolum("EVLER") {
                    if yanit.harita.evler.mevcut {
                        satir("Sistem", yanit.harita.evler.sistem)
                        if let y = yanit.harita.evler.yukselenBurc {
                            satir("Yükselen", y)
                        }
                        if let mc = yanit.harita.evler.mcBurc {
                            satir("Tepe noktası", mc)
                        }
                    } else {
                        Text(yanit.harita.evler.yoklugoSebebi
                             ?? "Ev sistemi hesaplanmadı.")
                            .font(Tema.govde(13))
                            .foregroundStyle(Tema.metinIkincil)
                            .lineSpacing(3)
                    }
                }

                if !yanit.harita.acilar.isEmpty {
                    bolum("AÇILAR") {
                        ForEach(yanit.harita.acilar.prefix(10)) { aci in
                            HStack(spacing: 8) {
                                Circle()
                                    .fill(Tema.aciRengi(aci.dogas))
                                    .frame(width: 6, height: 6)
                                Text("\(aci.a) – \(aci.b)")
                                    .font(Tema.govde(13))
                                    .foregroundStyle(Tema.metin)
                                Spacer(minLength: 6)
                                Text(aci.tur)
                                    .font(Tema.etiket(11))
                                    .foregroundStyle(Tema.metinIkincil)
                                Text(String(format: "%.2f°", aci.orb))
                                    .font(Tema.veri(11))
                                    .foregroundStyle(Tema.metinIkincil.opacity(0.7))
                                    .frame(width: 44, alignment: .trailing)
                            }
                            .padding(.vertical, 2)
                        }
                    }
                }

                bolum("ELEMENT DENGESİ") {
                    ForEach(["Ateş", "Toprak", "Hava", "Su"], id: \.self) { e in
                        let sayi = yanit.harita.denge.elementler[e] ?? 0
                        HStack(spacing: 10) {
                            Text(e)
                                .font(Tema.govde(14))
                                .foregroundStyle(sayi == 0 ? Tema.metinIkincil : Tema.metin)
                                .frame(width: 58, alignment: .leading)

                            // Sayıyı hem rakamla hem çubukla göstermek, eksik
                            // elementi tek bakışta görünür kılıyor.
                            GeometryReader { geo in
                                RoundedRectangle(cornerRadius: 2)
                                    .fill(sayi == 0
                                          ? Tema.metinIkincil.opacity(0.15)
                                          : Tema.altin.opacity(0.55))
                                    .frame(width: max(2, geo.size.width
                                                      * CGFloat(sayi) / 6.0),
                                           height: 6)
                                    .frame(maxHeight: .infinity, alignment: .center)
                            }
                            .frame(height: 14)

                            Text("\(sayi)")
                                .font(Tema.veri(12))
                                .foregroundStyle(Tema.metinIkincil)
                                .frame(width: 14, alignment: .trailing)
                        }
                    }

                    if !yanit.harita.denge.eksikElementler.isEmpty {
                        Text("Yerleşim almayan: "
                             + yanit.harita.denge.eksikElementler.joined(separator: ", "))
                            .font(Tema.govde(12))
                            .foregroundStyle(Tema.altinSolgun)
                            .padding(.top, 4)
                    }
                }

                bolum("HAM HESAPLAMA") {
                    ScrollView(.horizontal, showsIndicators: false) {
                        Text(yanit.olgusalPanel)
                            .font(Tema.veri(10))
                            .foregroundStyle(Tema.metinIkincil)
                            .textSelection(.enabled)
                    }
                }
            }
            .padding(.horizontal, 24)
            .padding(.top, 20)
            .padding(.bottom, 60)
        }
    }

    // MARK: Parçalar

    private func bolum<İçerik: View>(
        _ baslik: String, @ViewBuilder _ icerik: () -> İçerik
    ) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 10) {
                Text(baslik)
                    .font(Tema.etiket(11))
                    .tracking(1.4)
                    .foregroundStyle(Tema.altinSolgun)
                Rectangle().fill(Tema.cizgi).frame(height: 1)
            }
            VStack(alignment: .leading, spacing: 5, content: icerik)
        }
    }

    private func satir(_ etiket: String, _ deger: String) -> some View {
        HStack {
            Text(etiket)
                .font(Tema.govde(14))
                .foregroundStyle(Tema.metin)
            Spacer()
            Text(deger)
                .font(Tema.veri(12))
                .foregroundStyle(Tema.metinIkincil)
        }
    }
}
