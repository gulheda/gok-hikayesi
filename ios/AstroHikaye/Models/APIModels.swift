import Foundation

// Backend Türkçe alan adları kullanıyor; burada Swift tarafında okunabilir
// adlara eşliyoruz. Eşleme tek yerde durursa API alan adı değiştiğinde
// derleyici tüm kullanım yerlerini gösterir.

struct DogumGirdisi: Encodable {
    var ad: String?
    var tarih: String        // YYYY-AA-GG
    var saat: String?        // SS:DD, bilinmiyorsa nil
    var yer: String
    var evSistemi: String = "placidus"

    enum CodingKeys: String, CodingKey {
        case ad, tarih, saat, yer
        case evSistemi = "ev_sistemi"
    }
}

struct YerBilgisi: Decodable {
    let cozumlenenAd: String
    let enlem: Double
    let boylam: Double
    let kaynak: String

    enum CodingKeys: String, CodingKey {
        case cozumlenenAd = "cozumlenen_ad"
        case enlem, boylam, kaynak
    }
}

struct GokCismi: Decodable, Identifiable {
    let anahtar: String
    let ad: String
    let boylam: Double        // ekliptik boylam; çarkı çizmek için gerekli
    let burc: String
    let burcDerece: Double
    let gosterim: String
    let element: String
    let nitelik: String
    let ev: Int?
    let evTemasi: String?
    let gerileme: Bool

    var id: String { anahtar }

    enum CodingKeys: String, CodingKey {
        case anahtar, ad, boylam, burc, gosterim, element, nitelik, ev, gerileme
        case burcDerece = "burc_derece"
        case evTemasi = "ev_temasi"
    }
}

struct Ev: Decodable, Identifiable {
    let no: Int
    let boylam: Double        // ev başlangıcının ekliptik boylamı
    let burc: String
    let tema: String
    var id: Int { no }
}

struct EvBilgisi: Decodable {
    let mevcut: Bool
    let sistem: String
    let yukselen: Double?
    let mc: Double?
    let yukselenBurc: String?
    let mcBurc: String?
    let yoklugoSebebi: String?
    let evListesi: [Ev]

    enum CodingKeys: String, CodingKey {
        case mevcut, sistem, yukselen, mc
        case yukselenBurc = "yukselen_burc"
        case mcBurc = "mc_burc"
        case yoklugoSebebi = "yoklugu_sebebi"
        case evListesi = "ev_listesi"
    }
}

struct Aci: Decodable, Identifiable {
    let a: String
    let b: String
    let tur: String
    let turAnahtar: String
    let orb: Double
    let guc: Double
    let dogas: String

    var id: String { "\(a)-\(b)-\(tur)" }

    enum CodingKeys: String, CodingKey {
        case a, b, tur, orb, guc, dogas
        case turAnahtar = "tur_anahtar"
    }
}

struct Denge: Decodable {
    let elementler: [String: Int]
    let baskinElement: String?
    let eksikElementler: [String]

    enum CodingKeys: String, CodingKey {
        case elementler
        case baskinElement = "baskin_element"
        case eksikElementler = "eksik_elementler"
    }
}

struct HaritaMeta: Decodable {
    let efemerisModu: String
    let uyarilar: [String]

    enum CodingKeys: String, CodingKey {
        case efemerisModu = "efemeris_modu"
        case uyarilar
    }
}

struct Harita: Decodable {
    let gokCisimleri: [GokCismi]
    let evler: EvBilgisi
    let acilar: [Aci]
    let denge: Denge
    let meta: HaritaMeta

    enum CodingKeys: String, CodingKey {
        case gokCisimleri = "gok_cisimleri"
        case evler, acilar, denge, meta
    }
}

struct HikayeYaniti: Decodable {
    let yer: YerBilgisi
    let harita: Harita
    let baslik: String
    let metin: String
    let olgusalPanel: String
    let yas: Int
    let kelimeSayisi: Int

    enum CodingKeys: String, CodingKey {
        case yer, harita, baslik, metin, yas
        case olgusalPanel = "olgusal_panel"
        case kelimeSayisi = "kelime_sayisi"
    }
}

struct HaritaYaniti: Decodable {
    let yer: YerBilgisi
    let harita: Harita
}

struct SeslendirmeYaniti: Decodable {
    let sesBase64: String
    let mimeTuru: String

    enum CodingKeys: String, CodingKey {
        case sesBase64 = "ses_base64"
        case mimeTuru = "mime_turu"
    }
}

/// Backend'in doğrulama hatalarında döndürdüğü gövde.
struct APIHataGovdesi: Decodable {
    let detail: APIHataDetayi
}

/// FastAPI `detail` alanını kimi zaman düz metin, kimi zaman doğrulama
/// hatası listesi olarak döndürür; iki biçimi de karşılıyoruz.
enum APIHataDetayi: Decodable {
    case metin(String)
    case dogrulama([String])

    init(from decoder: Decoder) throws {
        let tekil = try decoder.singleValueContainer()
        if let s = try? tekil.decode(String.self) {
            self = .metin(s)
            return
        }
        struct Girdi: Decodable { let msg: String }
        if let liste = try? tekil.decode([Girdi].self) {
            self = .dogrulama(liste.map(\.msg))
            return
        }
        self = .metin("Bilinmeyen doğrulama hatası")
    }

    var okunabilir: String {
        switch self {
        case .metin(let s): return s
        case .dogrulama(let m): return m.joined(separator: "\n")
        }
    }
}
