"""Quadros só em imagem transcritos do PDF do DR (`consolidacao/anexos.py`, `texto.com_anexos`)."""

import json
import sys
from pathlib import Path

import pytest


PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "anexos.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

import anexos  # noqa: E402
import texto  # noqa: E402
from pdf_colunas import palavras  # noqa: E402


PDF = "https://files.diariodarepublica.pt/1s/2002/11/269b00/73227324.pdf"
IMAGEM = f"[[(ver quadro no documento original)]({PDF})]({PDF})"


def _transcricao(tmp_path, monkeypatch, imagens_no_texto, trocas):
    monkeypatch.setattr(texto, "ANEXOS", tmp_path)
    dados = {"imagens_no_texto": imagens_no_texto, "transcricoes": [{"ocorrencia": n, "texto": t} for n, t in trocas]}
    (tmp_path / "pt_dre_1_por.json").write_text(json.dumps(dados), encoding="utf-8")


def test_troca_so_as_imagens_transcritas(tmp_path, monkeypatch):
    _transcricao(tmp_path, monkeypatch, 2, [(2, "| A | B |\n| --- | --- |\n| x | 1 |")])
    original = f"QUADRO N.º 1\n\n{IMAGEM}\n\nQUADRO N.º 2\n\n{IMAGEM}\n"
    novo = texto.com_anexos(original, "pt:dre:1:por")
    assert novo == f"QUADRO N.º 1\n\n{IMAGEM}\n\nQUADRO N.º 2\n\n| A | B |\n| --- | --- |\n| x | 1 |\n"


def test_numero_de_imagens_diferente_e_erro(tmp_path, monkeypatch):
    _transcricao(tmp_path, monkeypatch, 3, [(1, "| A |")])
    with pytest.raises(ValueError):
        texto.com_anexos(f"{IMAGEM}\n\n{IMAGEM}", "pt:dre:1:por")


def test_sem_transcricao_o_texto_fica_igual(tmp_path, monkeypatch):
    monkeypatch.setattr(texto, "ANEXOS", tmp_path)
    assert texto.com_anexos(IMAGEM, "pt:dre:2:por") == IMAGEM


def _letras(texto_, x, y=100.0, largura=5.0):
    return [(x + i * largura, y, x + (i + 1) * largura, y + 8, c) for i, c in enumerate(texto_)]


def test_palavras_tiram_os_pontos_de_guia():
    chs = _letras("Física", 45) + _letras(".......", 90, largura=3) + _letras("30", 343)
    assert [t for _, _, t in palavras(chs)] == ["Física", "30"]


def test_quadro_poe_cada_numero_na_sua_coluna(monkeypatch):
    linha1 = _letras("Laboratório", 45, 100) + _letras("1.osemestre", 267, 100) + _letras("20", 387, 100) + _letras("40", 430, 100)
    linha2 = _letras("Indústria Ali-", 45, 110) + _letras("1.osemestre", 267, 110) + _letras("30", 343, 110)
    linha3 = _letras("mentar.", 54, 120)
    monkeypatch.setattr(anexos, "caixas", lambda pdf, pagina: linha1 + linha2 + linha3)
    colunas = [["Unidade", 0], ["Tipo", 262], ["Teóricas", 320], ["Teórico-práticas", 365], ["Práticas", 415]]
    md = anexos.quadro(Path("x.pdf"), [{"pagina": 1, "de": 0, "ate": 200}], colunas).split("\n")
    assert md[2] == "| Laboratório | 1.º semestre |  | 20 | 40 |"
    assert md[3] == "| Indústria Alimentar. | 1.º semestre | 30 |  |  |"


def test_pontos_de_guia_colados_a_palavra_saem_e_o_ponto_final_fica():
    guia = _letras("virgem*.", 45) + _letras(". . . .", 90, largura=3) + _letras("60", 300)
    assert [t for _, _, t in palavras(guia)] == ["virgem*", "60"]
    final = _letras("Alimentar.", 45)
    assert [t for _, _, t in palavras(final)] == ["Alimentar."]


def test_corte_pelo_x_tira_a_coluna_do_lado(monkeypatch):
    esquerda = _letras("Azeite", 50, 100) + _letras("120", 250, 100)
    direita = _letras("Despacho", 320, 100)
    monkeypatch.setattr(anexos, "caixas", lambda pdf, pagina: esquerda + direita)
    md = anexos.quadro(Path("x.pdf"), [{"pagina": 1, "de": 0, "ate": 200, "x_ate": 300}], [["Produto", 0], ["Valor", 200]])
    assert md.split("\n")[2] == "| Azeite | 120 |"


def test_texto_corrido_e_numero_com_expoente(monkeypatch):
    linhas_ = _letras("QUADRO N.o 1 do", 45, 100) + _letras("plano", 45, 110) + _letras("1.o ano", 45, 140)
    monkeypatch.setattr(anexos, "caixas", lambda pdf, pagina: linhas_)
    texto_ = anexos.texto_corrido(Path("x.pdf"), [{"pagina": 1, "de": 0, "ate": 200}])
    assert texto_ == "QUADRO N.º 1 do plano\n\n1.º ano"


def test_refazer_confirma_e_apanha_diferencas(tmp_path, monkeypatch):
    import hashlib

    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"pdf")
    linha = _letras("Física", 45, 100) + _letras("30", 343, 100)
    monkeypatch.setattr(anexos, "caixas", lambda p, pagina: linha)
    monkeypatch.setattr(anexos, "ANEXOS", tmp_path)
    colunas = [["Unidade", 0], ["Horas", 300]]
    blocos = [{"tipo": "quadro", "partes": [{"pagina": 1, "de": 0, "ate": 200}]}]
    texto_ = anexos.quadro(pdf, blocos[0]["partes"], colunas)
    dados = {"pdf_sha256": hashlib.sha256(b"pdf").hexdigest(),
             "transcricoes": [{"ocorrencia": 1, "blocos": blocos, "colunas": colunas, "texto": texto_}]}
    (tmp_path / "pt_dre_1_por.json").write_text(json.dumps(dados), encoding="utf-8")
    assert anexos.refazer("pt:dre:1:por", pdf) == 0
    dados["transcricoes"][0]["texto"] = texto_.replace("30", "40")
    (tmp_path / "pt_dre_1_por.json").write_text(json.dumps(dados), encoding="utf-8")
    assert anexos.refazer("pt:dre:1:por", pdf) == 1
