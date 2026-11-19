"""Segunda leitura de vigência com o LLM, para os consolidados que as regras não marcaram.

São os de certeza `alta` nas classes `caca`, `organicas` e `um_so_ano` da auditoria
(`auditoria/vigencia.jsonl`) sem marca em `auditoria/vigencia-revista.jsonl`. Os cursos anteriores
a Bolonha têm a marca `regime_anterior` por regra, e os 140 incertos ficam de fora até se ver o
rendimento.

1. `entrada`: um item por diploma em `llm/vigencia/entrada-NN.jsonl`, com:
   - o título, o sumário, a data e as relações do registo (sem as citações);
   - o início e o fim do texto em vigor;
   - as menções no acervo (outro registo que cite o diploma, ou o mesmo número de processo
     numa concessão de caça) perto de um verbo de vigência (revogar, extinguir, caducar,
     substituir, renovar, prorrogar), com o título e a data do registo onde estão.
2. O leitor (Sonnet, `llm/vigencia/PROMPT-leitor.md`) responde `nao_vigora`, `vigora` ou `duvida`,
   e em `nao_vigora` dá o motivo e a prova (o id de uma menção da entrada ou uma relação). As
   dúvidas vão a uma segunda leitura (Opus, o mesmo prompt) em `llm/vigencia/duvidas-NN.jsonl`.
3. `juntar`: só conta `nao_vigora` com uma prova que esteja na entrada. Grava
   `llm/vigencia/marcas-verificadas.jsonl`, que `vigencia.py` junta às marcas.

Uso: `python consolidacao/vigencia_llm.py entrada --numeros nums-hits.txt --processos procs-hits.txt`
e `python consolidacao/vigencia_llm.py duvidas|juntar`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

from texto import RAIZ, corpo, front_matter, padrao_diploma, sem_ligacoes  # noqa: E402


LLM = PASTA / "llm" / "vigencia"
AUDITORIA = PASTA / "auditoria"
CLASSES = ("caca", "organicas", "um_so_ano")
POR_LOTE = 40
MAX_MENCOES = 8
_VERBO = re.compile(r"revog|extin|caduc|substitu|cess[ao]|termo|renov|prorrog|deixa de vigorar|transita|sucede", re.I)
_PROC = re.compile(r"processo n\.?\s*º?\s*([\d.]+)", re.I)


def candidatos() -> list[dict]:
    marcados = {json.loads(l)["id"] for l in (AUDITORIA / "vigencia-revista.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    vig = [json.loads(l) for l in (AUDITORIA / "vigencia.jsonl").read_text(encoding="utf-8").splitlines()]
    return [v for v in vig if v["certeza"] == "alta" and v["classe"] in CLASSES and v["id"] not in marcados]


def _linhas_rg(ficheiro: Path) -> dict[str, list[str]]:
    """ficheiro → linhas (sem o «ficheiro:n:») de uma saída do rg."""
    por = defaultdict(list)
    for linha in ficheiro.read_text(encoding="utf-8", errors="replace").splitlines():
        f, _, resto = linha.partition(":")
        _, _, texto = resto.partition(":")
        por[f].append(texto)
    return por


_NUMERO = re.compile(r"(?<![\d/])(\d+(?:-[A-Z]+\d*)?)/(\d{2,4})(?![\d])")


def por_numero(linhas_rg: dict[str, list[str]]) -> dict[str, list[tuple[str, str]]]:
    """«158/96» → [(ficheiro, linha sem ligações)], com o ano em dois algarismos («1996» → «96»)."""
    indice: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for f, linhas in linhas_rg.items():
        for texto in linhas:
            plano = sem_ligacoes(texto)
            for chave_n in {f"{m.group(1)}/{m.group(2)[-2:]}" for m in _NUMERO.finditer(plano)}:
                indice[chave_n].append((f, plano))
    return indice


def _chave_numero(titulo: str) -> str | None:
    m = re.search(r"n\.?\s*[º°o]\s*(\d+(?:-[A-Z]+\d*)?)/(\d{2,4})\b", titulo or "")
    return f"{m.group(1)}/{m.group(2)[-2:]}" if m else None


_META: dict[str, dict] = {}


def _meta(caminho: str) -> dict:
    if caminho not in _META:
        _META[caminho] = front_matter((RAIZ / caminho).read_text(encoding="utf-8"))
    return _META[caminho]


def mencoes(v: dict, linhas_numeros: dict[str, list[tuple[str, str]]], ficheiros_processo: set[str]) -> list[dict]:
    """As menções do diploma noutros registos, perto de um verbo de vigência, as mais recentes primeiro."""
    padrao = padrao_diploma(v["titulo"])
    achados = []
    chave_n = _chave_numero(v["titulo"])
    if padrao is not None and chave_n:
        for f, plano in linhas_numeros.get(chave_n, []):
            if f == v["caminho"]:
                continue
            for m in padrao.finditer(plano):
                trecho = plano[max(0, m.start() - 250) : m.end() + 200]
                if _VERBO.search(trecho):
                    achados.append((f, trecho))
                    break
    for f in ficheiros_processo:
        if f != v["caminho"]:
            meta = _meta(f)
            achados.append((f, f"(mesmo número de processo) {meta.get('summary') or ''}"[:450]))
    resultado, vistos = [], set()
    for f, trecho in achados:
        if f in vistos:
            continue
        vistos.add(f)
        meta = _meta(f)
        resultado.append({"id": meta.get("id"), "titulo": meta.get("title"), "data": str(meta.get("publication_date") or ""), "trecho": trecho.strip()})
    resultado.sort(key=lambda m: m["data"], reverse=True)
    return resultado[:MAX_MENCOES]


def entrada(numeros: Path, processos: Path) -> None:
    linhas_numeros = por_numero(_linhas_rg(numeros))
    por_processo: dict[str, set[str]] = defaultdict(set)
    for f, linhas in _linhas_rg(processos).items():
        for texto in linhas:
            m = _PROC.search(texto)
            if m:
                por_processo[m.group(1).rstrip(".")].add(f)
    itens = []
    for v in candidatos():
        texto = (RAIZ / v["caminho"]).read_text(encoding="utf-8")
        meta = front_matter(texto)
        corpo_ = sem_ligacoes(corpo(texto)).strip()
        ficheiros_processo: set[str] = set()
        if v["classe"] == "caca":
            for p in {m.group(1).rstrip(".") for m in _PROC.finditer(texto)}:
                ficheiros_processo |= por_processo.get(p, set())
        relacoes = [{"tipo": r["type"], "alvo": r["target"], "rotulo": (r.get("label") or "").replace("\x00", "")[:250]} for r in meta.get("relationships") or [] if r["type"] != "cites"]
        itens.append({
            "id": v["id"], "titulo": v["titulo"], "sumario": v["sumario"], "tipo": v["tipo"], "classe": v["classe"],
            "publicacao": v["publicacao"], "texto_consolidado_ate": v.get("consolidacao"), "legal_status": v["legal_status"],
            "prazo_anos": v.get("prazo_anos"), "fim_estimado": v.get("fim_estimado"), "renovavel": v.get("renovavel"),
            "relacoes": relacoes[:25],
            "inicio_do_texto": corpo_[:1800], "fim_do_texto": corpo_[-700:] if len(corpo_) > 2500 else "",
            "mencoes_no_acervo": mencoes(v, linhas_numeros, ficheiros_processo),
        })
    LLM.mkdir(parents=True, exist_ok=True)
    for f in LLM.glob("entrada-*.jsonl"):
        f.unlink()
    for n in range(0, len(itens), POR_LOTE):
        (LLM / f"entrada-{n // POR_LOTE + 1:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens[n : n + POR_LOTE]), encoding="utf-8")
    print(f"{len(itens)} diplomas em {-(-len(itens) // POR_LOTE)} lotes; com menções: {sum(1 for x in itens if x['mencoes_no_acervo'])}")


def _respostas(padrao: str) -> dict[str, dict]:
    resultado = {}
    for f in sorted(LLM.glob(padrao)):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                resultado[d["id"]] = d
    return resultado


def _entradas() -> dict[str, dict]:
    return _respostas("entrada-*.jsonl")


def duvidas() -> None:
    entradas, leituras = _entradas(), _respostas("resposta-*.jsonl")
    lista = [entradas[i] for i, r in leituras.items() if r["veredicto"] == "duvida"]
    for f in LLM.glob("duvidas-entrada-*.jsonl"):
        f.unlink()
    for n in range(0, len(lista), POR_LOTE):
        (LLM / f"duvidas-entrada-{n // POR_LOTE + 1:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lista[n : n + POR_LOTE]), encoding="utf-8")
    print(f"{len(lista)} dúvidas para a segunda leitura (Opus)")


def prova_valida(r: dict, e: dict) -> bool:
    """A prova cita uma menção ou uma relação da entrada (o id) e há motivo."""
    ids = {m["id"] for m in e["mencoes_no_acervo"]} | {x["alvo"] for x in e["relacoes"]}
    return bool(r.get("motivo")) and bool(r.get("prova")) and r["prova"] in ids


def juntar() -> None:
    entradas = _entradas()
    leituras = _respostas("resposta-*.jsonl")
    leituras.update({i: r | {"segunda": True} for i, r in _respostas("duvidas-resposta-*.jsonl").items()})
    marcas, contas = [], defaultdict(int)
    for i, r in leituras.items():
        e = entradas.get(i)
        if not e:
            continue
        contas[r["veredicto"] + (" (Opus)" if r.get("segunda") else "")] += 1
        if r["veredicto"] != "nao_vigora":
            continue
        if not prova_valida(r, e):
            contas["nao_vigora sem prova na entrada (não conta)"] += 1
            continue
        prova = next((m for m in e["mencoes_no_acervo"] if m["id"] == r["prova"]), None) or next(x for x in e["relacoes"] if x["alvo"] == r["prova"])
        marcas.append({
            "id": i, "titulo": e["titulo"], "marca": "nao_vigora", "classe": f"llm_{e['classe']}",
            "motivo": r["motivo"].strip().rstrip(".") + ".", "prova": [{"tipo": "menção no acervo" if "trecho" in prova else "relação", **prova}],
            "fonte": "segunda leitura de vigência (Opus)" if r.get("segunda") else "segunda leitura de vigência (Sonnet)",
        })
    (LLM / "marcas-verificadas.jsonl").write_text("".join(json.dumps(m, ensure_ascii=False) + "\n" for m in marcas), encoding="utf-8")
    print(dict(contas), "| marcas:", len(marcas))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("passo", choices=["entrada", "duvidas", "juntar"])
    parser.add_argument("--numeros", type=Path)
    parser.add_argument("--processos", type=Path)
    args = parser.parse_args(argv)
    if args.passo == "entrada":
        entrada(args.numeros, args.processos)
    elif args.passo == "duvidas":
        duvidas()
    else:
        juntar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
