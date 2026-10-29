"""Junta ao original as respostas do LLM aprovadas no `llm.py --importar`.

Uma resposta aprovada (sem problemas na verificação letra a letra e com artigos) dá a nova
redação dos artigos que as regras não aplicaram. O consolidado é o original (com os títulos de
`texto.com_titulos` quando estão em texto corrido), com:

- as instruções que as regras aplicaram, quando o diploma ficou para o LLM só em parte (as
  outras foram para o LLM); quando falhou a verificação, o LLM fez todas e as regras não
  entram;
- os artigos da resposta: reescritos no lugar quando existem no original, aditados por ordem
  quando não existem, com a nota "> Alterado/Revogado/Aditado pelo/a …".

Não se junta, e fica com o motivo em `llm/juntados.jsonl`:

- o original sem artigos (portarias "1.º, 2.º" em texto corrido, bases): os artigos da
  resposta não têm onde encaixar sem inventar títulos;
- um artigo da resposta que as regras já tinham alterado;
- um artigo aditado sem lugar (ver `aplicar._inserir`).

Escreve `piloto/<caminho>.md` e `.alteracoes.json`, como o `consolidar.py`, e
`llm/juntados.jsonl`, que o `cegas.py` lê para a verificação às cegas. Quando a resposta deixou
uma instrução por aplicar (`nao_aplicavel`), a linha diz `parcial` com o motivo. Nada em
`data/` é alterado.

**Escala (`--escala`):** lê as respostas de `llm/escala/` (o `llm.py --escala --importar` grava ali,
para não tocar nas do piloto) e escreve `llm/juntados-escala.jsonl`. Parte do consolidado que as
regras deixaram (`consolidar.processar` com `extra`: com vários alteradores, o texto depois dos
que se aplicaram), junta-lhe os artigos da resposta e recusa os que as regras já tinham alterado.
Os 52 diplomas do piloto com `llm/juntados.jsonl` ficam como estão.

Uso: `python consolidacao/juntar.py [--escala]`.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from alteracoes import ler
from aplicar import Falha, Fonte, Registo, _bloco, _inserir, _reescrever, aplicar
from consolidar import PILOTO, _markdown, processar
from texto import RAIZ, Artigo, com_titulos, dividir, front_matter, publicado
from verificar import _REVOGADO

PASTA = RAIZ / "consolidacao"
LLM = PASTA / "llm"
METODO = "piloto da fase 2 (consolidacao/consolidar.py e, pelo LLM, consolidacao/juntar.py), sem valor oficial"


def _aplicar_resposta(resposta: dict, consolidado, tocados: set[str], ligacao: str, data: str, registo: dict):
    """Os artigos da resposta no consolidado. Devolve (registos, motivo): o motivo diz porque não
    se junta."""
    registos: list[Registo] = []
    for novo in resposta["artigos"]:
        parte, _, numero = novo["chave"].rpartition("::")
        paragrafos = [p.strip() for p in novo["texto"].split("\n\n") if p.strip()]
        revogado = len(paragrafos) == 1 and bool(_REVOGADO.match(paragrafos[0]))
        artigo = consolidado.artigo(parte, numero)
        if artigo is not None and artigo.chave in tocados:
            return registos, f"artigo {novo['chave']} alterado pelas regras e pelo LLM"
        if artigo is not None:
            antes, operacao = "\n".join(artigo.linhas).strip(), "revogar" if revogado else "substituir"
            nota = f"> {'Revogado' if revogado else 'Alterado'} pelo/a {ligacao}, publicado em {data}."
            _reescrever(artigo, novo["epigrafe"], paragrafos, nota)
        else:
            antes, operacao = "", "aditar"
            nota = f"> Aditado pelo/a {ligacao}, publicado em {data}."
            artigo = Artigo(parte, numero, novo["epigrafe"], _bloco(numero, novo["epigrafe"], paragrafos, [nota], [""]))
            try:
                _inserir(consolidado, artigo)
            except Falha as erro:
                return registos, f"artigo {novo['chave']}: {erro}"
        registos.append(Registo(artigo.chave, operacao, "llm", antes, "\n".join(artigo.linhas).strip(), "", "", metodo="llm"))
        tocados.add(artigo.chave)
    return registos, None


def juntar(resposta: dict, registo: dict, estado: dict) -> dict:
    linha = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "estado_regras": estado["estado"]}
    texto_original = publicado(RAIZ / registo["path"])
    original = dividir(texto_original)
    normalizados = False
    if not original.artigos and (normalizado := com_titulos(texto_original)) is not None:
        texto_original, original, normalizados = normalizado, dividir(normalizado), True
    if not original.artigos:
        return linha | {"estado": "não junto", "motivo": "original sem artigos: a resposta não tem onde encaixar"}

    alterador = registo["alterador"]
    meta = front_matter((RAIZ / alterador["path"]).read_text(encoding="utf-8"))
    fonte = Fonte(alterador["title"], (meta.get("source") or {}).get("official_url") or "", alterador.get("publication_date") or "")
    consolidado = dividir(texto_original)
    registos: list[Registo] = []
    tocados: set[str] = set()
    if estado["estado"] == "para LLM" and estado.get("aplicadas"):
        # As instruções que as regras aplicaram; as que falharam foram para o LLM.
        leitura = ler(publicado(RAIZ / alterador["path"]), registo["title"], original)
        resultado = aplicar(consolidado, leitura.instrucoes, fonte)
        registos, tocados = resultado.registos, resultado.tocados

    ligacao = f"[{fonte.titulo}]({fonte.url})" if fonte.url else fonte.titulo
    do_llm, erro = _aplicar_resposta(resposta, consolidado, tocados, ligacao, fonte.data, registo)
    if erro:
        return linha | {"estado": "não junto", "motivo": erro}
    registos += do_llm

    destino = PILOTO / Path(registo["path"]).relative_to("data")
    destino.parent.mkdir(parents=True, exist_ok=True)
    json_registos = [asdict(r) | {"diploma": registo["id"], "alterador": alterador["id"]} for r in registos]
    destino.with_suffix(".alteracoes.json").write_text(json.dumps(json_registos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    destino.write_text(_markdown(registo, alterador, consolidado, normalizados, METODO), encoding="utf-8")
    linha |= {"estado": "aplicado com LLM", "consolidado": str(destino.relative_to(RAIZ)),
              "artigos_llm": len(resposta["artigos"]), "artigos_regras": len(registos) - len(resposta["artigos"])}
    if normalizados:
        linha["titulos_normalizados"] = True
    if resposta.get("nao_aplicavel"):
        linha["parcial"] = resposta["nao_aplicavel"]
    return linha


def juntar_escala(resposta: dict, registo: dict, estado: dict, pendentes: dict) -> dict:
    """Como `juntar`, para um diploma da escala: parte do consolidado que as regras deixaram
    (`consolidar.processar` com `extra`) e junta-lhe os artigos da resposta. Os alteradores da
    nota são os dos pendentes, ou seja, os que o LLM tratou."""
    linha = {"id": registo["id"], "title": registo["title"], "path": registo["path"], "estado_regras": estado["estado"]}
    if registo["id"] in _juntados_no_piloto():
        return linha | {"estado": "não junto", "motivo": "já juntado com o LLM no piloto (llm/juntados.jsonl)"}
    extra: dict = {}
    processar(registo, escrever=False, extra=extra)
    consolidado = extra.get("consolidado")
    if consolidado is None or not consolidado.artigos:
        return linha | {"estado": "não junto", "motivo": "original sem artigos: a resposta não tem onde encaixar"}
    por_titulo = {a.get("title") or a["id"]: a for a in registo["alteradores"]}
    do_llm = sorted({item["alterador"] for item in pendentes["itens"]}, key=lambda t: por_titulo[t]["ordem"] if t in por_titulo else "")
    alteradores = [por_titulo[t] for t in do_llm if t in por_titulo]
    ligacoes = []
    for a in alteradores:
        url = (front_matter((RAIZ / a["path"]).read_text(encoding="utf-8")).get("source") or {}).get("official_url") or ""
        ligacoes.append(f"[{a['title']}]({url})" if url else a["title"])
    data = max((a.get("publication_date") or "" for a in alteradores), default="")
    tocados = set(extra["tocados"])
    registos_llm, erro = _aplicar_resposta(resposta, consolidado, tocados, " e ".join(ligacoes), data, registo)
    if erro:
        return linha | {"estado": "não junto", "motivo": erro}

    aplicados = extra["aplicados"] + [{"id": a["id"], "title": a["title"], "publication_date": a.get("publication_date")} for a in alteradores]
    destino = PILOTO / Path(registo["path"]).relative_to("data")
    destino.parent.mkdir(parents=True, exist_ok=True)
    json_registos = extra["registos"] + [asdict(r) | {"diploma": registo["id"], "alterador": ";".join(a["id"] for a in alteradores)} for r in registos_llm]
    destino.with_suffix(".alteracoes.json").write_text(json.dumps(json_registos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    destino.write_text(_markdown(registo, aplicados, consolidado, extra["titulos_normalizados"], METODO), encoding="utf-8")
    linha |= {"estado": "aplicado com LLM", "consolidado": str(destino.relative_to(RAIZ)), "artigos_llm": len(resposta["artigos"]),
              "artigos_regras": len(extra["registos"]), "alteradores_ids": [a["id"] for a in aplicados]}
    if extra["titulos_normalizados"]:
        linha["titulos_normalizados"] = True
    if resposta.get("nao_aplicavel"):
        linha["parcial"] = resposta["nao_aplicavel"]
    return linha


def _juntados_no_piloto() -> set[str]:
    ficheiro = LLM / "juntados.jsonl"
    if not ficheiro.exists():
        return set()
    return {j["id"] for j in map(json.loads, ficheiro.read_text(encoding="utf-8").splitlines()) if j["estado"] == "aplicado com LLM"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--escala", action="store_true", help="respostas de llm/escala/ sobre selecao-escala.jsonl")
    args = parser.parse_args()
    if args.escala:
        selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao-escala.jsonl").read_text(encoding="utf-8").splitlines())}
        estados = {r["id"]: r for r in map(json.loads, (PASTA / "resultados-escala.jsonl").read_text(encoding="utf-8").splitlines())}
        pendentes = {r["id"]: r for r in map(json.loads, (PASTA / "pendentes-escala.jsonl").read_text(encoding="utf-8").splitlines())}
        ficheiros, saida = sorted((LLM / "escala").glob("pt_*.json")), LLM / "juntados-escala.jsonl"
    else:
        selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}
        estados = {r["id"]: r for r in map(json.loads, (PASTA / "resultados.jsonl").read_text(encoding="utf-8").splitlines())}
        ficheiros, saida = sorted(LLM.glob("pt_*.json")), LLM / "juntados.jsonl"
    linhas = []
    for ficheiro in ficheiros:
        resposta = json.loads(ficheiro.read_text(encoding="utf-8"))
        if resposta["problemas"] or not resposta["artigos"]:
            continue
        if args.escala:
            linhas.append(juntar_escala(resposta, selecao[resposta["id"]], estados[resposta["id"]], pendentes[resposta["id"]]))
        else:
            linhas.append(juntar(resposta, selecao[resposta["id"]], estados[resposta["id"]]))
    saida.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    for estado in sorted({l["estado"] for l in linhas}):
        doestado = [l for l in linhas if l["estado"] == estado]
        print(f"{len(doestado):4d}  {estado}" + (f" ({sum('parcial' in l for l in doestado)} parciais)" if estado == "aplicado com LLM" else ""))
        for l in doestado:
            if "motivo" in l:
                print(f"        {l['title']}: {l['motivo']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
