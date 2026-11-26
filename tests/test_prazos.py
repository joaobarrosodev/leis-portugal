"""`rag.prazos`, com contas dos casos de `avaliacao/casos/` revistas à mão (as datas esperadas vêm da referência)."""

from __future__ import annotations

from datetime import date

import pytest
from rag import prazos
from rag.prazos import Conta, contar


def fim(*args, **kw) -> date:
    return contar(Conta("x", *args, **kw)).fim


def test_calendario():
    assert prazos.pascoa(2026) == date(2026, 4, 5) and prazos.pascoa(2027) == date(2027, 3, 28)
    f = prazos.feriados(2026)
    assert date(2026, 4, 3) in f and date(2026, 6, 4) in f and date(2026, 12, 8) in f  # Sexta-feira Santa, Corpo de Deus
    assert date(2026, 2, 17) not in f  # Carnaval não é feriado obrigatório
    assert prazos.ferias_judiciais(date(2026, 12, 22)) and prazos.ferias_judiciais(date(2027, 1, 3))
    assert not prazos.ferias_judiciais(date(2027, 1, 4)) and not prazos.ferias_judiciais(date(2026, 7, 15))
    assert prazos.ferias_judiciais(date(2026, 3, 29)) and prazos.ferias_judiciais(date(2026, 4, 6))  # Ramos a 2.ª de Páscoa
    assert not prazos.ferias_judiciais(date(2026, 4, 7))


def test_civil():
    # caso-arr-05: 10 dias da comunicação de 20/10/2026; 60 dias sobre 2/10/2026 acabam a 1/12 (feriado) e passam para 2/12
    assert fim(date(2026, 10, 20), 10) == date(2026, 10, 30)
    assert fim(date(2026, 10, 2), 60) == date(2026, 12, 2)
    # caso2-arr-02: 10 dias desde 15/10/2026 acabam num domingo e passam para segunda
    assert fim(date(2026, 10, 15), 10) == date(2026, 10, 26)
    # meses e anos acabam no dia correspondente; sem ele, no último dia do mês (CC 279.º, c))
    assert fim(date(2026, 3, 14), 3, "anos") == date(2029, 3, 14)
    assert fim(date(2026, 1, 31), 1, "meses") == date(2026, 2, 28)  # sem 31/2, o último dia do mês (sábado: fica)
    # 8 dias valem uma semana (CC 279.º, d))
    assert fim(date(2026, 11, 2), 8) == date(2026, 11, 9)


def test_civil_sabado_nao_transfere():
    assert date(2026, 2, 28).weekday() == 5
    assert fim(date(2026, 1, 28), 1, "meses") == date(2026, 2, 28)


def test_civil_em_juizo_passa_as_ferias():
    # caso-trab-08: 60 dias desde 31/10/2026 acabam a 30/12, em férias judiciais: a ação pode entrar a 4/01/2027
    assert fim(date(2026, 10, 31), 60, regime="civil_em_juizo") == date(2027, 1, 4)
    assert fim(date(2026, 10, 31), 60, regime="civil") == date(2026, 12, 30)


def test_processual_dilacao_e_urgente():
    # caso2-emp-01: anúncio a 2/10/2026, 5 de dilação + 30 dias, contínuos (processo urgente): 6/11/2026
    assert fim(date(2026, 10, 2), 30, regime="processual_urgente", dilacao=5) == date(2026, 11, 6)
    # caso2-trab-02: anúncio a 3/11/2026, o mesmo: 8/12 é feriado, passa para 9/12
    assert fim(date(2026, 11, 3), 30, regime="processual_urgente", dilacao=5) == date(2026, 12, 9)
    # caso2-emp-01: 6 meses desde o trânsito de 26/10/2026, sem suspensão por ser de 6 meses
    assert fim(date(2026, 10, 26), 6, "meses", regime="processual") == date(2027, 4, 26)


def test_processual_suspende_nas_ferias():
    # 10 dias desde 18/12/2026: 19, 20, 21 contam; 22/12 a 3/1 não; 4/1 a 10/1 contam 7: termina a 10/1/2027, domingo -> 11/1
    r = contar(Conta("x", date(2026, 12, 18), 10, regime="processual"))
    assert r.fim == date(2027, 1, 11) and any("férias judiciais" in p for p in r.passos)
    # urgente não suspende: 28/12/2026, segunda-feira
    assert fim(date(2026, 12, 18), 10, regime="processual_urgente") == date(2026, 12, 28)


def test_uteis():
    # caso2-trab-01: 5 dias úteis desde 3/11/2026 acabam a 10/11; 7 dias úteis depois de 10/11 acabam a 19/11
    assert fim(date(2026, 11, 3), 5, regime="uteis") == date(2026, 11, 10)
    assert fim(date(2026, 11, 10), 7, regime="uteis") == date(2026, 11, 19)
    # o 1/12 e o 8/12 não contam: 2, 3, 4, 7 e 9 de dezembro
    assert fim(date(2026, 11, 30), 5, regime="uteis") == date(2026, 12, 9)


def test_de_json_e_texto():
    c = prazos.de_json({"o_que": "Ação de impugnação", "inicio": "2026-10-31", "quantidade": "60", "unidade": "dias",
                        "regime": "civil_em_juizo", "artigo": "387.º CT"})
    assert c and c.quantidade == 60
    assert prazos.de_json({"inicio": "31/10/2026", "quantidade": 60, "regime": "civil"}) is None
    assert prazos.de_json({"inicio": "2026-10-31", "quantidade": 60, "regime": "outro"}) is None
    t = prazos.texto([contar(c)], date(2026, 11, 26))
    assert "termina a 04/01/2027, ainda não passou" in t and "férias judiciais" in t and prazos.AVISO in t


def test_erros():
    with pytest.raises(ValueError):
        contar(Conta("x", date(2026, 1, 1), 0))
    with pytest.raises(ValueError):
        contar(Conta("x", date(2026, 1, 1), 5, regime="nenhum"))
