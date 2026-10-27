"""Protótipo de RAG sobre o acervo (fase 4 do PLANO-RAG.md): índice por artigo, pesquisa e medição."""

import sys
from pathlib import Path


# Pacotes opcionais instalados à parte (`pip install --target .rag-deps …`), quando o ambiente
# do projeto não os tem; ficam no fim do caminho para não taparem os do projeto.
_DEPS = Path(__file__).resolve().parents[1] / ".rag-deps"
if _DEPS.is_dir() and str(_DEPS) not in sys.path:
    sys.path.append(str(_DEPS))
