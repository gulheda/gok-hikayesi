import SwiftUI

struct GirisView: View {
    @Bindable var model: DeneyimModeli

    var body: some View {
        Form {
            Section {
                TextField("Adın (isteğe bağlı)", text: $model.ad)
                    .textContentType(.givenName)

                DatePicker(
                    "Doğum tarihi",
                    selection: $model.dogumTarihi,
                    in: tarihAraligi,
                    displayedComponents: .date
                )

                TextField("Doğum yeri, örn. Denizli", text: $model.dogumYeri)
                    .textInputAutocapitalization(.words)
                    .autocorrectionDisabled()
            } header: {
                Text("Doğum bilgilerin")
            }

            Section {
                Toggle("Doğum saatimi biliyorum", isOn: $model.saatBiliniyor)

                if model.saatBiliniyor {
                    DatePicker(
                        "Doğum saati",
                        selection: $model.dogumSaati,
                        displayedComponents: .hourAndMinute
                    )
                } else {
                    Text(model.saatsizUyarisi)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            } header: {
                Text("Saat")
            } footer: {
                if model.saatBiliniyor {
                    Text("Yükselen burç dört dakikada bir derece ilerler; "
                         + "saat ne kadar kesinse harita o kadar doğru olur.")
                }
            }

            Section {
                Button {
                    Task { await model.hikayeyiOlustur() }
                } label: {
                    HStack {
                        Spacer()
                        Text("Hikâyemi oluştur")
                            .fontWeight(.semibold)
                        Spacer()
                    }
                }
                .disabled(!model.gonderilebilir)
            } footer: {
                Text(BilgiMetinleri.katmanAyrimi)
                    .font(.footnote)
            }
        }
        .navigationTitle("Gök Hikâyesi")
    }

    /// Efemeris veri dosyalarının kapsadığı aralık.
    private var tarihAraligi: ClosedRange<Date> {
        let takvim = Calendar.current
        let baslangic = takvim.date(from: DateComponents(year: 1900, month: 1, day: 1))!
        return baslangic...Date()
    }
}

enum BilgiMetinleri {
    static let katmanAyrimi = """
    Gök cismi konumları, doğduğun andaki gerçek astronomik veriden \
    hesaplanır. Bu konumlara yüklenen anlam ve kurulan hikâye ise \
    kurgudur; kişilik analizi veya öngörü değildir.
    """
}

#Preview {
    NavigationStack { GirisView(model: DeneyimModeli()) }
}
