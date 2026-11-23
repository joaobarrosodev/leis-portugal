#!/bin/sh
# Uso: commit-lote.sh <ficheiro com a lista de caminhos do data/ e da auditoria> <mensagem>
# Faz commit só desses ficheiros (os que mudaram) na pasta principal e push.
set -e
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
while [ -f .git/index.lock ]; do echo "à espera do index.lock"; sleep 5; done
tr '\n' '\0' < "$1" | xargs -0 git add --
git diff --cached --stat | tail -1
git commit -q -F "$2"
GIT_EDITOR=true git pull --no-rebase -q origin main
git push -q origin HEAD:main
git log --oneline -1
