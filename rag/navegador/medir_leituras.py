"""Quanto do índice cada pergunta lê: páginas, bytes e pedidos, se o índice estivesse na internet.

    python rag/navegador/medir_leituras.py <indice.sqlite>   (precisa do pacote `apsw`)

Repete as consultas gravadas por `rag.navegador.consultas` sobre o índice, através de uma VFS do
SQLite que conta cada leitura. Num browser, cada página que não está em cache seria pedida por HTTP
Range; páginas seguidas podem ir num só pedido. Mede-se:

- `paginas`: páginas distintas lidas na pergunta (cache vazia);
- `pedidos`: grupos de páginas seguidas, pela ordem de leitura (um pedido por grupo, o melhor caso);
- `novas`: páginas que ainda não tinham sido lidas nas perguntas anteriores (cache aquecida no browser).
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from urllib.parse import quote

import apsw


PASTA = Path(__file__).resolve().parent / "resultados"


class Contador(apsw.VFS):
    def __init__(self):
        self.leituras: list[tuple[int, int]] = []
        super().__init__("contador", "")

    def xOpen(self, nome, flags):
        return Ficheiro(self, nome, flags)


class Ficheiro(apsw.VFSFile):
    def __init__(self, vfs, nome, flags):
        self.vfs = vfs
        super().__init__("", nome, flags)

    def xRead(self, quantidade, posicao):
        self.vfs.leituras.append((posicao, quantidade))
        return super().xRead(quantidade, posicao)


def abrir(caminho: str, vfs: Contador) -> apsw.Connection:
    con = apsw.Connection(f"file:{quote(caminho)}?mode=ro", flags=apsw.SQLITE_OPEN_READONLY | apsw.SQLITE_OPEN_URI, vfs="contador")
    con.execute("PRAGMA cache_size = -200000")  # 200 MB: dentro da pergunta, cada página só se lê uma vez
    con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.vocab USING fts5vocab(main, pedacos_fts, 'row')")
    return con


def paginas_e_pedidos(leituras: list[tuple[int, int]], tamanho: int) -> tuple[list[int], int]:
    ordem: list[int] = []
    vistas: set[int] = set()
    for posicao, quantidade in leituras:
        for p in range(posicao // tamanho, (posicao + quantidade - 1) // tamanho + 1):
            if p not in vistas:
                vistas.add(p)
                ordem.append(p)
    pedidos = sum(1 for i, p in enumerate(ordem) if i == 0 or p != ordem[i - 1] + 1)
    return ordem, pedidos


def main() -> None:
    caminho = sys.argv[1]
    vfs = Contador()
    tamanho = abrir(caminho, vfs).execute("PRAGMA page_size").fetchone()[0]
    ja_lidas: set[int] = set()
    linhas = []
    for linha in (PASTA / "consultas.jsonl").open(encoding="utf-8"):
        q = json.loads(linha)
        con = abrir(caminho, vfs)  # ligação nova: a cache do SQLite começa vazia em cada pergunta
        vfs.leituras = []
        for c in q["consultas"]:
            con.execute(c["sql"], c["parametros"]).fetchall()
        ordem, pedidos = paginas_e_pedidos(vfs.leituras, tamanho)
        novas = len(set(ordem) - ja_lidas)
        ja_lidas |= set(ordem)
        linhas.append({"id": q["id"], "consultas": len(q["consultas"]), "paginas": len(ordem), "mb": round(len(ordem) * tamanho / 1e6, 1), "pedidos": pedidos, "novas_mb": round(novas * tamanho / 1e6, 1), "ms_local": q["ms"]})
        con.close()
        print(f"{q['id']:>10}  {len(q['consultas']):>5} consultas  {linhas[-1]['mb']:7.1f} MB  {pedidos:>6} pedidos  {linhas[-1]['novas_mb']:7.1f} MB novos")

    def resumo(campo):
        valores = sorted(x[campo] for x in linhas)
        return {"mediana": statistics.median(valores), "p90": valores[int(0.9 * (len(valores) - 1))], "max": valores[-1]}

    total = {"perguntas": len(linhas), "pagina_bytes": tamanho, **{c: resumo(c) for c in ("consultas", "mb", "pedidos", "novas_mb", "ms_local")}, "cache_total_mb": round(len(ja_lidas) * tamanho / 1e6, 1)}
    (PASTA / "leituras.json").write_text(json.dumps({"resumo": total, "perguntas": linhas}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(total, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
