"""O índice para descarregar: uma versão completa e deltas pequenos desde ela.

A aplicação não tem o repositório nem o git. Lê o manifesto `versao.json` do alojamento
(Hugging Face, `joaobarrosodev/leis-portugal-indice`) e:

- se o índice local está numa versão da cadeia atual, descarrega só os deltas que faltam;
- senão (primeira vez, ou parado há demasiado tempo), descarrega a versão completa e os deltas.

    {"versao": "2026-11-20", "metodo_termos": "…",
     "completo": {"versao": "2026-11-13", "nome": "completo-2026-11-13.sqlite.gz", "url": "…", "bytes": N, "sha256": "…", "bytes_descomprimido": M},
     "deltas": [{"de": "2026-11-13", "para": "2026-11-20", "nome": "delta-….sqlite.gz", "url": "…", "bytes": n, "sha256": "…"}],
     "anterior": {… a versão completa anterior, só para voltar atrás …}}

**Delta.** É por diploma, não pelo ficheiro: a lista dos diplomas novos ou alterados, com as suas
linhas (`documentos`, `pedacos` sem o id, `relacoes`), e a dos que saíram. Aplicar um delta apaga as
linhas antigas desses diplomas (na tabela de pesquisa, com os mesmos termos com que entraram:
`rag.indice.textos_fts`) e insere as novas com ids seguidos no fim. A pesquisa dá os mesmos
resultados que um índice construído de raiz (`tests/test_dados.py` e `rag/navegador/equivalencia.py`).

Publicar (no repositório, depois de `python -m rag.indice`):

    python -m rag.dados publicar --versao 2026-11-20 [--completo] [--enviar]

guarda em `dist/dados/` o último índice publicado e os ficheiros, e com `--enviar` manda-os para o
Hugging Face. Fica no alojamento a versão completa atual, os deltas desde ela e a completa anterior;
o resto apaga-se e o histórico do repositório é limpo (`super_squash_history`), para o espaço não crescer.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REPOSITORIO = "joaobarrosodev/leis-portugal-indice"
URL_BASE = f"https://huggingface.co/datasets/{REPOSITORIO}/resolve/main/"
MANIFESTO = URL_BASE + "versao.json"
BLOCO = 1024 * 1024
LIMITE_DELTA = 0.3  # acima desta fração da versão completa, publica-se uma completa nova
PUBLICACAO = Path("dist") / "dados"
CARTAO = Path(__file__).resolve().parent / "dados_cartao.md"


@dataclass
class Progresso:
    fase: str = ""  # "a descarregar", "a verificar", "a descomprimir", "a aplicar", "pronto", "erro"
    feito: int = 0
    total: int = 0
    mensagem: str = ""


def url_manifesto() -> str:
    return os.environ.get("RAG_DADOS_URL", MANIFESTO)


def versao_local(pasta: Path) -> dict:
    try:
        return json.loads((pasta / "versao.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _gravar_versao_local(pasta: Path, versao: str) -> None:
    (pasta / "versao.json").write_text(json.dumps({"versao": versao}), encoding="utf-8")


def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(BLOCO), b""):
            h.update(bloco)
    return h.hexdigest()


def _gzip(origem: Path, destino: Path) -> None:
    with origem.open("rb") as o, gzip.open(destino, "wb", compresslevel=6) as d:
        shutil.copyfileobj(o, d, BLOCO)


def _gunzip(origem: Path, destino: Path) -> None:
    with gzip.open(origem, "rb") as o, destino.open("wb") as d:
        shutil.copyfileobj(o, d, BLOCO)


# ---------------------------------------------------------------------------------------- deltas

_COLUNAS_PEDACO = "documento, parte, numero, epigrafe, chave, rotulo, texto, notas, desde, ate, ordem"


def impressoes(con: sqlite3.Connection) -> dict[str, str]:
    """Uma impressão digital (sha256) por diploma: a linha em `documentos`, os pedaços (sem o id) e as relações."""
    hashes = {}
    for linha in con.execute("SELECT * FROM documentos"):
        hashes[linha[0]] = hashlib.sha256(repr(linha).encode())
    for linha in con.execute(f"SELECT {_COLUNAS_PEDACO} FROM pedacos ORDER BY id"):
        if linha[0] in hashes:
            hashes[linha[0]].update(repr(linha[1:]).encode())
    for linha in con.execute("SELECT documento, tipo, alvo, alvo_titulo, data FROM relacoes ORDER BY documento, tipo, alvo, data, alvo_titulo"):
        if linha[0] in hashes:
            hashes[linha[0]].update(b"R" + repr(linha[1:]).encode())
    return {k: v.hexdigest() for k, v in hashes.items()}


def gerar_delta(antigo: Path, novo: Path, saida: Path, de: str, para: str) -> dict:
    """Escreve em `saida` (SQLite) os diplomas que mudaram de `antigo` para `novo`."""
    with sqlite3.connect(f"file:{antigo}?mode=ro", uri=True) as a, sqlite3.connect(f"file:{novo}?mode=ro", uri=True) as n:
        metodo_a = dict(a.execute("SELECT chave, valor FROM meta")).get("metodo_termos")
        metodo_n = dict(n.execute("SELECT chave, valor FROM meta")).get("metodo_termos")
        if metodo_a != metodo_n:
            raise RuntimeError(f"Os índices usam termos diferentes ({metodo_a} e {metodo_n}): publica uma versão completa.")
        ia, inn = impressoes(a), impressoes(n)
        mudados = [d for d, h in inn.items() if ia.get(d) != h]
        removidos = [d for d in ia if d not in inn]
        saida.unlink(missing_ok=True)
        colunas_doc = [c[1] for c in n.execute("PRAGMA table_info(documentos)")]
        with sqlite3.connect(saida) as s:
            s.execute("CREATE TABLE meta (chave TEXT PRIMARY KEY, valor TEXT)")
            s.execute("CREATE TABLE removidos (id TEXT PRIMARY KEY)")
            s.execute(f"CREATE TABLE documentos ({', '.join(colunas_doc)})")
            s.execute(f"CREATE TABLE pedacos ({_COLUNAS_PEDACO})")
            s.execute("CREATE TABLE relacoes (documento, tipo, alvo, alvo_titulo, data)")
            s.executemany("INSERT INTO meta VALUES (?, ?)", [("de", de), ("para", para), ("metodo_termos", metodo_n)])
            s.executemany("INSERT INTO removidos VALUES (?)", [(d,) for d in removidos])
            marcas = ",".join("?" * len(colunas_doc))
            for i in range(0, len(mudados), 500):
                lote = mudados[i : i + 500]
                q = ",".join("?" * len(lote))
                s.executemany(f"INSERT INTO documentos VALUES ({marcas})", n.execute(f"SELECT * FROM documentos WHERE id IN ({q})", lote))
                s.executemany(
                    "INSERT INTO pedacos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    n.execute(f"SELECT {_COLUNAS_PEDACO} FROM pedacos WHERE documento IN ({q}) ORDER BY id", lote),
                )
                s.executemany(
                    "INSERT INTO relacoes VALUES (?, ?, ?, ?, ?)",
                    n.execute(f"SELECT documento, tipo, alvo, alvo_titulo, data FROM relacoes WHERE documento IN ({q})", lote),
                )
    return {"mudados": len(mudados), "removidos": len(removidos)}


def aplicar_delta(indice: Path, delta: Path) -> dict:
    """Aplica o delta ao índice, numa só transação (se falhar a meio, o índice fica como estava)."""
    from rag.indice import textos_fts

    con = sqlite3.connect(indice, isolation_level=None)
    d = sqlite3.connect(f"file:{delta}?mode=ro", uri=True)
    try:
        meta = dict(d.execute("SELECT chave, valor FROM meta"))
        metodo = dict(con.execute("SELECT chave, valor FROM meta")).get("metodo_termos")
        if meta.get("metodo_termos") != metodo:
            raise RuntimeError("O delta foi feito com outros termos: descarrega a versão completa.")
        con.execute("BEGIN")
        sair = [r[0] for r in d.execute("SELECT id FROM removidos")] + [r[0] for r in d.execute("SELECT id FROM documentos")]
        for documento in sair:
            doc = con.execute("SELECT titulo, sumario FROM documentos WHERE id = ?", (documento,)).fetchone()
            if doc is None:
                continue
            for id_, parte, epigrafe, texto in con.execute("SELECT id, parte, epigrafe, texto FROM pedacos WHERE documento = ?", (documento,)).fetchall():
                con.execute(
                    "INSERT INTO pedacos_fts (pedacos_fts, rowid, cabecalho, texto) VALUES ('delete', ?, ?, ?)",
                    (id_, *textos_fts(doc[0], doc[1] or "", parte or "", epigrafe or "", texto or "")),
                )
            con.execute("DELETE FROM pedacos WHERE documento = ?", (documento,))
            con.execute("DELETE FROM relacoes WHERE documento = ?", (documento,))
            con.execute("DELETE FROM documentos WHERE id = ?", (documento,))
        proximo = (con.execute("SELECT max(id) FROM pedacos").fetchone()[0] or 0) + 1
        colunas_doc = [c[1] for c in d.execute("PRAGMA table_info(documentos)")]
        marcas = ",".join("?" * len(colunas_doc))
        novos = 0
        for doc in d.execute("SELECT * FROM documentos").fetchall():
            linha_doc = dict(zip(colunas_doc, doc, strict=True))
            con.execute(f"INSERT INTO documentos ({', '.join(colunas_doc)}) VALUES ({marcas})", doc)
            for p in d.execute(f"SELECT {_COLUNAS_PEDACO} FROM pedacos WHERE documento = ? ORDER BY rowid", (doc[0],)).fetchall():
                con.execute("INSERT INTO pedacos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (proximo, *p))
                con.execute(
                    "INSERT INTO pedacos_fts (rowid, cabecalho, texto) VALUES (?, ?, ?)",
                    (proximo, *textos_fts(linha_doc["titulo"], linha_doc["sumario"] or "", p[1] or "", p[3] or "", p[6] or "")),
                )
                proximo += 1
                novos += 1
            con.executemany("INSERT INTO relacoes VALUES (?, ?, ?, ?, ?)", d.execute("SELECT * FROM relacoes WHERE documento = ?", (doc[0],)).fetchall())
        con.execute("INSERT OR REPLACE INTO meta VALUES ('construido', ?)", (meta["para"],))
        con.execute("INSERT OR REPLACE INTO meta VALUES ('versao', ?)", (meta["para"],))
        con.execute("COMMIT")
        return {"saidos": len(sair), "pedacos_novos": novos}
    except Exception:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise
    finally:
        d.close()
        con.close()


# ---------------------------------------------------------------------------------------- aplicação


def ler_manifesto(url: str | None = None) -> dict:
    import requests

    resposta = requests.get(url or url_manifesto(), timeout=30)
    if resposta.status_code == 404:
        raise RuntimeError("O índice ainda não foi publicado para descarregar.")
    resposta.raise_for_status()
    return resposta.json()


def ha_atualizacao(pasta: Path) -> dict | None:
    """O manifesto, se for mais recente do que o índice na pasta."""
    manifesto = ler_manifesto()
    return manifesto if manifesto.get("versao", "") > versao_local(pasta).get("versao", "") else None


def plano(manifesto: dict, local: str | None) -> tuple[bool, list[dict]]:
    """(descarregar a completa?, deltas a aplicar) para passar de `local` à versão do manifesto."""
    if local == manifesto["versao"]:
        return False, []
    cadeia = [manifesto["completo"]["versao"]] + [d["para"] for d in manifesto["deltas"]]
    if local in cadeia:
        return False, manifesto["deltas"][cadeia.index(local) :]
    return True, manifesto["deltas"]


def _descarregar_ficheiro(ficheiro: dict, destino: Path, progresso: Progresso) -> None:
    """Para `destino` (comprimido), retomando onde parou, e confirma o sha256."""
    import requests

    ja = destino.stat().st_size if destino.exists() else 0
    if ja > ficheiro["bytes"]:
        destino.unlink()
        ja = 0
    progresso.fase = "a descarregar"
    progresso.feito += ja
    if ja < ficheiro["bytes"]:
        cabecalhos = {"Range": f"bytes={ja}-"} if ja else {}
        with requests.get(ficheiro["url"], headers=cabecalhos, stream=True, timeout=60) as r:
            r.raise_for_status()
            if ja and r.status_code != 206:  # o servidor não retoma: começa do zero
                progresso.feito -= ja
                ja = 0
            with destino.open("ab" if ja else "wb") as f:
                for bloco in r.iter_content(BLOCO):
                    f.write(bloco)
                    progresso.feito += len(bloco)
    progresso.fase = "a verificar"
    if _sha256(destino) != ficheiro["sha256"]:
        destino.unlink()
        raise RuntimeError(f"{ficheiro['nome']} chegou corrompido; tenta outra vez.")


def descarregar(pasta: Path, progresso: Progresso | None = None, manifesto: dict | None = None, antes_de_trocar=None) -> dict:
    """Põe em `pasta` (onde o `rag` lê o índice: RAG_INDICE) a versão do manifesto.

    `antes_de_trocar()` é chamada antes de mexer no índice: no Windows um ficheiro aberto não se
    pode substituir, e uma pesquisa aberta não deve ver o índice a meio de um delta."""
    progresso = progresso or Progresso()
    manifesto = manifesto or ler_manifesto()
    pasta.mkdir(parents=True, exist_ok=True)
    completa, deltas = plano(manifesto, versao_local(pasta).get("versao"))
    if completa:
        c = manifesto["completo"]
        precisa = c["bytes"] + c["bytes_descomprimido"] + sum(d["bytes"] * 4 for d in deltas)
        livre = shutil.disk_usage(pasta).free
        if livre < precisa:
            raise RuntimeError(f"Falta espaço em disco: são precisos {precisa / 1e9:.1f} GB livres e há {livre / 1e9:.1f} GB.")
    progresso.total = sum(f["bytes"] for f in ([manifesto["completo"]] if completa else []) + deltas)
    progresso.feito = 0
    if completa:
        c = manifesto["completo"]
        comprimido = pasta / (c["nome"] + ".parte")
        _descarregar_ficheiro(c, comprimido, progresso)
        progresso.fase = "a descomprimir"
        novo = pasta / "indice.sqlite.novo"
        _gunzip(comprimido, novo)
        if antes_de_trocar:
            antes_de_trocar()
        os.replace(novo, pasta / "indice.sqlite")
        comprimido.unlink()
        _gravar_versao_local(pasta, c["versao"])
    for delta in deltas:
        comprimido = pasta / (delta["nome"] + ".parte")
        _descarregar_ficheiro(delta, comprimido, progresso)
        with tempfile.TemporaryDirectory(dir=pasta) as tmp:
            aberto = Path(tmp) / "delta.sqlite"
            _gunzip(comprimido, aberto)
            progresso.fase = "a aplicar"
            if antes_de_trocar:
                antes_de_trocar()
            aplicar_delta(pasta / "indice.sqlite", aberto)
        comprimido.unlink()
        _gravar_versao_local(pasta, delta["para"])
    progresso.fase = "pronto"
    return manifesto


# ---------------------------------------------------------------------------------------- publicação


def _copia_publica(indice: Path, destino: Path, versao: str) -> None:
    """Cópia do índice sem o caminho local do export (tinha o nome do utilizador da máquina)."""
    shutil.copyfile(indice, destino)
    with sqlite3.connect(destino) as con:
        con.execute("DELETE FROM meta WHERE chave = 'export'")
        con.execute("INSERT OR REPLACE INTO meta VALUES ('versao', ?)", (versao,))
        con.execute("INSERT OR REPLACE INTO meta VALUES ('construido', ?)", (versao,))


def _entrada(caminho: Path, url_base: str, **extra) -> dict:
    return {"nome": caminho.name, "url": url_base + caminho.name, "bytes": caminho.stat().st_size, "sha256": _sha256(caminho), **extra}


def _manifesto_publicado(pasta: Path, remoto: bool) -> dict | None:
    """O manifesto da última publicação: o do alojamento (manda) ou, sem rede, o guardado em `pasta`."""
    if remoto:
        try:
            return ler_manifesto()
        except RuntimeError:  # 404: ainda nada publicado
            return None
        except Exception as e:
            print(f"Sem acesso ao manifesto publicado ({e}); uso o guardado em {pasta}.")
    local = pasta / "versao.json"
    return json.loads(local.read_text(encoding="utf-8")) if local.exists() else None


def _base(pasta: Path, anterior: dict) -> Path:
    """O índice tal como foi publicado (a base do próximo delta).

    Usa `pasta/publicado.sqlite` se for dessa versão; senão reconstrói-o a partir do alojamento
    (completa + deltas), como faz a aplicação. Assim publica-se de qualquer pasta ou computador."""
    publicado = pasta / "publicado.sqlite"
    if publicado.exists():
        with sqlite3.connect(f"file:{publicado}?mode=ro", uri=True) as con:
            if dict(con.execute("SELECT chave, valor FROM meta")).get("versao") == anterior["versao"]:
                return publicado
    print(f"A reconstruir a base (versão {anterior['versao']}) a partir do alojamento…")
    reconstrucao = pasta / "reconstrucao"
    shutil.rmtree(reconstrucao, ignore_errors=True)
    descarregar(reconstrucao, manifesto=anterior)
    os.replace(reconstrucao / "indice.sqlite", publicado)
    shutil.rmtree(reconstrucao, ignore_errors=True)
    return publicado


def publicar(
    indice: Path, pasta: Path, versao: str, *, url_base: str = URL_BASE, completo: bool = False, limite: float = LIMITE_DELTA, remoto: bool = True
) -> tuple[dict, list[Path]]:
    """Prepara em `pasta` a versão `versao`: um delta desde a última publicada ou uma completa nova.

    Devolve o manifesto novo e os ficheiros a enviar (o `versao.json` em último). A última publicação
    vem do alojamento (`remoto`); a base do delta é `pasta/publicado.sqlite` ou reconstrói-se (`_base`)."""
    pasta.mkdir(parents=True, exist_ok=True)
    anterior = _manifesto_publicado(pasta, remoto)
    publicado = pasta / "publicado.sqlite"
    if anterior and versao <= anterior["versao"]:
        raise RuntimeError(f"A versão {versao} não é posterior à publicada ({anterior['versao']}).")
    novo = pasta / "novo.sqlite"
    _copia_publica(indice, novo, versao)
    enviar: list[Path] = []
    manifesto = None
    if anterior and not completo:
        publicado = _base(pasta, anterior)
        caminho_delta = pasta / f"delta-{anterior['versao']}-{versao}.sqlite"
        contagem = gerar_delta(publicado, novo, caminho_delta, anterior["versao"], versao)
        comprimido = caminho_delta.with_name(caminho_delta.name + ".gz")
        _gzip(caminho_delta, comprimido)
        caminho_delta.unlink()
        if comprimido.stat().st_size <= limite * anterior["completo"]["bytes"]:
            delta = _entrada(comprimido, url_base, de=anterior["versao"], para=versao, **contagem)
            manifesto = {**anterior, "versao": versao, "deltas": [*anterior["deltas"], delta]}
            enviar.append(comprimido)
        else:
            print(f"O delta tem {comprimido.stat().st_size / 1e6:.0f} MB, mais de {limite:.0%} da versão completa: publica-se uma completa nova.")
            comprimido.unlink()
    if manifesto is None:
        comprimido = pasta / f"completo-{versao}.sqlite.gz"
        _gzip(novo, comprimido)
        with sqlite3.connect(f"file:{novo}?mode=ro", uri=True) as con:
            metodo = dict(con.execute("SELECT chave, valor FROM meta")).get("metodo_termos")
        manifesto = {
            "versao": versao,
            "metodo_termos": metodo,
            "completo": _entrada(comprimido, url_base, versao=versao, bytes_descomprimido=novo.stat().st_size),
            "deltas": [],
            "anterior": anterior["completo"] if anterior else None,
        }
        enviar.append(comprimido)
    os.replace(novo, publicado)
    (pasta / "versao.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    enviar.append(pasta / "versao.json")
    return manifesto, enviar


def nomes_a_manter(manifesto: dict) -> set[str]:
    """O que fica no alojamento: o manifesto, a descrição, a completa atual, os deltas desde ela e a completa anterior."""
    nomes = {"versao.json", "README.md", ".gitattributes", manifesto["completo"]["nome"]} | {d["nome"] for d in manifesto["deltas"]}
    if manifesto.get("anterior"):
        nomes.add(manifesto["anterior"]["nome"])
    return nomes


def enviar_hf(manifesto: dict, ficheiros: list[Path], *, repositorio: str = REPOSITORIO, cartao: Path | None = CARTAO, api=None) -> list[str]:
    """Envia os ficheiros, depois o manifesto, apaga os que já não fazem falta e limpa o histórico."""
    if api is None:
        from huggingface_hub import HfApi

        api = HfApi()
    from huggingface_hub import CommitOperationAdd, CommitOperationDelete

    existentes = set(api.list_repo_files(repositorio, repo_type="dataset"))
    manter = nomes_a_manter(manifesto)
    apagar = sorted(n for n in existentes if n not in manter)
    operacoes = [CommitOperationAdd(path_in_repo=f.name, path_or_fileobj=str(f)) for f in ficheiros if f.name != "versao.json"]
    if cartao:
        operacoes.append(CommitOperationAdd(path_in_repo="README.md", path_or_fileobj=str(cartao)))
    api.create_commit(repositorio, repo_type="dataset", operations=operacoes, commit_message=f"Ficheiros da versão {manifesto['versao']}")
    # O manifesto só muda quando os ficheiros para que aponta já lá estão; só depois se apagam os antigos.
    manifesto_local = next(f for f in ficheiros if f.name == "versao.json")
    api.upload_file(path_or_fileobj=str(manifesto_local), path_in_repo="versao.json", repo_id=repositorio, repo_type="dataset", commit_message=f"Versão {manifesto['versao']}")
    if apagar:
        api.create_commit(repositorio, repo_type="dataset", operations=[CommitOperationDelete(path_in_repo=n) for n in apagar], commit_message="Apaga as versões antigas")
    api.super_squash_history(repositorio, repo_type="dataset", commit_message=f"Versão {manifesto['versao']}")
    return apagar


# ---------------------------------------------------------------------------------------- linha de comandos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("publicar", help="Preparar (e, com --enviar, publicar) uma versão.")
    p.add_argument("--indice", type=Path)
    p.add_argument("--pasta", type=Path, default=PUBLICACAO)
    p.add_argument("--versao", default=date.today().isoformat())
    p.add_argument("--completo", action="store_true", help="Publicar uma versão completa mesmo que o delta seja pequeno.")
    p.add_argument("--enviar", action="store_true", help="Enviar para o Hugging Face.")
    d = sub.add_parser("descarregar", help="Descarregar a versão publicada (como faz a aplicação).")
    d.add_argument("--pasta", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.comando == "publicar":
        from rag.fontes import PASTA_INDICE

        manifesto, enviar = publicar(args.indice or PASTA_INDICE / "indice.sqlite", args.pasta, args.versao, completo=args.completo)
        for f in enviar:
            print(f"{f}: {f.stat().st_size / 1e6:.1f} MB")
        if args.enviar:
            apagados = enviar_hf(manifesto, enviar)
            print(f"Enviado para {REPOSITORIO}; apagados: {', '.join(apagados) or 'nenhum'}")
    else:
        descarregar(args.pasta)
        print(f"Pronto em {args.pasta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
