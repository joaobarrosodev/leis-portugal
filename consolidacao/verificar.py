"""Verificação automática de um diploma consolidado pelo piloto.

Três verificações, independentes do código que aplicou as alterações:

1. **Letra a letra.** Cada parágrafo de um artigo alterado vem, letra a letra, do diploma que
   altera ou do próprio artigo original (o "[...]"); nas substituições integrais e nos
   aditamentos, o corpo inteiro do artigo está seguido no diploma que altera. As únicas
   exceções são as marcas de revogação ("(Revogado.)") e as notas no fim do artigo.
2. **O resto não muda.** Lidos com o parser de `avaliacao/comum.py` (outro parser), os artigos
   que não foram alterados têm o mesmo texto e a mesma epígrafe no original e no consolidado,
   e o texto fora dos artigos é igual.
3. **Nada fica por aplicar.** Nenhum parágrafo do diploma que altera menciona o original com um
   verbo de alteração sem ter dado uma instrução aplicada; e os artigos que o DRE dá como
   alterados no rótulo da relação ("Altera Artigo 5.º") foram alterados.
"""

from __future__ import annotations

import difflib
import re
import sys
from collections import Counter

from alteracoes import _ONDE, Leitura, e_placeholder, paragrafos
from aplicar import Resultado, _paragrafos, unidades
from texto import RAIZ, Corpo, sem_abreviaturas, dividir, normalizar, numero_artigo, padrao_diploma, sem_ligacoes

sys.path.insert(0, str(RAIZ / "avaliacao"))
import comum  # noqa: E402  (só leitura: o parser de artigos da avaliação)

_REVOGADO = re.compile(r"^(?:[\w.]+(?:\)| -) )?\(Revogad[oa]\.\)$")
_VERBO_LARGO = re.compile(r"alter|adit|revog|reda[cç]|substitu|elimin|renumer|acrescent|onde se l", re.I)
_OBJETO = re.compile(r"procede(?:-se)? à .{0,40}altera[cç][ãa]o|altera(?:ção)? (?:o|a|ao|à) |objeto", re.I)
_MARCA = re.compile(r"\[\s*(?:\.\s*){3}\]|\[…\]|[\[(]\s*anterior\b|(?:^|\s)(?:\.\s*){3,}\s*$", re.I)
_DE_OUTRO = re.compile(r"(?:alterad[oa]s?|reda[cç]+[ãa]o (?:que lhe (?:foi|é) )?dada|republicad[oa]s?|introduzid[oa]s?|altera[cç](?:ão|ões) (?:que lhe (?:foram|foi) )?introduzidas?) pel[oa]s?[^.;]*$", re.I)
_ROTULO = re.compile(r"(Altera|Adita|Revoga)\s+Artigo\s+(\S+)", re.I)


def _plano(texto: str) -> str:
    return normalizar(sem_ligacoes(texto).replace("«", " ").replace("»", " "))


def verificar(original: Corpo, consolidado: Corpo, alterador: str, titulo: str, leitura: Leitura,
              resultado: Resultado, rotulos: list[str]) -> list[str]:
    problemas: list[str] = []
    fonte = _plano(alterador)

    # 1. Letra a letra.
    for registo in resultado.registos:
        artigo = next((a for a in consolidado.artigos if a.chave == registo.artigo), None)
        if artigo is None:
            problemas.append(f"{registo.artigo}: artigo alterado não está no consolidado")
            continue
        anterior = next((a for a in original.artigos if a.chave == registo.artigo), None)
        texto_antes = _plano(anterior.texto) if anterior else ""
        corpo = _paragrafos(artigo.texto)
        for p in corpo:
            if _REVOGADO.match(p):
                continue
            plano = _plano(p)
            sem_rotulo = _plano(re.sub(r"^(?:\d+(?:\.\d+)*\s*-|[a-z]{1,2}\))\s+", "", p))
            if registo.regra == "retificação" and any(
                d and d in p and _plano(p.replace(d, a)) in texto_antes for a, d in _pares_retificacao(registo.excerto)
            ):
                continue  # o parágrafo original com o que se lê trocado pelo que deve ler-se
            if plano not in fonte and plano not in texto_antes and not (registo.regra == "substituição parcial" and sem_rotulo in fonte):
                problemas.append(f"{registo.artigo}: parágrafo que não está nem no alterador nem no original: {p[:80]}")
        if registo.regra in ("substituição integral", "aditamento de artigo") and _plano("\n\n".join(corpo)) not in fonte:
            problemas.append(f"{registo.artigo}: a nova redação não está seguida, letra a letra, no alterador")
        if artigo.epigrafe and _plano(artigo.epigrafe) not in fonte and (not anterior or artigo.epigrafe != anterior.epigrafe):
            problemas.append(f"{registo.artigo}: epígrafe que não está no alterador nem no original")
        if any(e_placeholder(p) or _MARCA.search(p) for p in corpo):
            problemas.append(f"{registo.artigo}: ficou uma marca editorial ([...], [Anterior …]) no texto")

    # 1b. Nas alterações parciais, o resto do artigo não muda.
    por_artigo: dict[str, list] = {}
    for registo in resultado.registos:
        por_artigo.setdefault(registo.artigo, []).append(registo)
    for chave, registos in por_artigo.items():
        if any(not r.unidade for r in registos):
            continue  # o artigo também foi substituído por inteiro
        alvos = [tuple(r.unidade) for r in registos]

        def fora(texto: str) -> list:
            return [
                (u.chave, _plano(" ".join(u.paragrafos))) for u in unidades(_paragrafos(texto))
                if not any(u.chave[: len(a)] == a for a in alvos)
            ]

        antes_artigo = next((a for a in original.artigos if a.chave == chave), None)
        depois_artigo = next((a for a in consolidado.artigos if a.chave == chave), None)
        if antes_artigo and depois_artigo and fora(antes_artigo.texto) != fora(depois_artigo.texto):
            problemas.append(f"{chave}: a alteração de {', '.join('/'.join(a) for a in alvos)} mudou outras partes do artigo")

    # 2. O resto não muda (lido com o parser da avaliação).
    tocados = resultado.tocados
    antes = Counter((a.chave, a.epigrafe, a.texto) for a in comum.artigos(original.texto()) if a.chave not in _chaves_comum(tocados))
    depois = Counter((a.chave, a.epigrafe, a.texto) for a in comum.artigos(consolidado.texto()) if a.chave not in _chaves_comum(tocados))
    if antes != depois:
        diferentes = sorted({c for c, _, _ in (antes - depois) + (depois - antes)})
        problemas.append(f"artigos não alterados que mudaram: {', '.join(diferentes[:10])}")
    fora_antes = [s for s in original.segmentos if not hasattr(s, "chave")]
    fora_depois = [s for s in consolidado.segmentos if not hasattr(s, "chave")]
    if fora_antes != fora_depois:
        problemas.append("o texto fora dos artigos mudou")
    aditados = {r.artigo for r in resultado.registos if r.operacao == "aditar" and r.regra == "aditamento de artigo"}
    if len(consolidado.artigos) != len(original.artigos) + len(aditados):
        problemas.append("o número de artigos não bate certo com os aditamentos")

    # 3. Nada fica por aplicar.
    for p in leitura.por_aplicar:
        problemas.append(f"instrução por aplicar ({p.motivo}): {p.excerto[:120]}")
    for f in resultado.falhas:
        problemas.append(f"instrução que a regra não aplicou ({f['motivo']}): {f['excerto'][:120]}")
    padrao = padrao_diploma(titulo)
    cobertos = _plano(" ".join(i.excerto for i in leitura.instrucoes) + " " + " ".join(p.excerto for p in leitura.por_aplicar))
    tem_artigos = bool(dividir(alterador).artigos)
    for p in paragrafos(alterador):
        if tem_artigos and not p.artigo:
            continue  # preâmbulo
        if padrao and padrao.search(p.texto) and _VERBO_LARGO.search(p.texto) and _plano(p.texto) not in cobertos:
            if all(_DE_OUTRO.search(sem_abreviaturas(p.texto[: m.start()])) for m in padrao.finditer(p.texto)):
                continue  # o original só deu a redação de outro diploma
            if re.search(r"(?:é|são) republicad[oa]|republica-se", p.texto, re.I):
                continue  # a republicação compara-se à parte (republicacao())
            if _OBJETO.search(p.texto) and not re.search(r"seguinte reda|revogad|aditad", p.texto, re.I):
                continue
            if re.search(r"produz(?:em)? efeitos|entra(?:m)? em vigor|aplica-se|aplicam-se", p.texto, re.I) and not re.search(r"seguinte reda|revogad|aditad|onde se l", p.texto, re.I):
                continue  # norma sobre os efeitos da alteração, não uma instrução
            problemas.append(f"parágrafo do alterador com o original e um verbo de alteração sem instrução lida: {p.texto[:120]}")
    alterados = {r.artigo.split("::")[-1] for r in resultado.registos}
    for rotulo in rotulos:
        for _acao, numero in _ROTULO.findall(rotulo):
            if numero_artigo(numero) not in alterados:
                problemas.append(f"o DRE dá o artigo {numero_artigo(numero)} como alterado e não foi")
    return problemas


def _pares_retificacao(excerto: str) -> list[tuple[str, str]]:
    return [
        ((m.group("antes") or m.group("antes2") or "").strip(), (m.group("depois") or m.group("depois2") or "").strip())
        for m in _ONDE.finditer(excerto)
    ]


def _diferenca_menor(a: str, b: str) -> bool:
    """Diferença só de pontuação ou de até três palavras sem números ("referidos número" e
    "referidos no número"): acertos de edição da republicação, não de substância."""
    pa, pb = re.findall(r"\w+", a), re.findall(r"\w+", b)
    if pa == pb:
        return True
    diferentes = [
        x for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, pa, pb, autojunk=False).get_opcodes() if op != "equal"
        for x in pa[i1:i2] + pb[j1:j2]
    ]
    return len(diferentes) <= 3 and not any(re.search(r"\d", x) for x in diferentes)


def _sem_ortografia(texto: str) -> str:
    """Texto sem as diferenças do Acordo Ortográfico (as republicações atualizam a grafia)."""
    texto = _plano(texto).lower()
    for antes, depois in (("cç", "ç"), ("pç", "ç"), ("ct", "t"), ("pt", "t"), ("infra-e", "infrae")):
        texto = texto.replace(antes, depois)
    return texto


def _chaves_comum(tocados: set[str]) -> set[str]:
    """As chaves dos artigos tocados, também na forma do `comum.py` (anexos só com `## Anexo`)."""
    resultado = set(tocados)
    for chave in tocados:
        if "::" in chave:
            parte, numero = chave.split("::", 1)
            resultado.add(numero)
            resultado.add(f"{parte}::{numero}")
    return resultado


def republicacao(alterador: str, consolidado: Corpo, titulo: str, tocados: set[str]) -> dict | None:
    """Compara o consolidado com a republicação do original no anexo do diploma que altera.

    Quando o diploma que altera republica o original, o anexo é o texto em vigor nessa data,
    feito por quem legislou: é a melhor verificação independente que há. Devolve as contagens
    de artigos iguais, diferentes e em falta, ou None se não houver republicação. Só contam
    como erro as diferenças de substância nos artigos alterados: a republicação também atualiza a grafia e
    faz acertos de redação noutros artigos ("90" passa a "noventa"), que nenhuma instrução
    manda fazer."""
    corpo = dividir(alterador)
    partes = [p for p in corpo.partes() if p and re.search(r"republica", p, re.I)]
    if len(partes) != 1:
        return None
    padrao = padrao_diploma(titulo)
    anuncio = [p.texto for p in paragrafos(alterador) if re.search(r"republicad|republica-se", p.texto, re.I)]
    if not padrao or not (padrao.search(sem_ligacoes(partes[0])) or any(
        padrao.search(t) and not _DE_OUTRO.search(sem_abreviaturas(t[: padrao.search(t).start()])) for t in anuncio
    )):
        return None  # a republicação é de outro diploma
    republicados = {a.numero: a for a in corpo.artigos if a.parte == partes[0]}
    nossos = {a.numero: a for a in consolidado.artigos if not a.parte}
    if not republicados:
        return None
    iguais, menores, diferentes = [], [], []
    for numero, artigo in nossos.items():
        if numero not in republicados:
            continue
        a, b = _sem_ortografia(artigo.texto), _sem_ortografia(republicados[numero].texto)
        if a == b:
            iguais.append(numero)
        elif _diferenca_menor(a, b):
            menores.append(numero)
        else:
            diferentes.append(numero)
    return {
        "iguais": len(iguais),
        "diferencas_menores": menores,
        "diferentes": [n for n in diferentes if n in tocados],
        "diferentes_nao_alterados": [n for n in diferentes if n not in tocados],
        "so_no_consolidado": sorted(set(nossos) - set(republicados)),
        "so_na_republicacao": sorted(set(republicados) - set(nossos)),
    }
