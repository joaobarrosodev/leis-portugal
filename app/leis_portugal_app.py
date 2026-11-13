"""A aplicação Leis de Portugal (Mac e Windows): a página local numa janela própria.

Empacotada com o PyInstaller (`app/leis-portugal.spec`). Tudo o que a aplicação guarda fica na
pasta dela (`rag.definicoes.pasta()`): as Definições, os dados descarregados (`dados/`, onde o `rag`
lê o índice e os modelos) e as perguntas avaliadas. A chave fica no cofre do sistema.

    python app/leis_portugal_app.py                      # abre a janela (ou o browser, sem pywebview)
    python app/leis_portugal_app.py --verificar          # confirma que tudo se importa e sai
    python app/leis_portugal_app.py --verificar "pergunta"   # e faz uma pergunta, se houver dados
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path


if not getattr(sys, "frozen", False):  # a correr do repositório: o `rag` e o `leis_portugal` estão na raiz e em src/
    raiz = Path(__file__).resolve().parents[1]
    sys.path[:0] = [str(raiz), str(raiz / "src")]

from rag import definicoes  # noqa: E402  (só depende do ambiente, não lê o índice)


PASTA = definicoes.pasta()
# Antes de importar o resto do `rag`: o caminho do índice e dos modelos lê-se ao importar.
os.environ.setdefault("RAG_INDICE", str(PASTA / "dados"))
os.environ.setdefault("RAG_REGISTO", str(PASTA / "perguntas-testadas.jsonl"))


def verificar(pergunta: str | None) -> int:
    from rag import dados, modelos, pesquisa, provedores, reescrita, resposta, web  # noqa: F401
    from rag.texto import METODO

    print(f"Importações: ok. Termos: {METODO}. Pasta: {PASTA}. IA: {provedores.descricao()}.")
    print(f"Página: {web.PAGINA} ({'ok' if (web.PAGINA / 'index.html').is_file() else 'EM FALTA'}).")
    if pergunta:
        definicoes.aplicar()
        servico = web.Servico()
        servico.carregar()
        if servico.pesquisa is None:
            print(f"Sem dados: {servico.erro}")
            return 1
        r = servico.perguntar(pergunta, __import__("datetime").date.today().isoformat())
        print(r["texto"][:400] if r["responde"] else f"Não sei: {r['motivo']}")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--verificar"]:
        return verificar(argv[1] if len(argv) > 1 else None)

    from rag import web

    PASTA.mkdir(parents=True, exist_ok=True)
    definicoes.aplicar()
    servico = web.Servico()
    threading.Thread(target=servico.carregar, daemon=True).start()
    servidor = web.criar_servidor(servico)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    try:
        try:
            import webview
        except ImportError:
            import time
            import webbrowser

            webbrowser.open(url)
            print(f"Leis de Portugal em {url}. Fecha esta janela para sair.", flush=True)
            while True:
                time.sleep(3600)
        else:
            webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True
            webview.create_window("Leis de Portugal", url, width=1120, height=860, min_size=(380, 600))
            webview.start()
    except KeyboardInterrupt:
        pass
    finally:
        servico.gravar_pendentes()
        servidor.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
