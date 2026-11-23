#!/bin/sh
# Lote 1: as revogações da r3 (revogacoes.py aplicar) e commit só dos ficheiros que mudaram.
set -e
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
GIT_EDITOR=true git pull --no-rebase -q origin main
git status --porcelain -- data | sort > "$TMPDIR/r3-antes.txt"
PYTHONPATH=src .venv/bin/python consolidacao/revogacoes.py aplicar 2>&1 | tail -1
PYTHONPATH=src .venv/bin/python consolidacao/revogacoes.py estado 2>&1 | tail -1
git status --porcelain -- data | sort > "$TMPDIR/r3-depois.txt"
comm -13 "$TMPDIR/r3-antes.txt" "$TMPDIR/r3-depois.txt" | cut -c4- > "$TMPDIR/r3-ficheiros.txt"
printf 'consolidacao/auditoria/revogacoes-aplicadas.jsonl\nconsolidacao/auditoria/revogacoes-estado.jsonl\n' >> "$TMPDIR/r3-ficheiros.txt"
echo "$(wc -l < "$TMPDIR/r3-ficheiros.txt") ficheiros"
cat > "$TMPDIR/r3-msg.txt" <<'M'
Revogações parciais, ronda r3: mais 47 aplicadas em 41 consolidados, verificadas às cegas

Os pares que as duas primeiras passagens não confirmaram foram respondidos de novo, com o diploma que revoga mais completo e o motivo do verificador como reparo, e verificados às cegas outra vez.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
M
sh .claude/worktrees/consolidacao-bloco-3-7237a2/consolidacao/camada1/commit-lote.sh "$TMPDIR/r3-ficheiros.txt" "$TMPDIR/r3-msg.txt"
