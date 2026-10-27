"""Entrada da verificação às cegas do piloto: `consolidacao/verificacao/entrada-piloto.jsonl`.

Uma linha por diploma consolidado (estado "aplicado por regra" em `resultados.jsonl` ou
"aplicado com LLM" em `llm/juntados.jsonl`, sem dizer qual), com o
texto original, o texto do diploma que altera e o texto consolidado, e nada sobre como foi
feito: sem os registos de alterações, sem as regras e sem as notas "> Alterado pelo/a …" que o
piloto acrescenta aos artigos (quem verifica tem de encontrar sozinho o que mudou).

Quando o diploma que altera passa de 60 mil caracteres (orçamentos, diplomas com muitos
anexos), vão só os artigos dele que mencionam o original, com `alterador_completo: false`.
Quando os títulos dos artigos do original foram normalizados (artigos em texto corrido, ver
`texto.com_titulos`), a linha diz `titulos_normalizados: true` e traz também o original com os
títulos, `texto_original_com_titulos`. As regras da verificação estão em `consolidacao/README.md`.

Rondas: `--ronda 1` escreve `entrada-piloto.jsonl` com todos os aplicados por regra; `--ronda N`
escreve `entrada-piloto-N.jsonl` só com os que não estão nas rondas anteriores ou cujo
consolidado mudou desde a última em que estiveram (as rondas anteriores já foram verificadas e
não se reescrevem).

**Escala (`--escala`):** lê `resultados-escala.jsonl` e `selecao-escala.jsonl` e escreve a ronda
em lotes de `--lote` diplomas, `entrada-piloto-N-lote-01.jsonl`, `-02`, … Um diploma com
vários alteradores leva `alteradores`, uma lista com o título e o texto de cada um (por ordem
de aplicação, só os que deram instruções), e `alterador` e `texto_alterador` são a junção dos títulos e dos
textos (cada texto começa pelo título `# <diploma>` do registo).

Uso: `python consolidacao/cegas.py [--ronda N] [--escala] [--lote 30]`.
"""

from __future__ import annotations

import argparse
import json
import re

from texto import RAIZ, artigos_alteradores, com_titulos, corpo, publicado

PASTA = RAIZ / "consolidacao"
VERIFICACAO = PASTA / "verificacao"


def entrada(ronda: int):
    return VERIFICACAO / ("entrada-piloto.jsonl" if ronda == 1 else f"entrada-piloto-{ronda}.jsonl")


def entradas_da_ronda(ronda: int) -> list:
    """Os ficheiros de uma ronda: o único do piloto ou os lotes da escala."""
    unico = entrada(ronda)
    lotes = sorted(VERIFICACAO.glob(f"entrada-piloto-{ronda}-lote-*.jsonl"))
    return ([unico] if unico.exists() else []) + lotes


def ultima_ronda() -> int:
    numeros = [1] if entrada(1).exists() else []
    for f in VERIFICACAO.glob("entrada-piloto-*.jsonl"):
        m = re.match(r"entrada-piloto-(\d+)", f.name)
        if m:
            numeros.append(int(m.group(1)))
    return max(numeros, default=0)


LIMITE = 60_000
_NOTA_PILOTO = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*, publicado em \d{4}-\d{2}-\d{2}\.\n\n?", re.M)


def _texto_alterador(path: str, titulo_original: str) -> tuple[str, bool]:
    texto = publicado(RAIZ / path)
    if len(texto) <= LIMITE:
        return texto, True
    return "\n\n".join("\n".join(a.linhas).strip() for a in artigos_alteradores(texto, titulo_original)), False


def linha_de(r: dict, registo: dict) -> dict:
    """A linha da entrada para um diploma aplicado por regra."""
    consolidado = _NOTA_PILOTO.sub("", corpo((RAIZ / r["consolidado"]).read_text(encoding="utf-8")))
    original = publicado(RAIZ / registo["path"])
    if "alteradores" in registo:
        aplicados = {p["id"] for p in r.get("passos", []) if p.get("aplicadas")}
        alteradores = [a for a in registo["alteradores"] if a["id"] in aplicados]
    else:
        alteradores = [registo["alterador"]]
    textos = []
    for a in alteradores:
        texto, completo = _texto_alterador(a["path"], registo["title"])
        textos.append({"titulo": a["title"], "texto": texto, "completo": completo})
    if len(textos) == 1:
        linha = {"alterador": textos[0]["titulo"], "alterador_completo": textos[0]["completo"], "texto_alterador": textos[0]["texto"]}
    else:
        linha = {
            "alterador": " e ".join(t["titulo"] for t in textos),
            "alterador_completo": all(t["completo"] for t in textos),
            "texto_alterador": "\n\n".join(
                t["texto"] if t["texto"].lstrip().startswith("# ") else f"# {t['titulo']}\n\n{t['texto']}" for t in textos
            ),
            "alteradores": textos,
        }
    linha = {"id": r["id"], "titulo": registo["title"]} | linha | {"texto_original": original, "texto_consolidado": consolidado}
    if r.get("titulos_normalizados"):
        linha |= {"titulos_normalizados": True, "texto_original_com_titulos": com_titulos(original)}
    return linha


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ronda", type=int, default=0, help="por omissão, a seguir à última em verificacao/")
    parser.add_argument("--escala", action="store_true")
    parser.add_argument("--lote", type=int, default=30, help="escala: diplomas por ficheiro")
    args = parser.parse_args()
    ronda = args.ronda or (ultima_ronda() + 1 if args.escala else 1)
    anteriores = {}
    for anterior in range(1, ronda):
        for ficheiro in entradas_da_ronda(anterior):
            anteriores |= {d["id"]: d["texto_consolidado"] for d in map(json.loads, ficheiro.read_text(encoding="utf-8").splitlines())}
    selecao_ficheiro = PASTA / ("selecao-escala.jsonl" if args.escala else "selecao.jsonl")
    selecao = {r["id"]: r for r in map(json.loads, selecao_ficheiro.read_text(encoding="utf-8").splitlines())}
    resultados_ficheiro = PASTA / ("resultados-escala.jsonl" if args.escala else "resultados.jsonl")
    resultados = [json.loads(l) for l in resultados_ficheiro.read_text(encoding="utf-8").splitlines()]
    juntados = PASTA / "llm" / "juntados.jsonl"
    if juntados.exists() and not args.escala:
        resultados += [j for j in map(json.loads, juntados.read_text(encoding="utf-8").splitlines()) if j["estado"] == "aplicado com LLM"]
    VERIFICACAO.mkdir(exist_ok=True)
    linhas = []
    for r in resultados:
        if r["estado"] not in ("aplicado por regra", "aplicado com LLM"):
            continue
        linha = linha_de(r, selecao[r["id"]])
        if anteriores.get(r["id"]) == linha["texto_consolidado"]:
            continue
        linhas.append(linha)
    if not args.escala:
        saida = entrada(ronda)
        with saida.open("w", encoding="utf-8") as f:
            for linha in linhas:
                f.write(json.dumps(linha, ensure_ascii=False) + "\n")
        print(f"{len(linhas)} diplomas em {saida.relative_to(RAIZ)}")
        return 0
    lotes = [linhas[i : i + args.lote] for i in range(0, len(linhas), args.lote)]
    for n, lote in enumerate(lotes, 1):
        saida = VERIFICACAO / f"entrada-piloto-{ronda}-lote-{n:02d}.jsonl"
        with saida.open("w", encoding="utf-8") as f:
            for linha in lote:
                f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    print(f"ronda {ronda}: {len(linhas)} diplomas em {len(lotes)} lotes de até {args.lote} ({VERIFICACAO.relative_to(RAIZ)}/entrada-piloto-{ronda}-lote-NN.jsonl)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
