import SwiftUI

struct HataView: View {
    let mesaj: String
    let tekrarDene: () -> Void

    var body: some View {
        GokZeminView(yildizSayisi: 90) {
            VStack(spacing: 26) {
                Image(systemName: "moon.stars")
                    .font(.system(size: 44, weight: .light))
                    .foregroundStyle(Tema.altinSolgun)

                VStack(spacing: 12) {
                    Text("Hikâye oluşturulamadı")
                        .font(Tema.baslik(24))
                        .foregroundStyle(Tema.metin)

                    Text(mesaj)
                        .font(Tema.govde(15))
                        .foregroundStyle(Tema.metinIkincil)
                        .multilineTextAlignment(.center)
                        .lineSpacing(4)
                }

                Button(action: tekrarDene) {
                    Text("Bilgileri düzelt")
                        .font(.system(size: 16, weight: .semibold, design: .serif))
                        .foregroundStyle(Tema.gokAlt)
                        .padding(.horizontal, 28)
                        .padding(.vertical, 13)
                        .background(Capsule().fill(Tema.altin))
                }
                .padding(.top, 6)
            }
            .padding(.horizontal, 40)
        }
        .navigationBarBackButtonHidden()
    }
}

#Preview {
    HataView(mesaj: "'Qwerty' için yer bulunamadı. Şehir ve ülke şeklinde yazmayı deneyin.") {}
}
