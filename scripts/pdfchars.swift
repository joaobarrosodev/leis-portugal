// Cada carácter de uma página de um PDF com a sua caixa, para ler quadros pelas coordenadas
// (`consolidacao/pdf_colunas.py`). Saída: "x0\ty0\tx1\ty1\tc" por linha, em pontos, com y a
// contar do topo da página.
//
// Compilar:  swiftc -O scripts/pdfchars.swift -o .cache/pdfchars
// Usar:      .cache/pdfchars ficheiro.pdf PAGINA   (PAGINA a contar de 1)
import Foundation
import PDFKit
let a = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: a[1]))!
let p = Int(a[2])! - 1
let page = doc.page(at: p)!
let h = page.bounds(for: .mediaBox).height
let s = (page.string ?? "") as NSString
var out = ""
for i in 0..<s.length {
    let c = s.substring(with: NSRange(location: i, length: 1))
    if c == "\n" || c == "\r" { continue }
    guard let sel = page.selection(for: NSRange(location: i, length: 1)) else { continue }
    let b = sel.bounds(for: page)
    if b.width <= 0 && c != " " { continue }
    out += String(format: "%.1f\t%.1f\t%.1f\t%.1f\t", b.minX, h - b.maxY, b.maxX, h - b.minY) + c.replacingOccurrences(of: "\t", with: " ") + "\n"
}
FileHandle.standardOutput.write(out.data(using: .utf8)!)
