"""Números do piloto: `consolidacao/medicao.json`, a partir de `resultados.jsonl`.

Quantos diplomas ficaram aplicados por regra, quantos ficam para o LLM, quantos não têm
alteração textual a aplicar e porquê, quantas alterações por regra, as comparações com as
republicações e a estimativa do que custa o LLM (pedidos e tokens).

**Escala (`--escala`):** `medicao-escala.json`, a partir de `resultados-escala.jsonl`: as
contagens por estado final e por triagem, por número de alterações (1, 2–3, 4–10, >10) e por
faixa de citações (≥100, 10–99, 1–9, 0), os motivos, as regras aplicadas, a triagem alterador a
alterador e os tempos (dos `logs/escala.parte-*.txt` e do campo `segundos`).

Uso: `python consolidacao/medir.py [--escala]`.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict

from llm import estimar
from texto import RAIZ

PASTA = RAIZ / "consolidacao"


def _sessao() -> dict:
    """As respostas da sessão do Claude: o `--importar` e o que o `juntar.py` juntou."""
    respostas = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((PASTA / "llm").glob("pt_*.json"))]
    juntados = PASTA / "llm" / "juntados.jsonl"
    return {
        "importar": dict(Counter("com problemas" if r["problemas"] else "não aplicável" if not r.get("artigos") else "aprovada" for r in respostas)),
        "juntar": dict(Counter(j["estado"] for j in map(json.loads, juntados.read_text(encoding="utf-8").splitlines()))) if juntados.exists() else {},
    }


def faixa_citacoes(n: int) -> str:
    return "≥100" if n >= 100 else "10–99" if n >= 10 else "1–9" if n >= 1 else "0"


def faixa_alteracoes(n: int) -> str:
    return "1" if n == 1 else "2–3" if n <= 3 else "4–10" if n <= 10 else ">10"


FAIXAS_CITACOES = ("≥100", "10–99", "1–9", "0")
FAIXAS_ALTERACOES = ("1", "2–3", "4–10", ">10")


def _tabela(resultados: list[dict], chave: str, faixa, faixas: tuple[str, ...]) -> dict:
    """Contagem de `chave` (estado ou triagem) por faixa, com os totais."""
    tabela: dict[str, Counter] = defaultdict(Counter)
    for r in resultados:
        tabela[r[chave]][faixa(r)] += 1
    ordem = sorted(tabela, key=lambda e: -sum(tabela[e].values()))
    return {e: {f: tabela[e][f] for f in faixas} | {"total": sum(tabela[e].values())} for e in ordem} | {
        "total": {f: sum(tabela[e][f] for e in tabela) for f in faixas} | {"total": len(resultados)}
    }


def _tempos() -> dict:
    """Os tempos de cada parte, da última linha "fim em N s" dos logs."""
    tempos = {}
    for log in sorted((PASTA / "logs").glob("escala.parte-*.txt")):
        texto = log.read_text(encoding="utf-8")
        fins = re.findall(r"parte (\d+/\d+): fim em (\d+) s", texto)
        inicio = re.search(r"parte (\d+/\d+): (\d+) diplomas", texto)
        tempos[log.name] = {"parte": inicio.group(1) if inicio else None, "diplomas": int(inicio.group(2)) if inicio else None,
                            "segundos_por_corrida": [int(s) for _, s in fins]}
    return tempos


def medir_escala() -> dict:
    resultados = [json.loads(l) for l in (PASTA / "resultados-escala.jsonl").read_text(encoding="utf-8").splitlines()]
    pendentes = [json.loads(l) for l in (PASTA / "pendentes-escala.jsonl").read_text(encoding="utf-8").splitlines()]
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
    for r in resultados:
        r.setdefault("n_alteracoes", selecao[r["id"]]["n_alteracoes"])

    por_citacoes = _tabela(resultados, "estado", lambda r: faixa_citacoes(r["citacoes"]), FAIXAS_CITACOES)
    por_alteracoes = _tabela(resultados, "estado", lambda r: faixa_alteracoes(r["n_alteracoes"]), FAIXAS_ALTERACOES)
    triagem_por_citacoes = _tabela(resultados, "triagem", lambda r: faixa_citacoes(r["citacoes"]), FAIXAS_CITACOES)
    triagem_por_alteracoes = _tabela(resultados, "triagem", lambda r: faixa_alteracoes(r["n_alteracoes"]), FAIXAS_ALTERACOES)

    motivos: dict[str, Counter] = defaultdict(Counter)
    for r in resultados:
        motivos[r["estado"]][r.get("motivo") or "—"] += 1
    fases = Counter(r["falhou_em"]["fase"] for r in resultados if r.get("falhou_em"))
    passos = Counter(p["triagem"] for r in resultados for p in r.get("passos", []))
    motivos_passos: dict[str, Counter] = defaultdict(Counter)
    for r in resultados:
        for p in r.get("passos", []):
            motivos_passos[p["triagem"]][re.sub(r"\s*\(.*", "", p.get("motivo") or "—")] += 1
    regras = Counter()
    for r in resultados:
        if r["estado"] == "aplicado por regra":
            regras.update(r.get("regras", {}))
    instrucoes_pendentes = Counter(item["motivo"] for d in pendentes for item in d["itens"])
    sem_aviso = [r for r in resultados if r["estado"] == "sem alteração textual"]
    segundos = [r.get("segundos", 0) for r in resultados]
    return {
        "diplomas": len(resultados),
        "por_estado_e_faixa_de_citacoes": por_citacoes,
        "por_estado_e_numero_de_alteracoes": por_alteracoes,
        "triagem_por_faixa_de_citacoes": triagem_por_citacoes,
        "triagem_por_numero_de_alteracoes": triagem_por_alteracoes,
        "motivos_por_estado": {e: dict(c.most_common(15)) for e, c in motivos.items()},
        "para_llm_por_fase_da_falha": dict(fases),
        "alteradores_por_triagem": dict(passos.most_common()),
        "motivos_por_alterador": {t: dict(c.most_common(12)) for t, c in motivos_passos.items()},
        "alteracoes_aplicadas_por_regra": dict(regras.most_common()),
        "instrucoes_pendentes_por_motivo": dict(instrucoes_pendentes.most_common(20)),
        "sem_aviso_de_texto_original": {
            "diplomas": len(sem_aviso),
            "por_faixa_de_citacoes": dict(Counter(faixa_citacoes(r["citacoes"]) for r in sem_aviso)),
            "nota": "diplomas em que nenhum alterador dá instruções ao texto: o original é o texto em vigor e dispensa o aviso \"texto original; alterado por…\"",
        },
        "republicacoes": sum(1 for r in resultados if r.get("republicacao")),
        "titulos_pelo_parser_da_fase_3": dict(Counter(r["estado"] for r in resultados if r.get("titulos_normalizados"))),
        "erros": [{"id": r["id"], "motivo": r["motivo"]} for r in resultados if r["estado"] == "erro"][:50],
        "tempos": {
            "segundos_de_cpu_somados": round(sum(segundos)),
            "segundos_por_diploma_media": round(sum(segundos) / max(len(segundos), 1), 3),
            "diploma_mais_lento": max(resultados, key=lambda r: r.get("segundos", 0))["title"] if resultados else None,
            "partes": _tempos(),
        },
        "llm": {"pedidos_feitos": 0, "estimativa_para_os_pendentes": estimar(pendentes, selecao)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--escala", action="store_true")
    args = parser.parse_args()
    if args.escala:
        medicao = medir_escala()
        (PASTA / "medicao-escala.json").write_text(json.dumps(medicao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for tabela in ("por_estado_e_faixa_de_citacoes", "por_estado_e_numero_de_alteracoes"):
            print(tabela)
            for estado, linha in medicao[tabela].items():
                print(f"  {estado:28s} " + "  ".join(f"{k}={v}" for k, v in linha.items()))
        print("sem aviso:", medicao["sem_aviso_de_texto_original"]["diplomas"], "tempos:", medicao["tempos"]["segundos_de_cpu_somados"], "s")
        return 0

    resultados = [json.loads(l) for l in (PASTA / "resultados.jsonl").read_text(encoding="utf-8").splitlines()]
    pendentes = [json.loads(l) for l in (PASTA / "pendentes.jsonl").read_text(encoding="utf-8").splitlines()]
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}

    estados: dict[str, Counter] = defaultdict(Counter)
    for r in resultados:
        estados[r["estado"]][r["motivo"] or "—"] += 1
    regras = Counter()
    for r in resultados:
        if r["estado"] == "aplicado por regra":
            regras.update(r.get("regras", {}))
    republicacoes = [
        {"title": r["title"], "estado": r["estado"], **r["republicacao"]}
        for r in resultados if r.get("republicacao")
    ]
    for rep in republicacoes:
        rep.pop("so_na_republicacao", None)
    medicao = {
        "diplomas": len(resultados),
        "por_estado": {e: {"total": sum(c.values()), "motivos": dict(c.most_common())} for e, c in
                       sorted(estados.items(), key=lambda kv: -sum(kv[1].values()))},
        "alteracoes_aplicadas_por_regra": dict(regras.most_common()),
        "comparacao_com_republicacoes": republicacoes,
        "titulos_pelo_parser_da_fase_3": dict(Counter(r["estado"] for r in resultados if r.get("titulos_normalizados"))),
        "llm": {"pedidos_feitos": 0, "tokens_usados": 0,
                "motivo": "sem ANTHROPIC_API_KEY no ambiente do piloto; os pendentes foram feitos numa sessão do Claude (llm/entrada-sessao.jsonl)",
                "estimativa_para_os_pendentes": estimar(pendentes, selecao),
                "sessao": _sessao()},
    }
    (PASTA / "medicao.json").write_text(json.dumps(medicao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for estado, dados in medicao["por_estado"].items():
        print(f"{dados['total']:4d}  {estado}")
        for motivo, n in dados["motivos"].items():
            print(f"        {n:4d}  {motivo}")
    print("Alterações por regra:", medicao["alteracoes_aplicadas_por_regra"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
