"""Diagnóstico da pesquisa: porque é que o artigo certo de uma pergunta não chega aos primeiros resultados.

Para cada pergunta pedida (as de um detalhe de medição com `posicao_artigo` vazio ou acima de `--acima-de`),
olha para o índice e escreve uma linha com:

- o artigo certo no índice: pedaços, vigência na data da pergunta, se tem o excerto, se sai como revogado,
  se o diploma é redirecionado para um consolidado, se tem perguntas por artigo;
- a posição do artigo certo no BM25 em todo o acervo (nos 100 candidatos e mais fundo), no BM25 só nos
  códigos principais, e dentro do próprio diploma;
- se o artigo entra no conjunto que o reranker lê (os `maximo` melhores e os dos códigos), e com que origem;
- com `--reranker`: a nota e a posição depois do reranker, e a nota que o artigo certo teria se fosse lido
  (pontuado no mesmo lote que os 10 primeiros);
- os termos da pergunta que o texto do artigo tem, e os que só as perguntas por artigo trazem;
- os 10 primeiros resultados (com o texto, para ler à mão).

A saída tem o texto das perguntas reais: vai para `rag/resultados/privado/` (fora do git).

    RAG_INDICE=... PYTHONPATH=src:. python scripts/diagnostico_pesquisa.py \
        --detalhe rag/resultados/privado/app011-final-detalhe.jsonl --indice rag/indice/indice-final.sqlite \
        --perguntas avaliacao/privado/perguntas-reais.jsonl --tipo real --acima-de 8 --reranker
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from rag import ambito as ambito_mod
from rag import texto as termos_mod
from rag.fontes import normalizar, revogado
from rag.pesquisa import Pesquisa, Resultado


class SemModelo:
    """Faz de reranker sem pontuar: a pesquisa devolve o conjunto que o reranker leria."""

    tipo = "nenhum"

    def __init__(self, maximo: int = 30):
        self.maximo = maximo

    def pontuar(self, pergunta: str, textos: list[str]) -> list[float]:
        return [0.0] * len(textos)


_NUMERO = re.compile(r"\d+ ?[-–.] ")


def janela_do_excerto(texto: str, excerto: str) -> tuple[int, str] | None:
    """Onde começa o excerto no artigo (em caracteres) e o texto a partir do número em que está.

    A janela é o corpo do número («N - …», se o excerto estiver numa alínea) seguido do parágrafo do
    excerto em diante: o que o reranker leria se o artigo fosse partido por números."""
    paragrafos = re.split(r"\n\s*\n", texto)
    k = None
    for n in range(len(paragrafos)):
        if excerto and excerto in normalizar("\n\n".join(paragrafos[n:])):
            k = n
        else:
            break
    if k is None:
        return None
    inicio = len("\n\n".join(paragrafos[:k])) + (2 if k else 0)
    corpo = k
    while corpo > 0 and not _NUMERO.match(paragrafos[corpo].lstrip()):
        corpo -= 1
    partes = ([paragrafos[corpo]] if corpo != k and _NUMERO.match(paragrafos[corpo].lstrip()) else []) + paragrafos[k:]
    return inicio, "\n\n".join(partes)


def posicao(lista: list[tuple[int, float]], ids: set[int]) -> int | None:
    return next((n for n, (i, _) in enumerate(lista, 1) if i in ids), None)


def diagnosticar(pesquisa: Pesquisa, p: dict, *, fundo: int, com_modelo: bool) -> dict:
    con = pesquisa.con
    pergunta, data, fonte = p["pergunta"], p["data_referencia"], p["fonte"]
    documento, chave = fonte["documento"], fonte["artigo"]
    doc = pesquisa.documento(documento)
    excerto = normalizar(p.get("excerto") or "")

    # --- o artigo certo no índice
    linhas = con.execute(
        "SELECT id, parte, numero, epigrafe, texto, notas, desde, ate FROM pedacos WHERE documento = ? AND chave = ? ORDER BY desde", (documento, chave)
    ).fetchall()
    em_vigor = [ln for ln in linhas if pesquisa._em_vigor(ln[6], ln[7], data)]
    ids_certos = {ln[0] for ln in em_vigor}
    perguntas_artigo = (con.execute("SELECT perguntas FROM perguntas_artigo WHERE documento = ? AND chave = ?", (documento, chave)).fetchone() or ("",))[0]
    redireciona = [alvo for tipo, alvo, _, _ in pesquisa.relacoes(documento) if tipo == "texto_em_vigor_em"]
    artigo = {
        "documento_no_indice": doc is not None,
        "legal_status": (doc or {}).get("legal_status"),
        "versao": (doc or {}).get("versao"),
        "com_historico": bool((doc or {}).get("com_historico")),
        "so_referencia": documento in pesquisa.so_referencia,
        "codigo_principal": documento in pesquisa.codigos_principais(),
        "redireciona_para": redireciona,
        "pedacos": len(linhas),
        "em_vigor_na_data": len(em_vigor),
        "tem_excerto": any(excerto and excerto in normalizar(ln[4]) for ln in em_vigor),
        "excerto_noutra_redacao": any(excerto and excerto in normalizar(ln[4]) for ln in linhas if ln[0] not in ids_certos),
        "sai_revogado": any(revogado(ln[4], ln[5] or "") for ln in em_vigor),
        "caracteres": max((len(ln[4]) for ln in em_vigor), default=0),
        "excerto_comeca_em": (janela_do_excerto(em_vigor[-1][4], excerto) or (None,))[0] if em_vigor else None,
        "tem_perguntas_artigo": bool(perguntas_artigo),
        "setor": ambito_mod.setor((doc or {}).get("titulo") or "", (doc or {}).get("sumario") or "", em_vigor[0][1] if em_vigor else ""),
        "prior": pesquisa._prior(documento, em_vigor[0][1], revogado(em_vigor[0][4], em_vigor[0][5] or ""), pergunta=pergunta) if em_vigor and doc else None,
    }

    # --- termos da pergunta e do artigo
    consulta = pesquisa._consulta_fts(pergunta) or ""
    uteis = [t.strip('"') for t in consulta.split(" OR ") if t]
    termos = {"uteis": uteis}
    if em_vigor:
        ln = em_vigor[-1]
        do_texto = set(termos_mod.termos(ln[4]))
        do_cabecalho = set(termos_mod.termos(f"{(doc or {}).get('titulo', '')} {((doc or {}).get('sumario') or '')[:300]} {ln[1]} {ln[3]}"))
        das_perguntas = set(termos_mod.termos(perguntas_artigo))
        termos.update(
            no_texto=[t for t in uteis if t in do_texto],
            no_cabecalho=[t for t in uteis if t in do_cabecalho],
            so_nas_perguntas=[t for t in uteis if t in das_perguntas and t not in do_texto and t not in do_cabecalho],
            em_falta=[t for t in uteis if t not in do_texto | do_cabecalho | das_perguntas],
        )

    # --- BM25
    bm_global = pesquisa.bm25(pergunta, data, limite=pesquisa.candidatos)
    bm_fundo = pesquisa.bm25(pergunta, data, limite=fundo)
    principais = pesquisa.codigos_principais()
    bm_codigos = pesquisa.bm25(pergunta, data, documentos=principais, limite=200)
    bm_diploma = pesquisa.bm25(pergunta, data, documentos=[documento], limite=300) if doc else []
    bm25 = {
        "global_100": posicao(bm_global, ids_certos),
        "global_fundo": posicao(bm_fundo, ids_certos),
        "codigos": posicao(bm_codigos, ids_certos),
        "no_diploma": posicao(bm_diploma, ids_certos),
        "artigos_do_diploma_no_global_100": 0,
    }
    info = pesquisa._info([i for i, _ in bm_global])
    bm25["artigos_do_diploma_no_global_100"] = sum(1 for i, _ in bm_global if info[i][2] == documento)

    # --- o que o reranker lê e a ordem final
    cons = pesquisa.pesquisar(pergunta, data, k=1000)
    lidos = cons.resultados
    pos_final = next((n for n, r in enumerate(lidos, 1) if r.documento == documento and r.chave == chave), None)
    certo = lidos[pos_final - 1] if pos_final else None
    reranker = {
        "lidos": len(lidos),
        "citados": cons.diplomas_citados,
        "codigos_citados": cons.referencias.codigos,
        "artigos_citados": cons.referencias.artigos,
        "certo_lido": pos_final is not None,
        "certo_origem": certo.origem if certo else None,
        "certo_nivel": certo.nivel if certo else None,
        "posicao_final": pos_final if com_modelo else None,
        "nota_certo": certo.reranker if certo and com_modelo else None,
        "desconto_certo": pesquisa._desconto_reranker(certo, pergunta) if certo else None,
    }
    if com_modelo and em_vigor:
        # A nota que o artigo certo teria, no mesmo lote que os 10 primeiros (a nota depende do lote).
        topo = lidos[:10]
        ln = em_vigor[-1]
        r_certo = pesquisa._pedacos([ln[0]])[ln[0]]
        # E a nota se o reranker lesse o número do artigo onde está o excerto, em vez dos primeiros caracteres.
        janela = janela_do_excerto(ln[4], excerto)
        passagens = [pesquisa._passagem(r) for r in [*topo, r_certo]] + ([f"{r_certo.rotulo}\n{janela[1]}"] if janela else [])
        notas = pesquisa.reranker.pontuar(pergunta, passagens)
        desconto = pesquisa._desconto_reranker(r_certo, pergunta)
        outras = [n - pesquisa._desconto_reranker(r, pergunta) for r, n in zip(topo, notas[:10], strict=False) if (r.documento, r.chave) != (documento, chave)]
        nota = notas[len(topo)] - desconto
        reranker.update(nota_se_lido=notas[len(topo)], desconto_se_lido=desconto, posicao_se_lido=1 + sum(n > nota for n in outras),
                        notas_topo_no_lote=notas[: len(topo)])
        if janela:
            reranker.update(nota_janela=notas[-1], posicao_janela=1 + sum(n > notas[-1] - desconto for n in outras))

    def resumo(r: Resultado) -> dict:
        return {
            "documento": r.documento, "chave": r.chave, "rotulo": r.rotulo, "origem": r.origem, "nivel": r.nivel,
            "reranker": r.reranker if com_modelo else None, "revogado": revogado(r.texto, r.notas), "ate": r.ate,
            "redirecionado_de": r.redirecionado_de, "mesmo_diploma": r.documento == documento,
            "mesmo_numero_e_epigrafe": bool(em_vigor) and r.numero == em_vigor[-1][2] and normalizar(r.epigrafe or "") == normalizar(em_vigor[-1][3] or ""),
            "tem_excerto": bool(excerto) and excerto in normalizar(r.texto), "texto": r.texto[:1500],
        }

    return {
        "id": p["id"], "tipo": p["tipo"], "pergunta": pergunta, "data": data, "resposta": p.get("resposta"), "excerto": p.get("excerto"),
        "notas_pergunta": p.get("notas"), "depende_de_outro": p.get("depende_de_outro"),
        "fonte": fonte, "artigo": artigo, "termos": termos, "bm25": bm25, "reranker": reranker,
        "texto_certo": em_vigor[-1][4][:6000] if em_vigor else None, "perguntas_artigo": perguntas_artigo,
        "topo": [resumo(r) for r in lidos[:10]],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--detalhe", type=Path, required=True, help="Detalhe (ou parcial) de uma medição de rag.avaliar.")
    parser.add_argument("--perguntas", type=Path, action="append", required=True, help="Ficheiro(s) do conjunto de avaliação com as perguntas.")
    parser.add_argument("--indice", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True, help="JSONL de saída (em rag/resultados/privado/).")
    parser.add_argument("--tipo", default="real")
    parser.add_argument("--acima-de", type=int, default=8, help="Só as perguntas com o artigo certo fora dos N primeiros.")
    parser.add_argument("--todas", action="store_true", help="Todas as perguntas do tipo, falhadas ou não.")
    parser.add_argument("--ids", help="Só estes ids, separados por vírgulas.")
    parser.add_argument("--fundo", type=int, default=3000, help="Até que posição se procura o artigo no BM25 em todo o acervo.")
    parser.add_argument("--reranker", action="store_true", help="Pontuar com o cross-encoder (lento); sem isto, só o BM25 e o conjunto lido.")
    parser.add_argument("--maximo", type=int, default=30)
    parser.add_argument("--fios", type=int, default=4)
    args = parser.parse_args(argv)

    medidas = {}
    for linha in args.detalhe.read_text(encoding="utf-8").splitlines():
        x = json.loads(linha)
        if "id" in x and x.get("tipo") == args.tipo:
            medidas[x["id"]] = x
    perguntas = {}
    for ficheiro in args.perguntas:
        for linha in ficheiro.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                x = json.loads(linha)
                perguntas[x["id"]] = x
    escolhidas = [i for i, x in medidas.items() if args.todas or x["posicao_artigo"] is None or x["posicao_artigo"] > args.acima_de]
    if args.ids:
        escolhidas = [i for i in args.ids.split(",") if i in perguntas]
    print(f"{len(escolhidas)} perguntas de {len(medidas)} do tipo {args.tipo}", file=sys.stderr)

    if args.reranker:
        from rag.modelos import Reranker

        modelo = Reranker("cruzado", maximo=args.maximo, fios=args.fios)
    else:
        modelo = SemModelo(args.maximo)
    pesquisa = Pesquisa(args.indice, reranker=modelo)
    feitas = set()
    if args.saida.exists():
        feitas = {json.loads(linha)["id"] for linha in args.saida.read_text(encoding="utf-8").splitlines() if linha.strip()}
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    inicio = time.time()
    with args.saida.open("a", encoding="utf-8") as f:
        for n, i in enumerate(escolhidas, 1):
            if i in feitas:
                continue
            linha = diagnosticar(pesquisa, perguntas[i], fundo=args.fundo, com_modelo=args.reranker)
            linha["medida"] = {k: medidas.get(i, {}).get(k) for k in ("posicao_artigo", "posicao_texto", "topo", "topo_reranker", "responde")}
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{n}/{len(escolhidas)} {i} ({time.time() - inicio:.0f} s)", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
