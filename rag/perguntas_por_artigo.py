"""Perguntas de leigo por artigo, escritas uma vez e juntas aos termos do artigo no BM25 (piloto).

Sem chave da API não há reescrita da pergunta numa consulta jurídica (`rag.reescrita`): a pesquisa
recebe as palavras do dia a dia. Aqui, sessões do Claude escrevem para cada artigo 3 a 5 perguntas
como as faria uma pessoa sem formação jurídica (regras em `rag/perguntas_artigo/REGRAS.md`), e
`rag.indice.juntar_perguntas` junta-as aos termos do artigo em vigor. O piloto cobre o Código do
Trabalho e o arrendamento (`AMBITO`); a medição está em `rag/README.md`, «Perguntas por artigo».

    PYTHONPATH=src python -m rag.perguntas_por_artigo exportar --indice I --pasta P   # lotes para as sessões
    PYTHONPATH=src python -m rag.perguntas_por_artigo importar --pasta P              # valida e grava em rag/perguntas_artigo/
    PYTHONPATH=src python -m rag.perguntas_por_artigo juntar --indice I --saida J     # cópia de I com as perguntas
    PYTHONPATH=src python -m rag.perguntas_por_artigo comparar --antes N1 --depois N2 # por grupo, de rag.avaliar
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from rag.fontes import RAIZ, revogado


PASTA = Path(__file__).resolve().parent / "perguntas_artigo"


@dataclass(frozen=True)
class Bloco:
    nome: str  # ficheiro em PASTA (sem .jsonl)
    documento: str
    parte: str
    de: int | None = None  # intervalo dos números dos artigos, inclusive
    ate: int | None = None


AMBITO = (
    Bloco("codigo-do-trabalho", "pt:dre:602073:por", "Anexo — CÓDIGO DO TRABALHO"),
    Bloco("codigo-civil-arrendamento", "pt:dre:477358:por", "Anexo — CÓDIGO CIVIL", 1022, 1113),
    # Só o articulado do NRAU: o anexo de republicação do Código Civil é texto de 2006 (o em vigor está no DL 47344).
    Bloco("nrau", "pt:dre:693853:por", ""),
)

_NUMERO = re.compile(r"(\d+)")


def bloco_de(documento: str, chave: str) -> Bloco | None:
    """O bloco do âmbito a que pertence o artigo `chave` (`parte::número` ou `número`) do `documento`."""
    parte, _, numero = chave.rpartition("::")
    for b in AMBITO:
        if b.documento != documento or parte != b.parte:
            continue
        if b.de is not None:
            m = _NUMERO.match(numero)
            if not m or not (b.de <= int(m.group(1)) <= b.ate):
                continue
        return b
    return None


_DATA_NOTA = re.compile(r"em vigor a partir de (\d{4}-\d{2}-\d{2})|de (\d{4}-\d{2}-\d{2})\]")
_TEXTO_REVOGADO = re.compile(r"^\(?\s*revogad[oa]", re.I)


def revogado_agora(texto: str, notas: str) -> bool:
    """O artigo está revogado hoje: o texto diz "(Revogado.)" ou a nota mais recente é uma revogação.

    `rag.fontes.revogado` basta-lhe uma nota "Revogado pelo/a …", mas os artigos 1064.º a 1113.º do
    Código Civil têm a revogação de 1990 ou 2006 e, depois, "Aditado/Alterado pela Lei n.º 6/2006"
    ou por leis seguintes: estão em vigor."""
    if _TEXTO_REVOGADO.match(texto.strip()):
        return True
    datadas = []
    for nota in notas.splitlines():
        m = _DATA_NOTA.search(nota)
        if m:
            datadas.append((m.group(1) or m.group(2), bool(_TEXTO_REVOGADO.match(nota.strip()))))
    if not datadas:
        return revogado(texto, notas)
    return max(datadas)[1]


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()[:16]


def artigos_do_ambito(indice: Path) -> list[dict]:
    """Os artigos em vigor e não revogados do âmbito, pela ordem do índice."""
    saida = []
    with sqlite3.connect(f"file:{indice}?mode=ro", uri=True) as con:
        for b in AMBITO:
            titulo = con.execute("SELECT titulo FROM documentos WHERE id = ?", (b.documento,)).fetchone()
            for chave, parte, epigrafe, texto, notas in con.execute(
                "SELECT chave, parte, epigrafe, texto, notas FROM pedacos WHERE documento = ? AND parte = ? AND ate IS NULL ORDER BY id",
                (b.documento, b.parte),
            ):
                if bloco_de(b.documento, chave) is None or revogado_agora(texto, notas or ""):
                    continue
                saida.append({"documento": b.documento, "chave": chave, "titulo": titulo[0] if titulo else "", "parte": parte,
                              "epigrafe": epigrafe, "texto": texto, "sha": _sha(texto)})
    return saida


def exportar(indice: Path, pasta: Path, tamanho: int = 35) -> int:
    pasta.mkdir(parents=True, exist_ok=True)
    artigos = artigos_do_ambito(indice)
    for n in range(0, len(artigos), tamanho):
        with (pasta / f"entrada-{n // tamanho + 1:02d}.jsonl").open("w", encoding="utf-8") as f:
            for a in artigos[n : n + tamanho]:
                f.write(json.dumps(a, ensure_ascii=False) + "\n")
    return len(artigos)


# ---------------------------------------------------------------------------------------- validação

_PROIBIDO = re.compile(
    r"\d+\.º|\bartigos?\b|\bart\.|n\.º|\bal[ií]nea|c[óo]digo do trabalho|c[óo]digo civil|\bnrau\b|\blei n\.?º|decreto-lei|\bdecreto\b|\bdl\b",
    re.I,
)


def validar(linha: dict, entrada: dict | None) -> list[str]:
    """Os problemas de uma linha de saída das sessões; vazio se está boa."""
    problemas = []
    if entrada is None:
        return ["chave que não está na entrada"]
    perguntas = linha.get("perguntas")
    if not isinstance(perguntas, list) or not 3 <= len(perguntas) <= 5:
        return ["tem de ter 3 a 5 perguntas"]
    if len({p.strip().lower() for p in perguntas if isinstance(p, str)}) != len(perguntas):
        problemas.append("perguntas repetidas")
    for p in perguntas:
        if not isinstance(p, str):
            problemas.append("pergunta que não é texto")
            continue
        palavras = len(p.split())
        if not 4 <= palavras <= 40:
            problemas.append(f"{palavras} palavras: {p!r}")
        if not p.strip().endswith("?"):
            problemas.append(f"não acaba em '?': {p!r}")
        m = _PROIBIDO.search(p)
        if m:
            problemas.append(f"cita artigo ou diploma ({m.group(0)}): {p!r}")
    return problemas


def _ler_jsonl(caminho: Path) -> list[dict]:
    return [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]


def importar(pasta: Path, destino: Path = PASTA, *, modelo: str = "claude-opus-5-5", gerado: str | None = None) -> dict:
    """Valida as `saida-NN.jsonl` contra as `entrada-NN.jsonl` e grava um JSONL por bloco do âmbito."""
    gerado = gerado or date.today().isoformat()
    entradas = {(e["documento"], e["chave"]): e for f in sorted(pasta.glob("entrada-*.jsonl")) for e in _ler_jsonl(f)}
    boas: dict[tuple[str, str], dict] = {}
    recusadas: dict[str, list[str]] = {}
    for f in sorted(pasta.glob("saida-*.jsonl")):
        for n, linha in enumerate(_ler_jsonl(f), 1):
            chave = (linha.get("documento"), linha.get("chave"))
            problemas = validar(linha, entradas.get(chave))
            if problemas:
                recusadas[f"{f.name}:{n} {chave[1]}"] = problemas
                continue
            e = entradas[chave]
            boas[chave] = {"documento": e["documento"], "chave": e["chave"], "epigrafe": e["epigrafe"], "sha_texto": e["sha"],
                           "perguntas": [p.strip() for p in linha["perguntas"]], "gerado": gerado, "modelo": modelo}
    destino.mkdir(parents=True, exist_ok=True)
    ordem = {k: i for i, k in enumerate(entradas)}
    por_bloco: dict[str, list[dict]] = defaultdict(list)
    for chave in sorted(boas, key=ordem.__getitem__):
        por_bloco[bloco_de(*chave).nome].append(boas[chave])
    for b in AMBITO:
        with (destino / f"{b.nome}.jsonl").open("w", encoding="utf-8") as f:
            for linha in por_bloco.get(b.nome, []):
                f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    em_falta = [k for k in entradas if k not in boas]
    return {"artigos": len(entradas), "importados": len(boas), "perguntas": sum(len(x["perguntas"]) for x in boas.values()),
            "em_falta": em_falta, "recusadas": recusadas}


def ler(pasta: Path = PASTA) -> dict[tuple[str, str], list[str]]:
    """(documento, chave) → perguntas, de todos os JSONL da pasta."""
    return {(x["documento"], x["chave"]): x["perguntas"] for f in sorted(pasta.glob("*.jsonl")) for x in _ler_jsonl(f)}


def juntar(indice: Path, saida: Path, pasta: Path = PASTA) -> dict:
    """Uma cópia do índice com as perguntas juntas aos artigos (para medir o antes e o depois do mesmo índice)."""
    from rag.indice import juntar_perguntas

    temporario = saida.with_suffix(".tmp")
    shutil.copyfile(indice, temporario)
    con = sqlite3.connect(temporario)
    resultado = juntar_perguntas(con, ler(pasta))
    con.execute("INSERT INTO pedacos_fts (pedacos_fts) VALUES ('optimize')")
    con.commit()
    con.close()
    temporario.replace(saida)
    return resultado


# ---------------------------------------------------------------------------------------- medição

AFINADAS_ATE = 136  # real-001…136 serviram para afinar o limiar e a pesquisa (rag/README.md)


def grupo(p: dict) -> tuple[str, str]:
    """(âmbito, conjunto) de uma pergunta de avaliação: «âmbito»/«fora» e o tipo, com as reais afinadas à parte."""
    fonte = p.get("fonte") or {}
    artigos = [a["artigo"] for a in fonte.get("artigos", [])] or ([fonte["artigo"]] if fonte.get("artigo") else [])
    dentro = bool(artigos) and all(bloco_de(fonte["documento"], a) for a in artigos)
    conjunto = p["tipo"]
    if conjunto == "real":
        numero = int(re.sub(r"\D", "", p["id"].split("-")[-1]) or 0)
        conjunto = "real (afinadas)" if numero <= AFINADAS_ATE else "real (novas)"
    return ("âmbito" if dentro else "fora", conjunto)


def _detalhe(nome: str) -> dict[str, dict]:
    caminho = RAIZ / "rag" / "resultados" / "privado" / f"{nome}-detalhe.jsonl"
    return {x["id"]: x for x in _ler_jsonl(caminho)}


def comparar(antes: str, depois: str, perguntas: list[dict]) -> str:
    a, d = _detalhe(antes), _detalhe(depois)
    por_id = {p["id"]: p for p in perguntas}
    grupos: dict[tuple[str, str], list[str]] = defaultdict(list)
    for id_ in a:
        if id_ in d and id_ in por_id and por_id[id_].get("fonte"):
            grupos[grupo(por_id[id_])].append(id_)
    decisao = [i for (amb, c), ids in grupos.items() if amb == "âmbito" and c in ("coloquial", "real (novas)") for i in ids]

    def no_topo(x: dict, k: int) -> bool:
        return x["posicao_artigo"] is not None and x["posicao_artigo"] <= k

    def linha(nome: str, ids: list[str]) -> str:
        n = len(ids)
        if not n:
            return ""
        a1, d1 = sum(no_topo(a[i], 1) for i in ids), sum(no_topo(d[i], 1) for i in ids)
        a10, d10 = sum(no_topo(a[i], 10) for i in ids), sum(no_topo(d[i], 10) for i in ids)
        ganhos = sum(not no_topo(a[i], 1) and no_topo(d[i], 1) for i in ids)
        perdas = sum(no_topo(a[i], 1) and not no_topo(d[i], 1) for i in ids)
        pct = lambda x: f"{100 * x / n:.0f}%"  # noqa: E731
        return f"| {nome} | {n} | {pct(a1)} → **{pct(d1)}** ({d1 - a1:+d}) | {pct(a10)} → **{pct(d10)}** | {ganhos} / {perdas} |"

    linhas = ["| Grupo | n | Artigo certo em 1.º | Nos 10 primeiros | Ganhos / perdas no 1.º |", "|---|--:|--:|--:|--:|",
              linha("**Âmbito, nunca afinaram (decisão)**", decisao)]
    for chave in sorted(grupos, key=lambda g: (g[0] != "âmbito", g[1])):
        linhas.append(linha(f"{chave[0]}: {chave[1]}", grupos[chave]))
    fora = [i for (amb, _), ids in grupos.items() if amb == "fora" for i in ids]
    linhas.append(linha("**Fora do âmbito (todas)**", fora))
    return "\n".join(x for x in linhas if x)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)
    e = sub.add_parser("exportar")
    e.add_argument("--indice", type=Path, required=True)
    e.add_argument("--pasta", type=Path, required=True)
    e.add_argument("--lote", type=int, default=35)
    i = sub.add_parser("importar")
    i.add_argument("--pasta", type=Path, required=True)
    i.add_argument("--destino", type=Path, default=PASTA)
    j = sub.add_parser("juntar")
    j.add_argument("--indice", type=Path, required=True)
    j.add_argument("--saida", type=Path, required=True)
    c = sub.add_parser("comparar")
    c.add_argument("--antes", required=True)
    c.add_argument("--depois", required=True)
    c.add_argument("--perguntas", type=Path, action="append", help="Ficheiros de perguntas além do conjunto por omissão.")
    args = parser.parse_args(argv)
    if args.comando == "exportar":
        print(f"{exportar(args.indice, args.pasta, args.lote)} artigos em {args.pasta}")
    elif args.comando == "importar":
        r = importar(args.pasta, args.destino)
        for onde, problemas in r["recusadas"].items():
            print(f"recusada {onde}: {'; '.join(problemas)}", file=sys.stderr)
        print(f"{r['importados']}/{r['artigos']} artigos, {r['perguntas']} perguntas; em falta: {len(r['em_falta'])}")
        for documento, chave in r["em_falta"]:
            print(f"  em falta: {documento} {chave}")
    elif args.comando == "juntar":
        r = juntar(args.indice, args.saida)
        print(f"{r['artigos']} artigos, {r['pedacos']} pedaços; não encontrados no índice: {len(r['em_falta'])}")
    else:
        from rag.avaliar import ler_perguntas

        perguntas = ler_perguntas() + [p for f in args.perguntas or [] for p in ler_perguntas(ficheiro=f)]
        print(comparar(args.antes, args.depois, perguntas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
