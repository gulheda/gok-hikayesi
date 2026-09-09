import SwiftUI

/// Hesaplamanın çıktısını ham hâliyle gösterir. Ürünün "bilimsel katman"
/// iddiasının denetlenebilir olduğu yer burası: kullanıcı sayıları görüp
/// başka bir efemeris yazılımıyla karşılaştırabilir.
struct HaritaDetayView: View {
    let yanit: HikayeYaniti

    var body: some View {
        List {
            if !yanit.harita.meta.uyarilar.isEmpty {
                Section("Notlar") {
                    ForEach(yanit.harita.meta.uyarilar, id: \.self) { u in
                        Text(u).font(.footnote).foregroundStyle(.secondary)
                    }
                }
            }

            Section("Gök cisimleri") {
                ForEach(yanit.harita.gokCisimleri) { cisim in
                    HStack {
                        Text(cisim.ad)
                        Spacer()
                        Text(cisim.gosterim)
                            .foregroundStyle(.secondary)
                            .monospacedDigit()
                        if let ev = cisim.ev {
                            Text("\(ev). ev")
                                .font(.caption)
                                .foregroundStyle(.tertiary)
                        }
                    }
                }
            }

            Section("Evler") {
                if yanit.harita.evler.mevcut {
                    LabeledContent("Sistem", value: yanit.harita.evler.sistem)
                    if let y = yanit.harita.evler.yukselenBurc {
                        LabeledContent("Yükselen", value: y)
                    }
                    if let mc = yanit.harita.evler.mcBurc {
                        LabeledContent("Tepe noktası", value: mc)
                    }
                } else {
                    Text(yanit.harita.evler.yoklugoSebebi
                         ?? "Ev sistemi hesaplanmadı.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }

            if !yanit.harita.acilar.isEmpty {
                Section("Açılar") {
                    ForEach(yanit.harita.acilar.prefix(10)) { aci in
                        HStack {
                            Text("\(aci.a) – \(aci.b)")
                            Spacer()
                            Text(aci.tur).foregroundStyle(.secondary)
                            Text(String(format: "%.1f°", aci.orb))
                                .font(.caption)
                                .foregroundStyle(.tertiary)
                                .monospacedDigit()
                        }
                    }
                }
            }

            Section("Element dengesi") {
                ForEach(["Ateş", "Toprak", "Hava", "Su"], id: \.self) { e in
                    LabeledContent(e, value: "\(yanit.harita.denge.elementler[e] ?? 0)")
                }
                if !yanit.harita.denge.eksikElementler.isEmpty {
                    LabeledContent(
                        "Yerleşim almayan",
                        value: yanit.harita.denge.eksikElementler.joined(separator: ", ")
                    )
                }
            }

            Section("Ham hesaplama") {
                Text(yanit.olgusalPanel)
                    .font(.system(.caption, design: .monospaced))
                    .textSelection(.enabled)
            }
        }
    }
}
