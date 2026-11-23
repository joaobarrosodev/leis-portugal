"""Texto corrido lido como artigos no índice (`rag/corrido.py`, `rag.indice._unidades`) e a regra das redações
anteriores nas declarações de retificação (`rag.copias.TIPOS`), 20/11/2026."""

import re
import sqlite3

from rag import copias, corrido, indice
from rag.corrido import ArtigoCorrido
from rag.indice import Documento, _unidades, pedacos_do_documento


PREAMBULO = "Considerando que importa regular a pesca nos rios e nas albufeiras do continente, " * 5
MAPA = "Espécie | Período de defeso | Tamanho mínimo em centímetros | Observações sobre a pesca\n" * 6
DECRETO = f"""# Decreto-Lei n.º 1/70

{PREAMBULO}

Usando da faculdade conferida pela 1.ª parte do n.º 2.º do artigo 109.º da Constituição, o Governo decreta e eu promulgo, para valer como lei, o seguinte:

Artigo 1.º É proibida a pesca com redes de arrasto nos rios.

Art. 2.º - 1. A infracção é punida com multa.
2. A multa é graduada pelo juiz.

Artigo 3.º
(Entrada em vigor)
Este diploma entra em vigor no dia seguinte.

Visto e aprovado em Conselho de Ministros. - Marcello Caetano.

Promulgado em 10 de Janeiro de 1970.

MAPA ANEXO

{MAPA}
"""


def _palavras(texto: str) -> set[str]:
    return set(re.findall(r"\w+", texto.lower()))


# ---------------------------------------------------------------------------------- a salvaguarda


def test_le_os_artigos_com_numeracao_seguida_e_guarda_o_resto_fora():
    artigos, fora = corrido.ler(DECRETO)
    assert [(a.chave, a.epigrafe, a.texto) for a in artigos] == [
        ("1.º", "", "É proibida a pesca com redes de arrasto nos rios."),
        ("2.º", "", "1. A infracção é punida com multa.\n2. A multa é graduada pelo juiz."),
        ("3.º", "Entrada em vigor", "Este diploma entra em vigor no dia seguinte."),
    ]
    # O preâmbulo, as assinaturas e o mapa depois delas não ficam em nenhum artigo: saem em `fora`, na parte do diploma.
    assert [p for p, _ in fora] == [""]
    assert "Considerando que importa regular" in fora[0][1] and "Tamanho mínimo" in fora[0][1] and "Promulgado em 10" in fora[0][1]
    assert "É proibida a pesca" not in fora[0][1]


def test_artigo_unico_e_depois_o_texto_que_aprova():
    texto = "Artigo único. É aprovado o Acordo, que segue em anexo.\n\nArtigo 1.º As Partes cooperam.\n\nArtigo 2.º O Acordo entra em vigor.\n\nArtigo 3.º Pode ser denunciado."
    assert [a.chave for a in corrido.ler(texto)[0]] == ["único", "1.º", "2.º", "3.º"]


def test_menos_de_tres_linhas_de_artigo_fica_em_blocos():
    assert corrido.ler("Artigo 1.º Um.\n\nArt. 2.º Dois.") is None


def test_rubricas_de_orcamento_nao_sao_artigos():
    texto = ("Artigo 1.º É aberto um crédito especial de 100000$00, a adicionar às seguintes verbas:\n\n"
             "Artigo 127.º «Remunerações acidentais»:\n\nN.º 1) «Gratificações» ... 50000$00\n\n"
             "Artigo 128.º «Despesas de higiene»:\n\nN.º 2) ... 50000$00\n\nArt. 2.º Este diploma entra em vigor.")
    assert corrido.ler(texto) is None


def test_redacao_nova_de_outro_diploma_nao_abre_uma_parte():
    # «Artigo 1.º» de outro decreto-lei, sem aspas, logo a seguir a «… passa a ter a seguinte redacção:» (DL 39/81).
    texto = ("Artigo 1.º O artigo 1.º do Decreto-Lei n.º 668/75 passa a ter a seguinte redacção:\n\n"
             "Artigo 1.º As pensões são actualizadas.\n\nArt. 2.º A reparação das despesas de funeral.\n\n"
             "Art. 3.º As dúvidas são resolvidas por despacho.")
    assert corrido.ler(texto) is None
    # A mesma coisa sem «redacção», só com os dois pontos (DL 793/76, «na seguinte conformidade:»).
    assert corrido.ler(texto.replace("passa a ter a seguinte redacção:", "é aditada uma alínea, na seguinte conformidade:")) is None


def test_um_regulamento_aprovado_sem_titulo_de_anexo_abre_uma_parte():
    texto = ("Artigo 1.º É aprovado o regulamento que se segue.\n\nArt. 2.º Este decreto entra em vigor.\n\n"
             "REGULAMENTO INTERNO DO FUNDO\n\nArtigo 1.º O Fundo reúne uma vez por mês.\n\n"
             "Art. 2.º As deliberações são tomadas por maioria.\n\nArt. 3.º O presidente coordena.")
    artigos, _ = corrido.ler(texto)
    assert [a.chave for a in artigos] == ["1.º", "2.º", "Parte 2::1.º", "Parte 2::2.º", "Parte 2::3.º"]


def test_aspas_por_fechar_que_engolem_os_artigos_seguintes():
    # O último artigo lido traz dentro o artigo seguinte (DL 46379): a numeração parecia seguida, mas faltavam artigos.
    texto = ("Artigo 1.º Um.\n\nArt. 2.º Dois.\n\nArt. 3.º Os títulos dirão «Obrigações do Tesouro, 1965.\n\n"
             "Art. 4.º O juro é de 5 por cento.\n\nArt. 5.º Este diploma entra em vigor.")
    assert corrido.ler(texto) is None


def test_sumario_de_um_regulamento_nao_passa():
    # O DL 235/83: «Artigo 1.º Objecto e campo de aplicação.» no sumário e, a seguir, o artigo 1.º a começar pela epígrafe.
    epigrafes = ["Objecto e campo de aplicação.", "Simbologia e unidades.", "Critérios gerais de verificação da segurança."]
    sumario = "\n\n".join(f"Artigo {n}.º {e}" for n, e in enumerate(epigrafes, 1))
    corpo = "\n\n".join(f"Artigo {n}.º {e[:-1]} O presente artigo trata desta matéria com algum desenvolvimento." for n, e in enumerate(epigrafes, 1))
    texto = f"Artigo 1.º É aprovado o Regulamento.\n\nArt. 2.º Entra em vigor.\n\nArt. 3.º Revogações.\n\n{sumario}\n\n{corpo}"
    assert corrido.ler(texto) is None
    # Sem o sumário, o mesmo texto passa.
    assert corrido.ler(f"Artigo 1.º É aprovado o Regulamento.\n\nArt. 2.º Entra em vigor.\n\nArt. 3.º Revogações.\n\n{corpo}") is not None
    assert not corrido._tem_sumario([ArtigoCorrido("", "1.º", "", "Objecto."), ArtigoCorrido("", "2.º", "", "Âmbito.")])


def test_com_um_titulo_de_artigo_no_registo_nao_se_le_o_texto_corrido():
    texto = "###### Artigo 1.º - 1. ...\n\n... 4. Em matéria de abastecimento.\n\nArt. 13.º - 1. ...\n\nArt. 14.º Texto.\n\nArt. 16.º Texto."
    assert corrido.ler(texto) is None


def test_acordaos_e_pareceres_ficam_em_blocos():
    assert not corrido.le_o_tipo("acordao") and not corrido.le_o_tipo("acordao-tribunal-constitucional")
    assert not corrido.le_o_tipo("parecer-conselho-estado")
    assert corrido.le_o_tipo("decreto-lei") and corrido.le_o_tipo("portaria")


# ---------------------------------------------------------------------------------- no índice


def test_no_indice_os_artigos_e_o_resto_em_blocos_sem_perder_texto():
    unidades = _unidades(DECRETO)
    assert [u.chave for u in unidades] == ["1.º", "2.º", "3.º", "texto#1"]
    # Nenhuma palavra do registo sai do índice. O título `# …` nunca entrou (está no cabeçalho de cada pedaço) e o
    # «Artigo 3.º» que abre cada artigo é o número do pedaço, como nos títulos `###### Artigo`.
    no_indice = _palavras(" ".join(u.texto + " " + u.epigrafe for u in unidades))
    sem_rotulos = re.sub(r"(?m)^(?:Artigo|Art\.) \d+\.º", "", DECRETO.replace("# Decreto-Lei n.º 1/70", ""))
    assert _palavras(sem_rotulos) <= no_indice
    # Sem a leitura, o registo fica em blocos, como antes.
    assert [u.chave for u in _unidades(DECRETO, texto_corrido=False)] == ["texto#1"]


def test_artigo_comprido_passa_o_resto_para_blocos():
    comprido = "O regime aplica-se nos termos seguintes. " * 1000  # ~40 000 caracteres
    texto = f"Artigo 1.º {comprido}\n\nArt. 2.º Dois.\n\nArt. 3.º Três."
    unidades = _unidades(texto)
    assert [u.chave for u in unidades][:3] == ["1.º", "2.º", "3.º"] and all(u.chave.startswith("texto#") for u in unidades[3:])
    assert len(unidades) > 3


def _registo(tmp_path, monkeypatch, corpo, tipo="decreto-lei", ident="pt:x"):
    monkeypatch.setattr(indice, "RAIZ", tmp_path)
    (tmp_path / f"{ident}.md").write_text(f"---\nid: {ident}\n---\n\n{corpo}", encoding="utf-8")
    return Documento(ident, "Decreto-Lei n.º 1/70", tipo, "1/70", "1970-01-10", "Sumário", "in_force", "original", None, f"{ident}.md")


def test_pedacos_do_documento_le_o_texto_corrido_menos_nos_acordaos(tmp_path, monkeypatch):
    pedacos, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, DECRETO))
    assert [p.chave for p in pedacos] == ["1.º", "2.º", "3.º", "texto#1"] and pedacos[0].desde == "1970-01-10"
    acordao, _, _ = pedacos_do_documento(_registo(tmp_path, monkeypatch, DECRETO, tipo="acordao"))
    assert all(p.chave.startswith("texto#") for p in acordao)


def _export(tmp_path, ids):
    caminho = tmp_path / "export.sqlite"
    caminho.unlink(missing_ok=True)
    with sqlite3.connect(caminho) as con:
        con.execute("CREATE TABLE documentos (id, title)")
        con.execute("CREATE TABLE relacoes (source_id, type, target, target_id, date, label)")
        con.executemany("INSERT INTO documentos VALUES (?, ?)", [(i, i) for i in ids])
    return caminho


def test_construir_deixa_em_blocos_os_registos_com_uma_copia_marcada_em_texto_corrido(tmp_path, monkeypatch):
    # O Código Penal de 1982 no DL 400/82: a marca procura o início do texto antigo nos blocos (`aplicar_redacoes`).
    docs = [_registo(tmp_path, monkeypatch, DECRETO, ident=i) for i in ("marcado", "livre")]
    marca = copias.Marca("marcado", "", None, "Artigo 2.º - 1. A infracção é punida com multa.\n2. A multa é graduada pelo juiz.", "1995-03-15", "livre", "", "prova")
    saida = tmp_path / "indice.sqlite"
    indice.construir(saida, docs, _export(tmp_path, ["marcado", "livre"]), fios=1, redacoes={"marcado": [marca]})
    with sqlite3.connect(saida) as con:
        chaves = {d: [c for (c,) in con.execute("SELECT chave FROM pedacos WHERE documento = ? ORDER BY ordem", (d,))] for d in ("marcado", "livre")}
    assert chaves["livre"] == ["1.º", "2.º", "3.º", "texto#1"]
    assert all(c.startswith("texto#") for c in chaves["marcado"])
    indice.construir(saida, docs, _export(tmp_path, ["marcado", "livre"]), fios=1, texto_corrido=False)
    with sqlite3.connect(saida) as con:
        assert {c for (c,) in con.execute("SELECT chave FROM pedacos")} == {"texto#1"}


# ---------------------------------------------------------------------------------- declarações de retificação


TEMAS = [f"Tema {n}" for n in range(1, 13)]
NOTA = "\n\n> Alterado pelo/a [Decreto-Lei n.º 9/2025 - DR de 2025-04-01](https://x), em vigor a partir de 2025-04-11"


def _artigos(epigrafes, nota=""):
    return "\n\n".join(f"###### Artigo {n}.º — {e}\n\nTexto do artigo {n}.{nota}" for n, e in enumerate(epigrafes, 1))


def test_uma_declaracao_de_retificacao_que_republica_o_texto_e_uma_copia(tmp_path):
    # A Declaração de Rectificação n.º 100-A/2007 republica o Código de Processo Penal de 2007.
    from test_copias import _acervo

    registos = [
        ("atual", "Decreto-Lei n.º 1/2000", "Aprova o Código das Coisas", "2000-01-10", _artigos(TEMAS, NOTA), "2025-04-11"),
        ("retif", "Declaração de Rectificação n.º 5/2010", "Rectifica o Decreto-Lei n.º 1/2000", "2010-05-05",
         "Rectifica-se o seguinte.\n\n## ANEXO\n\n" + _artigos(TEMAS), None),
    ]
    acervo, cabecalhos = _acervo(tmp_path, registos, {"atual": [("retif", "2010-05-05", None)]})
    acervo.docs["retif"]["document_type"] = "declaracao-retificacao"
    marcas, _ = copias.redacoes_anteriores(acervo, cabecalhos, tmp_path, "2026-11-20")
    assert [(m.documento, m.parte, m.ate, m.alvo) for m in marcas] == [("retif", "ANEXO", "2025-04-11", "atual")]
    # Antes de 20/11/2026 as declarações de retificação não contavam.
    assert copias.redacoes_anteriores(acervo, cabecalhos, tmp_path, "2026-11-20", tipos=(*copias.PRIORITARIOS, "decreto"))[0] == []


def test_texto_curto_fora_dos_artigos_tambem_fica_em_blocos():
    # Antes o registo estava todo em blocos: a fórmula, as assinaturas e os títulos dos capítulos não podem sair.
    texto = ("# Decreto-Lei n.º 2/70\n\nUsando da faculdade conferida, o Governo decreta o seguinte:\n\n### CAPÍTULO I — Imunidades\n\n"
             "Artigo 1.º Um.\n\nArt. 2.º Dois.\n\nArt. 3.º Três.\n\nPublique-se. Américo Deus Rodrigues Thomaz.")
    unidades = _unidades(texto)
    assert [u.chave for u in unidades] == ["1.º", "2.º", "3.º", "texto#1"]
    assert {"faculdade", "imunidades", "thomaz"} <= _palavras(unidades[-1].texto)


def test_diploma_que_aprova_um_codigo_com_o_codigo_noutra_parte_fica_em_blocos(tmp_path, monkeypatch):
    # O DL 44561 «Aprova o Código do Imposto de Capitais»: a pesquisa procura o código na parte «» do diploma.
    texto = ("Artigo 1.º É aprovado o Código que se segue.\n\nArt. 2.º Entra em vigor.\n\nCÓDIGO DO IMPOSTO DE CAPITAIS\n\n"
             "Artigo 1.º O imposto incide sobre os capitais.\n\nArt. 2.º A taxa é de 10 por cento.\n\nArt. 3.º Isenções.")
    assert corrido.codigo_no_diploma("Aprova o Código do Imposto de Capitais") and not corrido.codigo_no_diploma("Cria o Fundo")
    assert corrido.ler(texto) is not None and corrido.ler(texto, so_no_diploma=True) is None
    doc = _registo(tmp_path, monkeypatch, texto)
    doc.sumario = "Aprova o Código do Imposto de Capitais"
    assert all(p.chave.startswith("texto#") for p in pedacos_do_documento(doc)[0])
    assert corrido.ler(DECRETO, so_no_diploma=True) is not None  # tudo na parte do diploma: lê-se
