import Foundation

enum APIHatasi: LocalizedError {
    case gecersizAdres
    case sunucu(kod: Int, mesaj: String)
    case aglaBaglanti(Error)
    case cozumleme(Error)

    var errorDescription: String? {
        switch self {
        case .gecersizAdres:
            return "Sunucu adresi geçersiz."
        case .sunucu(let kod, let mesaj):
            // 4xx kullanıcı girdisiyle ilgilidir ve mesajı doğrudan
            // gösterilebilir; 5xx'te sunucunun iç mesajını kullanıcıya
            // yansıtmak yerine genel bir ifade veriyoruz.
            return (400..<500).contains(kod)
                ? mesaj
                : "Sunucuda bir sorun oluştu. Lütfen biraz sonra tekrar deneyin."
        case .aglaBaglanti:
            return "İnternet bağlantısı kurulamadı."
        case .cozumleme:
            return "Sunucudan gelen yanıt okunamadı."
        }
    }
}

/// Backend ile konuşan tek nokta. API anahtarları yalnızca sunucuda durur;
/// uygulama hiçbir sağlayıcı anahtarı taşımaz.
actor APIClient {
    private let temelAdres: URL
    private let oturum: URLSession
    private let cozucu = JSONDecoder()

    init(temelAdres: URL = APIClient.varsayilanAdres) {
        self.temelAdres = temelAdres
        let yapilandirma = URLSessionConfiguration.default
        // Hikâye üretimi model çağrısını beklediği için uzun sürebilir.
        yapilandirma.timeoutIntervalForRequest = 180
        yapilandirma.timeoutIntervalForResource = 300
        self.oturum = URLSession(configuration: yapilandirma)
    }

    static var varsayilanAdres: URL {
        // Simülatörde makinedeki backend'e; gerçek cihazda Info.plist
        // üzerinden verilen adrese bağlanır.
        if let s = Bundle.main.object(forInfoDictionaryKey: "APITemelAdres") as? String,
           let u = URL(string: s) {
            return u
        }
        return URL(string: "http://127.0.0.1:8000")!
    }

    func harita(_ girdi: DogumGirdisi) async throws -> HaritaYaniti {
        try await gonder(yol: "/api/harita", govde: girdi)
    }

    func hikaye(_ girdi: DogumGirdisi) async throws -> HikayeYaniti {
        try await gonder(yol: "/api/hikaye", govde: girdi)
    }

    private func gonder<Govde: Encodable, Yanit: Decodable>(
        yol: String, govde: Govde
    ) async throws -> Yanit {
        guard let adres = URL(string: yol, relativeTo: temelAdres) else {
            throw APIHatasi.gecersizAdres
        }

        var istek = URLRequest(url: adres)
        istek.httpMethod = "POST"
        istek.setValue("application/json", forHTTPHeaderField: "Content-Type")
        istek.httpBody = try JSONEncoder().encode(govde)

        let veri: Data
        let yanit: URLResponse
        do {
            (veri, yanit) = try await oturum.data(for: istek)
        } catch {
            throw APIHatasi.aglaBaglanti(error)
        }

        guard let http = yanit as? HTTPURLResponse else {
            throw APIHatasi.sunucu(kod: -1, mesaj: "Yanıt okunamadı")
        }

        guard (200..<300).contains(http.statusCode) else {
            let mesaj = (try? cozucu.decode(APIHataGovdesi.self, from: veri))?
                .detail.okunabilir ?? "Beklenmeyen hata"
            throw APIHatasi.sunucu(kod: http.statusCode, mesaj: mesaj)
        }

        do {
            return try cozucu.decode(Yanit.self, from: veri)
        } catch {
            throw APIHatasi.cozumleme(error)
        }
    }
}
