"""Pesquisa no índice por artigo.

Ordem dos candidatos (`nivel`, do mais forte para o mais fraco):

3. referência exata: o artigo citado ("artigo 78.º-B") no diploma ou código citado;
2. BM25 dentro dos diplomas ou códigos citados na pergunta;
1. BM25 em todo o acervo.

Dentro de cada nível, o reranker (se houver: cross-encoder ou embeddings, ver `rag.modelos`)
reordena os primeiros candidatos. Só entram pedaços cujo texto
estava em vigor na data da pergunta (`desde <= data < ate`). Um código republicado
(`texto_em_vigor_em`, p. ex. o Código do IRS do DL 442-A/88) é trocado pelo mesmo artigo
no consolidado que tem o texto atual (a Lei n.º 82-E/2014).
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from rag import referencias as refs_mod
from rag import texto as termos_mod
from rag.fontes import PASTA_INDICE


PESOS_BM25 = (2.0, 1.0)  # cabeçalho (diploma, sumário, anexo, epígrafe), texto
MAX_TERMOS = 24
REVOGADO = ("repealed", "not_in_force")


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


class Pesquisa:
    def __init__(self, caminho: Path | None = None, *, reranker=None, candidatos: int = 100):
        caminho = caminho or PASTA_INDICE / "indice.sqlite"
        self.con = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True, check_same_thread=False)
        metodo = dict(self.con.execute("SELECT chave, valor FROM meta")).get("metodo_termos")
        if metodo != termos_mod.METODO:
            raise RuntimeError(f"O índice foi feito com termos '{metodo}' e a pesquisa usa '{termos_mod.METODO}'; reconstrói o índice.")
        self.con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS temp.vocab USING fts5vocab(main, pedacos_fts, 'row')")
        self.total = self.con.execute("SELECT count(*) FROM pedacos").fetchone()[0]
        self.reranker = reranker
        self.candidatos = candidatos
        self._codigos: dict[str, list[tuple[str, str]]] | None = None
        self._documentos: dict[str, dict | None] = {}
        self._relacoes: dict[str, tuple] = {}

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
            "SELECT id, titulo, tipo, numero, data, legal_status, versao, data_consolidacao, com_historico FROM documentos WHERE id = ?", (id_,)
        ).fetchone()
        chaves = ("id", "titulo", "tipo", "numero", "data", "legal_status", "versao", "data_consolidacao", "com_historico")
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
        return [linha[0] for linha in self.con.execute("SELECT id FROM documentos WHERE tipo = ? AND numero = ? ORDER BY data", (tipo, numero))]

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
        return self._codigos

    def codigo(self, nome: str) -> list[tuple[str, str]]:
        """Onde está o texto em vigor de um código: o anexo (ou o diploma) com esse nome.

        Há vários anexos com o nome de cada código, sobretudo republicações em leis de alteração
        (que o DRE também consolida). Prefere-se o diploma em vigor, com histórico de versões e com
        mais artigos em vigor nessa parte: o Código Penal no DL 48/95 e não na Lei 59/2007.
        """
        alvo = refs_mod.nome_normalizado(nome)
        candidatos = self.codigos().get(alvo, [])

        def preferencia(par: tuple[str, str]) -> tuple:
            doc = self.documento(par[0]) or {}
            estado = doc.get("legal_status")
            artigos = self.con.execute("SELECT count(*) FROM pedacos WHERE documento = ? AND parte = ? AND ate IS NULL", par).fetchone()[0]
            return (estado == "in_force", estado == "partially_in_force", bool(doc.get("com_historico")), artigos)

        return sorted(candidatos, key=preferencia, reverse=True)[:1]

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
        datas = self._datas([i for i, _ in linhas])
        return [(i, -s) for i, s in linhas if self._em_vigor(*datas[i], data)][:limite]

    def _datas(self, ids: list[int]) -> dict[int, tuple[str | None, str | None]]:
        resultado: dict[int, tuple[str | None, str | None]] = {}
        for n in range(0, len(ids), 900):
            lote = ids[n : n + 900]
            for i, desde, ate in self.con.execute(f"SELECT id, desde, ate FROM pedacos WHERE id IN ({','.join('?' * len(lote))})", lote):
                resultado[i] = (desde, ate)
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
        partes_codigo = [par for nome in refs.codigos for par in self.codigo(nome)]

        niveis: dict[int, tuple[int, float, str]] = {}  # id → (nível, pontuação, origem)

        def juntar(ids_pontuacoes, nivel: int, origem: str) -> None:
            for i, s in ids_pontuacoes:
                if i not in niveis or niveis[i][0] < nivel:
                    niveis[i] = (nivel, s, origem)

        # 3. Referência exata ao artigo.
        alvos = [(d, None) for d in citados] + partes_codigo
        if refs.artigos and alvos:
            for documento, parte in alvos:
                for numero in refs.artigos:
                    linhas = self.con.execute(
                        "SELECT id, parte, desde, ate FROM pedacos WHERE documento = ? AND numero = ?", (documento, numero)
                    ).fetchall()
                    linhas = [ln for ln in linhas if self._em_vigor(ln[2], ln[3], data) and (parte is None or ln[1] == parte)]
                    # Sem código citado, o artigo do diploma (parte "") antes do dos anexos.
                    linhas.sort(key=lambda ln: ln[1] != "")
                    juntar([(ln[0], 1.0 - 0.01 * n) for n, ln in enumerate(linhas)], 3, "referência")

        # 2. BM25 dentro dos diplomas e códigos citados.
        documentos_citados = list(dict.fromkeys([d for d, _ in alvos]))
        if documentos_citados:
            juntar(self.bm25(pergunta, data, documentos=documentos_citados, limite=self.candidatos), 2, "bm25-citado")

        # 1. BM25 em todo o acervo.
        globais = self.bm25(pergunta, data, limite=self.candidatos)
        juntar(globais, 1, "bm25")

        pedacos = self._pedacos(list(niveis))
        resultados: list[Resultado] = []
        for i, (nivel, s, origem) in niveis.items():
            r = pedacos.get(i)
            if r is None or not self._em_vigor(r.desde, r.ate, data):
                continue
            r.nivel, r.pontuacao, r.origem = nivel, s, origem
            resultados.append(self._redirecionar(r, data))

        if self.reranker is not None:
            topo = sorted(resultados, key=lambda r: (-r.nivel, -r.pontuacao))[: self.reranker.maximo]
            for r, s in zip(topo, self.reranker.pontuar(pergunta, [f"{r.rotulo}\n{r.texto}" for r in topo]), strict=True):
                r.reranker = s
            resultados = topo
            resultados.sort(key=lambda r: (-r.nivel, -(r.reranker if r.reranker is not None else -1e9)))
        else:
            resultados.sort(key=lambda r: (-r.nivel, -r.pontuacao))

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

    # ------------------------------------------------------------------ texto em vigor e avisos

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

    def _avisos(self, r: Resultado, data: str) -> None:
        doc = self.documento(r.documento) or {}
        relacoes = self.relacoes(r.documento)
        revogacoes = [(alvo, titulo, quando) for tipo, alvo, titulo, quando in relacoes if tipo == "repealed_by" and (quando or "") <= data]
        estado = doc.get("legal_status")
        if r.redirecionado_de:
            original = self.documento(r.redirecionado_de) or {}
            r.avisos.append(f"Texto em vigor do diploma republicado ({original.get('titulo', r.redirecionado_de)}), no consolidado de {doc.get('titulo')}.")
        if estado in REVOGADO or (revogacoes and estado not in ("in_force", "partially_in_force")):
            r.revogado_por = [alvo for alvo, _, _ in revogacoes]
            if revogacoes:
                lista = "; ".join(f"{titulo}" + (f" ({quando})" if quando else "") for _, titulo, quando in revogacoes[:3])
                r.avisos.append(f"Diploma revogado por {lista}: a norma já não está em vigor.")
            else:
                r.avisos.append("Diploma sem vigência (revogado ou caducado, segundo o DRE).")
        elif estado == "unknown":
            r.avisos.append("Vigência do diploma desconhecida.")
        if re.match(r"^\(?\s*revogad[oa]", r.texto, re.I) or any(n.lower().startswith("revogado") for n in r.notas.splitlines()):
            r.avisos.append("Artigo revogado.")
        if r.ate is not None:
            r.avisos.append(f"Redação em vigor de {r.desde} a {r.ate}, não a atual.")
        alteracoes = [(titulo, quando) for tipo, _, titulo, quando in relacoes if tipo == "amended_by" and (quando or "") <= data]
        if doc.get("versao") != "consolidated" and not doc.get("com_historico") and alteracoes and not r.redirecionado_de and not r.revogado_por:
            titulos = list(dict.fromkeys(t for t, _ in alteracoes))
            mais = f" e mais {len(titulos) - 3}" if len(titulos) > 3 else ""
            r.avisos.append(f"Texto original; alterado por {', '.join(titulos[:3])}{mais}, sem versão consolidada no acervo.")
