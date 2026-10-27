"""Aplicação das instruções de alteração ao texto original, por regras.

Regras (todas mecânicas; o que não cabe nelas falha com o motivo e fica para o LLM):

- **substituição integral**: a nova redação de um artigo, sem "[...]", substitui o corpo e a
  epígrafe do artigo;
- **substituição com "[...]"**: a nova redação junta-se ao original número a número e alínea a
  alínea; cada "[...]" (ou "...", "(...)") fica com o texto original dessa unidade. Falha se o
  "[...]" não tiver correspondência no original ou se a nova redação omitir números que o
  original tem;
- **substituição parcial**: "o n.º 2 do artigo 5.º passa a ter a seguinte redação" substitui
  só essa unidade;
- **aditamento**: o artigo novo entra a seguir ao último artigo de número menor da mesma parte
  (um número ou alínea nova, a seguir ao anterior);
- **revogação**: o corpo do artigo passa a "(Revogado.)" (mantém o título e a epígrafe, como
  nas consolidações do DRE); um número fica "N - (Revogado.)", uma alínea "a) (Revogada.)";
- **retificação**: "onde se lê «X» deve ler-se «Y»" troca X por Y no artigo indicado, só se X
  aparecer lá uma única vez.

Cada artigo alterado leva uma nota no fim, no formato das consolidações do acervo
("> Alterado pelo/a Artigo 2.º do/a [Decreto-Lei …](…)").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from alteracoes import Alvo, Instrucao, e_placeholder
from texto import Artigo, Corpo, numero_artigo, sem_ligacoes


class Falha(Exception):
    """Uma instrução que as regras não sabem aplicar com segurança."""


@dataclass
class Registo:
    artigo: str
    operacao: str
    regra: str
    antes: str
    depois: str
    excerto: str
    artigo_alterador: str
    metodo: str = "regra"
    aviso: str = ""
    unidade: list[str] = field(default_factory=list)  # nas alterações parciais: o número ou a alínea alvo


@dataclass
class Resultado:
    registos: list[Registo] = field(default_factory=list)
    falhas: list[dict] = field(default_factory=list)
    tocados: set[str] = field(default_factory=set)  # chaves dos artigos alterados ou aditados


# --- Unidades de um artigo: números, alíneas, subalíneas ------------------------------------

_NUMERO = re.compile(r"^(\d+(?:\.\d+)*)\s*(?:\.?\s*º)?\s*[-–—]\s*(.*)$", re.S)
_ALINEA = re.compile(r"^([a-z]{1,2})\)\s*(.*)$", re.S)
_ROMANA = re.compile(r"^([ivx]+)\)\s*(.*)$", re.S)
_TITULOS_ESTRUTURA = re.compile(r"^(?:CAP[ÍI]TULO|SEC[CÇ][ÃA]O|SUBSEC[CÇ][ÃA]O|T[ÍI]TULO|PARTE|LIVRO|DIVIS[ÃA]O)\b", re.I)


@dataclass
class Unidade:
    chave: tuple[str, ...]
    paragrafos: list[str]
    conteudo: str  # o primeiro parágrafo sem o rótulo ("1 - ", "a) ")


def unidades(paragrafos: list[str]) -> list[Unidade]:
    resultado: list[Unidade] = []
    numero, alinea = "", ""
    for p in paragrafos:
        m = _NUMERO.match(p)
        if m:
            numero, alinea = m.group(1), ""
            resultado.append(Unidade((numero,), [p], m.group(2)))
            continue
        romana = _ROMANA.match(p)
        if romana and alinea and not (romana.group(1) == "i" and alinea == "h") and not (romana.group(1) == "v" and alinea == "u") and not (romana.group(1) == "x" and alinea == "v"):
            resultado.append(Unidade((numero, alinea, romana.group(1)), [p], romana.group(2)))
            continue
        m = _ALINEA.match(p)
        if m:
            alinea = m.group(1)
            resultado.append(Unidade((numero, alinea), [p], m.group(2)))
            continue
        if resultado:
            resultado[-1].paragrafos.append(p)
        else:
            resultado.append(Unidade(("",), [p], p))
    return resultado


def _descende(chave: tuple[str, ...], de: tuple[str, ...]) -> bool:
    return len(chave) > len(de) and chave[: len(de)] == de


def _paragrafos(texto: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]


_ANTERIOR = re.compile(
    r"^[\[(]\s*anterior\s+(?:n\.?\s*[ºo]\s*(\d+(?:\.\d+)*)|al[íi]nea\s+([a-z]{1,2})\)?)\s*\.?\s*[\])]\s*[.;:]?$", re.I
)


def _anterior(unidade: Unidade) -> tuple[str, ...] | None:
    """A unidade do original que a marca de renumeração "[Anterior n.º 2]." traz para aqui."""
    m = _ANTERIOR.match(unidade.conteudo.strip())
    if not m:
        return None
    if m.group(1):
        return (m.group(1),)
    return (unidade.chave[0], m.group(2)) if len(unidade.chave) >= 2 else None


def _rerrotular(paragrafo: str, chave: tuple[str, ...]) -> str:
    """O primeiro parágrafo de uma unidade com o rótulo novo ("2 - …" passa a "4 - …")."""
    if len(chave) == 1:
        return _NUMERO.sub(lambda m: f"{chave[0]} - {m.group(2)}", paragrafo, count=1)
    return _ALINEA.sub(lambda m: f"{chave[-1]}) {m.group(2)}", paragrafo, count=1)


def fundir(original: list[str], nova: list[str]) -> tuple[list[str], bool]:
    """Junta a nova redação (com "[...]" e "[Anterior n.º 2]") ao texto original.

    Devolve (parágrafos, se houve [...] ou renumeração)."""
    novas = unidades(nova)
    if not any(e_placeholder(u.conteudo) or _anterior(u) for u in novas):
        return nova, False
    antigas = unidades(original)
    indice: dict[tuple[str, ...], Unidade] = {}
    for u in antigas:
        if u.chave in indice:
            raise Falha(f"unidade repetida no original ({'/'.join(u.chave)}): não se sabe a que corresponde o [...]")
        indice[u.chave] = u
    chaves_novas = [u.chave for u in novas]
    if len(set(chaves_novas)) != len(chaves_novas):
        raise Falha("unidade repetida na nova redação")
    resultado: list[str] = []
    cobertas = set(chaves_novas)
    for u in novas:
        origem = _anterior(u)
        if origem is None and not e_placeholder(u.conteudo):
            resultado.extend(u.paragrafos)
            continue
        origem = origem or u.chave
        if origem not in indice:
            raise Falha(f"[...] sem correspondência no original ({'/'.join(origem)})")
        if len(u.paragrafos) > 1:
            raise Falha(f"[...] seguido de texto na mesma unidade ({'/'.join(u.chave)})")
        cobertas.add(origem)
        primeiro, *resto = indice[origem].paragrafos
        resultado.append(_rerrotular(primeiro, u.chave) if origem != u.chave else primeiro)
        resultado.extend(resto)
        if not any(_descende(c, u.chave) for c in chaves_novas):
            resultado.extend(p for a in antigas if _descende(a.chave, origem) for p in a.paragrafos)
    omitidas = [
        a.chave for a in antigas
        if a.chave not in cobertas
        and not any(_descende(a.chave, c) for c in cobertas if c in indice)
        and len(a.chave) == 1
    ]
    if omitidas:
        raise Falha(f"a nova redação omite unidades do original: {', '.join('/'.join(c) for c in omitidas)}")
    return resultado, True


# --- Artigos da citação ---------------------------------------------------------------------

_CABECALHO = re.compile(
    r"^(?:#{6}\s*)?(?:Artigo|ARTIGO|Art\.?)\s+(\d+\s*\.?\s*[º°o]?(?:\s*-\s*[A-Z]{1,2})?)\.?\s*(?:[-–—]\s*(.*))?$"
)


@dataclass
class ArtigoCitado:
    numero: str
    epigrafe: str | None  # None: sem epígrafe; "" : epígrafe "[...]" (fica a original)
    paragrafos: list[str]


def artigos_citados(citacao: str) -> list[ArtigoCitado]:
    resultado: list[ArtigoCitado] = []
    paragrafos = _paragrafos(citacao)
    i = 0
    while i < len(paragrafos):
        p = paragrafos[i]
        m = _CABECALHO.match(p)
        if not m:
            if _TITULOS_ESTRUTURA.match(p):
                raise Falha("a citação traz títulos de capítulo ou secção")
            if not resultado:
                raise Falha("texto na citação antes do primeiro artigo")
            resultado[-1].paragrafos.append(p)
            i += 1
            continue
        artigo = ArtigoCitado(numero_artigo(m.group(1)), None, [])
        resto = (m.group(2) or "").strip()
        if resto and (_NUMERO.match(resto) or _ALINEA.match(resto) or len(resto) > 150):
            artigo.paragrafos.append(resto)
        elif resto:
            artigo.epigrafe = "" if e_placeholder(resto) else resto
        elif i + 1 < len(paragrafos):
            seguinte = paragrafos[i + 1]
            if e_placeholder(seguinte):
                artigo.epigrafe = ""
                i += 1
            elif (
                not _NUMERO.match(seguinte) and not _ALINEA.match(seguinte) and not _CABECALHO.match(seguinte)
                and len(seguinte) <= 150 and not seguinte.rstrip().endswith((".", ";", ":"))
            ):
                artigo.epigrafe = seguinte
                i += 1
        resultado.append(artigo)
        i += 1
    return resultado


# --- Escrita dos artigos --------------------------------------------------------------------


def _ordem(numero: str) -> tuple[int, str]:
    m = re.match(r"^(\d+)\.º(?:-([A-Z]+))?$", numero)
    return (int(m.group(1)), m.group(2) or "") if m else (10**9, numero)


def _bloco(numero: str, epigrafe: str, paragrafos: list[str], notas: list[str], fim: list[str]) -> list[str]:
    linhas = [f"###### Artigo {numero}" + (f" — {epigrafe}" if epigrafe else ""), ""]
    for p in paragrafos:
        linhas += [p, ""]
    for n in notas:
        linhas += [n, ""]
    while linhas and linhas[-1] == "":
        linhas.pop()
    return linhas + (fim or [""])


def _fim(artigo: Artigo) -> list[str]:
    """As linhas vazias no fim do bloco, para o artigo seguinte ficar igual."""
    n = 0
    for linha in reversed(artigo.linhas):
        if linha.strip():
            break
        n += 1
    return [""] * n


def _reescrever(artigo: Artigo, epigrafe: str, paragrafos: list[str], nota: str) -> None:
    artigo.epigrafe = epigrafe
    artigo.linhas = _bloco(artigo.numero, epigrafe, paragrafos, artigo.notas + [nota], _fim(artigo))


def _inserir(corpo: Corpo, novo: Artigo) -> None:
    mesma_parte = [i for i, s in enumerate(corpo.segmentos) if isinstance(s, Artigo) and s.parte == novo.parte]
    if not mesma_parte:
        raise Falha("parte do original sem artigos onde aditar")
    if corpo.artigo(novo.parte, novo.numero) is not None:
        raise Falha(f"o artigo aditado {novo.numero} já existe no original")
    anteriores = [i for i in mesma_parte if _ordem(corpo.segmentos[i].numero) < _ordem(novo.numero)]
    if not anteriores:
        raise Falha(f"não há artigo anterior ao {novo.numero} onde o aditar")
    depois = anteriores[-1]
    if depois != mesma_parte[-1] and _ordem(corpo.segmentos[mesma_parte[mesma_parte.index(depois) + 1]].numero) < _ordem(novo.numero):
        raise Falha("artigos do original fora de ordem")
    anterior = corpo.segmentos[depois]
    novo.linhas = novo.linhas[:-1] + _fim(anterior) if _fim(anterior) else novo.linhas
    corpo.segmentos.insert(depois + 1, novo)


# --- Aplicação ------------------------------------------------------------------------------


@dataclass
class Fonte:
    """O diploma que altera, para as notas."""

    titulo: str
    url: str
    data: str


def _nota(acao: str, instrucao: Instrucao, fonte: Fonte) -> str:
    artigo = instrucao.artigo_alterador.split("::")[-1]
    origem = f"Artigo {artigo} do/a " if artigo else ""
    ligacao = f"[{fonte.titulo}]({fonte.url})" if fonte.url else fonte.titulo
    return f"> {acao} pelo/a {origem}{ligacao}, publicado em {fonte.data}."


def aplicar(corpo: Corpo, instrucoes: list[Instrucao], fonte: Fonte) -> Resultado:
    resultado = Resultado()
    for instrucao in instrucoes:
        try:
            {
                "substituir": _substituir,
                "aditar": _substituir,
                "revogar": _revogar,
                "retificar": _retificar,
            }[instrucao.tipo](corpo, instrucao, fonte, resultado)
        except Falha as erro:
            resultado.falhas.append({
                "tipo": instrucao.tipo,
                "alvos": [str(a) for a in instrucao.alvos],
                "motivo": str(erro),
                "excerto": instrucao.excerto,
                "artigo_alterador": instrucao.artigo_alterador,
            })
    return resultado


def _registar(resultado: Resultado, artigo: Artigo, operacao: str, regra: str, antes: str, instrucao: Instrucao,
              unidade: tuple[str, ...] = ()) -> None:
    resultado.registos.append(Registo(
        artigo.chave, operacao, regra, antes, "\n".join(artigo.linhas).strip(), instrucao.excerto,
        instrucao.artigo_alterador, aviso=instrucao.aviso, unidade=list(unidade),
    ))
    resultado.tocados.add(artigo.chave)


def _substituir(corpo: Corpo, instrucao: Instrucao, fonte: Fonte, resultado: Resultado) -> None:
    alvo = instrucao.alvos[0]
    if alvo.artigo is None:
        citados = artigos_citados(instrucao.citacao)
        if not citados:
            raise Falha("citação sem artigos")
        pendentes: list[tuple[ArtigoCitado, Artigo | None]] = []
        for citado in citados:
            existente = corpo.artigo(alvo.parte, citado.numero)
            if existente is None and instrucao.tipo == "substituir":
                raise Falha(f"o artigo {citado.numero} a substituir não existe no original")
            if existente is not None and instrucao.tipo == "aditar":
                raise Falha(f"o artigo aditado {citado.numero} já existe no original")
            pendentes.append((citado, existente))
        for citado, existente in pendentes:
            if existente is None:
                if any(e_placeholder(u.conteudo) for u in unidades(citado.paragrafos)) or citado.epigrafe == "":
                    raise Falha(f"artigo aditado {citado.numero} com [...]")
                novo = Artigo(alvo.parte, citado.numero, citado.epigrafe or "", [])
                novo.linhas = _bloco(novo.numero, novo.epigrafe, citado.paragrafos, [_nota("Aditado", instrucao, fonte)], [""])
                _inserir(corpo, novo)
                _registar(resultado, novo, "aditar", "aditamento de artigo", "", instrucao)
                continue
            antes = "\n".join(existente.linhas).strip()
            paragrafos, fundido = fundir(_paragrafos(existente.texto), citado.paragrafos)
            if citado.epigrafe == "":
                epigrafe = existente.epigrafe
            elif citado.epigrafe is None:
                if existente.epigrafe and fundido:
                    epigrafe = existente.epigrafe
                elif existente.epigrafe:
                    raise Falha(f"a nova redação do artigo {citado.numero} não traz epígrafe e o original tem")
                else:
                    epigrafe = ""
            else:
                epigrafe = citado.epigrafe
            _reescrever(existente, epigrafe, paragrafos, _nota("Alterado", instrucao, fonte))
            regra = "substituição com [...]" if fundido else "substituição integral"
            _registar(resultado, existente, "substituir", regra, antes, instrucao)
        return

    # Só um número ou uma alínea.
    if len(instrucao.alvos) != 1:
        raise Falha("nova redação parcial com vários alvos")
    artigo = corpo.artigo(alvo.parte, alvo.artigo)
    if artigo is None:
        raise Falha(f"o artigo {alvo.artigo} não existe no original")
    chave = _chave(alvo)
    antigas = unidades(_paragrafos(artigo.texto))
    novas = _paragrafos(instrucao.citacao)
    primeira = unidades(novas)[0].chave if novas else ()
    if alvo.alinea and primeira == ("", alvo.alinea):
        primeira = chave  # a citação da alínea não repete o número
    elif primeira == ("",) and len(novas) == 1:
        # A citação só traz o texto, sem o rótulo: "«O Centro Gráfico é coordenado …»".
        novas = [f"{alvo.alinea}) {novas[0]}" if alvo.alinea else f"{alvo.numero} - {novas[0]}"]
        primeira = chave
    if primeira != chave:
        raise Falha(f"a citação começa por {'/'.join(primeira)} e a instrução fala de {'/'.join(chave)}")
    antes = "\n".join(artigo.linhas).strip()
    if any(u.chave == chave for u in antigas):
        if instrucao.tipo == "aditar":
            raise Falha(f"a unidade aditada {'/'.join(chave)} já existe")
        sub_antigo = [p for u in antigas if u.chave == chave or _descende(u.chave, chave) for p in u.paragrafos]
        sub_novo, _ = fundir(sub_antigo, novas)
        paragrafos, feito = [], False
        for u in antigas:
            if u.chave == chave or _descende(u.chave, chave):
                if not feito:
                    paragrafos.extend(sub_novo)
                    feito = True
                continue
            paragrafos.extend(u.paragrafos)
        regra, operacao = "substituição parcial", "substituir"
    else:
        if any(e_placeholder(u.conteudo) for u in unidades(novas)):
            raise Falha("unidade aditada com [...]")
        irmas = [i for i, u in enumerate(antigas) if len(u.chave) == len(chave) and u.chave[:-1] == chave[:-1]]
        anteriores = [i for i in irmas if _menor(antigas[i].chave[-1], chave[-1])]
        if not anteriores:
            raise Falha(f"não há unidade anterior a {'/'.join(chave)} onde a aditar")
        fim = anteriores[-1]
        while fim + 1 < len(antigas) and _descende(antigas[fim + 1].chave, antigas[anteriores[-1]].chave):
            fim += 1
        if fim + 1 < len(antigas) and len(antigas[fim + 1].chave) == len(chave) and not _menor(chave[-1], antigas[fim + 1].chave[-1]):
            raise Falha("unidades do original fora de ordem")
        paragrafos = [p for u in antigas[: fim + 1] for p in u.paragrafos] + novas + [p for u in antigas[fim + 1 :] for p in u.paragrafos]
        regra, operacao = "aditamento de número ou alínea", "aditar"
    _reescrever(artigo, artigo.epigrafe, paragrafos, _nota("Alterado", instrucao, fonte))
    _registar(resultado, artigo, operacao, regra, antes, instrucao, chave)


def _chave(alvo: Alvo) -> tuple[str, ...]:
    if alvo.alinea:
        return (alvo.numero or "", alvo.alinea)
    return (alvo.numero,) if alvo.numero else ("",)


def _menor(a: str, b: str) -> bool:
    if a.replace(".", "").isdigit() and b.replace(".", "").isdigit():
        return [int(x) for x in a.split(".")] < [int(x) for x in b.split(".")]
    return (len(a), a) < (len(b), b)


def _revogar(corpo: Corpo, instrucao: Instrucao, fonte: Fonte, resultado: Resultado) -> None:
    # Valida tudo antes de mexer, para não deixar a instrução meio aplicada.
    planos = []
    for alvo in instrucao.alvos:
        artigo = corpo.artigo(alvo.parte, alvo.artigo)
        if artigo is None:
            raise Falha(f"o artigo {alvo.artigo} a revogar não existe no original")
        if alvo.numero is None and alvo.alinea is None:
            planos.append((alvo, artigo, None))
            continue
        chave = _chave(alvo)
        antigas = unidades(_paragrafos(artigo.texto))
        if sum(u.chave == chave for u in antigas) != 1:
            raise Falha(f"{alvo} não existe (ou repete-se) no original")
        planos.append((alvo, artigo, chave))
    for alvo, artigo, chave in planos:
        antes = "\n".join(artigo.linhas).strip()
        if chave is None:
            _reescrever(artigo, artigo.epigrafe, ["(Revogado.)"], _nota("Revogado", instrucao, fonte))
            _registar(resultado, artigo, "revogar", "revogação de artigo", antes, instrucao)
            continue
        paragrafos = []
        for u in unidades(_paragrafos(artigo.texto)):
            if u.chave == chave:
                paragrafos.append(f"{chave[-1]} - (Revogado.)" if len(chave) == 1 else f"{chave[-1]}) (Revogada.)")
            elif not _descende(u.chave, chave):
                paragrafos.extend(u.paragrafos)
        _reescrever(artigo, artigo.epigrafe, paragrafos, _nota("Revogado", instrucao, fonte))
        _registar(resultado, artigo, "revogar", "revogação de número ou alínea", antes, instrucao, chave)


def _retificar(corpo: Corpo, instrucao: Instrucao, fonte: Fonte, resultado: Resultado) -> None:
    """Troca o que se lê pelo que deve ler-se, no artigo (e no número ou alínea) indicado.

    A procura é feita no texto sem ligações; o parágrafo retificado perde as ligações."""
    alvo = instrucao.alvos[0]
    candidatos = [corpo.artigo(alvo.parte, alvo.artigo)] if alvo.artigo else corpo.artigos
    candidatos = [a for a in candidatos if a is not None]
    epigrafe = bool(re.search(r"ep[íi]grafe[^«\"]*onde se l", instrucao.excerto, re.I))
    achados = []
    for artigo in candidatos:
        if epigrafe:
            achados += [(artigo, None)] * sem_ligacoes(artigo.epigrafe).count(instrucao.antes)
            continue
        chave = _chave(alvo) if alvo.numero or alvo.alinea else None
        for i, u in enumerate(unidades(_paragrafos(artigo.texto))):
            if chave and not (u.chave == chave or _descende(u.chave, chave)):
                continue
            for j, p in enumerate(u.paragrafos):
                plano = sem_ligacoes(p)
                if instrucao.antes in instrucao.depois and plano.count(instrucao.depois) == plano.count(instrucao.antes) > 0:
                    raise Falha("o texto do acervo já tem o que deve ler-se")
                achados += [(artigo, (i, j))] * plano.count(instrucao.antes)
    if not instrucao.antes or len(achados) != 1:
        raise Falha("o texto a retificar não aparece uma única vez no original")
    artigo, onde = achados[0]
    antes = "\n".join(artigo.linhas).strip()
    if onde is None:
        nova_epigrafe = sem_ligacoes(artigo.epigrafe).replace(instrucao.antes, instrucao.depois)
        _reescrever(artigo, nova_epigrafe, _paragrafos(artigo.texto), _nota("Retificado", instrucao, fonte))
    else:
        lista = unidades(_paragrafos(artigo.texto))
        u = lista[onde[0]]
        u.paragrafos[onde[1]] = sem_ligacoes(u.paragrafos[onde[1]]).replace(instrucao.antes, instrucao.depois)
        _reescrever(artigo, artigo.epigrafe, [p for x in lista for p in x.paragrafos], _nota("Retificado", instrucao, fonte))
    _registar(resultado, artigo, "retificar", "retificação", antes, instrucao)
