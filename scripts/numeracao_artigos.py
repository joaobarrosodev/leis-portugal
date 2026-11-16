"""Títulos de artigo fora de sequência no acervo: n-1, X, n+1 com X diferente de n.

Exemplo: no DRR 2/2005/M o DRE escrevia «Artigo 212.º» entre o 20.º e o 22.º. É o 21.º, mas
a chave do artigo ficava «212.º» e uma pergunta sobre o art. 21.º não o encontrava.

Só lê os títulos `###### Artigo N.º` com número inteiro, pela ordem do registo inteiro, sem
separar os anexos. Cada suspeita leva um tipo:
- `gralha`: X não é vizinho de nada (20.º, 212.º, 22.º);
- `repetido`: X repete o anterior ou o seguinte (2.º, 2.º, 4.º);
- `troca`: duas suspeitas seguidas no mesmo diploma (82.º, 81.º, 84.º, 83.º), números trocados
  ou um artigo fora do lugar. Não se corrige sem ler.

O `motivo` diz porque é que a suspeita não foi corrigida. As regras estão em
`src/leis_portugal/domain/numbering.py`; a correção do acervo, em `scripts/corrigir_numeracao.py`.

Uso: `python scripts/numeracao_artigos.py data > reports/numeracao_artigos_suspeitas.jsonl`
"""

from __future__ import annotations

import json
import os
import re
import sys

from leis_portugal.domain.articles import body
from leis_portugal.domain.numbering import review_numbers


_TITULO = re.compile(r"^###### Artigo (\d+)\.º(?:\s|$)")


def suspeitas(numeros: list[int]) -> list[dict]:
    """As posições fora de sequência numa lista de números de artigo, pela ordem do texto."""
    achadas = []
    for i in range(1, len(numeros) - 1):
        antes, lido, depois = numeros[i - 1], numeros[i], numeros[i + 1]
        if depois == antes + 2 and lido != antes + 1:
            tipo = "repetido" if lido in (antes, depois) else "gralha"
            achadas.append({"posicao": i, "antes": antes, "lido": lido, "depois": depois, "provavel": antes + 1, "tipo": tipo})
    for a, b in zip(achadas, achadas[1:], strict=False):
        if b["posicao"] - a["posicao"] <= 2:
            a["tipo"] = b["tipo"] = "troca"
    return achadas


_LETRA = re.compile(r"^###### Artigo \d+\.º(?: [A-Z]| ?‐ ?[A-Z])(?:\s|$)")


def motivo(caminho: str, titulos: list[str], linha: int, revisao: dict[int, str | None]) -> str:
    """`titulos`: o título suspeito e os dois vizinhos."""
    if any(_LETRA.match(titulo) for titulo in titulos):
        return "artigo aditado com letra («78.º A», «292.º ‐A»): não é gralha, mas o articles.py não lê esta forma"
    if linha not in revisao:
        razao = "a sequência atravessa um anexo ou uma parte: são números de partes diferentes"
    else:
        razao = revisao[linha] or "corrigível: falta correr scripts/corrigir_numeracao.py"
    if f"{os.sep}european_union{os.sep}" in caminho:
        return f"UE (EUR-Lex, fora desta correção): {razao}"
    return razao


def main(raiz: str) -> None:
    for pasta, _, ficheiros in sorted(os.walk(raiz)):
        for nome in sorted(ficheiros):
            if not nome.endswith(".md"):
                continue
            caminho = os.path.join(pasta, nome)
            with open(caminho, encoding="utf-8") as f:
                texto = body(f.read())
            if "###### Artigo" not in texto:
                continue
            todas = texto.split("\n")
            linhas = [(i, int(m.group(1))) for i, linha in enumerate(todas) if (m := _TITULO.match(linha))]
            achadas = suspeitas([n for _, n in linhas])
            if not achadas:
                continue
            revisao = {fix.line: razao for fix, razao in review_numbers(texto, repeated=True)}
            for s in achadas:
                linha = linhas[s["posicao"]][0]
                print(json.dumps({"path": caminho, **s, "motivo": motivo(caminho, [todas[linhas[p][0]] for p in range(s["posicao"] - 1, s["posicao"] + 2)], linha, revisao)}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
