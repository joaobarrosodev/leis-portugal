from __future__ import annotations

from pathlib import Path

from conftest import record_dict
from leis_portugal.domain.relations import eu_references
from leis_portugal.infrastructure.markdown import read_markdown_record, render_markdown
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.services.linking import link_eu_records, scan_portuguese_references
from leis_portugal.services.referenced import missing_references


def test_eu_references_and_transpositions():
    text = (
        "O presente decreto-lei transpõe para a ordem jurídica interna a Diretiva (UE) 2022/2555. "
        "Aplica-se o Regulamento (UE) 2016/679, o Regulamento (CE) n.º 1408/2013 e o Regulamento (CEE) n.º 1408/71. "
        "A Directiva n.º 89/391/CEE e a Decisão de Execução (UE) 2019/1234. "
        "Procede à transposição da Directiva 2004/49/CE e altera a Portaria n.º 1/2020."
    )
    assert eu_references(text) == {
        "32022L2555": "transposes",
        "32016R0679": "cites",
        "32013R1408": "cites",
        "31971R1408": "cites",
        "31989L0391": "cites",
        "32019D1234": "cites",
        "32004L0049": "transposes",
    }


def _write(root: Path, relative: str, metadata: dict, body: str = "# Texto") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(metadata, body), encoding="utf-8")
    return path


def test_link_writes_inverse_relations(repo_root: Path):
    _write(repo_root, "data/portugal/decretos-leis/2025/decreto-lei-1-2025.md", record_dict(
        "pt:dre:1:por",
        relationships=[
            {"type": "cites", "target": "celex:32022L2555", "label": None},
            {"type": "transposes", "target": "celex:32022L2555", "label": None},
            {"type": "cites", "target": "celex:32016R0679", "label": None},
        ],
    ))
    _write(repo_root, "data/regional/acores/decretos-legislativos-regionais/2025/x.md", record_dict(
        "pt:dre:2:por",
        relationships=[{"type": "cites", "target": "celex:32022L2555", "label": None}],
    ))
    eu_path = _write(repo_root, "data/european_union/directives/2022/diretiva-ue-2022-2555.md", record_dict(
        "eu:celex:32022L2555:por",
        identifiers={"celex": "32022L2555"},
        relationships=[
            {"type": "repeals", "target": "celex:32016L1148", "label": None},
            {"type": "cited_by", "target": "pt:dre:999:por", "label": None},
        ],
    ))

    acervo = Acervo(repo_root)
    references = scan_portuguese_references(acervo, workers=1)
    assert sorted(references["32022L2555"]) == [("pt:dre:1:por", "cites"), ("pt:dre:1:por", "transposes"), ("pt:dre:2:por", "cites")]
    # Em falta: o RGPD (citado pela lei portuguesa) e a diretiva revogada pela 2022/2555.
    assert set(missing_references(acervo, workers=1).celex) == {"32016R0679", "32016L1148"}

    summary = link_eu_records(acervo, workers=1)
    assert summary.updated == 1
    metadata, _ = read_markdown_record(eu_path)
    relations = {(item["type"], item["target"]) for item in metadata["relationships"]}
    assert relations == {
        ("repeals", "celex:32016L1148"),
        ("transposed_by", "pt:dre:1:por"),
        ("cited_by", "pt:dre:2:por"),
    }
    assert link_eu_records(acervo, workers=1).updated == 0
