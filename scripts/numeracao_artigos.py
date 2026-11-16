"""Títulos de artigo fora de sequência no acervo: n-1, X, n+1 com X diferente de n.

Exemplo: no DRR 2/2005/M o DRE escreve «Artigo 212.º» entre o 20.º e o 22.º. É o 21.º, mas
a chave do artigo fica «212.º» e uma pergunta sobre o art. 21.º não o encontra.

Só lê os títulos `###### Artigo N.º` com número inteiro. Cada suspeita leva um tipo:
- `gralha`: X não é vizinho de nada (20.º, 212.º, 22.º);
- `repetido`: X repete o anterior ou o seguinte (2.º, 2.º, 4.º);
- `troca`: duas suspeitas seguidas no mesmo diploma (82.º, 81.º, 84.º, 83.º), números trocados
  ou um artigo fora do lugar. Não se corrige sem ler.

Uso: `python scripts/numeracao_artigos.py data > reports/numeracao_artigos_suspeitas.jsonl`
"""

from __future__ import annotations

import json
import os
import re
import sys


_TITULO = re.compile(r"^###### Artigo (\d+)\.º(?:\s|$)", re.M)


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


def main(raiz: str) -> None:
    for pasta, _, ficheiros in sorted(os.walk(raiz)):
        for nome in sorted(ficheiros):
            if not nome.endswith(".md"):
                continue
            caminho = os.path.join(pasta, nome)
            with open(caminho, encoding="utf-8") as f:
                numeros = [int(n) for n in _TITULO.findall(f.read())]
            for s in suspeitas(numeros):
                print(json.dumps({"path": caminho, **s}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data")
