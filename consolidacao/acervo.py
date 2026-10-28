"""Aplicação ao acervo dos consolidados verificados às cegas.

Para cada diploma verificado às cegas com todos os artigos `certo` (os aplicados por regra e os
juntados com o LLM, `llm/juntados.jsonl`), o registo em `data/` passa a ter o texto em vigor
(`piloto/<caminho>.md`), como os consolidados do DRE:

- o corpo é o consolidado, com as notas "> Alterado pelo/a …" nos artigos alterados;
- `version.kind` passa a `consolidated`, com um rótulo que diz que a consolidação é do
  leis-portugal e não tem valor oficial, e `consolidation_date` é a data em que a alteração
  entrou em vigor;
- ao lado fica `<registo>.versoes.json` com duas versões, a original e a alterada, para o
  `leis-portugal version-at` dar o texto em qualquer data.

Antes de gravar, confirma-se que o consolidado é o que foi verificado às cegas (a entrada da
última ronda em que o diploma esteve) e que o original em `data/` é o que a verificação
recebeu. Um diploma que falhe uma das duas fica como estava. Uma nova recolha do DRE não
substitui o consolidado, porque o texto publicado tem menos precedência
(`LegalRecord.precedence`); uma versão consolidada do próprio DRE substitui-o.

**Escala:** as rondas 6 em diante são lotes, `entrada-piloto-N-lote-NN.jsonl` com
`saida-piloto-N-lote-NN.jsonl` ao lado (uma ronda pode ter só alguns lotes verificados: os
diplomas dos lotes sem saída ficam por verificar, não se aplicam). Os diplomas vêm de
`resultados-escala.jsonl` e `selecao-escala.jsonl` e podem ter vários alteradores aplicados: a
versão alterada leva todos em `acts` (só os que deram instruções ao texto) e a data em que o
último entrou em vigor. O texto de cada passo intermédio não se guarda, por isso o histórico
tem duas versões, a original e a consolidada com todas as alterações.

`--dry-run` não grava nada e diz quantos passam em cada controlo. `--supor-verificados` (só com
`--dry-run`) conta os diplomas como se todos os artigos fossem `certo`, para ver quantos passariam
nos controlos técnicos (o consolidado é o da entrada, o original em `data/` é o verificado, o
histórico renderiza o consolidado) antes de haver saídas da verificação.

Uso: `python consolidacao/acervo.py [--dry-run [--supor-verificados]]`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from texto import RAIZ, corpo, front_matter

from leis_portugal.domain.history import HISTORY_SCHEMA, render_version, summarize
from leis_portugal.domain.record import Version
from leis_portugal.infrastructure.repository import Acervo


PASTA = RAIZ / "consolidacao"
VERIFICACAO = PASTA / "verificacao"


def rondas() -> list[tuple[Path, Path]]:
    """Os pares (entrada, saída) por ordem de ronda: o ficheiro único das rondas 1 a 5 e os lotes
    das seguintes. Uma entrada sem saída ao lado (lote ainda por verificar) fica no par com o
    caminho da saída que faltar."""
    pares = [(VERIFICACAO / "entrada-piloto.jsonl", VERIFICACAO / "saida-piloto.jsonl")]
    numeros = sorted({int(m.group(1)) for f in VERIFICACAO.glob("entrada-piloto-*.jsonl") if (m := re.match(r"entrada-piloto-(\d+)", f.name))})
    for n in numeros:
        unico = VERIFICACAO / f"entrada-piloto-{n}.jsonl"
        if unico.exists():
            pares.append((unico, VERIFICACAO / f"saida-piloto-{n}.jsonl"))
        for lote in sorted(VERIFICACAO.glob(f"entrada-piloto-{n}-lote-*.jsonl")):
            pares.append((lote, lote.with_name(lote.name.replace("entrada-", "saida-"))))
    return pares

# Os 24 com todos os artigos `certo` e o Decreto-Lei n.º 513-M/79, cuja `dúvida` (a revogação
# do artigo 19.º só produz efeitos com a entrada em vigor do Código dos Regimes Contributivos)
# se resolve com a data: a Lei n.º 110/2009 e o Código entraram em vigor a 2011-01-01, e as
# alterações posteriores ao artigo 5.º dela não tocam na alínea a). Ficam de fora o Decreto
# Legislativo Regional n.º 13/98/A e a Lei n.º 10/2012 (ver README, "Resultado da verificação
# às cegas").
DUVIDAS_RESOLVIDAS = {"pt:dre:430016:por"}
DE_FORA = {"pt:dre:431229:por", "pt:dre:542458:por"}

ROTULO = "Versão consolidada pelo leis-portugal, sem valor oficial: alterações aplicadas por regra e verificadas às cegas"
ROTULO_LLM = "Versão consolidada pelo leis-portugal, sem valor oficial: alterações aplicadas com um LLM e verificadas às cegas"
_NOTA_PILOTO = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*, publicado em \d{4}-\d{2}-\d{2}\.\n\n?", re.M)
_NOTA = re.compile(r"^> ((?:Alterado|Aditado|Revogado|Retificado) pelo/a .*)$", re.M)
_TITULO = re.compile(r"^#{1,6} ", re.M)
_OPERACAO = {"revogar": "Revoga", "aditar": "Adita", "retificar": "Retifica"}


def _sem_problemas(diploma: dict) -> bool:
    """A linha do diploma na saída da verificação: nada em falta nem a mais, e nada mudado fora
    dos artigos (o verificador escreve "sem alterações…" quando está bem)."""
    listas = ("instrucoes_em_falta", "artigos_em_falta", "artigos_a_mais")
    return not any(diploma.get(k) for k in listas) and str(diploma.get("fora_dos_artigos") or "").startswith("sem alterações")


def verificados(supor_certos: bool = False) -> dict[str, dict]:
    """A entrada da última ronda de cada diploma, se todos os artigos dessa ronda são `certo`
    (ou a dúvida está resolvida) e o diploma não tem problemas fora dos artigos. Um diploma cuja
    última entrada não tem saída (lote por verificar) não está verificado, mesmo que uma ronda
    anterior o tenha aprovado com outro texto. Com `supor_certos` (dry-run) conta-se como certo
    tudo o que não tem saída."""
    entradas: dict[str, dict] = {}
    vereditos: dict[str, set[str]] = {}
    for entrada, saida in rondas():
        ronda: dict[str, set[str]] = {}
        if saida.exists():
            for linha in saida.read_text(encoding="utf-8").splitlines():
                item = json.loads(linha)
                if "veredicto" in item:
                    ronda.setdefault(item["id"], set()).add(item["veredicto"])
                elif not _sem_problemas(item):
                    ronda.setdefault(item["id"], set()).add("problema no diploma")
        for linha in entrada.read_text(encoding="utf-8").splitlines():
            item = json.loads(linha)
            entradas[item["id"]] = item
            vereditos[item["id"]] = ronda.get(item["id"], {"certo"} if supor_certos and not saida.exists() else set())
        for id_, v in ronda.items():  # o que a saída traz e a entrada não tem (não deve haver)
            vereditos.setdefault(id_, v)
    return {
        id_: item for id_, item in entradas.items()
        if id_ not in DE_FORA and (vereditos.get(id_) == {"certo"} or id_ in DUVIDAS_RESOLVIDAS)
    }


def blocos(texto: str) -> list[str]:
    """O corpo sem o título `# …`, dividido nos títulos (artigos, capítulos, anexos)."""
    texto = re.sub(r"\A# [^\n]*\n+", "", texto.strip())
    partes = [0, *(m.start() for m in _TITULO.finditer(texto) if m.start())]
    return [texto[a:b].strip() for a, b in zip(partes, [*partes[1:], len(texto)], strict=True) if texto[a:b].strip()]


def historico(id_: str, titulo: str, original: str, consolidado: str, versoes: list[dict]) -> dict:
    fragmentos: dict[str, dict] = {}

    def chaves(texto: str, desde: str | None) -> list[str]:
        lista = []
        for bloco in blocos(texto):
            chave = hashlib.sha256(bloco.encode("utf-8")).hexdigest()[:16]
            fragmentos.setdefault(chave, {
                "fragment_id": None,
                "type": None,
                "heading": bloco.splitlines()[0].lstrip("#").strip() if bloco.startswith("#") else None,
                "in_force_from": desde if _NOTA.search(bloco) else None,
                "changed_by": _NOTA.findall(bloco),
                "markdown": bloco,
            })
            lista.append(chave)
        return lista

    primeira, segunda = versoes
    primeira["fragments"] = chaves(original, None)
    segunda["fragments"] = chaves(consolidado, segunda["date"])
    return {
        "schema": HISTORY_SCHEMA,
        "id": id_,
        "consolidated_url": None,
        "consolidated_by": "leis-portugal (consolidacao/, fase 2 do PLANO-RAG.md)",
        "source_lastmod": None,
        "versions": [primeira, segunda],
        "fragments": fragmentos,
    }


def _sem_titulo(texto: str) -> str:
    return re.sub(r"\A# [^\n]*\n+", "", texto.strip())


def em_vigor(metadados: dict) -> str:
    entrada = (metadados.get("entry_into_force") or {}).get("date")
    return entrada or (metadados.get("entry_into_force_dates") or [None])[0] or metadados["publication_date"]


def _lista(texto: Path) -> list[dict]:
    return [json.loads(l) for l in texto.read_text(encoding="utf-8").splitlines()]


def alteradores_aplicados(resultado: dict, registo_selecao: dict) -> list[dict]:
    """Os diplomas que alteram o texto e cujas instruções ficaram aplicadas, por ordem de
    aplicação: o `alterador` do piloto ou, na escala, os `passos` com alterações aplicadas."""
    if "alteradores" not in registo_selecao:
        return [registo_selecao["alterador"]]
    aplicados = {p["id"] for p in resultado.get("passos", []) if p.get("aplicadas")}
    return [a for a in registo_selecao["alteradores"] if a["id"] in aplicados]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--supor-verificados", action="store_true", help="com --dry-run: conta como `certo` os lotes sem saída")
    args = parser.parse_args()
    if args.supor_verificados and not args.dry_run:
        parser.error("--supor-verificados só com --dry-run")
    acervo = Acervo(RAIZ)
    resultados = {r["id"]: r for r in _lista(PASTA / "resultados.jsonl")}
    selecao = {r["id"]: r for r in _lista(PASTA / "selecao.jsonl")}
    for ficheiro, destino in (("resultados-escala.jsonl", resultados), ("selecao-escala.jsonl", selecao)):
        if (PASTA / ficheiro).exists():
            for r in _lista(PASTA / ficheiro):
                destino.setdefault(r["id"], r)  # o piloto, com o LLM, tem precedência
    juntados = {r["id"]: r for r in _lista(PASTA / "llm" / "juntados.jsonl")}
    for id_, juntado in juntados.items():
        if juntado["estado"] == "aplicado com LLM":
            resultados[id_] = resultados[id_] | {"estado": juntado["estado"], "consolidado": juntado["consolidado"]}
    hoje = date.today().isoformat()
    aplicados, ja_aplicados, recusados, fora = 0, 0, [], []
    verif = verificados(supor_certos=args.supor_verificados)
    sem_verificar = sum(
        1 for r in resultados.values() if r["estado"] in ("aplicado por regra", "aplicado com LLM") and r["id"] not in verif and r["id"] not in DE_FORA
    )
    for id_, entrada in sorted(verif.items(), key=lambda kv: resultados[kv[0]]["path"]):
        resultado = resultados[id_]
        if resultado["estado"] not in ("aplicado por regra", "aplicado com LLM"):
            # Ex.: as revogações condicionais do Decreto-Lei n.º 16/2013, que saíram dos aplicados,
            # ou os três que deixaram de se juntar com o LLM depois da 4.ª ronda.
            fora.append(f"{resultado['title']}: {resultado['estado']} ({resultado['motivo']})")
            continue
        piloto = RAIZ / resultado["consolidado"]
        consolidado = corpo(piloto.read_text(encoding="utf-8"))
        if _NOTA_PILOTO.sub("", consolidado) != entrada["texto_consolidado"]:
            recusados.append(f"{id_}: o consolidado mudou depois da verificação às cegas")
            continue
        caminho = RAIZ / resultado["path"]
        registo, original = acervo.read(caminho)
        rotulo = ROTULO_LLM if resultado["estado"] == "aplicado com LLM" else ROTULO
        if registo.version.label == rotulo and original.strip() == consolidado.strip():
            ja_aplicados += 1
            continue
        if registo.version.kind != "original" or original.strip() != entrada["texto_original"].strip():
            recusados.append(f"{id_}: o registo em data/ já não é o original verificado")
            continue

        alteradores = [(a, front_matter((RAIZ / a["path"]).read_text(encoding="utf-8"))) for a in alteradores_aplicados(resultado, selecao[id_])]
        if not alteradores:
            recusados.append(f"{id_}: nenhum alterador com alterações aplicadas")
            continue
        alteracoes = json.loads(piloto.with_name(piloto.name.replace(".md", ".alteracoes.json")).read_text(encoding="utf-8"))
        data_alteracao = max(em_vigor(meta) for _, meta in alteradores)
        versoes = [
            {"date": registo.publication_date, "future": registo.publication_date > hoje, "acts": [], "changes": []},
            {
                "date": data_alteracao,
                "future": data_alteracao > hoje,
                "acts": [{
                    "id": meta["id"],
                    "title": meta["title"],
                    "published": meta["publication_date"],
                    "dre_path": (meta.get("identifiers") or {}).get("dre_path"),
                } for _, meta in alteradores],
                "changes": [f"{_OPERACAO.get(a['operacao'], 'Altera')} Artigo {a['artigo']}" for a in alteracoes],
            },
        ]
        try:
            dados = historico(id_, registo.title, original, consolidado, versoes)
            # O título `# …` vem do registo, não do corpo (que pode ter outra capitalização).
            assert _sem_titulo(render_version(dados, dados["versions"][1], title=registo.title)) == _sem_titulo(consolidado).replace("\n\n\n", "\n\n")
        except AssertionError:
            recusados.append(f"{id_}: o histórico não reproduz o consolidado")
            continue
        titulos = "; ".join(meta["title"] for _, meta in alteradores)
        nome = acervo.history_path(caminho).name
        registo.version = Version(kind="consolidated", label=rotulo, language="por", consolidation_date=data_alteracao)
        registo.version_history = summarize(dados, nome)
        registo.provenance.notes = (
            f"Texto em vigor consolidado pelo leis-portugal com as alterações publicadas em: {titulos}. "
            f"Método e verificação: consolidacao/README.md e {piloto.with_name(piloto.name.replace('.md', '.alteracoes.json')).relative_to(RAIZ)}"
        )
        if not args.dry_run:
            acervo.save(registo, consolidado, target=caminho)
            acervo.write_history(caminho, dados)
        aplicados += 1
        print(f"{'(dry-run) ' if args.dry_run else ''}{resultado['path']}: {len(alteracoes)} alteração(ões) de {len(alteradores)} alterador(es) ({resultado['estado']}), em vigor desde {data_alteracao}")
    print(f"Aplicados: {aplicados}. Já aplicados: {ja_aplicados}. Recusados: {len(recusados)}. Verificados que já não estão aplicados: {len(fora)}. Consolidados por verificar: {sem_verificar}.")
    for linha in recusados + fora:
        print("  ", linha)
    return 1 if recusados else 0


if __name__ == "__main__":
    raise SystemExit(main())
