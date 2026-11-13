// Uma página de um PDF desenhada em PNG, para conferir à vista uma transcrição feita pelas
// coordenadas (`consolidacao/anexos.py`) com a página do Diário da República.
//
// Compilar:  swiftc -O scripts/pdfpagina.swift -o .cache/pdfpagina
// Usar:      .cache/pdfpagina ficheiro.pdf PAGINA saida.png   (PAGINA a contar de 1; escala 2,5)
import Foundation
import PDFKit
import AppKit
let a = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: a[1]))!
let page = doc.page(at: Int(a[2])! - 1)!
let b = page.bounds(for: .mediaBox)
let img = page.thumbnail(of: CGSize(width: b.width*2.5, height: b.height*2.5), for: .mediaBox)
let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: a[3]))
