# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-11-13. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 323.150 | |
| Com texto | 221.977 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 66.109 | 29,8% |
| Só com números do dispositivo (`1.º`, `1 -`) | 58.666 | 26,4% |
| Artigos só nos anexos | 593 | 0,3% |
| Sem divisão (texto único) | 96.609 | 43,5% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 40.233; só em texto corrido (novos): 83.635.
- Em vigor com texto: 134.286; com artigos: 38.911 (29,0%); com artigos ou números: 78.355 (58,3%).
- Artigos com id: 994.441; números com id: 286.709.
- Diplomas com anexos com artigos: 6.621; com numeração repetida na mesma parte (chave `art-5-2`): 1.082; com ids repetidos: 0.

## Entrada em vigor

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Data calculada a partir da cláusula | 31.035 | 14,0% |
| Só a regra (não dá para calcular) | 4.081 | 1,8% |
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
| portugal / série II | 3.014 | 425 | 0 | 47.653 |
| regional / série ? | 0 | 0 | 0 | 4 |
| regional / série I | 4.754 | 333 | 0 | 6.110 |
| regional / série II | 56 | 1 | 0 | 240 |

## Vigência desconhecida

Diplomas com `legal_status: unknown`: 124.274. Estado proposto com prova: **352** (not_in_force: 22, repealed: 330).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 22 |
| Provas em conflito (o mesmo revogador, total e parcial) | 6 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 61.808 |
| Só revogação parcial: o resto continua desconhecido | 138 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 49 |
| Revogado (prova de revogação total) | 330 |
| Sem prova | 61.921 |

Revogações lidas nas normas revogatórias: 17.623 (sobre 15.316 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 312 | 9.947 | 951 | 91,5% |
| Relação do DRE (etiqueta) | 0 | 20.410 | 1.101 | 94,9% |

**Texto contra o DRE.** 785 diplomas que o DRE dá em vigor têm uma revogação total lida na norma revogatória de outro diploma do acervo (824 provas). Numa amostra verificada às cegas (2026-11-13, 113 casos estratificados por tipo, lida a norma inteira do revogador), 78 eram revogações totais, imediatas e incondicionais (69,0%); com a regra de hoje, 78 de 99 (78,8%, medido na mesma amostra). Os erros: ligação do DRE para outro diploma com o mesmo número (sobretudo diplomas regionais ligados a nacionais), revogações diferidas ou parciais noutro artigo, diplomas só citados (listas de imóveis classificados, notas). Abaixo dos 98%, o estado do DRE não se substitui por esta prova: só os casos verificados entram, como prova manual (`vigencia-manual.jsonl`). Lista e veredictos: `vigencia-texto-contra-dre.jsonl`.

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
