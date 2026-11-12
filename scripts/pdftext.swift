// Texto de um PDF com o PDFKit do macOS; as páginas sem camada de texto (digitalizações)
// passam por OCR com o Vision. Usado por `leis_portugal.sources.pdftext` quando o pypdf
// não está instalado.
//
// Compilar:  swiftc -O scripts/pdftext.swift -o .cache/pdftext
// Usar:      LEIS_PORTUGAL_PDFTEXT=.cache/pdftext leis-portugal collect cnpd ...
//            (`pdftext ficheiro.pdf --sem-ocr` não tenta o OCR; com LEIS_PORTUGAL_OCR=0)
//
// Saída: a 1.ª linha é "%%PAGINAS <total> <por OCR> <sem texto>"; depois, o texto das
// páginas, separadas por \f.
import Foundation
import PDFKit
import Vision

func ocr(_ page: PDFPage) -> String {
    let bounds = page.bounds(for: .mediaBox)
    let scale: CGFloat = 2.5
    let size = CGSize(width: bounds.width * scale, height: bounds.height * scale)
    let image = page.thumbnail(of: size, for: .mediaBox)
    guard let tiff = image.tiffRepresentation, let bitmap = NSBitmapImageRep(data: tiff), let cg = bitmap.cgImage else { return "" }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["pt-PT", "pt-BR"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try? handler.perform([request])
    let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    return lines.joined(separator: "\n")
}

let args = CommandLine.arguments
guard args.count > 1, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    FileHandle.standardError.write("PDF ilegível\n".data(using: .utf8)!)
    exit(2)
}
let useOcr = !args.contains("--sem-ocr")
var pages: [String] = []
var ocrPages = 0
var emptyPages = 0
for index in 0..<doc.pageCount {
    guard let page = doc.page(at: index) else { continue }
    let text = (page.string ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
    if text.count >= 20 {
        pages.append(text)
    } else {
        let recognized = useOcr ? ocr(page) : ""
        if recognized.isEmpty { emptyPages += 1 } else { ocrPages += 1 }
        pages.append(recognized.isEmpty ? text : recognized)
    }
}
print("%%PAGINAS \(doc.pageCount) \(ocrPages) \(emptyPages)")
print(pages.joined(separator: "\n\u{0C}\n"))
