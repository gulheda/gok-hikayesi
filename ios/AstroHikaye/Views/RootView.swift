import SwiftUI

struct RootView: View {
    @State private var model = DeneyimModeli()

    var body: some View {
        NavigationStack {
            switch model.durum {
            case .giris:
                GirisView(model: model)
            case .yukleniyor:
                YukleniyorView()
            case .hazir(let yanit):
                HikayeView(yanit: yanit) { model.basaDon() }
            case .hata(let mesaj):
                HataView(mesaj: mesaj) { model.basaDon() }
            }
        }
        .tint(.orange)
        .task {
            #if DEBUG
            // Geliştirmede uçtan uca akışı elle dokunmadan çalıştırmak için.
            if ProcessInfo.processInfo.environment["ON_DOLDUR_GONDER"] == "1",
               case .giris = model.durum, model.gonderilebilir {
                await model.hikayeyiOlustur()
            }
            #endif
        }
    }
}

#Preview {
    RootView()
}
