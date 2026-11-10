"""Reescrita da pergunta numa consulta jurídica, antes da pesquisa.

Uma pergunta como a escreve um utilizador ("q tem d ter uma fatura pra servir d papel d transporte")
quase nunca chega ao artigo certo por palavras. Um LLM reescreve-a numa consulta com o vocabulário
da lei ("requisitos da fatura como documento de transporte no regime de bens em circulação"), a
pesquisa usa só a consulta, e o LLM que responde continua a ver a pergunta original. As regras
estão em `rag/REESCRITA.md` (as mesmas que as sessões do Claude seguiram na medição). Medido em
`rag/README.md`: nas 281 coloquiais o artigo certo em 1.º passa de 21% para 59% e as perguntas
com resposta certa de 11% para 76%; nas 530 do teste o "não sei" cai de 53% para 34% com a
mesma fiabilidade; nas 407 sintéticas não piora.

Sem `ANTHROPIC_API_KEY` (ou se a chamada falhar), a pesquisa usa a pergunta tal como está.
"""

from __future__ import annotations

import dataclasses
import re

from rag.fontes import RAIZ
from rag.pesquisa import Consulta, Pesquisa
from rag.resposta import MODELO, llm_disponivel


FICHEIRO = RAIZ / "rag" / "REESCRITA.md"
_LINHA_DOS_FICHEIROS = re.compile(r"^.*entrada-NN\.jsonl.*\n\n?", re.M)
MAXIMO_CARACTERES = 600


def instrucoes() -> str:
    """As regras de `REESCRITA.md` sem a linha sobre os ficheiros das sessões, e o formato da resposta."""
    texto = _LINHA_DOS_FICHEIROS.sub("", FICHEIRO.read_text(encoding="utf-8")).rstrip()
    return texto + "\nResponde só com a consulta, numa linha, sem aspas nem explicações."


def reescrever(pergunta: str) -> str:
    """A consulta jurídica para a pergunta; a própria pergunta sem LLM ou se a chamada falhar."""
    if not llm_disponivel():
        return pergunta
    import anthropic

    try:
        resposta = anthropic.Anthropic().messages.create(
            model=MODELO,
            max_tokens=400,
            system=instrucoes(),
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": pergunta}],
        )
    except anthropic.APIError:
        return pergunta
    texto = " ".join("".join(b.text for b in resposta.content if b.type == "text").split())
    return texto[:MAXIMO_CARACTERES] if texto else pergunta


def pesquisar(pesquisa: Pesquisa, pergunta: str, data: str, *, k: int, consulta: str | None = None) -> Consulta:
    """Pesquisa pela consulta reescrita (a dada, ou a que o LLM escreve agora) e devolve a `Consulta`
    com a pergunta original: é essa que o LLM que responde e os juízes veem."""
    por = consulta or reescrever(pergunta)
    resultado = pesquisa.pesquisar(por, data, k=k)
    return dataclasses.replace(resultado, pergunta=pergunta, pesquisa_por=por if por != pergunta else None)
