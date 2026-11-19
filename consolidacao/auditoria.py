"""Auditoria dos consolidados do leis-portugal: retificações fora da cadeia e vigência.

Mede os dois achados do bloco 3 (ronda 114, `PENDENTE.md`, secção 7) nos registos que o
leis-portugal já consolidou (`consolidated_by` a começar por «leis-portugal» no `*.versoes.json`).
Só lê: não muda nada no `data/` nem no índice.

1. **Retificações.** Para cada consolidado, as relações `corrected_by` do DRE cujo alvo não está
   nos `acts` das versões. Cada retificação por aplicar é lida e classificada:
   - `sem_registo`: a declaração não está no acervo;
   - `outro_diploma`: o texto não menciona o número do original (o DRE ligou-a ao diploma errado);
   - `imagem_ou_republicacao`: sem «onde se lê», republica o texto ou um mapa (muitas vezes em imagem);
   - `sem_pares`: sem «onde se lê … deve ler-se …» que se leia, e sem imagem (fica para o LLM);
   - com pares, cada par tem um estado: `unico` (o «onde se lê» está uma vez no texto em vigor),
     `aprox` (está uma vez, mas só sem pontuação nem maiúsculas: «artigo 50» e «artigo 50.º»),
     `ja` (já lá está o «deve ler-se»), `metadados` (o par é do sumário, do título ou da data),
     `substituido` (o «onde se lê» está no original publicado mas já não no texto em vigor: uma
     alteração posterior reescreveu o trecho), `varios` (aparece mais de uma vez), `sem_aspas`
     (sem «», quase sempre quadros e mapas) e `ausente`.
     A retificação fica `por_regra` quando todos os pares são `unico`, `ja` ou `metadados` e pelo
     menos um é `unico`; `por_regra_aprox` quando há também `aprox`; `ja_no_texto` quando estão
     todos já aplicados; `so_metadados`; `substituida` quando nenhum par se aplica ao texto em vigor
     por ter sido reescrito; o resto é `llm`.
2. **Vigência.** Cada consolidado cai numa das quatro classes do achado (concessões de caça, cursos
   anteriores a Bolonha, regimes de um só ano, orgânicas de serviços), com certeza `alta` ou
   `incerta`, pelo título, o sumário, o tipo e a data. `alta` quer dizer que o diploma é da classe,
   não que deixou de vigorar. À parte, as provas que o registo já tem: `legal_status` diferente de
   `in_force`, relações `repealed_by` de revogação inteira, nas concessões de caça o fim do prazo
   que o texto dá (`fim_estimado`) e os diplomas do ultramar anteriores a 1976.

Uso (na raiz do repositório):

    python consolidacao/auditoria.py --indice ids.txt

`ids.txt` é a saída de `rg -m1 --no-heading -g '*.md' '^id: ' data/portugal data/regional`
(ficheiro:id); sem ele, o índice faz-se com `Acervo.index()`, que usa vários processos.
Grava `consolidacao/auditoria/retificacoes.jsonl`, `vigencia.jsonl` e `resumo.json`.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from texto import RAIZ, corpo, front_matter, normalizar, publicado, sem_ligacoes  # noqa: E402


PASTA = RAIZ / "consolidacao" / "auditoria"
HOJE = date.today().isoformat()
BOLONHA = "2006-03-24"  # DL 74/2006, de 24 de março: o regime anterior dos graus acaba com a adequação


# ---------------------------------------------------------------------------------------------
# Retificações
# ---------------------------------------------------------------------------------------------

_ONDE = re.compile(r"onde se l[êe]", re.I)
_DEVE = re.compile(r"dever?[áa]? ler-se|deve ler-se|leia-se|deve passar a ler-se", re.I)
_RETICENCIAS = re.compile(r"^(?:\s*(?:\.{3}|…|\[\s*\.{3}\s*\]|\(\s*\.{3}\s*\))\s*)+|(?:\s*(?:\.{3}|…|\[\s*\.{3}\s*\]|\(\s*\.{3}\s*\))\s*)+$")
_METADADOS = re.compile(r"\b(?:sum[áa]rio|t[íi]tulo do diploma|no t[íi]tulo|na data|data d[ao] (?:diploma|decreto|portaria|publica)|assinatura|[íi]ndice)\b", re.I)
_IMAGEM = re.compile(r"\(ver (?:documento|quadro|mapa|imagem)[^)]*original\)|de novo (?:à|a) sua publica|nova(?:mente)? publica|se republica|se publica (?:de novo|novamente)|republica[çc][ãa]o|se procede (?:de novo )?(?:à|a) (?:sua )?(?:nova )?publica|promove a sua publica|seguir se publica", re.I)


def _aspas(texto: str, inicio: int) -> tuple[str, int] | None:
    """O texto entre o próximo «…» equilibrado a partir de `inicio`, e a posição a seguir."""
    abre = texto.find("«", inicio)
    if abre == -1:
        return None
    nivel = 0
    for i in range(abre, len(texto)):
        if texto[i] == "«":
            nivel += 1
        elif texto[i] == "»":
            nivel -= 1
            if nivel == 0:
                return texto[abre + 1 : i], i + 1
    return None


def limpar(trecho: str) -> str:
    """Um trecho de retificação para procurar no texto: sem reticências nas pontas e normalizado."""
    trecho = normalizar(sem_ligacoes(trecho))
    anterior = None
    while anterior != trecho:
        anterior, trecho = trecho, _RETICENCIAS.sub("", trecho).strip()
    return trecho


def pares(texto: str) -> list[dict]:
    """Os pares «onde se lê «X» deve ler-se «Y»» de uma retificação, com o localizador que os precede.

    Aceita as aspas no mesmo parágrafo ou em parágrafos seguidos. Um par sem aspas («onde se lê:
    X, deve ler-se: Y») não se lê: fica de fora e conta como `sem_aspas`.
    """
    plano = normalizar(sem_ligacoes(texto))
    resultado = []
    fim_anterior = 0
    for m in _ONDE.finditer(plano):
        if m.start() < fim_anterior:
            continue
        deve = _DEVE.search(plano, m.end())
        antes = _aspas(plano, m.end())
        if deve is None or antes is None or antes[1] > deve.start() + 1:
            resultado.append({"sem_aspas": True, "localizador": plano[max(fim_anterior, m.start() - 200) : m.start()]})
            fim_anterior = m.end()
            continue
        depois = _aspas(plano, deve.end())
        proximo = _ONDE.search(plano, deve.end())
        if depois is None or (proximo and depois[1] > proximo.start()):
            resultado.append({"sem_aspas": True, "localizador": plano[max(fim_anterior, m.start() - 200) : m.start()]})
            fim_anterior = deve.end()
            continue
        resultado.append(
            {
                "localizador": plano[max(fim_anterior, m.start() - 200) : m.start()],
                "antes": limpar(antes[0]),
                "depois": limpar(depois[0]),
            }
        )
        fim_anterior = depois[1]
    return resultado


def chave(texto: str) -> str:
    """O texto sem pontuação nem maiúsculas, para a correspondência aproximada («artigo 50» e «artigo 50.º»)."""
    return " ".join(re.findall(r"\w+", texto.casefold()))


def estado_par(par: dict, em_vigor: str, original: str, metadados: str) -> str:
    """Estado de um par no texto em vigor (ver o início do ficheiro); `aprox` quando só se encontra
    uma vez sem pontuação nem maiúsculas."""
    if par.get("sem_aspas"):
        return "sem_aspas"
    antes, depois = par["antes"], par["depois"]
    if not antes or not chave(antes):
        return "ausente"
    n = em_vigor.count(antes)
    if n == 1:
        return "unico"
    if n > 1:
        return "varios"
    # O aproximado antes do `ja`: «Artigo 1.º Critérios» → «1.º Critérios» tem o depois dentro do antes.
    k = f" {chave(antes)} "
    n = f" {chave(em_vigor)} ".count(k)
    if n == 1:
        return "aprox"
    if n > 1:
        return "varios"
    if depois and chave(depois) and f" {chave(depois)} " in f" {chave(em_vigor)} ":
        return "ja"
    if _METADADOS.search(par["localizador"][-120:]) or k in f" {chave(metadados)} ":
        return "metadados"
    if k in f" {chave(original)} ":
        return "substituido"
    return "ausente"


def menciona(texto: str, titulo: str) -> bool | None:
    """O texto da retificação menciona o número do original («317/75», «10 910/2009», «44513»).

    Só pelo número, porque o DRE chama «Decreto» a decretos-leis e «Resolução» a resoluções do
    Conselho de Ministros. None quando o título não tem número.
    """
    m = re.search(r"n\.?\s*[º°o]\s*(\d[\d\s]*\d|\d)((?:-[A-Z]+\d*)?)(?:/(\d{2,4}))?", titulo)
    if not m:
        return None
    numero = r"\s?".join(re.findall(r"\d", m.group(1)))
    sufixo = re.escape(m.group(2)).replace("\\-", "\\s?-\\s?")
    if m.group(3):
        ano = m.group(3)[-2:]
        resto = rf"/(?:19|20)?{ano}"
    else:
        resto = r"(?:/\d{2,4})?"
    return re.search(rf"(?<![\d/.]){numero}{sufixo}{resto}(?![\d])", texto) is not None


def classificar_retificacao(texto_ret: str, titulo_original: str, em_vigor: str, original: str, metadados: str) -> dict:
    """Classe de uma retificação por aplicar (ver o início do ficheiro) e os estados dos pares.

    `em_vigor` e `original` são os corpos do consolidado e do original publicado; `metadados` é o
    título e o sumário do original. Todos já normalizados com `normalizar(sem_ligacoes(…))`.
    """
    plano = normalizar(sem_ligacoes(texto_ret))
    if menciona(plano, titulo_original) is False:
        return {"classe": "outro_diploma", "estados": []}
    lista = pares(texto_ret)
    estados = [estado_par(p, em_vigor, original, metadados) for p in lista]
    if not lista:
        classe = "imagem_ou_republicacao" if _IMAGEM.search(plano) else "sem_pares"
    elif all(e in ("unico", "ja", "metadados") for e in estados) and "unico" in estados:
        classe = "por_regra"
    elif all(e in ("unico", "aprox", "ja", "metadados") for e in estados) and "aprox" in estados:
        classe = "por_regra_aprox"
    elif all(e == "ja" for e in estados):
        classe = "ja_no_texto"
    elif all(e == "metadados" for e in estados):
        classe = "so_metadados"
    elif all(e in ("substituido", "ja", "metadados") for e in estados):
        classe = "substituida"
    else:
        classe = "llm"
    return {"classe": classe, "estados": estados, "pares": lista}


def faixa_data(data_ret: str | None, publicacao: str, consolidacao: str) -> str:
    if not data_ret or data_ret == "None":
        return "sem_data"
    if data_ret < publicacao:
        return "antes_do_original"
    if data_ret <= consolidacao:
        return "entre_original_e_consolidacao"
    return "depois_da_consolidacao"


# ---------------------------------------------------------------------------------------------
# Vigência
# ---------------------------------------------------------------------------------------------

_MESES = "janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"
_DATA = re.compile(rf"\b\d{{1,2}}(?:\.º)? de (?:{_MESES}) de \d{{4}}", re.I)
_NUMERO = re.compile(r"\b(?:n\.?\s*[º°o]s?\.?\s*)?\d+(?:-[A-Z]+)?/\d{2,4}(?:/[A-Z])?\b|\b\d{2,4}/\d+/(?:CE|CEE|UE)\b", re.I)

# Uma concessão ou zona com nome ou lugar; as regras gerais (taxas, sinais, épocas) ficam `incerta`.
CACA_ALTA = re.compile(
    r"regime cineg[ée]tico especial|sujeit[ao]s? ao regime cineg[ée]tico|"
    r"zonas? de ca[çc]a (?:associativa|tur[íi]stica|nacional|municipal|social) (?:d[aeo]s? |de )?(?-i:[A-ZÁÉÍÓÚÂÊÔ])|"
    r"(?:cria|concessiona|renova|anexa|desanexa|extingue|transfere|concede|prorroga)\w*\b[^.]{0,80}\bzonas? de ca[çc]a|"
    r"reservas? de ca[çc]a|coutadas?\b|concess[ãa]o de ca[çc]a",
    re.I,
)
CACA_GERAL = re.compile(r"\btaxas?\b|\bmontantes?\b|modelos? (?:de|para) (?:sinais|tabuletas)", re.I)
CACA = re.compile(r"\bca[çc]a\b|cineg[ée]tic", re.I)

CURSO_ALTA = re.compile(
    r"graus? de (?:mestre|licenciado|bacharel|doutor)|diplomas? de estudos superiores especializados|"
    r"cursos? (?:de |do |da )?(?:mestrado|licenciatura|bacharelato|estudos superiores especializados|p[óo]s-gradua)|"
    r"(?:mestrados?|licenciaturas?|bacharelatos?) em\b|"
    r"planos? (?:de estudos?|curricular(?:es)?) d[oa]s? (?:curso|licenciatura|mestrado|bacharelato)",
    re.I,
)
CURSO = re.compile(r"mestrado|licenciatura|bacharelato|plano de estudos|planos de estudos|plano curricular", re.I)
ENSINO_SUPERIOR = re.compile(r"universidade|instituto|escola superior|faculdade|academia|polit[ée]cnic|ensino superior|conservat[óo]rio", re.I)

ANO_ALTA = [
    re.compile(r"or[çc]amento(?: geral)?(?: do estado)?(?: da regi[ãa]o[^.]{0,30})? (?:para|de) (?:o ano de )?((?:19|20)\d\d)\b", re.I),
    re.compile(r"(?:para|durante|no|relativ[oa]s? ao) (?:o )?ano (?:de )?((?:19|20)\d\d)\b", re.I),
    re.compile(r"\bano (?:lectivo|letivo|escolar|econ[óo]mico|agr[íi]cola|civil|judicial|acad[ée]mico) (?:de )?((?:19|20)\d\d)\b", re.I),
    re.compile(r"\bcampanhas? (?:agr[íi]colas? |de comercializa[çc][ãa]o |oleícola |vin[íi]cola )?(?:de )?((?:19|20)\d\d)\b", re.I),
    re.compile(r"\b[ée]pocas? (?:venat[óo]ria |balnear |de ca[çc]a |de pesca )?(?:de )?((?:19|20)\d\d)\b", re.I),
    re.compile(r"\b(?:provas?|exames?|concursos?|candidaturas?|elei[çc][õo]es|recenseamento)\b[^.]{0,80}?\b(?:de|para|em) ((?:19|20)\d\d)\b(?![/-]\d)", re.I),
    re.compile(r"\b(?:seca|inc[êe]ndios?|cheias|intemp[ée]ries?|temporal|sismo) (?:de|em|ocorrid[oa]s? em) ((?:19|20)\d\d)\b", re.I),
    re.compile(r"\bexerc[íi]cio (?:econ[óo]mico )?de ((?:19|20)\d\d)\b", re.I),
    re.compile(r"\bpara ((?:19|20)\d\d)\b(?![/-]\d)", re.I),
]
ANO_INCERTO = re.compile(r"\b(?:de|em|até|desde) ((?:19|20)\d\d)\b|((?:19|20)\d\d)[-/]((?:19|20)?\d\d)\b", re.I)

ORG_ALTA = re.compile(
    r"lei org[âa]nica|\borg[âa]nica d|estrutura org[âa]nica|quadros? d[eo] pessoal|"
    r"estatutos? d[aoe]s? (?!deputad|oficia|militar|pessoal|magistrad|funcion|carreira|alun|trabalhador|bolseir|docente|m[ée]dic|enfermeir|jornalist|dirigente|eleit)|"
    r"regulamento (?:interno|org[âa]nico)|regulamento d[oa] (?:centro|instituto|fundo|servi[çc]o|gabinete|comiss[ãa]o|conselho|escola)|"
    r"(?:constitui[çc][ãa]o|composi[çc][ãa]o) d[ao] (?:comiss[ãa]o|conselho|grupo|j[úu]ri)",
    re.I,
)
ORG = re.compile(
    r"(?:cria|institui|reestrutura|reorganiza|remodela)\w*\b[^.]{0,40}\b(?:o|a|os|as) (?:servi[çc]os?|direc?[çc][ãa]o|instituto|gabinete|"
    r"comiss[ãa]o|fundo|centro|conselho|n[úu]cleo|junta|reparti[çc][ãa]o|secretaria|delega[çc][ãa]o|escola|museu|laborat[óo]rio)",
    re.I,
)


# À parte das quatro classes: diplomas do ultramar anteriores à descolonização.
ULTRAMAR = re.compile(r"ultramar|prov[íi]ncias? ultramarin|\b(?:Angola|Moçambique|Guiné|Timor|Cabo Verde|São Tomé|Macau|Estado da Índia)\b")


def _sem_numeros(texto: str) -> str:
    """Sem datas por extenso nem números de diplomas, para não ler «Lei n.º 3/2000» como um ano."""
    return _NUMERO.sub(" ", _DATA.sub(" ", texto))


def classe_vigencia(titulo: str, sumario: str, tipo: str, publicacao: str) -> tuple[str | None, str | None]:
    """(classe, certeza) de um consolidado; (None, None) quando não cai em nenhuma.

    As classes testam-se por ordem (caça, cursos, um só ano, orgânicas) e fica a primeira.
    `alta` quer dizer que o título e o sumário bastam para pôr o diploma na classe; não quer dizer
    que tenha deixado de vigorar, o que só a leitura do acervo mostra.
    """
    texto = f"{titulo or ''}. {sumario or ''}"
    if CACA_ALTA.search(texto) and not CACA_GERAL.search(texto):
        return "caca", "alta"
    if CACA.search(texto):
        return "caca", "incerta"
    if publicacao < BOLONHA and CURSO_ALTA.search(texto) and ENSINO_SUPERIOR.search(texto):
        return "cursos_pre_bolonha", "alta"
    if publicacao < BOLONHA and CURSO.search(texto):
        return "cursos_pre_bolonha", "incerta"
    plano = _sem_numeros(texto)
    for padrao in ANO_ALTA:
        m = padrao.search(plano)
        if m and int(m.group(1)) <= 2025:
            return "um_so_ano", "alta"
    m = ANO_INCERTO.search(plano)
    if m:
        return "um_so_ano", "incerta"
    if ORG_ALTA.search(texto):
        return "organicas", "alta"
    if ORG.search(texto):
        return "organicas", "incerta"
    return None, None


# Revogação de uma parte ou com ressalvas. O alvo («Revogado o art. 2.º», «Revogados os n.os …»,
# «relativamente à província de Moçambique») lê-se só antes de «pelo/pela», porque depois vem o
# diploma que revoga («pela Portaria n.º 207/2017, nos termos do seu art. 5.º»). As ressalvas
# («à excepção do art. 4.º», «em tudo o que o contrarie») leem-se em todo o rótulo. «Revogado o
# presente diploma» e «Revogada a concessão atribuída pelo presente» são inteiras. Na dúvida
# («sem prejuízo do disposto…»), conta como parcial.
_REVOGACAO_INTEIRA = re.compile(r"^revogad[oa]s?\b|revoga[çc][ãa]o total", re.I)
_ALVO_PARCIAL = re.compile(
    r"\b(?:o|a|os|as)\s+(?!presente\b|concess)(?:art|n\.|n[ºo]|al[íi]n|§|disposto|benef|anexo|cap|quadro|mapa|tabela|regime|dec|port|lei)|"
    r"\bart(?:igo)?s?\.?\s*\d|\bn\.?\s*[ºo]s?\.?\s*\d|al[íi]neas?|§|relativamente|respeite|todas as disposi",
    re.I,
)
# «Revogado[, a partir de …,] o/a/os/as X» em que X não é o próprio diploma nem o que ele concede.
_ALVO_ARTIGO = re.compile(
    r"^revogad[oa]s?,?\s+(?:\([^)]*\)\s*)?(?:(?:a partir|com efeitos|com produ[çc][ãa]o|de acordo)[^,]*,\s*)?"
    r"(?:o|a|os|as|n[ao]s?)\s+(?!presente\b|concess|licen)",
    re.I,
)
_RESSALVA = re.compile(
    r"exce[pç]+[ãa]o|excep[cç]+[ãa]o|à excep|salvo|excepto|exceto|na parte|em tudo|contr[áa]ri|sem preju[íi]zo|"
    r"no que (?:respeita|se refere)|parcial|progressiv",
    re.I,
)


def revogacao_inteira(rotulo: str | None) -> bool:
    """O rótulo de uma relação `repealed_by` diz que o diploma foi revogado por inteiro."""
    rotulo = html.unescape((rotulo or "").replace("\x00", "")).strip()
    rotulo = re.sub(r"^[^:]{0,80}: (?=revoga)", "", rotulo, flags=re.I)  # "Decreto-Lei n.º 42978: revogação total …"
    if not _REVOGACAO_INTEIRA.search(rotulo):
        return False
    alvo = re.split(r"\bpel[oa]s?\b|\bpelo\(a\)", rotulo, maxsplit=1)[0]
    if re.match(r"^revogad[oa] a concess", alvo, re.I):
        alvo = ""
    return not (_ALVO_ARTIGO.search(alvo) or _ALVO_PARCIAL.search(alvo) or _RESSALVA.search(rotulo))


_EXTENSO = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8,
    "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "catorze": 14, "quinze": 15, "dezasseis": 16,
    "dezassete": 17, "dezoito": 18, "dezanove": 19, "vinte": 20, "vinte e um": 21, "vinte e cinco": 25, "trinta": 30,
}
_PRAZO = re.compile(
    r"(?:per[íi]odo|prazo) de (\d+|" + "|".join(sorted(_EXTENSO, key=len, reverse=True)) + r")(?: \(\w+\))? anos", re.I
)
_RENOVAVEL = re.compile(r"renov[áa]ve(?:l|is)|renova[çc][ãa]o autom[áa]tica|automaticamente renovad", re.I)


def prazo_concessao(texto: str) -> int | None:
    """O maior prazo em anos que o texto dá («pelo período de 12 anos», «prazo de doze anos»)."""
    prazos = [int(n) if n.isdigit() else _EXTENSO[n.lower()] for n in (m.group(1) for m in _PRAZO.finditer(texto))]
    return max(prazos) if prazos else None


def fim_estimado(consolidacao: str, anos: int) -> str:
    """A data do último ato aplicado mais o prazo: o fim mais tardio possível sem outra renovação."""
    ano, resto = consolidacao[:4], consolidacao[4:]
    return f"{int(ano) + anos:04d}{resto}"


def ano_do_regime(titulo: str, sumario: str) -> int | None:
    plano = _sem_numeros(f"{titulo or ''}. {sumario or ''}")
    for padrao in ANO_ALTA:
        m = padrao.search(plano)
        if m and int(m.group(1)) <= 2025:
            return int(m.group(1))
    return None


# ---------------------------------------------------------------------------------------------
# Leitura do acervo
# ---------------------------------------------------------------------------------------------


def consolidados(raiz: Path = RAIZ):
    """Os registos consolidados pelo leis-portugal: (caminho do .md, front matter, versões)."""
    for versoes in sorted((raiz / "data").rglob("*.versoes.json")):
        dados = json.loads(versoes.read_text(encoding="utf-8"))
        if not str(dados.get("consolidated_by") or "").startswith("leis-portugal"):
            continue
        md = versoes.with_name(versoes.name[: -len(".versoes.json")] + ".md")
        yield md, front_matter(md.read_text(encoding="utf-8")), dados


def carregar_indice(ficheiro: Path | None) -> dict[str, Path]:
    if ficheiro is None:
        from leis_portugal.infrastructure.repository import Acervo

        return Acervo(RAIZ).index()
    indice = {}
    for linha in ficheiro.read_text(encoding="utf-8").splitlines():
        caminho, _, id_ = linha.partition(":id: ")
        if id_:
            indice[id_.strip().strip("'\"")] = RAIZ / caminho
    return indice


def _plano(texto: str) -> str:
    return normalizar(sem_ligacoes(texto))


def auditar(indice: dict[str, Path]) -> tuple[list[dict], list[dict], dict]:
    retificacoes, vigencia = [], []
    contas: dict[str, Counter] = {k: Counter() for k in ("retificacoes", "datas", "classes", "por_diploma", "vigencia", "provas")}
    total = 0
    for md, meta, dados in consolidados():
        total += 1
        id_ = meta["id"]
        titulo = meta.get("title") or ""
        publicacao = str(meta.get("publication_date") or "")
        consolidacao = str((meta.get("version") or {}).get("consolidation_date") or "")
        aplicados = {a["id"] for v in dados["versions"] for a in v["acts"]}
        relacoes = meta.get("relationships") or []
        alterados = {r["target"] for r in relacoes if r["type"] == "amended_by"}
        em_vigor = original = None
        por_aplicar = 0
        for r in relacoes:
            if r["type"] != "corrected_by":
                continue
            contas["retificacoes"]["corrected_by"] += 1
            if r["target"] in aplicados:
                contas["retificacoes"]["aplicadas"] += 1
                continue
            por_aplicar += 1
            contas["retificacoes"]["por_aplicar"] += 1
            if r["target"] in alterados:
                contas["retificacoes"]["por_aplicar_mas_em_amended_by"] += 1
            caminho = indice.get(r["target"])
            linha = {
                "id": id_, "titulo": titulo, "caminho": str(md.relative_to(RAIZ)), "publicacao": publicacao,
                "consolidacao": consolidacao, "retificacao": r["target"], "rotulo": (r.get("label") or "").replace("\x00", "").strip(),
            }
            if caminho is None or not caminho.exists():
                data_ret = str(r.get("date") or "") or None
                linha.update(classe="sem_registo", estados=[], data=data_ret)
            else:
                meta_ret = front_matter(caminho.read_text(encoding="utf-8"))
                data_ret = str(meta_ret.get("publication_date") or r.get("date") or "") or None
                if em_vigor is None:
                    em_vigor = _plano(corpo(md.read_text(encoding="utf-8")))
                    original = _plano(publicado(md))
                metadados = _plano(f"{titulo} {meta.get('summary') or ''}")
                texto_ret = corpo(caminho.read_text(encoding="utf-8"))
                linha.update(
                    titulo_retificacao=meta_ret.get("title"), tipo_retificacao=meta_ret.get("document_type"),
                    caminho_retificacao=str(caminho.relative_to(RAIZ)), data=data_ret,
                    **classificar_retificacao(texto_ret, titulo, em_vigor, original, metadados),
                )
            linha["faixa"] = faixa_data(linha["data"], publicacao, consolidacao)
            contas["datas"][linha["faixa"]] += 1
            contas["classes"][linha["classe"]] += 1
            retificacoes.append(linha)
        if por_aplicar:
            contas["por_diploma"]["com_retificacao_por_aplicar"] += 1
        if any(r["type"] == "corrected_by" for r in relacoes):
            contas["por_diploma"]["com_corrected_by"] += 1

        classe, certeza = classe_vigencia(titulo, meta.get("summary") or "", meta.get("document_type") or "", publicacao)
        inteiras = [r for r in relacoes if r["type"] == "repealed_by" and revogacao_inteira(r.get("label"))]
        estado = meta.get("legal_status")
        prova = "legal_status" if estado not in ("in_force", "partially_in_force") else ("repealed_by_inteira" if inteiras else None)
        extra = {}
        if classe == "caca":
            texto = _plano(corpo(md.read_text(encoding="utf-8")))
            anos = prazo_concessao(texto)
            extra = {"prazo_anos": anos, "renovavel": bool(_RENOVAVEL.search(texto))}
            if anos:
                extra["fim_estimado"] = fim_estimado(consolidacao, anos)
                if extra["fim_estimado"] < HOJE:
                    contas["provas"]["prazo_acabado:caca" + ("_renovavel" if extra["renovavel"] else "")] += 1
        elif classe == "um_so_ano":
            extra = {"ano": ano_do_regime(titulo, meta.get("summary") or "")}
        vigencia.append(
            {
                "id": id_, "titulo": titulo, "sumario": meta.get("summary"), "tipo": meta.get("document_type"),
                "publicacao": publicacao, "caminho": str(md.relative_to(RAIZ)), "classe": classe, "certeza": certeza,
                "legal_status": estado, "revogado_por": [{"alvo": r["target"], "rotulo": (r.get("label") or "").replace("\x00", "").strip()} for r in inteiras],
                "prova": prova, "consolidacao": consolidacao, **extra,
            }
        )
        if publicacao < "1976-01-01" and ULTRAMAR.search(f"{titulo}. {meta.get('summary') or ''}"):
            vigencia[-1]["ultramar"] = True
            contas["provas"][f"ultramar:{classe or 'nenhuma'}"] += 1
        contas["vigencia"][f"{classe}:{certeza}" if classe else "nenhuma"] += 1
        if prova:
            contas["provas"][f"{prova}:{classe or 'nenhuma'}"] += 1
    resumo = {"consolidados": total, **{k: dict(v.most_common()) for k, v in contas.items()}}
    return retificacoes, vigencia, resumo


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--indice", type=Path, help="saída do rg com ficheiro:id (ver o início do ficheiro)")
    args = parser.parse_args(argv)
    retificacoes, vigencia, resumo = auditar(carregar_indice(args.indice))
    PASTA.mkdir(exist_ok=True)
    for nome, linhas in (("retificacoes.jsonl", retificacoes), ("vigencia.jsonl", vigencia)):
        with (PASTA / nome).open("w", encoding="utf-8") as f:
            for linha in linhas:
                f.write(json.dumps(linha, ensure_ascii=False) + "\n")
    (PASTA / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
