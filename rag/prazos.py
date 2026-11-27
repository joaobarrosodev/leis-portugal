"""Contas de prazos com as regras da lei, para o fluxo de caso (`rag.caso`).

O LLM diz que conta é (o início, quanto tempo, em que unidade, qual o regime e a dilação, se houver) e este módulo faz a
conta. Errar a aritmética de um prazo, os feriados ou as férias judiciais é o erro mais caro para um advogado, e é o
que os modelos mais falham nos casos de `avaliacao/casos/`.

Regimes (todos excluem o dia do evento, CC 279.º, b), e CPA 87.º, b)):
- `civil`: prazos substantivos (CC 279.º e 296.º). Corridos. Semanas, meses e anos acabam no dia correspondente
  (279.º, c)), e 8 ou 15 dias valem uma ou duas semanas (279.º, d)). O termo em domingo ou feriado passa para o primeiro
  dia útil (279.º, e)).
- `civil_em_juizo`: o mesmo, para um ato a praticar em juízo (propor uma ação, por exemplo). As férias judiciais
  equiparam-se a domingos e feriados (279.º, e), 2.ª parte).
- `processual`: prazos do processo (CPC 138.º). Contínuo, suspende-se nas férias judiciais, salvo se durar 6 meses ou
  mais. O termo em dia de tribunais encerrados (sábado, domingo, feriado) passa para o 1.º dia útil seguinte.
- `processual_urgente`: o mesmo, sem suspensão nas férias (processos urgentes, por exemplo a insolvência, CIRE 9.º).
- `uteis`: só contam os dias úteis (CPA 87.º, c), RGCO 60.º, os «dias úteis» do Código do Trabalho). Num prazo de mais de
  6 meses contam-se todos os dias (CPA 87.º, d)).
- `periodo`: um período, e não um prazo para praticar um ato. Por exemplo, até quando dura uma presunção ou uma
  responsabilidade, ou a partir de quando uma renda é exigível. Conta-se como o `civil`, mas o termo fica onde cai,
  sem passar para dia útil.

A dilação (`dilacao`, em dias) conta-se com o prazo que se lhe segue como um prazo só (CPC 142.º).

O calendário tem os feriados obrigatórios do CT 234.º (com a Páscoa) e as férias judiciais da Lei n.º 62/2013, art. 28.º.
Não conta feriados municipais nem tolerâncias de ponto, e isso vai escrito em cada conta.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from functools import cache


REGIMES = ("civil", "civil_em_juizo", "processual", "processual_urgente", "uteis", "periodo")
UNIDADES = ("dias", "semanas", "meses", "anos")
AVISO = "Não conta feriados municipais nem tolerâncias de ponto."
_MESES_SEM_SUSPENSAO = 6


def pascoa(ano: int) -> date:
    """Domingo de Páscoa (calendário gregoriano, algoritmo de Meeus/Jones/Butcher)."""
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return date(ano, mes, dia)


@cache
def feriados(ano: int) -> frozenset[date]:
    """Os feriados obrigatórios do CT 234.º, n.º 1."""
    p = pascoa(ano)
    fixos = [(1, 1), (4, 25), (5, 1), (6, 10), (8, 15), (10, 5), (11, 1), (12, 1), (12, 8), (12, 25)]
    return frozenset([date(ano, m, d) for m, d in fixos] + [p - timedelta(days=2), p, p + timedelta(days=60)])


def feriado(d: date) -> bool:
    return d in feriados(d.year)


def ferias_judiciais(d: date) -> bool:
    """Lei n.º 62/2013, art. 28.º: 22/12 a 3/1, Domingo de Ramos a Segunda-Feira de Páscoa, 16/7 a 31/8."""
    if (d.month == 12 and d.day >= 22) or (d.month == 1 and d.day <= 3):
        return True
    if (d.month == 7 and d.day >= 16) or d.month == 8:
        return True
    p = pascoa(d.year)
    return p - timedelta(days=7) <= d <= p + timedelta(days=1)


def dia_util(d: date) -> bool:
    return d.weekday() < 5 and not feriado(d)


def _seguinte(d: date, aceita) -> date:
    while not aceita(d):
        d += timedelta(days=1)
    return d


def _mais_meses(d: date, meses: int) -> date:
    mes = d.month - 1 + meses
    ano, mes = d.year + mes // 12, mes % 12 + 1
    return date(ano, mes, min(d.day, calendar.monthrange(ano, mes)[1]))


@dataclass
class Conta:
    o_que: str
    inicio: date  # o dia do evento (não conta)
    quantidade: int
    unidade: str = "dias"
    regime: str = "civil"
    dilacao: int = 0
    artigo: str = ""


@dataclass
class Contado:
    conta: Conta
    fim: date  # o último dia em que o ato ainda pode ser praticado
    passos: list[str]

    def passou(self, referencia: date) -> bool:
        return self.fim < referencia


def _meses_equivalentes(c: Conta) -> float:
    return {"dias": c.quantidade / 30, "semanas": c.quantidade * 7 / 30, "meses": c.quantidade, "anos": c.quantidade * 12}[c.unidade]


def contar(c: Conta) -> Contado:
    """O fim do prazo, com os passos da conta (para mostrar ao LLM e ao advogado)."""
    if c.regime not in REGIMES:
        raise ValueError(f"regime desconhecido: {c.regime}")
    if c.unidade not in UNIDADES:
        raise ValueError(f"unidade desconhecida: {c.unidade}")
    if c.quantidade <= 0 or c.dilacao < 0:
        raise ValueError("quantidade tem de ser positiva e dilação não negativa")
    passos: list[str] = []
    quantidade, unidade = c.quantidade, c.unidade
    if c.regime in ("civil", "civil_em_juizo", "periodo") and unidade == "dias" and quantidade in (8, 15) and not c.dilacao:
        quantidade, unidade = (1 if quantidade == 8 else 2), "semanas"
        passos.append(f"{c.quantidade} dias valem {quantidade} semana(s) (CC 279.º, d))")
    longo = _meses_equivalentes(c) >= _MESES_SEM_SUSPENSAO

    if c.regime == "uteis" and not (longo and unidade == "meses") and unidade in ("dias", "semanas"):
        n = c.dilacao + quantidade * (7 if unidade == "semanas" else 1)
        if longo:
            fim = c.inicio + timedelta(days=n)
            passos.append(f"{n} dias contados todos, por ser prazo de mais de seis meses (CPA 87.º, d))")
        else:
            d, contados = c.inicio, 0
            while contados < n:
                d += timedelta(days=1)
                if dia_util(d):
                    contados += 1
            fim = d
            passos.append(f"{n} dias úteis a partir do dia seguinte a {c.inicio:%d/%m/%Y}, sem sábados, domingos e feriados")
    elif c.regime == "processual" and not longo:
        # Contínuo, suspenso nas férias judiciais (CPC 138.º, n.º 1); a dilação conta-se com o prazo (CPC 142.º).
        if unidade in ("dias", "semanas"):
            n = c.dilacao + quantidade * (7 if unidade == "semanas" else 1)
            d, contados, suspensos = c.inicio, 0, 0
            while contados < n:
                d += timedelta(days=1)
                if ferias_judiciais(d):
                    suspensos += 1
                else:
                    contados += 1
            fim = d
        else:
            alvo = _mais_meses(c.inicio + timedelta(days=c.dilacao), quantidade * (12 if unidade == "anos" else 1))
            suspensos = sum(ferias_judiciais(c.inicio + timedelta(days=i)) for i in range(1, (alvo - c.inicio).days + 1))
            d, falta = alvo, suspensos
            while falta:
                d += timedelta(days=1)
                if not ferias_judiciais(d):
                    falta -= 1
            fim = d
        total = f"{c.dilacao} de dilação + {c.quantidade} {c.unidade}" if c.dilacao else f"{c.quantidade} {c.unidade}"
        passos.append(f"{total} contínuos desde o dia seguinte a {c.inicio:%d/%m/%Y}"
                      + (f", suspensos {suspensos} dias em férias judiciais (CPC 138.º, n.º 1)" if suspensos else ""))
    else:
        inicio = c.inicio + timedelta(days=c.dilacao)
        if unidade == "dias":
            fim = inicio + timedelta(days=quantidade)
        elif unidade == "semanas":
            fim = inicio + timedelta(days=7 * quantidade)
        else:
            fim = _mais_meses(inicio, quantidade * (12 if unidade == "anos" else 1))
        if c.dilacao:
            passos.append(f"{c.dilacao} dias de dilação contados com o prazo (CPC 142.º)")
        sem = " sem suspensão em férias" if c.regime in ("processual", "processual_urgente") else ""
        passos.append(f"{quantidade} {unidade}{sem} a contar de {inicio:%d/%m/%Y}, sem contar esse dia: {fim:%d/%m/%Y}")
    # Transferência do termo.
    if c.regime == "periodo":
        return Contado(c, fim, passos + ["é um período, e não um prazo para um ato: o termo não passa para dia útil"])
    if c.regime == "civil":
        aceita, regra = (lambda d: d.weekday() != 6 and not feriado(d)), "domingo ou feriado: primeiro dia útil (CC 279.º, e))"
        destino = _seguinte(fim, aceita)
        if destino != fim:
            destino = _seguinte(destino, dia_util)
    elif c.regime == "civil_em_juizo":
        aceita = lambda d: d.weekday() != 6 and not feriado(d) and not ferias_judiciais(d)  # noqa: E731
        regra = "domingo, feriado ou férias judiciais, por ser ato em juízo: primeiro dia útil (CC 279.º, e))"
        destino = _seguinte(fim, aceita)
        if destino != fim:
            destino = _seguinte(destino, lambda d: dia_util(d) and not ferias_judiciais(d))
    else:
        aceita, regra = dia_util, "dia em que tribunais ou serviços estão fechados: 1.º dia útil seguinte (CPC 138.º, n.º 2; CPA 87.º, f))"
        destino = _seguinte(fim, aceita)
    if destino != fim:
        passos.append(f"o termo, {fim:%d/%m/%Y}, cai em {regra}: {destino:%d/%m/%Y}")
    return Contado(c, destino, passos)


def _data(valor) -> date | None:
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def de_json(d: dict) -> Conta | None:
    """Uma conta pedida pelo LLM ({"o_que", "inicio": "AAAA-MM-DD", "quantidade", "unidade", "regime", "dilacao",
    "artigo"}); `None` se lhe falta o início, a quantidade ou um regime e uma unidade conhecidos."""
    if not isinstance(d, dict):
        return None
    inicio = _data(d.get("inicio"))
    try:
        quantidade, dilacao = int(d.get("quantidade")), int(d.get("dilacao") or 0)
    except (TypeError, ValueError):
        return None
    unidade, regime = str(d.get("unidade") or "dias").strip().lower(), str(d.get("regime") or "").strip().lower()
    if not inicio or quantidade <= 0 or dilacao < 0 or unidade not in UNIDADES or regime not in REGIMES:
        return None
    return Conta(" ".join(str(d.get("o_que") or "").split())[:200], inicio, quantidade, unidade, regime, dilacao,
                 " ".join(str(d.get("artigo") or "").split())[:100])


def texto(contados: list[Contado], referencia: date) -> str:
    """As contas para dar ao LLM na 2.ª análise, uma por linha."""
    linhas = []
    for n, r in enumerate(contados, 1):
        c = r.conta
        estado = "já passou" if r.passou(referencia) else "ainda não passou"
        linhas.append(f"({n}) {c.o_que or 'prazo'} [{c.artigo}]: termina a {r.fim:%d/%m/%Y}, {estado} a {referencia:%d/%m/%Y}. "
                      f"Conta ({c.regime}): " + "; ".join(r.passos) + ".")
    return "\n".join(linhas + [AVISO]) if linhas else ""
