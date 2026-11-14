# Pendente para segunda-feira (16/11/2026)

O plano semanal do Claude estava a 98 % no sábado (14/11) e renova-se na segunda, por volta das 4h.
Por ordem: primeiro o que gasta pouco, depois o que precisa de modelos.

## 1. Três diplomas consolidados por confirmar (consolidação)

**Ler os três: cerca de 15 minutos.** Basta comparar o consolidado com o texto do alterador.

- **DL 82/73:** quase de certeza o mais rápido. Se o registo em `data/` tiver a relação
  `repealed_by` do DRE a apontar para o DL 553/77, fica confirmado que é o mesmo diploma e não há
  nada a corrigir.
- **DL 92/92:** é o que pede mais leitura. É preciso decidir se o 13.º-A é deste diploma ou se foi
  aditado a outro. Se foi aditado a outro, a revogação não devia estar aqui.
- **DRR 2/2005/M:** o texto está certo, só a chave «212.º» está errada. O que leva tempo é perceber
  porque é que o parser leu mal o artigo 21.º.

**Corrigir o que estiver mal: mais 15 a 45 minutos.**
- Um consolidado corrigido tem de voltar a passar pela verificação às cegas (numa sessão à parte) e
  pelo `acervo.py` antes de mudar o `data/`.
- Se o erro for do parser, como no DRR 2/2005/M, também é preciso corrigir o parser e confirmar que
  mais nada muda.

## 2. Atos da UE em vigor que ainda faltam (30)

Os 1.218 sem versão portuguesa já estão traduzidos (14/11). Faltam:

- **23 por identificar:** são a diferença entre a lista do CELLAR de 11/11/2026 e
  `reports/eurlex_em_vigor_failures.jsonl`. Refazer a lista dos atos em vigor, cruzar com o acervo
  e ver se já estão gravados com outro id ou se têm outro problema.
- **4 com o número oficial repetido:** decisões cujo número coincide com o de outra já gravada.
  Decidir se se gravam com o caminho desambiguado.
- **3 sem texto no CELLAR:** confirmar que não há PDF nem HTML em nenhuma língua.

Gasta pouco: são consultas ao CELLAR e um script.

## 3. RAG

- **Reconstruir o índice** para entrarem as 1.218 traduções da UE. Usa só o PC.
- **Mostrar na resposta o `version.label`** («Tradução não oficial … sem valor jurídico») quando
  se cita um ato traduzido.
- **Decidir se as traduções ficam no índice:** quase todas são decisões antigas dirigidas a outros
  Estados e podem baralhar perguntas gerais.
- **Medir os tipos novos:**
  - a 2.ª Série, a CNPD e o TC (`--com-serie-ii`);
  - juntar à avaliação cerca de 50 perguntas desses tipos, verificadas às cegas;
  - repetir a avaliação BM25 com o aviso de inconstitucionalidade de 1983–2026.

## 4. Só no PC, sem gastar o plano (pode correr antes de segunda)

OCR dos cerca de 36 mil PDF digitalizados da CNPD. São 2 a 3 dias de máquina e pode ser
interrompido. Corre num Terminal, no checkout principal:

```bash
LEIS_PORTUGAL_PDFTEXT="/Users/barroso/Documents/Seamless Doubt/leis-portugal/.claude/worktrees/fase2-texto-em-vigor-c8cffe/.cache/pdftext" PYTHONPATH=src .venv/bin/leis-portugal collect cnpd --without-text
```

No fim, faz o commit dos registos regravados.

## 5. À espera de terceiros

- **TC e CNPD:** a resposta ao pedido de confirmação da reutilização, notificados a 12/11/2026.
- **Chave da API:** para testar as respostas escritas com o LLM.
