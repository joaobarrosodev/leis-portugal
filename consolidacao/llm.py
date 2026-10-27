"""As alterações que as regras não aplicam, com um LLM (API da Anthropic).

Lê `consolidacao/pendentes.jsonl` (escrito por `consolidar.py`) e, por diploma, pede ao modelo
a nova redação dos artigos em causa, em JSON. Cada resposta passa pela verificação letra a
letra das regras (cada parágrafo vem do diploma que altera ou do original) e fica gravada com
os problemas encontrados. Juntar as respostas aprovadas ao consolidado e à entrada às cegas é o
passo seguinte, quando houver respostas (não houve chave da API no piloto).

Sem chave da API, `--estimar` (o modo por omissão) só conta os pedidos e estima os tokens e o
custo. Com `ANTHROPIC_API_KEY` e o pacote `anthropic` instalado, `--executar` faz os pedidos
e grava as respostas em `consolidacao/llm/`.

Sem a API, uma sessão do Claude pode fazer o mesmo: `--sessao` escreve
`consolidacao/llm/entrada-sessao.jsonl` (uma linha por diploma, com as regras em `regras` e o
pedido em `pedido`) e `--importar FICHEIRO` passa as respostas da sessão (uma linha por
diploma, `{"id", "artigos", "nao_aplicavel"}`) pela mesma verificação e grava-as em
`consolidacao/llm/`, como `--executar`.

**Escala (`--escala`):** lê `pendentes-escala.jsonl` e `selecao-escala.jsonl`. Com `--sessao`,
os diplomas vão ordenados por citações recebidas (os mais citados primeiro) em lotes de `--lote`,
`llm/entrada-sessao-escala-001.jsonl`, `-002`, … Um diploma com vários alteradores leva as
instruções por ordem de aplicação, cada uma com o diploma de que vem.

Uso: `python consolidacao/llm.py [--estimar | --executar | --sessao | --importar FICHEIRO] [--modelo claude-opus-5-5] [--escala] [--lote 40]`.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from texto import RAIZ, corpo, publicado

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


def _alteradores(selecao: dict) -> list[dict]:
    return selecao.get("alteradores") or [selecao["alterador"]]


def pedido(diploma: dict, selecao: dict) -> str:
    """O conteúdo do pedido para um diploma: os artigos do original e as instruções."""
    alteradores = [a for a in _alteradores(selecao) if a.get("path")]
    if len(alteradores) > 1:
        titulos = [a.get("title") or a["id"] for a in alteradores]
        partes = [f"Diploma original: {diploma['title']}", f"Diplomas que alteram, por ordem de aplicação: {'; '.join(titulos)}", ""]
    else:
        partes = [f"Diploma original: {diploma['title']}", f"Diploma que altera: {alteradores[0].get('title')}", ""]
    artigos = {a["chave"]: a["texto"] for item in diploma["itens"] for a in item["artigos_original"]}
    if artigos:
        partes.append("## Artigos do original")
        partes += [f"### {chave}\n{texto}\n" for chave, texto in artigos.items()]
    else:
        # Original sem artigos identificados: vai o texto inteiro.
        partes += ["## Texto do original", publicado(RAIZ / selecao["path"])]
    partes.append("## Instruções do diploma que altera")
    for i, item in enumerate(diploma["itens"], 1):
        origem = f" ({item['alterador']})" if len(alteradores) > 1 and item.get("alterador") else ""
        partes.append(f"### Instrução {i}{origem}\n{item['excerto']}\n")
    return "\n".join(partes)


def verificar_resposta(resultado: dict, diploma: dict, selecao: dict) -> list[str]:
    """Cada parágrafo devolvido vem, letra a letra, do diploma que altera ou do original."""
    from verificar import _REVOGADO, _plano

    alteradores = [_plano(publicado(RAIZ / a["path"])) for a in _alteradores(selecao) if a.get("path")]
    original = _plano(publicado(RAIZ / selecao["path"]))
    problemas = []
    for artigo in resultado.get("artigos", []):
        for p in (x.strip() for x in artigo["texto"].split("\n\n") if x.strip()):
            if not _REVOGADO.match(p) and not any(_plano(p) in a for a in alteradores) and _plano(p) not in original:
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


def _linha_sessao(d: dict, selecao: dict) -> dict:
    alteradores = [a.get("title") or a["id"] for a in _alteradores(selecao) if a.get("path")]
    return {
        "id": d["id"], "titulo": d["title"], "alterador": "; ".join(alteradores),
        "citacoes": selecao.get("citacoes", 0),
        "motivos": sorted({item["motivo"] for item in d["itens"]}),
        "regras": SISTEMA, "esquema_da_resposta": ESQUEMA, "pedido": pedido(d, selecao),
    }


def sessao(pendentes: list[dict], selecao: dict[str, dict]) -> Path:
    """A entrada para uma sessão do Claude aplicar as instruções, sem a API."""
    SAIDA.mkdir(exist_ok=True)
    destino = SAIDA / "entrada-sessao.jsonl"
    with destino.open("w", encoding="utf-8") as f:
        for d in pendentes:
            f.write(json.dumps(_linha_sessao(d, selecao[d["id"]]), ensure_ascii=False) + "\n")
    return destino


def sessao_escala(pendentes: list[dict], selecao: dict[str, dict], lote: int) -> list[Path]:
    """A entrada para uma sessão do Claude, por lotes, os mais citados primeiro."""
    SAIDA.mkdir(exist_ok=True)
    for antigo in SAIDA.glob("entrada-sessao-escala-*.jsonl"):
        antigo.unlink()
    ordenados = sorted(pendentes, key=lambda d: (-selecao[d["id"]].get("citacoes", 0), d["id"]))
    destinos = []
    for n, inicio in enumerate(range(0, len(ordenados), lote), 1):
        destino = SAIDA / f"entrada-sessao-escala-{n:03d}.jsonl"
        with destino.open("w", encoding="utf-8") as f:
            for d in ordenados[inicio : inicio + lote]:
                f.write(json.dumps(_linha_sessao(d, selecao[d["id"]]), ensure_ascii=False) + "\n")
        destinos.append(destino)
    return destinos


def importar(ficheiro: Path, pendentes: list[dict], selecao: dict[str, dict], modelo: str) -> dict:
    """As respostas de uma sessão, com a mesma verificação das respostas da API."""
    por_id = {d["id"]: d for d in pendentes}
    SAIDA.mkdir(exist_ok=True)
    contagem = Counter()
    for linha in ficheiro.read_text(encoding="utf-8").splitlines():
        resultado = json.loads(linha)
        d = por_id[resultado["id"]]
        resultado |= {"modelo": resultado.get("modelo") or modelo, "pedido": "sessão"}
        resultado["problemas"] = verificar_resposta(resultado, d, selecao[d["id"]])
        contagem["com problemas" if resultado["problemas"] else "não aplicável" if not resultado.get("artigos") else "sem problemas"] += 1
        (SAIDA / (d["id"].replace(":", "_") + ".json")).write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dict(contagem)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--estimar", action="store_true", default=True)
    modo.add_argument("--executar", action="store_true")
    modo.add_argument("--sessao", action="store_true")
    modo.add_argument("--importar", type=Path)
    parser.add_argument("--modelo", default="claude-opus-5-5")
    parser.add_argument("--pendentes", type=Path, default=None)
    parser.add_argument("--escala", action="store_true", help="pendentes-escala.jsonl e selecao-escala.jsonl")
    parser.add_argument("--lote", type=int, default=40, help="escala, com --sessao: diplomas por ficheiro")
    args = parser.parse_args()
    ficheiro_pendentes = args.pendentes or (PASTA / ("pendentes-escala.jsonl" if args.escala else "pendentes.jsonl"))
    pendentes = [json.loads(l) for l in ficheiro_pendentes.read_text(encoding="utf-8").splitlines()]
    ficheiro_selecao = PASTA / ("selecao-escala.jsonl" if args.escala else "selecao.jsonl")
    selecao = {r["id"]: r for r in map(json.loads, ficheiro_selecao.read_text(encoding="utf-8").splitlines())}
    if args.sessao and args.escala:
        destinos = sessao_escala(pendentes, selecao, args.lote)
        print(f"{len(pendentes)} diplomas em {len(destinos)} lotes de até {args.lote}: {SAIDA.relative_to(RAIZ)}/entrada-sessao-escala-NNN.jsonl")
        return 0
    if args.sessao:
        print(f"{len(pendentes)} diplomas em {sessao(pendentes, selecao).relative_to(RAIZ)}")
        return 0
    if args.importar:
        print(json.dumps(importar(args.importar, pendentes, selecao, args.modelo), ensure_ascii=False, indent=2))
        return 0
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
