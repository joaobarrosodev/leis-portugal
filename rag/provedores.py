"""As IAs que escrevem a resposta e reescrevem a pergunta: Claude, OpenAI ou Gemini.

A escolha vem do ambiente (a aplicação define-o no seu próprio processo, a partir das Definições):

- `RAG_PROVEDOR`: `claude` (por omissão), `openai` ou `gemini`;
- `RAG_MODELO`: o modelo; por omissão, o de `PROVEDORES[...]["modelo"]`;
- a chave na variável de cada provedor (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`).

**A qualidade publicada (cerca de 95% de respostas certas, `rag/README.md`) foi medida só com o
Claude Opus 5.5.** Com outro provedor ou modelo, as instruções, o formato da resposta e o modo
estrito são os mesmos, mas a qualidade não foi medida: `aviso_medicao()` diz isso em cada resposta.

Os nomes dos modelos da OpenAI e da Gemini vêm da documentação oficial de 12/11/2026; mudam com
frequência, por isso `validar()` confirma que o modelo existe quando se valida a chave.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass


MEDIDO = ("claude", "claude-opus-5-5")

PROVEDORES: dict[str, dict] = {
    "claude": {
        "nome": "Claude (Anthropic)",
        "variavel": "ANTHROPIC_API_KEY",
        "pacote": "anthropic",
        "modelo": "claude-opus-5-5",
        "modelos": ["claude-opus-5-5", "claude-sonnet-5-5"],
        "chaves": "https://platform.claude.com/settings/keys",
        "conta": "https://platform.claude.com/",
    },
    "openai": {
        "nome": "OpenAI",
        "variavel": "OPENAI_API_KEY",
        "pacote": "openai",
        "modelo": "gpt-6-astra",
        "modelos": ["gpt-6-astra", "gpt-6.1-sol", "gpt-6-luna"],
        "chaves": "https://platform.openai.com/api-keys",
        "conta": "https://platform.openai.com/",
    },
    "gemini": {
        "nome": "Gemini (Google)",
        "variavel": "GEMINI_API_KEY",
        "pacote": "google.genai",
        "modelo": "gemini-4-carbon",
        "modelos": ["gemini-4-carbon", "gemini-4-hydrogen", "gemini-3.8-flash"],
        "chaves": "https://aistudio.google.com/apikey",
        "conta": "https://aistudio.google.com/",
    },
}


class ErroIA(Exception):
    """A chamada à IA falhou (chave, créditos, rede, modelo); a mensagem é para mostrar a quem usa."""


@dataclass
class Escrita:
    texto: str
    recusou: bool = False


def provedor() -> str:
    nome = os.environ.get("RAG_PROVEDOR", "claude").strip().lower()
    if nome not in PROVEDORES:
        raise ErroIA(f"IA desconhecida: {nome} (escolhe entre {', '.join(PROVEDORES)})")
    return nome


def modelo() -> str:
    return os.environ.get("RAG_MODELO") or PROVEDORES[provedor()]["modelo"]


def chave(nome: str | None = None) -> str | None:
    return os.environ.get(PROVEDORES[nome or provedor()]["variavel"]) or None


def _instalado(pacote: str) -> bool:
    """O pacote está instalado (para `google.genai`, o próprio subpacote, não só o espaço `google`)."""
    try:
        return importlib.util.find_spec(pacote) is not None
    except (ImportError, ValueError):
        return False


def disponivel() -> bool:
    """Há chave para o provedor escolhido e o pacote dele está instalado."""
    try:
        nome = provedor()
    except ErroIA:
        return False
    return bool(chave(nome)) and _instalado(PROVEDORES[nome]["pacote"])


def descricao() -> str:
    return f"{PROVEDORES[provedor()]['nome']}, {modelo()}"


def aviso_medicao() -> str | None:
    """Quando não é o modelo medido, o aviso de que a qualidade publicada não se aplica."""
    if (provedor(), modelo()) == MEDIDO:
        return None
    return (
        f"Respondido por {descricao()}. Os resultados publicados (cerca de 95% de respostas certas) "
        "foram medidos com o Claude Opus 5.5; a qualidade com este modelo não foi medida."
    )


def escrever(sistema: str, mensagem: str, *, max_tokens: int, esforco: str = "medium") -> Escrita:
    """Uma resposta de texto do provedor escolhido. `esforco` só se aplica ao Claude."""
    nome = provedor()
    try:
        return _ESCREVER[nome](sistema, mensagem, max_tokens, esforco)
    except ErroIA:
        raise
    except Exception as e:  # cada SDK tem as suas exceções; para quem usa, interessa a mensagem
        raise ErroIA(_mensagem_de_erro(nome, e)) from e


def _claude(sistema, mensagem, max_tokens, esforco) -> Escrita:
    import anthropic

    resposta = anthropic.Anthropic(api_key=chave("claude")).messages.create(
        model=modelo(),
        max_tokens=max_tokens,
        system=sistema,
        output_config={"effort": esforco},
        messages=[{"role": "user", "content": mensagem}],
    )
    if resposta.stop_reason == "refusal":
        return Escrita("", recusou=True)
    return Escrita("".join(b.text for b in resposta.content if b.type == "text"))


def _openai(sistema, mensagem, max_tokens, esforco) -> Escrita:
    import openai

    resposta = openai.OpenAI(api_key=chave("openai")).responses.create(
        model=modelo(),
        instructions=sistema,
        input=mensagem,
        max_output_tokens=max_tokens,
    )
    texto = resposta.output_text or ""
    recusou = not texto and any(
        getattr(c, "type", "") == "refusal" for item in resposta.output or [] for c in (getattr(item, "content", None) or [])
    )
    return Escrita(texto, recusou=recusou)


def _gemini(sistema, mensagem, max_tokens, esforco) -> Escrita:
    from google import genai
    from google.genai import types

    resposta = genai.Client(api_key=chave("gemini")).models.generate_content(
        model=modelo(),
        contents=mensagem,
        config=types.GenerateContentConfig(system_instruction=sistema, max_output_tokens=max_tokens),
    )
    bloqueada = getattr(getattr(resposta, "prompt_feedback", None), "block_reason", None)
    texto = resposta.text or ""
    return Escrita(texto, recusou=bool(bloqueada) and not texto)


_ESCREVER = {"claude": _claude, "openai": _openai, "gemini": _gemini}


def validar(nome: str, chave_dada: str, modelo_dado: str | None = None) -> tuple[bool, str]:
    """Confirma a chave e o modelo sem gastar créditos (pede só a ficha do modelo)."""
    if nome not in PROVEDORES:
        return False, f"IA desconhecida: {nome}"
    modelo_dado = modelo_dado or PROVEDORES[nome]["modelo"]
    try:
        if nome == "claude":
            import anthropic

            anthropic.Anthropic(api_key=chave_dada).models.retrieve(modelo_dado)
        elif nome == "openai":
            import openai

            openai.OpenAI(api_key=chave_dada).models.retrieve(modelo_dado)
        else:
            from google import genai

            genai.Client(api_key=chave_dada).models.get(model=modelo_dado)
    except Exception as e:
        return False, _mensagem_de_erro(nome, e)
    return True, f"Chave válida e modelo {modelo_dado} disponível."


def _mensagem_de_erro(nome: str, e: Exception) -> str:
    """Uma frase simples a partir do erro do SDK (sem o texto técnico todo)."""
    estado = getattr(e, "status_code", None) or getattr(e, "code", None) or getattr(getattr(e, "response", None), "status_code", None)
    texto = str(e).lower()
    ia = PROVEDORES[nome]["nome"]
    if estado in (401, 403) or "api key" in texto or "authentication" in texto or "x-api-key" in texto:
        return f"A chave da {ia} não é válida (ou foi apagada). Confirma que a copiaste toda."
    if estado == 404 or "not found" in texto or "does not exist" in texto:
        return f"O modelo pedido não existe ou a tua conta da {ia} não tem acesso a ele. Escolhe outro nas Definições."
    if estado == 429 or "rate" in texto or "quota" in texto:
        return f"A {ia} recusou por excesso de pedidos ou quota esgotada. Espera um pouco ou confirma a quota na tua conta."
    if "credit" in texto or "billing" in texto or "balance" in texto or estado == 402:
        return f"A conta da {ia} não tem créditos. Carrega créditos na conta."
    if "connect" in texto or "timeout" in texto or "network" in texto or "resolve" in texto:
        return f"Sem ligação à {ia}. Confirma a internet."
    return f"A {ia} devolveu um erro: {str(e)[:200]}"
