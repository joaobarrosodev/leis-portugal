"""Revogações parciais registadas só como `repealed_by` nos consolidados do leis-portugal (20/11/2026).

A seleção da escala (`selecionar.py --todos`) só pôs na cadeia de alteradores as relações
`amended_by` (e, mais tarde, `corrected_by`). Uma revogação que o DRE regista só como `repealed_by`
(«Revogados os arts. 41.º a 43.º pelo DL 46380…») nunca entrou: nos 2.785 consolidados nossos no
`data/` ficaram 398 por aplicar, em 259 diplomas, e o índice servia esses artigos como em vigor.
As revogações do diploma inteiro (10) são vigência e ficam de fora daqui.

Três passos, como `anexos_alteradores.py`:

1. `entrada`: um item por consolidado, com o texto em vigor em linhas numeradas (Markdown cru), as
   revogações por aplicar (o rótulo do DRE, a data e o texto do diploma que revoga) por ordem de data
   (`llm/revogacoes/entrada-NN.jsonl`).
2. O respondedor (Opus, `llm/revogacoes/PROMPT-respondedor.md`) dá, por revogação, as trocas que põem
   «(Revogado.)» onde ela manda, a data de efeitos quando a revogação a tem, e o que não se aplica,
   com o motivo; `verificacao` junta-as para o verificador às cegas (Sonnet,
   `llm/revogacoes/PROMPT-verificador.md`).
3. `aplicar`: só as `certo`, na pasta principal. O diploma que revoga entra nos `acts` da versão
   consolidada, com a nota «> Revogado pelo/a …, publicado em …» (e «, com efeitos a partir de …»
   quando a revogação a tem, que `rag.fontes.revogado` lê), e a data da versão passa a ser a mais
   recente entre a de hoje e a dos efeitos. Os registos ficam em `auditoria/revogacoes-aplicadas.jsonl`,
   que `acervo.py` também guarda.

Uso: `python consolidacao/revogacoes.py entrada|verificacao|aplicar|estado [--dry-run]`.
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
sys.path.insert(0, str(PASTA.parent / "src"))

import retificacoes as rt  # noqa: E402
import retificacoes_llm as rl  # noqa: E402
from acervo import blocos, em_vigor, historico  # noqa: E402
from texto import RAIZ, artigos_alteradores, corpo, front_matter, sem_ligacoes  # noqa: E402

from leis_portugal.domain.history import render_version, summarize  # noqa: E402
from leis_portugal.infrastructure.repository import Acervo  # noqa: E402

LLM = PASTA / "llm" / "revogacoes"
APLICADOS = PASTA / "auditoria" / "revogacoes-aplicadas.jsonl"
LOTE_BYTES = 140_000
POR_LOTE = 8
MAX_ALTERADOR = 30_000
# Uma revogação do diploma inteiro («Revogado o presente diploma…», «Revogado, a partir de…» sem artigos):
# é vigência (`vigencia.py`), não texto.
TOTAL = re.compile(r"^\s*Revogad[oa]\s*(?:,|\s+(?:o|a)\s+(?:presente|diploma))", re.I)
EXCECAO = re.compile(r"excep|exceç|salvo|art|n\.?\s*º|al[íi]nea|cap[íi]tulo|sec[cç]", re.I)


def _total(rotulo: str) -> bool:
    return bool(TOTAL.search(rotulo)) and not EXCECAO.search(rotulo.split(" pel")[0])


def candidatos() -> dict[str, dict]:
    """Por consolidado nosso no `data/`: as relações `repealed_by` do export cujo diploma não está nos
    `acts` das versões, sem as revogações do diploma inteiro."""
    import html  # noqa: PLC0415
    import sqlite3  # noqa: PLC0415

    from auditoria import consolidados  # noqa: PLC0415
    from selecionar import export_por_omissao  # noqa: PLC0415

    db = sqlite3.connect(f"file:{export_por_omissao()}?mode=ro", uri=True)
    por_doc: dict[str, dict] = {}
    for caminho, meta, *_ in consolidados():
        acts = set()
        versoes = caminho.with_name(caminho.name[:-3] + ".versoes.json")
        if versoes.exists():
            for v in json.loads(versoes.read_text(encoding="utf-8")).get("versions", []):
                acts |= {a.get("id") if isinstance(a, dict) else a for a in v.get("acts") or []}
        for tid, alvo, rotulo, data in db.execute(
            "select target_id, target, label, date from relacoes where source_id = ? and type = 'repealed_by'", (meta["id"],)
        ):
            rotulo = html.unescape((rotulo or "").replace("\x00", "")).strip()
            if (tid and tid in acts) or _total(rotulo):
                continue
            doc = db.execute("select id, title, path, text_quality, publication_date from documentos where id = ?", (tid,)).fetchone() if tid else None
            a = ({"id": doc[0], "title": doc[1], "path": doc[2] if doc[3] == "texto" else None, "text_quality": doc[3], "publication_date": doc[4]}
                 if doc else {"id": tid or alvo, "title": alvo, "path": None, "text_quality": None, "publication_date": None})
            a |= {"rotulos_dre": [rotulo], "data_dre": data, "ordem": a.get("publication_date") or data or ""}
            item = por_doc.setdefault(meta["id"], {"selecao": {"title": meta["title"]}, "caminho": str(caminho.relative_to(RAIZ)), "alteradores": {}})
            if a["id"] in item["alteradores"]:
                item["alteradores"][a["id"]]["rotulos_dre"].append(rotulo)
            else:
                item["alteradores"][a["id"]] = a
    return por_doc


def entrada() -> None:
    itens = []
    for id_, c in sorted(candidatos().items()):
        caminho = RAIZ / c["caminho"]
        texto = caminho.read_text(encoding="utf-8")
        meta = front_matter(texto)
        linhas = corpo(texto).split("\n")
        alteradores = []
        for a in sorted(c["alteradores"].values(), key=lambda a: (a.get("ordem") or "", a["id"])):
            ta = corpo((RAIZ / a["path"]).read_text(encoding="utf-8")).strip() if a.get("path") else "(o acervo não tem o texto deste diploma: só o rótulo do DRE)"
            if len(ta) > MAX_ALTERADOR:
                # grande: os artigos que mencionam o consolidado, que é onde está a revogação
                arts = artigos_alteradores(ta, meta.get("title") or "")
                ta = "\n\n".join("\n".join(x.linhas).strip() for x in arts) or ta
            alteradores.append({"id": a["id"], "titulo": a["title"], "publicacao": a.get("publication_date"),
                                "rotulos_dre": a.get("rotulos_dre") or [], "data_dre": a.get("data_dre"),
                                "texto": ta[:MAX_ALTERADOR], "texto_cortado": len(ta) > MAX_ALTERADOR})
        outros = []
        mostradas = rl.linhas_relevantes(linhas, [sem_ligacoes(x["texto"]) for x in alteradores] + [" ".join(x["rotulos_dre"]) for x in alteradores])
        # o fim do texto (onde costumam estar os anexos) vai sempre
        fim = [i for i in range(max(0, len(linhas) - 120), len(linhas)) if linhas[i].strip()]
        mostradas = sorted(set(mostradas) | set(fim))
        itens.append({
            "id": id_, "titulo": meta.get("title"), "caminho": c["caminho"],
            "texto_parcial": len(mostradas) < sum(1 for l in linhas if l.strip()),
            "texto_em_vigor": "\n".join(f"L{i}: {linhas[i]}" for i in mostradas),
            "alteradores_candidatos": alteradores, "outros_alteradores": outros,
        })
    LLM.mkdir(parents=True, exist_ok=True)
    for f in LLM.glob("entrada-*.jsonl"):
        f.unlink()
    lotes: list[list[dict]] = [[]]
    for x in itens:
        tamanho = len(json.dumps(x, ensure_ascii=False))
        if lotes[-1] and (sum(len(json.dumps(y, ensure_ascii=False)) for y in lotes[-1]) + tamanho > LOTE_BYTES or len(lotes[-1]) >= POR_LOTE):
            lotes.append([])
        lotes[-1].append(x)
    for n, lote in enumerate(lotes, 1):
        (LLM / f"entrada-{n:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lote), encoding="utf-8")
    print(f"{len(itens)} consolidados, {sum(len(x['alteradores_candidatos']) for x in itens)} alteradores, {len(lotes)} lotes")


MAX_ALTERADOR_R3 = 100_000
MAX_EM_VIGOR_R3 = 150_000


def entrada_r3() -> None:
    """Ronda r3: os pares que ainda não estão aplicados nem confirmados às cegas como «não se aplica», com o
    motivo do último verificador como reparo. O diploma que revoga vai até 100 000 caracteres (os artigos que
    mencionam o consolidado, quando é maior), e o texto em vigor vai inteiro até 150 000."""
    vered = _veredictos()
    itens = []
    for id_, c in sorted(candidatos().items()):
        pendentes = [alt for alt in _ordem(c) if vered.get((id_, alt), {}).get("veredicto") != "certo"]
        if not pendentes:
            continue
        caminho = RAIZ / c["caminho"]
        texto = caminho.read_text(encoding="utf-8")
        meta = front_matter(texto)
        linhas = corpo(texto).split("\n")
        alteradores = []
        for alt in pendentes:
            a = c["alteradores"][alt]
            ta = corpo((RAIZ / a["path"]).read_text(encoding="utf-8")).strip() if a.get("path") else "(o acervo não tem o texto deste diploma: só o rótulo do DRE)"
            if len(ta) > MAX_ALTERADOR_R3:
                arts = artigos_alteradores(ta, meta.get("title") or "")
                ta = "\n\n".join("\n".join(x.linhas).strip() for x in arts) or ta
            v = vered.get((id_, alt))
            alteradores.append({"id": a["id"], "titulo": a["title"], "publicacao": a.get("publication_date"),
                                "rotulos_dre": a.get("rotulos_dre") or [], "data_dre": a.get("data_dre"),
                                "texto": ta[:MAX_ALTERADOR_R3], "texto_cortado": len(ta) > MAX_ALTERADOR_R3,
                                "reparo": (f"Uma verificação às cegas da resposta anterior deu «{v['veredicto']}»: {v.get('motivo', '')}" if v
                                           else "Não houve resposta anterior para este par.")})
        completo = "\n".join(f"L{i}: {l}" for i, l in enumerate(linhas) if l.strip())
        if len(completo) <= MAX_EM_VIGOR_R3:
            em_vigor_txt, parcial = completo, False
        else:
            mostradas = rl.linhas_relevantes(linhas, [sem_ligacoes(x["texto"]) for x in alteradores] + [" ".join(x["rotulos_dre"]) for x in alteradores])
            fim = [i for i in range(max(0, len(linhas) - 120), len(linhas)) if linhas[i].strip()]
            em_vigor_txt, parcial = "\n".join(f"L{i}: {linhas[i]}" for i in sorted(set(mostradas) | set(fim))), True
        itens.append({"id": id_, "titulo": meta.get("title"), "caminho": c["caminho"], "texto_parcial": parcial,
                      "texto_em_vigor": em_vigor_txt, "alteradores_candidatos": alteradores, "outros_alteradores": []})
    for f in LLM.glob("entrada-r3-*.jsonl"):
        f.unlink()
    lotes: list[list[dict]] = [[]]
    for x in itens:
        tamanho = len(json.dumps(x, ensure_ascii=False))
        if lotes[-1] and (sum(len(json.dumps(y, ensure_ascii=False)) for y in lotes[-1]) + tamanho > 250_000 or len(lotes[-1]) >= 4):
            lotes.append([])
        lotes[-1].append(x)
    for n, lote in enumerate(lotes, 1):
        (LLM / f"entrada-r3-{n:02d}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lote), encoding="utf-8")
    print(f"r3: {len(itens)} consolidados, {sum(len(x['alteradores_candidatos']) for x in itens)} pares, {len(lotes)} lotes")


def _vistos() -> dict[str, dict]:
    """O que o respondedor leu, por consolidado: a entrada da ronda mais recente que o trouxe."""
    vistos = {}
    for f in sorted(LLM.glob("entrada-*.jsonl"), key=lambda f: (f.stem.count("-r"), f.name)):
        for l in f.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                vistos.setdefault(d["id"], {}).update({"texto_em_vigor": d["texto_em_vigor"], "texto_parcial": d.get("texto_parcial")})
                for a in d["alteradores_candidatos"]:
                    vistos[d["id"]][a["id"]] = a
    return vistos


def respostas() -> dict[tuple[str, str], dict]:
    """(consolidado, alterador) → resposta, de todos os `resposta-NN.jsonl`."""
    resultado = {}
    for f in sorted(LLM.glob("resposta-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                for r in d.get("alteradores", []):
                    resultado[(d["id"], r["alterador"])] = r
    return resultado


def encadear(linhas: list[str], trocas: list[dict]) -> list[dict]:
    """Os respondedores escrevem as trocas sobre o texto de hoje. Quando dois alteradores mexem na
    mesma linha (um troca a imagem, outro insere a seguir; ou dois inserem), o segundo encontra a
    linha já mudada pelo primeiro: nesse caso, e só numa inserção (o texto novo começa pelo atual
    e uma linha em branco), o que ele insere acrescenta-se ao fim do que lá está, pela ordem dos
    alteradores."""
    resultado = []
    for t in trocas:
        i, atual, novo = int(t["linha"]), t["texto_atual"], t["texto_novo"]
        hoje = linhas[i] if 0 <= i < len(linhas) else None
        # a linha só difere do que o respondedor viu se um alterador anterior da mesma cadeia já a
        # mudou (outra inserção, ou a troca da imagem); numa inserção, acrescenta-se ao que lá está
        if hoje is not None and hoje != atual and novo.startswith(atual + "\n\n"):
            t = t | {"texto_atual": hoje, "texto_novo": hoje + novo[len(atual):]}
        resultado.append(t)
    return resultado


def _ordem(c: dict) -> list[str]:
    return [a["id"] for a in sorted(c["alteradores"].values(), key=lambda a: (a.get("ordem") or "", a["id"]))]


def _da_ronda(ronda: str) -> set[tuple[str, str]]:
    pares = set()
    for f in sorted(LLM.glob(f"resposta-{ronda}-*.jsonl")):
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                pares |= {(d["id"], r["alterador"]) for r in d.get("alteradores", [])}
    return pares


def _certos(sufixo: str = "") -> set[tuple[str, str]]:
    entrada_v = LLM / f"verificacao-entrada{sufixo}.jsonl"
    saida = LLM / f"verificacao-saida{sufixo}.jsonl"
    if not saida.exists():
        return set()
    itens = {json.loads(l)["n"]: json.loads(l) for l in entrada_v.read_text(encoding="utf-8").splitlines() if l.strip()}
    certos = set()
    for linha in saida.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            v = json.loads(linha)
            if v["veredicto"] == "certo":
                certos.add((itens[v["n"]]["id"], itens[v["n"]]["alterador_id"]))
    return certos


def verificacao(ronda: str | None = None) -> None:
    """Uma entrada por (consolidado, alterador) com trocas, encadeadas pela ordem de data. Numa
    ronda seguinte (`--ronda r2`), só os pares respondidos nessa ronda; os outros do mesmo
    consolidado que já passaram encadeiam-se antes, como no `aplicar`."""
    resp, cands, itens = respostas(), candidatos(), []
    da_ronda = _da_ronda(ronda) if ronda else None
    ja_certos = _certos() if ronda else set()
    for id_, c in sorted(cands.items()):
        linhas = corpo((RAIZ / c["caminho"]).read_text(encoding="utf-8")).split("\n")
        for alt in _ordem(c):
            r = resp.get((id_, alt))
            if not r:
                continue
            if not r.get("trocas"):
                if da_ronda is not None and (id_, alt) not in da_ronda:
                    continue
                # sem trocas: o verificador confirma o motivo do que não se aplica (outro diploma, condicional…)
                a = c["alteradores"][alt]
                itens.append({
                    "n": len(itens) + 1, "diploma": c["selecao"]["title"], "id": id_, "alterador_id": alt,
                    "alterador": f"{a['title']} ({a.get('publication_date')})", "rotulos_dre": a.get("rotulos_dre"),
                    "texto_do_alterador": corpo((RAIZ / a["path"]).read_text(encoding="utf-8"))[:40000] if a.get("path") else "(sem texto no acervo)",
                    "efeitos": r.get("efeitos"), "alteracoes_feitas": [], "nao_aplicadas": r.get("nao_aplicadas", []),
                })
                continue
            if da_ronda is not None and (id_, alt) not in da_ronda:
                if (id_, alt) in ja_certos:
                    try:
                        copia = list(linhas)
                        rl.trocar(copia, encadear(linhas, r["trocas"]))
                        linhas = copia
                    except rl.Recusa:
                        pass
                continue
            copia = list(linhas)
            try:
                feitas = rl.trocar(copia, encadear(linhas, r["trocas"]))
            except rl.Recusa as erro:
                print(f"   {id_} {alt}: {erro}")
                continue
            a = c["alteradores"][alt]
            itens.append({
                "n": len(itens) + 1, "diploma": c["selecao"]["title"], "id": id_, "alterador_id": alt,
                "alterador": f"{a['title']} ({a.get('publication_date')})", "rotulos_dre": a.get("rotulos_dre"),
                "texto_do_alterador": corpo((RAIZ / a["path"]).read_text(encoding="utf-8"))[:40000] if a.get("path") else "(sem texto no acervo)",
                "efeitos": r.get("efeitos"),
                "alteracoes_feitas": [{"paragrafo_antes": f["antes"], "paragrafo_depois": f["depois"] or "(parágrafo apagado)",
                                       "contexto": rl.contexto(linhas, f["linha"])} | ({"nota_do_respondedor": f["nota"]} if f.get("nota") else {}) for f in feitas],
                "nao_aplicadas": r.get("nao_aplicadas", []),
            })
            linhas = copia
    if ronda:
        # o verificador lê o que o respondedor leu (como na 2.ª passagem), e não os primeiros 40 000 caracteres
        vistos = _vistos()
        for x in itens:
            v = vistos.get(x["id"], {})
            a = v.get(x["alterador_id"])
            if a is not None:
                x["texto_do_alterador"] = a["texto"]
                x["texto_do_alterador_cortado"] = bool(a.get("texto_cortado"))
            ja = any("já aplicad" in str(n.get("motivo", "")).lower() for n in x.get("nao_aplicadas") or [])
            if not x["alteracoes_feitas"] or ja:
                x["texto_em_vigor"] = v.get("texto_em_vigor", "")
                x["texto_em_vigor_parcial"] = bool(v.get("texto_parcial"))
    (LLM / (f"verificacao-entrada-{ronda}.jsonl" if ronda else "verificacao-entrada.jsonl")).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")
    print(f"{len(itens)} pares com trocas para a verificação às cegas")


def juntar_saidas() -> None:
    """As saídas dos lotes da 1.ª passagem (`verif/verificacao-saida-KK.jsonl`) num só
    `verificacao-saida.jsonl`, pelo `n` da entrada."""
    linhas = {}
    for f in sorted((LLM / "verif").glob("verificacao-saida-*.jsonl")):
        for l in f.read_text(encoding="utf-8").splitlines():
            if l.strip():
                v = json.loads(l)
                linhas[v["n"]] = v
    (LLM / "verificacao-saida.jsonl").write_text("".join(json.dumps(linhas[n], ensure_ascii=False) + "\n" for n in sorted(linhas)), encoding="utf-8")
    print(f"{len(linhas)} veredictos em verificacao-saida.jsonl")


MAX_EM_VIGOR = 60_000


def verificacao_v2() -> None:
    """2.ª passagem (`r2v`): os pares que a 1.ª não deu `certo` ou não viu, com o texto do diploma
    que revoga tal como o respondedor o leu (os artigos que mencionam o consolidado, quando é
    grande) em vez dos primeiros 40 000 caracteres, e, quando nada se aplicou ou o motivo é «já
    aplicada», as linhas do texto em vigor que o respondedor viu."""
    certos = _certos()
    vistos = {}
    for f in sorted(LLM.glob("entrada-*.jsonl")):
        for l in f.read_text(encoding="utf-8").splitlines():
            if l.strip():
                d = json.loads(l)
                vistos[d["id"]] = d
    itens = []
    for l in (LLM / "verificacao-entrada.jsonl").read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        x = json.loads(l)
        if (x["id"], x["alterador_id"]) in certos:
            continue
        d = vistos.get(x["id"], {})
        a = next((a for a in d.get("alteradores_candidatos", []) if a["id"] == x["alterador_id"]), None)
        if a is not None:
            x["texto_do_alterador"] = a["texto"]
            x["texto_do_alterador_cortado"] = bool(a.get("texto_cortado"))
        ja = any("já aplicad" in str(n.get("motivo", "")).lower() for n in x.get("nao_aplicadas") or [])
        if not x["alteracoes_feitas"] or ja:
            x["texto_em_vigor"] = d.get("texto_em_vigor", "")[:MAX_EM_VIGOR]
            x["texto_em_vigor_parcial"] = bool(d.get("texto_parcial")) or len(d.get("texto_em_vigor", "")) > MAX_EM_VIGOR
        x["n_1a_passagem"] = x["n"]
        x["n"] = len(itens) + 1
        itens.append(x)
    (LLM / "verificacao-entrada-r2v.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in itens), encoding="utf-8")
    pasta = LLM / "verif-r2v"
    pasta.mkdir(exist_ok=True)
    lotes, atual, tam = [], [], 0
    for x in itens:
        s = json.dumps(x, ensure_ascii=False) + "\n"
        if atual and tam + len(s) > 300_000:
            lotes.append(atual)
            atual, tam = [], 0
        atual.append(s)
        tam += len(s)
    if atual:
        lotes.append(atual)
    for k, lo in enumerate(lotes, 1):
        (pasta / f"verificacao-entrada-{k:02d}.jsonl").write_text("".join(lo), encoding="utf-8")
    print(f"{len(itens)} pares na 2.ª passagem, {len(lotes)} lotes em {pasta.relative_to(RAIZ)}")


def _nota(meta: dict, efeitos: str | None = None) -> str:
    caminho = (meta.get("identifiers") or {}).get("dre_path")
    ligacao = f"[{meta['title']}](https://diariodarepublica.pt{caminho})" if caminho else meta["title"]
    # sem data própria para a revogação, vale a entrada em vigor do diploma que revoga, quando é
    # posterior à publicação (vacatio legis)
    if not efeitos and em_vigor(meta) != str(meta.get("publication_date")):
        efeitos = em_vigor(meta)
    com_efeitos = f", com efeitos a partir de {efeitos}" if efeitos else ""
    return f"> Revogado pelo/a {ligacao}, publicado em {meta['publication_date']}{com_efeitos}."


def aplicar(dry_run: bool) -> None:
    # As certas da 1.ª ronda e das seguintes (verificacao-saida-<ronda>.jsonl); a resposta que conta
    # é a mais recente, que é a que a sua ronda verificou.
    certos = _certos()
    for f in sorted(LLM.glob("verificacao-saida-r*.jsonl")):
        certos |= _certos("-" + f.stem.split("-", 2)[2])
    resp, cands = respostas(), candidatos()
    acervo = Acervo(RAIZ)
    feitos, recusadas, n = [], [], 0
    for id_, c in sorted(cands.items()):
        # só os pares com trocas: um par sem trocas confirmado às cegas («outro diploma», «já aplicada»…) não muda o texto
        lista = [alt for alt in _ordem(c) if (id_, alt) in certos and resp.get((id_, alt), {}).get("trocas")]
        if not lista:
            continue
        caminho = RAIZ / c["caminho"]
        registo, _ = acervo.read(caminho)
        dados = acervo.read_history(caminho)
        if len(dados["versions"]) != 2:
            recusadas.append(f"{c['caminho']}: o histórico não tem duas versões")
            continue
        ja = {a["id"] for v in dados["versions"] for a in v["acts"]}
        linhas = corpo(caminho.read_text(encoding="utf-8")).split("\n")
        tocadas: dict[int, set[str]] = defaultdict(set)
        aplicados = []
        for alt in lista:
            if alt in ja:
                continue
            copia = list(linhas)
            try:
                feitas = rl.trocar(copia, encadear(linhas, resp[(id_, alt)]["trocas"]))
            except rl.Recusa as erro:
                recusadas.append(f"{c['caminho']}: {alt}: {erro}")
                continue
            linhas = copia
            meta = front_matter((RAIZ / c["alteradores"][alt]["path"]).read_text(encoding="utf-8"))
            efeitos = resp[(id_, alt)].get("efeitos")
            for f in feitas:
                tocadas[f["linha"]].add(_nota(meta, efeitos))
            aplicados.append({"alterador": alt, "titulo": meta["title"], "publicacao": str(meta["publication_date"]), "em_vigor": str(resp[(id_, alt)].get("efeitos") or em_vigor(meta)),
                              "dre_path": (meta.get("identifiers") or {}).get("dre_path"), "trocas": feitas,
                              "nao_aplicadas": resp[(id_, alt)].get("nao_aplicadas", [])})
        if not aplicados:
            continue
        novo = re.sub(r"\n{3,}", "\n\n", "\n".join(rt._com_notas(linhas, tocadas)))
        original = render_version(dados, dados["versions"][0], title=registo.title)
        primeira, segunda = (dict(v) for v in dados["versions"])
        segunda["acts"] = list(segunda["acts"]) + [{"id": a["alterador"], "title": a["titulo"], "published": a["publicacao"], "dre_path": a["dre_path"]} for a in aplicados]
        artigos = dict.fromkeys(f["artigo"] or "" for a in aplicados for f in a["trocas"])
        segunda["changes"] = list(segunda["changes"]) + [c_ for c_ in (f"Revoga Artigo {x}" if x else "Revoga anexo ou texto fora do articulado" for x in artigos) if c_ not in segunda["changes"]]
        data_nova = max([segunda["date"]] + [a["em_vigor"] for a in aplicados])
        segunda["date"] = data_nova
        novos = historico(registo.id, registo.title, original, novo, [primeira, segunda])
        if blocos(render_version(novos, novos["versions"][1], title=registo.title)) != blocos(novo) or blocos(render_version(novos, novos["versions"][0], title=registo.title)) != blocos(original):
            recusadas.append(f"{c['caminho']}: o histórico não reproduz o texto")
            continue
        registo.version_history = summarize(novos, acervo.history_path(caminho).name)
        if getattr(registo, "version", None) is not None and getattr(registo.version, "consolidation_date", None):
            registo.version.consolidation_date = max(str(registo.version.consolidation_date), data_nova)
        nota = " Revogações registadas só como repealed_by, aplicadas com um LLM e verificadas às cegas (consolidacao/revogacoes.py): " + "; ".join(a["titulo"] for a in aplicados) + "."
        if "consolidacao/revogacoes.py" not in (registo.provenance.notes or ""):
            anteriores = (registo.provenance.notes or "").rstrip()
            registo.provenance.notes = (anteriores + ("" if not anteriores or anteriores.endswith(".") else ".") + nota).strip()
        if not dry_run:
            acervo.save(registo, novo, target=caminho)
            acervo.write_history(caminho, novos)
        n += len(aplicados)
        feitos.append({"id": registo.id, "caminho": c["caminho"], "titulo": registo.title, "alteradores": aplicados})
        print(f"{'(dry-run) ' if dry_run else ''}{c['caminho']}: {len(aplicados)} alterador(es)")
    if not dry_run and feitos:
        anteriores = {json.loads(l)["id"]: json.loads(l) for l in APLICADOS.read_text(encoding="utf-8").splitlines() if l.strip()} if APLICADOS.exists() else {}
        for f in feitos:
            if f["id"] in anteriores:
                anteriores[f["id"]]["alteradores"] += f["alteradores"]
            else:
                anteriores[f["id"]] = f
        APLICADOS.write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in anteriores.values()), encoding="utf-8")
    print(f"Revogações aplicadas: {n}, em {len(feitos)} consolidados. Recusadas: {len(recusadas)}.")
    for r in recusadas:
        print("  ", r)


ESTADO = PASTA / "auditoria" / "revogacoes-estado.jsonl"


def _veredictos() -> dict[tuple[str, str], dict]:
    """O veredicto mais recente de cada par, de todas as rondas."""
    resultado = {}
    for sufixo in [""] + sorted("-" + f.stem.split("-", 2)[2] for f in LLM.glob("verificacao-saida-r*.jsonl")):
        entrada_v, saida = LLM / f"verificacao-entrada{sufixo}.jsonl", LLM / f"verificacao-saida{sufixo}.jsonl"
        if not saida.exists():
            continue
        itens = {json.loads(l)["n"]: json.loads(l) for l in entrada_v.read_text(encoding="utf-8").splitlines() if l.strip()}
        for linha in saida.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                v = json.loads(linha)
                resultado[(itens[v["n"]]["id"], itens[v["n"]]["alterador_id"])] = v
    return resultado


def estado() -> None:
    """Cada par (consolidado, alterador candidato) acaba aplicado ou com o motivo, em
    `auditoria/revogacoes-estado.jsonl`. Um par que a verificação às cegas não deu `certo` não se
    aplica (na dúvida, não se aplica), e o motivo é o do verificador."""
    resp, cands, vered = respostas(), candidatos(), _veredictos()
    aplicados = set()
    if APLICADOS.exists():
        for linha in APLICADOS.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                aplicados |= {(d["id"], a["alterador"]) for a in d["alteradores"]}
    linhas, contas = [], defaultdict(int)
    for id_, c in sorted(cands.items()):
        for alt in _ordem(c):
            r, a = resp.get((id_, alt)), c["alteradores"][alt]
            base = {"id": id_, "titulo": c["selecao"]["title"], "alterador": alt, "alterador_titulo": a["title"]}
            nao = (r or {}).get("nao_aplicadas", [])
            if (id_, alt) in aplicados:
                linha = base | {"estado": "aplicado", "por_aplicar": nao}
            elif r and r.get("trocas"):
                v = vered.get((id_, alt), {})
                linha = base | {"estado": "não se aplica", "motivo": f"a verificação às cegas deu «{v.get('veredicto', 'sem veredicto')}»: {v.get('motivo', '')}", "por_aplicar": nao}
            elif r:
                v = vered.get((id_, alt), {})
                motivo = "; ".join(f"{n['motivo']}: {n['instrucao']}" for n in nao)[:600]
                if v.get("veredicto") == "certo":
                    linha = base | {"estado": "não se aplica", "motivo": motivo, "confirmado_as_cegas": True}
                else:
                    linha = base | {"estado": "não se aplica", "motivo": motivo, "confirmado_as_cegas": False,
                                    "verificacao": f"«{v.get('veredicto', 'sem veredicto')}»: {v.get('motivo', '')}"[:600]}
            else:
                linha = base | {"estado": "sem resposta"}
            linhas.append(linha)
            contas[linha["estado"]] += 1
    # os pares já aplicados saem dos candidatos (o diploma que revoga passa a estar nas versões): vêm de APLICADOS
    vistos = {(l["id"], l["alterador"]) for l in linhas}
    if APLICADOS.exists():
        for l in APLICADOS.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            d = json.loads(l)
            for a in d["alteradores"]:
                if (d["id"], a["alterador"]) in vistos:
                    continue
                artigos = sorted({f.get("artigo") or "fora do articulado" for f in a.get("trocas", [])})
                linhas.append({"id": d["id"], "titulo": d["titulo"], "alterador": a["alterador"], "alterador_titulo": a["titulo"],
                               "estado": "aplicado", "artigos": artigos, "efeitos": a.get("em_vigor"), "por_aplicar": a.get("nao_aplicadas", [])})
                contas["aplicado"] += 1
    ESTADO.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    print(dict(contas), "| por ver:", contas.get("sem resposta", 0))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("passo", choices=["entrada", "entrada-r3", "verificacao", "juntar-saidas", "verificacao-v2", "aplicar", "estado"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ronda", help="com verificacao: só os pares respondidos nessa ronda (r2, …)")
    args = parser.parse_args(argv)
    if args.passo == "entrada":
        entrada()
    elif args.passo == "verificacao":
        verificacao(args.ronda)
    elif args.passo == "entrada-r3":
        entrada_r3()
    elif args.passo == "juntar-saidas":
        juntar_saidas()
    elif args.passo == "verificacao-v2":
        verificacao_v2()
    elif args.passo == "estado":
        estado()
    else:
        aplicar(args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
