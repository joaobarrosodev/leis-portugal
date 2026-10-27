"""Resposta a partir dos artigos encontrados.

Com `ANTHROPIC_API_KEY` no ambiente (e o pacote `anthropic`), um LLM escreve a resposta só a
partir dos artigos dados e cita-os; sem chave, a "resposta" é o primeiro artigo encontrado,
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
import os
import re
from dataclasses import dataclass, field

from rag.pesquisa import Consulta, Resultado


MODELO = os.environ.get("RAG_MODELO", "claude-opus-5-5")
ARTIGOS_NO_CONTEXTO = 8
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


def responder(consulta: Consulta, *, limiar: float | None = None, usar_llm: bool | None = None) -> Resposta:
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
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def _contexto(consulta: Consulta) -> tuple[str, list[Resultado]]:
    artigos = consulta.resultados[:ARTIGOS_NO_CONTEXTO]
    blocos = []
    for n, r in enumerate(artigos, 1):
        avisos = "".join(f"\nAviso: {a}" for a in r.avisos)
        blocos.append(f"[{n}] {r.rotulo}{avisos}\n{r.texto[:CARACTERES_POR_ARTIGO]}")
    return "\n\n".join(blocos), artigos


def _com_llm(consulta: Consulta) -> Resposta:
    import anthropic

    contexto, artigos = _contexto(consulta)
    cliente = anthropic.Anthropic()
    mensagem = cliente.messages.create(
        model=MODELO,
        max_tokens=16000,
        system=INSTRUCOES,
        output_config={"effort": "medium"},
        messages=[{"role": "user", "content": f"Data de referência: {consulta.data}\n\nArtigos:\n\n{contexto}\n\nPergunta: {consulta.pergunta}"}],
    )
    if mensagem.stop_reason == "refusal":
        return Resposta(False, "Não sei.", motivo="o modelo recusou", com_llm=True)
    texto = "".join(b.text for b in mensagem.content if b.type == "text")
    m = re.search(r"\{.*\}", texto, re.S)
    try:
        dados = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        dados = {}
    citacoes = [artigos[n - 1] for n in dados.get("citacoes") or [] if isinstance(n, int) and 1 <= n <= len(artigos)]
    if not dados.get("responde"):
        return Resposta(False, "Não sei.", motivo="o modelo diz que os artigos não respondem", com_llm=True)
    if not citacoes:
        return Resposta(False, "Não sei.", motivo="resposta sem citação de um artigo dado", com_llm=True)
    avisos = list(dict.fromkeys(a for r in citacoes for a in r.avisos))
    return Resposta(True, str(dados.get("resposta", "")), citacoes, avisos, com_llm=True)
