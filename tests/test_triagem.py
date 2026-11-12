"""A alteração provável que as regras de leitura não veem (`consolidacao/consolidar.py`)."""

import sys
from pathlib import Path

import pytest

PASTA = Path(__file__).resolve().parents[1] / "consolidacao"
if not (PASTA / "consolidar.py").exists():
    pytest.skip("consolidacao/ não está nesta cópia", allow_module_level=True)
sys.path.insert(0, str(PASTA))

from consolidar import alteracao_provavel  # noqa: E402


def test_quadro_de_pessoal_alterado_pelo_quadro_anexo():
    texto = (
        "# Portaria n.º 975/84\n\nManda o Governo, ao abrigo do Decreto-Lei n.º 272/83 e do Decreto-Lei n.º 119/84, "
        "que o quadro de pessoal do Centro de Saúde Distrital do Porto, aprovado pela Portaria n.º 142/81, de 29 de Janeiro, "
        "seja alterado, na parte referente aos técnicos auxiliares sanitários, de acordo com o quadro anexo."
    )
    assert alteracao_provavel(texto, "Portaria n.º 142/81", "Portaria n.º 975/84")


def test_revogacao_com_o_verbo_antes_da_citacao():
    texto = "# Portaria n.º 18170\n\n1.º Seja considerada revogada, com a presente, a Portaria n.º 18092, de 2 de Dezembro de 1960."
    assert alteracao_provavel(texto, "Portaria n.º 18092", "Portaria n.º 18170")


def test_original_so_numa_lista_de_alteradores_de_outro():
    texto = (
        "# Portaria n.º 786/83\n\nManda o Governo que o quadro de pessoal da Direcção-Geral de Saúde, aprovado pela "
        "Portaria n.º 819/81, de 22 de Setembro, alterado pela Portaria n.º 1295/82, de 31 de Dezembro, seja alterado "
        "de acordo com o quadro anexo."
    )
    assert alteracao_provavel(texto, "Portaria n.º 1295/82", "Portaria n.º 786/83") is None
    assert alteracao_provavel(texto, "Portaria n.º 819/81", "Portaria n.º 786/83")


def test_habilitante_nao_e_o_alvo():
    texto = "# Portaria n.º 1/2000\n\nAo abrigo do Decreto-Lei n.º 202/2004, manda o Governo o seguinte: 1.º É revogada a Portaria n.º 664/2003."
    assert alteracao_provavel(texto, "Decreto-Lei n.º 202/2004", "Portaria n.º 1/2000") is None


def test_anexacao_a_zona_de_caca_fica_de_fora():
    texto = (
        "# Portaria n.º 33/2004\n\nManda o Governo o seguinte: 1.º São anexados à zona de caça associativa criada pela "
        "Portaria n.º 805/2001, de 20 de Julho, vários prédios rústicos, ficando a mesma com a área total de 900 ha."
    )
    assert alteracao_provavel(texto, "Portaria n.º 805/2001", "Portaria n.º 33/2004") is None
