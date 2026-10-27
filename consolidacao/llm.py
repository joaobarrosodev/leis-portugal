"""As alterações que as regras não aplicam, com um LLM (API da Anthropic).

Lê `consolidacao/pendentes.jsonl` (escrito por `consolidar.py`) e, por diploma, pede ao modelo
a nova redação dos artigos em causa, em JSON. Cada resposta passa pela verificação letra a
letra das regras (cada parágrafo vem do diploma que altera ou do original) e fica gravada com
os problemas encontrados. Juntar as respostas aprovadas ao consolidado e à entrada às cegas é o
passo seguinte, quando houver respostas (não houve chave da API no piloto).

Sem chave da API, `--estimar` (o modo por omissão) só conta os pedidos e estima os tokens e o
custo. Com `ANTHROPIC_API_KEY` e o pacote `anthropic` instalado, `--executar` faz os pedidos
e grava as respostas em `consolidacao/llm/`.

Uso: `python consolidacao/llm.py [--estimar | --executar] [--modelo claude-opus-5-5]`.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from texto import RAIZ, corpo

PASTA = RAIZ / "consolidacao"
SAIDA = PASTA / "llm"

# Preços por milhão de tokens (entrada, saída), da tabela da API em 2026-10.
PRECOS = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00)}
CARACTERES_POR_TOKEN = 3.5  # português legislativo; a contagem exata faz-se com count_tokens
PENSAMENTO_POR_PEDIDO = 2000  # tokens de saída de raciocínio, estimativa para effort "medium"

SISTEMA = """Aplicas alterações legislativas portuguesas ao texto original de um diploma.

Recebes o texto atual dos artigos do original e a instrução do diploma que os altera
(substituição de redação, aditamento, revogação, retificação). Devolves a nova redação de
cada artigo que a instrução altera, e só desses.

Regras:
- O texto novo copia-se letra a letra do diploma que altera; o que a instrução não muda
  copia-se letra a letra do original. Não corrijas grafia, pontuação nem gralhas.
- "[...]", "..." ou "(...)" numa nova redação querem dizer "fica o texto original dessa
  unidade" (número, alínea ou epígrafe). "[Anterior n.º 2]" quer dizer que o antigo n.º 2
  passa para aqui com o novo número.
- Um artigo revogado fica com o corpo "(Revogado.)"; um número "N - (Revogado.)"; uma alínea
  "a) (Revogada.)".
- Um artigo por elemento de "artigos", com a chave tal como a recebes ("3.º" ou
  "Anexo …::3.º"), a epígrafe e o corpo (parágrafos separados por uma linha em branco, sem o
  título "Artigo N.º").
- Se a instrução não se puder aplicar com segurança (alvo ambíguo, texto que não existe no
  original, alteração que não é textual), devolve "artigos" vazio e explica em "nao_aplicavel".
"""

ESQUEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["artigos", "nao_aplicavel"],
    "properties": {
        "artigos": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["chave", "epigrafe", "texto"],
                "properties": {"chave": {"type": "string"}, "epigrafe": {"type": "string"}, "texto": {"type": "string"}},
            },
        },
        "nao_aplicavel": {"type": ["string", "null"]},
    },
}


def pedido(diploma: dict, selecao: dict) -> str:
    """O conteúdo do pedido para um diploma: os artigos do original e as instruções."""
    partes = [f"Diploma original: {diploma['title']}", f"Diploma que altera: {selecao['alterador'].get('title')}", ""]
    artigos = {a["chave"]: a["texto"] for item in diploma["itens"] for a in item["artigos_original"]}
    if artigos:
        partes.append("## Artigos do original")
        partes += [f"### {chave}\n{texto}\n" for chave, texto in artigos.items()]
    else:
        # Original sem artigos identificados: vai o texto inteiro.
        partes += ["## Texto do original", corpo((RAIZ / selecao["path"]).read_text(encoding="utf-8"))]
    partes.append("## Instruções do diploma que altera")
    partes += [f"### Instrução {i}\n{item['excerto']}\n" for i, item in enumerate(diploma["itens"], 1)]
    return "\n".join(partes)


def verificar_resposta(resultado: dict, diploma: dict, selecao: dict) -> list[str]:
    """Cada parágrafo devolvido vem, letra a letra, do diploma que altera ou do original."""
    from verificar import _REVOGADO, _plano

    alterador = _plano(corpo((RAIZ / selecao["alterador"]["path"]).read_text(encoding="utf-8")))
    original = _plano(corpo((RAIZ / selecao["path"]).read_text(encoding="utf-8")))
    problemas = []
    for artigo in resultado.get("artigos", []):
        for p in (x.strip() for x in artigo["texto"].split("\n\n") if x.strip()):
            if not _REVOGADO.match(p) and _plano(p) not in alterador and _plano(p) not in original:
                problemas.append(f"{artigo['chave']}: parágrafo que não está no alterador nem no original: {p[:80]}")
    return problemas


def estimar(pendentes: list[dict], selecao: dict[str, dict]) -> dict:
    entrada = saida = 0
    for d in pendentes:
        texto = pedido(d, selecao[d["id"]])
        entrada += (len(SISTEMA) + len(texto)) / CARACTERES_POR_TOKEN
        artigos = sum(len(a["texto"]) for item in d["itens"] for a in item["artigos_original"])
        citado = sum(len(item["excerto"]) for item in d["itens"])
        saida += (artigos + citado) / CARACTERES_POR_TOKEN + PENSAMENTO_POR_PEDIDO
    return {
        "pedidos": len(pendentes),
        "tokens_entrada_estimados": round(entrada),
        "tokens_saida_estimados": round(saida),
        "custo_estimado_usd": {m: round(entrada / 1e6 * p[0] + saida / 1e6 * p[1], 2) for m, p in PRECOS.items()},
        "motivos": dict(Counter(item["motivo"] for d in pendentes for item in d["itens"])),
    }


def executar(pendentes: list[dict], selecao: dict[str, dict], modelo: str) -> dict:
    import anthropic  # só é preciso com --executar

    client = anthropic.Anthropic()
    SAIDA.mkdir(exist_ok=True)
    uso = Counter()

    def um(d: dict) -> None:
        resposta = client.beta.messages.create(
            model=modelo,
            max_tokens=16000,
            system=SISTEMA,
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": ESQUEMA}},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": pedido(d, selecao[d["id"]])}],
        )
        uso["pedidos"] += 1
        uso["tokens_entrada"] += resposta.usage.input_tokens
        uso["tokens_saida"] += resposta.usage.output_tokens
        if resposta.stop_reason == "refusal":
            resultado = {"erro": "recusa", "detalhe": str(resposta.stop_details)}
        elif resposta.stop_reason == "max_tokens":
            resultado = {"erro": "resposta cortada (max_tokens)"}
        else:
            texto = next((b.text for b in resposta.content if b.type == "text"), "")
            resultado = json.loads(texto)
        resultado |= {"id": d["id"], "modelo": resposta.model, "pedido": resposta._request_id}
        resultado["problemas"] = verificar_resposta(resultado, d, selecao[d["id"]])
        nome = d["id"].replace(":", "_") + ".json"
        (SAIDA / nome).write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with ThreadPoolExecutor(max_workers=4) as conjunto:
        list(conjunto.map(um, pendentes))
    return dict(uso)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--estimar", action="store_true", default=True)
    modo.add_argument("--executar", action="store_true")
    parser.add_argument("--modelo", default="claude-opus-5-5")
    parser.add_argument("--pendentes", type=Path, default=PASTA / "pendentes.jsonl")
    args = parser.parse_args()
    pendentes = [json.loads(l) for l in args.pendentes.read_text(encoding="utf-8").splitlines()]
    selecao = {r["id"]: r for r in map(json.loads, (PASTA / "selecao.jsonl").read_text(encoding="utf-8").splitlines())}
    if args.executar:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Sem ANTHROPIC_API_KEY no ambiente: corre com --estimar ou define a chave.")
            return 1
        print(json.dumps(executar(pendentes, selecao, args.modelo), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(estimar(pendentes, selecao), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
