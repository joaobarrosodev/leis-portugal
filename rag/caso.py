"""Análise de um caso narrado por um advogado: partir o caso, pesquisar por partes, analisar (experimental).

Um advogado escreve «o contexto é este, aconteceu isto ao meu cliente, estou a pensar usar estas leis». Numa consulta
só, a pesquisa encontra o código certo mas não o artigo. O fluxo de caso tem três passos:

1. `partir`: um LLM escreve 3 a 6 consultas curtas, uma por questão jurídica, no vocabulário da lei e com o nome do
   código, e os artigos que acha decisivos («o 394.º do Código do Trabalho»), com as regras de `rag/CASO-PARTIR.md`;
2. `pesquisar`: uma pesquisa por artigo provável (conta o 1.º resultado) e uma por consulta, intercaladas (o 1.º de
   cada, depois o 2.º de cada, …, cada artigo uma vez); o LLM recebe os 16 primeiros;
3. `analisar`: um LLM analisa o caso só com esses artigos, com as regras de `rag/CASO-ANALISE.md`, numa estrutura fixa
   (questões, leis pensadas, o que fazer, prazos, resultado previsível, o que depende de prova), com cada afirmação
   presa a um artigo;
4. `completar`: na análise, o LLM lista em `falta` as consultas para os artigos de que precisava e não teve (sobretudo
   prazos e a forma dos atos). Cada consulta é mais uma pesquisa, entram até 8 artigos novos depois dos 16;
5. contas dos prazos: na mesma análise, o LLM escreve em `contas` as contas que o sistema deve fazer (início, duração,
   regime, dilação), e `rag.prazos` faz-as com as regras da lei (feriados, férias judiciais, transferência do termo).
   O LLM analisa outra vez com os artigos novos e as contas feitas. Só há segunda volta se a primeira pediu alguma
   coisa (artigos que a pesquisa trouxe, ou contas válidas).

Medido nos 39 casos de `avaliacao/casos/` (26/11/2026, Opus em todos os passos, sem jurista): com o texto inteiro, 33
de 161 artigos essenciais nos 8 primeiros e 5 de 39 análises certas para os dois juízes; partindo o caso, 127 de 161
e 31 de 39. Com a 2.ª volta (`completar`), 36 de 39; em 16 casos novos, escritos depois, de 10 para 14 de 16. Com as
contas dos prazos, 37 de 39 e 12 de 16, com menos prazos errados (4 → 2 nos 55). Não é número para dizer em público.

Dois modos, por causa do regime dos atos de advogados e solicitadores (Lei n.º 10/2024): a consulta jurídica, que
é interpretar e aplicar normas a pedido de terceiro (art. 6.º), é competência de advogados e solicitadores (art. 4.º,
n.º 4), e praticá-la sem habilitação é crime (art. 11.º, n.º 2).
- `profissional` (`--profissional`, com a declaração de que quem usa é advogado ou solicitador inscrito): o fluxo acima,
  com o que fazer, os prazos contados e o resultado previsível (`rag/CASO-ANALISE.md`). É uma ferramenta de trabalho
  do profissional, que decide e responde pelo conselho.
- `publico` (por omissão): explica o que a lei diz sobre as questões que a situação levanta, de que factos dependem e
  que prazos fixa, sem dizer o que a pessoa deve fazer nem calcular datas do caso dela (`rag/CASO-INFORMACAO.md`), e
  acaba sempre a dizer onde procurar um advogado ou solicitador e a proteção jurídica. Não foi medido.

Não está na aplicação. Não há limiar: é o LLM que diz se os artigos chegam. Sem a chave de uma IA (`rag.provedores`),
ou se o passo de partir falhar, a pesquisa é a do texto inteiro, como a app faz hoje.

    PYTHONPATH=src python -m rag.caso pedido.txt [--profissional] [--data 2026-11-26] [--indice PASTA]
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from rag import prazos as prazos_mod
from rag import provedores
from rag.fontes import RAIZ
from rag.pesquisa import Resultado
from rag.resposta import CARACTERES_POR_ARTIGO, extrair_json, llm_disponivel


FICHEIRO_PARTIR = RAIZ / "rag" / "CASO-PARTIR.md"
FICHEIRO_ANALISE = RAIZ / "rag" / "CASO-ANALISE.md"
FICHEIRO_INFORMACAO = RAIZ / "rag" / "CASO-INFORMACAO.md"
PROFISSIONAL, PUBLICO = "profissional", "publico"
ARTIGOS_NO_CONTEXTO = 16
K_POR_CONSULTA = 30
K_POR_ARTIGO = 3
MAXIMO_CONSULTAS = 8
MAXIMO_ARTIGOS = 10
MAXIMO_CARACTERES_CONSULTA = 400
MAXIMO_FALTA = 6
MAXIMO_CONTAS = 10
ARTIGOS_A_MAIS = 8
POR_FALTA = 2
SECCOES = ("questoes", "leis_pensadas", "o_que_fazer", "prazos", "resultado_previsivel", "depende_de_prova")
SECCOES_PUBLICO = ("temas", "o_que_a_lei_diz", "de_que_depende", "prazos_na_lei")
TITULOS = {
    "questoes": "Questões", "leis_pensadas": "As leis que pensa usar", "o_que_fazer": "O que fazer", "prazos": "Prazos",
    "resultado_previsivel": "Resultado previsível", "depende_de_prova": "O que depende de prova",
    "temas": "As questões que a situação levanta", "o_que_a_lei_diz": "O que a lei diz", "de_que_depende": "De que depende",
    "prazos_na_lei": "Prazos que a lei fixa",
}
ENCAMINHAMENTO = (
    "Para saber o que fazer no seu caso, fale com um advogado ou solicitador. Se não puder pagar, pode pedir proteção "
    "jurídica (consulta jurídica e apoio judiciário) no sítio da Segurança Social (Lei n.º 34/2004, art. 22.º). A Ordem "
    "dos Advogados e algumas câmaras municipais têm gabinetes de consulta jurídica."
)
AVISO_PUBLICO = ("Isto é informação sobre o que a lei diz, escrita por um modelo de IA a partir dos artigos citados. Não é "
                 "aconselhamento jurídico sobre o seu caso, e o texto deve confirmar-se na fonte oficial. " + ENCAMINHAMENTO)
AVISO_PROFISSIONAL = ("Apoio ao trabalho de advogados e solicitadores, escrito por um modelo de IA a partir dos artigos citados: "
                      "não substitui o juízo profissional, e o texto deve confirmar-se na fonte oficial.")
# As linhas que só servem às sessões do Claude que fazem estes passos por lotes, nas medições.
_LINHA_DOS_FICHEIROS = re.compile(r"^.*(?:entrada|saida)-NN\.jsonl.*\n\n?", re.M)
_CITACAO_NO_TEXTO = re.compile(r"\[(\d{1,3})\]")


def _sem_ficheiros(ficheiro: Path) -> str:
    return _LINHA_DOS_FICHEIROS.sub("", ficheiro.read_text(encoding="utf-8")).rstrip()


def instrucoes_partir() -> str:
    return _sem_ficheiros(FICHEIRO_PARTIR) + (
        '\n\nResponde só com um objeto JSON: {"consultas": ["…", "…"], "artigos_provaveis": ["…"]}'
    )


def _modo(modo: str) -> str:
    if modo not in (PROFISSIONAL, PUBLICO):
        raise ValueError(f"modo desconhecido: {modo} (profissional ou publico)")
    return modo


def instrucoes_analise(modo: str = PUBLICO) -> str:
    ficheiro = FICHEIRO_ANALISE if _modo(modo) == PROFISSIONAL else FICHEIRO_INFORMACAO
    return _sem_ficheiros(ficheiro) + "\n\nResponde só com esse objeto JSON."


@dataclass
class Decomposicao:
    consultas: list[str]
    artigos_provaveis: list[str] = field(default_factory=list)


def _textos(valor, maximo: int) -> list[str]:
    if not isinstance(valor, list):
        return []
    saida: list[str] = []
    for t in valor:
        if isinstance(t, str):
            t = " ".join(t.split())[:MAXIMO_CARACTERES_CONSULTA]
            if t and t not in saida:
                saida.append(t)
    return saida[:maximo]


def decomposicao(dados: dict) -> Decomposicao | None:
    """O JSON do passo de partir ({"consultas", "artigos_provaveis"}) limpo; `None` se não traz nenhuma consulta."""
    consultas = _textos(dados.get("consultas"), MAXIMO_CONSULTAS)
    return Decomposicao(consultas, _textos(dados.get("artigos_provaveis"), MAXIMO_ARTIGOS)) if consultas else None


def partir(pedido: str) -> Decomposicao | None:
    """As consultas e os artigos prováveis para o pedido; `None` sem LLM ou se a chamada falhar."""
    if not llm_disponivel():
        return None
    try:
        escrita = provedores.escrever(instrucoes_partir(), pedido, max_tokens=4000, esforco="medium")
    except provedores.ErroIA:
        return None
    return None if escrita.recusou else decomposicao(extrair_json(escrita.texto))


def intercalar(listas: list[list[Resultado]]) -> list[Resultado]:
    """O 1.º de cada lista, depois o 2.º de cada, …; cada artigo uma vez. Cada consulta tem lugar nos primeiros."""
    vistos, saida = set(), []
    for i in range(max((len(l) for l in listas), default=0)):
        for l in listas:
            if i < len(l) and (l[i].documento, l[i].chave) not in vistos:
                vistos.add((l[i].documento, l[i].chave))
                saida.append(l[i])
    return saida


def pesquisar(pesquisa, pedido: str, data: str, decomposto: Decomposicao | None, *, n: int | None = ARTIGOS_NO_CONTEXTO) -> list[Resultado]:
    """Os artigos para o caso: os das consultas e dos artigos prováveis, intercalados (primeiro os artigos prováveis);
    sem decomposição, os do texto inteiro. `n=None` devolve a lista toda (para medir posições)."""
    if decomposto is None:
        resultados = pesquisa.pesquisar(pedido, data, k=max(n or 0, K_POR_CONSULTA)).resultados
    else:
        por_artigo = [pesquisa.pesquisar(a, data, k=K_POR_ARTIGO).resultados[:1] for a in decomposto.artigos_provaveis]
        por_consulta = [pesquisa.pesquisar(q, data, k=K_POR_CONSULTA).resultados for q in decomposto.consultas]
        resultados = intercalar(por_artigo + por_consulta)
    return resultados if n is None else resultados[:n]


def contexto(artigos: list[Resultado], inicio: int = 1) -> str:
    """Os artigos numerados (a partir de `inicio`) com os avisos, no formato de `rag.resposta.contexto`."""
    return "\n\n".join(
        f"[{n}] {r.rotulo}" + "".join(f"\nAviso: {a}" for a in r.avisos) + f"\n{r.texto[:CARACTERES_POR_ARTIGO]}"
        for n, r in enumerate(artigos, inicio)
    )


def completar(pesquisa, ja: set[tuple[str, str]], falta: list[str], data: str, *, maximo: int = ARTIGOS_A_MAIS) -> list[Resultado]:
    """Os artigos novos para as consultas em `falta`: os `POR_FALTA` primeiros de cada uma que não estão em `ja`
    (pares documento, chave), intercalados, até `maximo`."""
    listas = [[r for r in pesquisa.pesquisar(q, data, k=K_POR_CONSULTA).resultados if (r.documento, r.chave) not in ja][:POR_FALTA]
              for q in falta[:MAXIMO_FALTA]]
    return intercalar(listas)[:maximo]


def mensagem(pedido: str, data: str, artigos: list[Resultado], contas: str = "", modo: str = PUBLICO) -> str:
    blocos = f"\n\nContas de prazos feitas pelo sistema:\n{contas}" if contas else ""
    quem = "Pedido do advogado" if _modo(modo) == PROFISSIONAL else "Situação descrita"
    return f"Data de referência: {data}\n\nArtigos:\n\n{contexto(artigos)}{blocos}\n\n{quem}:\n{pedido}"


def contas_feitas(contas: list[prazos_mod.Conta], data: str) -> str:
    """As contas pedidas pelo LLM, feitas, no texto que a 2.ª análise recebe; vazio se não houver nenhuma válida."""
    feitas = []
    for c in contas:
        try:
            feitas.append(prazos_mod.contar(c))
        except ValueError:
            continue
    return prazos_mod.texto(feitas, date.fromisoformat(data)) if feitas else ""


@dataclass
class Analise:
    responde: bool
    seccoes: dict[str, str] = field(default_factory=dict)
    citacoes: list[Resultado] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    artigos: list[Resultado] = field(default_factory=list)  # os que o LLM recebeu
    decomposicao: Decomposicao | None = None
    falta: list[str] = field(default_factory=list)  # o que o LLM disse que lhe faltava
    contas: list[prazos_mod.Conta] = field(default_factory=list)  # as contas de prazos que o LLM pediu
    contas_texto: str = ""  # as contas feitas pelo sistema, como a 2.ª análise as recebeu
    completada: bool = False  # houve segunda volta com os artigos de `falta`
    modo: str = PUBLICO
    motivo: str | None = None
    modelo: str = ""
    aviso_modelo: str | None = None
    erro: str | None = None

    @property
    def aviso(self) -> str:
        """O aviso que acompanha sempre a análise, em qualquer ecrã: profissional ou público, consoante o modo."""
        return AVISO_PROFISSIONAL if self.modo == PROFISSIONAL else AVISO_PUBLICO


def interpretar(dados: dict, artigos: list[Resultado], modo: str = PUBLICO) -> Analise:
    """A resposta do LLM como `Analise`. Conta como citado cada número válido em `citacoes` ou escrito [n] no texto;
    sem nenhuma citação de um artigo dado, a análise não conta («não sei»). No modo público lê `explicacao` e ignora
    as contas de prazos (não se calculam datas do caso de quem pergunta)."""
    profissional = _modo(modo) == PROFISSIONAL
    falta = _textos(dados.get("falta"), MAXIMO_FALTA)
    pedidas = dados.get("contas") if profissional and isinstance(dados.get("contas"), list) else []
    contas = [c for c in map(prazos_mod.de_json, pedidas) if c][:MAXIMO_CONTAS]
    if not dados.get("responde"):
        return Analise(False, artigos=artigos, falta=falta, contas=contas, modo=modo, motivo="o modelo diz que os artigos não chegam para analisar o caso")
    chave, nomes = ("analise", SECCOES) if profissional else ("explicacao", SECCOES_PUBLICO)
    bruto = dados.get(chave) if isinstance(dados.get(chave), dict) else {}
    seccoes = {s: " ".join(str(bruto.get(s) or "").split()) for s in nomes if bruto.get(s)}
    numeros = [n for n in dados.get("citacoes") or [] if isinstance(n, int)]
    numeros += [int(m) for t in seccoes.values() for m in _CITACAO_NO_TEXTO.findall(t)]
    validos = list(dict.fromkeys(n for n in numeros if 1 <= n <= len(artigos)))
    citacoes = [artigos[n - 1] for n in sorted(validos)]
    if not seccoes or not citacoes:
        return Analise(False, artigos=artigos, falta=falta, contas=contas, modo=modo, motivo="análise sem citação de um artigo dado")
    avisos = list(dict.fromkeys(a for r in citacoes for a in r.avisos))
    return Analise(True, seccoes, citacoes, avisos, artigos, falta=falta, contas=contas, modo=modo)


def _uma_analise(pedido: str, data: str, artigos: list[Resultado], contas: str = "", modo: str = PUBLICO) -> Analise:
    try:
        escrita = provedores.escrever(instrucoes_analise(modo), mensagem(pedido, data, artigos, contas, modo), max_tokens=16000, esforco="medium")
    except provedores.ErroIA as e:
        return Analise(False, artigos=artigos, modo=modo, motivo=str(e), erro=str(e))
    if escrita.recusou:
        return Analise(False, artigos=artigos, modo=modo, motivo="o modelo recusou")
    return interpretar(extrair_json(escrita.texto), artigos, modo)


def analisar(pesquisa, pedido: str, data: str, *, decomposto: Decomposicao | None = None, completar_falta: bool = True,
             modo: str = PUBLICO) -> Analise:
    """O fluxo todo: partir (se não vier já a decomposição), pesquisar, analisar e, se o LLM disse que lhe faltavam
    artigos e a pesquisa os traz (ou, no modo profissional, pediu contas de prazos), analisar outra vez com eles."""
    _modo(modo)
    if not llm_disponivel():
        return Analise(False, modo=modo, motivo="a análise de caso precisa da chave de uma IA (rag.provedores)")
    quem, aviso = provedores.descricao(), provedores.aviso_medicao()
    decomposto = decomposto or partir(pedido)
    artigos = pesquisar(pesquisa, pedido, data, decomposto)
    if not artigos:
        return Analise(False, decomposicao=decomposto, modo=modo, motivo="a pesquisa não encontrou artigos", modelo=quem, aviso_modelo=aviso)
    analise = _uma_analise(pedido, data, artigos, modo=modo)
    novos = completar(pesquisa, {(r.documento, r.chave) for r in artigos}, analise.falta, data) if completar_falta and analise.falta and not analise.erro else []
    contas = contas_feitas(analise.contas, data) if completar_falta and not analise.erro and modo == PROFISSIONAL else ""
    if novos or contas:
        segunda = _uma_analise(pedido, data, artigos + novos, contas, modo)
        if not segunda.erro:
            segunda.falta, segunda.contas, segunda.contas_texto, segunda.completada = analise.falta, analise.contas, contas, True
            analise = segunda
    analise.decomposicao, analise.modelo, analise.aviso_modelo = decomposto, quem, aviso
    return analise


def mostrar(analise: Analise) -> str:
    linhas = []
    if analise.decomposicao:
        linhas += ["Consultas:"] + [f"  - {q}" for q in analise.decomposicao.consultas]
        if analise.decomposicao.artigos_provaveis:
            linhas += ["Artigos prováveis: " + "; ".join(analise.decomposicao.artigos_provaveis)]
        linhas.append("")
    if not analise.responde:
        linhas.append(f"Não sei. ({analise.motivo})")
    for s, texto in analise.seccoes.items():
        linhas += [f"{TITULOS[s]}:", f"  {texto}", ""]
    if analise.falta:
        linhas.append(("Procurado à parte, porque faltava: " if analise.completada else "O modelo diz que faltava: ") + "; ".join(analise.falta))
    if analise.contas_texto:
        linhas += ["Contas de prazos feitas pelo sistema:", analise.contas_texto, ""]
    if analise.artigos:
        linhas.append("Artigos dados ao modelo:")
        citados = {id(r) for r in analise.citacoes}
        linhas += [f"  [{n}] {'*' if id(r) in citados else ' '} {r.rotulo}" for n, r in enumerate(analise.artigos, 1)]
    linhas += [f"Aviso: {a}" for a in analise.avisos]
    if analise.aviso_modelo:
        linhas.append(analise.aviso_modelo)
    linhas += ["", analise.aviso]
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pedido", type=Path, help="Ficheiro de texto com o pedido ou a situação ('-' lê da entrada).")
    parser.add_argument("--profissional", action="store_true",
                        help="Declaras que és advogado ou solicitador inscrito: a análise aplica a lei ao caso concreto.")
    parser.add_argument("--data", default=date.today().isoformat(), help="Data de referência (AAAA-MM-DD).")
    parser.add_argument("--indice", type=Path)
    args = parser.parse_args(argv)
    pedido = sys.stdin.read() if str(args.pedido) == "-" else args.pedido.read_text(encoding="utf-8")
    from rag.modelos import Reranker
    from rag.pesquisa import Pesquisa

    pesquisa = Pesquisa(args.indice, reranker=Reranker("cruzado"))
    modo = PROFISSIONAL if args.profissional else PUBLICO
    if args.profissional:
        print("Modo profissional: declaraste ser advogado ou solicitador inscrito.\n")
    print(mostrar(analisar(pesquisa, pedido.strip(), args.data, modo=modo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
