"""As Definições da página e da aplicação: a IA escolhida, o modelo e a chave.

- A IA e o modelo ficam em `definicoes.json`, na pasta da aplicação de cada sistema
  (`~/Library/Application Support/Leis de Portugal`, `%APPDATA%\\Leis de Portugal`,
  `~/.local/share/leis-portugal`), ou em `LEIS_PORTUGAL_PASTA` se estiver definida.
- A chave fica no cofre do sistema (Keychain no Mac, Credential Manager no Windows), com o
  pacote `keyring`. Nunca vai para ficheiros. Sem `keyring`, fica só na memória até fechar.

`aplicar()` põe tudo no `os.environ` do próprio processo (`RAG_PROVEDOR`, `RAG_MODELO` e a
variável da chave), que é onde `rag.provedores` a lê. Nada muda nas variáveis do sistema.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from rag import provedores


SERVICO = "leis-portugal"
_em_memoria: dict[str, str] = {}


def pasta() -> Path:
    if os.environ.get("LEIS_PORTUGAL_PASTA"):
        return Path(os.environ["LEIS_PORTUGAL_PASTA"])
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Leis de Portugal"
    if os.name == "nt":
        return Path(os.environ.get("APPDATA", Path.home())) / "Leis de Portugal"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "leis-portugal"


def _ficheiro() -> Path:
    return pasta() / "definicoes.json"


def ler() -> dict:
    try:
        return json.loads(_ficheiro().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def gravar(dados: dict) -> None:
    _ficheiro().parent.mkdir(parents=True, exist_ok=True)
    _ficheiro().write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")


def _keyring():
    try:
        import keyring

        keyring.get_keyring()
        return keyring
    except Exception:
        return None


def cofre_disponivel() -> bool:
    return _keyring() is not None


def guardar_chave(provedor: str, chave: str) -> bool:
    """Guarda no cofre do sistema; devolve False se só ficou na memória."""
    _em_memoria[provedor] = chave
    kr = _keyring()
    if kr is None:
        return False
    try:
        kr.set_password(SERVICO, provedor, chave)
        return True
    except Exception:
        return False


def ler_chave(provedor: str) -> str | None:
    if provedor in _em_memoria:
        return _em_memoria[provedor]
    kr = _keyring()
    if kr is None:
        return None
    try:
        return kr.get_password(SERVICO, provedor)
    except Exception:
        return None


def apagar_chave(provedor: str) -> None:
    _em_memoria.pop(provedor, None)
    os.environ.pop(provedores.PROVEDORES[provedor]["variavel"], None)
    kr = _keyring()
    if kr is not None:
        try:
            kr.delete_password(SERVICO, provedor)
        except Exception:
            pass


def aplicar() -> None:
    """Põe a IA, o modelo e a chave escolhidos no ambiente deste processo.

    Uma variável já definida no ambiente (por exemplo `ANTHROPIC_API_KEY` no Terminal) ganha às
    Definições, para quem usa o `./perguntar` continuar como antes."""
    dados = ler()
    nome = os.environ.get("RAG_PROVEDOR") or dados.get("provedor") or "claude"
    if nome not in provedores.PROVEDORES:
        nome = "claude"
    os.environ["RAG_PROVEDOR"] = nome
    if dados.get("modelo") and dados.get("provedor") == nome and not os.environ.get("RAG_MODELO"):
        os.environ["RAG_MODELO"] = dados["modelo"]
    variavel = provedores.PROVEDORES[nome]["variavel"]
    if not os.environ.get(variavel):
        chave = ler_chave(nome)
        if chave:
            os.environ[variavel] = chave


def escolher(provedor: str, modelo: str, chave: str) -> bool:
    """Grava a escolha (já validada) e aplica-a; devolve se a chave ficou no cofre."""
    no_cofre = guardar_chave(provedor, chave)
    gravar({**ler(), "provedor": provedor, "modelo": modelo})
    os.environ["RAG_PROVEDOR"] = provedor
    os.environ["RAG_MODELO"] = modelo
    os.environ[provedores.PROVEDORES[provedor]["variavel"]] = chave
    return no_cofre
