"""As normas que cada acórdão de uniformização do STJ e do STA publicado no Diário da República interpretou.

Os acórdãos do Supremo Tribunal de Justiça e do Supremo Tribunal Administrativo publicados na 1.ª Série
são quase todos de uniformização (ou, no processo penal, de fixação) de jurisprudência. De cada um lê-se
só a jurisprudência fixada, o segmento uniformizador da decisão ("fixa-se a seguinte jurisprudência: «…»"),
e tiram-se dele o artigo e o diploma, com a mesma leitura das normas dos acórdãos do TC
(`rag.jurisprudencia.normas`).

A fundamentação cita muitas vezes outros acórdãos de uniformização e a jurisprudência que eles fixaram
("Nos termos do Acórdão Uniformizador de 8 de Maio de 2013, «Transitada em julgado…»"): isso não é o que
este acórdão decidiu. O texto fixado é por isso o do sumário publicado no Diário da República, que é o
segmento uniformizador deste acórdão. A última fórmula de fixação da decisão (antes das declarações de voto
e da assinatura) só o confirma (`confirmado`): às vezes é a jurisprudência de outro acórdão citada no fim,
ou remete para outro ponto ("no sentido fixado no ponto 3.2.13"). Sem sumário, vale a decisão (`fonte`).

    python -m rag.uniformizacao --indice …/indice.sqlite   # grava data/jurisprudencia/uniformizacao/normas-interpretadas.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from rag import jurisprudencia as tc
from rag.fontes import RAIZ, corpo


NOMES_TRIBUNAIS = {"STJ": "Supremo Tribunal de Justiça", "STA": "Supremo Tribunal Administrativo"}
_PORTUGAL = RAIZ / "data" / "portugal"
# (tribunal, pasta, emissor exigido). Até 2007 o DRE classificava estes acórdãos como "Acórdão" (com os do TC e
# do Tribunal de Contas, em `outros/acordao`) e, de 2001 a 2004, os do STJ como "Jurisprudência".
PASTAS: list[tuple[str, Path, str | None]] = [
    ("STJ", _PORTUGAL / "acordaos-supremo-tribunal-justica", None),
    ("STA", _PORTUGAL / "acordaos-supremo-tribunal-administrativo", None),
    ("STJ", _PORTUGAL / "outros" / "jurisprudencia", NOMES_TRIBUNAIS["STJ"]),
    ("STJ", _PORTUGAL / "outros" / "acordao", NOMES_TRIBUNAIS["STJ"]),
    ("STA", _PORTUGAL / "outros" / "acordao", NOMES_TRIBUNAIS["STA"]),
]
SAIDA = tc.SAIDA_UNIFORMIZACAO

# ------------------------------------------------------------------ onde está a jurisprudência fixada

# "fixa a seguinte jurisprudência", "uniformizar jurisprudência", "uniformiza-se a jurisprudência",
# "uniformizando-se jurisprudência", "fixando-se jurisprudência", "reafirmar a jurisprudência".
_FIXA = re.compile(
    r"(?<!\w)(fix|uniformiz|reafirm|reiter|confirm|mant)"
    r"(?:a|ar|am|e|em|a-se|ando|ando-se|ou)(?![\w-])"
    r"\s*(?:,\s*)?(?:assim\s*,?\s*|em\s+consequência\s*,?\s*|ainda\s*,?\s*)?"
    r"(?:a\s+|o\s+)?(?:seguinte\s+)?(?:jurisprud[êe]ncia|segmento\s+uniformizador)",
    re.I,
)
# O que vem a seguir à fórmula: o texto fixado ("nos seguintes termos:", "no sentido de que") ou uma remissão.
_INTRODUCAO = re.compile(
    r"^\s*(?:(?:do|deste)\s+(?:STA|STJ|Supremo\s+Tribunal\s+\w+)\s*,?\s*)?"
    r"(?:(?:uniformizadora|obrigatória)\s*)?"
    r"(?:(?:nos|com\s+os|pelos)\s+seguintes\s+termos|no\s+(?:seguinte\s+)?sentido(?:\s+seguinte)?(?:\s+de(?:\s+que)?)?|"
    r"(?:de\s+)?que|com\s+o\s+seguinte\s+(?:teor|sentido|conteúdo)|seguinte|assim\s+formulada|nestes\s+termos)?"
    r"\s*[:,\-–—]?\s*",
    re.I,
)
_REMISSAO = re.compile(
    r"^\s*(?:(?:no|com\s+o)\s+sentido\s+(?:fixado|enunciado|exposto|referido|definido|indicado|acima|supra)|"
    r"nos\s+termos\s+(?:supra|acima|atrás|descritos|referidos|expostos|enunciados|já|do\s+ponto|da\s+conclusão|fixados\s+no\s+ponto)|"
    r"(?:supra|acima)\s|e\s+ordenar|,?\s*(?:e\s+)?ordenando|\.)",
    re.I,
)
# O fim do texto fixado: custas, notificação, publicação, alínea seguinte da decisão, assinatura.
_FIM = re.compile(
    r"(?:^|\n|(?<=[.;»”\"])\s*)\s*(?:\*+\s*)?(?:(?:[b-z]|i{2,3}|iv|v|\d+)\s*\)\s*(?!\s*(?:Se|O|A|Os|As|No|Na|Em|É|Não|Quando|Para|Tendo|Sendo)\b)"
    r"(?=[^\n]{0,40}?(?:revog|conced|neg|anul|julg|ordenar|confirm|condena|determina|custas|remet|manter|dar\s+provimento|baixa|notific|public))"
    r"|Sem\s+custas|Custas\b|Custas\s+pel|Cumpra-se|Oportunamente|Notifique|Publique-se|Registe|D[êe]-se\s+cumprimento|"
    r"Lisboa\s*,|L\.\s*,|Supremo\s+Tribunal\s+(?:de\s+Justiça|Administrativo)\s*,\s*\d|Porto\s*,\s*\d|"
    r"Revoga-se|Revogar|Concede-se|Nega-se|Anula-se|Em\s+consequência\s*,|Consequentemente\s*,|E,\s+em\s+consequência|"
    r"\(?Processado|\(?Texto\s+processado|O\s+presente\s+acórdão\s+(?:é|vai|será))",
    re.I,
)
# Declarações de voto e votos de vencido vêm depois da assinatura e citam a jurisprudência fixada.
_VOTO = re.compile(
    r"^\s*[\*#]*\s*(?:Declara[çc][ãa]o(?:\s+de\s+voto)?|Declara[çc][õo]es\s+de\s+voto|Voto\s+(?:de\s+)?(?:vencid|venc\.)|Votos?\s+de\s+vencid|Vencid[oa]\b)",
    re.M | re.I,
)
_ASSINATURA = re.compile(
    r"^\s*(?:Lisboa|L\.|Supremo\s+Tribunal\s+(?:de\s+Justiça|Administrativo)|S\.\s*T\.\s*[JA]\.?|Porto)\s*,\s*\d{1,2}\s*(?:\.?\s*º)?\s*(?:de\s+)?[A-Za-zçÇ]+\s+(?:de\s+)?\d{4}",
    re.M | re.I,
)
_MESES = {m: i for i, m in enumerate(
    ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"], 1)}
_DATA = re.compile(r"(\d{1,2})\s*(?:\.?\s*º)?\s*(?:de\s+)?([A-Za-zçÇ]+)\s+(?:de\s+)?(\d{4})")
_DATA_SUMARIO = re.compile(r"Acórdão\s+do\s+(?:STA|STJ|Supremo\s+Tribunal\s+\w+)\s+de\s+(?:(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})|(\d{1,2})\s+de\s+([A-Za-zç]+)\s+de\s+(\d{4}))", re.I)
# O prefixo dos sumários do DR antes do texto fixado.
_PREFIXO_SUMARIO = re.compile(
    r"^.*?(?:Uniformiz\w*(?:-se)?(?:/confirma)?\s+(?:a\s+)?jurisprud[êe]ncia(?:\s+do\s+STA)?\s*,?\s*"
    r"(?:nos\s+(?:seguintes\s+)?termos(?:\s+descritos\s+em\s+[\d.]+)?|no\s+sentido(?:\s+seguinte)?(?:\s+de(?:\s+que)?)?)?\s*[:.]?\s*)",
    re.I | re.S,
)


def _data_iso(dia: str, mes: str, ano: str) -> str | None:
    mes_n = int(mes) if mes.isdigit() else _MESES.get(mes.lower().replace("ç", "ç"))
    if not mes_n or not (1 <= int(dia) <= 31) or not (1 <= mes_n <= 12):
        return None
    return f"{int(ano):04d}-{mes_n:02d}-{int(dia):02d}"


def principal(texto: str) -> str:
    """O acórdão sem as declarações de voto (que vêm depois da assinatura e discutem a jurisprudência fixada)."""
    for m in _VOTO.finditer(texto):
        # "Vencido" a meio da lista de juízes não conta: só um título numa linha que vem depois da assinatura.
        if _ASSINATURA.search(texto, 0, m.start()) or m.start() > len(texto) * 0.6:
            return texto[: m.start()]
    return texto


def data_decisao(texto: str) -> str | None:
    """A data da assinatura do acórdão ("Lisboa, 11 de outubro de 2023")."""
    for m in _ASSINATURA.finditer(texto):
        d = _DATA.search(m.group(0))
        if d and (iso := _data_iso(*d.groups())):
            return iso
    return None


def _cortar(texto: str) -> str:
    """O texto fixado até às custas, à alínea seguinte da decisão ou à assinatura."""
    m = _FIM.search(texto, 1)
    return texto[: m.start()] if m else texto


def _aspas(texto: str) -> str | None:
    """O texto entre aspas no início («…», “…” ou "…"), que é o que se fixa."""
    m = re.match(r"\s*(?:[\*:]\s*)*([«“\"])", texto)
    if not m:
        return None
    fecho = {"«": "»", "“": "”", '"': '"'}[m.group(1)]
    fim = texto.find(fecho, m.end())
    if fim < 0:
        return None
    dentro = texto[m.end(): fim]
    # Aspas aninhadas («… «artigo» …»): continuar até ao fecho que equilibra.
    while dentro.count("«") > dentro.count("»") and (fim := texto.find(fecho, fim + 1)) >= 0:
        dentro = texto[m.end(): fim]
    return dentro


def fixada_na_decisao(texto: str) -> str | None:
    """O texto da jurisprudência fixada, tirado da decisão, ou None quando a decisão não o traz
    (remete para outro ponto do acórdão ou só diz "uniformizar jurisprudência")."""
    corpo_principal = principal(texto)
    candidatos = list(_FIXA.finditer(corpo_principal))
    # Da última para a primeira: a decisão vem no fim. Uma fórmula sem texto a seguir ("… e uniformizar
    # jurisprudência nos termos supra referidos") remete para trás, para o ponto onde o texto foi formulado.
    for m in reversed(candidatos):
        if m.start() < len(corpo_principal) * 0.35:
            break
        resto = corpo_principal[m.end(): m.end() + 6000]
        if _REMISSAO.match(resto):
            continue
        intro = _INTRODUCAO.match(resto)
        depois = resto[intro.end():] if intro else resto
        entre_aspas = _aspas(depois)
        fixado = entre_aspas if entre_aspas is not None else _cortar(depois)
        fixado = re.sub(r"\s+", " ", fixado).strip(" .;:-–—*")
        if len(fixado) >= 40:
            return fixado
    return None


_PREFIXO_ACORDAO = re.compile(
    r"^Acórdão\s+do\s+(?:STA|STJ|Supremo\s+Tribunal\s+\w+)\b[^«]{0,160}?"
    r"(?:Sec[çc][ãa]o(?:\s+do\s+Contencioso\s+Tributário)?|Ampliado|n\.\s*º\s*:?\s*[\w./-]+(?:\s*\([^)]*\))?)\s*(?:[-―—–.:]\s*)*",
    re.I,
)


# O que sobra da identificação do processo: "1.ª Secção Julgamento Ampliado ―", "Pleno da 1.ª Secção".
_PREFIXO_SECCAO = re.compile(
    r"^(?:Pleno\s+da\s+)?(?:\d\.ª\s+)?Sec[çc][ãa]o(?:\s+(?:do|de)\s+Contencioso\s+\w+)?(?:\s*[-―—–]?\s*Julgamento\s+Ampliado)?\s*(?:[-―—–.:]\s*)+"
    r"|^Julgamento\s+Ampliado\s*(?:[-―—–.:]\s*)+",
    re.I,
)


def fixada_no_sumario(sumario: str) -> str | None:
    """O texto fixado no sumário do DR, sem o prefixo ("Acórdão do STA de …, no Processo …. Uniformiza a
    jurisprudência nos seguintes termos:")."""
    if not sumario:
        return None
    texto = re.sub(r"\s+", " ", sumario).replace("­", "").strip()
    for _ in range(3):
        antes = texto
        if m := _PREFIXO_SUMARIO.match(texto):
            texto = texto[m.end():].strip()
        if m := _PREFIXO_ACORDAO.match(texto):
            texto = texto[m.end():].strip()
        if m := _PREFIXO_SECCAO.match(texto):
            texto = texto[m.end():].strip()
        if texto == antes:
            break
    texto = texto.strip(" «»\"“”.―—-")
    return texto if len(texto) >= 40 else None


def _palavras(texto: str) -> set[str]:
    return set(re.findall(r"[a-z]{4,}", tc.refs_mod.sem_acentos(texto.lower())))


def confirmada(sumario: str, decisao: str | None) -> bool:
    """O texto do sumário está na decisão: metade das palavras dele aparecem no texto fixado na decisão."""
    if not decisao:
        return False
    palavras = _palavras(sumario)
    return bool(palavras) and len(palavras & _palavras(decisao)) / len(palavras) >= 0.5


# O texto fixado antes de ler as normas: sem ligações e sem as orações sobre a redação do diploma.
_LIGACAO = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_PARENTESES_ALTERACAO = re.compile(
    r"\(\s*(?:aprovad|alterad|na\s+(?:sua\s+)?(?:redac?[çc][ãa]o|vers[ãa]o)|republicad|com\s+as\s+altera|introduzid|actualizad|atualizad)[^()]*\)",
    re.I,
)


# Abreviaturas que a leitura das normas não conhece, e códigos citados com o ano ("Código do Trabalho de
# 2003"), que não são os em vigor na data do acórdão.
_ABREVIATURAS = [
    (r"\bC\.\s*Civil\b", "Código Civil"),
    (r"\bC\.\s*Penal\b", "Código Penal"),
    (r"\bC\.\s*P\.\s*P(?:enal|\.)", "CPP"),
    (r"\bC\.\s*P\.\s*C(?:ivil|\.)", "CPC"),
    (r"\bC\.\s*P\.\s*T\.\s*A\.", "CPTA"),
    (r"\bC\.\s*P\.\s*T\.", "CPT"),
    (r"\bR\.\s*G\.\s*I\.\s*T\.", "RGIT"),
    (r"\bC\.\s*I\.\s*R\.\s*E\.", "CIRE"),
    (r"\bCód\.\s*", "Código "),
    (r"(?<=\s)0(?=[1-9]\d*\s*\.?\s*º)", ""),  # "arts. 04.º, n.º 1, do ETAF"
    (r"\bCPA\s*/\s*91\b", "Decreto-Lei n.º 442/91"),
    (r"\bCPC\s*/\s*61\b", "Decreto-Lei n.º 44129"),
    (r"\bCT\s*/\s*2003\b", "Lei n.º 99/2003"),
    (r"C[óo]digo\s+do\s+Trabalho\s+de\s+2003", "Lei n.º 99/2003"),
    # "Código Penal de 1982, revisão de 1995" é o de hoje; "na versão de 1982" e "de 1982, versão original" não.
    (r"C[óo]digo\s+Penal\s+de\s+1982,?\s+(?:na\s+)?(?:revisão|revisto|redac?[çc][ãa]o)\s+(?:de|em)\s+1995", "Código Penal"),
    (r"C[óo]digo\s+Penal(?:\s+de\s+1982|,?\s+na\s+(?:sua\s+)?versão\s+de\s+1982)", "Decreto-Lei n.º 400/82"),
    (r"C[óo]digo\s+de\s+Processo\s+Penal\s+de\s+1929", "Decreto n.º 16489"),
    (r"C[óo]digo\s+da\s+Estrada\s+de\s+1954", "Decreto-Lei n.º 39672"),
    (r"C[óo]digo\s+da\s+Estrada\s+de\s+1998", "Decreto-Lei n.º 2/98"),
    (r"C[óo]digo\s+de\s+Processo\s+do\s+Trabalho(?:\s+de\s+1981|,?\s+aprovado\s+pelo\s+Decreto-Lei\s+n\.º\s+272-A/81)", "Decreto-Lei n.º 272-A/81"),
    (r"C[óo]digo\s+de\s+Processo\s+Civil\s+de\s+1961", "Decreto-Lei n.º 44129"),
    (r"C[óo]digo\s+do\s+Procedimento\s+Administrativo\s+de\s+1991", "Decreto-Lei n.º 442/91"),
]


def preparar(texto: str) -> str:
    texto = _LIGACAO.sub(r"\1", texto)
    for padrao, por in _ABREVIATURAS:
        texto = re.sub(padrao, por, texto, flags=re.I if padrao.startswith("C[") else 0)
    # Os dois códigos estão em anexos da Lei n.º 22-A/2007, e ambos têm artigos 1.º a 80.º: pelo nome escolhe-se o anexo.
    texto = re.sub(r"\bCISV\b|C[óo]digo\s+do\s+ISV\b", "Código do Imposto sobre Veículos", texto)
    texto = re.sub(r"\bCIUC\b|C[óo]digo\s+do\s+IUC\b", "Código do Imposto Único de Circulação", texto)
    texto = _PARENTESES_ALTERACAO.sub(" ", texto)
    # "na redacção originária do n.º 1 do artigo 10.º da Lei n.º 23/96" e "cláusula de redacção conforme ao
    # artigo 781.º do Código Civil": a lei citada não é um diploma de alteração.
    texto = re.sub(r"redac?[çc][ãa]o\s+(originária|inicial|primitiva|original)", r"versão \1", texto, flags=re.I)
    texto = re.sub(r"(?:de\s+)?redac?[çc][ãa]o\s+conforme", "conforme", texto, flags=re.I)
    return re.sub(r"\s+", " ", texto).strip()


# ------------------------------------------------------------------ sentido

_SECCOES_CRIMINAIS = re.compile(r"Sec[çc][õo]es\s+Criminais|Sec[çc][ãa]o\s+Criminal", re.I)


_DECLARA_ILEGALIDADE = re.compile(r"^\s*Declara,?\s+com\s+força\s+obrigatória\s+geral,?\s+a\s+ilegalidade", re.I)


def sentido(texto: str, tribunal: str, assuntos: list[str] | None = None, fixado: str = "") -> str:
    """No processo penal o Pleno das Secções Criminais do STJ fixa jurisprudência (artigos 437.º e 445.º
    do CPP); as Secções Cíveis e Social do STJ e o STA uniformizam-na. Sem texto (só o sumário no DR),
    decidem os assuntos do registo."""
    if _DECLARA_ILEGALIDADE.match(fixado):
        # O STA declara a ilegalidade de normas regulamentares com força obrigatória geral (1992).
        return "declara_ilegalidade_fog"
    if tribunal != "STJ":
        return "uniformiza_jurisprudencia"
    if _SECCOES_CRIMINAIS.search(texto):
        return "fixa_jurisprudencia"
    fixacao = len(re.findall(r"fixação\s+de\s+jurisprud", texto, re.I))
    uniformizacao = len(re.findall(r"uniformização\s+de\s+jurisprud", texto, re.I))
    if fixacao or uniformizacao:
        return "fixa_jurisprudencia" if fixacao > uniformizacao else "uniformiza_jurisprudencia"
    if any(a in {"Processo Penal", "Crime", "Código de Processo Penal", "Código Penal"} for a in assuntos or []):
        return "fixa_jurisprudencia"
    return "uniformiza_jurisprudencia"


# ------------------------------------------------------------------ acórdão inteiro


@dataclass
class Acordao:
    acordao: str  # id do registo (pt:dre:116826827:por)
    tribunal: str  # STJ ou STA
    numero: str  # "5/2018"
    data: str | None  # da decisão; a da publicação quando não se lê
    publicacao: str | None
    url: str | None
    sentido: str
    fonte: str  # "sumario" ou "decisao": de onde veio o texto fixado
    confirmado: bool  # o texto do sumário também está na fórmula de fixação da decisão
    alinea: str  # o texto fixado (só para medir a extração; a resposta não o mostra)
    normas: list[tc.Norma] = field(default_factory=list)


def cabecalho(markdown: str) -> dict:
    if not markdown.startswith("---\n"):
        return {}
    return yaml.safe_load(markdown[4: markdown.find("\n---\n", 4)]) or {}


def texto_fixado(texto: str, sumario: str) -> tuple[str, str, bool] | None:
    """(texto fixado, fonte, confirmado).

    O sumário publicado no DR é o segmento uniformizador deste acórdão. A última fórmula de fixação
    da decisão costuma trazer o mesmo texto, mas às vezes é a jurisprudência de outro acórdão citada
    no fim ("na linha do entendimento propugnado pelo acórdão fundamento…", o AUJ n.º 11/2024 lido no
    8/2025) ou remete para um ponto anterior: por isso o sumário vem primeiro e a decisão só confirma,
    ou serve quando o sumário não traz texto."""
    na_decisao = fixada_na_decisao(texto)
    no_sumario = fixada_no_sumario(sumario)
    if no_sumario:
        return no_sumario, "sumario", confirmada(no_sumario, na_decisao)
    if na_decisao:
        return na_decisao, "decisao", False
    return None


def ler(markdown: str, tribunal: str) -> Acordao | None:
    campos = cabecalho(markdown)
    texto = corpo(markdown).replace("\u00ad", "")
    sumario = str(campos.get("summary") or "")
    achado = texto_fixado(texto, sumario)
    if achado is None:
        return None
    fixado, fonte, confirmado = achado
    data = data_decisao(principal(texto))
    if data is None and (m := _DATA_SUMARIO.search(sumario)):
        data = _data_iso(m.group(1), m.group(2), m.group(3)) if m.group(1) else _data_iso(m.group(4), m.group(5), m.group(6))
    publicacao = str(campos.get("publication_date") or "") or None
    # Uma data de decisão posterior à publicação, ou com mais de 3 anos antes dela, é uma gralha da leitura.
    if data and publicacao and not (str(int(publicacao[:4]) - 3) <= data <= publicacao):
        data = None
    fonte_url = (campos.get("source") or {}).get("official_url")
    normas = tc.normas(preparar(fixado), tc.siglas_do_acordao(texto), sigla_desconhecida=True)
    for n in normas:
        # O texto fixado é todo interpretação: os artigos que cita são os que o acórdão interpretou ou aplicou.
        n.principal = True
    return Acordao(
        acordao=campos.get("id", ""), tribunal=tribunal, numero=str(campos.get("official_number") or ""),
        data=data or publicacao, publicacao=publicacao, url=fonte_url or None, sentido=sentido(principal(texto), tribunal, campos.get("subjects") or [], fixado),
        fonte=fonte, confirmado=confirmado, alinea=fixado, normas=normas,
    )


_ANEXO_NAO_CODIGO = re.compile(r"tabela|emolumentos|mapa|quadro|modelo|formulário|minuta", re.I)


class Resolvedor(tc.Resolvedor):
    """O do TC, mais: um nome de código que a leitura apanhou com palavras a mais ("Código Penal e não o
    crime de desobediência qualificada do artigo") resolve-se pelo nome mais comprido que o índice conhece."""

    def resolver(self, norma: tc.Norma, data: str | None = None) -> tc.Norma:
        norma = super().resolver(norma, data)
        if norma.parte and norma.parte.startswith("Anexo") and norma.documento and norma.artigo:
            # Vários anexos com o mesmo artigo: o que tem o nome do diploma citado.
            anexos = [linha[0] for linha in self.p.con.execute(
                "SELECT DISTINCT parte FROM pedacos WHERE documento = ? AND numero = ? AND parte LIKE 'Anexo%'", (norma.documento, norma.artigo))]
            if len(anexos) > 1:
                citado = set(tc.chave_nome(norma.diploma_texto).split())
                melhor = max(anexos, key=lambda a: (len(citado & set(tc.chave_nome(a).split())), a == norma.parte))
                if len(citado & set(tc.chave_nome(melhor).split())) > len(citado & set(tc.chave_nome(norma.parte).split())):
                    norma.parte = melhor
        if norma.parte and _ANEXO_NAO_CODIGO.search(norma.parte) and norma.documento and norma.artigo:
            # O artigo 7.º do Código do Registo Predial está no próprio Decreto-Lei n.º 224/84, não no anexo
            # com a tabela de emolumentos, que também tem um artigo 7.º.
            if self.p.con.execute("SELECT 1 FROM pedacos WHERE documento = ? AND numero = ? AND parte = ''", (norma.documento, norma.artigo)).fetchone():
                norma.parte = ""
        if norma.documento or not norma.codigo or tc.no_tempo(norma, data) is None:
            return norma
        palavras = norma.codigo.split()
        for n in range(len(palavras) - 1, 1, -1):
            nome = " ".join(palavras[:n])
            if re.search(r"\b(?:d[oa]s?|de|e|em|n[oa]s?|ou)$", nome):
                continue
            codigo, fixo = tc.nome_canonico(nome)
            curta = tc.Norma(norma.artigo, nome, fixo[0] if fixo else None, fixo[1] if fixo else None,
                             None if fixo else codigo, principal=norma.principal)
            curta = super().resolver(curta, data)
            if curta.documento:
                return curta
        return norma


def construir(pesquisa, pastas: list[tuple[str, Path, str | None]] = PASTAS, saida: Path = SAIDA, progresso=print) -> Counter:
    resolvedor = Resolvedor(pesquisa)
    contas: Counter = Counter()
    linhas = []
    for tribunal, pasta, emissor in pastas:
        for caminho in sorted(pasta.rglob("*.md")):
            markdown = caminho.read_text(encoding="utf-8")
            if emissor and emissor not in (cabecalho(markdown).get("issuing_authority") or []):
                continue
            contas[f"acordaos:{tribunal}"] += 1
            acordao = ler(markdown, tribunal)
            if acordao is None:
                contas[f"sem_texto_fixado:{tribunal}"] += 1
                continue
            contas[f"fonte:{acordao.fonte}"] += 1
            contas["confirmados_na_decisao"] += acordao.confirmado
            resolvidas = [resolvedor.resolver(n, acordao.data) for n in acordao.normas]
            # O mesmo artigo citado duas vezes ("artigo 113.º do Código de Processo Penal" e "do CPP") conta uma.
            vistas: set = set()
            ligados = {n.artigo for n in resolvidas if n.documento and n.artigo}
            acordao.normas = []
            for n in resolvidas:
                chave = (n.artigo, n.documento or n.diploma_texto, n.parte)
                if chave in vistas or (not n.documento and n.artigo in ligados):
                    continue
                vistas.add(chave)
                acordao.normas.append(n)
            if not acordao.normas:
                contas[f"sem_norma:{tribunal}"] += 1
            if any(n.artigo_encontrado for n in acordao.normas):
                contas[f"com_artigo_encontrado:{tribunal}"] += 1
            for norma in acordao.normas:
                contas[f"normas:{tribunal}"] += 1
                contas["normas_com_diploma"] += bool(norma.documento)
                contas["normas_com_artigo"] += bool(norma.artigo)
                contas["normas_artigo_encontrado"] += norma.artigo_encontrado
            linhas.append(json.dumps(asdict(acordao), ensure_ascii=False))
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    progresso(f"{len(linhas)} acórdãos gravados em {saida}")
    return contas


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--saida", type=Path, default=SAIDA)
    parser.add_argument("--indice", type=Path, default=None, help="o indice.sqlite (por omissão o de RAG_INDICE)")
    args = parser.parse_args(argv)
    from rag.pesquisa import Pesquisa

    contas = construir(Pesquisa(args.indice), saida=args.saida, progresso=lambda m: print(m, file=sys.stderr))
    for chave, valor in sorted(contas.items()):
        print(f"{chave}: {valor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
