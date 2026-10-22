"""Interface de linha de comandos: lê argumentos, chama os serviços, imprime resultados."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from leis_portugal.cli import collect, maintenance, versions
from leis_portugal.errors import LeisPortugalError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="leis-portugal", description="Recolha, validação e relatórios do acervo Leis de Portugal.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Raiz do repositório (por omissão: diretório atual).")
    commands = parser.add_subparsers(dest="command", required=True)
    collect.register(commands)
    versions.register(commands)
    maintenance.register(commands)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except BrokenPipeError:
        # Saída cortada (p. ex. `| head`): terminar sem erro.
        sys.stderr.close()
        return 0
    except (LeisPortugalError, ValueError) as exc:
        # ValueError: dados de entrada inválidos (p. ex. um CELEX mal escrito).
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
