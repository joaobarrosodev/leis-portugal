"""rag.avaliar: cada pergunta fica gravada e uma medição interrompida retoma onde parou."""

import json

import pytest
from rag import avaliar


PERGUNTAS = [{"id": f"p-{i}", "tipo": "literal", "pergunta": f"pergunta {i}", "data_referencia": "2026-01-01"} for i in range(5)]


@pytest.fixture
def medicao(tmp_path, monkeypatch):
    ficheiro = tmp_path / "perguntas.jsonl"
    ficheiro.write_text("".join(json.dumps(p) + "\n" for p in PERGUNTAS), encoding="utf-8")
    monkeypatch.setattr(avaliar, "RESULTADOS", tmp_path / "resultados")
    monkeypatch.setattr(avaliar, "Pesquisa", lambda *a, **k: None)
    monkeypatch.setattr(avaliar, "llm_disponivel", lambda: False)
    feitas: list[str] = []
    corte = {"em": None}

    def avaliar_pergunta(pesquisa, p, **kwargs):
        if p["id"] == corte["em"]:
            raise KeyboardInterrupt  # o corte de luz
        feitas.append(p["id"])
        return {"id": p["id"], "tipo": "literal", "posicao_artigo": 1, "posicao_texto": 1, "responde": True,
                "certa": True, "acerta_topo": True, "topo_reranker": None}

    monkeypatch.setattr(avaliar, "avaliar_pergunta", avaliar_pergunta)
    return ficheiro, tmp_path / "resultados", feitas, corte


def test_retoma_depois_de_um_corte(medicao):
    ficheiro, resultados, feitas, corte = medicao
    corte["em"] = "p-3"
    with pytest.raises(KeyboardInterrupt):
        avaliar.main(["--nome", "t", "--perguntas", str(ficheiro)])
    parcial = resultados / "privado" / "t-parcial.jsonl"
    assert len(parcial.read_text().splitlines()) == 1 + 3  # o cabeçalho e as 3 feitas
    with parcial.open("a") as f:
        f.write('{"id": "p-3", "tipo": "lit')  # a linha que ficou a meio

    corte["em"] = None
    feitas.clear()
    assert avaliar.main(["--nome", "t", "--perguntas", str(ficheiro)]) == 0
    assert feitas == ["p-3", "p-4"]
    detalhe = [json.loads(linha)["id"] for linha in (resultados / "privado" / "t-detalhe.jsonl").read_text().splitlines()]
    assert detalhe == [p["id"] for p in PERGUNTAS]
    assert json.loads((resultados / "t.json").read_text())["resumo"]["total"]["n"] == 5
    assert not parcial.exists()


def test_recomecar_ignora_o_parcial(medicao):
    ficheiro, _, feitas, corte = medicao
    corte["em"] = "p-2"
    with pytest.raises(KeyboardInterrupt):
        avaliar.main(["--nome", "t", "--perguntas", str(ficheiro)])
    corte["em"] = None
    feitas.clear()
    avaliar.main(["--nome", "t", "--perguntas", str(ficheiro), "--recomecar"])
    assert feitas == [p["id"] for p in PERGUNTAS]


def test_parcial_de_outra_medicao_nao_se_mistura(medicao):
    ficheiro, _, _, corte = medicao
    corte["em"] = "p-2"
    with pytest.raises(KeyboardInterrupt):
        avaliar.main(["--nome", "t", "--perguntas", str(ficheiro)])
    corte["em"] = None
    with pytest.raises(SystemExit, match="outra medição"):
        avaliar.main(["--nome", "t", "--perguntas", str(ficheiro), "--limiar", "3"])
