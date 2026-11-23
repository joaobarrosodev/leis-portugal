"""Camada 1: fechar o texto em vigor do que o inventário deixou por fechar (`reports/inventario-camada-1.md`).

O inventário de 19/11/2026 (`texto-em-vigor-por-fechar.jsonl`) deixa três linhas por fechar:

- **linha 6:** os alterados de vigência desconhecida (`unknown`) que nunca foram triados, porque a
  seleção da escala (`selecionar.py --todos`) só aceitava `in_force` e `partially_in_force`;
- **linha 7:** as alterações ao texto por aplicar (`para LLM`, `sem texto do alterador`, `alteração só
  em imagem`), quase todas resíduos das rondas anteriores;
- **linha 9:** os consolidados com um alterador posterior à última versão.

«Fechar» quer dizer o mesmo que na auditoria dos consolidados: cada diploma acaba aplicado e verificado
às cegas, ou com o motivo escrito no estado (`auditoria/camada1-estado.jsonl`).

As ondas vão por ordem de retorno. A onda 1 são os citados por 10 ou mais diplomas em vigor e os
diplomas centrais (`reports/inventario-camada-1/diplomas-centrais.jsonl`) das linhas 6 e 7.

Passos:

    python consolidacao/camada1.py onda 1                # camada1/onda-1.jsonl, com a categoria de cada um
    python consolidacao/camada1.py selecao 1             # junta os nunca triados a selecao-escala.jsonl
    python consolidacao/camada1.py triagem 1             # regras e triagem, em resultados-escala.parte-7.jsonl

Depois da triagem, `python consolidacao/consolidar.py --escala --juntar` volta a escrever
`resultados-escala.jsonl` e `pendentes-escala.jsonl` com as partes todas.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import time
import traceback
from collections import Counter
from functools import lru_cache
from pathlib import Path

from texto import RAIZ, front_matter

PASTA = RAIZ / "consolidacao"
CAMADA1 = PASTA / "camada1"
INVENTARIO = RAIZ / "reports" / "inventario-camada-1"
SELECAO_ESCALA = PASTA / "selecao-escala.jsonl"
PARTE = PASTA / "resultados-escala.parte-7.jsonl"


def _jsonl(caminho: Path) -> list[dict]:
    return [json.loads(l) for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip()]


def _resposta(id_: str) -> tuple[str | None, dict | None]:
    for pasta in ("completo", "corrido"):
        f = PASTA / "llm" / pasta / f"{id_.replace(':', '_')}.json"
        if f.exists():
            return pasta, json.loads(f.read_text(encoding="utf-8"))
    return None, None


def _resultados() -> dict[str, dict]:
    return {r["id"]: r for r in _jsonl(PASTA / "resultados-escala.jsonl")}


def categoria(item: dict, resultado: dict | None) -> str:
    """Onde o diploma parou no pipeline, pela classe do inventário e pela última resposta do LLM."""
    if item["classe"] == "nao_triado":
        return "nao_triado"
    if item["classe"] == "alteracao_so_em_imagem":
        return "so_em_imagem"
    pasta, resposta = _resposta(item["id"])
    if resposta is None:
        estado = (resultado or {}).get("estado") or item.get("triagem")
        return {"sem texto do alterador": "sem_texto_do_alterador", "aplicado por regra": "aplicado_por_regra"}.get(estado, "sem_resposta")
    mudancas = sum(len(resposta.get(k) or []) for k in ("artigos", "anexos", "titulos", "removidos"))
    if resposta.get("problemas"):
        return f"{pasta}_com_problemas"
    if not mudancas:
        return f"{pasta}_nada_a_aplicar"
    return f"{pasta}_juntado"


def _estado_atual(path: str) -> str | None:
    """O `legal_status` do registo no data/ de hoje (depois da regra da vigência inferida da linha 3)."""
    from texto import front_matter  # noqa: PLC0415

    f = RAIZ / path
    if not f.exists():
        return None
    return (front_matter(f.read_text(encoding="utf-8")).get("legal_status") or None)


def onda_2() -> list[dict]:
    """O resto das linhas 6, 7 e 9 do inventário, para lá dos 214 da onda 1, por ordem de citações por diplomas em
    vigor. A vigência é a do data/ de hoje: saem os que já não estão em vigor (revogados ou caducados entretanto).
    Linha 9: os consolidados com alterador posterior à última versão, por quem os consolidou."""
    ja = {d["id"] for d in _jsonl(CAMADA1 / "onda-1.jsonl")}
    resultados = _resultados()
    em_vigor = ("in_force", "partially_in_force")
    itens, fora = [], Counter()
    for d in _jsonl(INVENTARIO / "texto-em-vigor-por-fechar.jsonl"):
        if d["classe"] == "revogado_por_inteiro" or d["id"] in ja:
            continue
        estado = _estado_atual(_path_de(d["id"]) or "")
        if estado not in em_vigor:
            fora[f"linhas 6 e 7, {estado}"] += 1
            continue
        itens.append({"id": d["id"], "titulo": d["titulo"], "tipo": d["tipo"], "estado_dre": d["estado"], "estado_hoje": estado,
                      "classe": d["classe"], "linha": 6 if d["classe"] == "nao_triado" else 7,
                      "citado_por_vigentes": d["citado_por_vigentes"], "central": False, "categoria": categoria(d, resultados.get(d["id"]))})
    for d in _jsonl(INVENTARIO / "consolidados-por-atualizar.jsonl"):
        if d["id"] in ja:
            continue
        if d.get("marca_de_vigencia") == "nao_vigora":
            fora["linha 9, marca nao_vigora (consolidacao/auditoria/vigencia-revista.jsonl)"] += 1
            continue
        estado = _estado_atual(_path_de(d["id"]) or "")
        if estado not in em_vigor:
            fora[f"linha 9, {estado}"] += 1
            continue
        quem = {"consolidado_leis_portugal": "nosso", "consolidado_dre": "dre"}.get(d["classe"], d["classe"])
        itens.append({"id": d["id"], "titulo": d["titulo"], "tipo": d["tipo"], "estado_dre": d["estado"], "estado_hoje": estado,
                      "classe": d["classe"], "linha": 9, "citado_por_vigentes": d["citado_por_vigentes"], "central": False,
                      "categoria": f"linha_9_{quem}", "consolidado_ate": d.get("consolidado_ate"),
                      "alteradores_posteriores": d.get("alteradores_posteriores") or []})
    itens.sort(key=lambda i: (-i["citado_por_vigentes"], i["id"]))
    for motivo, k in sorted(fora.items()):
        print(f"fora da onda 2: {k:5d}  {motivo}")
    return itens


@lru_cache(maxsize=1)
def _paths() -> dict[str, str]:
    """id → path no data/, pela seleção da escala e, para os outros, pelo índice do export."""
    paths = {r["id"]: r["path"] for r in _jsonl(SELECAO_ESCALA)}
    db = sqlite3.connect(f"file:{_export()}?mode=ro", uri=True)
    for i, p in db.execute("SELECT id, path FROM documentos"):
        paths.setdefault(i, p)
    return paths


def _path_de(id_: str) -> str | None:
    return _paths().get(id_)


def onda(n: int) -> list[dict]:
    if n == 2:
        return onda_2()
    if n != 1:
        raise SystemExit("só as ondas 1 e 2 estão definidas")
    centrais = {c["id"] for c in _jsonl(INVENTARIO / "diplomas-centrais.jsonl") if c.get("texto") in ("nao_triado", "alteracao_por_aplicar")}
    resultados = _resultados()
    itens = []
    for d in _jsonl(INVENTARIO / "texto-em-vigor-por-fechar.jsonl"):
        if d["classe"] == "revogado_por_inteiro":
            continue  # linha 8 do inventário, fora desta tarefa
        if d["citado_por_vigentes"] < 10 and d["id"] not in centrais:
            continue
        itens.append({"id": d["id"], "titulo": d["titulo"], "tipo": d["tipo"], "estado_dre": d["estado"], "classe": d["classe"],
                      "citado_por_vigentes": d["citado_por_vigentes"], "central": d["id"] in centrais,
                      "categoria": categoria(d, resultados.get(d["id"]))})
    itens.sort(key=lambda i: (-i["citado_por_vigentes"], i["id"]))
    return itens


def _export() -> Path:
    from selecionar import export_por_omissao  # noqa: PLC0415

    return export_por_omissao()


def selecao(itens: list[dict]) -> int:
    """Junta a `selecao-escala.jsonl` os nunca triados, com a seleção da escala (alteradores por ordem
    de data, retificações primeiro) feita sobre o export de hoje e sem filtro de vigência."""
    from selecionar import completar, selecionar_todos  # noqa: PLC0415

    ja = {json.loads(l)["id"] for l in SELECAO_ESCALA.read_text(encoding="utf-8").splitlines() if l.strip()}
    ids = {i["id"] for i in itens if i["categoria"] == "nao_triado" and i["id"] not in ja}
    if not ids:
        print("nada a juntar: os nunca triados já estão na seleção")
        return 0
    db = sqlite3.connect(f"file:{_export()}?mode=ro", uri=True)
    registos = [completar(r) | {"camada1": True} for r in selecionar_todos(db, ids)]
    em_falta = ids - {r["id"] for r in registos}
    with SELECAO_ESCALA.open("a", encoding="utf-8") as f:
        for r in registos:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(registos)} juntados a {SELECAO_ESCALA.name}; sem registo no export com texto: {sorted(em_falta)}")
    return 0


def triagem(itens: list[dict]) -> int:
    """`consolidar.processar` nos nunca triados, em `resultados-escala.parte-7.jsonl` (retomável)."""
    from consolidar import processar  # noqa: PLC0415

    ids = {i["id"] for i in itens if i["categoria"] == "nao_triado"}
    registos = [r for r in _jsonl(SELECAO_ESCALA) if r["id"] in ids]
    feitos = {r["id"] for r in _jsonl(PARTE)} if PARTE.exists() else set()
    contagem: Counter = Counter()
    with PARTE.open("a", encoding="utf-8") as f:
        for registo in registos:
            if registo["id"] in feitos:
                continue
            t = time.time()
            try:
                e = processar(registo)
            except Exception as erro:  # noqa: BLE001
                e = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "citacoes": registo["citacoes"],
                     "estado": "erro", "triagem": "erro", "motivo": f"{type(erro).__name__}: {erro}"[:300],
                     "traceback": traceback.format_exc()[-1500:]}
            e["segundos"] = round(time.time() - t, 3)
            contagem[e["estado"]] += 1
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"{sum(contagem.values())} triados: {dict(contagem)}")
    return 0


# A triagem às cegas por diploma: os que não têm trabalho do LLM pendente (as regras ou a última
# resposta dizem que não há nada a aplicar, o alterador não tem texto, o pedido era grande demais).
PARA_TRIAGEM = ("nao_triado", "completo_nada_a_aplicar", "corrido_nada_a_aplicar", "sem_texto_do_alterador",
                "sem_resposta", "so_em_imagem")
LIMITE_ALTERADOR = 8_000
INICIO = 3_000
JANELA = 800
LIMITE_GRANDE = 30_000
MAX_LOTE = 150_000
MAX_ITEM = 90_000


def _titulos(texto: str, n: int = 120) -> str:
    linhas = [l for l in texto.splitlines() if l.startswith("#")]
    extra = f"\n… e mais {len(linhas) - n} títulos" if len(linhas) > n else ""
    return "\n".join(linhas[:n]) + extra


def _alterador_para_triagem(a: dict, titulo_original: str) -> dict:
    from texto import alterador as texto_do_alterador  # noqa: PLC0415
    from texto import artigos_alteradores, front_matter, padrao_diploma, sem_ligacoes  # noqa: PLC0415

    base = {"alterador": a.get("title") or a["id"], "id": a["id"], "rotulos_dre": a.get("rotulos_dre") or [],
            "data": a.get("publication_date") or ""}
    caminho = RAIZ / a["path"] if a.get("path") else None
    if not caminho or not caminho.exists():
        return base | {"texto": None, "sem_texto": "o alterador não está no acervo"}
    meta = front_matter(caminho.read_text(encoding="utf-8"))
    if a.get("text_quality") != "texto":
        return base | {"texto": None, "sem_texto": f"o acervo só tem {a.get('text_quality')}",
                       "sumario": meta.get("summary") or meta.get("sumario") or ""}
    texto = texto_do_alterador(caminho)
    if len(texto) <= LIMITE_ALTERADOR:
        return base | {"texto": texto, "completo": True}
    # Grande: o início (o sumário e o preâmbulo, onde a «referida portaria» se identifica), os artigos
    # que mencionam o original e, fora deles, uma janela à volta de cada menção.
    artigos = artigos_alteradores(texto, titulo_original)
    partes = [texto[:INICIO]]
    partes += ["\n".join(x.linhas).strip() for x in artigos]
    padrao = padrao_diploma(titulo_original)
    limpo = sem_ligacoes(texto)
    if padrao is not None:
        dentro = "\n".join(partes)
        for m in list(padrao.finditer(limpo))[:12]:
            janela = limpo[max(0, m.start() - JANELA): m.end() + JANELA]
            if janela[JANELA // 2: -JANELA // 2] not in dentro:
                partes.append("[…] " + janela + " […]")
    trecho = "\n\n".join(partes)[:LIMITE_GRANDE]
    return base | {"texto": trecho, "completo": False, "tamanho_do_alterador": len(texto),
                   "nota": "o início do alterador, os artigos que mencionam o original e janelas à volta das outras menções"}


def _pasta_triagem(n: int) -> Path:
    """A pasta da triagem às cegas da onda `n`: `triagem/` na onda 1, `triagem-N/` nas seguintes."""
    return CAMADA1 / ("triagem" if n == 1 else f"triagem-{n}")


def entrada_triagem(itens: list[dict], n: int = 1) -> int:
    from texto import front_matter, publicado  # noqa: PLC0415

    selecao = {r["id"]: r for r in _jsonl(SELECAO_ESCALA)}
    linhas = []
    for i in itens:
        if i["categoria"] not in PARA_TRIAGEM:
            continue
        registo = selecao[i["id"]]
        caminho = RAIZ / registo["path"]
        meta = front_matter(caminho.read_text(encoding="utf-8"))
        original = publicado(caminho)
        linhas.append({
            "id": i["id"], "titulo": registo["title"], "data": registo.get("publication_date") or "",
            "sumario": meta.get("summary") or "", "titulos_do_original": _titulos(original),
            "imagens_no_original": original.count("(ver documento original)"),
            "inicio_do_original": original[:3000],
            "alteradores": [_alterador_para_triagem(a, registo["title"]) for a in registo["alteradores"]],
        })
    # Um diploma com muitos alteradores parte-se em itens de até MAX_ITEM caracteres de alteradores
    # (`parte`: «2/3»); a resposta é por alterador, por isso as partes juntam-se sem mais nada.
    itens_lote = []
    for linha in linhas:
        grupos, atual_g, t_g = [], [], 0
        for a in linha["alteradores"]:
            t = len(a.get("texto") or "") + 300
            if atual_g and t_g + t > MAX_ITEM:
                grupos.append(atual_g)
                atual_g, t_g = [], 0
            atual_g.append(a)
            t_g += t
        grupos.append(atual_g)
        for k, g in enumerate(grupos, 1):
            itens_lote.append(linha | {"alteradores": g, "parte": f"{k}/{len(grupos)}"})
    lotes, atual, tamanho = [], [], 0
    for linha in itens_lote:
        t = len(json.dumps(linha, ensure_ascii=False))
        if atual and tamanho + t > MAX_LOTE:
            lotes.append(atual)
            atual, tamanho = [], 0
        atual.append(linha)
        tamanho += t
    if atual:
        lotes.append(atual)
    pasta = _pasta_triagem(n)
    pasta.mkdir(exist_ok=True)
    for k, lote in enumerate(lotes, 1):
        (pasta / f"entrada-{k:02d}.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lote), encoding="utf-8")
    print(f"{len(linhas)} diplomas em {len(itens_lote)} itens e {len(lotes)} lotes em {pasta.relative_to(RAIZ)}")
    return 0


# O pedido de novo ao LLM: os juntados que falharam às cegas e as respostas com problemas na
# verificação letra a letra, com os reparos todos (também os de imagem, que o `reparos.py` salta).
PARA_PEDIDO = ("completo_juntado", "completo_com_problemas", "corrido_com_problemas", "aplicado_por_regra")
ADENDA = CAMADA1 / "ADENDA-respondedor.md"


def texto_dos_reparos(id_: str, ultima: dict[str, list[dict]]) -> str | None:
    """Os reparos da última ronda às cegas e os problemas da última resposta, para o pedido."""
    import reparos as reparos_mod  # noqa: PLC0415

    linhas = ultima.get(id_, [])
    diploma = [x for x in linhas if "instrucoes_em_falta" in x]
    artigos = [x for x in linhas if x.get("veredicto") in ("errado", "dúvida")]
    falta = [i for x in diploma for i in (x.get("instrucoes_em_falta") or [])]
    _, resposta = _resposta(id_)
    problemas = (resposta or {}).get("problemas") or []
    achados = _achados_da_triagem().get(id_, [])
    segunda = _segunda_e_nada().get(id_, [])
    if not artigos and not falta and not problemas and not achados and not segunda:
        return None
    partes = ["### Reparos às respostas anteriores",
              "Uma resposta anterior a este diploma foi verificada por outro modelo e por um programa, que encontraram estes",
              "problemas. Confirma cada um no texto dos diplomas que alteram (podem estar enganados) e devolve a resposta",
              "inteira corrigida. Um reparo sobre um quadro, mapa ou anexo que só existe em imagem resolve-se como diz a",
              "adenda das regras («Imagens»), ou vai para `nao_aplicavel` com o motivo.", ""]
    for a in artigos:
        nome = re.sub(r"^Artigo\s+", "", str(a.get("artigo") or ""))
        imagem = " (fala de uma imagem)" if reparos_mod.de_imagem(a) else ""
        partes.append(f"- Artigo {nome}: {a.get('veredicto')}{imagem}. {a.get('motivo') or ''}".rstrip())
        if (a.get("texto_esperado") or "").strip():
            partes.append(f"  Texto esperado segundo o verificador: {a['texto_esperado'].strip()}")
    for i in falta:
        partes.append(f"- Instrução que não se vê aplicada: {i if isinstance(i, str) else json.dumps(i, ensure_ascii=False)}")
    for p in problemas[:30]:
        partes.append(f"- Problema na verificação letra a letra da resposta anterior: {p}")
    for s in segunda:
        partes.append(f"- {s}")
    for a in achados:
        o_que = "; ".join(a["instrucoes"]) or a["motivo"]
        partes.append(f"- Uma triagem às cegas leu {a['alterador']} e viu ({a['veredicto']}): {o_que}")
    return "\n".join(partes) + "\n"


def _segunda_e_nada() -> dict[str, list[str]]:
    """Os problemas da segunda leitura jurídica e as instruções em falta da verificação do «nada a aplicar»,
    para os reparos da ronda 116."""
    por: dict[str, list[str]] = {}
    for f in sorted(CAMADA1.glob("segunda*/segunda-*.json")):
        for d in json.loads(f.read_text(encoding="utf-8")):
            if d["veredicto"] != "certo":
                por.setdefault(d["id"], []).extend(f"Uma segunda leitura jurídica encontrou: {p}" for p in d.get("problemas") or [])
    for f in sorted(CAMADA1.glob("nada*/resposta-*.json")):
        for d in json.loads(f.read_text(encoding="utf-8")):
            por.setdefault(d["id"], []).extend(f"Instrução que não se vê aplicada: {i}" for i in d.get("instrucoes_em_falta") or [])
    if ESTADO.exists():
        for e in _jsonl(ESTADO):
            if e.get("estado") == "recusado_na_verificacao_mecanica":
                por.setdefault(e["id"], []).append(
                    "Uma verificação mecânica viu o texto antigo a seguir à nova redação ou a «(Revogado.)». Devolve cada um destes "
                    "artigos inteiro, só com o texto em vigor: " + str(e.get("motivo", "")).split(": ", 1)[-1])
    return por


def pedidos_llm(itens: list[dict], ids_extra: list[str], nome: str = "pedidos", so_extra: bool = False) -> int:
    import reparos as reparos_mod  # noqa: PLC0415

    pasta_base = CAMADA1 / nome
    ids = ([] if so_extra else [i["id"] for i in itens if i["categoria"] in PARA_PEDIDO]) + [i for i in ids_extra]
    ultima = reparos_mod.ultima_ronda()
    rotas = {}
    for id_ in ids:
        pasta, _ = _resposta(id_)
        rotas[id_] = "corrido" if pasta == "corrido" else "completo"
    adenda = ADENDA.read_text(encoding="utf-8")
    tamanhos = {}
    for rota in ("completo", "corrido"):
        deste = [i for i in ids if rotas[i] == rota]
        if not deste:
            continue
        pasta = pasta_base / rota
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "ids.txt").write_text("\n".join(deste) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(PASTA / f"llm_{rota}.py"), "pedidos", str(pasta / "ids.txt"), str(pasta), "--por-ficheiro", "1"],
                       check=True)
        regras = pasta / "REGRAS.md"
        regras.write_text(regras.read_text(encoding="utf-8") + "\n" + adenda, encoding="utf-8")
        for pedido in sorted(pasta.glob("pedido-*.md")):
            texto = pedido.read_text(encoding="utf-8")
            for id_ in re.findall(r"^<<<DIPLOMA id=(\S+)>>>$", texto, re.M):
                r = texto_dos_reparos(id_, ultima)
                if r:
                    texto = texto.replace(f"<<<DIPLOMA id={id_}>>>\n", f"<<<DIPLOMA id={id_}>>>\n\n{r}\n", 1)
                tamanhos[f"{rota}/{pedido.name}"] = (id_, len(texto))
            pedido.write_text(texto, encoding="utf-8")
    (pasta_base / "tamanhos.json").write_text(json.dumps(tamanhos, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(ids)} diplomas: {Counter(rotas.values())}; acima de 200 mil caracteres: "
          f"{sum(1 for _, t in tamanhos.values() if t > 200_000)}")
    return 0


def classe_da_triagem(veredictos: list[dict]) -> str:
    """O que a triagem às cegas diz do diploma, pela precedência dos veredictos dos alteradores."""
    s = {v["veredicto"] for v in veredictos}
    if s & {"altera_texto", "duvida"}:
        return "para_llm"
    if "revoga_o_original" in s:
        return "revogado"
    if "so_imagem" in s:
        return "so_imagem"
    if "sem_texto" in s:
        return "sem_texto"
    return "sem_alteracao"


def juntar_triagem(n: int = 1) -> int:
    """`camada1/triagem.jsonl`: por diploma, os veredictos de cada alterador e a classe. As saídas que
    escreveram o título no lugar do id do alterador juntam-se pela posição (o número e a ordem batem). Os diplomas
    de outras ondas que já lá estão ficam; os desta onda substituem-se."""
    pasta = _pasta_triagem(n)
    entradas, saidas = {}, {}
    for f in sorted(pasta.glob("entrada-*.jsonl")):
        for d in _jsonl(f):
            entradas[(d["id"], d["parte"])] = d
    for f in sorted(pasta.glob("saida-*.jsonl")):
        for d in _jsonl(f):
            saidas[(d["id"], d["parte"])] = d
    em_falta = [k for k in entradas if k not in saidas]
    if em_falta:
        raise SystemExit(f"itens sem saída: {em_falta}")
    por: dict[str, list[dict]] = {}
    for k, e in entradas.items():
        s = saidas[k]["alteradores"]
        if len(s) != len(e["alteradores"]):
            raise SystemExit(f"{k}: {len(s)} veredictos para {len(e['alteradores'])} alteradores")
        for a, v in zip(e["alteradores"], s, strict=True):
            por.setdefault(k[0], []).append({"id": a["id"], "alterador": a["alterador"], "veredicto": v["veredicto"],
                                             "motivo": v.get("motivo") or "", "instrucoes": v.get("instrucoes") or [],
                                             "texto_completo": a.get("completo"), "sem_texto": a.get("sem_texto")})
    linhas = [{"id": i, "classe": classe_da_triagem(v), "alteradores": v} for i, v in por.items()]
    f = CAMADA1 / "triagem.jsonl"
    linhas = [d for d in (_jsonl(f) if f.exists() else []) if d["id"] not in por] + linhas
    f.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    print(f"{len(por)} diplomas desta onda: {dict(Counter(l['classe'] for l in linhas if l['id'] in por))}; {len(linhas)} no ficheiro")
    return 0


def _achados_da_triagem() -> dict[str, list[dict]]:
    f = CAMADA1 / "triagem.jsonl"
    if not f.exists():
        return {}
    return {d["id"]: [a for a in d["alteradores"] if a["veredicto"] in ("altera_texto", "duvida")] for d in _jsonl(f)}


AFASTADOS = ("nao_menciona", "outro_diploma", "nao_textual", "sem_texto")


def encolher(nome: str, limite: int) -> int:
    """Nos pedidos acima de `limite` caracteres, troca o texto dos alteradores que a triagem às cegas
    afastou (não menciona o original, é de outro diploma, não é textual) por uma linha com o veredicto e
    o motivo. A numeração dos alteradores fica a mesma, por isso a resposta junta-se como sempre."""
    from llm_completo import _alteradores  # noqa: PLC0415

    selecao = {r["id"]: r for r in _jsonl(SELECAO_ESCALA)}
    triagem = {d["id"]: {a["id"]: a for a in d["alteradores"]} for d in _jsonl(CAMADA1 / "triagem.jsonl")}
    pasta_base = CAMADA1 / nome
    tamanhos = json.loads((pasta_base / "tamanhos.json").read_text(encoding="utf-8"))
    for chave, (id_, tamanho) in sorted(tamanhos.items()):
        if tamanho <= limite or id_ not in triagem:
            continue
        caminho = pasta_base / chave
        texto = caminho.read_text(encoding="utf-8")
        ids = [a["id"] for a in _alteradores(selecao[id_])]
        partes = re.split(r"(?m)^(### Alterador (\d+): .*)$", texto)
        # partes: [antes, cabeçalho, n, corpo, cabeçalho, n, corpo, …]
        novo, omitidos = [partes[0]], 0
        for k in range(1, len(partes), 3):
            cabecalho, n, corpo = partes[k], int(partes[k + 1]), partes[k + 2]
            v = triagem[id_].get(ids[n - 1]) if n - 1 < len(ids) else None
            fim = ""
            if v is None:
                novo += [cabecalho, corpo]
                continue
            # o último alterador leva o fim do diploma («<<<FIM DO DIPLOMA…»): não se perde
            m = re.search(r"(?m)^<<<FIM DO DIPLOMA id=.*$", corpo)
            if m:
                fim = "\n" + corpo[m.start():]
            if v["veredicto"] in AFASTADOS:
                novo += [cabecalho, f"\n(Texto omitido: uma triagem às cegas leu este alterador e não muda o texto deste diploma: "
                                    f"{v['veredicto']}. {v['motivo']})\n\n" + fim]
                omitidos += 1
            else:
                novo += [cabecalho, corpo]
        texto_novo = "".join(novo)
        caminho.write_text(texto_novo, encoding="utf-8")
        tamanhos[chave] = [id_, len(texto_novo)]
        print(f"{chave}: {tamanho // 1000} → {len(texto_novo) // 1000} mil caracteres ({omitidos} alteradores omitidos)")
    (pasta_base / "tamanhos.json").write_text(json.dumps(tamanhos, ensure_ascii=False, indent=0), encoding="utf-8")
    return 0


# A numeração que a verificação letra a letra de `llm_completo` não tira: «§ 5.º», «§ único.», «Art. 10.º -»,
# «2.», «3)». Um parágrafo renumerado («§ 4.º» que passa a «§ 5.º») vem do original ou do alterador sem ela.
_NUMERACAO_LARGA = re.compile(r"^(?:§\s*(?:\d+\s*\.?\s*[º°o]|[úu]nico)|Art(?:igo)?\.?\s*\d+\s*\.?\s*[º°o]?(?:-[A-Z])?|\d+\s*\.?\s*[º°o]|\d+\.|\d+\)|[a-z]{1,3}\))\s*[-–.:]?\s*", re.I)
_REVOGADO_LARGO = re.compile(r"^\(?Revogad[oa]s?\.?\)?\.?$", re.I)


def troca_de_expressao(par: str, base: list[str], alteradores: list[str], maximo: int = 15) -> bool:
    """O parágrafo é um parágrafo da base (texto atual ou original) com uma expressão trocada por outra, e o
    mesmo alterador traz as duas expressões letra a letra: «onde se lê … deve ler-se …», «a expressão … é
    substituída por …», «os prazos até 30 de Abril … passam para 30 de Junho». Todos os textos já vêm planos
    (`_plano`). As diferenças ficam numa só zona de até `maximo` palavras; essa zona, com o contexto que for
    preciso para ter pelo menos 15 caracteres de cada lado da troca, tem de estar no alterador antes e depois."""
    import difflib  # noqa: PLC0415

    p = par.split()
    if len(p) < 4:
        return False
    for q_texto in base:
        q = q_texto.split()
        if not q or abs(len(q) - len(p)) > maximo:
            continue
        m = difflib.SequenceMatcher(None, q, p, autojunk=False)
        if m.real_quick_ratio() < 0.6 or m.quick_ratio() < 0.6:
            continue
        ops = [o for o in m.get_opcodes() if o[0] != "equal"]
        if not ops:
            continue
        i1, i2, j1, j2 = ops[0][1], ops[-1][2], ops[0][3], ops[-1][4]
        if max(i2 - i1, j2 - j1) > maximo:
            continue
        for esq in range(0, 5):
            for dir_ in range(0, 5):
                if i1 - esq < 0 or j1 - esq < 0 or i2 + dir_ > len(q) or j2 + dir_ > len(p):
                    continue
                antes = " ".join(q[i1 - esq : i2 + dir_])
                depois = " ".join(p[j1 - esq : j2 + dir_])
                if len(antes) < 15 or len(depois) < 15:
                    continue
                if any(antes in a and depois in a for a in alteradores):
                    return True
    return False


def _problemas_que_ficam(problemas: list[str], fontes: list[str]) -> tuple[list[str], list[str]]:
    """Separa os problemas «parágrafo que não está no alterador nem no original» que são só numeração
    (o parágrafo, sem «§ N.º» ou «Art. N.º -», está numa fonte, ou é uma revogação) dos outros."""
    from verificar import _plano  # noqa: PLC0415

    ficam, aceites = [], []
    for prob in problemas:
        m = re.match(r"^(.+?): parágrafo que não está no alterador nem no original: (.*)$", prob)
        if not m:
            ficam.append(prob)
            continue
        inicio = m.group(2)
        resto = _NUMERACAO_LARGA.sub("", inicio).strip()
        if _REVOGADO_LARGO.match(resto) or (len(_plano(resto)) >= 20 and any(_plano(resto)[:70] in f for f in fontes)):
            aceites.append(prob)
        else:
            ficam.append(prob)
    return ficam, aceites


def importar(pastas: list[str]) -> int:
    """Importa as respostas da ronda como `llm_completo.py importar` e `llm_corrido.py importar`, com uma
    diferença no pedido completo: a verificação letra a letra aceita também os parágrafos do texto atual
    (o consolidado das regras e o corpo dos anexos), como já faz nas passagens. Sem isto, um parágrafo que a
    resposta copia do texto atual (um «§ único - (Revogado.)» que as regras aplicaram) contava como
    inventado."""
    import llm_completo as lc  # noqa: PLC0415

    selecao = {r["id"]: r for r in _jsonl(SELECAO_ESCALA)}
    contagem: Counter = Counter()
    por_id: dict[str, list[dict]] = {}
    corridos = []
    for nome in pastas:
        for f in sorted((CAMADA1 / nome / "completo").glob("resposta-*.json")):
            lido = json.loads(f.read_text(encoding="utf-8"))
            for r in (lido if isinstance(lido, list) else [lido]):
                por_id.setdefault(r["id"], []).append(r)
        corridos += sorted((CAMADA1 / nome / "corrido").glob("resposta-*.json"))
    lc.COMPLETO.mkdir(parents=True, exist_ok=True)
    for i, partes in por_id.items():
        resposta = partes[0] if len(partes) == 1 else lc._fundir(partes)
        resposta |= {"modelo": resposta.get("modelo") or "claude-opus-5-5", "pedido": "completo", "ronda_camada1": RONDA}
        extra = lc._estado(selecao[i])
        atuais = [lc._texto_atual(extra["consolidado"]), extra["consolidado"].texto()] if extra.get("consolidado") is not None else []
        problemas = lc.verificar_resposta(resposta, selecao[i], atuais)
        # A verificação devolve só os primeiros 80 caracteres do parágrafo: confirma-se o parágrafo inteiro.
        from verificar import _plano  # noqa: PLC0415
        fontes = [_plano(x) for x in atuais] + [_plano(lc.texto_do_alterador(RAIZ / a["path"])) for a in lc._alteradores_da_selecao(selecao[i]) if a.get("path")]
        fontes.append(_plano(lc.publicado(RAIZ / selecao[i]["path"])))
        alts = [_plano(lc.texto_do_alterador(RAIZ / a["path"])) for a in lc._alteradores_da_selecao(selecao[i]) if a.get("path")]
        textos_alts = [lc.texto_do_alterador(RAIZ / a["path"]) for a in lc._alteradores_da_selecao(selecao[i]) if a.get("path")]
        base = [_plano(x) for t in atuais + [lc.publicado(RAIZ / selecao[i]["path"])] + textos_alts for x in t.split("\n\n") if x.strip()]
        inteiros = {}
        for artigo in resposta.get("artigos") or []:
            for par in (x.strip() for x in artigo["texto"].split("\n\n") if x.strip()):
                inteiros[f"{artigo['chave']}: parágrafo que não está no alterador nem no original: {par[:80]}"] = par
        ficam, aceites = [], []
        for prob in problemas:
            par = inteiros.get(prob)
            if par is None:
                ficam.append(prob)
                continue
            resto = _NUMERACAO_LARGA.sub("", par).strip()
            plano = _plano(resto)
            if _REVOGADO_LARGO.match(resto) or (len(plano) >= 20 and any(plano in f for f in fontes)):
                aceites.append(prob)
            elif troca_de_expressao(_plano(par), base, alts):
                aceites.append(prob + " (troca de expressão do alterador)")
            else:
                ficam.append(prob)
        resposta["problemas"] = ficam
        resposta["numeracao_aceite"] = aceites
        alvos = lc._alvos_com_regras(resposta, selecao[i])
        resposta["problemas"] += alvos["sem_instrucao"]
        resposta["avisos"] = alvos["rotulo_por_aplicar"]
        tipo = "com problemas" if resposta["problemas"] else "sem alterações" if not (resposta.get("artigos") or resposta.get("anexos") or resposta.get("titulos") or resposta.get("removidos")) else "sem problemas"
        contagem[tipo] += 1
        (lc.COMPLETO / (i.replace(":", "_") + ".json")).write_text(json.dumps(resposta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"pedido completo: {dict(contagem)}")
    if corridos:
        subprocess.run([sys.executable, str(PASTA / "llm_corrido.py"), "importar", *map(str, corridos)], check=True)
        # No texto corrido, «Art. 10.º - (Revogado.)» é a revogação na forma do diploma: não é texto inventado.
        # Um parágrafo com uma expressão trocada pelo alterador também não (troca_de_expressao).
        import llm_corrido as lco  # noqa: PLC0415
        from verificar import _plano  # noqa: PLC0415

        for f in corridos:
            for r in json.loads(f.read_text(encoding="utf-8")):
                g = PASTA / "llm" / "corrido" / f"{r['id'].replace(':', '_')}.json"
                d = json.loads(g.read_text(encoding="utf-8"))
                registo = selecao[r["id"]]
                base = [_plano(t) for tipo, _, t in lco.itens(lco._registo_base(registo)) if tipo == "u" and t.strip()]
                textos_alts = [lc.texto_do_alterador(RAIZ / a["path"]) for a in lco._alteradores(registo) if a.get("path")]
                alts = [_plano(t) for t in textos_alts]
                base += [_plano(x) for t in textos_alts for x in t.split("\n\n") if x.strip()]
                novos = [p.strip() for s in (d.get("substituicoes") or []) + (d.get("insercoes") or []) for p in (s.get("texto") or "").split("\n\n") if p.strip()]
                ficam, aceites = [], []
                for prob in d.get("problemas") or []:
                    m = re.match(r"^.+?: parágrafo que não está no alterador nem no original: (.*)$", prob)
                    inteiro = next((p for p in novos if m and p.startswith(m.group(1))), None)
                    if m and _REVOGADO_LARGO.match(_NUMERACAO_LARGA.sub("", m.group(1)).strip()):
                        aceites.append(prob)
                    elif inteiro and troca_de_expressao(_plano(inteiro), base, alts):
                        aceites.append(prob + " (troca de expressão do alterador)")
                    else:
                        ficam.append(prob)
                if aceites:
                    d["problemas"], d["numeracao_aceite"] = ficam, aceites
                    g.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


RONDA = 115
PASTAS_DA_RONDA = {115: ("pedidos", "pedidos-2"), 116: ("pedidos-3",), 117: ("pedidos-4",), 118: ("pedidos-5",), 119: ("pedidos-6",)}


def _sufixo() -> str:
    """As pastas `nada/` e `segunda/` são da ronda 115; as das rondas seguintes levam o número."""
    return "" if RONDA == 115 else f"-{RONDA}"


def _nossos() -> set[str]:
    nossos = set()
    for nome in PASTAS_DA_RONDA[RONDA]:
        for f in (CAMADA1 / nome).glob("*/resposta-*.json"):
            lido = json.loads(f.read_text(encoding="utf-8"))
            nossos |= {r["id"] for r in (lido if isinstance(lido, list) else [lido])}
    return nossos


def ronda() -> int:
    """Junta as respostas (`llm_completo.py juntar`, `llm_corrido.py juntar`), escreve a entrada às cegas da
    ronda 115 (`cegas.py --escala`) e deixa nela só os diplomas desta camada, com o `nao_aplicavel` de cada
    resposta em `nao_aplicavel_respondedor` (a vista mostra-o ao verificador como afirmação a confirmar)."""
    from cegas import VERIFICACAO  # noqa: PLC0415

    for comando in (["llm_completo.py", "juntar"], ["llm_corrido.py", "juntar"]):
        subprocess.run([sys.executable, str(PASTA / comando[0]), *comando[1:]], check=True, capture_output=True)
    if list(VERIFICACAO.glob(f"entrada-piloto-{RONDA}-lote-*.jsonl")):
        raise SystemExit(f"a ronda {RONDA} já tem entrada")
    subprocess.run([sys.executable, str(PASTA / "cegas.py"), "--escala", "--ronda", str(RONDA)], check=True)
    nossos = _nossos()
    linhas, fora = [], Counter()
    for f in sorted(VERIFICACAO.glob(f"entrada-piloto-{RONDA}-lote-*.jsonl")):
        for d in _jsonl(f):
            if d["id"] in nossos:
                _, resposta = _resposta(d["id"])
                if (resposta or {}).get("nao_aplicavel"):
                    d["nao_aplicavel_respondedor"] = resposta["nao_aplicavel"]
                linhas.append(d)
            else:
                fora[d["id"]] += 1
        f.unlink()
    lotes = [linhas[i : i + 30] for i in range(0, len(linhas), 30)]
    for n, lote in enumerate(lotes, 1):
        (VERIFICACAO / f"entrada-piloto-{RONDA}-lote-{n:02d}.jsonl").write_text(
            "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lote), encoding="utf-8")
    print(f"ronda {RONDA}: {len(linhas)} diplomas desta camada em {len(lotes)} lotes; {len(fora)} de fora (outros juntados que mudaram)")
    (CAMADA1 / f"ronda-{RONDA}-de-fora.txt").write_text("".join(f"{i}\n" for i in sorted(fora)), encoding="utf-8")
    return 0


def acrescentar_iguais() -> int:
    """Junta à ronda 115 os juntados desta camada que o `cegas.py` saltou por terem o mesmo texto de uma
    ronda anterior. Essa ronda recusou-os, muitas vezes só por instruções sobre imagens que não se aplicam;
    a ronda 115 vê o `nao_aplicavel` e pode dá-las por justificadas."""
    from cegas import VERIFICACAO, linha_de  # noqa: PLC0415

    selecao = {r["id"]: r for r in _jsonl(SELECAO_ESCALA)}
    nossos = _nossos()
    lotes = sorted(VERIFICACAO.glob(f"entrada-piloto-{RONDA}-lote-*.jsonl"))
    linhas = [d for f in lotes for d in _jsonl(f)]
    ja = {d["id"] for d in linhas}
    juntados = {}
    for nome in ("juntados-completo.jsonl", "juntados-corrido.jsonl"):
        for j in _jsonl(PASTA / "llm" / nome):
            if j["id"] in nossos and j["estado"] == "aplicado com LLM":
                juntados[j["id"]] = j
    novos = 0
    for i, j in juntados.items():
        if i in ja:
            continue
        d = linha_de(j, selecao[i])
        _, resposta = _resposta(i)
        if (resposta or {}).get("nao_aplicavel"):
            d["nao_aplicavel_respondedor"] = resposta["nao_aplicavel"]
        d["igual_a_ronda_anterior"] = True
        linhas.append(d)
        novos += 1
    for f in lotes:
        f.unlink()
    for n, k in enumerate(range(0, len(linhas), 30), 1):
        (VERIFICACAO / f"entrada-piloto-{RONDA}-lote-{n:02d}.jsonl").write_text(
            "".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas[k : k + 30]), encoding="utf-8")
    print(f"ronda {RONDA}: {novos} juntados com o texto de uma ronda anterior acrescentados; {len(linhas)} diplomas")
    return 0


def encolher_ronda() -> int:
    """Nas entradas da ronda 115, troca o texto dos alteradores que a triagem às cegas afastou por uma linha
    com o veredicto, como `encolher` faz nos pedidos. O consolidado e o original não mudam."""
    from cegas import VERIFICACAO  # noqa: PLC0415

    triagem = {d["id"]: d["alteradores"] for d in _jsonl(CAMADA1 / "triagem.jsonl")}
    for f in sorted(VERIFICACAO.glob(f"entrada-piloto-{RONDA}-lote-*.jsonl")):
        linhas = _jsonl(f)
        for d in linhas:
            if d["id"] not in triagem or "alteradores" not in d:
                continue
            por_titulo: dict[str, list[dict]] = {}
            for v in triagem[d["id"]]:
                por_titulo.setdefault(v["alterador"], []).append(v)
            antes = len(d["texto_alterador"])
            for a in d["alteradores"]:
                vs = por_titulo.get(a["titulo"]) or []
                # títulos repetidos («Despacho»): só se omite quando todos os do mesmo título foram afastados
                if vs and all(v["veredicto"] in AFASTADOS for v in vs):
                    a["texto"] = (f"(Texto omitido: uma triagem às cegas leu este alterador e não muda o texto deste diploma: "
                                  f"{vs[0]['veredicto']}. {vs[0]['motivo']})")
                    a["omitido_pela_triagem"] = True
            d["texto_alterador"] = "\n\n".join(
                a["texto"] if a["texto"].lstrip().startswith("# ") else f"# {a['titulo']}\n\n{a['texto']}" for a in d["alteradores"])
            if len(d["texto_alterador"]) < antes:
                print(f"{d['titulo']}: alteradores {antes // 1000} → {len(d['texto_alterador']) // 1000} mil caracteres")
        f.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    return 0


def entrada_nada() -> int:
    """`camada1/nada/`: os diplomas desta camada cuja resposta não muda nada («não junto» por não ter artigos
    ou por não mudar o texto). Uma entrada no formato da ronda às cegas, com o texto atual como consolidado
    (igual ao original, ou com o que as regras aplicaram) e o `nao_aplicavel` da resposta, para um
    verificador às cegas confirmar ou não cada motivo. Fica fora de `verificacao/`: o `acervo.py` não a lê."""
    import llm_completo as lc  # noqa: PLC0415
    from cegas import _texto_alterador  # noqa: PLC0415
    from cegas_vista import vista  # noqa: PLC0415
    from texto import publicado  # noqa: PLC0415

    selecao = {r["id"]: r for r in _jsonl(SELECAO_ESCALA)}
    triagem = {d["id"]: {a["id"]: a for a in d["alteradores"]} for d in _jsonl(CAMADA1 / "triagem.jsonl")}
    juntados = {}
    for nome in ("juntados-completo.jsonl", "juntados-corrido.jsonl"):
        for j in _jsonl(PASTA / "llm" / nome):
            juntados[j["id"]] = j
    nossos = _nossos()
    pasta = CAMADA1 / f"nada{_sufixo()}"
    pasta.mkdir(exist_ok=True)
    linhas = []
    for i in sorted(nossos):
        j = juntados.get(i, {})
        motivo = str(j.get("motivo") or "")
        if j.get("estado") != "não junto" or not motivo.startswith(("a resposta não tem artigos", "a resposta não muda")):
            continue
        registo = selecao[i]
        _, resposta = _resposta(i)
        original = publicado(RAIZ / registo["path"])
        extra = lc._estado(registo)
        atual = extra["consolidado"].texto() if extra.get("consolidado") is not None else original
        textos = []
        for a in lc._alteradores(registo):
            v = triagem.get(i, {}).get(a["id"])
            if v and v["veredicto"] in AFASTADOS:
                texto, completo = (f"(Texto omitido: uma triagem às cegas leu este alterador e não muda o texto deste diploma: "
                                   f"{v['veredicto']}. {v['motivo']})"), True
            else:
                texto, completo = _texto_alterador(a["path"], registo["title"])
            textos.append({"titulo": a["title"], "texto": texto, "completo": completo})
        d = {"id": i, "titulo": registo["title"], "alterador": " e ".join(t["titulo"] for t in textos),
             "alterador_completo": all(t["completo"] for t in textos),
             "texto_alterador": "\n\n".join(t["texto"] if t["texto"].lstrip().startswith("# ") else f"# {t['titulo']}\n\n{t['texto']}" for t in textos),
             "alteradores": textos, "texto_original": original, "texto_consolidado": atual,
             "nao_aplicavel_respondedor": (resposta or {}).get("nao_aplicavel") or "(a resposta diz que não há nada a aplicar, sem motivo)"}
        if (resposta or {}).get("pedido") == "corrido":
            d["modo"] = "corrido"
        linhas.append(d)
    (pasta / "entrada.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    pedacos, atual_p = [], None
    for d in linhas:
        texto = vista(d)
        if atual_p is None or (atual_p["chars"] + len(texto) > 140_000 and atual_p["ids"]):
            atual_p = {"ids": [], "chars": 0, "textos": []}
            pedacos.append(atual_p)
        atual_p["ids"].append(d["id"])
        atual_p["chars"] += len(texto)
        atual_p["textos"].append(texto)
    for n, p in enumerate(pedacos, 1):
        (pasta / f"vista-{n:03d}.md").write_text("\n".join(p["textos"]), encoding="utf-8")
    (pasta / "pedacos.json").write_text(json.dumps([{"pedaco": n, "ids": p["ids"], "chars": p["chars"]} for n, p in enumerate(pedacos, 1)],
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(linhas)} diplomas em {len(pedacos)} vistas ({sum(p['chars'] for p in pedacos) // 1000} mil caracteres) em {pasta.relative_to(RAIZ)}")
    return 0


ESTADO = PASTA / "auditoria" / "camada1-estado.jsonl"
BLOQUEADOS = {  # alteradores sem texto no acervo que, pelo sumário ou rótulo, dão nova redação a artigos
    "pt:dre:466238:por": "DL 35108: os DL 35590, 36095, 36430, 41105, 41321, 41401, 41723 e 42210 dão nova redação a artigos e só há PDF no acervo",
    "pt:dre:328440:por": "o alterador «Alterados os artºs 20º, 21º, 23º, 28º, 29º…» só tem metadados no acervo",
    "pt:dre:200261:por": "o alterador que muda o n.º 4 do art. 24.º só tem metadados no acervo",
}


def _resumo_cegas(linhas: list[dict]) -> str:
    diploma = next((x for x in linhas if "instrucoes_em_falta" in x), {})
    partes = []
    for a in linhas:
        if a.get("veredicto") in ("errado", "dúvida"):
            partes.append(f"{a['artigo']}: {a['veredicto']} ({str(a.get('motivo') or '')[:160]})")
    for i in diploma.get("instrucoes_em_falta") or []:
        partes.append(f"instrução em falta: {str(i)[:200]}")
    for k in ("artigos_em_falta", "artigos_a_mais"):
        if diploma.get(k):
            partes.append(f"{k}: {str(diploma[k])[:200]}")
    if diploma and not str(diploma.get("fora_dos_artigos")).lower().startswith("sem alter"):
        partes.append(f"fora dos artigos: {str(diploma.get('fora_dos_artigos'))[:200]}")
    return "; ".join(partes)


def estado() -> int:
    """`auditoria/camada1-estado.jsonl`: o estado final de cada diploma da onda 1, com o motivo e a prova."""
    itens = _jsonl(CAMADA1 / "onda-1.jsonl")
    triagem = {d["id"]: d for d in _jsonl(CAMADA1 / "triagem.jsonl")}
    juntados = {}
    for nome in ("juntados-completo.jsonl", "juntados-corrido.jsonl"):
        for j in _jsonl(PASTA / "llm" / nome):
            juntados[j["id"]] = j
    nossos = _nossos()
    ronda: dict[str, list[dict]] = {}
    for f in sorted((PASTA / "verificacao").glob(f"saida-piloto-{RONDA}-lote-*.jsonl")):
        for d in _jsonl(f):
            ronda.setdefault(d["id"], []).append(d)
    nada = {}
    for f in sorted((CAMADA1 / f"nada{_sufixo()}").glob("resposta-*.json")):
        for d in json.loads(f.read_text(encoding="utf-8")):
            nada[d["id"]] = d
    segunda = {}
    for f in sorted((CAMADA1 / f"segunda{_sufixo()}").glob("segunda-*.json")):
        for d in json.loads(f.read_text(encoding="utf-8")):
            segunda[d["id"]] = d
    anteriores = {e["id"]: e for e in _jsonl(ESTADO)} if RONDA != 115 and ESTADO.exists() else {}
    # barreira mecânica (texto_antigo.py): o corpo antigo que fica a seguir à nova redação ou a «(Revogado.)»
    import texto_antigo  # noqa: PLC0415
    mecanica = {}
    for f in sorted((PASTA / "verificacao").glob(f"entrada-piloto-{RONDA}-lote-*.jsonl")):
        for d in _jsonl(f):
            achados = texto_antigo.marcados(d.get("texto_original", ""), d.get("texto_consolidado", ""))
            if achados:
                mecanica[d["id"]] = achados
    linhas = []
    for item in itens:
        i = item["id"]
        if anteriores and i not in nossos:
            linhas.append(anteriores[i])
            continue
        e = {"id": i, "titulo": item["titulo"], "citado_por_vigentes": item["citado_por_vigentes"], "central": item["central"],
             "classe_inventario": item["classe"], "categoria": item["categoria"]}
        tri = triagem.get(i)
        if i in BLOQUEADOS:
            e |= {"estado": "sem_texto_do_alterador", "motivo": BLOQUEADOS[i], "prova": "camada1/triagem.jsonl"}
        elif i in ronda:
            linhas_r = ronda[i]
            diploma = next(x for x in linhas_r if "instrucoes_em_falta" in x)
            bom = (all(x["veredicto"] == "certo" for x in linhas_r if "veredicto" in x) and not diploma["instrucoes_em_falta"]
                   and not diploma["artigos_em_falta"] and not diploma["artigos_a_mais"]
                   and str(diploma["fora_dos_artigos"]).lower().startswith("sem alter"))
            justificadas = diploma.get("instrucoes_justificadas") or []
            if not bom:
                e |= {"estado": "recusado_as_cegas", "motivo": _resumo_cegas(linhas_r), "prova": f"verificacao/saida-piloto-{RONDA}-lote-*.jsonl"}
            elif i in mecanica:
                e |= {"estado": "recusado_na_verificacao_mecanica",
                      "motivo": "passou às cegas, mas o texto antigo ficou a seguir à nova redação ou a «(Revogado.)»: "
                      + "; ".join(f"art. {a['artigo']} («{a['exemplo'][:80]}»)" for a in mecanica[i])[:600],
                      "prova": "consolidacao/texto_antigo.py sobre verificacao/entrada-piloto-*.jsonl"}
            elif i not in segunda:
                e |= {"estado": "por_ver", "motivo": "passou às cegas; falta a segunda leitura"}
            elif segunda[i]["veredicto"] != "certo":
                e |= {"estado": "recusado_na_segunda_leitura", "motivo": "; ".join(segunda[i].get("problemas") or [])[:600],
                      "prova": f"camada1/segunda{_sufixo()}/segunda-*.json"}
            else:
                e |= {"estado": "aplicar", "motivo": f"certo às cegas e na segunda leitura; {len(justificadas)} instruções não aplicadas com motivo confirmado às cegas",
                      "nao_aplicadas": justificadas, "prova": f"verificacao/saida-piloto-{RONDA}-lote-*.jsonl; camada1/segunda{_sufixo()}/segunda-*.json"}
            if i in segunda and segunda[i].get("vigencia"):
                e["vigencia"] = segunda[i]["vigencia"]
        elif i in nossos and anteriores and juntados.get(i, {}).get("estado") == "aplicado com LLM":
            # tirado da entrada às cegas: a resposta desta ronda deu o mesmo texto que a ronda anterior já recusou
            a = anteriores[i]
            prefixo = f"a resposta da ronda {RONDA} deu o mesmo texto que a ronda anterior recusou; "
            e |= {"estado": a["estado"], "motivo": prefixo + str(a.get("motivo")).replace(prefixo, "")[:500],
                  "prova": a.get("prova")}
        elif i in nada:
            d = nada[i]
            if d.get("instrucoes_em_falta"):
                e |= {"estado": "recusado_as_cegas", "motivo": "a resposta não aplicou nada, mas o verificador viu instruções por aplicar: "
                      + "; ".join(str(x)[:200] for x in d["instrucoes_em_falta"]), "prova": f"camada1/nada{_sufixo()}/resposta-*.json"}
            else:
                e |= {"estado": "sem_alteracao_aplicavel", "motivo": "nada a aplicar, confirmado às cegas: "
                      + "; ".join(f"{x.get('instrucao')}: {x.get('motivo')}" for x in (d.get("instrucoes_justificadas") or []))[:800],
                      "prova": f"camada1/nada{_sufixo()}/resposta-*.json"}
        elif i in nossos and juntados.get(i, {}).get("estado") == "não junto":
            e |= {"estado": "resposta_recusada", "motivo": str(juntados[i].get("motivo"))[:600], "prova": "llm/juntados-*.jsonl"}
        elif tri is not None and tri["classe"] != "para_llm":
            motivos = {"sem_alteracao": "sem_alteracao_textual", "so_imagem": "so_em_imagem", "sem_texto": "sem_texto_do_alterador", "revogado": "revogado_por_inteiro"}
            e |= {"estado": motivos[tri["classe"]],
                  "motivo": "; ".join(f"{a['alterador']}: {a['veredicto']} ({a['motivo'][:120]})" for a in tri["alteradores"]
                                      if a["veredicto"] not in ("nao_menciona",))[:800] or "nenhum alterador menciona o original",
                  "prova": "camada1/triagem.jsonl"}
        else:
            e |= {"estado": "por_ver", "motivo": "sem resultado nesta onda"}
        if anteriores:
            e["ronda"] = RONDA
            e["estado_ronda_anterior"] = anteriores[i]["estado"]
        linhas.append(e)
    ESTADO.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    print(f"{len(linhas)} diplomas em {ESTADO.relative_to(RAIZ)}")
    for c, k in Counter(l["estado"] for l in linhas).most_common():
        print(f"{k:5d}  {c}")
    return 0


A_REPEDIR = ("recusado_as_cegas", "recusado_na_segunda_leitura", "resposta_recusada", "recusado_na_verificacao_mecanica")


def refazer_selecao() -> int:
    """Ronda 116: os recusados da onda 1 com a seleção refeita sobre o export de hoje, com as retificações
    (`corrected_by`) e as revogações (`repealed_by`) na lista de alteradores. A segunda leitura mostrou que
    eram estas que faltavam. Substitui as linhas destes diplomas em `selecao-escala.jsonl`, corre as
    regras (`consolidar.processar`) e substitui as linhas em `resultados-escala.jsonl`, na parte 7 e nos
    pendentes."""
    from selecionar import completar, selecionar_todos  # noqa: PLC0415

    ids = {e["id"] for e in _jsonl(ESTADO) if e["estado"] in A_REPEDIR}
    db = sqlite3.connect(f"file:{_export()}?mode=ro", uri=True)
    novos = {r["id"]: completar(r) | {"camada1": True, "selecao_refeita": "ronda 116"} for r in selecionar_todos(db, ids, com_revogacoes=True)}
    _trocar_selecao(novos)
    acrescentados = sum(len(novos[i]["alteradores"]) for i in novos)
    print(f"{len(novos)} seleções refeitas ({len(ids)} a repetir; {acrescentados} alteradores no total)")
    return 0


def _trocar_selecao(novos: dict[str, dict]) -> None:
    """Troca as linhas destes diplomas em `selecao-escala.jsonl`, corre as regras (`consolidar.processar`) e troca as
    linhas em `resultados-escala.jsonl`, na parte 7 e nos pendentes."""
    from consolidar import processar  # noqa: PLC0415

    linhas = [json.loads(l) for l in SELECAO_ESCALA.read_text(encoding="utf-8").splitlines() if l.strip()]
    trocadas = 0
    with SELECAO_ESCALA.open("w", encoding="utf-8") as f:
        for r in linhas:
            if r["id"] in novos:
                r = novos[r["id"]]
                trocadas += 1
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    estados = {i: processar(r) for i, r in novos.items()}
    for ficheiro in (PASTA / "resultados-escala.jsonl", PARTE):
        resultado = _jsonl(ficheiro)
        ja = {r["id"] for r in resultado}
        resultado = [({k: v for k, v in estados[r["id"]].items() if k != "pendentes"} | {"segundos": 0}) if r["id"] in estados else r for r in resultado]
        resultado += [{k: v for k, v in e.items() if k != "pendentes"} for i, e in estados.items() if i not in ja and ficheiro == PARTE]
        ficheiro.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in resultado), encoding="utf-8")
    pendentes = [p for p in _jsonl(PASTA / "pendentes-escala.jsonl") if p["id"] not in estados]
    for i, e in estados.items():
        if e.get("pendentes") and e["estado"] in ("para LLM", "falhou a verificação"):
            pendentes.append({"id": i, "title": e["title"], "itens": e["pendentes"]})
    (PASTA / "pendentes-escala.jsonl").write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in pendentes), encoding="utf-8")
    print(f"{trocadas} linhas trocadas na seleção; regras: {dict(Counter(e['estado'] for e in estados.values()))}")


def acrescentar_alteradores(ficheiro: Path) -> int:
    """Ronda 118: os alteradores que a segunda leitura achou no acervo e que não estavam na seleção (uma linha por par,
    `{"id": …, "alterador_path": "data/…", "motivo": …}`). Entram na lista de alteradores do diploma, pela data, e as
    regras correm de novo sobre a seleção nova."""
    selecao = {r["id"]: r for r in _jsonl(SELECAO_ESCALA)}
    novos: dict[str, dict] = {}
    for par in _jsonl(ficheiro):
        r = novos.get(par["id"]) or json.loads(json.dumps(selecao[par["id"]]))
        bruto = (RAIZ / par["alterador_path"]).read_text(encoding="utf-8")
        meta = front_matter(bruto)
        from texto import corpo  # noqa: PLC0415
        qualidade = meta.get("text_quality") or ("texto" if len(corpo(bruto).strip()) > 200 else None)
        r["alteradores"] = [x for x in r["alteradores"] if x["id"] != meta["id"]]
        tipo = str(meta.get("document_type") or "")
        a = {"id": meta["id"], "title": meta["title"], "path": par["alterador_path"], "text_quality": qualidade,
             "document_type": tipo, "legal_status": meta.get("legal_status"), "publication_date": str(meta.get("publication_date")),
             "rotulos_dre": [par["motivo"]], "datas_dre": [], "ordem": str(meta.get("publication_date"))}
        if "declara" in tipo.lower() or "retifica" in meta["title"].lower() or "rectifica" in meta["title"].lower():
            a["retificacao"] = True
        r["alteradores"] = sorted(r["alteradores"] + [a], key=lambda x: (x.get("ordem") or "", x["id"]))
        r["selecao_refeita"] = "ronda 118: alteradores da segunda leitura"
        novos[par["id"]] = r
    _trocar_selecao(novos)
    print(f"{len(novos)} diplomas com alteradores acrescentados")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("passo", choices=("onda", "selecao", "triagem", "entrada-triagem", "juntar-triagem", "pedidos", "encolher", "importar", "ronda", "acrescentar-iguais", "encolher-ronda", "entrada-nada", "estado", "refazer-selecao", "acrescentar-alteradores"))
    parser.add_argument("n", type=int)
    parser.add_argument("--ronda", type=int, default=115, choices=sorted(PASTAS_DA_RONDA))
    parser.add_argument("--pasta", default="pedidos", help="pedidos: a pasta em camada1/")
    parser.add_argument("--so-extra", action="store_true", help="pedidos: só os de --ids-extra")
    parser.add_argument("--ids-extra", type=Path, help="pedidos: mais estes ids (um por linha), p. ex. os que a triagem às cegas mandou para o LLM")
    args = parser.parse_args()
    global RONDA  # noqa: PLW0603
    RONDA = args.ronda
    CAMADA1.mkdir(exist_ok=True)
    ficheiro = CAMADA1 / f"onda-{args.n}.jsonl"
    if args.passo == "onda":
        itens = onda(args.n)
        ficheiro.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in itens), encoding="utf-8")
        print(f"{len(itens)} diplomas em {ficheiro.relative_to(RAIZ)}")
        for c, k in Counter(i["categoria"] for i in itens).most_common():
            print(f"{k:5d}  {c}")
        return 0
    if args.passo == "juntar-triagem":
        return juntar_triagem(args.n)
    if args.passo == "refazer-selecao":
        return refazer_selecao()
    if args.passo == "acrescentar-alteradores":
        return acrescentar_alteradores(args.ids_extra)
    if args.passo == "estado":
        return estado()
    if args.passo == "entrada-nada":
        return entrada_nada()
    if args.passo == "encolher-ronda":
        return encolher_ronda()
    if args.passo == "acrescentar-iguais":
        return acrescentar_iguais()
    if args.passo == "ronda":
        return ronda()
    if args.passo == "importar":
        return importar(list(PASTAS_DA_RONDA[RONDA]))
    if args.passo == "encolher":
        return encolher(args.pasta, 300_000)
    itens = _jsonl(ficheiro)
    if args.passo == "entrada-triagem":
        return entrada_triagem(itens, args.n)
    if args.passo == "pedidos":
        extra = args.ids_extra.read_text(encoding="utf-8").split() if args.ids_extra else []
        return pedidos_llm(itens, extra, args.pasta, args.so_extra)
    return selecao(itens) if args.passo == "selecao" else triagem(itens)


if __name__ == "__main__":
    sys.exit(main())
