import SwiftUI

struct HataView: View {
    let mesaj: String
    let tekrarDene: () -> Void

    var body: some View {
        ContentUnavailableView {
            Label("Hikâye oluşturulamadı", systemImage: "exclamationmark.triangle")
        } description: {
            Text(mesaj)
        } actions: {
            Button("Bilgileri düzelt", action: tekrarDene)
                .buttonStyle(.borderedProminent)
        }
    }
}

#Preview {
    HataView(mesaj: "'Qwerty' için yer bulunamadı.") {}
}
