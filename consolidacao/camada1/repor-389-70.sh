#!/bin/sh
# Repõe no data/ o texto original do DL 389/70 (pt:dre:139401), que a ronda 121 consolidou com todos os artigos
# «(Revogado.)». Pela regra da ronda 80, uma revogação total não se consolida: fica em llm/exclusoes.json e a
# revogação está em reports/vigencia-manual.jsonl. Volta a versão anterior ao commit 9b934bcd7a2.
set -e
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
while [ -f .git/index.lock ]; do echo "à espera do index.lock"; sleep 5; done
git fetch -q origin
GIT_EDITOR=true git pull --no-rebase -q origin main
MD=data/portugal/decretos-leis/1970/decreto-lei-389-70.md
VERSOES=data/portugal/decretos-leis/1970/decreto-lei-389-70.versoes.json
git checkout 9b934bcd7a2^ -- "$MD"
git rm -q "$VERSOES"
printf '%s\n' "$MD" > "$TMPDIR/repor-389.txt"
PYTHONPATH=src .venv/bin/python - "$TMPDIR/repor-389.txt" <<'PY'
import sys
from pathlib import Path
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.infrastructure.markdown import read_markdown_record
acervo = Acervo(Path("."))
p = Path(Path(sys.argv[1]).read_text(encoding="utf-8").strip())
metadata, body = read_markdown_record(p)
erros = list(acervo.schema.record_errors(metadata)) + ([] if body.strip() else ["corpo vazio"])
print(f"{p}: {len(erros)} erros", *erros)
sys.exit(1 if erros else 0)
PY
PYTHONPATH=src:consolidacao .venv/bin/python -m pytest -q -x tests > "$TMPDIR/testes-389.txt" 2>&1 || { tail -20 "$TMPDIR/testes-389.txt"; echo "PARADO: testes"; exit 1; }
tail -1 "$TMPDIR/testes-389.txt"
git add -- "$MD"
git commit -q -F - <<'M'
DL 389/70: volta o texto original (revogado por inteiro, não se consolida)

A ronda 121 tinha posto o DL 389/70 no data/ com todos os artigos «(Revogado.)», em cumprimento do DL 241/75. Pela regra da ronda 80 (consolidacao/README.md), uma revogação do diploma inteiro não se consolida: o diploma fica com o texto original e a revogação vai para a vigência. Já estava em reports/vigencia-manual.jsonl e agora está também em consolidacao/llm/exclusoes.json.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
M
git fetch -q origin
GIT_EDITOR=true git pull --no-rebase -q origin main
git push -q origin HEAD:main
git log --oneline -1
