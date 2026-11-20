"""Diagnóstico: o que o reranker daria ao artigo certo se lesse outra passagem dele.

Parte da saída de `scripts/diagnostico_pesquisa.py --reranker`. Para cada pergunta, pontua no mesmo lote
os 10 primeiros resultados (tal como estão e com o sumário do diploma) e o artigo certo em várias formas:

- `base`: o que o reranker lê hoje (rótulo e os primeiros caracteres do artigo);
- `assunto`: com o sumário do diploma a seguir ao rótulo;
- `janela`: a partir do número do artigo onde está o excerto (em vez do início do artigo);
- `perguntas`: com as perguntas por artigo, quando o artigo as tem (a variante `reranker_com_perguntas`);
- as combinações `janela_assunto` e `janela_perguntas`.

A posição de cada forma é a que teria entre os 10 primeiros. É o melhor caso: só o artigo certo muda de
forma (nas variantes com o assunto, os 10 primeiros também o levam), e a janela usa o excerto do conjunto
de avaliação para saber que número ler. Diz também quantos artigos do diploma certo o reranker leu.

    RAG_INDICE=... PYTHONPATH=src:. python scripts/diagnostico_variantes.py ENTRADA.jsonl SAIDA.jsonl INDICE.sqlite

A saída tem ids e notas, sem o texto das perguntas; mesmo assim fica em `rag/resultados/privado/`.
"""
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnostico_pesquisa import SemModelo, janela_do_excerto
from rag.fontes import normalizar
from rag.modelos import Reranker
from rag.pesquisa import Pesquisa


ent, sai, indice = sys.argv[1], sys.argv[2], sys.argv[3]
modelo = Reranker("cruzado", maximo=30, fios=3)
ps = Pesquisa(Path(indice), reranker=SemModelo(30))
con = ps.con
feitas = set()
if Path(sai).exists(): feitas = {json.loads(l)["id"] for l in open(sai)}
out = open(sai, "a")
def peca(doc, chave, data):
    ls = con.execute("SELECT id, desde, ate FROM pedacos WHERE documento=? AND chave=?", (doc, chave)).fetchall()
    ls = [l for l in ls if ps._em_vigor(l[1], l[2], data)]
    return ps._pedacos([ls[-1][0]])[ls[-1][0]] if ls else None
def assunto(r):
    d = ps.documento(r.documento) or {}
    return (d.get("sumario") or "")[:250]
def com_assunto(r, texto=None):
    s = assunto(r)
    return f"{r.rotulo}\nAssunto do diploma: {s}\n{texto if texto is not None else r.texto}" if s else f"{r.rotulo}\n{texto if texto is not None else r.texto}"
for l in open(ent):
    x = json.loads(l)
    if x["id"] in feitas: continue
    perg, data = x["pergunta"], x["data"]; doc, chave = x["fonte"]["documento"], x["fonte"]["artigo"]
    topo = [peca(t["documento"], t["chave"], data) for t in x["topo"]]
    topo = [r for r in topo if r is not None and (r.documento, r.chave) != (doc, chave)]
    certo = peca(doc, chave, data)
    jan = janela_do_excerto(certo.texto, normalizar(x["excerto"] or ""))
    pa = x["perguntas_artigo"]
    variantes = {"base": f"{certo.rotulo}\n{certo.texto}", "assunto": com_assunto(certo)}
    if jan: variantes["janela"] = f"{certo.rotulo}\n{jan[1]}"; variantes["janela_assunto"] = com_assunto(certo, jan[1])
    if pa:
        variantes["perguntas"] = f"{certo.rotulo}\nPerguntas: {' '.join(pa.splitlines())}\n{certo.texto}"
        if jan: variantes["janela_perguntas"] = f"{certo.rotulo}\nPerguntas: {' '.join(pa.splitlines())}\n{jan[1]}"
    passagens = [f"{r.rotulo}\n{r.texto}" for r in topo] + [com_assunto(r) for r in topo] + list(variantes.values())
    notas = modelo.pontuar(perg, passagens)
    n = len(topo); desc = [ps._desconto_reranker(r, perg) for r in topo]
    base = [a - d for a, d in zip(notas[:n], desc, strict=False)]; cass = [a - d for a, d in zip(notas[n:2*n], desc, strict=False)]
    res = {"id": x["id"], "topo_base": notas[:n], "topo_assunto": notas[n:2*n]}
    for k, v in zip(variantes, notas[2*n:], strict=False):
        contra = cass if "assunto" in k else base
        res[k] = {"nota": v, "posicao": 1 + sum(c > v for c in contra)}
    # expansão por diploma: o diploma certo está entre os que o reranker lê? e nos 10 primeiros?
    lidos = ps.pesquisar(perg, data, k=1000).resultados
    res["diploma_lido"] = sum(r.documento == doc for r in lidos)
    res["diploma_no_topo10"] = sum(t["mesmo_diploma"] for t in x["topo"])
    res["diplomas_lidos"] = len({r.documento for r in lidos})
    out.write(json.dumps(res, ensure_ascii=False) + "\n"); out.flush()
    print(x["id"], {k: (round(v["nota"], 1), v["posicao"]) for k, v in res.items() if isinstance(v, dict)}, "dip lido:", res["diploma_lido"], flush=True)
