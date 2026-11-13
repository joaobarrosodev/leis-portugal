"""Resposta a partir dos artigos encontrados.

Com a chave de uma IA no ambiente (`rag.provedores`: Claude por omissão, OpenAI ou Gemini), um LLM
escreve a resposta só a partir dos artigos dados e cita-os; sem chave, a "resposta" é o primeiro artigo encontrado,
com os avisos. Em ambos os casos a resposta é "não sei" quando:

- a pergunta cita um diploma que não está no acervo (e nenhum outro que esteja);
- a pergunta é sobre um ano posterior à data de referência (o acervo não tem o futuro);
- não há artigos, ou o reranker dá ao melhor uma pontuação abaixo de `limiar`;
- o LLM diz que os artigos não respondem, ou não cita nenhum dos artigos dados.

Os avisos (revogado, texto original de um diploma alterado, redação antiga, texto em vigor
de um código republicado) vêm sempre da pesquisa e juntam-se à resposta, não dependem do LLM.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from rag import provedores
from rag.pesquisa import Consulta, Resultado


LIMIAR_PADRAO = 3.0  # do reranker, sem LLM: o artigo do topo é a resposta (rag/README.md)
# Com LLM, o LLM lê os artigos e recusa quando não respondem: entre 1 e 3, nas perguntas que o limiar 3
# recusava, respondeu a 43 de 61 e 41 estavam certas para os quatro juízes (rag/README.md, `limiar1`).
LIMIAR_COM_LLM = 1.0
ARTIGOS_NO_CONTEXTO = 8

# Modo estrito (por omissão): a fiabilidade conta mais do que responder a tudo. Não responde quando
#  - o artigo citado é o texto original de um diploma alterado sem versão consolidada no acervo
#    (a redação em vigor pode ser outra: nos testes só 60% destas respostas estavam certas), ou
#  - a própria resposta diz que os artigos dados não trazem a norma (só 1 de 24 estava certa).
AVISO_TEXTO_ORIGINAL = "Texto original; alterado por"
_FALTA_NORMA = re.compile(
    r"(não (consta|constam|vem|vêm|foi dado|foram dados|está|estão) (nos|entre os|dos) artigos"
    r"|artigos (dados|fornecidos|vistos|apresentados)[^.]{0,40}não"
    r"|não (consta|constam)\b"
    r"|não (é|são) (dado|dados|fornecido)"
    r"|(os )?artigos[^.]{0,30}não (trazem|contêm|dizem|indicam|incluem))",
    re.I,
)
CARACTERES_POR_ARTIGO = 6000

INSTRUCOES = """És um assistente que responde a perguntas sobre legislação portuguesa e europeia em vigor.
Respondes só com base nos artigos dados, em português de Portugal, de forma curta e literal.
Cada afirmação tem de estar escrita num dos artigos; cita o artigo pelo número entre parênteses retos, por exemplo [2].
Se os artigos não respondem à pergunta, ou se a pergunta pede aconselhamento sobre um caso concreto, jurisprudência,
doutrina, lei estrangeira, previsões ou informação que não é legislação, não respondas.
Se o artigo pertence a um diploma revogado, diz que foi revogado e por que diploma.
Responde só com um objeto JSON: {"responde": true|false, "resposta": "...", "citacoes": [números dos artigos usados]}."""


@dataclass
class Resposta:
    responde: bool
    texto: str
    citacoes: list[Resultado] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    motivo: str = ""  # porque não responde
    com_llm: bool = False
    modelo: str = ""  # a IA e o modelo que escreveram a resposta
    aviso_modelo: str | None = None  # quando não é o modelo medido (rag.provedores.aviso_medicao)
    erro: str = ""  # a chamada à IA falhou (chave, créditos, rede): não é um "não sei" da lei
    # A segunda resposta: os acórdãos do Tribunal Constitucional que julgaram os artigos citados.
    # Vem dos dados (rag.jurisprudencia), não do LLM, e fica separada da resposta da lei.
    jurisprudencia: list[dict] = field(default_factory=list)


def _ano_futuro(consulta: Consulta) -> bool:
    ano = int(consulta.data[:4])
    # Os anos de um intervalo ("horizonte 2021-2030") não contam.
    return any(int(a) > ano for a in re.findall(r"(?<![\d/-])(20\d\d)(?![\d/-])", consulta.pergunta))


def nao_sei_antes(consulta: Consulta, limiar: float | None = None) -> str | None:
    """O motivo para não responder que a pesquisa já mostra, ou None."""
    if consulta.diplomas_em_falta and not consulta.diplomas_citados and not consulta.referencias.codigos:
        return f"{', '.join(consulta.diplomas_em_falta)}: não está no acervo"
    if _ano_futuro(consulta):
        return "pergunta sobre uma data futura"
    if not consulta.resultados:
        return "sem artigos encontrados"
    topo = consulta.resultados[0]
    if limiar is not None and topo.reranker is not None and topo.reranker < limiar:
        return f"artigo mais próximo pouco relevante (reranker {topo.reranker:.2f} < {limiar})"
    return None


JULGAMENTOS_POR_ARTIGO = 5


def jurisprudencia(consulta: Consulta, citacoes: list[Resultado], pesquisa=None) -> list[dict]:
    """Os acórdãos do TC sobre os artigos citados, até à data de referência, um por acórdão e artigo:
    as decisões com força obrigatória geral primeiro, depois os mais recentes. Os primeiros
    `JULGAMENTOS_POR_ARTIGO` de cada artigo têm `mostrar`; os outros contam só para o resumo."""
    if pesquisa is None:
        return []
    lista: list[dict] = []
    for r in citacoes:
        vistos: set[str] = set()
        for j in pesquisa.julgamentos(r):
            if (j["data"] or "") > consulta.data or j["acordao"] in vistos:
                continue
            vistos.add(j["acordao"])
            lista.append({**j, "artigo": r.rotulo, "mostrar": len(vistos) <= JULGAMENTOS_POR_ARTIGO})
    return lista


def responder(consulta: Consulta, *, limiar: float | None = None, usar_llm: bool | None = None, pesquisa=None) -> Resposta:
    """A resposta da lei e, com `pesquisa`, a segunda resposta: a jurisprudência dos artigos citados."""
    resposta = _responder(consulta, limiar=limiar, usar_llm=usar_llm)
    if resposta.responde:
        resposta.jurisprudencia = jurisprudencia(consulta, resposta.citacoes, pesquisa)
    return resposta


def _responder(consulta: Consulta, *, limiar: float | None = None, usar_llm: bool | None = None) -> Resposta:
    motivo = nao_sei_antes(consulta, limiar)
    if motivo:
        return Resposta(False, "Não sei.", motivo=motivo)
    if usar_llm is None:
        usar_llm = llm_disponivel()
    if usar_llm:
        return _com_llm(consulta)
    topo = consulta.resultados[0]
    texto = f"{topo.rotulo}:\n{topo.texto[:1200]}"
    return Resposta(True, texto, [topo], list(topo.avisos))


def llm_disponivel() -> bool:
    return provedores.disponivel()


def contexto(consulta: Consulta) -> tuple[str, list[Resultado]]:
    """Os artigos que o LLM recebe, numerados, com os avisos; e a lista deles pela mesma ordem."""
    artigos = consulta.resultados[:ARTIGOS_NO_CONTEXTO]
    blocos = []
    for n, r in enumerate(artigos, 1):
        avisos = "".join(f"\nAviso: {a}" for a in r.avisos)
        blocos.append(f"[{n}] {r.rotulo}{avisos}\n{r.texto[:CARACTERES_POR_ARTIGO]}")
    return "\n\n".join(blocos), artigos


def mensagem(consulta: Consulta, artigos: str) -> str:
    return f"Data de referência: {consulta.data}\n\nArtigos:\n\n{artigos}\n\nPergunta: {consulta.pergunta}"


def extrair_json(texto: str) -> dict:
    m = re.search(r"\{.*\}", texto, re.S)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


def interpretar(dados: dict, artigos: list[Resultado], *, estrito: bool = True) -> Resposta:
    """A resposta do LLM ({"responde", "resposta", "citacoes"}) como `Resposta`: "não sei" se não responde ou não cita um artigo dado."""
    citacoes = [artigos[n - 1] for n in dados.get("citacoes") or [] if isinstance(n, int) and 1 <= n <= len(artigos)]
    if not dados.get("responde"):
        return Resposta(False, "Não sei.", motivo="o modelo diz que os artigos não respondem", com_llm=True)
    if not citacoes:
        return Resposta(False, "Não sei.", motivo="resposta sem citação de um artigo dado", com_llm=True)
    avisos = list(dict.fromkeys(a for r in citacoes for a in r.avisos))
    texto = str(dados.get("resposta", ""))
    if estrito:
        if any(a.startswith(AVISO_TEXTO_ORIGINAL) for a in avisos):
            return Resposta(False, "Não sei.", motivo="texto original de um diploma alterado, sem versão consolidada no acervo", com_llm=True)
        if _FALTA_NORMA.search(texto):
            return Resposta(False, "Não sei.", motivo="a resposta diz que os artigos dados não trazem a norma", com_llm=True)
    return Resposta(True, texto, citacoes, avisos, com_llm=True)


def _com_llm(consulta: Consulta) -> Resposta:
    texto_artigos, artigos = contexto(consulta)
    quem, aviso = provedores.descricao(), provedores.aviso_medicao()
    try:
        escrita = provedores.escrever(INSTRUCOES, mensagem(consulta, texto_artigos), max_tokens=16000, esforco="medium")
    except provedores.ErroIA as e:
        return Resposta(False, "Não sei.", motivo=str(e), com_llm=True, modelo=quem, aviso_modelo=aviso, erro=str(e))
    if escrita.recusou:
        resposta = Resposta(False, "Não sei.", motivo="o modelo recusou", com_llm=True)
    else:
        resposta = interpretar(extrair_json(escrita.texto), artigos)
    resposta.modelo, resposta.aviso_modelo = quem, aviso
    return resposta
