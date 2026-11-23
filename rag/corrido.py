"""Os artigos de um registo em texto corrido («Artigo 1.º … Art. 2.º …» sem `###### Artigo`), com salvaguarda.

O índice guarda em blocos de ~300 palavras os registos em que o leitor dos títulos (`avaliacao/comum.py`) não acha
nenhum artigo. Muitos são diplomas de 1960 a 1999 com os artigos em texto corrido. Aqui lê-se esse texto com o leitor
do acervo (`leis_portugal.domain.articles.parse_articles`), mas só se aceita a leitura quando a numeração mostra que
está certa (`numeracao_seguida`):

- todas as unidades são artigos (não bases, cláusulas nem números de portaria);
- em cada parte, a numeração começa em 1 (ou em «único») e segue de um em um, sem saltos, sem voltar atrás e sem
  números repetidos (um aditado com letra, «10.º-A», pode vir a seguir ao 10.º);
- nenhum artigo ficou aberto logo depois de «… passa a ter a seguinte redacção:», nem acaba nessa frase (a redação
  nova, de outro diploma, ficou noutra unidade: «Artigo 1.º» de outro decreto-lei abria uma «Parte 2»); e a numeração
  não recomeça logo depois de um artigo que acaba em «:» (texto citado, ou as rubricas de um orçamento);
- o último artigo de cada parte não tem dentro o artigo seguinte (umas aspas por fechar engolem o resto);
- não há nenhum título `###### Artigo` ou `###### 1.º` (registos mistos: o leitor lê só os títulos);
- nenhuma parte é o sumário de outra (`_tem_sumario`: «Artigo 1.º Objecto.» e, a seguir, o artigo 1.º a sério);
- o registo tem pelo menos três linhas «Artigo N.º» (`LINHAS_MINIMAS`), como a população que se reviu à mão;
- não é um acórdão nem um parecer (`le_o_tipo`): os artigos que lá estão são os da norma julgada;
- num diploma que «Aprova o Código …», todos os artigos ficam na parte do diploma (`codigo_no_diploma`).

As famílias de erro das amostras de 20/11/2026 (`reports/leitura-texto-corrido-amostra.md`) partem a numeração ou caem
numa destas regras: as rubricas de orçamento («Artigo 127.º «Remunerações acidentais»»), a redação nova de artigos de
outro diploma, os registos mistos, as aspas por fechar e os acórdãos.

**Nenhum texto sai do índice.** O que não fica em nenhum artigo (o preâmbulo, o que vem depois das assinaturas: mapas,
modelos, anexos sem artigos, os títulos dos capítulos) sai em `fora`, por parte, e o índice guarda-o todo em blocos, seja
qual for o tamanho (`rag.indice._unidades`). Fica só o título `# …` do registo, que nunca entrou nos blocos, e o «Artigo 3.º»
que abre cada artigo, que passa a ser o número do pedaço.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


LINHAS_MINIMAS = 3
TIPOS_DE_FORA = ("acordao", "parecer")  # prefixos de `document_type` (ver `le_o_tipo`)
# Como em `avaliacao/comum.py` e no inventário: «Artigo 5.º», «ARTIGO 5.º», «Art. 5.º» no início da linha.
_ARTIGO_SOLTO = re.compile(r"^(?:Artigo|ARTIGO|Art\.) ?\d+\.?[º°]", re.M)
_LIGACAO = re.compile(r"<a [^>]*>(.*?)</a>")


@dataclass
class ArtigoCorrido:
    """Um artigo lido do texto corrido, com os campos de `comum.Artigo` que o índice usa."""

    parte: str
    numero: str
    epigrafe: str
    texto: str
    notas: list[str] = field(default_factory=list)
    forma: str = "corrido"

    @property
    def chave(self) -> str:
        return f"{self.parte}::{self.numero}" if self.parte else self.numero


def _inteiro(numero: str) -> tuple[int, bool] | None:
    """(número inteiro, tem letra) de «10.º», «10.º-A»; None para «único» e outros."""
    m = re.match(r"^(\d+)", numero)
    return (int(m.group(1)), "-" in numero) if m else None


_APROVA_CODIGO = re.compile(r"Aprova o C[óo]digo")


def codigo_no_diploma(sumario: str | None) -> bool:
    """Um diploma que «Aprova o Código …» (o DL 44561, Código do Imposto de Capitais): a pesquisa procura o código pelo
    sumário e na parte do diploma («», `Pesquisa.codigos`). Se a leitura pusesse o código numa «Parte 2», «artigo 5.º do
    Código do Imposto de Capitais» ia dar ao artigo 5.º do decreto que o aprova. Estes registos só se leem como artigos
    quando todos os artigos ficam na parte do diploma; senão ficam em blocos, como antes."""
    return bool(_APROVA_CODIGO.match(sumario or ""))


def le_o_tipo(tipo: str) -> bool:
    """Os acórdãos e os pareceres citam artigos de outros textos (a norma julgada): não se leem como artigos."""
    return not tipo.startswith(TIPOS_DE_FORA)


def numeracao_seguida(lidos) -> bool:
    """Se a leitura do `parse_articles` passa a salvaguarda (ver o cabeçalho do módulo)."""
    from leis_portugal.domain.articles import _REDACTION  # noqa: PLC0415

    if not lidos or any(a.kind != "artigo" or a.repeat or a.quoted for a in lidos):
        return False
    # «… passa a ter a seguinte redacção:» no fim de um artigo: a redação nova ficou fora dele, noutra unidade.
    if any(_REDACTION.search(_ultima_linha(a.text)) for a in lidos):
        return False
    # A numeração recomeça (o `parse_articles` abre uma «Parte 2») logo a seguir a um artigo que acaba em «:»: o que vem
    # é texto citado («… na seguinte conformidade:», as rubricas «Capítulo 1.º … Artigo 1.º «Juros»» de um orçamento).
    for anterior, a in zip(lidos, lidos[1:], strict=False):
        if a.part_slug != anterior.part_slug and re.fullmatch(r"parte-\d+", a.part_slug) and _ultima_linha(anterior.text).endswith(":"):
            return False
    por_parte: dict[str, list] = {}
    for a in lidos:
        por_parte.setdefault(a.part_slug, []).append(a)
    for artigos in por_parte.values():
        # O artigo seguinte dentro do último (umas aspas por fechar engolem o resto do diploma).
        seguinte = _inteiro(_numero(artigos[-1].number))
        if seguinte and re.search(rf"^(?:Artigo|ARTIGO|Art\.) ?{seguinte[0] + 1}\.?[º°]", artigos[-1].text, re.M):
            return False
        anterior = None
        for posicao, a in enumerate(artigos):
            numero = _numero(a.number)
            inteiro = _inteiro(numero)
            if inteiro is None:
                if numero != "único" or posicao != 0:
                    return False
                continue
            valor, com_letra = inteiro
            if anterior is None:
                if valor != 1 or com_letra:
                    return False
            elif not (valor == anterior + 1 and not com_letra) and not (valor == anterior and com_letra):
                return False
            anterior = valor
    return True


def _ultima_linha(texto: str) -> str:
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    return linhas[-1] if linhas else ""


def _numero(bruto: str) -> str:
    """O número na forma das perguntas e do índice («1.º», «10.º-A», «único»)."""
    from rag.fontes import comum  # noqa: PLC0415

    numero = comum.numero_artigo(bruto) or bruto
    return "único" if numero.lower() in ("único", "unico") else numero


def _parte(titulo: str) -> str:
    """O nome da parte: como nos títulos (`comum._nome_do_anexo`), o título de um «ANEXO — X» vem à frente."""
    from rag.fontes import comum  # noqa: PLC0415

    titulo = _LIGACAO.sub(r"\1", titulo).strip()
    return comum._nome_do_anexo(titulo) if re.match(r"(?i)anexo", titulo) else titulo


def _normal(linha: str) -> str:
    return " ".join(_LIGACAO.sub(r"\1", linha).split())


def ler(texto: str, *, so_no_diploma: bool = False) -> tuple[list[ArtigoCorrido], list[tuple[str, str]]] | None:
    """(artigos, fora) de um corpo em texto corrido, ou None se a leitura não passa a salvaguarda.

    `fora`: (parte, texto) do que não ficou em nenhum artigo, pela ordem do texto. Uma linha conta como lida quando
    é a linha que abre um artigo, a da epígrafe ou uma linha do texto de um artigo (comparadas sem espaços a mais)."""
    if len(_ARTIGO_SOLTO.findall(texto)) < LINHAS_MINIMAS:
        return None
    from leis_portugal.domain.articles import _HEADING_ARTICLE, _HEADING_POINT, parse_articles  # noqa: PLC0415

    # Com algum título `###### …` o `parse_articles` lê só os títulos e os artigos seguintes a eles: registos mistos.
    if any(_HEADING_ARTICLE.match(linha) or _HEADING_POINT.match(linha) for linha in texto.splitlines()):
        return None
    lidos = parse_articles(texto)
    if not numeracao_seguida(lidos):
        return None
    artigos = [ArtigoCorrido(_parte(a.part), _numero(a.number), a.heading, a.text, list(a.notes)) for a in lidos]
    if _tem_sumario(artigos) or (so_no_diploma and any(a.parte for a in artigos)):
        return None
    return artigos, _fora(texto, lidos)


def _sem_ponto(texto: str) -> str:
    return " ".join(texto.split()).rstrip(". ").lower()


def _tem_sumario(artigos: list[ArtigoCorrido]) -> bool:
    """Uma parte que é o sumário de outra: «Artigo 1.º Objecto e campo de aplicação.», «Artigo 2.º Simbologia…», e a
    seguir o regulamento com os mesmos números, cada artigo a começar pela epígrafe (o DL 235/83). Conta quando 80 %
    dos artigos de uma parte (pelo menos três) são o início do artigo com o mesmo número noutra parte."""
    partes: dict[str, dict[str, str]] = {}
    for a in artigos:
        partes.setdefault(a.parte, {})[a.numero] = _sem_ponto(a.texto)
    for nome, textos in partes.items():
        if len(textos) < 3:
            continue
        for outro, textos_outro in partes.items():
            if outro == nome:
                continue
            inicios = sum(
                1 for numero, t in textos.items()
                if t and len(textos_outro.get(numero, "")) > len(t) + 20 and textos_outro[numero].startswith(t)
            )
            if inicios >= 0.8 * len(textos):
                return True
    return False


def _fora(texto: str, lidos) -> list[tuple[str, str]]:
    from collections import Counter  # noqa: PLC0415

    from leis_portugal.domain.articles import _HEADING  # noqa: PLC0415

    lidas: Counter = Counter()
    for a in lidos:
        lidas[_normal(a.source_line)] += 1
        if a.heading:
            lidas[_normal(a.heading)] += 1
            lidas[_normal(f"({a.heading})")] += 1
        for linha in a.text.splitlines():
            if linha.strip():
                lidas[_normal(linha)] += 1
        for nota in a.notes:
            lidas[_normal("> " + nota)] += 1
    fora: list[tuple[str, str]] = []
    parte, atual = "", []
    nomes = iter(dict.fromkeys(a.part for a in lidos if a.part))
    proxima = next(nomes, None)

    def fechar() -> None:
        corpo_ = "\n".join(atual).strip()
        if corpo_:
            fora.append((parte, corpo_))

    for linha in texto.splitlines():
        titulo = _HEADING.match(linha)
        if titulo and len(titulo.group(1)) == 2 and proxima is not None and titulo.group(2).strip() == proxima:
            fechar()
            parte, atual, proxima = _parte(proxima), [], next(nomes, None)
            continue
        if proxima is not None and linha.strip() == proxima:  # uma linha «ANEXO …» do texto corrido
            fechar()
            parte, atual, proxima = _parte(proxima), [], next(nomes, None)
            continue
        normal = _normal(linha)
        if normal and lidas[normal] > 0:
            lidas[normal] -= 1
            atual.append("")  # o que estava antes e o que vem depois não se juntam no mesmo parágrafo
            continue
        atual.append(linha)
    fechar()
    return [(p, re.sub(r"\n{3,}", "\n\n", t)) for p, t in fora]
