import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

// Uygulama ikonu: gece göğü zemini, altın burç halkası, doğu ufkunda
// yükselen tek bir cisim. Küçük boyutta okunabilir olsun diye ayrıntı az.

let S: CGFloat = 1024
let uzay = CGColorSpace(name: CGColorSpace.sRGB)!
guard let ctx = CGContext(data: nil, width: Int(S), height: Int(S),
                          bitsPerComponent: 8, bytesPerRow: 0, space: uzay,
                          bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
else { fatalError("bağlam oluşturulamadı") }

func renk(_ r: CGFloat, _ g: CGFloat, _ b: CGFloat, _ a: CGFloat = 1) -> CGColor {
    CGColor(colorSpace: uzay, components: [r, g, b, a])!
}

let gokUst = renk(0.06, 0.07, 0.15)
let gokAlt = renk(0.015, 0.015, 0.04)
let altin  = renk(0.90, 0.72, 0.42)

// Zemin
let gecis = CGGradient(colorsSpace: uzay, colors: [gokUst, gokAlt] as CFArray,
                       locations: [0, 1])!
ctx.drawLinearGradient(gecis, start: CGPoint(x: 0, y: S),
                       end: CGPoint(x: 0, y: 0), options: [])

// Yıldızlar — sabit tohumla, ikon her üretimde aynı olsun
var tohum: UInt64 = 20030703
func rastgele() -> CGFloat {
    tohum = tohum &* 6364136223846793005 &+ 1442695040888963407
    return CGFloat((tohum >> 33) % 100_000) / 100_000
}
for _ in 0..<90 {
    let x = rastgele() * S, y = rastgele() * S
    let r = 1.5 + rastgele() * 3.5
    ctx.setFillColor(renk(1, 1, 1, 0.15 + rastgele() * 0.5))
    ctx.fillEllipse(in: CGRect(x: x - r, y: y - r, width: r * 2, height: r * 2))
}

let merkez = CGPoint(x: S / 2, y: S / 2)
// Halka, ikonun yuvarlatılmış köşelerinden güvenli mesafede kalmalı;
// iOS köşeleri kenarın yaklaşık dörtte biri kadar yuvarlar.
let disR = S * 0.30
let icR  = S * 0.23

// Burç halkası
ctx.setStrokeColor(altin)
ctx.setLineWidth(S * 0.011)
ctx.strokeEllipse(in: CGRect(x: merkez.x - disR, y: merkez.y - disR,
                             width: disR * 2, height: disR * 2))
ctx.setLineWidth(S * 0.007)
ctx.setStrokeColor(renk(0.90, 0.72, 0.42, 0.6))
ctx.strokeEllipse(in: CGRect(x: merkez.x - icR, y: merkez.y - icR,
                             width: icR * 2, height: icR * 2))

// On iki bölme — çarkla aynı dil
ctx.setLineWidth(S * 0.006)
ctx.setStrokeColor(renk(0.90, 0.72, 0.42, 0.55))
for i in 0..<12 {
    let a = CGFloat(i) * .pi / 6
    ctx.move(to: CGPoint(x: merkez.x + icR * cos(a), y: merkez.y + icR * sin(a)))
    ctx.addLine(to: CGPoint(x: merkez.x + disR * cos(a), y: merkez.y + disR * sin(a)))
    ctx.strokePath()
}

// Ufuk çizgisi: Yükselen ekseni, çarktaki gibi yatay
ctx.setLineWidth(S * 0.008)
ctx.setStrokeColor(renk(0.90, 0.72, 0.42, 0.85))
ctx.move(to: CGPoint(x: merkez.x - disR * 1.18, y: merkez.y))
ctx.addLine(to: CGPoint(x: merkez.x + disR * 1.18, y: merkez.y))
ctx.strokePath()

// Ufkun hemen üstünde yükselen cisim — hikâyedeki "kapıda duran" imge
// Cisim tam ufuk çizgisinin halkayı kestiği yerde: "Yükselen'de duran"
// imgesinin karşılığı. Hale ikonun dışına taşmasın diye halkanın üstünde.
let cisimR = S * 0.048
let cisimMerkez = CGPoint(x: merkez.x - disR, y: merkez.y + S * 0.022)
let hale = CGGradient(colorsSpace: uzay,
                      colors: [renk(1, 0.88, 0.62, 0.95), renk(0.9, 0.72, 0.42, 0)] as CFArray,
                      locations: [0, 1])!
ctx.drawRadialGradient(hale, startCenter: cisimMerkez, startRadius: 0,
                       endCenter: cisimMerkez, endRadius: cisimR * 2.9, options: [])
ctx.setFillColor(renk(1, 0.95, 0.85))
ctx.fillEllipse(in: CGRect(x: cisimMerkez.x - cisimR, y: cisimMerkez.y - cisimR,
                           width: cisimR * 2, height: cisimR * 2))

// Yaz
let cikti = CommandLine.arguments.count > 1
    ? CommandLine.arguments[1] : "AppIcon-1024.png"
guard let gorsel = ctx.makeImage(),
      let hedef = CGImageDestinationCreateWithURL(
        URL(fileURLWithPath: cikti) as CFURL, UTType.png.identifier as CFString, 1, nil)
else { fatalError("görsel yazılamadı") }
CGImageDestinationAddImage(hedef, gorsel, nil)
CGImageDestinationFinalize(hedef)
print("yazıldı: \(cikti)")
