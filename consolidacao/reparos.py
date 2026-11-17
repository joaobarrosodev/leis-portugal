"""Repedir ao LLM os diplomas que falharam a verificação às cegas, com o que o verificador apontou.

Repedir o mesmo pedido rende pouco (ronda 81: em 82 de 99 o LLM devolveu o mesmo texto). Aqui o pedido
de `llm_completo.py pedidos` leva, logo a seguir ao início de cada diploma, a lista dos reparos da
última ronda às cegas em que o diploma esteve: os artigos `errado` ou `dúvida`, com o motivo e o texto
esperado quando o verificador o escreveu, e as instruções que não se viram aplicadas. Ficam de fora os
diplomas cujos reparos falam de anexos, quadros, mapas, plantas ou imagens: esses não se resolvem com
texto. Cada reparo é visto à parte (`de_imagem`): basta um sobre imagem para o diploma ficar de fora,
mas a palavra "anexo" ou "quadro" sozinha não chega (um "estatuto anexo" é texto).

Entram os juntados com o LLM no pedido completo, no texto corrido e na escala antiga, e os aplicados por
regra (`resultados-escala.jsonl`). O caminho do pedido novo é o texto corrido quando o diploma foi
juntado por `llm_corrido.py`, e o pedido completo nos outros casos. Os pedidos ficam em `PASTA/completo/`
e `PASTA/corrido/`, cada um com o seu `REGRAS.md`. Ficam de fora as exclusões (`llm/exclusoes.json`), os
grandes de `llm_gigantes.py` e os já repedidos com reparos (`llm/repedidos-com-reparos.txt`, a que esta
corrida junta os seus).

A resposta tem o formato de sempre e passa pelo mesmo caminho: `llm_completo.py importar` ou
`llm_corrido.py importar` (verificação letra a letra), `juntar`, `cegas.py --escala` e `acervo.py`. O
verificador da ronda nova não vê estes reparos.

Uso: `python consolidacao/reparos.py PASTA [--max N] [--ids FICHEIRO] [--por-ficheiro 3] [--max-chars 450000]
[--so-listar]`.

Com `--ids` (um id por linha), só esses diplomas: é assim que se repedem, um por pedido
(`--por-ficheiro 1`), os que ficaram em pedidos grandes demais.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

import acervo
import texto as texto_mod
from texto import RAIZ

PASTA = RAIZ / "consolidacao"
_IMAGEM = re.compile(r"imagem|documento original|\bpdf\b|planta|cartograf|\bmapas?\b|gráfico|figura|digitaliz|ligaç", re.I)
REPEDIDOS = PASTA / "llm" / "repedidos-com-reparos.txt"


def de_imagem(item) -> bool:
    """Um reparo (artigo `errado`/`dúvida` ou instrução em falta) que fala de uma imagem, um PDF,
    uma planta ou um mapa: o texto não o resolve."""
    return bool(_IMAGEM.search(item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)))


def ultima_ronda() -> dict[str, list[dict]]:
    """As linhas da saída da última ronda às cegas em que cada diploma esteve."""
    ultima: dict[str, list[dict]] = {}
    for _, saida in acervo.rondas():
        if not Path(saida).exists():
            continue
        por: dict[str, list[dict]] = collections.defaultdict(list)
        for linha in Path(saida).read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                por[d["id"]].append(d)
        ultima.update(por)
    return ultima


def _juntados(nome: str) -> set[str]:
    caminho = PASTA / "llm" / (f"juntados-{nome}.jsonl" if nome else "juntados.jsonl")
    if not caminho.exists():
        return set()
    return {d["id"] for d in map(json.loads, caminho.read_text(encoding="utf-8").splitlines()) if d.get("estado") == "aplicado com LLM"}


def juntados_completo() -> set[str]:
    return _juntados("completo")


def repedidos() -> set[str]:
    return set(REPEDIDOS.read_text(encoding="utf-8").split()) if REPEDIDOS.exists() else set()


def caminho(id_: str, corrido: set[str], outros: set[str]) -> str | None:
    """"corrido" para os juntados por `llm_corrido.py`, "completo" para os outros juntados e os
    aplicados por regra, None para os que não foram juntados."""
    if id_ in corrido:
        return "corrido"
    if id_ in outros:
        return "completo"
    return None


def reparos(linhas: list[dict]) -> str | None:
    """O texto dos reparos de um diploma, ou None se não há nada que o texto resolva."""
    diploma = [x for x in linhas if "instrucoes_em_falta" in x]
    artigos = [x for x in linhas if x.get("veredicto") in ("errado", "dúvida")]
    falta = [i for x in diploma for i in (x.get("instrucoes_em_falta") or [])]
    if not artigos and not falta:
        return None
    if any(de_imagem(a) for a in artigos) or any(de_imagem(i) for i in falta):
        return None
    partes = [
        "### Reparos da verificação às cegas da resposta anterior",
        "Uma resposta anterior a este diploma foi verificada por outro modelo, que encontrou estes problemas.",
        "Lê-os, confirma cada um no texto dos diplomas que alteram (o verificador pode ter-se enganado) e",
        "devolve a resposta inteira corrigida, no formato de sempre. Não te limites aos reparos daqui: tudo o",
        "que muda tem de vir na resposta.",
        "",
    ]
    for a in artigos:
        nome = re.sub(r"^Artigo\s+", "", str(a.get("artigo") or ""))
        partes.append(f"- Artigo {nome}: {a.get('veredicto')}. {a.get('motivo') or ''}".rstrip())
        if (a.get("texto_esperado") or "").strip():
            partes.append(f"  Texto esperado segundo o verificador: {a['texto_esperado'].strip()}")
    for i in falta:
        partes.append(f"- Instrução que não se vê aplicada: {i if isinstance(i, str) else json.dumps(i, ensure_ascii=False)}")
    return "\n".join(partes) + "\n"


def candidatos(com_repedidos: bool = False) -> dict[str, tuple[str, str]]:
    """Os diplomas a repedir: id → (caminho, texto dos reparos). Com `com_repedidos`, também os já
    repedidos (para refazer os pedidos de um bloco, um diploma por pedido)."""
    verificados = acervo.verificados()
    corrido = _juntados("corrido")
    estados = {d["id"]: d for d in map(json.loads, (PASTA / "resultados-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    regra = {i for i, d in estados.items() if d.get("estado") == "aplicado por regra"}
    outros = _juntados("completo") | _juntados("escala") | _juntados("") | regra
    fora = set(texto_mod.exclusoes()) | texto_mod.gigantes() | (set() if com_repedidos else repedidos())
    escolhidos = {}
    for id_, linhas in ultima_ronda().items():
        if id_ in verificados or id_ in fora:
            continue
        rota = caminho(id_, corrido, outros)
        r = reparos(linhas) if rota else None
        if r:
            escolhidos[id_] = (rota, r)
    return escolhidos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--max", type=int, default=0, help="só os N mais citados")
    parser.add_argument("--ids", type=Path, help="só os diplomas deste ficheiro (um id por linha)")
    parser.add_argument("--por-ficheiro", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=450_000, help="pedidos maiores ficam de fora")
    parser.add_argument("--so-listar", action="store_true", help="escreve só PASTA/ids.txt, sem pedidos")
    parser.add_argument("--com-repedidos", action="store_true", help="não salta os já repedidos (com --ids, para os refazer)")
    args = parser.parse_args()
    selecao = {d["id"]: d for d in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    textos = candidatos(args.com_repedidos)
    if args.ids:
        so = set(args.ids.read_text(encoding="utf-8").split())
        textos = {i: r for i, r in textos.items() if i in so}
    ids = sorted(textos, key=lambda i: (-(selecao.get(i, {}).get("citacoes") or 0), i))
    if args.max:
        ids = ids[: args.max]
    args.pasta.mkdir(parents=True, exist_ok=True)
    (args.pasta / "ids.txt").write_text("".join(f"{i}\t{textos[i][0]}\n" for i in ids), encoding="utf-8")
    print(f"{len(ids)} diplomas com reparos de texto: " + ", ".join(f"{n} {r}" for r, n in collections.Counter(textos[i][0] for i in ids).items()))
    if args.so_listar:
        return 0
    grandes = []
    for rota in ("completo", "corrido"):
        deste = [i for i in ids if textos[i][0] == rota]
        if not deste:
            continue
        pasta = args.pasta / rota
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "ids.txt").write_text("\n".join(deste) + "\n", encoding="utf-8")
        subprocess.run(
            [sys.executable, str(PASTA / f"llm_{rota}.py"), "pedidos", str(pasta / "ids.txt"), str(pasta), "--por-ficheiro", str(args.por_ficheiro)],
            check=True,
        )
        for pedido in sorted(pasta.glob("pedido-*.md")):
            texto = pedido.read_text(encoding="utf-8")
            for id_ in re.findall(r"^<<<DIPLOMA id=(\S+)>>>$", texto, re.M):
                texto = texto.replace(f"<<<DIPLOMA id={id_}>>>\n", f"<<<DIPLOMA id={id_}>>>\n\n{textos[id_][1]}\n", 1)
            pedido.write_text(texto, encoding="utf-8")
            if len(texto) > args.max_chars:
                grandes.append(f"{rota}/{pedido.name}")
    feitos = repedidos() | set(ids)
    REPEDIDOS.write_text("\n".join(sorted(feitos)) + "\n", encoding="utf-8")
    print(f"pedidos acima de {args.max_chars} caracteres (a pôr de lado): {grandes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
