#!/usr/bin/env bash
# Publica no Hugging Face a versão nova do índice de pesquisa (rag/dados.py): normalmente um delta
# de poucos MB; uma versão completa se o delta passar de 30% dela.
#
# Corre na pasta principal do repositório (a que tem o .venv), à mão ou agendado pelo
# scripts/agendar_publicacao.sh. Precisa da sessão do Hugging Face (`.venv/bin/hf auth login`).
#
#   1. git pull (só se o main estiver limpo; senão publica o que está aqui);
#   2. o export e o índice de novo (leis-portugal export, python -m rag.indice);
#   3. python -m rag.dados publicar --enviar.
#
# O registo fica em rag/resultados/privado/publicacao.log (fora do git).
set -euo pipefail

cd "$(dirname "$0")/.."
REGISTO=rag/resultados/privado/publicacao.log
mkdir -p "$(dirname "$REGISTO")"
exec >>"$REGISTO" 2>&1
echo "== início $(date '+%F %T')"

if [[ ! -x .venv/bin/python ]]; then
  echo "Sem .venv nesta pasta: corre na pasta principal do repositório (a que tem o .venv)."
  exit 1
fi

if [[ "$(git branch --show-current)" == "main" && -z "$(git status --porcelain --untracked-files=no)" ]]; then
  git pull --ff-only || echo "O git pull falhou: publica-se o que está aqui."
else
  echo "Fora do main ou com alterações por gravar: sem git pull; publica-se o que está aqui."
fi

.venv/bin/leis-portugal export
PYTHONPATH=src .venv/bin/python -m rag.indice
PYTHONPATH=src .venv/bin/python -m rag.dados publicar --enviar --versao "$(date +%F)"
echo "== fim $(date '+%F %T')"
