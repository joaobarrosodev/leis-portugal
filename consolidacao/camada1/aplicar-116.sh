#!/bin/sh
# Ronda 116: acervo.py no data/ da pasta principal e commit só dos ficheiros que ele mudou.
set -e
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
while [ -f .git/index.lock ]; do echo "à espera do index.lock"; sleep 5; done
git status --porcelain -- data | sort > "$TMPDIR/antes-116.txt"
PYTHONPATH=src .venv/bin/python consolidacao/acervo.py 2>&1 | grep -E "^Aplicados"
git status --porcelain -- data | sort > "$TMPDIR/depois-116.txt"
comm -13 "$TMPDIR/antes-116.txt" "$TMPDIR/depois-116.txt" | cut -c4- > "$TMPDIR/ficheiros-116.txt"
echo "$(wc -l < "$TMPDIR/ficheiros-116.txt") ficheiros do data/ mudados pela ronda 116"
cat "$TMPDIR/ficheiros-116.txt"
tr '\n' '\0' < "$TMPDIR/ficheiros-116.txt" | xargs -0 git add --
git commit -q -F - <<'M'
Camada 1, ronda 116: 11 consolidados para o data/

Os recusados da onda 1 repedidos com as retificações e as revogações nos reparos. Cada um passou a verificação às cegas, a barreira mecânica do texto antigo (texto_antigo.py) e a segunda leitura jurídica.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
M
GIT_EDITOR=true git pull --no-rebase -q origin main
git push -q origin HEAD:main
git log --oneline -1
