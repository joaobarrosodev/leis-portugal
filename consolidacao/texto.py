"""Leitura dos registos do acervo para a consolidação: corpo, artigos e números.

O corpo de um registo divide-se em segmentos que, juntos, dão o texto original letra a letra:
os artigos (`###### Artigo N.º — Epígrafe` e as linhas até ao título seguinte) e o resto
(preâmbulo, títulos de capítulos e de anexos). Só os artigos alterados são reescritos, por
isso os outros ficam iguais por construção.

Cada artigo fica identificado pela parte onde está, como em `avaliacao/comum.py`: "" para o
diploma e o título do anexo (`## Anexo …`) para o resto. Aqui o título do anexo reconhece-se
também em maiúsculas (`## ANEXO`), que o `comum.py` não reconhece.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]

_ARTIGO = re.compile(r"^#{6} Artigo (\S+)(?: — (.*))?$")
_ANEXO = re.compile(r"^## (Anexo\b.*)$", re.I)
_TITULO = re.compile(r"^#{1,5} ")
_NOTA = re.compile(r"^> (Alterado|Aditado|Revogado|Retificado|Republicado)", re.I)
_LIGACAO_MD = re.compile(r"\[([^\]]*)\]\((?:[^()]|\([^()]*\))*\)")
_LIGACAO_HTML = re.compile(r"<a [^>]*>(.*?)</a>")


def corpo(markdown: str) -> str:
    """O texto do registo sem o cabeçalho YAML."""
    if markdown.startswith("---\n"):
        fim = markdown.find("\n---\n", 4)
        if fim != -1:
            return markdown[fim + 5 :]
    return markdown


def front_matter(markdown: str) -> dict:
    if not markdown.startswith("---\n"):
        return {}
    fim = markdown.find("\n---\n", 4)
    return yaml.safe_load(markdown[4:fim]) or {} if fim != -1 else {}


def sem_ligacoes(texto: str) -> str:
    """O texto sem as ligações Markdown e HTML (fica o texto da ligação)."""
    return _LIGACAO_HTML.sub(r"\1", _LIGACAO_MD.sub(r"\1", texto))


def normalizar(texto: str) -> str:
    """Espaços colapsados e aspas tipográficas uniformes, para comparar letra a letra."""
    texto = texto.replace(" ", " ").replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", texto).strip()


def sem_abreviaturas(texto: str) -> str:
    """"n.º", "n.os" e "art." sem o ponto, para as expressões que param no fim da frase."""
    return re.sub(r"\b(n|art|arts)\.\s*", r"\1 ", texto, flags=re.I)


def numero_artigo(numero: str) -> str:
    """`3.º`, `3º`, `3.°` e `3` ficam iguais: `3.º`; `4.º-A` e `4-A` ficam `4.º-A`."""
    m = re.match(r"^(\d+)\s*\.?\s*[º°o]?\s*(?:[-–]\s*([A-Z]{1,2}))?\.?$", numero.strip())
    if not m:
        return numero.strip()
    return f"{m.group(1)}.º" + (f"-{m.group(2)}" if m.group(2) else "")


# --- Segmentos do corpo ---------------------------------------------------------------------


@dataclass
class Artigo:
    parte: str
    numero: str
    epigrafe: str
    linhas: list[str]  # o bloco tal como está no registo, a começar pelo título

    @property
    def chave(self) -> str:
        return f"{self.parte}::{self.numero}" if self.parte else self.numero

    @property
    def texto(self) -> str:
        """O corpo do artigo sem o título e sem as notas do DRE."""
        return "\n".join(l for l in self.linhas[1:] if not _NOTA.match(l)).strip()

    @property
    def notas(self) -> list[str]:
        return [l for l in self.linhas[1:] if _NOTA.match(l)]


@dataclass
class Corpo:
    segmentos: list[Artigo | list[str]] = field(default_factory=list)

    @property
    def artigos(self) -> list[Artigo]:
        return [s for s in self.segmentos if isinstance(s, Artigo)]

    def artigo(self, parte: str, numero: str) -> Artigo | None:
        return next((a for a in self.artigos if a.parte == parte and a.numero == numero), None)

    def partes(self) -> list[str]:
        return list(dict.fromkeys(a.parte for a in self.artigos))

    def texto(self) -> str:
        linhas: list[str] = []
        for s in self.segmentos:
            linhas.extend(s.linhas if isinstance(s, Artigo) else s)
        return "\n".join(linhas)


def dividir(texto: str) -> Corpo:
    """O corpo em segmentos; `dividir(t).texto() == t`."""
    resultado = Corpo()
    parte = ""
    atual: list[str] = []
    artigo: Artigo | None = None

    def fechar() -> None:
        nonlocal atual, artigo
        if artigo is not None:
            artigo.linhas = atual
            resultado.segmentos.append(artigo)
        elif atual:
            resultado.segmentos.append(atual)
        atual, artigo = [], None

    for linha in texto.split("\n"):
        cabecalho = _ARTIGO.match(linha)
        if cabecalho:
            fechar()
            artigo = Artigo(parte, numero_artigo(cabecalho.group(1)), (cabecalho.group(2) or "").strip(), [])
        elif _TITULO.match(linha):
            if artigo is not None:
                fechar()
            anexo = _ANEXO.match(linha)
            if anexo:
                parte = anexo.group(1).strip()
        atual.append(linha)
    fechar()
    return resultado


def com_titulos(texto: str) -> str | None:
    """Um corpo sem `###### Artigo` com os títulos que o parser da fase 3 encontra.

    `parse_articles` (`src/leis_portugal/domain/articles.py`) reconhece os artigos em texto
    corrido ("Artigo 1.º", "Art. 1.º - …", a epígrafe na linha seguinte) e os títulos noutros
    formatos ("###### ARTIGO 1.º"). Aqui só se reescrevem essas linhas: a linha do artigo passa
    a `###### Artigo N.º — Epígrafe` (o texto que vinha na mesma linha fica no parágrafo
    seguinte), a linha da epígrafe sai, e um anexo em texto corrido ("ANEXO I") passa a
    `## ANEXO I`. As outras linhas ficam como estão.

    Devolve None quando não há artigos, quando uma linha não se encontra ou quando a divisão
    resultante não dá os mesmos artigos (números repetidos sem anexo que os separe, por exemplo).
    """
    from leis_portugal.domain import articles as fase3

    artigos = [a for a in fase3.parse_articles(texto) if a.kind == "artigo" and not a.quoted]
    if not artigos:
        return None
    linhas = texto.split("\n")
    trocas: dict[int, list[str]] = {}
    i, parte = 0, ""
    for a in artigos:
        if a.part != parte:
            parte = a.part
            j = next((k for k in range(i, len(linhas)) if linhas[k].strip() == a.part), None)
            if j is not None and not linhas[j].startswith("#"):
                trocas[j] = [f"## {linhas[j].strip()}"]
            elif j is None and not any(re.match(rf"^##\s+{re.escape(a.part)}\s*$", l) for l in linhas[i:]):
                return None  # parte implícita (a numeração recomeça sem título)
        while i < len(linhas):
            s = linhas[i].strip()
            m = fase3._HEADING_ARTICLE.match(s) or (fase3._PLAIN_ARTICLE.match(s) if not s.startswith("#") else None)
            if m and fase3._clean_number(m.group("number")) == a.number and (not a.source_line or s == a.source_line):
                break
            i += 1
        else:
            return None
        if s.startswith("#"):
            epigrafe, primeira = (m.group("heading") or m.group("heading2") or "").strip(), ""
        else:
            epigrafe, primeira = fase3._plain_rest(m.group("rest"))
        novo = [f"###### Artigo {a.number}" + (f" — {a.heading}" if a.heading else "")]
        if a.heading and not epigrafe:
            # A epígrafe estava na linha seguinte: sai, com a linha vazia que a seguia.
            k = next((k for k in range(i + 1, len(linhas)) if linhas[k].strip()), None)
            if k is None or fase3._split_heading(linhas[k].strip()) != a.heading:
                return None
            trocas.update({x: [] for x in range(i + 1, k + 1)})
        elif epigrafe != a.heading:
            return None
        trocas[i] = novo + (["", primeira] if primeira else [])
        i += 1
    resultado = "\n".join(l for k, linha in enumerate(linhas) for l in trocas.get(k, [linha]))
    esperado = [(a.part, numero_artigo(a.number)) for a in artigos]
    obtido = [(a.parte, a.numero) for a in dividir(resultado).artigos]
    if obtido != esperado or len(set(obtido)) != len(obtido):
        return None
    return resultado


# --- Referências a um diploma ---------------------------------------------------------------


def padrao_diploma(titulo: str) -> re.Pattern[str] | None:
    """Expressão que reconhece o diploma no texto de outro: `Decreto-Lei n.º 380/97` também
    como `Decreto-Lei n.o 380/97`, `Decreto-Lei 380/97` ou `Decreto-Lei n.º 380/1997`."""
    titulo = re.sub(r"\s*\(.*\)$", "", titulo).strip()
    m = re.match(r"^(.*?)\s+n\.?\s*[º°o]\s*(\S+)$", titulo)
    if not m:
        return None
    rotulo, numero = m.groups()
    rotulo_re = r"[\s-]+".join(re.escape(p) for p in re.split(r"[\s-]+", rotulo))
    partes = numero.split("/")
    if len(partes) >= 2 and re.fullmatch(r"\d{2}", partes[1]):
        partes[1] = f"(?:19|20)?{partes[1]}"
    elif len(partes) >= 2 and re.fullmatch(r"(19|20)\d{2}", partes[1]):
        partes[1] = f"(?:{partes[1][:2]})?{partes[1][2:]}"
    else:
        partes = [re.escape(p) for p in partes]
    numero_re = "/".join(p if p.startswith("(?:") else re.escape(p) for p in partes)
    return re.compile(
        rf"(?<![\w-]){rotulo_re}\s+(?:n\.?\s*[º°o]\.?\s*)?{numero_re}(?![\w/]|-[A-Z]\b)", re.I
    )


_QUALQUER_DIPLOMA = re.compile(
    r"(?<![\w-])(?:Decreto[\s-]Lei|Decreto Legislativo Regional|Decreto Regulamentar(?: Regional)?|Decreto|"
    r"Lei Orgânica|Lei Constitucional|Lei|Portaria|Despacho Normativo|Despacho|Resolução do Conselho de Ministros|"
    r"Resolução da Assembleia da República|Resolução|Regulamento|Aviso|Decreto do Governo)"
    r"\s+(?:n\.?\s*[º°o]\.?\s*)?\d+(?:-[A-Z]+)?(?:/\d{2,4})?(?:/[A-Z])?(?:/M)?",
    re.I,
)


def diplomas_em(texto: str) -> list[re.Match[str]]:
    """Todas as referências a diplomas num texto (sem ligações)."""
    return list(_QUALQUER_DIPLOMA.finditer(texto))


def artigos_alteradores(texto: str, titulo: str) -> list[Artigo]:
    """Os artigos do diploma que altera que mencionam o original."""
    padrao = padrao_diploma(titulo)
    if padrao is None:
        return []
    return [a for a in dividir(texto).artigos if padrao.search(sem_ligacoes("\n".join(a.linhas)))]
