#!/bin/sh
# Repor o DL 99/94 e o DL 106/97 como ficaram em 599ee20d8e3 (o acervo.py da ronda 117 repôs-lhes o texto antigo)
# e aplicar a revogação mecânica do art. 16.º do DL 143/96 (verificada às cegas). Dois commits, só com estes ficheiros.
set -e
cd "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
while [ -f .git/index.lock ]; do echo "à espera do index.lock"; sleep 5; done
GIT_EDITOR=true git pull --no-rebase -q origin main
F="data/portugal/decretos-leis/1994/decreto-lei-99-94.md data/portugal/decretos-leis/1994/decreto-lei-99-94.versoes.json data/portugal/decretos-leis/1997/decreto-lei-106-97.md data/portugal/decretos-leis/1997/decreto-lei-106-97.versoes.json"
git checkout 599ee20d8e3 -- $F
git commit -q -m "Repor o texto antigo retirado do DL 99/94 e do DL 106/97

O acervo.py da ronda 117 (e9eedeb4ca5) voltou a escrever-lhes o consolidado do piloto, que ainda tinha o texto antigo. Ficam como em 599ee20d8e3. O acervo.py passa a ler auditoria/texto-antigo-corrigidos.jsonl e já não os escreve por cima.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- $F
git log --oneline -1
.venv/bin/python consolidacao/texto_antigo.py revogar-aplicar "/Users/barroso/Documents/Seamless Doubt/leis-portugal"
G="data/portugal/decretos-leis/1996/decreto-lei-143-96.md data/portugal/decretos-leis/1996/decreto-lei-143-96.versoes.json consolidacao/auditoria/texto-antigo-corrigidos.jsonl"
git add -- $G
git commit -q -m "DL 143/96, art. 16.º: corpo antigo retirado a seguir a «(Revogado.)», por regra e verificado às cegas

texto_antigo.revogar_inteiro: o art. 16.º, revogado pelo DL 208/2002, tinha a seguir o corpo antigo com as alíneas d) e e) já revogadas pelo DL 206/98. Era o artigo que a correção de 599ee20d8e3 tinha recusado.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- $G
GIT_EDITOR=true git pull --no-rebase -q origin main
git push -q origin HEAD:main
git log --oneline -3
