"""Pesquisa no índice por artigo.

Ordem dos candidatos (`nivel`, do mais forte para o mais fraco):

3. referência exata: o artigo citado ("artigo 78.º-B") no diploma ou código citado;
2. BM25 dentro dos diplomas ou códigos citados na pergunta;
1. BM25 em todo o acervo.

Com reranker (cross-encoder ou embeddings, ver `rag.modelos`), os níveis 3 e 2 juntam-se e o
reranker reordena-os: a referência exata entra como candidata, não passa à frente, porque muitas
perguntas citam um artigo só como contexto ("a coima das contraordenações do n.º 1 do artigo 24.º"
está no 25.º). Sem reranker, a ordem é a dos níveis. Só entram pedaços cujo texto
estava em vigor na data da pergunta (`desde <= data < ate`). Um código republicado
(`texto_em_vigor_em`, p. ex. o Código do IRS do DL 442-A/88) é trocado pelo mesmo artigo
no consolidado que tem o texto atual (a Lei n.º 82-E/2014).

Um diploma citado pelo número cujo texto já não está em vigor no próprio registo (o Código Penal do
DL 400/82, fechado pela regra das redações anteriores) responde pelo registo com o texto em vigor
(`texto_em_vigor_em` ou `redacao_atual_em`): o mesmo artigo, ou o da mesma epígrafe quando a numeração
mudou (`_no_texto_em_vigor`). Um registo repetido do mesmo diploma (`mesmo_diploma_em`, p. ex. a Lei
n.º 28/82 do Tribunal Constitucional, que o DRE tem consolidada e original) é trocado pelo principal.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

from rag import ambito as ambito_mod
from rag import referencias as refs_mod
from rag import texto as termos_mod
from rag import vigencia as vigencia_mod
from rag.fontes import PASTA_INDICE, revogacao_por_produzir_efeitos, revogado


PESOS_BM25 = (2.0, 1.0)  # cabeçalho (diploma, sumário, anexo, epígrafe), texto
MAX_TERMOS = 24
PRIOR_CONSOLIDADO = 1.25
PRIOR_ESTADO = {"repealed": 0.6, "not_in_force": 0.6, "unknown": 0.85}
PRIOR_REPUBLICACAO = 0.6
PRIOR_ARTIGO_REVOGADO = 0.6
PRIOR_SETOR = 0.8  # regime de um setor (função pública) numa pergunta que não fala dele: `rag.ambito`
PRIOR_ANTIGO = 0.75  # portaria, despacho ou aviso de antes de 1990 sem versão consolidada
# O reranker não vê os pesos acima: nos artigos que a pergunta não cita, tira-se isto à pontuação dele
# para ordenar (não para o limiar do "não sei"). Pontos de logit do bge-reranker-v2-m3.
RERANKER_SETOR = 1.0
RERANKER_ANTIGO = 1.0
REVOGADO = ("repealed", "not_in_force")
# Atos da UE sem versão portuguesa, traduzidos pelo projeto (`version.kind: translation`). O índice não
# guarda o `version.label`, que diz de que língua; o aviso diz o essencial sem mudar o formato do índice.
AVISO_TRADUCAO = (
    "Tradução não oficial para português europeu, feita pelo projeto a partir de outra língua do EUR-Lex; "
    "sem valor jurídico. O ato não tem versão portuguesa oficial."
)
CODIGOS_CANDIDATOS = 15  # candidatos do BM25 só nos códigos principais, juntos aos do reranker
CODIGO_GRANDE = 60  # artigos, no mínimo, de uma parte para contar como código principal
_NOME_CODIGO = re.compile(r"^(codigo|lei geral)\b")
# Ligações de um registo ao que tem o texto em vigor (`rag.indice`, `rag.copias`) e ao registo principal do
# mesmo diploma (`rag.duplicados`). A aplicação 0.1.1 só conhece `texto_em_vigor_em` e ignora as outras.
LIGACOES_AO_ATUAL = ("texto_em_vigor_em", "redacao_atual_em")
MESMO_DIPLOMA = "mesmo_diploma_em"
# Artigos em vigor, no mínimo, para um nome de código do próprio índice («Código Cooperativo») contar
# como citação sem estar em `rag.referencias.CODIGOS` (`Pesquisa.codigos_na_pergunta`).
ARTIGOS_NOME_DO_INDICE = 20
_EPIGRAFES_VAZIAS = {"", "revogado", "revogada"}
EPIGRAFE_PARECIDA = 0.75  # no mesmo número
EPIGRAFE_MUITO_PARECIDA = 0.9  # noutro número, e só uma


def _parecida(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0.0
_LIGACAO = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def _sem_ligacoes(texto: str) -> str:
    return _LIGACAO.sub(r"\1", texto.strip().removeprefix(">").strip()).rstrip(".")


@dataclass
class Resultado:
    id: int
    documento: str
    titulo: str
    parte: str
    numero: str
    epigrafe: str
    chave: str
    rotulo: str
    texto: str
    notas: str
    desde: str | None
    ate: str | None
    nivel: int = 1
    pontuacao: float = 0.0
    origem: str = ""
    reranker: float | None = None
    redirecionado_de: str | None = None
    # O número citado na pergunta, quando o texto em vigor numera o artigo de outra maneira (`_no_texto_em_vigor`).
    numero_citado: str | None = None
    # Com o reranker por passagens: a passagem do artigo que lhe deu a nota, quando não é o início dele.
    passagem: str | None = None
    avisos: list[str] = field(default_factory=list)
    revogado_por: list[str] = field(default_factory=list)


@dataclass
class Consulta:
    pergunta: str
    data: str
    referencias: refs_mod.Referencias
    resultados: list[Resultado]
    diplomas_citados: list[str] = field(default_factory=list)  # ids encontrados no acervo
    diplomas_em_falta: list[str] = field(default_factory=list)  # citados mas não encontrados
    pesquisa_por: str | None = None  # a consulta reescrita (rag.reescrita), quando difere da pergunta


_TIPOS_UE = {"regulation", "directive", "decision"}


def _numeros_ue(numero: str) -> list[str]:
    """As formas "ano/número" com que um ato da UE pode estar no índice, a partir da citação.

    O índice guarda "1994/631" e "2025/2180"; as perguntas citam "Decisão 94/631" (ano primeiro, com
    dois algarismos), "Regulamento (CE) n.º 195/98" (número primeiro) ou "(UE) 2025/2180" (ano primeiro).
    Devolve a forma citada e as formas ano/número possíveis, com os anos de dois algarismos por extenso."""
    formas = [numero]
    partes = numero.split("/")
    if len(partes) != 2 or not all(p.isdigit() for p in partes):
        return formas

    def ano(texto: str) -> str | None:
        if len(texto) == 4 and 1950 <= int(texto) <= 2099:
            return texto
        if len(texto) == 2:
            return ("19" if int(texto) >= 50 else "20") + texto
        return None

    a, b = partes
    for possivel_ano, num in ((a, b), (b, a)):
        completo = ano(possivel_ano)
        if completo:
            formas.append(f"{completo}/{int(num)}")
    return list(dict.fromkeys(formas))


class Pesquisa:
    def __init__(
        self, caminho: Path | None = None, *, reranker=None, candidatos: int = 100, codigos_candidatos: int = CODIGOS_CANDIDATOS,
        reranker_com_perguntas: bool = False, semantica=None, vigencia_prior: bool | None = None,
    ):
        caminho = caminho or PASTA_INDICE / "indice.sqlite"
        self.con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True, check_same_thread=False)
        metodo = dict(self.con.execute("SELECT chave, valor FROM meta")).get("metodo_termos")
        if metodo != termos_mod.METODO:
            raise RuntimeError(f"O índice foi feito com termos '{metodo}' e a pesquisa usa '{termos_mod.METODO}'; reconstrói o índice.")
        self.con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.vocab USING fts5vocab(main, pedacos_fts, 'row')")
        self.total = self.con.execute("SELECT count(*) FROM pedacos").fetchone()[0]
        self.reranker = reranker
        # Opcional (rag.semantica.Semantica): os artigos mais próximos da pergunta também vão ao reranker.
        self.semantica = semantica
        self.candidatos = candidatos
        self.codigos_candidatos = codigos_candidatos
        self._codigos: dict[str, list[tuple[str, str]]] | None = None
        self._codigos_soltos: dict[str, list[tuple[str, str]]] | None = None
        self._codigo: dict[str, list[tuple[str, str]]] = {}
        self._nomes_do_indice: re.Pattern | None | bool = False  # False: ainda por calcular
        self._principais: list[str] | None = None
        self._documentos: dict[str, dict | None] = {}
        self._jurisprudencia = None
        self._relacoes: dict[str, tuple] = {}
        # Vigência revista (`rag.vigencia`): o aviso vai sempre; o peso no prior só se ligado.
        self.vigencia = vigencia_mod.marcas()
        self.vigencia_prior = vigencia_mod.prior_ligado() if vigencia_prior is None else vigencia_prior
        # Diplomas que só se encontram quando a pergunta os cita (a 2.ª Série, por omissão em
        # `rag.indice`): ficam fora do BM25 em todo o acervo. Índices sem a tabela: nenhum.
        tem_tabela = self.con.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'so_referencia'").fetchone()
        self.so_referencia: set[str] = {i for (i,) in self.con.execute("SELECT id FROM so_referencia")} if tem_tabela else set()
        # Variante do piloto das perguntas por artigo: o reranker também lê as perguntas de leigo do artigo.
        self.perguntas: dict[tuple[str, str], str] = {}
        if reranker_com_perguntas:
            from rag.indice import perguntas_do_indice

            self.perguntas = perguntas_do_indice(self.con)

    # ------------------------------------------------------------------ pedaços e documentos

    _COLUNAS = "p.id, p.documento, d.titulo, p.parte, p.numero, p.epigrafe, p.chave, p.rotulo, p.texto, p.notas, p.desde, p.ate"

    def _pedacos(self, ids: list[int]) -> dict[int, Resultado]:
        if not ids:
            return {}
        marcadores = ",".join("?" * len(ids))
        linhas = self.con.execute(
            f"SELECT {self._COLUNAS} FROM pedacos p JOIN documentos d ON d.id = p.documento WHERE p.id IN ({marcadores})", ids
        )
        return {linha[0]: Resultado(*linha) for linha in linhas}

    def documento(self, id_: str) -> dict | None:
        if id_ in self._documentos:
            return self._documentos[id_]
        linha = self.con.execute(
            "SELECT id, titulo, tipo, numero, data, legal_status, versao, data_consolidacao, com_historico, sumario FROM documentos WHERE id = ?",
            (id_,),
        ).fetchone()
        chaves = ("id", "titulo", "tipo", "numero", "data", "legal_status", "versao", "data_consolidacao", "com_historico", "sumario")
        self._documentos[id_] = dict(zip(chaves, linha, strict=True)) if linha else None
        return self._documentos[id_]

    def relacoes(self, id_: str) -> tuple[tuple[str, str, str, str | None], ...]:
        if id_ not in self._relacoes:
            self._relacoes[id_] = tuple(self.con.execute("SELECT tipo, alvo, alvo_titulo, data FROM relacoes WHERE documento = ?", (id_,)))
        return self._relacoes[id_]

    @staticmethod
    def _em_vigor(desde: str | None, ate: str | None, data: str) -> bool:
        return (desde is None or desde <= data) and (ate is None or ate > data)

    # ------------------------------------------------------------------ referências exatas

    def diplomas(self, tipo: str, numero: str) -> list[str]:
        numeros = _numeros_ue(numero) if tipo in _TIPOS_UE else [numero]
        marcas = ",".join("?" * len(numeros))
        # Na 2.ª Série o DRE escreve o número com sufixo: "81/2002 (2.ª série)", "113/2000 (2.ª série) - AP",
        # "11/2003 - AP". O intervalo [numero + " ", numero + "!") apanha-os e continua a usar o índice da coluna.
        return [linha[0] for linha in self.con.execute(
            f"SELECT id FROM documentos WHERE tipo = ? AND (numero IN ({marcas}) OR (numero >= ? AND numero < ?)) ORDER BY data",
            (tipo, *numeros, f"{numero} ", f"{numero}!"),
        )]

    def codigos(self) -> dict[str, list[tuple[str, str]]]:
        """Nome normalizado de cada anexo (ou diploma) → [(documento, parte)], para resolver "Código do IRS"."""
        if self._codigos is None:
            self._codigos = {}
            for documento, parte in self.con.execute("SELECT DISTINCT documento, parte FROM pedacos WHERE parte LIKE 'Anexo%'"):
                self._codigos.setdefault(refs_mod.nome_normalizado(parte), []).append((documento, parte))
            for documento, sumario in self.con.execute("SELECT id, sumario FROM documentos WHERE sumario LIKE 'Aprova o C_digo%'"):
                m = re.match(r"Aprova o (C[óo]digo [^,.;]+?)(?: e |,|\.|;|$)", sumario)
                if m:
                    self._codigos.setdefault(refs_mod.nome_normalizado(m.group(1)), []).append((documento, ""))
            # A Constituição está no «Decreto de Aprovação da Constituição», sem anexo.
            for (documento,) in self.con.execute("SELECT id FROM documentos WHERE sumario LIKE 'Aprova a Constitui__o da Rep_blica Portuguesa%'"):
                self._codigos.setdefault("constituicao da republica portuguesa", []).append((documento, ""))
        return self._codigos

    def codigos_soltos(self) -> dict[str, list[tuple[str, str]]]:
        """`codigos` pelo nome sem palavras de ligação (`rag.referencias.nome_solto`)."""
        if self._codigos_soltos is None:
            self._codigos_soltos = {}
            for nome, pares in self.codigos().items():
                self._codigos_soltos.setdefault(refs_mod.nome_solto(nome), []).extend(pares)
        return self._codigos_soltos

    def codigos_na_pergunta(self, pergunta: str, citados: list[str]) -> list[str]:
        """Os nomes de códigos do próprio índice que a pergunta cita («Código Cooperativo»), além de `citados`.

        Só os nomes começados por «Código» cujo texto em vigor tem pelo menos `ARTIGOS_NOME_DO_INDICE` artigos e
        não é só pela referência: um nome novo no acervo resolve-se sem mudar `rag.referencias.CODIGOS`."""
        if self._nomes_do_indice is False:
            nomes = []
            for nome in self.codigos():
                if not nome.startswith("codigo ") or len(nome) > 150:
                    continue
                pares = self.codigo(nome)
                if not pares or pares[0][0] in self.so_referencia:
                    continue
                if ((self.documento(pares[0][0]) or {}).get("legal_status") or "") in REVOGADO:
                    continue
                abertos = self.con.execute("SELECT count(*) FROM pedacos WHERE documento = ? AND parte = ? AND ate IS NULL AND numero != ''", pares[0]).fetchone()[0]
                if abertos >= ARTIGOS_NOME_DO_INDICE:
                    nomes.append(nome)
            alternativas = "|".join(re.escape(n) for n in sorted(nomes, key=len, reverse=True))
            self._nomes_do_indice = re.compile(rf"(?<!\w)({alternativas})(?!\w)") if nomes else None
        if self._nomes_do_indice is None:
            return []
        ja = [refs_mod.nome_normalizado(n) for n in citados]
        encontrados: list[str] = []
        for m in self._nomes_do_indice.finditer(refs_mod.texto_comparavel(pergunta)):
            nome = m.group(1)
            if nome not in encontrados and not any(nome in c for c in ja):
                encontrados.append(nome)
        return encontrados

    def codigos_principais(self) -> list[str]:
        """Os diplomas com os códigos e leis gerais grandes em vigor (Trabalho, Civil, IRS, IVA...).

        Uma pergunta de um leigo ("quando é trabalho noturno?") quase nunca cita o código, e o BM25 em todo o
        acervo põe à frente portarias e regulamentos pequenos que repetem as palavras; por isso pesquisa-se
        também só nestes diplomas e os melhores juntam-se aos candidatos do reranker.
        """
        if self._principais is None:
            partes = []
            for nome in self.codigos():
                if _NOME_CODIGO.match(nome):
                    partes += self.codigo(nome)
            self._principais = []
            for documento, parte in dict.fromkeys(partes):
                artigos = self.con.execute("SELECT count(*) FROM pedacos WHERE documento = ? AND parte = ?", (documento, parte)).fetchone()[0]
                # Os da 2.ª Série só pela referência ("Código de Conduta do Município…") não contam.
                if artigos >= CODIGO_GRANDE and documento not in self._principais and documento not in self.so_referencia:
                    self._principais.append(documento)
        return self._principais

    def codigo(self, nome: str) -> list[tuple[str, str]]:
        """Onde está o texto em vigor de um código: o anexo (ou o diploma) com esse nome.

        Há vários anexos com o nome de cada código, sobretudo republicações em leis de alteração
        (que o DRE também consolida). Prefere-se o diploma em vigor, com histórico de versões e com
        mais artigos em vigor nessa parte: o Código Penal no DL 48/95 e não na Lei 59/2007.
        """
        alvo = refs_mod.nome_normalizado(nome)
        if alvo in self._codigo:
            return self._codigo[alvo]
        # «Código de Processo Penal» na pergunta e «Código do Processo Penal» no sumário do DL 78/87.
        candidatos = self.codigos().get(alvo) or self.codigos_soltos().get(refs_mod.nome_solto(nome), [])

        def preferencia(par: tuple[str, str]) -> tuple:
            doc = self.documento(par[0]) or {}
            estado = doc.get("legal_status")
            artigos = self.con.execute("SELECT count(*) FROM pedacos WHERE documento = ? AND parte = ? AND ate IS NULL", par).fetchone()[0]
            return (estado == "in_force", estado == "partially_in_force", bool(doc.get("com_historico")), artigos)

        self._codigo[alvo] = sorted(candidatos, key=preferencia, reverse=True)[:1]
        return self._codigo[alvo]

    # ------------------------------------------------------------------ BM25

    def _consulta_fts(self, pergunta: str) -> str | None:
        vistos: list[str] = []
        for termo in termos_mod.termos(pergunta):
            if termo not in vistos:
                vistos.append(termo)
        # Os termos que aparecem em mais de 20% dos pedaços quase não distinguem e tornam o BM25 lento.
        frequencias = {t: (self.con.execute("SELECT doc FROM vocab WHERE term = ?", (t,)).fetchone() or (0,))[0] for t in vistos}
        uteis = [t for t in vistos if 0 < frequencias[t] < 0.2 * self.total][:MAX_TERMOS]
        return " OR ".join(f'"{t}"' for t in uteis) or None

    def bm25(self, pergunta: str, data: str, *, documentos: list[str] | None = None, limite: int = 100) -> list[tuple[int, float]]:
        """Os melhores pedaços por BM25 em vigor na data, em todo o acervo ou só nos `documentos`."""
        consulta = self._consulta_fts(pergunta)
        if consulta is None:
            return []
        sql = f"SELECT rowid, bm25(pedacos_fts, {PESOS_BM25[0]}, {PESOS_BM25[1]}) AS s FROM pedacos_fts WHERE pedacos_fts MATCH ?"
        if documentos:
            # Os pedaços de um diploma têm ids seguidos: filtrar por intervalo de rowid é rápido no FTS5.
            linhas = []
            for documento in documentos:
                inicio, fim = self.con.execute("SELECT min(id), max(id) FROM pedacos WHERE documento = ?", (documento,)).fetchone()
                if inicio is not None:
                    linhas += self.con.execute(sql + " AND rowid BETWEEN ? AND ? ORDER BY s LIMIT ?", (consulta, inicio, fim, limite * 3)).fetchall()
            linhas.sort(key=lambda x: x[1])
        else:
            linhas = self.con.execute(sql + " ORDER BY s LIMIT ?", (consulta, limite * 10)).fetchall()
        info = self._info([i for i, _ in linhas], data)
        if not documentos and self.so_referencia:
            linhas = [(i, s) for i, s in linhas if info[i][2] not in self.so_referencia]
        pontuacoes = [
            (i, -s * (1.0 if documentos else self._prior(*info[i][2:], pergunta=pergunta))) for i, s in linhas if self._em_vigor(*info[i][:2], data)
        ]
        return sorted(pontuacoes, key=lambda x: -x[1])[:limite]

    def _prior(self, documento: str, parte: str, artigo_revogado: bool, *, pergunta: str = "") -> float:
        """Peso da "lei atual" na pesquisa em todo o acervo: o texto consolidado pelo DRE à frente, os
        diplomas revogados, de vigência desconhecida, os artigos revogados e os anexos de republicação
        (texto de outra data) atrás. Também atrás: o regime de um setor quando a pergunta não fala dele,
        e os regulamentos antigos sem versão consolidada (`rag.ambito`)."""
        doc = self.documento(documento) or {}
        peso = PRIOR_CONSOLIDADO if doc.get("com_historico") else 1.0
        peso *= PRIOR_ESTADO.get(doc.get("legal_status"), 1.0)
        marca = getattr(self, "vigencia", {}).get(documento) or {}
        if getattr(self, "vigencia_prior", False) and marca.get("marca") == "nao_vigora" and doc.get("legal_status") not in REVOGADO:
            peso *= vigencia_mod.PRIOR_NAO_VIGORA
        if artigo_revogado:
            peso *= PRIOR_ARTIGO_REVOGADO
        if "republica" in parte.lower():
            peso *= PRIOR_REPUBLICACAO
        nome_setor = ambito_mod.setor(doc.get("titulo") or "", doc.get("sumario") or "", parte)
        if nome_setor and not ambito_mod.pergunta_fala_do_setor(pergunta, nome_setor):
            peso *= PRIOR_SETOR
        if ambito_mod.antigo_regulamentar(doc):
            peso *= PRIOR_ANTIGO
        return peso

    def _desconto_reranker(self, r: Resultado, pergunta: str) -> float:
        """Quanto se tira à pontuação do reranker de um artigo que a pergunta não cita (`RERANKER_SETOR`…)."""
        if r.nivel >= 2:
            return 0.0
        doc = self.documento(r.documento) or {}
        desconto = 0.0
        nome_setor = ambito_mod.setor(doc.get("titulo") or "", doc.get("sumario") or "", r.parte or "")
        if nome_setor and not ambito_mod.pergunta_fala_do_setor(pergunta, nome_setor):
            desconto += RERANKER_SETOR
        if ambito_mod.antigo_regulamentar(doc):
            desconto += RERANKER_ANTIGO
        return desconto

    def _info(self, ids: list[int], data: str | None = None) -> dict[int, tuple[str | None, str | None, str, str, bool]]:
        """(desde, ate, documento, parte, artigo revogado na data) de cada pedaço."""
        resultado = {}
        for n in range(0, len(ids), 900):
            lote = ids[n : n + 900]
            sql = f"SELECT id, desde, ate, documento, parte, substr(texto, 1, 40), notas FROM pedacos WHERE id IN ({','.join('?' * len(lote))})"
            for i, desde, ate, documento, parte, inicio, notas in self.con.execute(sql, lote):
                resultado[i] = (desde, ate, documento, parte, revogado(inicio, notas or "", data))
        return resultado

    # ------------------------------------------------------------------ pesquisa

    def pesquisar(self, pergunta: str, data: str | None = None, *, k: int = 10) -> Consulta:
        data = data or date.today().isoformat()
        refs = refs_mod.extrair(pergunta)
        citados: list[str] = []
        em_falta: list[str] = []
        for tipo, numero, texto in refs.diplomas:
            ids = [i for i in self.diplomas(tipo, numero) if ((self.documento(i) or {}).get("data") or "") <= data]
            (citados.extend(ids) if ids else em_falta.append(texto))
        # Se a mesma referência deu resultado com outro tipo (p. ex. Regulamento PT e UE), não está em falta.
        em_falta = [t for t in em_falta if not any(t == texto for tipo, numero, texto in refs.diplomas if self.diplomas(tipo, numero))]
        # O DRE tem alguns diplomas em dois registos: fica o principal (`rag.duplicados`).
        citados = list(dict.fromkeys(self._principal(i) for i in citados))
        partes_codigo = [par for nome in refs.codigos for par in self.codigo(nome)]
        # Um código citado que o acervo não tem (o Código Comercial) fica em falta, como um diploma.
        em_falta += [nome for nome in refs.codigos if not self.codigo(nome)]
        for nome in self.codigos_na_pergunta(pergunta, refs.codigos):
            partes_codigo += [par for par in self.codigo(nome) if par not in partes_codigo]

        niveis: dict[int, tuple[int, float, str]] = {}  # id → (nível, pontuação, origem)

        def juntar(ids_pontuacoes, nivel: int, origem: str) -> None:
            for i, s in ids_pontuacoes:
                if i not in niveis or niveis[i][0] < nivel:
                    niveis[i] = (nivel, s, origem)

        # 3. Referência exata ao artigo.
        alvos = [(d, None) for d in citados] + partes_codigo
        seguidos: dict[int, tuple[str, str]] = {}  # artigo do texto em vigor → (diploma citado, número citado)
        if refs.artigos and alvos:
            for documento, parte in alvos:
                for numero in refs.artigos:
                    linhas = self.con.execute(
                        "SELECT id, parte, desde, ate FROM pedacos WHERE documento = ? AND numero = ?", (documento, numero)
                    ).fetchall()
                    linhas = [ln for ln in linhas if self._em_vigor(ln[2], ln[3], data) and (parte is None or ln[1] == parte)]
                    if not linhas and parte is None:
                        # O texto deste diploma já não está em vigor neste registo: responde o que o tem.
                        for i in self._no_texto_em_vigor(documento, numero, data):
                            seguidos.setdefault(i, (documento, numero))
                            juntar([(i, 0.995)], 3, "referência")
                        continue
                    # Sem código citado, o artigo do diploma (parte "") antes do dos anexos.
                    linhas.sort(key=lambda ln: ln[1] != "")
                    juntar([(ln[0], 1.0 - 0.01 * n) for n, ln in enumerate(linhas)], 3, "referência")

        # 2. BM25 dentro dos diplomas e códigos citados.
        documentos_citados = list(dict.fromkeys([d for d, _ in alvos] + [a for d in citados for a in self._atuais(d)]))
        if documentos_citados:
            juntar(self.bm25(pergunta, data, documentos=documentos_citados, limite=self.candidatos), 2, "bm25-citado")

        # 1. BM25 em todo o acervo.
        globais = self.bm25(pergunta, data, limite=self.candidatos)
        juntar(globais, 1, "bm25")

        # 0. BM25 só nos códigos principais: entram no reranker além dos melhores acima.
        dos_codigos: set[int] = set()
        if self.reranker is not None and self.codigos_candidatos:
            principais = [d for d in self.codigos_principais() if d not in documentos_citados]
            for i, s in self.bm25(pergunta, data, documentos=principais, limite=self.codigos_candidatos):
                dos_codigos.add(i)
                if i not in niveis:
                    niveis[i] = (1, s, "bm25-codigos")

        # 0. Pesquisa semântica nos consolidados e códigos (rag.semantica): também só para o reranker.
        semanticos: set[int] = set()
        if self.reranker is not None and self.semantica is not None:
            for i, s in self.semantica.pesquisar(pergunta, excluir=set(niveis)):
                semanticos.add(i)
                niveis[i] = (1, s, "semantica")

        pedacos = self._pedacos(list(niveis))
        resultados: list[Resultado] = []
        for i, (nivel, s, origem) in niveis.items():
            r = pedacos.get(i)
            if r is None or not self._em_vigor(r.desde, r.ate, data):
                continue
            r.nivel, r.pontuacao, r.origem = nivel, s, origem
            if i in seguidos:
                r.redirecionado_de, citado = seguidos[i]
                r.numero_citado = citado if citado != r.numero else None
                resultados.append(r)
            else:
                resultados.append(self._redirecionar(r, data))

        if self.reranker is not None:
            extras = dos_codigos | semanticos
            topo = sorted((r for r in resultados if r.id not in extras), key=lambda r: (-r.nivel, -r.pontuacao))[: self.reranker.maximo]
            topo += [r for r in resultados if r.id in extras]
            if getattr(self.reranker, "passagens", False):
                # Os artigos compridos valem pela melhor passagem, não só pelo início (`Reranker.pontuar_artigos`).
                notas = self.reranker.pontuar_artigos(pergunta, [(self._cabecalho(r), r.texto) for r in topo])
                for r, (s, passagem) in zip(topo, notas, strict=True):
                    r.reranker, r.passagem = s, passagem
            else:
                for r, s in zip(topo, self.reranker.pontuar(pergunta, [self._passagem(r) for r in topo]), strict=True):
                    r.reranker = s
            resultados = topo
            # Um artigo revogado fica atrás dos outros do mesmo nível: numa pergunta sobre a lei em
            # vigor nunca é a resposta (quando o diploma é citado, os dele vêm antes na mesma).
            resultados.sort(
                key=lambda r: (
                    -min(r.nivel, 2),
                    revogado(r.texto, r.notas, data),
                    -((r.reranker if r.reranker is not None else -1e9) - self._desconto_reranker(r, pergunta)),
                )
            )
        else:
            resultados.sort(key=lambda r: (-r.nivel, revogado(r.texto, r.notas, data), -r.pontuacao))

        unicos: list[Resultado] = []
        vistos: set[tuple[str, str]] = set()
        for r in resultados:
            if (r.documento, r.chave) not in vistos:
                vistos.add((r.documento, r.chave))
                unicos.append(r)
            if len(unicos) == k:
                break
        for r in unicos:
            self._avisos(r, data)
        return Consulta(pergunta, data, refs, unicos, citados, em_falta)

    def _cabecalho(self, r: Resultado) -> str:
        """O que o reranker lê antes do texto de um pedaço: o caminho (e as perguntas de leigo, na variante do piloto)."""
        perguntas = self.perguntas.get((r.documento, r.chave)) if r.ate is None else None
        if perguntas:
            return f"{r.rotulo}\nPerguntas: {' '.join(perguntas.splitlines())}"
        return r.rotulo

    def _passagem(self, r: Resultado) -> str:
        """O que o reranker lê de um pedaço: o cabeçalho e o texto."""
        return f"{self._cabecalho(r)}\n{r.texto}"

    # ------------------------------------------------------------------ texto em vigor e avisos

    def _atuais(self, documento: str) -> list[str]:
        """Os registos com o texto em vigor deste (`LIGACOES_AO_ATUAL`)."""
        return list(dict.fromkeys(alvo for tipo, alvo, _, _ in self.relacoes(documento) if tipo in LIGACOES_AO_ATUAL and alvo and alvo != documento))

    def _principal(self, documento: str) -> str:
        """O registo principal de um diploma que o DRE tem duas vezes (`MESMO_DIPLOMA`); senão, o próprio."""
        return next((alvo for tipo, alvo, _, _ in self.relacoes(documento) if tipo == MESMO_DIPLOMA and alvo), documento)

    @staticmethod
    def _epigrafe(texto: str | None) -> str:
        return refs_mod.texto_comparavel(_sem_ligacoes(texto or "")).strip(" .()")

    def _no_texto_em_vigor(self, documento: str, numero: str, data: str) -> list[int]:
        """O artigo `numero` de `documento` no registo que tem o texto em vigor dele (`_atuais`).

        O artigo antigo dá a epígrafe e a parte. Com epígrafe: o artigo do mesmo número e da mesma epígrafe; se a
        numeração mudou, o único com essa epígrafe (o Estatuto da Ordem dos Engenheiros de 1992 e o de 2015). Se o
        do mesmo número tem outra epígrafe e nenhum tem a mesma, nada: é outro artigo. Sem epígrafe (o Código Penal
        de 1982 está em blocos, sem artigos), o do mesmo número, à frente o que tem epígrafe (é o do código, não o
        do diploma que o aprova)."""
        antigos = self.con.execute(
            "SELECT parte, epigrafe FROM pedacos WHERE documento = ? AND numero = ? ORDER BY desde DESC, id DESC", (documento, numero)
        ).fetchall()
        parte, epigrafe = (antigos[0][0], self._epigrafe(antigos[0][1])) if antigos else (None, "")
        if epigrafe in _EPIGRAFES_VAZIAS:
            epigrafe = ""
        for alvo in self._atuais(documento):
            linhas = [
                (i, p, n, self._epigrafe(e))
                for i, p, n, e, desde, ate in self.con.execute("SELECT id, parte, numero, epigrafe, desde, ate FROM pedacos WHERE documento = ? ORDER BY id", (alvo,))
                if n and self._em_vigor(desde, ate, data)
            ]
            mesmo_numero = [ln for ln in linhas if ln[2] == numero]
            if parte is not None:
                # O artigo de um código anexo vai para o anexo do texto em vigor; o do diploma, para o articulado.
                mesmo_numero.sort(key=lambda ln: (bool(ln[1]) != bool(parte), ln[1] != parte))
            if not epigrafe:
                # Sem o artigo antigo (o IVA de 1984 está em blocos), o código está no anexo do texto em vigor.
                mesmo_numero.sort(key=lambda ln: (ln[3] in _EPIGRAFES_VAZIAS, parte is None and not ln[1]))
                if mesmo_numero:
                    return [mesmo_numero[0][0]]
                continue
            iguais = [ln for ln in mesmo_numero if ln[3] == epigrafe]
            if iguais:
                return [iguais[0][0]]
            noutro_numero = {(ln[1], ln[2]): ln[0] for ln in linhas if ln[3] == epigrafe}
            if len(noutro_numero) == 1:
                return list(noutro_numero.values())
            # Epígrafe retocada («Proibição temporária da circulação…» → «… temporária ou permanente…»).
            parecidas = [ln for ln in mesmo_numero if _parecida(ln[3], epigrafe) >= EPIGRAFE_PARECIDA]
            if parecidas:
                return [parecidas[0][0]]
            notas = sorted(((_parecida(ln[3], epigrafe), (ln[1], ln[2]), ln[0]) for ln in linhas), reverse=True)
            if notas and notas[0][0] >= EPIGRAFE_MUITO_PARECIDA and (len(notas) == 1 or notas[1][0] < EPIGRAFE_MUITO_PARECIDA):
                return [notas[0][2]]
            sem_epigrafe = [ln for ln in mesmo_numero if ln[3] in _EPIGRAFES_VAZIAS]
            if sem_epigrafe and len(sem_epigrafe) == len(mesmo_numero):
                return [sem_epigrafe[0][0]]
        return []

    def _redirecionar(self, r: Resultado, data: str) -> Resultado:
        """Troca um artigo de um código republicado pelo mesmo artigo no consolidado com o texto atual."""
        alvos = [alvo for tipo, alvo, _, _ in self.relacoes(r.documento) if tipo == "texto_em_vigor_em"]
        if not alvos or not r.numero:
            return r
        for alvo in alvos:
            linhas = self.con.execute("SELECT id, parte, desde, ate FROM pedacos WHERE documento = ? AND numero = ?", (alvo, r.numero)).fetchall()
            linhas = [ln for ln in linhas if self._em_vigor(ln[2], ln[3], data)]
            # O artigo do código está num anexo do consolidado; o do próprio diploma, na parte "".
            linhas.sort(key=lambda ln: (bool(ln[1]) != bool(r.parte), ln[1] != r.parte))
            if linhas:
                novo = self._pedacos([linhas[0][0]])[linhas[0][0]]
                novo.nivel, novo.pontuacao, novo.origem = r.nivel, r.pontuacao, r.origem
                novo.redirecionado_de = r.documento
                return novo
        return r

    @property
    def jurisprudencia(self):
        """As normas julgadas pelo TC e as interpretadas pelo STJ e pelo STA (`rag.jurisprudencia`), lidas na primeira vez."""
        if self._jurisprudencia is None:
            from rag.jurisprudencia import Jurisprudencia

            self._jurisprudencia = Jurisprudencia()
        return self._jurisprudencia

    def julgamentos(self, r: Resultado) -> list[dict]:
        """Os acórdãos do TC que julgaram este artigo e os do STJ e do STA que o interpretaram (no diploma ou no republicado)."""
        if not r.numero:
            return []
        procurar: list[tuple[str, str | None]] = [(d, r.parte) for d in (r.documento, r.redirecionado_de) if d]
        if r.parte.startswith("Anexo"):
            # O mesmo código noutro diploma (o Código Penal republicado na Lei n.º 59/2007 e o do
            # Decreto-Lei n.º 48/95): os acórdãos ficaram ligados ao que `codigo` escolhe pelo nome.
            procurar += [(documento, None) for documento, _ in self.codigo(refs_mod.nome_normalizado(r.parte))]
        vistos: list[dict] = []
        for documento, parte in dict.fromkeys(procurar):
            for j in self.jurisprudencia.por_artigo(documento, r.numero, parte):
                if j not in vistos:
                    vistos.append(j)
        ordem = self.jurisprudencia._ORDEM
        return sorted(vistos, key=lambda j: (ordem.get(j["sentido"], 9), "".join(chr(0x10FFFF - ord(c)) for c in (j["data"] or ""))))

    def _avisos(self, r: Resultado, data: str) -> None:
        doc = self.documento(r.documento) or {}
        relacoes = self.relacoes(r.documento)
        revogacoes = [(alvo, titulo, quando) for tipo, alvo, titulo, quando in relacoes if tipo == "repealed_by" and (quando or "") <= data]
        estado = doc.get("legal_status")
        if doc.get("versao") == "translation":
            r.avisos.append(AVISO_TRADUCAO)
        if r.redirecionado_de:
            original = self.documento(r.redirecionado_de) or {}
            titulo_original = original.get("titulo", r.redirecionado_de)
            if titulo_original == doc.get("titulo"):
                r.avisos.append(f"Texto do registo consolidado de {doc.get('titulo')} (o DRE tem outro registo do mesmo diploma, com o texto de origem).")
            else:
                r.avisos.append(f"Texto em vigor do diploma republicado ({titulo_original}), no consolidado de {doc.get('titulo')}.")
            if r.numero_citado:
                r.avisos.append(f"O artigo {r.numero_citado} de {titulo_original} é, no texto em vigor, o artigo {r.numero} (a mesma epígrafe; a numeração mudou).")
            if original.get("legal_status") in REVOGADO:
                r.avisos.append(f"{titulo_original} já não está em vigor (segundo o DRE); este é o artigo correspondente do texto em vigor.")
        if estado in REVOGADO or (revogacoes and estado not in ("in_force", "partially_in_force")):
            r.revogado_por = [alvo for alvo, _, _ in revogacoes]
            if revogacoes:
                lista = "; ".join(f"{titulo}" + (f" ({quando})" if quando else "") for _, titulo, quando in revogacoes[:3])
                r.avisos.append(f"Diploma revogado por {lista}: a norma já não está em vigor.")
            else:
                r.avisos.append("Diploma sem vigência (revogado ou caducado, segundo o DRE).")
        elif estado == "unknown":
            r.avisos.append("Vigência do diploma desconhecida.")
        elif r.documento in getattr(self, "vigencia", {}):
            r.avisos.append(vigencia_mod.aviso(self.vigencia[r.documento]))
        if revogado(r.texto, r.notas, data):
            nota = next((n for n in r.notas.splitlines() if n.strip().lower().startswith("revogad")), "")
            r.avisos.append(f"Artigo revogado ({_sem_ligacoes(nota)})." if nota else "Artigo revogado.")
        elif por_produzir := revogacao_por_produzir_efeitos(r.notas or "", data):
            # A revogação já foi publicada mas ainda não produz efeitos: o artigo está em vigor, com data para acabar.
            r.avisos.append(f"Em vigor até à véspera de {por_produzir[0]}, data em que a revogação produz efeitos ({_sem_ligacoes(por_produzir[1])}).")
        if r.ate is not None:
            r.avisos.append(f"Redação em vigor de {r.desde} a {r.ate}, não a atual.")
        alteracoes = [(titulo, quando) for tipo, _, titulo, quando in relacoes if tipo == "amended_by" and (quando or "") <= data]
        if doc.get("versao") != "consolidated" and not doc.get("com_historico") and alteracoes and not r.redirecionado_de and not r.revogado_por:
            titulos = list(dict.fromkeys(t for t, _ in alteracoes))
            mais = f" e mais {len(titulos) - 3}" if len(titulos) > 3 else ""
            r.avisos.append(f"Texto original; alterado por {', '.join(titulos[:3])}{mais}, sem versão consolidada no acervo.")
        from rag.jurisprudencia import aviso_declaracao

        for j in self.julgamentos(r):
            if j["sentido"] == "declara_fog" and (j["data"] or "") <= data:
                r.avisos.append(aviso_declaracao(j, r.desde))
