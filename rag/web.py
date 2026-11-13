"""A página local para fazer perguntas: `./perguntar --web`, ou dentro da aplicação.

    PYTHONPATH=src python -m rag.web [--porta N] [--sem-browser]

Um servidor só da biblioteca padrão, em 127.0.0.1, serve a página (`rag/pagina/`) e quatro pedidos:

- `GET  /api/estado`: a IA e o modelo escolhidos, se há chave, se os dados estão prontos;
- `POST /api/configurar`: valida a chave sem gastar créditos (`rag.provedores.validar`) e, se for
  válida, guarda-a no cofre do sistema (`rag.definicoes`);
- `POST /api/perguntar`: pesquisa, reescreve e responde como o `rag.perguntar`;
- `POST /api/avaliar`: grava a pergunta, a resposta e "certo / errado / o que esperavas" no mesmo
  ficheiro que o `rag.perguntar` (`perguntas-testadas.jsonl`).

Segurança: só aceita ligações locais com o `Host` deste servidor (contra DNS rebinding) e cada
pedido à API leva um código aleatório que só a página servida conhece (contra outros sites abertos
no browser a pedirem respostas, que gastariam créditos, ou a mudarem a chave).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import secrets
import sys
import threading
import uuid
import webbrowser
from collections import Counter
from dataclasses import asdict
from datetime import date
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from rag import dados, definicoes, jurisprudencia, provedores, reescrita
from rag.fontes import PASTA_INDICE
from rag.resposta import LIMIAR_COM_LLM, LIMIAR_PADRAO, llm_disponivel, responder


PAGINA = Path(__file__).resolve().parent / "pagina"
TIPOS = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".png": "image/png", ".svg": "image/svg+xml"}
MAXIMO_PEDIDO = 64 * 1024


class Servico:
    """A pesquisa (carregada uma vez, em segundo plano) e as respostas ainda por avaliar."""

    def __init__(self, indice: Path | None = None, reranker: str | None = None):
        self.indice = indice
        self.tipo_reranker = reranker or ("cruzado" if importlib.util.find_spec("fastembed") else "nenhum")
        self.pesquisa = None
        self.estado = "a preparar"
        self.erro = ""
        self.pendentes: dict[str, tuple] = {}
        self._trinco = threading.Lock()
        self.progresso = dados.Progresso()
        self.pasta_dados = (indice.parent if indice else PASTA_INDICE)

    def carregar(self) -> None:
        try:
            from rag.pesquisa import Pesquisa

            reranker = None
            if self.tipo_reranker != "nenhum":
                from rag.modelos import Reranker

                reranker = Reranker(self.tipo_reranker)
            self.pesquisa = Pesquisa(self.indice, reranker=reranker)
            self.estado = "pronto"
        except Exception as e:  # sem índice, sem modelos, índice de outra versão…
            self.estado, self.erro = "sem dados", str(e)

    def info(self) -> dict:
        nome = provedores.provedor()
        return {
            "estado": self.estado,
            "erro": self.erro,
            "provedor": nome,
            "modelo": provedores.modelo(),
            "descricao": provedores.descricao(),
            "com_chave": provedores.disponivel(),
            "aviso_medicao": provedores.aviso_medicao(),
            "medido": {"provedor": provedores.MEDIDO[0], "modelo": provedores.MEDIDO[1]},
            "cofre": definicoes.cofre_disponivel(),
            "reranker": self.tipo_reranker != "nenhum",
            "configurado": bool(definicoes.ler().get("provedor")) or provedores.disponivel(),
            "dados": {
                "pode_descarregar": bool(dados.url_manifesto()),
                "versao": dados.versao_local(self.pasta_dados).get("versao"),
                "progresso": asdict(self.progresso),
            },
            "provedores": {
                k: {c: v[c] for c in ("nome", "modelo", "modelos", "chaves", "conta")} for k, v in provedores.PROVEDORES.items()
            },
        }

    def perguntar(self, pergunta: str, data: str) -> dict:
        if self.pesquisa is None:
            raise RuntimeError("Os dados ainda não estão prontos." if self.estado == "a preparar" else f"Sem dados para pesquisar: {self.erro}")
        usar_llm = llm_disponivel()
        cruzado = self.tipo_reranker == "cruzado"
        limiar = (LIMIAR_COM_LLM if usar_llm else LIMIAR_PADRAO) if cruzado else None
        with self._trinco:  # o reranker e a ligação ao índice servem uma pergunta de cada vez
            if usar_llm:
                consulta = reescrita.pesquisar(self.pesquisa, pergunta, data, k=10)
            else:
                consulta = self.pesquisa.pesquisar(pergunta, data, k=10)
            resposta = responder(consulta, limiar=limiar, usar_llm=usar_llm, pesquisa=self.pesquisa)
        id_ = uuid.uuid4().hex
        self.pendentes[id_] = (consulta, resposta)
        return serializar(id_, consulta, resposta)

    def avaliar(self, id_: str, anotacao: dict) -> bool:
        from rag.perguntar import registar

        par = self.pendentes.pop(id_, None)
        if par is None:
            return False
        registar(*par, anotacao)
        return True

    def descarregar_dados(self) -> None:
        """Descarrega (ou atualiza) o índice em segundo plano e volta a carregar a pesquisa."""
        if self.progresso.fase in ("a descarregar", "a verificar", "a descomprimir"):
            return

        def fechar():
            with self._trinco:
                if self.pesquisa is not None:
                    self.pesquisa.con.close()
                    self.pesquisa, self.estado = None, "a preparar"

        def correr():
            try:
                dados.descarregar(self.pasta_dados, self.progresso, antes_de_trocar=fechar)
                self.carregar()
            except Exception as e:
                self.progresso.fase, self.progresso.mensagem = "erro", str(e)

        self.progresso = dados.Progresso(fase="a descarregar")
        threading.Thread(target=correr, daemon=True).start()

    def gravar_pendentes(self) -> None:
        for id_ in list(self.pendentes):
            self.avaliar(id_, {})


def serializar(id_: str, consulta, resposta) -> dict:
    citados = {r.id for r in resposta.citacoes}
    juris = []
    for j in resposta.jurisprudencia:
        juris.append(
            {
                "artigo": j["artigo"],
                "numero": j["numero"],
                "data": jurisprudencia.data_pt(j["data"]),
                "sentido": jurisprudencia.ROTULOS.get(j["sentido"], j["sentido"]),
                "url": j.get("url"),
                "mostrar": j["mostrar"],
            }
        )
    resto = Counter(j["sentido"] for j in juris if not j["mostrar"])
    return {
        "id": id_,
        "pergunta": consulta.pergunta,
        "data": consulta.data,
        "pesquisa_por": consulta.pesquisa_por,
        "responde": resposta.responde,
        "com_llm": resposta.com_llm,
        "texto": resposta.texto,
        "motivo": resposta.motivo,
        "erro": resposta.erro,
        "modelo": resposta.modelo,
        "aviso_modelo": resposta.aviso_modelo,
        "avisos": resposta.avisos,
        "em_falta": consulta.diplomas_em_falta,
        "citacoes": [{"rotulo": r.rotulo, "texto": r.texto[:1500]} for r in resposta.citacoes],
        "jurisprudencia": [j for j in juris if j["mostrar"]],
        "jurisprudencia_resto": [{"sentido": s, "n": n} for s, n in resto.most_common()],
        "outros": [{"rotulo": r.rotulo, "texto": r.texto[:600]} for r in consulta.resultados[:6] if r.id not in citados],
    }


def criar_tratador(servico: Servico, codigo: str) -> type[BaseHTTPRequestHandler]:
    """A classe que trata cada pedido; `codigo` é o código aleatório que a página leva."""

    class Pedido(BaseHTTPRequestHandler):
        server_version = "LeisDePortugal"

        def log_message(self, formato, *args):  # silencioso: só os erros interessam
            pass

        def _host_valido(self) -> bool:
            porta_atual = self.server.server_address[1]
            return self.headers.get("Host", "") in (f"127.0.0.1:{porta_atual}", f"localhost:{porta_atual}")

        def _responder(self, estado: int, corpo: bytes, tipo: str) -> None:
            self.send_response(estado)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(corpo)

        def _json(self, dados: dict, estado: int = 200) -> None:
            self._responder(estado, json.dumps(dados, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if not self._host_valido():
                return self._responder(HTTPStatus.FORBIDDEN, b"", "text/plain")
            caminho = self.path.split("?", 1)[0]
            if caminho == "/api/estado":
                if self.headers.get("X-Codigo") != codigo:
                    return self._json({"erro": "sem autorização"}, HTTPStatus.FORBIDDEN)
                return self._json(servico.info())
            nome = "index.html" if caminho in ("/", "/index.html") else caminho.lstrip("/")
            ficheiro = (PAGINA / nome).resolve()
            if PAGINA.resolve() not in ficheiro.parents or not ficheiro.is_file():
                return self._responder(HTTPStatus.NOT_FOUND, "Não encontrado".encode(), "text/plain; charset=utf-8")
            corpo = ficheiro.read_bytes()
            if nome == "index.html":
                corpo = corpo.replace(b"__CODIGO__", codigo.encode())
            self._responder(HTTPStatus.OK, corpo, TIPOS.get(ficheiro.suffix, "application/octet-stream"))

        def do_POST(self):
            if not self._host_valido() or self.headers.get("X-Codigo") != codigo:
                return self._json({"erro": "sem autorização"}, HTTPStatus.FORBIDDEN)
            tamanho = int(self.headers.get("Content-Length") or 0)
            if tamanho > MAXIMO_PEDIDO:
                return self._json({"erro": "pedido grande demais"}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            try:
                dados = json.loads(self.rfile.read(tamanho) or b"{}")
            except ValueError:
                return self._json({"erro": "pedido inválido"}, HTTPStatus.BAD_REQUEST)
            try:
                if self.path == "/api/perguntar":
                    pergunta = str(dados.get("pergunta", "")).strip()[:2000]
                    if not pergunta:
                        return self._json({"erro": "Escreve uma pergunta."}, HTTPStatus.BAD_REQUEST)
                    data = str(dados.get("data") or date.today().isoformat())[:10]
                    return self._json(servico.perguntar(pergunta, data))
                if self.path == "/api/avaliar":
                    anotacao = {}
                    if dados.get("certo") is not None:
                        anotacao["certo"] = bool(dados["certo"])
                    if dados.get("esperado"):
                        anotacao["esperado"] = str(dados["esperado"])[:2000]
                    return self._json({"gravado": servico.avaliar(str(dados.get("id", "")), anotacao)})
                if self.path == "/api/configurar":
                    nome = str(dados.get("provedor", ""))
                    modelo = str(dados.get("modelo") or provedores.PROVEDORES.get(nome, {}).get("modelo", ""))
                    chave = str(dados.get("chave", "")).strip()
                    if not chave:
                        return self._json({"ok": False, "mensagem": "Cola a chave."})
                    ok, mensagem = provedores.validar(nome, chave, modelo)
                    if ok:
                        no_cofre = definicoes.escolher(nome, modelo, chave)
                        if not no_cofre:
                            mensagem += " Não foi possível guardá-la no cofre do sistema: fica só até fechares."
                    return self._json({"ok": ok, "mensagem": mensagem, "estado": servico.info()})
                if self.path == "/api/esquecer":
                    definicoes.apagar_chave(str(dados.get("provedor") or provedores.provedor()))
                    return self._json({"ok": True, "estado": servico.info()})
                if self.path == "/api/dados/descarregar":
                    servico.descarregar_dados()
                    return self._json({"ok": True, "estado": servico.info()})
                if self.path == "/api/dados/atualizacao":
                    try:
                        nova = dados.ha_atualizacao(servico.pasta_dados)
                    except Exception as e:
                        return self._json({"ok": False, "mensagem": f"Não foi possível ver se há atualização: {e}"})
                    return self._json({"ok": True, "nova": nova["versao"] if nova else None})
                if self.path == "/api/sem-ia":
                    definicoes.gravar({**definicoes.ler(), "provedor": provedores.provedor(), "sem_ia": True})
                    return self._json({"ok": True, "estado": servico.info()})
            except RuntimeError as e:
                return self._json({"erro": str(e)}, HTTPStatus.SERVICE_UNAVAILABLE)
            return self._json({"erro": "não encontrado"}, HTTPStatus.NOT_FOUND)

    return Pedido


def criar_servidor(servico: Servico, porta: int = 0) -> ThreadingHTTPServer:
    servidor = ThreadingHTTPServer(("127.0.0.1", porta), criar_tratador(servico, secrets.token_urlsafe(24)))
    servidor.daemon_threads = True
    return servidor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--porta", type=int, default=0, help="Por omissão, uma porta livre.")
    parser.add_argument("--indice", type=Path)
    parser.add_argument("--reranker", choices=("cruzado", "denso", "nenhum"))
    parser.add_argument("--sem-browser", action="store_true", help="Não abrir o browser.")
    args = parser.parse_args(argv)

    definicoes.aplicar()
    servico = Servico(args.indice, args.reranker)
    threading.Thread(target=servico.carregar, daemon=True).start()
    servidor = criar_servidor(servico, args.porta)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    print(f"Leis de Portugal: abre {url} no browser. Ctrl + C para fechar.", file=sys.stderr, flush=True)
    if not args.sem_browser:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servico.gravar_pendentes()
        servidor.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
