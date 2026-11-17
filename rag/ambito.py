"""O âmbito de um diploma: regime geral, regime de um setor, ato regional, diploma antigo...

Serve para duas coisas, as duas sem IA:

- a ordenação (`Pesquisa._prior`): numa pergunta que não fala de um setor, os regimes de um setor
  (a função pública) e os regulamentos antigos sem versão consolidada ficam atrás da lei geral;
- a página e o terminal: no modo sem IA mostram-se os artigos mais prováveis com o âmbito à vista,
  para quem lê ver que o 1.º é, por exemplo, da função pública e o 2.º do Código do Trabalho.
"""

from __future__ import annotations

import re

from rag.texto import sem_acentos


# Regimes de um setor: (nome mostrado, o que o diz no diploma, o que o diz na pergunta). Os textos
# comparam-se sem acentos e em minúsculas.
SETORES = (
    (
        "Função pública",
        re.compile(r"func(?:ao|oes) public|trabalho em funcoes|administracao publica"),
        re.compile(
            r"func(?:ao|oes) public|funcionari[oa]s? public|administracao publica|set?or public|trabalhador(?:es)? em funcoes"
            r"|servico public|carreira (?:geral|especial)|\bltfp\b"
        ),
    ),
)
# Regulamentos antigos (sem versão consolidada) que, numa pergunta geral, quase nunca são a resposta:
# portarias e despachos de antes de 1990, muitas vezes de um organismo ou de um setor só.
TIPOS_REGULAMENTARES = ("portaria", "despacho", "despacho-normativo", "despacho-conjunto", "aviso")
ANTIGO_ATE = "1990-01-01"
REGIONAL = {"/A": "Só Açores", "/M": "Só Madeira"}
TIPOS_UE = ("regulation", "directive", "decision")


def _normalizar(texto: str) -> str:
    return sem_acentos(texto or "").lower()


def setor(titulo: str, sumario: str, parte: str) -> str | None:
    """O setor do diploma (ou do anexo), se é o regime de um setor; senão None."""
    texto = _normalizar(f"{titulo} {sumario} {parte}")
    return next((nome for nome, no_diploma, _ in SETORES if no_diploma.search(texto)), None)


def pergunta_fala_do_setor(pergunta: str, nome: str) -> bool:
    texto = _normalizar(pergunta)
    return any(nome == n and na_pergunta.search(texto) for n, _, na_pergunta in SETORES)


def antigo_regulamentar(doc: dict) -> bool:
    """Portaria, despacho ou aviso de antes de 1990 sem versão consolidada."""
    return doc.get("tipo") in TIPOS_REGULAMENTARES and (doc.get("data") or "9999") < ANTIGO_ATE and not doc.get("com_historico")


def rotulo(doc: dict, parte: str) -> str:
    """O âmbito em poucas palavras, para mostrar ao lado do artigo."""
    nome_setor = setor(doc.get("titulo") or "", doc.get("sumario") or "", parte)
    if nome_setor:
        return nome_setor
    if doc.get("tipo") in TIPOS_UE:
        return "Direito da UE"
    numero = doc.get("numero") or ""
    for sufixo, nome in REGIONAL.items():
        if numero.endswith(sufixo):
            return nome
    if antigo_regulamentar(doc):
        return f"Regulamento de {(doc.get('data') or '')[:4]}, sem versão consolidada"
    if re.search(r"\bcodigo\b|\blei geral\b", _normalizar(parte)):
        return "Regime geral"
    return ""
