"""As linhas de uma página de um PDF com as palavras e a posição de cada uma, para ler quadros.

No texto simples de um PDF do DR, um quadro perde as colunas: "Topografia … Anual …. 2" não
diz se o 2 está nas aulas teóricas ou nas teórico-práticas, porque as células vazias não deixam
marca. Com a posição x de cada palavra (de `scripts/pdfchars.swift`), cada número fica na sua
coluna. Ver "Anexos só em imagem" em `consolidacao/README.md`.

Uso:
    .cache/pdfchars ficheiro.pdf PAGINA > pagina.tsv
    python consolidacao/pdf_colunas.py pagina.tsv

Saída: uma linha por linha visual, "y [x0-x1] palavra ‖ [x0-x1] palavra …". Os pontos de guia
("....") saem.
"""

from __future__ import annotations

import re
import sys


Caixa = tuple[float, float, float, float, str]


def ler(caminho: str) -> list[Caixa]:
    caixas = []
    for linha in open(caminho, encoding="utf-8"):
        x0, y0, x1, y1, c = linha.rstrip("\n").split("\t", 4)
        caixas.append((float(x0), float(y0), float(x1), float(y1), c))
    return caixas


def linhas(caixas: list[Caixa]) -> list[tuple[float, list[Caixa]]]:
    """Os caracteres agrupados por linha visual (pelo centro em y)."""
    saida: list[tuple[float, list[Caixa]]] = []
    for ch in sorted(caixas, key=lambda r: ((r[1] + r[3]) / 2, r[0])):
        yc = (ch[1] + ch[3]) / 2
        if saida and abs(saida[-1][0] - yc) < 2.5:
            saida[-1][1].append(ch)
        else:
            saida.append((yc, [ch]))
    return saida


def palavras(chs: list[Caixa]) -> list[tuple[float, float, str]]:
    """As palavras de uma linha (x0, x1, texto): um intervalo largo separa duas; sem pontos de guia."""
    chs = sorted((c for c in chs if c[4] != " "), key=lambda r: r[0])
    juntas: list[list] = []
    for c in chs:
        largura = c[2] - c[0]
        atual = juntas[-1] if juntas else None
        if atual and c[0] - atual[2] < max(2.2, 0.45 * largura):
            if c[0] - atual[2] > 0.9:
                atual[3] += " "
            atual[2] = c[2]
            atual[3] += c[4]
        else:
            juntas.append([c[0], c[1], c[2], c[4]])
    saida = []
    for i, (x0, _, x1, texto) in enumerate(juntas):
        guia_a_seguir = i + 1 < len(juntas) and re.fullmatch(r"[.\s]+", juntas[i + 1][3])
        # os pontos de guia: três ou mais no fim, ou os que se colam à palavra antes de um grupo
        # só de pontos ("virgem*." + ". . ."); um ponto final sem guia a seguir fica
        texto = re.sub(r"(?:\s*\.)+\s*$" if guia_a_seguir else r"(?:\s*\.){3,}\s*$", "", texto).strip()
        if texto and not re.fullmatch(r"[.\s]+", texto):
            saida.append((x0, x1, texto))
    return saida


def main() -> None:
    for yc, chs in linhas(ler(sys.argv[1])):
        print(f"{yc:6.1f} " + " ‖ ".join(f"[{a:.0f}-{b:.0f}] {t}" for a, b, t in palavras(chs)))


if __name__ == "__main__":
    main()
