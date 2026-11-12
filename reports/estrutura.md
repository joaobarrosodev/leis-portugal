# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-11-12. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 305.883 | |
| Com texto | 213.160 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 64.180 | 30,1% |
| Só com números do dispositivo (`1.º`, `1 -`) | 58.384 | 27,4% |
| Artigos só nos anexos | 546 | 0,3% |
| Sem divisão (texto único) | 90.050 | 42,2% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 39.950; só em texto corrido (novos): 81.707.
- Em vigor com texto: 129.180; com artigos: 37.212 (28,8%); com artigos ou números: 76.588 (59,3%).
- Artigos com id: 983.467; números com id: 285.728.
- Diplomas com anexos com artigos: 6.515; com numeração repetida na mesma parte (chave `art-5-2`): 894; com ids repetidos: 0.

## Entrada em vigor

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Data calculada a partir da cláusula | 31.017 | 14,6% |
| Só a regra (não dá para calcular) | 4.073 | 1,9% |
| Regra supletiva (5.º dia após a publicação) | 52.414 | 24,6% |
| Sem cláusula e sem regra supletiva | 125.656 | 58,9% |

- Produção de efeitos: 12.249 com data; 5.094 só com a regra.
- Com fim de vigência no texto: 228; com cláusulas parciais (só alguns artigos): 18.176.

Regras mais frequentes que ficam sem data:

- 127 × no dia seguinte ao da sua assinatura
- 113 × no dia útil seguinte ao da sua publicação
- 106 × na data da sua assinatura
- 82 × no N.º dia útil seguinte ao da sua publicação
- 82 × no primeiro dia útil seguinte ao da sua publicação
- 66 × no N.º dia útil do mês seguinte ao da sua publicação
- 63 × no primeiro dia útil do mês seguinte ao da sua publicação
- 46 × na data da assinatura
- 41 × na data da última notificação do cumprimento das formalidades exigidas pela ordem jurídica
- 28 × decorridos N dias após a data da sua publicação
- 26 × imediatamente
- 20 × no dia útil seguinte ao da sua publicação e
- 19 × :
- 19 × com o orçamento do estado subsequente à sua publicação
- 18 × N dias após a recepção da última notificação, por escrito e por via diplomática, de que fo

Por jurisdição e série:

| | Com data | Só regra | Supletiva | Sem cláusula |
| --- | --: | --: | --: | --: |
| portugal / série I | 23.210 | 3.320 | 52.414 | 76.528 |
| portugal / série II | 2.995 | 419 | 0 | 42.838 |
| regional / série ? | 0 | 0 | 0 | 4 |
| regional / série I | 4.756 | 333 | 0 | 6.067 |
| regional / série II | 56 | 1 | 0 | 219 |

## Vigência desconhecida

Diplomas com `legal_status: unknown`: 114.487. Estado proposto com prova: **375** (not_in_force: 22, repealed: 353).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 22 |
| Provas em conflito (o mesmo revogador, total e parcial) | 8 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 55.742 |
| Só revogação parcial: o resto continua desconhecido | 126 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 47 |
| Revogado (prova de revogação total) | 353 |
| Sem prova | 58.189 |

Revogações lidas nas normas revogatórias: 18.454 (sobre 15.995 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 324 | 10.373 | 1.364 | 88,7% |
| Relação do DRE (etiqueta) | 0 | 20.397 | 1.088 | 94,9% |

As propostas, com as provas e a proveniência de cada uma, estão em `vigencia-proposta.jsonl`.

### Como se resolve, sem inferir sem prova

- **Só uma revogação total fixa o estado** (`repealed`). Conta a norma revogatória de outro diploma do acervo ("É revogado o [Decreto-Lei n.º 253/86]…", com a ligação ao diploma) e a etiqueta da relação do DRE ("Revogado pelo DEC LEI…"). Proveniência: `norma revogatória: <id do revogador>#<artigo>` ou `DRE repealed_by: <id>`.
- **Revogação parcial não resolve**: "os artigos 3.º e 5.º do…" ou "Revogado o nº 5 pela…" ficam registados como prova, mas o resto do diploma continua de vigência desconhecida (não se conclui que está em vigor).
- **Revogações condicionais ou diferidas não contam** ("a partir da entrada em vigor da portaria…", "mantido transitoriamente…"), e uma ligação noutro papel ("na redação dada pelo…", "aprovado pelo…") também não.
- **Relação `repealed_by` sem etiqueta**: não diz se é total ou parcial; fica "por confirmar" até haver o texto do revogador.
- **Caducidade**: só quando o próprio diploma fixa o fim ("vigora até 31 de dezembro de 2013"), a data já passou e o diploma não foi alterado depois (uma alteração pode ter prorrogado a vigência). Proveniência: `cláusula de vigência: <artigo>`.
- **Declarações de retificação** não têm vigência própria: seguem o diploma retificado (relação `corrects`).
- **Só PDF e anteriores a 1960**: sem texto não há prova; ficam marcados como históricos e saem do índice de lei atual, sem mudar `legal_status`.
- Ao escrever nos registos, o estado proposto vai para `legal_status` e as provas para `legal_status_basis`; um conflito entre provas (total num lado, parcial noutro) não muda nada.
