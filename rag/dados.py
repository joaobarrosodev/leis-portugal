"""O índice pronto a descarregar: publicar uma versão e, na aplicação, descarregá-la e atualizá-la.

A aplicação não tem o repositório nem o git: descarrega o índice já feito (`indice.sqlite`,
comprimido em gzip) a partir de um manifesto `versao.json`:

    {"versao": "2026-11-12", "metodo_termos": "...", "ficheiros": [
      {"nome": "indice.sqlite", "url": "…/indice.sqlite.gz", "bytes": N, "sha256": "…", "bytes_descomprimido": M}]}

- `RAG_DADOS_URL`: o endereço do manifesto (por omissão `MANIFESTO`, vazio até haver publicação).
- A descarga retoma onde parou (pedidos HTTP Range), confirma o sha256, descomprime para um
  ficheiro temporário e só então troca o índice (a versão antiga continua a servir até lá).
- Os modelos de pesquisa (~0,6 GB) descarregam-se sozinhos na primeira pergunta (`rag.modelos`).

Publicar (no repositório, depois de `python -m rag.indice`):

    python -m rag.dados publicar --url-base https://…/resolve/main/ --saida dist/dados

grava `indice.sqlite.gz` e `versao.json` em `dist/dados/`, para carregar no alojamento escolhido.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path


MANIFESTO = ""  # o endereço público do versao.json, quando o índice for publicado
BLOCO = 1024 * 1024


@dataclass
class Progresso:
    fase: str = ""  # "a descarregar", "a verificar", "a descomprimir", "pronto", "erro"
    feito: int = 0
    total: int = 0
    mensagem: str = ""


def url_manifesto() -> str:
    return os.environ.get("RAG_DADOS_URL") or MANIFESTO


def versao_local(pasta: Path) -> dict:
    try:
        return json.loads((pasta / "versao.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def ler_manifesto(url: str | None = None) -> dict:
    import requests

    url = url or url_manifesto()
    if not url:
        raise RuntimeError("O índice ainda não foi publicado para descarregar.")
    resposta = requests.get(url, timeout=30)
    resposta.raise_for_status()
    return resposta.json()


def ha_atualizacao(pasta: Path) -> dict | None:
    """O manifesto, se for mais recente do que o que está na pasta."""
    manifesto = ler_manifesto()
    return manifesto if manifesto.get("versao", "") > versao_local(pasta).get("versao", "") else None


def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(BLOCO), b""):
            h.update(bloco)
    return h.hexdigest()


def descarregar(pasta: Path, progresso: Progresso | None = None, manifesto: dict | None = None, antes_de_trocar=None) -> dict:
    """Descarrega a versão do manifesto para `pasta` (onde o `rag` lê o índice: RAG_INDICE).

    `antes_de_trocar()` é chamada antes de substituir cada ficheiro: no Windows, um ficheiro aberto
    não se pode substituir, por isso quem o tem aberto fecha-o aí."""
    import requests

    progresso = progresso or Progresso()
    manifesto = manifesto or ler_manifesto()
    pasta.mkdir(parents=True, exist_ok=True)
    precisa = sum(f["bytes"] + f.get("bytes_descomprimido", f["bytes"]) for f in manifesto["ficheiros"])
    livre = shutil.disk_usage(pasta).free
    if livre < precisa:
        raise RuntimeError(f"Falta espaço em disco: são precisos {precisa / 1e9:.1f} GB livres e há {livre / 1e9:.1f} GB.")
    progresso.total = sum(f["bytes"] for f in manifesto["ficheiros"])
    progresso.feito = 0
    for ficheiro in manifesto["ficheiros"]:
        comprimido = pasta / (ficheiro["nome"] + ".gz.parte")
        ja = comprimido.stat().st_size if comprimido.exists() else 0
        if ja > ficheiro["bytes"]:
            comprimido.unlink()
            ja = 0
        progresso.fase = "a descarregar"
        if ja < ficheiro["bytes"]:
            cabecalhos = {"Range": f"bytes={ja}-"} if ja else {}
            with requests.get(ficheiro["url"], headers=cabecalhos, stream=True, timeout=60) as r:
                r.raise_for_status()
                if ja and r.status_code != 206:  # o servidor não retoma: começa do zero
                    ja = 0
                with comprimido.open("ab" if ja else "wb") as f:
                    progresso.feito += ja
                    for bloco in r.iter_content(BLOCO):
                        f.write(bloco)
                        progresso.feito += len(bloco)
        else:
            progresso.feito += ja
        progresso.fase = "a verificar"
        if _sha256(comprimido) != ficheiro["sha256"]:
            comprimido.unlink()
            raise RuntimeError(f"{ficheiro['nome']} chegou corrompido; tenta outra vez.")
        progresso.fase = "a descomprimir"
        novo = pasta / (ficheiro["nome"] + ".novo")
        with gzip.open(comprimido, "rb") as origem, novo.open("wb") as destino:
            shutil.copyfileobj(origem, destino, BLOCO)
        if antes_de_trocar:
            antes_de_trocar()
        os.replace(novo, pasta / ficheiro["nome"])
        comprimido.unlink()
    (pasta / "versao.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    progresso.fase = "pronto"
    return manifesto


def publicar(indice: Path, saida: Path, url_base: str, versao: str | None = None) -> dict:
    """Comprime o índice e escreve o `versao.json` com o tamanho e o sha256."""
    saida.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(f"file:{indice}?mode=ro", uri=True) as con:
        meta = dict(con.execute("SELECT chave, valor FROM meta"))
    comprimido = saida / "indice.sqlite.gz"
    with indice.open("rb") as origem, gzip.open(comprimido, "wb", compresslevel=6) as destino:
        shutil.copyfileobj(origem, destino, BLOCO)
    manifesto = {
        "versao": versao or date.today().isoformat(),
        "metodo_termos": meta.get("metodo_termos"),
        "ficheiros": [
            {
                "nome": "indice.sqlite",
                "url": url_base.rstrip("/") + "/indice.sqlite.gz",
                "bytes": comprimido.stat().st_size,
                "sha256": _sha256(comprimido),
                "bytes_descomprimido": indice.stat().st_size,
            }
        ],
    }
    (saida / "versao.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifesto


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("publicar", help="Comprimir o índice e escrever o versao.json.")
    p.add_argument("--indice", type=Path, default=None)
    p.add_argument("--saida", type=Path, default=Path("dist/dados"))
    p.add_argument("--url-base", required=True, help="Onde o indice.sqlite.gz vai ficar público.")
    p.add_argument("--versao")
    d = sub.add_parser("descarregar", help="Descarregar a versão publicada (como faz a aplicação).")
    d.add_argument("--pasta", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.comando == "publicar":
        from rag.fontes import PASTA_INDICE

        m = publicar(args.indice or PASTA_INDICE / "indice.sqlite", args.saida, args.url_base, args.versao)
        f = m["ficheiros"][0]
        print(f"{args.saida}/indice.sqlite.gz: {f['bytes'] / 1e9:.2f} GB (de {f['bytes_descomprimido'] / 1e9:.2f} GB), versão {m['versao']}")
    else:
        descarregar(args.pasta)
        print(f"Pronto em {args.pasta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
