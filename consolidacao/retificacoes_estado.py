"""O estado de cada uma das 243 retificações fora da cadeia (`auditoria/retificacoes-estado.jsonl`).

Refaz o ficheiro a partir de:

- `auditoria/retificacoes-estado.jsonl` (a linha de base: o diploma, a retificação, a classe da
  auditoria e os estados que não vêm do LLM: «sem trabalho», «fora»);
- `auditoria/retificacoes-aplicadas.jsonl` (as que estão no `data/`, por regra ou com o LLM);
- as respostas de cada ronda (`llm/retificacoes/resposta-*.jsonl`) e a verificação às cegas dessa
  ronda. Uma resposta só conta se a ronda a deu `certo`, ou se não tem trocas (nesse caso só diz o
  que não se aplica e porquê).

Cada linha fica com `estado`, `motivo`, `rondas` (as que a aplicaram) e `por_aplicar` (as
instruções que não se aplicaram, com o motivo final). No fim diz quantas ficam «por ver»: um
estado em aberto ou uma instrução com o motivo «dúvida». Fechado é zero.

Uso: `python consolidacao/retificacoes_estado.py`.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

import retificacoes_llm as rl  # noqa: E402

ESTADO = PASTA / "auditoria" / "retificacoes-estado.jsonl"
APLICADAS = PASTA / "auditoria" / "retificacoes-aplicadas.jsonl"
_RONDA = re.compile(r"^resposta-(?:(?P<ronda>[a-z]+\d*)-)?\d+\.jsonl$")


def _certas(ronda: str | None) -> set[tuple[str, str]] | None:
    sufixo = f"-{ronda}" if ronda else ""
    entrada, saida = rl.LLM / f"verificacao-entrada{sufixo}.jsonl", rl.LLM / f"verificacao-saida{sufixo}.jsonl"
    if not saida.exists():
        return None
    itens = {json.loads(l)["n"]: json.loads(l) for l in entrada.read_text(encoding="utf-8").splitlines() if l.strip()}
    certas = set()
    for linha in saida.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            v = json.loads(linha)
            if v["veredicto"] == "certo":
                certas.add((itens[v["n"]]["id"], itens[v["n"]]["retificacao_id"]))
    return certas


def respostas_validas() -> dict[tuple[str, str], tuple[str, dict]]:
    """Por par, a resposta mais recente que conta, e a ronda dela («1» na primeira)."""
    validas: dict[tuple[str, str], tuple[str, dict]] = {}
    for f in sorted(rl.LLM.glob("resposta-*.jsonl")):
        m = _RONDA.match(f.name)
        if not m:
            continue
        ronda = m.group("ronda")
        certas = _certas(ronda)
        for linha in f.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            d = json.loads(linha)
            for r in d.get("retificacoes", []):
                chave = (d["id"], r["retificacao"])
                if not r.get("trocas") or (certas is not None and chave in certas):
                    validas[chave] = (ronda or "1", r)
    return validas


def main() -> int:
    base = [json.loads(l) for l in ESTADO.read_text(encoding="utf-8").splitlines() if l.strip()]
    aplicadas: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for linha in APLICADAS.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            d = json.loads(linha)
            for r in d["retificacoes"]:
                aplicadas[(d["id"], r["retificacao"])].append(r)
    validas = respostas_validas()
    # As rondas que aplicaram trocas a cada par (a resposta certa de cada ronda com trocas).
    rondas_de: dict[tuple[str, str], list[str]] = defaultdict(list)
    for f in sorted(rl.LLM.glob("resposta-*.jsonl")):
        m = _RONDA.match(f.name)
        if not m:
            continue
        certas = _certas(m.group("ronda")) or set()
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                for r in d.get("retificacoes", []):
                    if r.get("trocas") and (d["id"], r["retificacao"]) in certas:
                        rondas_de[(d["id"], r["retificacao"])].append(m.group("ronda") or "1")
    saida, por_ver = [], []
    for x in base:
        chave = (x["id"], x["retificacao"])
        linha = {k: x[k] for k in ("id", "titulo", "retificacao", "titulo_retificacao", "classe_auditoria")}
        resposta = validas.get(chave)
        por_aplicar = [{"instrucao": n["instrucao"], "motivo": n["motivo"]} for n in (resposta[1].get("nao_aplicadas", []) if resposta else [])]
        if chave in aplicadas:
            llm = any(r.get("classe") == "llm" for r in aplicadas[chave])
            linha |= {"estado": "aplicada com o LLM" if llm else "aplicada por regra", "motivo": ""}
            if llm:
                linha["rondas"] = rondas_de.get(chave, [])
        elif resposta:
            linha |= {"estado": "nada a aplicar (LLM)", "motivo": "; ".join(f"{n['motivo']}: {n['instrucao']}" for n in por_aplicar)[:500]}
        else:
            linha |= {"estado": x["estado"], "motivo": x.get("motivo", "")}
        if por_aplicar:
            linha["por_aplicar"] = por_aplicar
        aberto = linha["estado"] not in {"aplicada com o LLM", "aplicada por regra", "nada a aplicar (LLM)", "sem trabalho"}
        duvidas = [n for n in por_aplicar if n["motivo"].lower().startswith("dúvida")]
        if aberto or duvidas:
            por_ver.append((linha["titulo"], linha["estado"], [n["instrucao"][:60] for n in duvidas]))
        saida.append(linha)
    ESTADO.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in saida), encoding="utf-8")
    print(dict(Counter(l["estado"] for l in saida).most_common()))
    motivos = Counter(n["motivo"].split(":")[0].split(" (")[0].strip().lower() for l in saida for n in l.get("por_aplicar", []))
    print("instruções por aplicar, por motivo:", dict(motivos.most_common()))
    print(f"por ver: {len(por_ver)}")
    for p in por_ver:
        print("  ", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
