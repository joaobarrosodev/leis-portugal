"""Verificação mecânica, sem LLM: o texto antigo que fica num artigo que recebeu nova redação ou revogação.

O erro que mais se repete nas rondas da camada 1 é este: a resposta escreve a nova redação, ou
«(Revogado.)», e o corpo antigo do artigo fica a seguir. Às vezes fica depois de um título de divisão
interno, como «##### Divisão de Pessoal». A verificação às cegas deixou passar alguns, como o DR 44/80 na
ronda 116. Por isso esta verificação corre antes de aplicar ao acervo. Um artigo fica marcado quando:

- o corpo original inteiro está no fim do artigo e há texto novo antes dele; ou
- o artigo tem «(Revogado.)» e mantém parágrafos do corpo original.

Não contam as fórmulas finais e as assinaturas («Visto e aprovado…», «Promulgado…»), nem os anexos que
ficaram dentro do último artigo. Na varredura de 23/11/2026 aos 2.795 consolidados do data/ eram os
falsos positivos conhecidos. Os rótulos repetidos («1 -» duas vezes) também não marcam por si sós: nessa
varredura, 50 casos sem mais nada foram todos falsos positivos (redações de outros diplomas citadas,
artigos sem título juntos debaixo da mesma chave).

Uso:
    python consolidacao/texto_antigo.py "verificacao/entrada-piloto-116-lote-*.jsonl"
"""

from __future__ import annotations

import glob
import json
import re
import sys

TITULO = re.compile(r"^#{1,6}\s+(?:Artigo|Art\.?)\s*([0-9]+\.?\s*[º°o]?(?:-[A-Z])?)", re.I)
FECHO = re.compile(
    r"^(Visto e aprovado|Promulgad|Publique-se|Referendad|Assinatura|Presidência do Conselho de Ministros, \d|"
    r"O Presidente da República|Pelo Primeiro-Ministro|O Primeiro-Ministro, [A-ZÁÉÍÓÚ][a-záéíóú]+ [A-ZÁÉÍÓÚ]|"
    r"\[?\(ver documento original\))"
)
REVOGADO = re.compile(r"\(Revogad[oa]\.?\)\.?")
ANEXO = re.compile(r"^#{1,3} +(ANEXO|MAPA|QUADRO|TABELA)", re.M | re.I)


def _chave(numero: str) -> str:
    return re.sub(r"\s", "", numero).rstrip(".").replace("°", "º").replace("o", "º")


def artigos(texto: str) -> dict[str, str]:
    """Corpo de cada artigo, pela chave «N.º», até ao título do artigo seguinte."""
    resultado: dict[str, str] = {}
    atual, linhas = None, []
    for linha in texto.split("\n"):
        m = TITULO.match(linha)
        if m:
            if atual and atual not in resultado:
                resultado[atual] = "\n".join(linhas)
            atual, linhas = _chave(m.group(1)), []
        elif atual:
            linhas.append(linha)
    if atual and atual not in resultado:
        resultado[atual] = "\n".join(linhas)
    return resultado


def paragrafos(corpo: str) -> list[str]:
    """Os parágrafos do corpo, sem notas («> …») nem títulos de divisão («#…»)."""
    return [p.strip() for p in corpo.split("\n\n") if p.strip() and not p.strip().startswith((">", "#"))]


def marcados(original: str, consolidado: str) -> list[dict]:
    """Os artigos do consolidado que mantêm o corpo antigo a seguir à nova redação ou a «(Revogado.)»."""
    o, c = artigos(original), artigos(consolidado)
    ultimo = list(o)[-1] if o else None
    achados = []
    for chave, corpo in c.items():
        if chave not in o or corpo.strip() == o[chave].strip():
            continue
        if chave == ultimo and ANEXO.search(corpo):
            continue
        antigos_todos = [p for p in paragrafos(o[chave]) if not FECHO.search(p)]
        # o que vem a partir da primeira fórmula final do original é fecho, não corpo
        po = paragrafos(o[chave])
        i = next((k for k, p in enumerate(po) if FECHO.search(p)), None)
        if i is not None:
            antigos_todos = [p for p in po[:i]]
        pc = paragrafos(corpo)
        no_fim = (bool(antigos_todos) and len(pc) > len(antigos_todos) and pc[-len(antigos_todos):] == antigos_todos
                  and any(p not in antigos_todos for p in pc[: -len(antigos_todos)]))
        revogado = any(REVOGADO.fullmatch(p) for p in pc)
        mantidos = [p for p in pc if p in antigos_todos and len(p) >= 30 and "Revogad" not in p]
        if no_fim or (revogado and mantidos):
            achados.append({"artigo": chave, "corpo_antigo_no_fim": no_fim, "revogado_com_texto_antigo": bool(revogado and mantidos),
                            "exemplo": (mantidos or antigos_todos or [""])[0][:160]})
    return achados


def main() -> int:
    total = 0
    for f in sorted(glob.glob(sys.argv[1])):
        for linha in open(f, encoding="utf-8"):
            d = json.loads(linha)
            a = marcados(d.get("texto_original", ""), d.get("texto_consolidado", ""))
            if a:
                total += 1
                print(d["id"], d.get("titulo"), [x["artigo"] for x in a])
    print(f"{total} diplomas marcados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
