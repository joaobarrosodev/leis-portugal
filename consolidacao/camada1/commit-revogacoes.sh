#!/bin/sh
# Commit só dos ficheiros que revogacoes.py aplicar mudou no data/ (pasta principal) e da auditoria das revogações.
set -e
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
while [ -f .git/index.lock ]; do echo "à espera do index.lock"; sleep 5; done
.venv/bin/python - <<'E' > "$TMPDIR/revogacoes-ficheiros.txt"
import json
for l in open("consolidacao/auditoria/revogacoes-aplicadas.jsonl", encoding="utf-8"):
    if l.strip():
        c = json.loads(l)["caminho"]
        print(c)
        print(c[: -len(".md")] + ".versoes.json")
E
echo "$(wc -l < "$TMPDIR/revogacoes-ficheiros.txt") ficheiros do data/"
tr '\n' '\0' < "$TMPDIR/revogacoes-ficheiros.txt" | xargs -0 git add --
git add consolidacao/auditoria/revogacoes-aplicadas.jsonl consolidacao/auditoria/revogacoes-estado.jsonl
git diff --cached --stat | tail -1
git commit -q -F - <<'M'
Revogações parciais: 170 aplicadas em 134 consolidados, verificadas às cegas

Revogações registadas no DRE só como repealed_by, que os consolidados nossos ainda serviam como texto em vigor. Cada par foi aplicado por um respondedor (Opus), com a data de efeitos e a nota do DRE, e verificado às cegas em duas passagens (Sonnet). Os pares que não deram certo ficam com o motivo em consolidacao/auditoria/revogacoes-estado.jsonl.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
M
GIT_EDITOR=true git pull --no-rebase -q origin main
git push -q origin HEAD:main
git log --oneline -2
