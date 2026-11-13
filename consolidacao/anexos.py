"""Quadros que o acervo só tem em imagem, transcritos do PDF do DR pelas coordenadas.

No acervo, um quadro de um alterador é muitas vezes só uma ligação "(ver quadro no documento
original)" para o PDF do DR. Desde 1997 esses PDFs têm camada de texto. O texto simples perde as
colunas, mas a posição de cada palavra não (ver "Anexos só em imagem" em `README.md`, com o guia
passo a passo). Aqui:

- `quadros ID ESPEC PDF` lê, com `scripts/pdfchars.swift` (compilado em `.cache/pdfchars`, ou no
  caminho de `LEIS_PORTUGAL_PDFCHARS`), as páginas e as faixas de y que a especificação dá, e
  escreve `anexos/<id>.json`: a especificação, o hash do PDF, o número de imagens do texto do
  alterador e o texto de cada imagem que se troca;
- `refazer ID PDF` volta a transcrever a partir do próprio `anexos/<id>.json` e diz se o texto mudou;
- `mostrar ID` mostra as transcrições;
- `texto.com_anexos` troca, no texto do alterador, as imagens pelas transcrições. Todos os pedidos
  ao LLM, as verificações letra a letra e as vistas às cegas leem o alterador por
  `texto.alterador`, e por isso veem o quadro. O original nunca se transcreve.

A especificação (JSON):

    {"titulo": "...", "pdf": "<URL do PDF no DR>",
     "colunas": [["Nome da coluna", x_inicial], ...],          # por omissão, para os quadros
     "conferido": {"data": "...", "por": "...", "resultado": "..."},
     "quadros": [{"ocorrencia": N, "blocos": [
         {"tipo": "texto", "partes": [{"pagina": P, "de": y0, "ate": y1}]},
         {"tipo": "quadro", "partes": [{"pagina": P, "de": y0, "ate": y1, "x_de": 0, "x_ate": 300}],
          "colunas": [...], "valores_no_fim": false, "recuo": null, "colunas_de_valor": []}]}]}

- "ocorrencia" é a N-ésima ligação a uma imagem do DR no texto do alterador (`texto.IMAGEM_DR`);
- "partes" são faixas de y (o centro da linha, em pontos, a contar do topo) numa ou mais páginas;
  "x_de"/"x_ate" cortam uma coluna da página, quando o DR tem outro diploma ao lado;
- num quadro, cada palavra vai para a coluna cujo x inicial é o maior que não passa do x0 dela. Uma
  linha com alguma palavra fora da 1.ª coluna é uma linha do quadro; uma linha só com a 1.ª coluna
  continua a célula de cima ou, com "valores_no_fim", começa a da linha seguinte. O cabeçalho sai
  dos nomes das colunas, copiados da imagem; deixa-se fora das faixas;
- com "recuo" (um x), as continuações vêm recuadas: só abre linha do quadro a linha com uma palavra
  da 1.ª coluna antes desse x, e as outras continuam as células de cima, coluna a coluna; nas
  "colunas_de_valor", que não partem em duas linhas, um segundo valor (os agrupados por uma
  chaveta) fica na mesma célula, depois de "<br>", e o carácter da chaveta ("{") sai;
- um bloco de texto junta as linhas em parágrafos (um intervalo maior do que 1,6 vezes o habitual
  abre um parágrafo novo);
- em todas as células: os pontos de guia saem ("…… 4" e "virgem*." seguido de ". . ."), uma palavra
  partida no fim da linha junta-se ("Ali-" + "mentar."; "Pós-" + "-Coloniais." dá "Pós-Coloniais."), e "1.o"/"N.o" passam a "1.º"/"N.º".

A transcrição confere-se à parte, contra a imagem da página (`scripts/pdfpagina.swift`), por quem
não a fez, e o resultado fica em "conferido". Uma transcrição sem conferência não serve para
aplicar nada. O que o PDF não dá letra a letra ("€" lido como "E", palavras coladas sem espaço,
células com chavetas) não se transcreve: corrigir à mão deixaria de ser uma transcrição.

Uso:
    python consolidacao/anexos.py quadros ID ESPEC.json FICHEIRO.pdf
    python consolidacao/anexos.py refazer ID FICHEIRO.pdf
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
_NUMERO = re.compile(r"\b([Nn])\.o(?=\s|\d|$)")  # "N.o 1" é "N.º 1" com o º em expoente
_SO_ORDINAL = re.compile(r"^(\d+)\.o$")  # uma célula só com "10.o" é "10.º"


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
        elif texto.endswith("-") and p.startswith("-") and p[1:2].isalpha():
            texto = texto + p[1:]  # "Pós-" + "-Coloniais.": o DR repete o hífen de uma palavra composta
        else:
            texto = f"{texto} {p}".strip()
    return _SO_ORDINAL.sub(r"\1.º", _NUMERO.sub(r"\1.º", _ORDINAL.sub(r"\1.º ", texto)).strip())


def _linhas_das_partes(pdf: Path, partes: list[dict]):
    for parte in partes:
        # "x_de"/"x_ate" cortam uma coluna da página (o DR tem duas, com outros diplomas ao lado)
        cs = [c for c in caixas(pdf, parte["pagina"]) if parte.get("x_de", 0) <= c[0] < parte.get("x_ate", 1e9)]
        for yc, chs in linhas(cs):
            if parte["de"] <= yc <= parte["ate"]:
                yield yc, palavras(chs)


def quadro(pdf: Path, partes: list[dict], colunas: list[list], valores_no_fim: bool = False,
           recuo: float | None = None, colunas_de_valor: list[int] = ()) -> str:
    """O quadro em Markdown: cabeçalho das colunas e uma linha por linha do quadro.

    Uma linha com alguma palavra fora da 1.ª coluna é uma linha do quadro. Uma linha só com a 1.ª
    coluna continua a célula de cima, ou, com `valores_no_fim`, começa a da linha seguinte (quando
    os valores estão na última linha de uma designação longa).

    Com `recuo` (um x), as continuações vêm recuadas em todas as colunas (a lista da Portaria
    269/2006): só começa uma linha do quadro a que tem uma palavra da 1.ª coluna antes de `recuo`.
    As outras continuam, coluna a coluna, as células de cima. Nas `colunas_de_valor` (índices a
    partir de 0), que nunca partem em duas linhas, uma continuação numa célula já cheia é outro valor
    da mesma célula (os valores agrupados por uma chaveta), e fica separado por "<br>"."""
    limites = [float(x) for _, x in colunas]
    linhas_quadro: list[list[list[str]]] = []
    pendente: list[str] = []
    for _, ps in _linhas_das_partes(pdf, partes):
        celulas: list[list[str]] = [[] for _ in colunas]
        for x0, _, texto in ps:
            if colunas_de_valor and texto in ("{", "}"):
                continue  # a chaveta que agrupa os valores: fica dita pelo "<br>"
            k = max(i for i, limite in enumerate(limites) if x0 >= limite) if x0 >= limites[0] else 0
            celulas[k].append(texto)
        if recuo is not None:
            if any(x0 < recuo for x0, _, _ in ps) or not linhas_quadro:
                linhas_quadro.append(celulas)
                continue
            for k, c in enumerate(celulas):
                if c and k in colunas_de_valor and linhas_quadro[-1][k]:
                    linhas_quadro[-1][k] += ["<br>"] + c
                else:
                    linhas_quadro[-1][k] += c
            continue
        if any(celulas[1:]) or (not linhas_quadro and not valores_no_fim):
            celulas[0] = pendente + celulas[0]
            pendente = []
            linhas_quadro.append(celulas)
        elif valores_no_fim:
            pendente += celulas[0]
        else:
            linhas_quadro[-1][0] += celulas[0]
    if pendente:
        raise ValueError(f"texto da 1.ª coluna sem linha de valores a seguir: {' '.join(pendente)[:80]}")
    saida = ["| " + " | ".join(nome for nome, _ in colunas) + " |", "| " + " | ".join("---" for _ in colunas) + " |"]
    for celulas in linhas_quadro:
        saida.append("| " + " | ".join(_valores(c) for c in celulas) + " |")
    return "\n".join(saida)


def _valores(partes: list[str]) -> str:
    """Uma célula com um ou mais valores separados por "<br>" (ver `quadro`, `colunas_de_valor`)."""
    valores, atual = [], []
    for p in partes + ["<br>"]:
        if p == "<br>":
            valores.append(_celula(atual))
            atual = []
        else:
            atual.append(p)
    return "<br>".join(valores)


def texto_corrido(pdf: Path, partes: list[dict]) -> str:
    """Parágrafos de texto: as linhas juntam-se, e um intervalo maior do que 1,6 vezes o habitual
    entre linhas abre um parágrafo novo."""
    ls = [(yc, " ".join(t for _, _, t in ps)) for yc, ps in _linhas_das_partes(pdf, partes) if ps]
    if not ls:
        return ""
    saltos = sorted(b[0] - a[0] for a, b in zip(ls, ls[1:], strict=False) if b[0] > a[0])
    normal = saltos[(len(saltos) - 1) // 2] if saltos else 0
    paragrafos: list[list[str]] = [[ls[0][1]]]
    for (y0, _), (y1, t) in zip(ls, ls[1:], strict=False):
        if normal and (y1 - y0 > 1.6 * normal or y1 < y0):
            paragrafos.append([t])
        else:
            paragrafos[-1].append(t)
    return "\n\n".join(_celula(p) for p in paragrafos)


def bloco(pdf: Path, b: dict, colunas: list[list] | None) -> str:
    if b.get("tipo") == "texto":
        return texto_corrido(pdf, b["partes"])
    return quadro(pdf, b["partes"], b.get("colunas") or colunas, bool(b.get("valores_no_fim")), b.get("recuo"), b.get("colunas_de_valor") or ())


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
        blocos = q.get("blocos") or [{"tipo": "quadro", "partes": q["partes"]}]
        texto = "\n\n".join(bloco(pdf, b, e.get("colunas")) for b in blocos)
        transcricoes.append({"ocorrencia": q["ocorrencia"], "blocos": blocos, "colunas": e.get("colunas"), "texto": texto})
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


def refazer(id_: str, pdf: Path) -> int:
    """Volta a transcrever a partir da especificação guardada no próprio ficheiro e diz se o texto
    mudou. Não escreve nada: serve para confirmar que uma transcrição conferida se reproduz."""
    dados = json.loads(_caminho(id_).read_text(encoding="utf-8"))
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != dados["pdf_sha256"]:
        print(f"{id_}: o PDF não é o da transcrição (sha256 diferente)")
        return 1
    diferentes = [t["ocorrencia"] for t in dados["transcricoes"]
                  if "\n\n".join(bloco(pdf, b, t.get("colunas")) for b in t["blocos"]) != t["texto"]]
    print(f"{id_}: " + (f"o texto muda nas imagens {diferentes}" if diferentes else "igual à transcrição guardada"))
    return 1 if diferentes else 0


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
    r = sub.add_parser("refazer")
    r.add_argument("id")
    r.add_argument("pdf", type=Path)
    m = sub.add_parser("mostrar")
    m.add_argument("id")
    a = ap.parse_args()
    if a.cmd == "quadros":
        quadros(a.id, a.espec, a.pdf)
    elif a.cmd == "refazer":
        raise SystemExit(refazer(a.id, a.pdf))
    else:
        mostrar(a.id)


if __name__ == "__main__":
    main()
