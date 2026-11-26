"""O «contexto ideal» de cada caso: os artigos essenciais e úteis da referência e os das leis pensadas, numa ordem baralhada, no mesmo
formato da exportação do `medir.py`. Quem responde não sabe que são os certos: mede-se o raciocínio sem a pesquisa.

    python avaliacao/casos/exportar_ideal.py PASTA
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from medir import texto_inteiro  # noqa: E402
from rag.fontes import corpo, ler_artigos  # noqa: E402
from rag.resposta import CARACTERES_POR_ARTIGO  # noqa: E402


def main() -> int:
    pasta = Path(sys.argv[1])
    casos = [json.loads(l) for l in (RAIZ / "avaliacao" / "casos" / "casos.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    lidos: dict[str, list] = {}
    saida = []
    for caso in casos:
        refs = caso["resposta"]["artigos_essenciais"] + caso["resposta"].get("artigos_uteis", []) + [l for l in caso.get("leis_pensadas", []) if l.get("artigo")]
        vistos, lista = set(), []
        for r in refs:
            if (r["documento"], r["artigo"]) in vistos:
                continue
            vistos.add((r["documento"], r["artigo"]))
            lista.append(r)
        random.Random(caso["id"]).shuffle(lista)
        blocos = []
        for n, r in enumerate(lista, 1):
            if r["caminho"] not in lidos:
                lidos[r["caminho"]] = ler_artigos(corpo((RAIZ / r["caminho"]).read_text(encoding="utf-8")))
            a = next(a for a in lidos[r["caminho"]] if a.chave == r["artigo"])
            rotulo = f"{r['titulo']}, art. {a.numero}" + (f" ({a.parte})" if a.parte else "") + (f" — {a.epigrafe}" if a.epigrafe else "")
            blocos.append(f"[{n}] {rotulo}\n{a.texto[:CARACTERES_POR_ARTIGO]}")
        saida.append({"id": caso["id"], "data_referencia": caso["data_referencia"], "pedido": texto_inteiro(caso),
                      "artigos": "\n\n".join(blocos), "chaves": [[r["documento"], r["artigo"]] for r in lista]})
    pasta.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(saida), 10):
        (pasta / f"entrada-{i // 10 + 1:02d}.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in saida[i:i + 10]), encoding="utf-8")
    print(f"{len(saida)} casos em {pasta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
