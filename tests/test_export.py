"""Resolução das referências por ELI e exportação (JSONL, SQLite, Parquet)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from conftest import record_dict
from leis_portugal.cli import main
from leis_portugal.domain.relations import eli_key, valid_target
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.export import export_acervo, text_quality
from leis_portugal.services.linking import resolve_references


LAW_ELI = "https://data.dre.pt/eli/lei/7/2009/02/12/p/dre/pt/html"


def _write(root: Path, relative: str, record: dict, body: str = "# x") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(record, body), encoding="utf-8")
    return path


def _acervo(root: Path) -> dict[str, Path]:
    law = record_dict(
        "pt:dre:1:por", document_type="lei", official_number="7/2009", title="Lei n.º 7/2009",
        identifiers={"dre": "1", "eli": LAW_ELI, "internal": "pt:dre:1:por"}, subjects=["Trabalho"],
    )
    decree = record_dict("pt:dre:2:por", official_number="140/2009", title="Decreto-Lei n.º 140/2009")
    citing = record_dict(
        "pt:dre:3:por",
        title="Portaria n.º 1/2010",
        document_type="portaria",
        relationships=[
            {"type": "cites", "target": "eli:http://data.dre.pt/eli/lei/7/2009/02/12/p/dre", "label": None, "source": None},
            {"type": "cites", "target": "eli:h", "label": None, "source": "h"},
            {"type": "cites", "target": "eli:/application/external/tratado", "label": None, "source": None},
            {"type": "cites", "target": "eli:http://data.dre.pt/eli/lei/99/2000/01/01/p/dre", "label": None, "source": None},
            {"type": "cites", "target": "celex:32016R0679", "label": None, "source": None},
            {"type": "based_on", "target": "pt:numero:decreto-lei:140/2009", "label": None, "source": None},
            {"type": "amended_by", "target": "pt:dre:999:por", "label": "Alterado pela Portaria n.º 9/2011", "source": None, "date": "2011-01-01"},
        ],
    )
    gdpr = record_dict(
        "eu:celex:32016R0679:por", document_type="regulation", title="Regulamento (UE) 2016/679",
        identifiers={"celex": "32016R0679", "eli": "http://data.europa.eu/eli/reg/2016/679/oj", "internal": "eu:celex:32016R0679:por"},
    )
    without_text = record_dict("pt:dre:4:por", title="Resolução n.º 17/81", notes=["Fonte sem texto: o DRE não tem texto eletrónico nem PDF deste diploma; o registo tem só os metadados (verificado em 2026-10-23)."])
    return {
        "law": _write(root, "data/portugal/leis/2009/lei-7-2009.md", law, "# Lei\n\n###### Artigo 1.º\n\nTexto."),
        "decree": _write(root, "data/portugal/decretos-leis/2009/decreto-lei-140-2009.md", decree),
        "citing": _write(root, "data/portugal/portarias/2010/portaria-1-2010.md", citing),
        "gdpr": _write(root, "data/european_union/regulations/2016/regulamento-ue-2016-679.md", gdpr),
        "without_text": _write(root, "data/regional/acores/resolucoes/1981/resolucao-17-81.md", without_text, "# Resolução\n\n> só os metadados"),
    }


def test_valid_targets_and_eli_keys():
    for target in ("pt:dre:1:por", "eu:celex:32016R0679:por", "celex:11994NN01/05/F1A", "pt:numero:lei:7/2009", "eli:http://data.dre.pt/eli/lei/7/2009/p/dre"):
        assert valid_target(target), target
    for target in ("eli:h", "eli:http://", "eli:http:/", "eli:http:", "eli:/application/external/tratado", "pt:qualquer"):
        assert not valid_target(target), target
    assert eli_key(LAW_ELI) == eli_key("eli:http://data.dre.pt/eli/lei/7/2009/02/12/p/dre/") == "data.dre.pt/eli/lei/7/2009/02/12/p/dre"


def test_eli_of_a_consolidated_record_matches_the_publication_eli():
    from leis_portugal.domain.relations import EliIndex, eli_work_key

    consolidated = "https://data.dre.pt/eli/dec-lei/202/2004/p/cons/20241011/pt/html"
    assert eli_work_key(consolidated) == eli_work_key("eli:http://data.dre.pt/eli/dec-lei/202/2004/08/18/p/dre") == "dec-lei/202/2004"
    index = EliIndex([("pt:dre:480704:por", consolidated), ("pt:dre:1:por", "https://data.dre.pt/eli/port/1/2010/p/dre"),
                      ("pt:dre:2:por", "https://data.dre.pt/eli/port/1/2010/01/02/p/dre/pt/html")])
    assert index.get("eli:http://data.dre.pt/eli/dec-lei/202/2004/08/18/p/dre") == "pt:dre:480704:por"
    # Dois documentos com o mesmo tipo/número/ano (p. ex. nas duas séries): só o ELI exato serve.
    assert index.get("eli:http://data.dre.pt/eli/port/1/2010/03/03/p/dre") is None
    assert index.get("eli:http://data.dre.pt/eli/port/1/2010/p/dre") == "pt:dre:1:por"


def test_resolve_references_points_eli_to_acervo_ids_and_drops_broken_links(repo_root: Path):
    paths = _acervo(repo_root)
    summary = resolve_references(Acervo(repo_root), workers=1)
    assert (summary.checked, summary.resolved, summary.removed, summary.updated) == (1, 1, 2, 1)
    metadata, _ = read_markdown_record(paths["citing"])
    targets = {relation["target"]: relation for relation in metadata["relationships"]}
    assert targets["pt:dre:1:por"]["source"] == "http://data.dre.pt/eli/lei/7/2009/02/12/p/dre"
    assert "eli:http://data.dre.pt/eli/lei/99/2000/01/01/p/dre" in targets  # ainda não está no acervo
    assert not any(target in targets for target in ("eli:h", "eli:/application/external/tratado"))
    # Segunda passagem: nada a mudar.
    assert resolve_references(Acervo(repo_root), workers=1).updated == 0


def test_text_quality():
    assert text_quality({"notes": ["Fonte sem texto: … o registo tem só os metadados (…)"]}, "") == "metadados"
    assert text_quality({}, "> O texto deste diploma não está disponível em formato eletrónico. [Ver]") == "pdf"
    assert text_quality({}, "# Lei\n\nTexto") == "texto"


def test_export_writes_relationship_index_and_sqlite(repo_root: Path):
    _acervo(repo_root)
    summary = export_acervo(Acervo(repo_root), repo_root / "exports", formats=("jsonl", "sqlite"), workers=1)
    assert (summary.documents, summary.relations) == (5, 7)
    lines = [json.loads(line) for line in (repo_root / "exports" / "relationships.jsonl").read_text(encoding="utf-8").splitlines()]
    resolved = {line["target"]: line["target_id"] for line in lines}
    assert resolved["eli:http://data.dre.pt/eli/lei/7/2009/02/12/p/dre"] == "pt:dre:1:por"
    assert resolved["celex:32016R0679"] == "eu:celex:32016R0679:por"
    assert resolved["pt:numero:decreto-lei:140/2009"] == "pt:dre:2:por"
    assert resolved["pt:dre:999:por"] is None and resolved["eli:h"] is None
    assert set(lines[0]) == {"source_id", "type", "target", "target_id", "date", "label"}

    with sqlite3.connect(repo_root / "exports" / "leis-portugal.sqlite") as connection:
        # Sentido inverso: quem cita o RGPD?
        assert connection.execute("SELECT source_id FROM relacoes WHERE target_id = ?", ("eu:celex:32016R0679:por",)).fetchall() == [("pt:dre:3:por",)]
        row = connection.execute("SELECT subjects, text_quality, article_count FROM documentos WHERE id = 'pt:dre:1:por'").fetchone()
        assert json.loads(row[0]) == ["Trabalho"] and row[1] == "texto"
        assert connection.execute("SELECT text_quality FROM documentos WHERE id = 'pt:dre:4:por'").fetchone() == ("metadados",)


def test_export_parquet(repo_root: Path):
    pytest.importorskip("pyarrow")
    import pyarrow.parquet as pq

    _acervo(repo_root)
    export_acervo(Acervo(repo_root), repo_root / "exports", formats=("parquet",), workers=1)
    documents = pq.read_table(repo_root / "exports" / "documentos.parquet")
    relations = pq.read_table(repo_root / "exports" / "relacoes.parquet")
    assert documents.num_rows == 5 and relations.num_rows == 7
    assert documents.column("subjects").to_pylist().count(["Trabalho"]) == 1


def test_cli_export_and_link(repo_root: Path, capsys):
    _acervo(repo_root)
    assert main(["--root", str(repo_root), "link"]) == 0
    assert 'resolvidas: 1; "sem diploma" passadas a número: 0; ligações partidas removidas: 2' in capsys.readouterr().out
    assert main(["--root", str(repo_root), "export", "--format", "jsonl", "--format", "sqlite"]) == 0
    out = capsys.readouterr().out
    # Depois do link: menos 2 ligações partidas, mais o `cited_by` no RGPD.
    assert "Documentos: 5; relações: 6; com alvo no acervo: 4 (67%)" in out
    assert "Escrito: exports/relationships.jsonl" in out and "Escrito: exports/leis-portugal.sqlite" in out


def test_diploma_index_resolves_dre_eli_and_numbers_without_eli(repo_root: Path):
    from leis_portugal.domain.relations import DiplomaIndex, DiplomaKey, diploma_key, valid_target

    assert diploma_key("resolucao-conselho-ministros", "51/94", publication_date="1994-07-07", territory=None) == DiplomaKey(
        "resolucao-conselho-ministros", "51", "1994", "p"
    )
    assert diploma_key("decreto-legislativo-regional", "1/2005/A", publication_date="2005-05-09", territory="acores").region == "a"
    assert diploma_key("decreto-ministro-republica", "4/93, de 13 de Setembro", publication_date="1993-09-13", territory=None).year == "1993"
    assert not valid_target("eli:http://data.dre.pt/e") and not valid_target("eli:http://data.dre.pt/eli/ac")

    index = DiplomaIndex(Acervo(repo_root).types.eli_codes)
    for record_id, kind, number, published, territory, series in (
        ("pt:dre:10:por", "decreto-legislativo-regional", "1/2005/A", "2005-05-09", "acores", "I"),
        ("pt:dre:11:por", "decreto-legislativo-regional", "1/2005/M", "2005-02-18", "madeira", "I"),
        ("pt:dre:20:por", "portaria", "1/2010", "2010-01-04", None, "I"),
        ("pt:dre:21:por", "portaria", "1/2010", "2010-03-03", None, "II"),
        ("pt:dre:30:por", "resolucao-conselho-ministros", "1-B/95", "1995-01-11", None, "I"),
    ):
        index.add(record_id, diploma_key(kind, number, publication_date=published, territory=territory), publication_date=published, series=series)
    # A região do ELI separa os Açores da Madeira; a data separa as séries.
    assert index.from_eli("eli:http://data.dre.pt/eli/declegreg/1/2005/05/09/a/dre") == "pt:dre:10:por"
    assert index.from_eli("eli:http://data.dre.pt/eli/declegreg/1/2005/02/18/m/dre") == "pt:dre:11:por"
    assert index.from_eli("eli:http://data.dre.pt/eli/port/1/2010/03/03/p/dre") == "pt:dre:21:por"
    assert index.from_eli("eli:http://data.dre.pt/eli/resolconsmin/1-b/1995/01/11/p/dre") == "pt:dre:30:por"
    # Sem data, prevalece a 1.ª Série; tipos e números desconhecidos não resolvem.
    assert index.from_number("pt:numero:portaria:1/2010") == "pt:dre:20:por"
    assert index.from_number("pt:numero:decreto-legislativo-regional:1/2005/A") == "pt:dre:10:por"
    assert index.from_number("pt:numero:resolucao-conselho-ministros:1-B/95") == "pt:dre:30:por"
    assert index.from_eli("eli:http://data.dre.pt/eli/xpto/1/2010/01/04/p/dre") is None
    assert index.from_number("pt:numero:lei:99/2099") is None


def test_link_resolves_eli_of_records_without_eli(repo_root: Path):
    _acervo(repo_root)
    regional = record_dict(
        "pt:dre:50:por", jurisdiction="regional", territory="madeira", document_type="decreto-legislativo-regional",
        official_number="1/2009/M", publication_date="2009-01-12", title="Decreto Legislativo Regional n.º 1/2009/M",
    )
    _write(repo_root, "data/regional/madeira/decretos-legislativos-regionais/2009/decreto-legislativo-regional-1-2009-m.md", regional)
    citing = record_dict("pt:dre:51:por", relationships=[
        {"type": "cites", "target": "eli:http://data.dre.pt/eli/declegreg/1/2009/01/12/m/dre", "label": None, "source": None},
        {"type": "cites", "target": "eli:http://data.dre.pt/el", "label": None, "source": None},
    ])
    path = _write(repo_root, "data/portugal/decretos-leis/2010/decreto-lei-5-2010.md", citing)
    resolve_references(Acervo(repo_root), workers=1)
    metadata, _ = read_markdown_record(path)
    assert [relation["target"] for relation in metadata["relationships"]] == ["pt:dre:50:por"]


SEM_DIPLOMA = "https://diariodarepublica.pt/dr/analise-juridica/informacoes-gerais/sem-diploma/2000-1945608"


def test_acting_reference_reads_the_amending_act_from_old_notes():
    from leis_portugal.domain.relations import acting_reference

    assert acting_reference(
        "Alterado o art. 52º do Estatuto dos Benefícios Fiscais, aprovado pelo Dec Lei 215/89, de 01-Jul, "
        "rectificado pela presente declaração, pelo DEC LEI.189/90.08.06.1990.MF, DR.IS [132] de 08.06.1990\x00\x00"
    ) == "pt:numero:decreto-lei:189/90"
    assert acting_reference("RECTIFICADA PELA DECLARAÇÃO RECTIFICAÇÃO 80/93, DE 930420") == "pt:numero:declaracao-retificacao:80/93"
    assert acting_reference("Revogada pela PORTARIA NUMERO 12-A/91") == "pt:numero:portaria:12-A/91"
    assert acting_reference("Alterado pelo DLR 3/2001/A") == "pt:numero:decreto-legislativo-regional:3/2001/A"
    assert acting_reference("\x00") is None and acting_reference("pela presente declaração") is None


def test_sem_diploma_links_become_numbered_references_or_are_dropped(repo_root: Path):
    from leis_portugal.sources.dre.mapper import DreMapper

    mapper = DreMapper(Acervo(repo_root).types)
    relations = mapper.relationships({"162": {"InversasList": {"List": [
        {"DiplomaLegisId": "0", "LinkSitemapAnaliseJuridica": "/dr/analise-juridica/informacoes-gerais/sem-diploma/2000-1945608",
         "Texto": "Alterado pelo DEC LEI.189/90.08.06.1990\x00", "Data": "1990-06-08"},
        {"DiplomaLegisId": "0", "LinkSitemapAnaliseJuridica": "/dr/analise-juridica/informacoes-gerais/sem-diploma/2000-1945608",
         "Texto": "\x00"},
    ]}}})
    assert [(relation.type, relation.target, relation.source) for relation in relations] == [
        ("amended_by", "pt:numero:decreto-lei:189/90", None)
    ]

    path = _write(repo_root, "data/portugal/portarias/1989/portaria-1-89.md", record_dict("pt:dre:60:por", relationships=[
        {"type": "amended_by", "target": "pt:dre:1945608:por", "label": "Alterado pelo DEC LEI.189/90.08.06.1990\x00",
         "source": SEM_DIPLOMA, "date": "1990-06-08"},
        {"type": "cites", "target": "pt:dre:1945608:por", "label": "\x00", "source": SEM_DIPLOMA},
    ]))
    summary = resolve_references(Acervo(repo_root), workers=1)
    assert (summary.by_number, summary.removed) == (1, 1)
    metadata, _ = read_markdown_record(path)
    assert metadata["relationships"] == [{
        "type": "amended_by", "target": "pt:numero:decreto-lei:189/90", "label": "Alterado pelo DEC LEI.189/90.08.06.1990",
        "source": None, "date": "1990-06-08",
    }]
