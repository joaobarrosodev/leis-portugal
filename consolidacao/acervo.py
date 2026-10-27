"""Aplicação ao acervo dos consolidados verificados às cegas.

Para cada diploma em `APLICAR`, o registo em `data/` passa a ter o texto em vigor
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

Uso: `python consolidacao/acervo.py [--dry-run]`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date

from texto import RAIZ, corpo, front_matter

from leis_portugal.domain.history import HISTORY_SCHEMA, render_version, summarize
from leis_portugal.domain.record import Version
from leis_portugal.infrastructure.repository import Acervo


PASTA = RAIZ / "consolidacao"
RONDAS = ("entrada-piloto.jsonl", "entrada-piloto-2.jsonl", "entrada-piloto-3.jsonl")
SAIDAS = ("saida-piloto.jsonl", "saida-piloto-2.jsonl", "saida-piloto-3.jsonl")

# Os 24 com todos os artigos `certo` e o Decreto-Lei n.º 513-M/79, cuja `dúvida` (a revogação
# do artigo 19.º só produz efeitos com a entrada em vigor do Código dos Regimes Contributivos)
# se resolve com a data: a Lei n.º 110/2009 e o Código entraram em vigor a 2011-01-01, e as
# alterações posteriores ao artigo 5.º dela não tocam na alínea a). Ficam de fora o Decreto
# Legislativo Regional n.º 13/98/A e a Lei n.º 10/2012 (ver README, "Resultado da verificação
# às cegas").
DUVIDAS_RESOLVIDAS = {"pt:dre:430016:por"}
DE_FORA = {"pt:dre:431229:por", "pt:dre:542458:por"}

ROTULO = "Versão consolidada pelo leis-portugal, sem valor oficial: alterações aplicadas por regra e verificadas às cegas"
_NOTA_PILOTO = re.compile(r"^> (?:Alterado|Aditado|Revogado|Retificado) pelo/a .*, publicado em \d{4}-\d{2}-\d{2}\.\n\n?", re.M)
_NOTA = re.compile(r"^> ((?:Alterado|Aditado|Revogado|Retificado) pelo/a .*)$", re.M)
_TITULO = re.compile(r"^#{1,6} ", re.M)
_OPERACAO = {"revogar": "Revoga", "aditar": "Adita", "retificar": "Retifica"}


def verificados() -> dict[str, dict]:
    """A entrada da última ronda de cada diploma, se todos os artigos dessa ronda são `certo`
    (ou a dúvida está resolvida)."""
    entradas: dict[str, dict] = {}
    vereditos: dict[str, set[str]] = {}
    for entrada, saida in zip(RONDAS, SAIDAS, strict=True):
        ronda = {}
        for linha in (PASTA / "verificacao" / saida).read_text(encoding="utf-8").splitlines():
            item = json.loads(linha)
            if "veredicto" in item:
                ronda.setdefault(item["id"], set()).add(item["veredicto"])
        vereditos |= ronda
        for linha in (PASTA / "verificacao" / entrada).read_text(encoding="utf-8").splitlines():
            item = json.loads(linha)
            entradas[item["id"]] = item
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


def em_vigor(metadados: dict) -> str:
    entrada = (metadados.get("entry_into_force") or {}).get("date")
    return entrada or (metadados.get("entry_into_force_dates") or [None])[0] or metadados["publication_date"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    acervo = Acervo(RAIZ)
    resultados = {r["id"]: r for r in map(json.loads, (PASTA / "resultados.jsonl").read_text(encoding="utf-8").splitlines())}
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}
    hoje = date.today().isoformat()
    aplicados, ja_aplicados, recusados, fora = 0, 0, [], []
    for id_, entrada in sorted(verificados().items(), key=lambda kv: resultados[kv[0]]["path"]):
        resultado = resultados[id_]
        if resultado["estado"] != "aplicado por regra":
            # Ex.: as revogações condicionais do Decreto-Lei n.º 16/2013, que saíram dos aplicados.
            fora.append(f"{resultado['title']}: {resultado['estado']} ({resultado['motivo']})")
            continue
        piloto = RAIZ / resultado["consolidado"]
        consolidado = corpo(piloto.read_text(encoding="utf-8"))
        if _NOTA_PILOTO.sub("", consolidado) != entrada["texto_consolidado"]:
            recusados.append(f"{id_}: o consolidado mudou depois da verificação às cegas")
            continue
        caminho = RAIZ / resultado["path"]
        registo, original = acervo.read(caminho)
        if registo.version.label == ROTULO and original.strip() == consolidado.strip():
            ja_aplicados += 1
            continue
        if registo.version.kind != "original" or original.strip() != entrada["texto_original"].strip():
            recusados.append(f"{id_}: o registo em data/ já não é o original verificado")
            continue

        alterador_meta = front_matter((RAIZ / selecao[id_]["alterador"]["path"]).read_text(encoding="utf-8"))
        alteracoes = json.loads(piloto.with_name(piloto.name.replace(".md", ".alteracoes.json")).read_text(encoding="utf-8"))
        data_alteracao = em_vigor(alterador_meta)
        versoes = [
            {"date": registo.publication_date, "future": registo.publication_date > hoje, "acts": [], "changes": []},
            {
                "date": data_alteracao,
                "future": data_alteracao > hoje,
                "acts": [{
                    "id": alterador_meta["id"],
                    "title": alterador_meta["title"],
                    "published": alterador_meta["publication_date"],
                    "dre_path": (alterador_meta.get("identifiers") or {}).get("dre_path"),
                }],
                "changes": [f"{_OPERACAO.get(a['operacao'], 'Altera')} Artigo {a['artigo']}" for a in alteracoes],
            },
        ]
        dados = historico(id_, registo.title, original, consolidado, versoes)
        assert render_version(dados, dados["versions"][1], title=registo.title).strip() == consolidado.strip().replace("\n\n\n", "\n\n")
        nome = acervo.history_path(caminho).name
        registo.version = Version(kind="consolidated", label=ROTULO, language="por", consolidation_date=data_alteracao)
        registo.version_history = summarize(dados, nome)
        registo.provenance.notes = (
            f"Texto em vigor consolidado pelo leis-portugal com as alterações publicadas em: {alterador_meta['title']}. "
            f"Método e verificação: consolidacao/README.md e {piloto.with_name(piloto.name.replace('.md', '.alteracoes.json')).relative_to(RAIZ)}"
        )
        if not args.dry_run:
            acervo.save(registo, consolidado, target=caminho)
            acervo.write_history(caminho, dados)
        aplicados += 1
        print(f"{'(dry-run) ' if args.dry_run else ''}{resultado['path']}: {len(alteracoes)} alteração(ões), em vigor desde {data_alteracao}")
    print(f"Aplicados: {aplicados}. Já aplicados: {ja_aplicados}. Recusados: {len(recusados)}. Verificados que já não são aplicados por regra: {len(fora)}.")
    for linha in recusados + fora:
        print("  ", linha)
    return 1 if recusados else 0


if __name__ == "__main__":
    raise SystemExit(main())
