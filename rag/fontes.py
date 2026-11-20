"""Onde estão os dados e como se leem os artigos de um registo.

A leitura dos artigos fica toda em `ler_artigos`: hoje usa `avaliacao/comum.py`; quando o
parser da fase 3 estiver pronto, troca-se só esta função.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


RAIZ = Path(__file__).resolve().parents[1]
PASTA_INDICE = Path(os.environ.get("RAG_INDICE", RAIZ / "rag" / "indice"))

_spec = importlib.util.spec_from_file_location("avaliacao_comum", RAIZ / "avaliacao" / "comum.py")
comum = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = comum
_spec.loader.exec_module(comum)  # type: ignore[union-attr]

Artigo = comum.Artigo
corpo = comum.corpo
normalizar = comum.normalizar


def ler_artigos(texto: str) -> list[Artigo]:
    """Os artigos do corpo de um registo (sem o cabeçalho YAML), pela ordem do texto."""
    return comum.artigos(texto)


def fora_dos_artigos(texto: str) -> list[tuple[str, str]]:
    """(parte, texto) do que `ler_artigos` não devolve: o texto antes do primeiro artigo de cada parte (`comum.fora_dos_artigos`)."""
    return comum.fora_dos_artigos(texto)


def chave_atual(artigos: list[Artigo], chave: str, epigrafe: str | None = None) -> str:
    """A chave que o leitor de hoje dá ao artigo que uma chave escrita antes de 20/11/2026 identificava.

    Até essa data `## ANEXO` em maiúsculas não abria parte: o artigo 13.º de um regulamento anexo tinha a chave
    «13.º», como se fosse do diploma, e agora tem «ANEXO — Regulamento…::13.º». As perguntas de avaliação guardam
    a chave antiga e a epígrafe: se o artigo com essa chave já não existe, ou existe com outra epígrafe (é o do
    diploma e não o do anexo), procura-se o do mesmo número e da mesma epígrafe. Sem um candidato único, fica a chave dada."""
    com_a_chave = [a for a in artigos if a.chave == chave]
    if any(epigrafe is None or a.epigrafe == epigrafe for a in com_a_chave):
        return chave
    numero = chave.rsplit("::", 1)[-1]
    do_numero = [a for a in artigos if a.numero == numero and a.chave != chave]
    for candidatos in ([a for a in do_numero if epigrafe is not None and a.epigrafe == epigrafe], [] if com_a_chave else do_numero):
        chaves = {a.chave for a in candidatos}
        if len(chaves) == 1:
            return chaves.pop()
    return chave


def acertar_fontes(perguntas: list[dict], raiz: Path = RAIZ) -> list[dict]:
    """Põe nas fontes das perguntas de avaliação a chave que o leitor de hoje dá a cada artigo (`chave_atual`).

    Só em memória: os ficheiros das perguntas ficam como estão. A chave antiga fica em `artigo_antes`.
    Um índice construído antes de 20/11/2026 tem as chaves antigas: para o medir, usar o código dessa altura."""
    lidos: dict[str, list[Artigo]] = {}
    for pergunta in perguntas:
        fonte = pergunta.get("fonte") or {}
        alvos = [(fonte.get("caminho"), a) for a in fonte.get("artigos", [])] + [(x.get("caminho"), x) for x in (fonte, pergunta.get("distrator") or {})]
        for caminho, alvo in alvos:
            if not caminho or not alvo.get("artigo"):
                continue
            if caminho not in lidos:
                ficheiro = raiz / caminho
                lidos[caminho] = ler_artigos(corpo(ficheiro.read_text(encoding="utf-8"))) if ficheiro.exists() else []
            nova = chave_atual(lidos[caminho], alvo["artigo"], alvo.get("epigrafe")) if lidos[caminho] else alvo["artigo"]
            if nova != alvo["artigo"]:
                alvo["artigo_antes"], alvo["artigo"] = alvo["artigo"], nova
    return perguntas


_REVOGADO = re.compile(r"^\(?\s*revogad[oa]", re.I)


_PUBLICADO_EM = re.compile(r"Série [^,\]]*?de (\d{4}-\d{2}-\d{2})")
_EM_VIGOR_DESDE = re.compile(r"em vigor a partir de (\d{4}-\d{2}-\d{2})")


_EFEITOS_DESDE = re.compile(r"(?:em vigor|com efeitos|produz efeitos) a partir de (\d{4}-\d{2}-\d{2})")


def efeitos_da_revogacao(nota: str) -> str | None:
    """A data em que uma nota "Revogado pelo/a …" passa a valer, pelo que a própria nota do DRE diz.

    «… em vigor a partir de 2026-08-14, com efeitos a partir de 2026-12-31»: o diploma que revoga entra em vigor
    em agosto, mas o artigo vigora até 30 de dezembro. É a mais tardia das datas da nota («em vigor», «com
    efeitos», «produz efeitos a partir de»); sem nenhuma, não se sabe e devolve None."""
    datas = [d for d in _EFEITOS_DESDE.findall(nota) if d >= "1800"]
    return max(datas) if datas else None


def revogacao_por_produzir_efeitos(notas: str, data: str) -> tuple[str, str] | None:
    """(data de efeitos, nota) se todas as revogações do artigo só passam a valer depois de `data`; senão None."""
    futuras = []
    for nota in (n.strip() for n in notas.splitlines()):
        if _REVOGADO.match(nota):
            efeitos = efeitos_da_revogacao(nota)
            if efeitos is None or efeitos <= data:
                return None
            futuras.append((efeitos, nota))
    return min(futuras) if futuras else None


def revogado(texto: str, notas: str, data: str | None = None) -> bool:
    """O artigo está revogado: o texto é "(Revogado.)" ou uma nota diz "Revogado pelo/a …".

    Nos consolidados do DRE, um artigo revogado fica muitas vezes com o texto antigo e só ganha a
    nota (p. ex. os do Código do Trabalho de 2003, revogados pela Lei n.º 7/2009). Conta a nota de
    revogação mais recente: se uma nota com data posterior o altera (o artigo foi reposto, como os
    do arrendamento do Código Civil, revogados em 1975 e repostos pela Lei n.º 6/2006), já não está.

    Com `data` (a da pergunta), uma revogação só conta a partir do dia em que produz efeitos
    (`efeitos_da_revogacao`): a Lei n.º 13/2003 foi revogada em agosto de 2026 com efeitos a 31 de dezembro.
    Sem `data`, conta qualquer nota de revogação, como antes."""
    if _REVOGADO.match(texto.strip()):
        return True
    linhas = [n.strip() for n in notas.splitlines() if n.strip()]
    if data is not None:
        linhas = [n for n in linhas if not (_REVOGADO.match(n) and (efeitos_da_revogacao(n) or "") > data)]
    revogacoes = [n for n in linhas if _REVOGADO.match(n)]
    if not revogacoes:
        return False
    def data(nota: str) -> str | None:
        # A data de publicação do diploma que altera ou revoga ("… Série I de 2013-12-31"); a de entrada em
        # vigor engana às vezes (uma revogação de 2013 "em vigor a partir de 2004-01-01"). Sem ela, a de
        # entrada em vigor. Uma data impossível (1079-01-01, gralha do DRE por 1979) conta como sem data.
        m = _PUBLICADO_EM.search(nota) or _EM_VIGOR_DESDE.search(nota)
        return m.group(1) if m and m.group(1) >= "1800" else None

    datas_revogacao = [data(n) for n in revogacoes]
    if None in datas_revogacao:
        return True  # sem data não se sabe a ordem: fica revogado, como antes
    ultima_revogacao = max(datas_revogacao)
    return not any((d := data(n)) and d > ultima_revogacao for n in linhas if not _REVOGADO.match(n))


def export_sqlite() -> Path:
    """O `exports/leis-portugal.sqlite`: na raiz, ou na pasta principal quando se corre numa worktree."""
    if os.environ.get("RAG_EXPORT"):
        return Path(os.environ["RAG_EXPORT"])
    for pasta in (RAIZ, *RAIZ.parents):
        candidato = pasta / "exports" / "leis-portugal.sqlite"
        if candidato.exists():
            return candidato
    raise FileNotFoundError("exports/leis-portugal.sqlite não encontrado; corre `leis-portugal export` ou define RAG_EXPORT")


def ler_historico(caminho_md: Path) -> dict[str, Any] | None:
    """O `.versoes.json` de um registo, com os fragmentos dos blocos quando está dividido."""
    caminho = caminho_md.with_suffix(".versoes.json")
    if not caminho.exists():
        return None
    historico = json.loads(caminho.read_text(encoding="utf-8"))
    if "fragment_blocks" in historico:
        fragmentos: dict[str, Any] = {}
        for nome in historico.pop("fragment_blocks"):
            fragmentos.update(json.loads((caminho.parent / nome).read_text(encoding="utf-8"))["fragments"])
        historico["fragments"] = fragmentos
    return historico


def texto_da_versao(historico: dict[str, Any], versao: dict[str, Any]) -> str:
    """O corpo de uma versão: a concatenação dos seus fragmentos (como `render_version`, sem título)."""
    fragmentos = historico["fragments"]
    return "\n\n".join(fragmentos[chave]["markdown"] for chave in versao["fragments"] if fragmentos[chave]["markdown"])
