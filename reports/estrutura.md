# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-11-13. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 323.151 | |
| Com texto | 221.978 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 66.110 | 29,8% |
| Só com números do dispositivo (`1.º`, `1 -`) | 58.667 | 26,4% |
| Artigos só nos anexos | 593 | 0,3% |
| Sem divisão (texto único) | 96.608 | 43,5% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 40.234; só em texto corrido (novos): 83.636.
- Em vigor com texto: 134.286; com artigos: 38.911 (29,0%); com artigos ou números: 78.356 (58,4%).
- Artigos com id: 994.525; números com id: 286.711.
- Diplomas com anexos com artigos: 6.621; com numeração repetida na mesma parte (chave `art-5-2`): 1.082; com ids repetidos: 0.

## Entrada em vigor

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Data calculada a partir da cláusula | 31.035 | 14,0% |
| Só a regra (não dá para calcular) | 4.082 | 1,8% |
| Regra supletiva (5.º dia após a publicação) | 52.415 | 23,6% |
| Sem cláusula e sem regra supletiva | 134.446 | 60,6% |

- Produção de efeitos: 12.268 com data; 5.124 só com a regra.
- Com fim de vigência no texto: 228; com cláusulas parciais (só alguns artigos): 18.300.

Regras mais frequentes que ficam sem data:

- 127 × no dia seguinte ao da sua assinatura
- 115 × no dia útil seguinte ao da sua publicação
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
| portugal / série I | 23.211 | 3.322 | 52.415 | 80.439 |
| portugal / série II | 3.014 | 426 | 0 | 47.653 |
| regional / série ? | 0 | 0 | 0 | 4 |
| regional / série I | 4.754 | 333 | 0 | 6.110 |
| regional / série II | 56 | 1 | 0 | 240 |

## Vigência desconhecida

Diplomas com `legal_status: unknown`: 124.275. Estado proposto com prova: **342** (not_in_force: 22, repealed: 320).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 22 |
| Provas em conflito (o mesmo revogador, total e parcial) | 7 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 61.812 |
| Só revogação parcial: o resto continua desconhecido | 138 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 49 |
| Revogado (prova de revogação total) | 320 |
| Sem prova | 61.927 |

Revogações lidas nas normas revogatórias: 17.131 (sobre 15.068 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 292 | 9.597 | 827 | 92,3% |
| Relação do DRE (etiqueta) | 0 | 20.410 | 1.106 | 94,9% |

**Texto contra o DRE.** 729 diplomas que o DRE dá em vigor têm uma revogação total lida na norma revogatória de outro diploma do acervo (736 provas). Cada prova tem um segmento: a identidade do diploma ligado (o número do rótulo, a data citada até 20 dias antes da publicação, a entidade e a série) e os sinais contra (alteração registada no DRE depois do revogador, outro revogador ou revogação parcial no DRE, repristinação, declaração de retificação, "legislação em contrário").

| Segmento | Provas | Amostra às cegas | Certos | Precisão ponderada | Wilson 95 % |
| --- | --: | --: | --: | --: | --: |
| a: identidade confirmada (número e data), nacional, sem sinais contra | 507 | 95 | 89 | 93,6% | 86,7% – 97,0% |
| b: só o número confirmado (sem data citada), nacional, sem sinais contra | 35 | 29 | 22 | 75,9% | 57,9% – 87,8% |
| c: algum sinal contra (identidade suspeita, série, alteração posterior, conflito no DRE, repristinação, retificação) ou regional | 194 | 26 | 16 | 61,4% | 41,6% – 78,0% |

Amostra de 2026-11-14 (seed 20261114, 150 casos nunca verificados, estratificada por segmento e tipo): verificadores às cegas e auditoria de todos os "não" e de 20 "sim" (43 de 45 concordam; prevalece a auditoria). A primeira amostra (2026-11-13, 113 casos: 78 certos, 69,0%) serviu para afinar a regra e não conta para a medida. Os erros que ficam: outro diploma com o mesmo número e data próxima (só a matéria os distingue), ressalvas de situações em curso noutro artigo e revogações diferidas. Nenhum segmento chega aos 98%: o estado do DRE não se substitui por esta prova. Só os casos verificados entram, como prova manual (`vigencia-manual.jsonl`). Lista, segmentos e veredictos: `vigencia-texto-contra-dre.jsonl`.

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
