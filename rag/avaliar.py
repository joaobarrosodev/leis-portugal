"""Mede a pesquisa (e a resposta, se houver LLM) com o conjunto de avaliação.

    PYTHONPATH=src python -m rag.avaliar --nome bm25
    PYTHONPATH=src python -m rag.avaliar --nome cruzado --reranker cruzado --limiar 0

Por tipo de pergunta:

- `artigo@k`: o artigo certo (`fonte.documento` e `fonte.artigo`) está nos k primeiros;
- `texto@k`: e o pedaço tem o excerto, isto é, é a redação em vigor na `data_referencia`
  (nas temporais é a "versão certa");
- revogadas: se o primeiro resultado avisa da revogação e nomeia o diploma revogatório certo;
- sem resposta: a taxa de "não sei";
- "não sei", respondidas, certas e fiabilidade (certas / respondidas). Sem LLM, uma resposta
  é certa quando o primeiro artigo é o certo e tem o excerto (nas revogadas: é do diploma
  certo e avisa da revogação por X); com LLM, quando cita o artigo certo e a resposta tem
  o mesmo sentido que a certa (`verifica.mesmo_sentido`).

O resumo (só números) vai para `rag/resultados/<nome>.json`; o detalhe por pergunta, com o
texto das perguntas reais, para `rag/resultados/privado/` (fora do git).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

from rag.fontes import RAIZ, normalizar
from rag.pesquisa import Consulta, Pesquisa
from rag.resposta import Resposta, llm_disponivel, responder


TIPOS = ("literal", "temporal", "revogada", "sem_resposta", "real")
KS = (1, 5, 10)
RESULTADOS = RAIZ / "rag" / "resultados"


def perguntas_reais() -> Path | None:
    for pasta in (RAIZ, *RAIZ.parents):
        caminho = pasta / "avaliacao" / "privado" / "perguntas-reais.jsonl"
        if caminho.exists():
            return caminho
    return None


def ler_perguntas(incluir_reais: bool = True) -> list[dict]:
    ficheiros = [RAIZ / "avaliacao" / "perguntas.jsonl"]
    reais = perguntas_reais()
    if incluir_reais and reais:
        ficheiros.append(reais)
    return [json.loads(linha) for f in ficheiros for linha in f.read_text(encoding="utf-8").splitlines() if linha.strip()]


def _mesmo_sentido():
    sys.path.insert(0, str(RAIZ / "avaliacao"))
    from verifica import mesmo_sentido  # noqa: PLC0415

    return mesmo_sentido


def avaliar_pergunta(pesquisa: Pesquisa, p: dict, *, limiar: float | None, usar_llm: bool) -> dict:
    consulta = pesquisa.pesquisar(p["pergunta"], p["data_referencia"], k=max(KS))
    resposta = responder(consulta, limiar=limiar, usar_llm=usar_llm)
    fonte = p.get("fonte")
    pos_artigo = pos_texto = None
    if fonte:
        excerto = normalizar(p.get("excerto") or "")
        for n, r in enumerate(consulta.resultados, 1):
            if r.documento == fonte["documento"] and r.chave == fonte["artigo"]:
                pos_artigo = pos_artigo or n
                if excerto in normalizar(r.texto):
                    pos_texto = pos_texto or n
    topo = consulta.resultados[0] if consulta.resultados else None
    avisa_revogacao = bool(topo and topo.revogado_por) or bool(topo and any("revogad" in a.lower() for a in topo.avisos))
    revogado_por_certo = bool(topo and p.get("revogado_por") and p["revogado_por"]["documento"] in topo.revogado_por)

    # O primeiro resultado está certo (artigo e redação; nas revogadas, diploma e aviso), responda ou não.
    if p["tipo"] == "sem_resposta":
        acerta_topo = False
    elif p["tipo"] == "revogada":
        acerta_topo = bool(topo and topo.documento == fonte["documento"] and revogado_por_certo)
    else:
        acerta_topo = pos_texto == 1

    if p["tipo"] == "sem_resposta":
        certa = not resposta.responde
    elif not resposta.responde:
        certa = False
    elif resposta.com_llm:
        citado = any(r.documento == fonte["documento"] and (r.chave == fonte["artigo"] or p["tipo"] == "revogada") for r in resposta.citacoes)
        if p["tipo"] == "revogada":
            certa = citado and "revogad" in resposta.texto.lower() and p["revogado_por"]["titulo"].split("n.º")[-1].strip() in resposta.texto
        else:
            certa = citado and _mesmo_sentido()(p["resposta"], resposta.texto)
    else:
        certa = acerta_topo

    return {
        "id": p["id"],
        "tipo": p["tipo"],
        "pergunta": p["pergunta"],
        "data": p["data_referencia"],
        "fonte": f"{fonte['titulo']} › {fonte['artigo']}" if fonte else None,
        "posicao_artigo": pos_artigo,
        "posicao_texto": pos_texto,
        "topo": topo.rotulo if topo else None,
        "topo_origem": topo.origem if topo else None,
        "topo_reranker": topo.reranker if topo else None,
        "avisos": topo.avisos if topo else [],
        "avisa_revogacao": avisa_revogacao,
        "revogado_por_certo": revogado_por_certo,
        "referencias": {"diplomas": [d[2] for d in consulta.referencias.diplomas], "codigos": consulta.referencias.codigos,
                        "artigos": consulta.referencias.artigos, "em_falta": consulta.diplomas_em_falta},
        "responde": resposta.responde,
        "motivo": resposta.motivo,
        "resposta": resposta.texto[:500] if resposta.com_llm else None,
        "certa": certa,
        "acerta_topo": acerta_topo,
    }


def resumir(linhas: list[dict]) -> dict[str, dict]:
    grupos: dict[str, list[dict]] = defaultdict(list)
    for linha in linhas:
        grupos[linha["tipo"]].append(linha)
    grupos["total"] = linhas
    resumo = {}
    for tipo, xs in grupos.items():
        n = len(xs)
        com_fonte = [x for x in xs if x["tipo"] != "sem_resposta"]
        respondidas = [x for x in xs if x["responde"]]
        r = {"n": n, "nao_sei": sum(not x["responde"] for x in xs), "respondidas": len(respondidas),
             "certas": sum(x["certa"] for x in respondidas) if tipo != "sem_resposta" else 0}
        if tipo == "sem_resposta":
            r["certas_nao_sei"] = sum(x["certa"] for x in xs)
        for k in KS:
            r[f"artigo@{k}"] = sum(x["posicao_artigo"] is not None and x["posicao_artigo"] <= k for x in com_fonte)
            r[f"texto@{k}"] = sum(x["posicao_texto"] is not None and x["posicao_texto"] <= k for x in com_fonte)
        r["com_fonte"] = len(com_fonte)
        rev = [x for x in xs if x["tipo"] == "revogada"]
        if rev:
            r["avisa_revogacao@1"] = sum(x["avisa_revogacao"] for x in rev)
            r["revogado_por_certo@1"] = sum(x["revogado_por_certo"] for x in rev)
        resumo[tipo] = r
    return resumo


def curva(linhas: list[dict], limiares: list[float]) -> str:
    """"Não sei" e fiabilidade sem LLM se se recusar quando o reranker dá ao melhor artigo menos do que o limiar."""
    texto = ["| Limiar | \"não sei\" nas que têm resposta | \"não sei\" nas sem resposta | fiabilidade (certas/respondidas) |",
             "|--:|--:|--:|--:|"]
    com = [x for x in linhas if x["tipo"] != "sem_resposta"]
    sem = [x for x in linhas if x["tipo"] == "sem_resposta"]
    def responde(x: dict, limiar: float) -> bool:
        return x["responde"] and (x["topo_reranker"] is None or x["topo_reranker"] >= limiar)

    for limiar in limiares:
        respondidas = [x for x in linhas if responde(x, limiar)]
        certas = sum(x["acerta_topo"] for x in respondidas)
        texto.append(f"| {limiar:g} | {100 * sum(not responde(x, limiar) for x in com) / len(com):.0f}% | "
                     f"{100 * sum(not responde(x, limiar) for x in sem) / max(len(sem), 1):.0f}% | "
                     f"{100 * certas / max(len(respondidas), 1):.0f}% ({certas}/{len(respondidas)}) |")
    return "\n".join(texto)


def tabela(resumo: dict[str, dict]) -> str:
    def pct(a: int, b: int) -> str:
        return f"{100 * a / b:.0f}%" if b else "—"

    linhas = ["| Tipo | n | artigo@1 | artigo@5 | artigo@10 | texto@1 | texto@10 | \"não sei\" | fiabilidade (certas/respondidas) |",
              "|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for tipo in (*TIPOS, "total"):
        r = resumo.get(tipo)
        if not r:
            continue
        cf = r["com_fonte"]
        artigos = [pct(r[f"artigo@{k}"], cf) for k in KS] + [pct(r["texto@1"], cf), pct(r["texto@10"], cf)]
        certas = r["certas"] if tipo != "total" else r["certas"]
        linhas.append(f"| {tipo} | {r['n']} | {' | '.join(artigos)} | {pct(r['nao_sei'], r['n'])} | "
                      f"{pct(certas, r['respondidas'])} ({certas}/{r['respondidas']}) |")
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--nome", default="bm25")
    parser.add_argument("--indice", type=Path)
    parser.add_argument("--reranker", choices=("cruzado", "denso"), help="Reordena os candidatos com um modelo multilingue (extra `rag`).")
    parser.add_argument("--limiar", type=float, help="'Não sei' quando o reranker dá ao melhor artigo menos do que isto.")
    parser.add_argument("--sem-llm", action="store_true", help="Não usar o LLM mesmo que haja chave.")
    parser.add_argument("--sem-reais", action="store_true")
    parser.add_argument("--limite", type=int)
    args = parser.parse_args(argv)

    reranker = None
    if args.reranker:
        from rag.modelos import Reranker

        reranker = Reranker(args.reranker)
    pesquisa = Pesquisa(args.indice, reranker=reranker)
    usar_llm = llm_disponivel() and not args.sem_llm
    perguntas = ler_perguntas(not args.sem_reais)[: args.limite]
    print(f"{len(perguntas)} perguntas; LLM: {'sim' if usar_llm else 'não'}", file=sys.stderr)

    linhas = []
    inicio = time.time()
    for n, p in enumerate(perguntas, 1):
        linhas.append(avaliar_pergunta(pesquisa, p, limiar=args.limiar, usar_llm=usar_llm))
        if n % 50 == 0:
            print(f"{n}/{len(perguntas)} ({time.time() - inicio:.0f} s)", file=sys.stderr, flush=True)

    configuracao = {"reranker": args.reranker, "limiar": args.limiar, "llm": usar_llm}
    resumo = guardar(args.nome, configuracao, linhas)
    print(tabela(resumo))
    for tipo in ("revogada",):
        r = resumo.get(tipo)
        if r:
            print(f"\nRevogadas: avisa da revogação no 1.º resultado {r['avisa_revogacao@1']}/{r['n']}, "
                  f"com o diploma revogatório certo {r['revogado_por_certo@1']}/{r['n']}")
    if reranker is not None and reranker.tipo == "cruzado" and not usar_llm:
        print("\n" + curva(linhas, [-6, -4, -2, -1, 0, 1, 2, 3, 4]))
    print(f"\n{time.time() - inicio:.0f} s", file=sys.stderr)
    return 0


def guardar(nome: str, configuracao: dict, linhas: list[dict]) -> dict[str, dict]:
    """Escreve o resumo em `rag/resultados/<nome>.json` e o detalhe em `rag/resultados/privado/<nome>-detalhe.jsonl`."""
    resumo = resumir(linhas)
    (RESULTADOS / "privado").mkdir(parents=True, exist_ok=True)
    (RESULTADOS / f"{nome}.json").write_text(
        json.dumps({"configuracao": configuracao, "resumo": resumo}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    with (RESULTADOS / "privado" / f"{nome}-detalhe.jsonl").open("w", encoding="utf-8") as f:
        for linha in linhas:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    return resumo


if __name__ == "__main__":
    raise SystemExit(main())
