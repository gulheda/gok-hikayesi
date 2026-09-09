import SwiftUI

struct GirisView: View {
    @Bindable var model: DeneyimModeli
    @FocusState private var odak: Alan?
    @Environment(\.dynamicTypeSize) private var puntoBoyutu

    private enum Alan { case ad, yer }

    var body: some View {
        GokZeminView(yildizSayisi: 170) {
            ScrollView {
                VStack(spacing: 0) {
                    baslikBolumu
                        .padding(.top, 48)
                        .padding(.bottom, 40)

                    kart {
                        MetinAlani(
                            etiket: "AD",
                            ipucu: "isteğe bağlı",
                            metin: $model.ad
                        )
                        .focused($odak, equals: .ad)

                        AyracCizgi()

                        TarihAlani(
                            etiket: "DOĞUM TARİHİ",
                            secim: $model.dogumTarihi,
                            bilesenler: .date,
                            aralik: tarihAraligi
                        )

                        AyracCizgi()

                        MetinAlani(
                            etiket: "DOĞUM YERİ",
                            ipucu: "örn. Denizli",
                            metin: $model.dogumYeri
                        )
                        .focused($odak, equals: .yer)
                    }

                    kart {
                        saatAnahtari

                        if model.saatBiliniyor {
                            AyracCizgi()
                            TarihAlani(
                                etiket: "SAAT",
                                secim: $model.dogumSaati,
                                bilesenler: .hourAndMinute,
                                aralik: nil
                            )
                        }
                    }
                    .padding(.top, 16)

                    aciklama
                        .padding(.top, 14)

                    olusturDugmesi
                        .padding(.top, 28)

                    katmanNotu
                        .padding(.top, 28)
                        .padding(.bottom, 48)
                }
                .padding(.horizontal, 24)
            }
            .scrollDismissesKeyboard(.interactively)
        }
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Bitti") { odak = nil }.tint(Tema.altin)
            }
        }
    }

    // MARK: Parçalar

    /// Doğum saati anahtarı.
    ///
    /// Erişilebilirlik puntolarında etiket ile anahtar yan yana sığmıyor ve
    /// etiket birkaç satıra bölünüyor. Bu boyutlarda iOS'un kendi kalıbını
    /// izliyoruz: etiket üstte, anahtar altında.
    @ViewBuilder
    private var saatAnahtari: some View {
        let baglama = $model.saatBiliniyor.animation(.easeInOut(duration: 0.25))

        if puntoBoyutu.isAccessibilitySize {
            VStack(alignment: .leading, spacing: 10) {
                Text("Doğum saatimi biliyorum")
                    .font(Tema.govde(.callout))
                    .foregroundStyle(Tema.metin)
                    .accessibilityHidden(true)
                Toggle("Doğum saatimi biliyorum", isOn: baglama)
                    .labelsHidden()
                    .tint(Tema.altin)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.vertical, 4)
        } else {
            Toggle(isOn: baglama) {
                Text("Doğum saatimi biliyorum")
                    .font(Tema.govde(.callout))
                    .foregroundStyle(Tema.metin)
            }
            .tint(Tema.altin)
            .padding(.vertical, 4)
        }
    }

    private var baslikBolumu: some View {
        VStack(spacing: 10) {
            Text("Gök Hikâyesi")
                .font(Tema.baslik(.largeTitle))
                .foregroundStyle(Tema.metin)

            Text("doğduğun anın gökyüzünden")
                .font(Tema.govde(.subheadline))
                .foregroundStyle(Tema.metinIkincil)
                .italic()
        }
    }

    private func kart<İçerik: View>(
        @ViewBuilder _ icerik: () -> İçerik
    ) -> some View {
        VStack(spacing: 0, content: icerik)
            .padding(.horizontal, 18)
            .padding(.vertical, 6)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.white.opacity(0.045))
                    .overlay(
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .strokeBorder(Tema.cizgi, lineWidth: 1)
                    )
            )
    }

    @ViewBuilder
    private var aciklama: some View {
        if model.saatBiliniyor {
            Text("Yükselen burç dört dakikada bir derece ilerler; saat ne kadar kesinse harita o kadar doğru olur.")
                .font(Tema.govde(.footnote))
                .foregroundStyle(Tema.metinIkincil)
                .frame(maxWidth: .infinity, alignment: .leading)
        } else {
            HStack(alignment: .top, spacing: 10) {
                Image(systemName: "exclamationmark.circle")
                    .foregroundStyle(Tema.altinSolgun)
                    .font(.system(size: 14))
                Text(model.saatsizUyarisi)
                    .font(Tema.govde(.footnote))
                    .foregroundStyle(Tema.metinIkincil)
            }
            .padding(14)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(Tema.altin.opacity(0.07))
            )
            .accessibilityElement(children: .combine)
        }
    }

    private var olusturDugmesi: some View {
        Button {
            odak = nil
            Task { await model.hikayeyiOlustur() }
        } label: {
            Text("Hikâyemi oluştur")
                .font(.system(size: 17, weight: .semibold, design: .serif))
                .foregroundStyle(Tema.gokAlt)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
                .background(
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .fill(model.gonderilebilir
                              ? Tema.altin
                              : Tema.altin.opacity(0.28))
                )
        }
        .disabled(!model.gonderilebilir)
        .accessibilityHint(model.gonderilebilir
                           ? "Doğum haritanı hesaplar ve hikâyeni yazar"
                           : "Önce doğum yerini girmelisin")
        .animation(.easeInOut(duration: 0.2), value: model.gonderilebilir)
    }

    private var katmanNotu: some View {
        VStack(spacing: 8) {
            Rectangle()
                .fill(Tema.cizgi)
                .frame(width: 40, height: 1)
                .accessibilityHidden(true)
            Text(BilgiMetinleri.katmanAyrimi)
                .font(Tema.govde(.caption))
                .foregroundStyle(Tema.metinIkincil.opacity(0.85))
                .multilineTextAlignment(.center)
                .lineSpacing(4)
        }
    }

    private var tarihAraligi: ClosedRange<Date> {
        let takvim = Calendar.current
        let baslangic = takvim.date(from: DateComponents(year: 1900, month: 1, day: 1))!
        return baslangic...Date()
    }
}

// MARK: - Alan bileşenleri

/// Etiketi üstte, girdisi altta duran alan. `Form` satırı yerine bunu
/// kullanmak, ekranın Ayarlar uygulaması gibi görünmesini engelliyor.
private struct MetinAlani: View {
    let etiket: String
    let ipucu: String
    @Binding var metin: String

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(etiket)
                .font(Tema.etiket(.caption2))
                .tracking(1.2)
                .foregroundStyle(Tema.altinSolgun.opacity(0.9))

            TextField("", text: $metin, prompt:
                Text(ipucu).foregroundStyle(Tema.metinIkincil.opacity(0.55))
            )
            .font(Tema.govde(.body))
            .foregroundStyle(Tema.metin)
            .textInputAutocapitalization(.words)
            .autocorrectionDisabled()
            // Etiket görsel olarak alanın üstünde duruyor; VoiceOver alanın
            // kendisini okuduğunda o etiketi görmez, bu yüzden bağlıyoruz.
            .accessibilityLabel(etiket)
        }
        .padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct TarihAlani: View {
    let etiket: String
    @Binding var secim: Date
    let bilesenler: DatePickerComponents
    let aralik: ClosedRange<Date>?

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(etiket)
                .font(Tema.etiket(.caption2))
                .tracking(1.2)
                .foregroundStyle(Tema.altinSolgun.opacity(0.9))

            HStack {
                if let aralik {
                    DatePicker("", selection: $secim, in: aralik,
                               displayedComponents: bilesenler)
                        .labelsHidden()
                } else {
                    DatePicker("", selection: $secim,
                               displayedComponents: bilesenler)
                        .labelsHidden()
                }
                Spacer()
            }
            .colorScheme(.dark)
            .tint(Tema.altin)
            .accessibilityLabel(etiket)
        }
        .padding(.vertical, 12)
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct AyracCizgi: View {
    var body: some View {
        Rectangle().fill(Tema.cizgi).frame(height: 1)
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
