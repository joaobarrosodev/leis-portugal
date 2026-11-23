#!/bin/sh
# Lote 2: o texto antigo retirado dos 4 consolidados (texto_antigo.py aplicar) e commit só desses ficheiros.
set -e
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
GIT_EDITOR=true git pull --no-rebase -q origin main
git status --porcelain -- data | sort > "$TMPDIR/ta-antes.txt"
PYTHONPATH=src .venv/bin/python consolidacao/texto_antigo.py aplicar "/Users/barroso/Documents/Seamless Doubt/leis-portugal" 2>&1 | tail -3
git status --porcelain -- data | sort > "$TMPDIR/ta-depois.txt"
comm -13 "$TMPDIR/ta-antes.txt" "$TMPDIR/ta-depois.txt" | cut -c4- > "$TMPDIR/ta-ficheiros.txt"
printf 'consolidacao/auditoria/texto-antigo-corrigidos.jsonl\n' >> "$TMPDIR/ta-ficheiros.txt"
cat "$TMPDIR/ta-ficheiros.txt"
cat > "$TMPDIR/ta-msg.txt" <<'M'
Texto antigo retirado de 25 artigos em 4 consolidados, por regra e verificado às cegas

DL 106/97, DL 143/96, DL 122/93 e DL 99/94: artigos revogados, ou com nova redação, que o índice servia com o corpo antigo a seguir (consolidacao/texto_antigo.py). Os 25 deram certo às cegas.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
M
sh .claude/worktrees/consolidacao-bloco-3-7237a2/consolidacao/camada1/commit-lote.sh "$TMPDIR/ta-ficheiros.txt" "$TMPDIR/ta-msg.txt"
