"""Servidor MCP do leis-portugal: liga o acervo ao Claude, ao Cursor ou a outro cliente MCP, sem dependências.

Corre sobre o índice de pesquisa (SQLite com FTS5, um pedaço por artigo), o mesmo que a aplicação descarrega do
Hugging Face. Não precisa de clonar o repositório nem de chave de IA: o LLM é o do cliente.

    python -m rag.dados descarregar --pasta ~/leis-portugal-indice   # uma vez (cerca de 2 GB comprimidos)
    RAG_INDICE=~/leis-portugal-indice python mcp/servidor.py          # fala MCP por stdin/stdout

Ferramentas:
- `pesquisar`: os artigos mais próximos de uma pergunta ou consulta (BM25; com `reranker` se o extra `rag` estiver
  instalado), com o rótulo, o texto e os avisos de vigência (revogado, redação antiga, texto original);
- `ler_artigo`: o texto de um artigo de um diploma, com as notas e as datas da redação;
- `diploma`: os metadados de um diploma pelo título ou número («Lei n.º 7/2009», «Código do Trabalho»);
- `relacoes`: o que um diploma altera, revoga ou transpõe, e o que o altera;
- `contar_prazo`: o fim de um prazo com as regras da lei (feriados, férias judiciais, dilação), de `rag/prazos.py`.

Transporte stdio do MCP: uma mensagem JSON-RPC 2.0 por linha. Não é aconselhamento jurídico, e o texto deve
confirmar-se na fonte oficial (o `official_url` de cada diploma).
"""

from __future__ import annotations

import json
import sys
import traceback
from datetime import date
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

VERSAO_PROTOCOLO = "2025-06-18"
MAXIMO_TEXTO = 4000
AVISO = ("Texto do acervo leis-portugal, não oficial: confirma na fonte oficial (Diário da República, EUR-Lex) antes de "
         "o usar num contexto jurídico. Não é aconselhamento jurídico.")

# O enquadramento para o LLM do cliente: a consulta jurídica (interpretar e aplicar normas ao caso de quem pede) é
# competência de advogados e solicitadores (Lei n.º 10/2024, arts. 4.º e 6.º). Quem não é deve receber informação.
INSTRUCOES = (
    "Legislação portuguesa e da UE do acervo leis-portugal. Cita sempre o diploma e o artigo, respeita os avisos de "
    "vigência e lembra que o texto deve confirmar-se na fonte oficial. Quem pergunta pode não ser advogado: nesse caso "
    "explica o que a lei diz e de que factos depende, sem dizer o que a pessoa deve fazer no caso dela nem prever o "
    "resultado, e acaba a indicar um advogado ou solicitador e a proteção jurídica pedida no sítio da Segurança Social "
    "(Lei n.º 34/2004, art. 22.º). Aplicar a lei ao caso concreto é consulta jurídica, reservada a advogados e "
    "solicitadores (Lei n.º 10/2024): só o faças como apoio a quem disser que é advogado ou solicitador, e diz que não "
    "substitui o juízo profissional. Não é aconselhamento jurídico."
)

_pesquisa = None


def pesquisa():
    """A pesquisa sobre o índice, aberta uma vez (com o reranker, se estiver instalado e RAG_RERANKER não for 0)."""
    global _pesquisa
    if _pesquisa is None:
        import os

        from rag import texto
        from rag.pesquisa import Pesquisa

        if texto.METODO != "snowball-pt-grafia":
            raise RuntimeError("Falta o radical Snowball com que o índice foi feito: pip install 'leis-portugal[mcp]' "
                               "(ou pip install py-rust-stemmers).")

        reranker = None
        if os.environ.get("RAG_RERANKER", "1") != "0":
            try:
                from rag.modelos import Reranker

                reranker = Reranker("cruzado")
            except Exception:  # sem o extra `rag` (torch, transformers): fica só o BM25
                reranker = None
        _pesquisa = Pesquisa(reranker=reranker)
    return _pesquisa


def _cortar(texto: str, maximo: int = MAXIMO_TEXTO) -> str:
    return texto if len(texto) <= maximo else texto[:maximo] + " […]"


def t_pesquisar(pergunta: str, data: str | None = None, k: int = 8) -> dict:
    k = max(1, min(int(k), 20))
    c = pesquisa().pesquisar(pergunta, data or date.today().isoformat(), k=k)
    return {
        "data_referencia": c.data,
        "diplomas_citados_em_falta": c.diplomas_em_falta,
        "artigos": [{"documento": r.documento, "titulo": r.titulo, "artigo": r.chave, "rotulo": r.rotulo,
                     "nota_reranker": round(r.reranker, 2) if r.reranker is not None else None,
                     "avisos": r.avisos, "texto": _cortar(r.texto, 1500)} for r in c.resultados[:k]],
        "aviso": AVISO,
    }


def _documento(documento: str) -> dict | None:
    return pesquisa().documento(documento)


def t_ler_artigo(documento: str, artigo: str) -> dict:
    con = pesquisa().con
    numero = artigo.strip()
    linhas = con.execute(
        "SELECT chave, rotulo, texto, notas, desde, ate FROM pedacos WHERE documento = ? AND (chave = ? OR numero = ? OR numero = ?) "
        "ORDER BY ordem", (documento, numero, numero, numero.rstrip("º.° ") + ".º")).fetchall()
    if not linhas:
        return {"erro": f"Não encontrei o artigo {artigo} em {documento}. Usa `diploma` para ver o id e `pesquisar` para o artigo."}
    return {"documento": _documento(documento), "aviso": AVISO, "redacoes": [
        {"artigo": ch, "rotulo": rot, "texto": _cortar(tx), "notas": _cortar(no or "", 1500), "desde": de, "ate": ate}
        for ch, rot, tx, no, de, ate in linhas]}


def t_diploma(referencia: str, limite: int = 5) -> dict:
    p = pesquisa()
    refs = __import__("rag.referencias", fromlist=["extrair"]).extrair(referencia)
    ids: list[str] = []
    for tipo, numero, _ in refs.diplomas:
        ids += p.diplomas(tipo, numero)
    for nome in refs.codigos:
        ids += [i for i, _ in p.codigo(nome)]
    if not ids:
        ids = [i for (i,) in p.con.execute("SELECT id FROM documentos WHERE titulo LIKE ? ORDER BY data DESC LIMIT ?",
                                           (f"%{referencia.strip()}%", int(limite)))]
    docs = [d for d in dict.fromkeys(ids) if d][: int(limite)]
    saida = []
    for i in docs:
        d = dict(p.documento(i) or {"id": i})
        d["artigos"] = p.con.execute("SELECT count(*) FROM pedacos WHERE documento = ?", (i,)).fetchone()[0]
        saida.append(d)
    return {"diplomas": saida} if saida else {"erro": f"Não encontrei «{referencia}» no índice."}


def t_relacoes(documento: str, limite: int = 50) -> dict:
    con = pesquisa().con
    de = con.execute("SELECT tipo, alvo, alvo_titulo, data FROM relacoes WHERE documento = ? ORDER BY data LIMIT ?", (documento, int(limite))).fetchall()
    para = con.execute("SELECT documento, tipo, data FROM relacoes WHERE alvo = ? ORDER BY data LIMIT ?", (documento, int(limite))).fetchall()
    titulo = {i: (pesquisa().documento(i) or {}).get("titulo") for i, _, _ in para}
    return {"documento": _documento(documento),
            "este_diploma": [{"tipo": t, "alvo": a, "titulo": ti, "data": d} for t, a, ti, d in de],
            "sobre_este_diploma": [{"documento": o, "titulo": titulo.get(o), "tipo": t, "data": d} for o, t, d in para]}


def t_contar_prazo(inicio: str, quantidade: int, regime: str, unidade: str = "dias", dilacao: int = 0, data_referencia: str | None = None) -> dict:
    from rag import prazos

    c = prazos.de_json({"inicio": inicio, "quantidade": quantidade, "unidade": unidade, "regime": regime, "dilacao": dilacao})
    if c is None:
        return {"erro": f"Conta inválida. inicio AAAA-MM-DD, quantidade > 0, unidade em {list(prazos.UNIDADES)}, regime em {list(prazos.REGIMES)}."}
    r = prazos.contar(c)
    ref = date.fromisoformat(data_referencia) if data_referencia else date.today()
    return {"fim": r.fim.isoformat(), "ja_passou": r.passou(ref), "data_referencia": ref.isoformat(), "passos": r.passos, "aviso": prazos.AVISO}


FERRAMENTAS = {
    "pesquisar": (t_pesquisar, "Procura na legislação portuguesa e da UE os artigos que respondem a uma pergunta ou consulta, com os avisos de vigência.", {
        "pergunta": {"type": "string", "description": "A pergunta ou uma consulta no vocabulário da lei; citar o diploma ou o código ajuda."},
        "data": {"type": "string", "description": "Data de referência AAAA-MM-DD (por omissão, hoje): o texto em vigor nessa data."},
        "k": {"type": "integer", "description": "Quantos artigos (1 a 20, por omissão 8)."}}, ["pergunta"]),
    "ler_artigo": (t_ler_artigo, "O texto de um artigo de um diploma, com as notas e as datas de cada redação.", {
        "documento": {"type": "string", "description": "O id do diploma (p. ex. pt:dre:602073:por), de `diploma` ou `pesquisar`."},
        "artigo": {"type": "string", "description": "O número (p. ex. 351.º) ou a chave dada por `pesquisar`."}}, ["documento", "artigo"]),
    "diploma": (t_diploma, "Os metadados de um diploma (id, título, tipo, data, estado de vigência) pelo número ou nome.", {
        "referencia": {"type": "string", "description": "P. ex. «Lei n.º 7/2009», «Decreto-Lei n.º 47344», «Código do Trabalho»."},
        "limite": {"type": "integer"}}, ["referencia"]),
    "relacoes": (t_relacoes, "O que um diploma altera, revoga ou transpõe, e os diplomas que o alteram ou revogam.", {
        "documento": {"type": "string"}, "limite": {"type": "integer"}}, ["documento"]),
    "contar_prazo": (t_contar_prazo, "O fim de um prazo legal com as regras portuguesas: CC 279.º e 296.º (civil), CPC 138.º e 142.º "
                     "(processual, férias judiciais, dilação), CPA 87.º (dias úteis), feriados do CT 234.º.", {
        "inicio": {"type": "string", "description": "O dia do evento, AAAA-MM-DD (não conta)."},
        "quantidade": {"type": "integer"},
        "unidade": {"type": "string", "enum": ["dias", "semanas", "meses", "anos"]},
        "regime": {"type": "string", "enum": ["civil", "civil_em_juizo", "processual", "processual_urgente", "uteis"]},
        "dilacao": {"type": "integer", "description": "Dias de dilação contados com o prazo (CPC 142.º)."},
        "data_referencia": {"type": "string", "description": "Para dizer se já passou (por omissão, hoje)."}},
        ["inicio", "quantidade", "regime"]),
}


def lista_ferramentas() -> list[dict]:
    return [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": p, "required": r}}
            for n, (_, d, p, r) in FERRAMENTAS.items()]


def responder(pedido: dict) -> dict | None:
    """A resposta a uma mensagem JSON-RPC; `None` para notificações."""
    metodo, id_ = pedido.get("method"), pedido.get("id")
    if id_ is None:
        return None
    try:
        if metodo == "initialize":
            resultado = {"protocolVersion": VERSAO_PROTOCOLO, "capabilities": {"tools": {}},
                         "serverInfo": {"name": "leis-portugal", "version": "0.1.0"},
                         "instructions": INSTRUCOES}
        elif metodo == "ping":
            resultado = {}
        elif metodo == "tools/list":
            resultado = {"tools": lista_ferramentas()}
        elif metodo == "tools/call":
            nome = (pedido.get("params") or {}).get("name")
            argumentos = (pedido.get("params") or {}).get("arguments") or {}
            if nome not in FERRAMENTAS:
                return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32602, "message": f"Ferramenta desconhecida: {nome}"}}
            try:
                dados = FERRAMENTAS[nome][0](**argumentos)
                erro = "erro" in dados
            except TypeError as e:
                dados, erro = {"erro": f"Argumentos inválidos: {e}"}, True
            resultado = {"content": [{"type": "text", "text": json.dumps(dados, ensure_ascii=False, indent=1)}], "isError": erro}
        else:
            return {"jsonrpc": "2.0", "id": id_, "error": {"code": -32601, "message": f"Método desconhecido: {metodo}"}}
    except Exception as e:  # o servidor não cai por uma ferramenta: o erro vai ao cliente
        traceback.print_exc(file=sys.stderr)
        return {"jsonrpc": "2.0", "id": id_, "result": {"content": [{"type": "text", "text": f"Erro: {e}"}], "isError": True}}
    return {"jsonrpc": "2.0", "id": id_, "result": resultado}


def main() -> int:
    for linha in sys.stdin:
        if not linha.strip():
            continue
        try:
            pedido = json.loads(linha)
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON inválido"}}), flush=True)
            continue
        resposta = responder(pedido)
        if resposta is not None:
            print(json.dumps(resposta, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
