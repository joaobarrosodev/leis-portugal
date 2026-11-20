"""rag.comparar: ganhos e perdas face à base, pergunta a pergunta, e as contas com outro limiar."""

import json

from rag import comparar


def _linha(id_, tipo="real", posicao=1, responde=True, certa=True, nota=5.0, motivo=""):
    return {"id": id_, "tipo": tipo, "posicao_artigo": posicao, "responde": responde, "certa": certa,
            "acerta_topo": posicao == 1, "topo_reranker": nota, "motivo": motivo}


def _medicao(resultados, nome, linhas, **configuracao):
    (resultados / "privado").mkdir(parents=True, exist_ok=True)
    (resultados / f"{nome}.json").write_text(json.dumps({"configuracao": {"limiar": 3.0, "llm": False} | configuracao}), encoding="utf-8")
    (resultados / "privado" / f"{nome}-detalhe.jsonl").write_text("".join(json.dumps(x) + "\n" for x in linhas), encoding="utf-8")


RECUSA = "artigo mais próximo pouco relevante (reranker 2.40 < 3.0)"


def test_ganhos_e_perdas_por_lugar_do_artigo_na_base(tmp_path):
    _medicao(tmp_path, "base", [
        _linha("real-1"),  # em 1.º e certa
        _linha("real-2", responde=False, certa=False, nota=2.4, motivo=RECUSA),  # em 1.º, mas abaixo do limiar
        _linha("real-3", posicao=4, certa=False),  # do 2.º ao 8.º: responde com outro artigo
        _linha("real-4", posicao=None, certa=False),  # fora dos 8
        _linha("sem-1", tipo="sem_resposta", posicao=None, responde=False),
    ])
    _medicao(tmp_path, "nova", [
        _linha("real-1", posicao=2, certa=False),  # perde-se
        _linha("real-2", nota=3.5),  # ganha-se
        _linha("real-3"),  # ganha-se
        _linha("real-4", posicao=9, certa=False),
        _linha("sem-1", tipo="sem_resposta", posicao=None, responde=True, certa=False, nota=3.2),
    ])
    r = comparar.comparar("base", ["nova"], [4.0], resultados=tmp_path)
    assert r["base"]["real"] == {"n": 4, "certas": 1, "respondidas": 3, "nao_sei": 1, "erradas": 2, "artigo@1": 2, "artigo@8": 3}
    nova = r["variantes"]["nova"]
    assert nova["real"]["certas"] == 2 and nova["real"]["erradas"] == 2 and nova["sem_resposta"] == {"n": 1, "respondidas": 1}
    face = nova["face_a_base"]
    assert (face["em_1"]["n"], face["em_1"]["certas_base"], face["em_1"]["ganhos"], face["em_1"]["perdas"]) == (2, 1, 1, 1)
    assert (face["de_2_a_8"]["n"], face["de_2_a_8"]["ganhos"], face["de_2_a_8"]["perdas"]) == (1, 1, 0)
    assert (face["fora_dos_8"]["n"], face["fora_dos_8"]["certas"]) == (1, 0)
    assert (face["total"]["ganhos"], face["total"]["perdas"]) == (2, 1)
    # Com o limiar 4, a real-2 (nota 3,5) e a «sem resposta» (3,2) voltam a «não sei».
    com_4 = nova["limiares"]["4"]
    assert com_4["real"]["certas"] == 1 and com_4["real"]["nao_sei"] == 1 and com_4["sem_resposta"]["respondidas"] == 0


def test_sem_llm_baixar_o_limiar_responde_ao_que_o_limiar_recusava(tmp_path):
    linhas = [
        _linha("real-1", responde=False, certa=False, nota=2.4, motivo=RECUSA),
        _linha("real-2", responde=False, certa=False, nota=None, motivo="pergunta sobre uma data futura"),  # recusa por regra: fica
    ]
    _medicao(tmp_path, "base", linhas)
    _medicao(tmp_path, "nova", linhas)
    r = comparar.comparar("base", ["nova"], [2.0], resultados=tmp_path)
    assert r["variantes"]["nova"]["limiares"]["2"]["real"] == {"n": 2, "certas": 1, "respondidas": 1, "nao_sei": 1, "erradas": 0, "artigo@1": 2, "artigo@8": 2}


def test_com_llm_so_se_sobe_o_limiar_e_os_juizes_decidem_as_certas(tmp_path):
    _medicao(tmp_path, "base", [_linha("real-1"), _linha("real-2", posicao=3, certa=False)])
    _medicao(tmp_path, "x-llm", [_linha("real-1", nota=1.5), _linha("real-2", posicao=3, nota=4.0)], limiar=1.0, llm="sessão do Claude")
    (tmp_path / "x-juizes.json").write_text(json.dumps({"juizes": ["a", "b"], "por_tipo": {"real": {"ids_nao_certos": ["real-2"]}, "total": {}}}), encoding="utf-8")
    r = comparar.comparar("base", ["x-llm"], [0.5, 2.0], resultados=tmp_path)
    x = r["variantes"]["x-llm"]
    assert x["real"]["certas"] == 1 and x["real"]["certas_brando"] == 2 and x["real"]["erradas"] == 1
    assert list(x["limiares"]) == ["2"]  # abaixo do limiar da corrida não se sabe o que o LLM diria
    assert x["limiares"]["2"]["real"]["respondidas"] == 1 and x["limiares"]["2"]["real"]["certas"] == 0


def test_por_tipo_o_total_nao_conta_as_sem_resposta(tmp_path):
    _medicao(tmp_path, "base", [
        _linha("real-1"),
        _linha("lit-1", tipo="literal", posicao=3, certa=False),
        _linha("sem-1", tipo="sem_resposta", posicao=None, responde=False, certa=True),
    ])
    _medicao(tmp_path, "nova", [
        _linha("real-1", posicao=2, certa=False),
        _linha("lit-1", tipo="literal"),
        _linha("sem-1", tipo="sem_resposta", posicao=None, responde=True, certa=False, nota=3.2),
    ])
    r = comparar.comparar("base", ["nova"], [], resultados=tmp_path, todos_os_tipos=True)["variantes"]["nova"]["por_tipo"]
    assert (r["real"]["ganhos"], r["real"]["perdas"]) == (0, 1) and (r["literal"]["ganhos"], r["literal"]["perdas"]) == (1, 0)
    assert r["sem_resposta"]["base"]["respondidas"] == 0 and r["sem_resposta"]["variante"]["respondidas"] == 1
    total = r["total"]
    assert (total["base"]["n"], total["base"]["certas"], total["variante"]["certas"], total["ganhos"], total["perdas"]) == (3, 1, 1, 1, 1)
    assert "| total | 3 | 1 → 1 |" in comparar.tabela_por_tipo("nova", r)
