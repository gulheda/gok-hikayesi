import Foundation
import Observation

/// Ekranların paylaştığı durum makinesi.
@Observable
final class DeneyimModeli {
    enum Durum {
        case giris
        case yukleniyor
        case hazir(HikayeYaniti)
        case hata(String)
    }

    var durum: Durum = .giris

    // Giriş formu alanları
    var ad: String = ""
    var dogumTarihi: Date = Calendar.current.date(
        from: DateComponents(year: 2000, month: 1, day: 1)
    ) ?? Date()
    var saatBiliniyor: Bool = true
    var dogumSaati: Date = Calendar.current.date(
        from: DateComponents(hour: 12, minute: 0)
    ) ?? Date()
    var dogumYeri: String = ""

    private let istemci = APIClient()

    init() {
        #if DEBUG
        // Geliştirme sırasında formu her seferinde elle doldurmamak için
        // başlatma ortamından ön doldurma. Yayın derlemesinde yer almaz.
        let ortam = ProcessInfo.processInfo.environment
        if let yer = ortam["ON_DOLDUR_YER"] { dogumYeri = yer }
        if let isim = ortam["ON_DOLDUR_AD"] { ad = isim }
        if let tarih = ortam["ON_DOLDUR_TARIH"] {
            let bicim = DateFormatter()
            bicim.dateFormat = "yyyy-MM-dd"
            bicim.locale = Locale(identifier: "en_US_POSIX")
            if let d = bicim.date(from: tarih) { dogumTarihi = d }
        }
        // Tasarım üzerinde çalışırken hikâye ekranını API çağrısı yapmadan
        // açabilmek için, uygulamayla gelen örnek yanıt yüklenir. Gerçek
        // veriyle üretilmiş bir harita taşır; yayın derlemesinde yer almaz.
        if ortam["ON_DOLDUR_ORNEK"] == "1", let ornek = Self.ornekYanit() {
            durum = .hazir(ornek)
        }
        if let saat = ortam["ON_DOLDUR_SAAT"] {
            let bicim = DateFormatter()
            bicim.dateFormat = "HH:mm"
            bicim.locale = Locale(identifier: "en_US_POSIX")
            if let d = bicim.date(from: saat) { dogumSaati = d }
        }
        #endif
    }

    var gonderilebilir: Bool {
        dogumYeri.trimmingCharacters(in: .whitespacesAndNewlines).count >= 2
    }

    /// Doğum saati bilinmediğinde neyin hesaplanamayacağı kullanıcıya
    /// önceden söylenir. Bu, ürünün "gerçek astronomik veri" iddiasının
    /// arayüzdeki karşılığı: eksik veriyi gizlemek yerine adını koyuyoruz.
    var saatsizUyarisi: String {
        """
        Doğum saati olmadan Yükselen burç ve ev yerleşimleri hesaplanamaz; \
        bunlar hikâyede yer almayacak. Gezegen burçları hesaplanır, ancak \
        Ay burcu gün içinde değişebildiği için yaklaşık kabul edilmelidir.
        """
    }

    private var girdi: DogumGirdisi {
        let tarihBicimi = DateFormatter()
        tarihBicimi.dateFormat = "yyyy-MM-dd"
        tarihBicimi.locale = Locale(identifier: "en_US_POSIX")

        let saatBicimi = DateFormatter()
        saatBicimi.dateFormat = "HH:mm"
        saatBicimi.locale = Locale(identifier: "en_US_POSIX")

        let temizAd = ad.trimmingCharacters(in: .whitespacesAndNewlines)
        return DogumGirdisi(
            ad: temizAd.isEmpty ? nil : temizAd,
            tarih: tarihBicimi.string(from: dogumTarihi),
            saat: saatBiliniyor ? saatBicimi.string(from: dogumSaati) : nil,
            yer: dogumYeri.trimmingCharacters(in: .whitespacesAndNewlines)
        )
    }

    @MainActor
    func hikayeyiOlustur() async {
        durum = .yukleniyor
        do {
            let yanit = try await istemci.hikaye(girdi)
            durum = .hazir(yanit)
        } catch let hata as APIHatasi {
            durum = .hata(hata.errorDescription ?? "Bilinmeyen hata")
        } catch {
            durum = .hata(error.localizedDescription)
        }
    }

    @MainActor
    func basaDon() {
        durum = .giris
    }

    #if DEBUG
    static func ornekYanit() -> HikayeYaniti? {
        guard let adres = Bundle.main.url(forResource: "ornek-yanit",
                                          withExtension: "json"),
              let veri = try? Data(contentsOf: adres) else { return nil }
        return try? JSONDecoder().decode(HikayeYaniti.self, from: veri)
    }
    #endif
}
