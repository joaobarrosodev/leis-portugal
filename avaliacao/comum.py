"""Leitura dos artigos de um registo, partilhada pela amostragem e pela verificação.

Os artigos são os títulos `###### Artigo N.º — Epígrafe` do corpo do registo. A numeração
repete-se entre o diploma e os anexos (o Código do Trabalho, anexo da Lei n.º 7/2009, tem
o seu próprio artigo 3.º), por isso cada artigo fica identificado pela parte onde está:
"" para o diploma, o título do anexo (`## Anexo — …`) para o resto. Um `## ANEXO` em maiúsculas também
abre parte quando tem artigos (20/11/2026); com título, o título vem à frente: os artigos de
`## ANEXO — CÓDIGO DE PROCESSO PENAL` ficam na parte «CÓDIGO DE PROCESSO PENAL (ANEXO)» (ver `_nome_do_anexo`).
Sem artigos (tabelas, mapas, texto corrido), o texto de um `## ANEXO` fica onde sempre esteve: colado ao
artigo anterior.

Contam como artigo, com o número a dizer o que são (20/11/2026):

- `###### ARTIGO 1.º`, em maiúsculas (leis e decretos de 1970 a 1989): número «1.º», como os outros;
- `###### Base IV — Epígrafe` (leis de bases e bases de concessões): número «Base IV»;
- `###### 1.º` (os números das portarias e dos despachos): número «N.º 1.º».

O texto que fica fora dos artigos (antes do primeiro artigo do diploma ou de um `## Anexo`, e os `## Anexo`
sem artigos) sai em `fora_dos_artigos`: o índice do RAG guarda-o em blocos nos registos que só têm títulos
das formas novas, que antes entravam inteiros em blocos.

Um registo quase todo em texto corrido, com dois ou três títulos soltos em maiúsculas pelo meio (o Código
Penal de 1982 no Decreto-Lei n.º 400/82), não se parte por esses títulos: `artigos` devolve uma lista vazia e
o índice guarda-o inteiro em blocos, como antes.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
# Na raiz, ou na pasta principal quando se corre numa worktree (como `rag.fontes.export_sqlite`).
EXPORT = next(
    (p / "exports" / "leis-portugal.sqlite" for p in (RAIZ, *RAIZ.parents) if (p / "exports" / "leis-portugal.sqlite").exists()),
    RAIZ / "exports" / "leis-portugal.sqlite",
)

_ARTIGO = re.compile(r"^#{6} (Artigo|ARTIGO)(?: |(?=\d))(.+?)(?: — (.*))?$")
_BASE = re.compile(r"^#{6} (?:Base|BASE) +(.+?)(?: — (.*))?$")
_NUMERO_DE_BASE = re.compile(r"^(?:[IVXLCDM]+|\d+)(?:\.ª)?(?:-[A-Z])?$")
_PONTO = re.compile(r"^#{6} (\d+)\.?\s?º$")
# Os textos antigos em maiúsculas põem às vezes o próprio texto no título («###### ARTIGO 30.º — É facultado…»):
# acima deste tamanho, o que vem depois do travessão é texto e não epígrafe (como no `domain/articles.py`).
EPIGRAFE_MAXIMA = 200
# O mesmo leitor de números que o `domain/articles.py`, mas com o número na forma das perguntas («1.º»,
# «78.º-A»), porque a pesquisa procura o artigo pelo número exato.
# Um inteiro escreve-se de muitas maneiras: «1.º», «1º», «1°.», «1.», «1», «1o», «1o.» e «1g.» (atos antigos
# do EUR-Lex), «3. º», «34 .º». A letra de um aditado vem junta («12.ºA»), separada («78.º A», «292.º ‐A»,
# com o hífen U+2010 do EUR-Lex, «10.º - A», «230.º-AAA») ou com travessão («3.º–EA»). A pontuação no fim
# («3.º:», «3.º.», «18.º...») não conta.
_INTEIRO = re.compile(r"^(\d+)\s?(?:\.?\s?[º°]|\.?o|g\.?)?\.?(?:(?:\s?[-‐‑]\s?|–)([A-Z]{1,3})|\s?([A-Z]{1,2}))?$")
# Os compostos dos regulamentos («A-1/2.º», «C - 1/4.º», «A/1 - 5.º», «D-11/2.º-A», «III/1.º») e dos acordos
# da UE («2.1», «J.1») ficam como estão, sem os espaços.
_COMPOSTO = re.compile(r"^(?:[A-Z]{1,3}|\d+)(?:[-/.](?:[A-Z]{1,3}|\d+))+(?:\.?º)?(?:-[A-Z]{1,2})?$")


def numero_artigo(bruto: str) -> str | None:
    """O número de um título de artigo na forma das perguntas («1.º», «78.º-A»), ou None se não é um número."""
    bruto = bruto.strip()
    if re.search(r"\s(?:\.\.|…)", bruto):
        return None  # «Artigo 42.º ...»: o artigo que um ato de alteração não muda.
    bruto = bruto.rstrip("-:;.…").strip()
    inteiro = _INTEIRO.match(bruto)
    if inteiro:
        letra = inteiro.group(2) or inteiro.group(3)
        return f"{inteiro.group(1)}.º" + (f"-{letra}" if letra else "")
    composto = re.sub(r"\s+", "", re.sub(r"[‐‑–]", "-", bruto))
    if _COMPOSTO.match(composto):
        return composto
    if re.search(r"\s", bruto):
        return None
    # O resto («único», «IV», «12.ª»…) como vem, se for uma palavra só.
    return bruto.replace("‐", "-").replace("‑", "-").rstrip(".") or None


def _cabecalho(linha: str) -> tuple[str, str, str, str] | None:
    """(número, epígrafe, início do texto, forma) de um título de artigo, base ou número, ou None se não é uma unidade.

    Ao contrário do `articles.py`, não lê a epígrafe depois de um hífen («Artigo 87.º - Ensaios.»): nos decretos
    antigos que a têm, os outros artigos estão em texto corrido antes do título, e o índice perdia-os.
    """
    cabecalho = _ARTIGO.match(linha)
    if cabecalho:
        numero = numero_artigo(cabecalho.group(2))
        if not numero:
            return None
        epigrafe = (cabecalho.group(3) or "").strip()
        if cabecalho.group(1) == "ARTIGO":
            if numero in ("ÚNICO", "UNICO"):
                numero = "único"
            if len(epigrafe) > EPIGRAFE_MAXIMA:
                return numero, "", epigrafe, "ARTIGO"
        return numero, epigrafe, "", cabecalho.group(1)
    base = _BASE.match(linha)
    if base:
        numero = base.group(1).strip().rstrip(".")
        return (f"Base {numero}", (base.group(2) or "").strip(), "", "Base") if _NUMERO_DE_BASE.match(numero) else None
    ponto = _PONTO.match(linha)
    return (f"N.º {ponto.group(1)}.º", "", "", "N.º") if ponto else None


_ANEXO = re.compile(r"^## (Anexo.*)$", re.I)
# «Artigo 5.º …» ou «Art. 5.º …» no início de uma linha de texto corrido (artigos que o `structure` não marcou).
_ARTIGO_SOLTO = re.compile(r"^(?:Artigo|ARTIGO|Art\.) ?\d+\.?[º°]")


def _nome_do_anexo(titulo: str) -> str:
    """O nome da parte de um anexo, pelo título `## …`.

    `## Anexo — CÓDIGO DO TRABALHO` fica como está, como sempre. Um `## ANEXO` em maiúsculas com título passa o
    título para a frente: `## ANEXO I — ESTATUTOS DA SIEV, S. A.` é «ESTATUTOS DA SIEV, S. A. (ANEXO I)». A razão
    é a pesquisa (a de hoje e a da aplicação 0.1.1): procura os códigos nas partes que começam por «Anexo», sem
    olhar a maiúsculas, e com «ANEXO — Código de Processo Penal» passava a responder pela republicação de 2007 do
    código (verificado com o código da 0.1.1). Sem título (`## ANEXO II`, `## ANEXO — (a que se refere o artigo
    1.º)`) fica como está: não tem nome de código."""
    titulo = titulo.strip()
    if titulo.startswith("Anexo"):
        return titulo
    rotulo, separador, nome = titulo.partition(" — ")
    nome = nome.strip()
    return f"{nome} ({rotulo.strip()})" if separador and nome and not nome.startswith("(") else titulo
_NOTA = re.compile(r"^> (Alterado|Aditado|Revogado|Retificado|Republicado)", re.I)
_LIGACAO = re.compile(r"<a [^>]*>(.*?)</a>")


@dataclass
class Artigo:
    parte: str
    numero: str
    epigrafe: str
    texto: str
    notas: list[str] = field(default_factory=list)
    forma: str = "Artigo"  # como vem no título: «Artigo», «ARTIGO», «Base» ou «N.º»

    @property
    def chave(self) -> str:
        """Identificador do artigo dentro do diploma: `anexo::3.º` ou `3.º`."""
        return f"{self.parte}::{self.numero}" if self.parte else self.numero


def corpo(markdown: str) -> str:
    """O texto do registo sem o cabeçalho YAML."""
    if markdown.startswith("---\n"):
        fim = markdown.find("\n---\n", 4)
        if fim != -1:
            return markdown[fim + 5 :]
    return markdown


def _ler(texto: str) -> tuple[list[Artigo], list[tuple[str, str]], int]:
    """Os artigos; o texto fora deles, por parte: (parte, texto); e quantas linhas de texto corrido começam por
    «Artigo N.º» ou «Art. N.º»."""
    resultado: list[Artigo] = []
    fora: list[tuple[str, str]] = []
    parte = ""
    atual: Artigo | None = None
    linhas: list[str] = []
    sem_artigo: list[str] = []  # o texto da parte antes do seu primeiro artigo
    # Um `## ANEXO` em maiúsculas fica à espera da sua primeira unidade: só então abre parte. Até lá (e se nunca a
    # tiver) o texto continua colado ao artigo anterior, como antes de 20/11/2026.
    a_espera: str | None = None
    soltos = 0

    def fechar() -> None:
        if atual is not None:
            atual.texto = "\n".join(linhas).strip()
            resultado.append(atual)

    def fechar_parte() -> None:
        corpo_ = "\n".join(sem_artigo).strip()
        if corpo_:
            fora.append((parte, corpo_))

    for linha in texto.splitlines():
        anexo = _ANEXO.match(linha)
        if anexo:
            titulo = anexo.group(1).strip()
            if titulo.startswith("Anexo"):
                fechar()
                fechar_parte()
                atual, linhas, sem_artigo, parte, a_espera = None, [], [], titulo, None
            else:
                a_espera = _nome_do_anexo(titulo)
            continue
        if linha.startswith("#") and not linha.startswith("######"):
            continue
        cabecalho = _cabecalho(linha)
        if cabecalho:
            fechar()
            if a_espera is not None:
                parte, a_espera = a_espera, None
            numero, epigrafe, inicio, forma = cabecalho
            atual, linhas = Artigo(parte, numero, epigrafe, "", forma=forma), ([inicio] if inicio else [])
            continue
        if _ARTIGO_SOLTO.match(linha):
            soltos += 1
        if atual is None:
            sem_artigo.append(linha)
            continue
        if _NOTA.match(linha):
            atual.notas.append(linha[2:].strip())
            continue
        linhas.append(_LIGACAO.sub(r"\1", linha))
    fechar()
    fechar_parte()
    return resultado, fora, soltos


def _pouco_marcado(artigos_: list[Artigo], soltos: int) -> bool:
    """O registo está quase todo em texto corrido e só tem títulos das formas novas («ARTIGO», «Base», «N.º»),
    em número pequeno face aos artigos por marcar: não se parte por eles."""
    return bool(artigos_) and all(a.forma != "Artigo" for a in artigos_) and soltos >= 3 and soltos * 5 >= len(artigos_)


def artigos(texto: str) -> list[Artigo]:
    """Os artigos do corpo de um registo, pela ordem em que aparecem."""
    resultado, _, soltos = _ler(texto)
    return [] if _pouco_marcado(resultado, soltos) else resultado


def fora_dos_artigos(texto: str) -> list[tuple[str, str]]:
    """(parte, texto) do que `artigos` não devolve: o texto antes do primeiro artigo do diploma (o preâmbulo ou, nas
    convenções, o decreto que as aprova) e de cada `## Anexo`, e os `## Anexo` sem artigos. Pela ordem do texto;
    vazio quando `artigos` também é."""
    resultado, fora, soltos = _ler(texto)
    return [] if not resultado or _pouco_marcado(resultado, soltos) else fora


_INTERVALO = re.compile(r"\bartigos?\s+(\d+)\.º\s+a\s+(\d+)\.º", re.I)


def menciona_artigo(texto: str, numero: str) -> bool:
    """Se um texto fala no artigo com este número: "artigo 7.º", "art. 7.º", "artigos 5.º e 7.º",
    "artigos 5.º a 9.º"; não "artigo 17.º" nem "artigo 7.º-A"."""
    base = re.escape(numero.replace(".º", "")).replace("\\-", "-")
    if re.search(rf"\bart(?:igos?|\.|s\.)\s*(?:\d+\.º(?:-[A-Z])?\s*(?:,|e)\s*)*{base}\.?\s*º(?!-[A-Z])", texto, re.I):
        return True
    inteiro = re.match(r"\d+", numero)
    return inteiro is not None and "-" not in numero and any(
        int(inicio) <= int(inteiro.group()) <= int(fim) for inicio, fim in _INTERVALO.findall(texto)
    )


def normalizar(texto: str) -> str:
    """Espaços colapsados, para comparar excertos com o texto do artigo."""
    return re.sub(r"\s+", " ", texto).strip()


def texto_em(caminho: Path, data: str | None) -> str:
    """Corpo do registo na data pedida (`version-at`), ou o texto atual sem data."""
    if data is None:
        return corpo(caminho.read_text(encoding="utf-8"))
    resultado = subprocess.run(
        [sys.executable, "-c", "from leis_portugal.cli import main; raise SystemExit(main())",
         "version-at", str(caminho), "--date", data],
        capture_output=True, text=True, check=True, cwd=RAIZ,
    )
    return corpo(resultado.stdout)


def artigo(caminho: Path, chave: str, data: str | None = None) -> Artigo | None:
    """Um artigo pela chave (`anexo::3.º` ou `3.º`), no texto atual ou numa data."""
    return next((a for a in artigos(texto_em(caminho, data)) if a.chave == chave), None)
