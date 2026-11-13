// OCR (Vision) de uma página de um PDF digitalizado, com a caixa de cada palavra, no formato do
// `pdfchars.swift`: uma linha por palavra, "x0 y0 x1 y1 palavra" separados por tabulações, em
// pontos da página e com o y a contar do topo. Dá ao `consolidacao/pdf_colunas.py` as colunas de
// um quadro das digitalizações anteriores a 1997 (ver "Anexos só em imagem", ronda 110, no
// `consolidacao/README.md`). Só serve para medir: o OCR não é fiel letra a letra.
//
// Compilar:  swiftc -O scripts/pdfocr.swift -o .cache/pdfocr
// Usar:      .cache/pdfocr ficheiro.pdf PAGINA > p.tsv && python consolidacao/pdf_colunas.py p.tsv
import Foundation
import PDFKit
import Vision

let args = CommandLine.arguments
guard args.count > 2, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])), let n = Int(args[2]),
      n >= 1, n <= doc.pageCount, let page = doc.page(at: n - 1) else {
    FileHandle.standardError.write("uso: pdfocr ficheiro.pdf PAGINA\n".data(using: .utf8)!)
    exit(2)
}
let bounds = page.bounds(for: .mediaBox)
let scale: CGFloat = 3
let image = page.thumbnail(of: CGSize(width: bounds.width * scale, height: bounds.height * scale), for: .mediaBox)
guard let tiff = image.tiffRepresentation, let bitmap = NSBitmapImageRep(data: tiff), let cg = bitmap.cgImage else { exit(3) }
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false  // a correção troca números e siglas por palavras
request.recognitionLanguages = ["pt-PT", "pt-BR"]
try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
var out = ""
for obs in request.results ?? [] {
    guard let cand = obs.topCandidates(1).first else { continue }
    let s = cand.string
    var i = s.startIndex
    while i < s.endIndex {
        while i < s.endIndex && s[i] == " " { i = s.index(after: i) }
        var j = i
        while j < s.endIndex && s[j] != " " { j = s.index(after: j) }
        if i < j, let caixa = try? cand.boundingBox(for: i..<j) {
            let r = caixa.boundingBox  // normalizada, origem em baixo à esquerda
            let x0 = r.minX * bounds.width, x1 = r.maxX * bounds.width
            let y0 = (1 - r.maxY) * bounds.height, y1 = (1 - r.minY) * bounds.height
            out += String(format: "%.1f\t%.1f\t%.1f\t%.1f\t", x0, y0, x1, y1) + String(s[i..<j]).replacingOccurrences(of: "\t", with: " ") + "\n"
        }
        i = j
    }
}
FileHandle.standardOutput.write(out.data(using: .utf8)!)
