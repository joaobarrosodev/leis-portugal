"""Ler artigos do acervo e verificar o ficheiro dos casos, com o mesmo leitor do índice.

    python avaliacao/casos/artigo.py diploma "Lei n.º 7/2009"          # caminho e id do registo com esse título
    python avaliacao/casos/artigo.py listar <caminho> [regex]           # chave | epígrafe (filtra pela epígrafe ou chave)
    python avaliacao/casos/artigo.py ler <caminho> <chave>              # texto do artigo, notas e se está revogado
    python avaliacao/casos/artigo.py procurar <caminho> <regex>         # artigos cujo texto tem a expressão
    python avaliacao/casos/artigo.py verificar <casos.jsonl>            # verificação mecânica de todos os casos

A chave é a que o índice usa: «3.º», ou «ANEXO — Código …::3.º» nos códigos aprovados em anexo.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from rag.fontes import corpo, ler_artigos, normalizar  # noqa: E402

_REVOGADO = re.compile(r"^\W*revogad[oa]", re.I)


def _artigos(caminho: str):
    return ler_artigos(corpo((RAIZ / caminho).read_text(encoding="utf-8")))


def _cabecalho(caminho: str) -> dict:
    texto = (RAIZ / caminho).read_text(encoding="utf-8")
    cab = {}
    for linha in texto.split("\n---\n", 1)[0].splitlines():
        m = re.match(r"^(id|title|legal_status|summary): (.*)$", linha)
        if m:
            cab[m.group(1)] = m.group(2).strip().strip("'\"")
    return cab


def revogado(artigo) -> bool:
    """O texto do artigo é só a marca «(Revogado.)» ou começa por ela."""
    return bool(_REVOGADO.match(artigo.texto.strip()))


def diploma(titulo: str) -> None:
    """Procura pelo nome do ficheiro (número e ano do título) e confirma o título no cabeçalho."""
    m = re.search(r"n\.º\s*([\w-]+)(?:/(\d{2,4}))?", titulo)
    if not m:
        sys.exit("Título sem «n.º»: escreva-o como no DRE, por exemplo «Decreto-Lei n.º 47344» ou «Lei n.º 7/2009».")
    numero, ano = m.group(1).lower(), m.group(2)
    padrao = f"*-{numero}-{ano}.md" if ano else f"*-{numero}.md"
    saida = subprocess.run(["find", str(RAIZ / "data"), "-path", padrao], capture_output=True, text=True).stdout
    for ficheiro in sorted(saida.split("\n")):
        if not ficheiro:
            continue
        caminho = str(Path(ficheiro).relative_to(RAIZ))
        cab = _cabecalho(caminho)
        if cab.get("title") == titulo:
            print(f"{caminho}\t{cab.get('id')}\t{cab.get('legal_status')}\t{cab.get('summary', '')[:120]}")


def listar(caminho: str, filtro: str | None) -> None:
    rx = re.compile(filtro, re.I) if filtro else None
    for a in _artigos(caminho):
        if rx is None or rx.search(a.epigrafe) or rx.search(a.chave):
            print(f"{a.chave}\t{a.epigrafe}{'  [REVOGADO]' if revogado(a) else ''}")


def ler(caminho: str, chave: str) -> None:
    cab = _cabecalho(caminho)
    achados = [a for a in _artigos(caminho) if a.chave == chave]
    if not achados:
        sys.exit(f"Sem artigo com a chave {chave!r} em {caminho}")
    for a in achados:
        print(f"documento: {cab.get('id')}\ntitulo: {cab.get('title')}\nchave: {a.chave}\nepigrafe: {a.epigrafe}\nrevogado: {revogado(a)}\n")
        print(a.texto)
        if a.notas:
            print("\nnotas:\n" + "\n".join(a.notas))


def procurar(caminho: str, expressao: str) -> None:
    rx = re.compile(expressao, re.I)
    for a in _artigos(caminho):
        m = rx.search(a.texto)
        if m:
            ini = max(0, m.start() - 80)
            print(f"{a.chave}\t{a.epigrafe}\t…{a.texto[ini:m.end() + 80].replace(chr(10), ' ')}…")


def verificar(ficheiro: str) -> int:
    """Cada artigo citado existe com essa chave e essa epígrafe, no documento dito, não está revogado
    (salvo se o caso o marca como revogado) e o excerto está lá, letra a letra (sem contar espaços e maiúsculas)."""
    erros = 0
    cache: dict[str, list] = {}
    for n, linha in enumerate(Path(ficheiro).read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip():
            continue
        caso = json.loads(linha)
        refs = [("essencial", r) for r in caso["resposta"]["artigos_essenciais"]]
        refs += [("util", r) for r in caso["resposta"].get("artigos_uteis", [])]
        refs += [("lei_pensada", r) for r in caso.get("leis_pensadas", []) if r.get("artigo")]
        for papel, r in refs:
            onde = f"{caso['id']} {papel} {r.get('titulo')} {r.get('artigo')}"
            caminho = r.get("caminho")
            if not caminho or not (RAIZ / caminho).exists():
                print(f"ERRO {onde}: caminho inexistente {caminho}")
                erros += 1
                continue
            if caminho not in cache:
                cache[caminho] = _artigos(caminho)
            cab = _cabecalho(caminho)
            if r.get("documento") != cab.get("id"):
                print(f"ERRO {onde}: documento {r.get('documento')} ≠ {cab.get('id')}")
                erros += 1
            achados = [a for a in cache[caminho] if a.chave == r.get("artigo")]
            if len(achados) != 1:
                print(f"ERRO {onde}: {len(achados)} artigos com essa chave")
                erros += 1
                continue
            a = achados[0]
            if r.get("epigrafe") is not None and r["epigrafe"] != a.epigrafe:
                print(f"ERRO {onde}: epígrafe {r['epigrafe']!r} ≠ {a.epigrafe!r}")
                erros += 1
            if revogado(a) and not r.get("revogado"):
                print(f"ERRO {onde}: o artigo está revogado no acervo")
                erros += 1
            for excerto in ([r["excerto"]] if isinstance(r.get("excerto"), str) else r.get("excerto") or []):
                if normalizar(excerto) not in normalizar(a.texto):
                    print(f"ERRO {onde}: excerto não está no texto: {excerto[:90]!r}")
                    erros += 1
            if papel == "essencial" and not r.get("excerto"):
                print(f"ERRO {onde}: artigo essencial sem excerto")
                erros += 1
    print(f"{erros} erros")
    return erros


if __name__ == "__main__":
    comando, *resto = sys.argv[1:] or ["-h"]
    if comando == "diploma":
        diploma(resto[0])
    elif comando == "listar":
        listar(resto[0], resto[1] if len(resto) > 1 else None)
    elif comando == "ler":
        ler(resto[0], resto[1])
    elif comando == "procurar":
        procurar(resto[0], resto[1])
    elif comando == "verificar":
        sys.exit(1 if verificar(resto[0]) else 0)
    else:
        print(__doc__)
