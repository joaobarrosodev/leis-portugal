#!/bin/sh
# Lote de uma ronda da camada 1 para o data/ da pasta principal (desde a ronda 122).
# Uso: sh consolidacao/camada1/lote.sh RONDA ESPERADOS
# 1. git fetch e git pull --no-rebase; 2. acervo.py; 3. valida os ficheiros mudados (o esquema do
# `leis-portugal validate`, só nesses ficheiros) e corre os testes; 4. só então commit e push, só desses
# ficheiros. Se o número de aplicados não for ESPERADOS, ou a validação ou os testes falharem, não há
# commit: os ficheiros do data/ ficam como o acervo.py os deixou, para ver, e o script sai com erro.
set -e
RONDA="$1"
ESPERADOS="$2"
[ -n "$RONDA" ] && [ -n "$ESPERADOS" ] || { echo "uso: lote.sh RONDA ESPERADOS"; exit 2; }
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
while [ -f .git/index.lock ]; do echo "à espera do index.lock"; sleep 5; done
git fetch -q origin
GIT_EDITOR=true git pull --no-rebase -q origin main
git status --porcelain -- data | sort > "$TMPDIR/antes-$RONDA.txt"
PYTHONPATH=src .venv/bin/python consolidacao/acervo.py > "$TMPDIR/acervo-$RONDA.txt" 2>&1 || true
grep -E "^Aplicados" "$TMPDIR/acervo-$RONDA.txt"
APLICADOS=$(grep -E "^Aplicados" "$TMPDIR/acervo-$RONDA.txt" | sed -E 's/^Aplicados: ([0-9]+).*/\1/')
git status --porcelain -- data | sort > "$TMPDIR/depois-$RONDA.txt"
comm -13 "$TMPDIR/antes-$RONDA.txt" "$TMPDIR/depois-$RONDA.txt" | cut -c4- > "$TMPDIR/ficheiros-$RONDA.txt"
echo "$(wc -l < "$TMPDIR/ficheiros-$RONDA.txt") ficheiros do data/ mudados pela ronda $RONDA"
if [ "$APLICADOS" != "$ESPERADOS" ]; then echo "PARADO: aplicados $APLICADOS, esperados $ESPERADOS"; exit 1; fi
PYTHONPATH=src .venv/bin/python - "$TMPDIR/ficheiros-$RONDA.txt" <<'PY'
import json, sys
from pathlib import Path
from leis_portugal.infrastructure.repository import Acervo
from leis_portugal.infrastructure.markdown import read_markdown_record
acervo = Acervo(Path("."))
erros = 0
for linha in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    p = Path(linha.strip())
    if p.suffix == ".json":
        json.loads(p.read_text(encoding="utf-8"))
        continue
    metadata, body = read_markdown_record(p)
    problemas = list(acervo.schema.record_errors(metadata))
    if not body.strip():
        problemas.append("corpo vazio")
    if metadata.get("validation", {}).get("status") == "validation_failed":
        problemas.append("validation_failed")
    for m in problemas:
        print(f"{p}: {m}")
        erros += 1
print(f"validação dos ficheiros mudados: {erros} erros")
sys.exit(1 if erros else 0)
PY
PYTHONPATH=src:consolidacao .venv/bin/python -m pytest -q -x tests > "$TMPDIR/testes-$RONDA.txt" 2>&1 || { tail -20 "$TMPDIR/testes-$RONDA.txt"; echo "PARADO: testes"; exit 1; }
tail -1 "$TMPDIR/testes-$RONDA.txt"
tr '\n' '\0' < "$TMPDIR/ficheiros-$RONDA.txt" | xargs -0 git add --
git commit -q -F - <<M
Camada 1, ronda $RONDA: $APLICADOS consolidados da onda 2 para o data/

Os $APLICADOS diplomas passaram a verificação às cegas, a barreira mecânica (texto_antigo.py) e a segunda leitura jurídica (Opus). Antes do commit, a validação do esquema dos ficheiros mudados e os testes passaram (consolidacao/camada1/lote.sh).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
M
git fetch -q origin
GIT_EDITOR=true git pull --no-rebase -q origin main
git push -q origin HEAD:main
git log --oneline -1
