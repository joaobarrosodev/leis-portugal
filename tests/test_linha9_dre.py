"""Linha 9 «dre» da camada 1 (ronda 125): a seleção sobre o texto do DRE (`camada1.linha_dre`, `camada1.selecao_dre`)
e o ramo do `acervo.py` que acrescenta uma versão ao histórico do DRE."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

from conftest import record_dict
from leis_portugal.domain.history import HISTORY_SCHEMA, render_version
from leis_portugal.domain.record import LegalRecord
from leis_portugal.infrastructure.repository import Acervo


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "camada1.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import acervo as acervo_mod  # noqa: E402
import camada1  # noqa: E402
import selecionar  # noqa: E402


ROTULO_DRE = "Versão consolidada pelo DRE"
TITULO = "Decreto-Lei n.º 1/2020"
ART1 = "###### Artigo 1.º — Objeto\n\nO presente decreto-lei cria o programa."
ART2 = "###### Artigo 2.º — Prazo\n\nO prazo é de 10 dias."
NOTA_DRE = "> Alterado pelo/a Artigo 3.º do/a [Decreto-Lei n.º 2/2020 - Diário da República](https://x/2), em vigor a partir de 2020-02-01"
ART1_DRE = f"{ART1}\n\n{NOTA_DRE}"
NOTA = "> Alterado pelo/a [Decreto-Lei n.º 5/2021](https://diariodarepublica.pt/dr/detalhe/decreto-lei/5-2021-200), publicado em 2021-03-01."
ART2_NOVO = f"###### Artigo 2.º — Prazo\n\nO prazo é de 20 dias.\n\n{NOTA}"


# --- acervo.py ------------------------------------------------------------------------------------


def _historico_do_dre() -> dict:
    return {
        "schema": HISTORY_SCHEMA,
        "id": "pt:dre:100:por",
        "consolidated_url": "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2020-1",
        "dre_path": "/dr/detalhe/decreto-lei/1-2020-100",
        "source_lastmod": "2024-06-25",
        "versions": [
            {"date": "2020-01-02", "future": False, "acts": [], "changes": [], "fragments": ["900", "901"]},
            {"date": "2020-02-01", "future": False, "acts": [{"id": "pt:dre:150:por", "title": "Decreto-Lei n.º 2/2020"}],
             "changes": ["Alteração Artigo 1.º"], "fragments": ["902", "901"],
             "acts_without_text_change": [{"id": "pt:dre:200:por", "title": "Decreto-Lei n.º 5/2021", "date": "2021-03-06"}]},
        ],
        "fragments": {
            "900": {"fragment_id": "1", "type": 11, "heading": "Artigo 1.º — Objeto", "in_force_from": None, "changed_by": [], "markdown": ART1},
            "901": {"fragment_id": "2", "type": 11, "heading": "Artigo 2.º — Prazo", "in_force_from": None, "changed_by": [], "markdown": ART2},
            "902": {"fragment_id": "3", "type": 11, "heading": "Artigo 1.º — Objeto", "in_force_from": "2020-02-01",
                    "changed_by": [NOTA_DRE[2:]], "markdown": ART1_DRE},
        },
    }


def test_historico_dre_acrescenta_uma_versao_e_deixa_as_do_dre():
    anterior = _historico_do_dre()
    original = f"# {TITULO}\n\n{ART1_DRE}\n\n{ART2}\n"
    consolidado = f"# {TITULO}\n\n{ART1_DRE}\n\n{ART2_NOVO}\n"
    versao = {"date": "2021-03-06", "future": False, "acts": [{"id": "pt:dre:200:por"}], "changes": ["Altera Artigo 2.º"]}
    dados = acervo_mod.historico_dre(anterior, original, consolidado, versao)
    assert anterior == _historico_do_dre()  # não muda o que recebe
    assert dados["versions"][:2] == anterior["versions"]
    assert {k: dados["fragments"][k] for k in anterior["fragments"]} == anterior["fragments"]
    nova = dados["versions"][-1]
    assert nova["date"] == "2021-03-06" and nova["acts"] == [{"id": "pt:dre:200:por"}]
    assert nova["fragments"][0] == "902"  # o artigo que não mudou é o fragmento do DRE
    novo = dados["fragments"][nova["fragments"][1]]
    assert novo["markdown"] == ART2_NOVO and novo["in_force_from"] == "2021-03-06" and novo["changed_by"] == [NOTA[2:]]
    assert render_version(dados, nova, title=TITULO) == consolidado
    assert render_version(dados, dados["versions"][1], title=TITULO) == original


def _jsonl(caminho: Path, linhas: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in linhas), encoding="utf-8")


@pytest.fixture
def raiz_dre(repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    """Um acervo com um registo do DRE (duas versões no histórico do DRE), um alterador posterior, a consolidação
    sobre o texto do DRE e a verificação às cegas toda `certo`."""
    acervo = Acervo(repo_root)
    dre = LegalRecord.from_dict(record_dict(
        "pt:dre:100:por", title=TITULO, official_number="1/2020", publication_date="2020-01-02",
        identifiers={"dre": "100", "internal": "pt:dre:100:por"},
        version={"kind": "consolidated", "label": ROTULO_DRE, "language": "por", "consolidation_date": "2020-02-01"},
    ))
    original = f"# {TITULO}\n\n{ART1_DRE}\n\n{ART2}"
    caminho = acervo.save(dre, original).path
    acervo.write_history(caminho, _historico_do_dre())
    alterador = LegalRecord.from_dict(record_dict(
        "pt:dre:200:por", title="Decreto-Lei n.º 5/2021", official_number="5/2021", publication_date="2021-03-01",
        entry_into_force_dates=["2021-03-06"], identifiers={"dre": "200", "internal": "pt:dre:200:por", "dre_path": "/dr/detalhe/decreto-lei/5-2021-200"},
    ))
    caminho_alt = acervo.save(alterador, "# Decreto-Lei n.º 5/2021\n\n###### Artigo 1.º\n\nO artigo 2.º passa a 20 dias.").path
    rel = str(caminho.relative_to(repo_root))
    pasta = repo_root / "consolidacao"
    piloto = pasta / "piloto" / caminho.relative_to(repo_root / "data")
    piloto.parent.mkdir(parents=True)
    consolidado = f"# {TITULO}\n\n{ART1_DRE}\n\n{ART2_NOVO}\n"
    piloto.write_text(consolidado, encoding="utf-8")
    piloto.with_name(piloto.name.replace(".md", ".alteracoes.json")).write_text(
        json.dumps([{"operacao": "alterar", "artigo": "2.º"}]), encoding="utf-8")
    _jsonl(pasta / "resultados.jsonl", [])
    _jsonl(pasta / "selecao.jsonl", [])
    _jsonl(pasta / "llm" / "juntados.jsonl", [])
    _jsonl(pasta / "resultados-escala.jsonl", [{
        "id": "pt:dre:100:por", "title": TITULO, "path": rel, "estado": "aplicado com LLM", "motivo": None,
        "consolidado": str(piloto.relative_to(repo_root)), "alteradores_ids": ["pt:dre:200:por"]}])
    _jsonl(pasta / "selecao-escala.jsonl", [{
        "id": "pt:dre:100:por", "title": TITULO, "path": rel, "text_quality": "texto",
        "alteradores": [{"id": "pt:dre:200:por", "title": "Decreto-Lei n.º 5/2021", "path": str(caminho_alt.relative_to(repo_root)),
                         "text_quality": "texto", "publication_date": "2021-03-01", "ordem": "2021-03-01"}]}])
    _jsonl(pasta / "verificacao" / "entrada-piloto.jsonl", [{
        "id": "pt:dre:100:por", "titulo": TITULO, "texto_original": original + "\n",
        "texto_consolidado": acervo_mod._NOTA_PILOTO.sub("", consolidado)}])
    _jsonl(pasta / "verificacao" / "saida-piloto.jsonl", [
        {"id": "pt:dre:100:por", "artigo": "2.º", "veredicto": "certo"},
        {"id": "pt:dre:100:por", "instrucoes_em_falta": [], "artigos_em_falta": [], "artigos_a_mais": [], "fora_dos_artigos": "sem alterações"}])
    monkeypatch.setattr(acervo_mod, "RAIZ", repo_root)
    monkeypatch.setattr(acervo_mod, "PASTA", pasta)
    monkeypatch.setattr(acervo_mod, "VERIFICACAO", pasta / "verificacao")
    monkeypatch.setattr(acervo_mod, "DE_FORA", set())
    monkeypatch.setattr(sys, "argv", ["acervo.py"])
    return {"acervo": acervo, "caminho": caminho, "consolidado": consolidado}


def test_acervo_acrescenta_a_versao_ao_historico_do_dre(raiz_dre: dict, capsys: pytest.CaptureFixture):
    acervo, caminho = raiz_dre["acervo"], raiz_dre["caminho"]
    assert acervo_mod.main() == 0
    assert "Aplicados: 1." in capsys.readouterr().out
    registo, corpo = acervo.read(caminho)
    assert corpo.strip() == raiz_dre["consolidado"].strip()
    assert registo.version.kind == "consolidated" and registo.version.label == acervo_mod.ROTULO_LLM
    assert str(registo.version.consolidation_date) == "2021-03-06"
    assert registo.version_history.count == 3 and registo.version_history.versions[-1].amending == "pt:dre:200:por"
    assert "sobre a versão consolidada pelo DRE de 2020-02-01" in registo.provenance.notes
    dados = acervo.read_history(caminho)
    assert dados["versions"][:2] == _historico_do_dre()["versions"]
    assert dados["dre_path"] == "/dr/detalhe/decreto-lei/1-2020-100"
    nova = dados["versions"][-1]
    assert nova["date"] == "2021-03-06" and [a["id"] for a in nova["acts"]] == ["pt:dre:200:por"]
    assert nova["changes"] == ["Altera Artigo 2.º"]
    assert render_version(dados, nova, title=TITULO).strip() == raiz_dre["consolidado"].strip()
    # outra corrida não muda nada: o registo já tem o consolidado e o nosso rótulo
    assert acervo_mod.main() == 0
    assert "Aplicados: 0. Já aplicados: 1." in capsys.readouterr().out
    assert len(acervo.read_history(caminho)["versions"]) == 3


def test_acervo_recusa_o_registo_do_dre_que_mudou(raiz_dre: dict, capsys: pytest.CaptureFixture):
    acervo, caminho = raiz_dre["acervo"], raiz_dre["caminho"]
    registo, corpo = acervo.read(caminho)
    acervo.save(registo, corpo.replace("10 dias", "15 dias"), target=caminho)
    assert acervo_mod.main() == 1
    assert "o registo em data/ já não é o original verificado" in capsys.readouterr().out
    registo, _ = acervo.read(caminho)
    assert registo.version.label == ROTULO_DRE
    assert len(acervo.read_history(caminho)["versions"]) == 2


def test_acervo_recusa_se_o_historico_do_dre_nao_reproduz_o_data(raiz_dre: dict, capsys: pytest.CaptureFixture):
    acervo, caminho = raiz_dre["acervo"], raiz_dre["caminho"]
    historico = _historico_do_dre()
    historico["versions"][-1]["fragments"] = ["900", "901"]
    acervo.write_history(caminho, historico)
    assert acervo_mod.main() == 1
    assert "a última versão do histórico do DRE não reproduz o texto do data/" in capsys.readouterr().out
    assert acervo.read(caminho)[0].version.label == ROTULO_DRE


# --- camada1.py: seleção -------------------------------------------------------------------------


def _registo_md(meta: dict) -> str:
    import yaml

    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n# Texto\n"


@pytest.fixture
def export_dre(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    raiz = tmp_path / "raiz"
    path = "data/portugal/decretos-leis/2014/decreto-lei-10-2014.md"
    (raiz / path).parent.mkdir(parents=True)
    (raiz / path).write_text(_registo_md({
        "id": "pt:dre:10:por", "title": "Decreto-Lei n.º 10/2014",
        "version": {"kind": "consolidated", "label": ROTULO_DRE, "language": "por", "consolidation_date": "2015-01-01"},
        "relationships": [
            {"type": "amended_by", "target": "pt:dre:11:por", "date": "2014-03-01"},
            {"type": "amended_by", "target": "pt:dre:12:por", "date": "2016-01-10"},
            {"type": "corrected_by", "target": "pt:dre:13:por", "date": "2016-02-01"},
            {"type": "corrected_by", "target": "pt:dre:14:por", "date": "2014-05-01"},
        ],
    }), encoding="utf-8")
    nosso = "data/portugal/decretos-leis/2014/decreto-lei-20-2014.md"
    (raiz / nosso).write_text(_registo_md({
        "id": "pt:dre:30:por", "title": "Decreto-Lei n.º 20/2014",
        "version": {"kind": "consolidated", "label": "Versão consolidada pelo leis-portugal, sem valor oficial", "consolidation_date": "2015-01-01"},
    }), encoding="utf-8")
    db_path = tmp_path / "export.sqlite"
    db = sqlite3.connect(db_path)
    db.execute("create table documentos (id, title, path, text_quality, document_type, legal_status, publication_date)")
    db.execute("create table relacoes (source_id, type, target, target_id, date, label)")
    db.executemany("insert into documentos values (?, ?, ?, ?, ?, ?, ?)", [
        ("pt:dre:10:por", "Decreto-Lei n.º 10/2014", path, "texto", "decreto-lei", "in_force", "2014-02-01"),
        ("pt:dre:30:por", "Decreto-Lei n.º 20/2014", nosso, "texto", "decreto-lei", "in_force", "2014-02-01"),
        ("pt:dre:11:por", "Decreto-Lei n.º 11/2014", "data/a.md", "texto", "decreto-lei", "in_force", "2014-03-01"),
        ("pt:dre:12:por", "Decreto-Lei n.º 12/2016", "data/b.md", "texto", "decreto-lei", "in_force", "2016-01-10"),
        ("pt:dre:13:por", "Declaração de Retificação n.º 3/2016", "data/c.md", "texto", "declaracao-retificacao", "unknown", "2016-02-01"),
    ])
    db.executemany("insert into relacoes values (?, ?, ?, ?, ?, ?)", [
        ("pt:dre:10:por", "amended_by", "pt:dre:11:por", "pt:dre:11:por", "2014-03-01", "Alterado o art. 1.º"),
        ("pt:dre:10:por", "amended_by", "pt:dre:12:por", "pt:dre:12:por", "2016-01-10", "Alterado o art. 2.º"),
        ("pt:dre:10:por", "repealed_by", "pt:dre:15:por", "pt:dre:15:por", "2017-01-01", "Revogado o art. 3.º"),
        ("pt:dre:20:por", "cites", "pt:dre:10:por", "pt:dre:10:por", None, None),
        ("pt:dre:20:por", "cites", "pt:dre:10:por", "pt:dre:10:por", None, None),
        ("pt:dre:21:por", "cites", "pt:dre:10:por", "pt:dre:10:por", None, None),
    ])
    db.commit()
    monkeypatch.setattr(camada1, "RAIZ", raiz)
    monkeypatch.setattr(selecionar, "RAIZ", raiz)
    item = {"id": "pt:dre:10:por", "titulo": "Decreto-Lei n.º 10/2014", "categoria": "linha_9_dre", "consolidado_ate": "2015-01-01",
            "alteradores_posteriores": [{"id": "pt:dre:12:por", "data": "2016-01-10", "titulo": "Decreto-Lei n.º 12/2016"}]}
    return {"raiz": raiz, "db": db, "db_path": db_path, "path": path, "nosso": nosso, "item": item}


def test_linha_dre_leva_so_os_alteradores_posteriores(export_dre: dict):
    linha = camada1.linha_dre(export_dre["item"], export_dre["db"], export_dre["path"])
    assert {k: linha[k] for k in ("id", "title", "path", "text_quality", "document_type", "legal_status", "publication_date")} == {
        "id": "pt:dre:10:por", "title": "Decreto-Lei n.º 10/2014", "path": export_dre["path"], "text_quality": "texto",
        "document_type": "decreto-lei", "legal_status": "in_force", "publication_date": "2014-02-01"}
    assert linha["citacoes"] == 2 and linha["republicado_por"] == [] and linha["camada1"] is True
    assert linha["consolidado_dre_ate"] == "2015-01-01"
    ids = [a["id"] for a in linha["alteradores"]]
    assert ids == ["pt:dre:13:por", "pt:dre:12:por", "pt:dre:15:por"] and linha["n_alteracoes"] == 3
    ret, alt, rev = linha["alteradores"]
    assert ret["retificacao"] is True and ret["ordem"] == "2015-01-01" and ret["path"] == "data/c.md"
    assert alt["rotulos_dre"] == ["Alterado o art. 2.º"] and alt["datas_dre"] == ["2016-01-10"] and alt["ordem"] == "2016-01-10"
    assert "retificacao" not in alt and "revogacao" not in alt
    assert rev == {"id": "pt:dre:15:por", "title": "pt:dre:15:por", "rotulos_dre": ["Revogado o art. 3.º"], "datas_dre": ["2017-01-01"],
                   "ordem": "2017-01-01", "revogacao": True}


def test_linha_dre_recusa_o_que_ja_nao_e_do_dre(export_dre: dict):
    item = export_dre["item"] | {"id": "pt:dre:30:por"}
    with pytest.raises(ValueError, match="já não é a versão consolidada pelo DRE"):
        camada1.linha_dre(item, export_dre["db"], export_dre["nosso"])


def test_selecao_dre_junta_a_selecao_resultados_e_ids(export_dre: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import consolidar

    pasta = tmp_path / "consolidacao"
    cam = pasta / "camada1"
    item = export_dre["item"]
    _jsonl(cam / "onda-2.jsonl", [
        item,
        item | {"id": "pt:dre:30:por", "titulo": "Decreto-Lei n.º 20/2014"},
        item | {"id": "pt:dre:40:por", "categoria": "linha_9_nosso"},
        item | {"id": "pt:dre:41:por", "alteradores_posteriores": []},
    ])
    _jsonl(pasta / "selecao-escala.jsonl", [{"id": "pt:dre:1:por", "title": "outro"}])
    _jsonl(pasta / "resultados-escala.jsonl", [{"id": "pt:dre:1:por", "estado": "aplicado por regra"}])
    _jsonl(pasta / "resultados-escala.parte-7.jsonl", [])
    _jsonl(pasta / "pendentes-escala.jsonl", [])

    def processar(registo: dict, escrever: bool = True, extra: dict | None = None) -> dict:
        if extra is not None:
            extra["consolidado"] = object()
        return {"id": registo["id"], "title": registo["title"], "path": registo["path"], "citacoes": registo["citacoes"],
                "estado": "para LLM", "pendentes": [{"motivo": "alteração provável"}]}

    monkeypatch.setattr(consolidar, "processar", processar)
    monkeypatch.setattr(camada1, "PASTA", pasta)
    monkeypatch.setattr(camada1, "CAMADA1", cam)
    monkeypatch.setattr(camada1, "SELECAO_ESCALA", pasta / "selecao-escala.jsonl")
    monkeypatch.setattr(camada1, "PARTE", pasta / "resultados-escala.parte-7.jsonl")
    monkeypatch.setattr(camada1, "_export", lambda: export_dre["db_path"])
    paths = {"pt:dre:10:por": export_dre["path"], "pt:dre:30:por": export_dre["nosso"]}
    monkeypatch.setattr(camada1, "_path_de", paths.get)
    assert camada1.selecao_dre() == 0
    selecao = camada1._jsonl(pasta / "selecao-escala.jsonl")
    assert [r["id"] for r in selecao] == ["pt:dre:1:por", "pt:dre:10:por"]
    assert [a["id"] for a in selecao[1]["alteradores"]] == ["pt:dre:13:por", "pt:dre:12:por", "pt:dre:15:por"]
    resultados = camada1._jsonl(pasta / "resultados-escala.jsonl")
    assert [(r["id"], r["estado"]) for r in resultados] == [("pt:dre:1:por", "aplicado por regra"), ("pt:dre:10:por", "para LLM")]
    assert "pendentes" not in resultados[1]
    assert [r["id"] for r in camada1._jsonl(pasta / "resultados-escala.parte-7.jsonl")] == ["pt:dre:10:por"]
    assert [p["id"] for p in camada1._jsonl(pasta / "pendentes-escala.jsonl")] == ["pt:dre:10:por"]
    assert (cam / "ids-125.txt").read_text(encoding="utf-8") == "pt:dre:10:por\n"
    fora = camada1._jsonl(cam / "ronda-125-de-fora.jsonl")
    assert [d["id"] for d in fora] == ["pt:dre:30:por"] and "já não é a versão consolidada pelo DRE" in fora[0]["motivo"]
    # de novo: a linha da seleção troca-se, não se repete
    assert camada1.selecao_dre() == 0
    assert [r["id"] for r in camada1._jsonl(pasta / "selecao-escala.jsonl")] == ["pt:dre:1:por", "pt:dre:10:por"]
    assert [r["id"] for r in camada1._jsonl(pasta / "resultados-escala.jsonl")] == ["pt:dre:1:por", "pt:dre:10:por"]
