"""Repedir ao LLM os diplomas do pedido completo que falharam a verificação às cegas, com o que o
verificador apontou.

Repedir o mesmo pedido rende pouco (ronda 81: em 82 de 99 o LLM devolveu o mesmo texto). Aqui o pedido
de `llm_completo.py pedidos` leva, logo a seguir ao início de cada diploma, a lista dos reparos da
última ronda às cegas em que o diploma esteve: os artigos `errado` ou `dúvida`, com o motivo e o texto
esperado quando o verificador o escreveu, e as instruções que não se viram aplicadas. Ficam de fora os
diplomas cujos reparos falam de anexos, quadros, mapas, plantas ou imagens: esses não se resolvem com
texto.

A resposta tem o formato de sempre e passa pelo mesmo caminho: `llm_completo.py importar` (verificação
letra a letra), `juntar`, `cegas.py --escala --ronda N` e `acervo.py`. O verificador da ronda nova não
vê estes reparos.

Uso: `python consolidacao/reparos.py PASTA [--max N] [--ids FICHEIRO] [--por-ficheiro 3] [--max-chars 450000]`.

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
from texto import RAIZ

PASTA = RAIZ / "consolidacao"
_IMAGEM = re.compile(r"anexo|quadro|mapa|imagem|planta|pdf|tabela|figura|gráfico|cartograf", re.I)


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


def juntados_completo() -> set[str]:
    linhas = (PASTA / "llm" / "juntados-completo.jsonl").read_text(encoding="utf-8").splitlines()
    return {d["id"] for d in map(json.loads, linhas) if d.get("estado") == "aplicado com LLM"}


def reparos(linhas: list[dict]) -> str | None:
    """O texto dos reparos de um diploma, ou None se não há nada que o texto resolva."""
    diploma = [x for x in linhas if "instrucoes_em_falta" in x]
    artigos = [x for x in linhas if x.get("veredicto") in ("errado", "dúvida")]
    if _IMAGEM.search(json.dumps(diploma + artigos, ensure_ascii=False)):
        return None
    falta = [i for x in diploma for i in (x.get("instrucoes_em_falta") or [])]
    if not artigos and not falta:
        return None
    partes = [
        "### Reparos da verificação às cegas da resposta anterior",
        "Uma resposta anterior a este diploma foi verificada por outro modelo, que encontrou estes problemas.",
        "Lê-os, confirma cada um no texto dos diplomas que alteram (o verificador pode ter-se enganado) e",
        "devolve a resposta inteira corrigida, no formato de sempre. Não te limites aos artigos daqui: todos os",
        "artigos que mudam têm de vir na resposta.",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--max", type=int, default=0, help="só os N mais citados")
    parser.add_argument("--ids", type=Path, help="só os diplomas deste ficheiro (um id por linha)")
    parser.add_argument("--por-ficheiro", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=450_000, help="pedidos maiores ficam de fora")
    args = parser.parse_args()
    verificados = acervo.verificados()
    completos = juntados_completo()
    selecao = {d["id"]: d for d in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    textos = {}
    for id_, linhas in ultima_ronda().items():
        if id_ in verificados or id_ not in completos:
            continue
        r = reparos(linhas)
        if r:
            textos[id_] = r
    if args.ids:
        so = set(args.ids.read_text(encoding="utf-8").split())
        textos = {i: r for i, r in textos.items() if i in so}
    ids = sorted(textos, key=lambda i: -(selecao.get(i, {}).get("citacoes") or 0))
    if args.max:
        ids = ids[: args.max]
    args.pasta.mkdir(parents=True, exist_ok=True)
    (args.pasta / "ids.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
    subprocess.run(
        [sys.executable, str(PASTA / "llm_completo.py"), "pedidos", str(args.pasta / "ids.txt"), str(args.pasta), "--por-ficheiro", str(args.por_ficheiro)],
        check=True,
    )
    grandes = []
    for pedido in sorted(args.pasta.glob("pedido-*.md")):
        texto = pedido.read_text(encoding="utf-8")
        for id_ in re.findall(r"^<<<DIPLOMA id=(\S+)>>>$", texto, re.M):
            texto = texto.replace(f"<<<DIPLOMA id={id_}>>>\n", f"<<<DIPLOMA id={id_}>>>\n\n{textos[id_]}\n", 1)
        pedido.write_text(texto, encoding="utf-8")
        if len(texto) > args.max_chars:
            grandes.append(pedido.name)
    print(f"{len(ids)} diplomas com reparos de texto; pedidos acima de {args.max_chars} caracteres (a pôr de lado): {grandes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
