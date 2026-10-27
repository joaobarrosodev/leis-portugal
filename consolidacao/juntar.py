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

Uso: `python consolidacao/juntar.py`.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from alteracoes import ler
from aplicar import Falha, Fonte, Registo, _bloco, _inserir, _reescrever, aplicar
from consolidar import PILOTO, _markdown
from texto import RAIZ, Artigo, com_titulos, dividir, front_matter, publicado
from verificar import _REVOGADO

PASTA = RAIZ / "consolidacao"
LLM = PASTA / "llm"
METODO = "piloto da fase 2 (consolidacao/consolidar.py e, pelo LLM, consolidacao/juntar.py), sem valor oficial"


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
    for novo in resposta["artigos"]:
        parte, _, numero = novo["chave"].rpartition("::")
        paragrafos = [p.strip() for p in novo["texto"].split("\n\n") if p.strip()]
        revogado = len(paragrafos) == 1 and bool(_REVOGADO.match(paragrafos[0]))
        artigo = consolidado.artigo(parte, numero)
        if artigo is not None and artigo.chave in tocados:
            return linha | {"estado": "não junto", "motivo": f"artigo {novo['chave']} alterado pelas regras e pelo LLM"}
        if artigo is not None:
            antes, operacao = "\n".join(artigo.linhas).strip(), "revogar" if revogado else "substituir"
            nota = f"> {'Revogado' if revogado else 'Alterado'} pelo/a {ligacao}, publicado em {fonte.data}."
            _reescrever(artigo, novo["epigrafe"], paragrafos, nota)
        else:
            antes, operacao = "", "aditar"
            nota = f"> Aditado pelo/a {ligacao}, publicado em {fonte.data}."
            artigo = Artigo(parte, numero, novo["epigrafe"], _bloco(numero, novo["epigrafe"], paragrafos, [nota], [""]))
            try:
                _inserir(consolidado, artigo)
            except Falha as erro:
                return linha | {"estado": "não junto", "motivo": f"artigo {novo['chave']}: {erro}"}
        registos.append(Registo(artigo.chave, operacao, "llm", antes, "\n".join(artigo.linhas).strip(), "", "", metodo="llm"))
        tocados.add(artigo.chave)

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


def main() -> int:
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}
    estados = {r["id"]: r for r in map(json.loads, (PASTA / "resultados.jsonl").read_text(encoding="utf-8").splitlines())}
    linhas = []
    for ficheiro in sorted(LLM.glob("pt_*.json")):
        resposta = json.loads(ficheiro.read_text(encoding="utf-8"))
        if resposta["problemas"] or not resposta["artigos"]:
            continue
        linhas.append(juntar(resposta, selecao[resposta["id"]], estados[resposta["id"]]))
    (LLM / "juntados.jsonl").write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")
    for estado in sorted({l["estado"] for l in linhas}):
        doestado = [l for l in linhas if l["estado"] == estado]
        print(f"{len(doestado):4d}  {estado}" + (f" ({sum('parcial' in l for l in doestado)} parciais)" if estado == "aplicado com LLM" else ""))
        for l in doestado:
            if "motivo" in l:
                print(f"        {l['title']}: {l['motivo']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
