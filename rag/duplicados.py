"""Registos repetidos do mesmo diploma, e qual é o principal.

O DRE tem alguns diplomas em dois registos com o mesmo título e a mesma data. O caso que importa é a Lei n.º 28/82
(a do Tribunal Constitucional): um registo consolidado e outro com o texto de origem, os dois no índice como texto
atual. Outros pares têm o mesmo texto com estados diferentes (um «unknown», outro «not_in_force»). E há pares que não
são o mesmo diploma: o DRE deu o mesmo número a dois diplomas do mesmo dia (o DL 129/86, a Lei n.º 27/81).

**A prova.** Dois registos são o mesmo diploma quando têm o mesmo tipo, título e data e o texto o confirma: o mesmo
sumário (ou um sumário que começa pelo outro) ou o mesmo início do texto e, se os dois têm artigos, quase os mesmos
números de artigo. Só se comparam títulos com número («Portaria n.º 10/2008»), não os «Resolução do Conselho de
Ministros» sem número. Se um diz que está em
vigor e o outro que foi revogado, fica de fora: não se sabe qual dos dois estados é o certo.

**O principal** é o consolidado, depois o de estado conhecido, depois o que tem mais alterações registadas e mais
artigos. O `rag.indice` grava, para cada repetido:

- a relação `mesmo_diploma_em` para o principal (a pesquisa nova troca o repetido pelo principal quando a pergunta o
  cita: `rag.pesquisa.Pesquisa._principal`);
- a relação `texto_em_vigor_em`, só se o principal é um consolidado em vigor ou de vigência desconhecida: a aplicação
  0.1.1 já a conhece e troca o artigo do repetido pelo mesmo artigo do principal (a numeração é a mesma: é o mesmo
  diploma);
- o repetido na tabela `so_referencia`: deixa de entrar no BM25 em todo o acervo (a 0.1.1 também a lê).

Nada se apaga: o texto do repetido continua no índice.

Uso: `python -m rag.duplicados` lista os pares e os de fora.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from rag.fontes import RAIZ, corpo, export_sqlite, ler_artigos
from rag.texto import sem_acentos


TIPOS = (
    "lei", "lei-organica", "lei-constitucional", "decreto-lei", "decreto-regulamentar", "decreto-legislativo-regional",
    "decreto-regulamentar-regional", "portaria", "resolucao-conselho-ministros",
)
VIGENTES = ("in_force", "partially_in_force")
REVOGADOS = ("repealed", "not_in_force")
INICIO = 3000  # caracteres do texto que se comparam
TEXTO_PARECIDO = 0.9
NUMEROS_EM_COMUM = 0.8
MESMO_DIPLOMA = "mesmo_diploma_em"
TEXTO_EM_VIGOR = "texto_em_vigor_em"
_LIGACAO = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _simples(texto: str) -> str:
    texto = sem_acentos(_LIGACAO.sub(r"\1", texto).lower())
    return re.sub(r"\W+", " ", texto).strip()


def _ler(raiz: Path, caminho: str | None) -> tuple[str, set[str]]:
    """(início do texto, números dos artigos) do registo."""
    ficheiro = raiz / (caminho or "")
    if not caminho or not ficheiro.exists():
        return "", set()
    texto = corpo(ficheiro.read_text(encoding="utf-8"))
    return _simples(texto)[:INICIO], {a.numero for a in ler_artigos(texto) if a.numero}


def mesmo_diploma(a: dict, b: dict) -> str | None:
    """Porque é que `a` e `b` (com `inicio` e `numeros`) são o mesmo diploma, ou None."""
    # A Lei n.º 28/82 foi publicada outra vez com a referenda: «… Tribunal Constitucional. - Repete a publicação…».
    sa, sb = sorted((_simples(a["summary"] or ""), _simples(b["summary"] or "")), key=len)
    sumario = bool(sa) and sb.startswith(sa)
    texto = bool(a["inicio"]) and SequenceMatcher(None, a["inicio"], b["inicio"], autojunk=False).ratio() >= TEXTO_PARECIDO
    if not (sumario or texto):
        return None
    if a["numeros"] and b["numeros"]:
        comuns = len(a["numeros"] & b["numeros"]) / min(len(a["numeros"]), len(b["numeros"]))
        if comuns < NUMEROS_EM_COMUM:
            return None
    return "o mesmo sumário" if sumario else "o mesmo início do texto"


def _ordem(d: dict) -> tuple:
    return (d["version_kind"] == "consolidated", d["legal_status"] in VIGENTES, d["legal_status"] != "unknown", d["alteracoes"], len(d["numeros"]), d["id"])


def calcular(export: Path, raiz: Path = RAIZ) -> tuple[list[dict], list[dict]]:
    """(pares, de fora). Cada par: `repetido`, `principal`, `motivo`, `texto_em_vigor` (se leva essa relação)."""
    con = sqlite3.connect(f"file:{export}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    marcas = ",".join("?" * len(TIPOS))
    grupos: dict[tuple, list[dict]] = defaultdict(list)
    for linha in con.execute(
        f"""SELECT id, title, summary, document_type, publication_date, legal_status, version_kind, path FROM documentos
            WHERE id LIKE 'pt:%' AND text_quality = 'texto' AND publication_date IS NOT NULL AND document_type IN ({marcas})""",
        TIPOS,
    ):
        if "n.º" in (linha["title"] or ""):
            grupos[(linha["document_type"], linha["title"], linha["publication_date"])].append(dict(linha))
    grupos = {k: g for k, g in grupos.items() if len(g) > 1}
    ids = [d["id"] for g in grupos.values() for d in g]
    alteracoes: dict[str, int] = defaultdict(int)
    for n in range(0, len(ids), 900):
        lote = ids[n : n + 900]
        for origem, total in con.execute(
            f"SELECT source_id, count(*) FROM relacoes WHERE type = 'amended_by' AND source_id IN ({','.join('?' * len(lote))}) GROUP BY 1", lote
        ):
            alteracoes[origem] = total
    con.close()
    pares, fora = [], []
    for (_, titulo, data), registos in sorted(grupos.items()):
        for d in registos:
            d["inicio"], d["numeros"] = _ler(raiz, d["path"])
            d["alteracoes"] = alteracoes.get(d["id"], 0)
        principal = max(registos, key=_ordem)
        for d in sorted(registos, key=lambda x: x["id"]):
            if d is principal:
                continue
            base = {"titulo": titulo, "data": data, "repetido": d["id"], "principal": principal["id"],
                    "estados": [d["legal_status"], principal["legal_status"]], "versoes": [d["version_kind"], principal["version_kind"]]}
            motivo = mesmo_diploma(d, principal)
            if motivo is None:
                fora.append(base | {"motivo": "outro diploma com o mesmo título e a mesma data (o sumário e o texto diferem)"})
            elif {d["legal_status"], principal["legal_status"]} & set(VIGENTES) and {d["legal_status"], principal["legal_status"]} & set(REVOGADOS):
                fora.append(base | {"motivo": "o mesmo diploma, mas um registo diz que vigora e o outro que não: não se sabe qual é o certo"})
            else:
                em_vigor = principal["version_kind"] == "consolidated" and principal["legal_status"] in (*VIGENTES, "unknown")
                pares.append(base | {"motivo": motivo, "texto_em_vigor": em_vigor})
    return pares, fora


def relacoes(pares: list[dict], titulos: dict[str, str]) -> list[tuple[str, str, str, str, None]]:
    """As linhas da tabela `relacoes` do índice para os pares."""
    linhas = []
    for par in pares:
        alvo = par["principal"]
        linhas.append((par["repetido"], MESMO_DIPLOMA, alvo, titulos.get(alvo, alvo), None))
        if par["texto_em_vigor"]:
            linhas.append((par["repetido"], TEXTO_EM_VIGOR, alvo, titulos.get(alvo, alvo), None))
    return linhas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--export", type=Path)
    args = parser.parse_args(argv)
    pares, fora = calcular(args.export or export_sqlite())
    for par in pares:
        print(json.dumps(par, ensure_ascii=False))
    for d in fora:
        print(json.dumps(d | {"fora": True}, ensure_ascii=False))
    print(f"{len(pares)} repetidos com principal ({sum(p['texto_em_vigor'] for p in pares)} com texto_em_vigor_em); {len(fora)} de fora")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
