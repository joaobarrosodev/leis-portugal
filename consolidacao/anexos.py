"""Quadros que o acervo só tem em imagem, transcritos do PDF do DR pelas coordenadas.

No acervo, um quadro de um alterador é muitas vezes só uma ligação "(ver quadro no documento
original)" para o PDF do DR. Desde 1997 esses PDFs têm camada de texto. O texto simples perde as
colunas, mas a posição de cada palavra não (ver "Anexos só em imagem" em `README.md`). Aqui:

- `quadros ID ESPEC PDF` lê, com `scripts/pdfchars.swift` (compilado em `.cache/pdfchars`, ou no
  caminho de `LEIS_PORTUGAL_PDFCHARS`), as páginas e as faixas de y que a especificação dá. Cada
  palavra vai para a coluna em que começa, pelas fronteiras de x da especificação. Uma linha com
  alguma palavra fora da 1.ª coluna começa uma linha do quadro. Uma linha só com a 1.ª coluna
  continua a célula de cima. Escreve `anexos/<id>.json` com a especificação, o hash do PDF e o
  quadro em Markdown, para cada imagem do texto do alterador que se troca;
- `texto.com_anexos` troca, no texto do alterador, as imagens por esses quadros. Todos os pedidos
  ao LLM, as verificações letra a letra e as vistas às cegas leem o alterador por
  `texto.alterador`, e por isso veem o quadro.

A transcrição confere-se à parte, contra a imagem da página, por quem não a fez. O resultado fica
em "conferido" no ficheiro. Uma transcrição sem conferência não deve servir para aplicar nada.

Uso:
    python consolidacao/anexos.py quadros ID ESPEC.json FICHEIRO.pdf
    python consolidacao/anexos.py mostrar ID
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from pdf_colunas import Caixa, linhas, palavras
from texto import ANEXOS, IMAGEM_DR, RAIZ, front_matter, publicado


PDFCHARS = Path(os.environ.get("LEIS_PORTUGAL_PDFCHARS") or RAIZ / ".cache" / "pdfchars")
_ORDINAL = re.compile(r"\b(\d+)\.o\s*(?=[a-záéíóú])")


def caixas(pdf: Path, pagina: int) -> list[Caixa]:
    saida = subprocess.run([str(PDFCHARS), str(pdf), str(pagina)], capture_output=True, check=True, timeout=300)
    caixas = []
    for linha in saida.stdout.decode("utf-8").splitlines():
        x0, y0, x1, y1, c = linha.split("\t", 4)
        caixas.append((float(x0), float(y0), float(x1), float(y1), c))
    return caixas


def _celula(partes: list[str]) -> str:
    """As linhas de uma célula numa só: "Ali-" e "mentar." dão "Alimentar."."""
    texto = ""
    for p in partes:
        if texto.endswith("-") and p[:1].islower():
            texto = texto[:-1] + p
        else:
            texto = f"{texto} {p}".strip()
    return _ORDINAL.sub(r"\1.º ", texto).strip()


def quadro(pdf: Path, partes: list[dict], colunas: list[list]) -> str:
    """O quadro em Markdown: cabeçalho das colunas e uma linha por linha do quadro."""
    limites = [float(x) for _, x in colunas]
    linhas_quadro: list[list[list[str]]] = []
    for parte in partes:
        for yc, chs in linhas(caixas(pdf, parte["pagina"])):
            if not parte["de"] <= yc <= parte["ate"]:
                continue
            celulas: list[list[str]] = [[] for _ in colunas]
            for x0, _, texto in palavras(chs):
                k = max(i for i, limite in enumerate(limites) if x0 >= limite) if x0 >= limites[0] else 0
                celulas[k].append(texto)
            if any(celulas[1:]) or not linhas_quadro:
                linhas_quadro.append(celulas)
            else:
                linhas_quadro[-1][0] += celulas[0]
    saida = ["| " + " | ".join(nome for nome, _ in colunas) + " |", "| " + " | ".join("---" for _ in colunas) + " |"]
    for celulas in linhas_quadro:
        saida.append("| " + " | ".join(_celula(c) for c in celulas) + " |")
    return "\n".join(saida)


def _caminho(id_: str) -> Path:
    return ANEXOS / (id_.replace(":", "_") + ".json")


def _registo(id_: str) -> Path:
    for f in ("selecao-escala.jsonl", "selecao.jsonl"):
        for linha in (RAIZ / "consolidacao" / f).read_text(encoding="utf-8").splitlines():
            r = json.loads(linha)
            for d in [r] + r.get("alteradores", []):
                if d.get("id") == id_ and d.get("path"):
                    return RAIZ / d["path"]
    raise SystemExit(f"{id_}: não está nas seleções")


def quadros(id_: str, espec: Path, pdf: Path) -> None:
    e = json.loads(espec.read_text(encoding="utf-8"))
    registo = _registo(id_)
    if front_matter(registo.read_text(encoding="utf-8")).get("id") != id_:
        raise SystemExit(f"{registo}: o id não é {id_}")
    n_imagens = len(IMAGEM_DR.findall(publicado(registo)))
    transcricoes = []
    for q in e["quadros"]:
        if not 1 <= q["ocorrencia"] <= n_imagens:
            raise SystemExit(f"ocorrência {q['ocorrencia']} fora das {n_imagens} imagens do texto")
        transcricoes.append({"ocorrencia": q["ocorrencia"], "partes": q["partes"], "colunas": e["colunas"],
                             "texto": quadro(pdf, q["partes"], e["colunas"])})
    dados = {
        "id": id_,
        "titulo": e["titulo"],
        "pdf": e["pdf"],
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "metodo": "camada de texto do PDF, colunas pelas coordenadas (consolidacao/anexos.py, scripts/pdfchars.swift)",
        "imagens_no_texto": n_imagens,
        "conferido": e.get("conferido"),
        "transcricoes": transcricoes,
    }
    ANEXOS.mkdir(exist_ok=True)
    _caminho(id_).write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{_caminho(id_).relative_to(RAIZ)}: {len(transcricoes)} quadros de {n_imagens} imagens")


def mostrar(id_: str) -> None:
    for t in json.loads(_caminho(id_).read_text(encoding="utf-8"))["transcricoes"]:
        print(f"## Imagem {t['ocorrencia']}\n\n{t['texto']}\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("quadros")
    q.add_argument("id")
    q.add_argument("espec", type=Path)
    q.add_argument("pdf", type=Path)
    m = sub.add_parser("mostrar")
    m.add_argument("id")
    a = ap.parse_args()
    if a.cmd == "quadros":
        quadros(a.id, a.espec, a.pdf)
    else:
        mostrar(a.id)


if __name__ == "__main__":
    main()
