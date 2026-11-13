# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-11-13. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 323.151 | |
| Com texto | 221.978 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 66.110 | 29,8% |
| Só com números do dispositivo (`1.º`, `1 -`) | 58.666 | 26,4% |
| Artigos só nos anexos | 593 | 0,3% |
| Sem divisão (texto único) | 96.609 | 43,5% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 40.234; só em texto corrido (novos): 83.635.
- Em vigor com texto: 134.286; com artigos: 38.911 (29,0%); com artigos ou números: 78.355 (58,3%).
- Artigos com id: 994.525; números com id: 286.709.
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

Diplomas com `legal_status: unknown`: 124.275. Estado proposto com prova: **352** (not_in_force: 22, repealed: 330).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 22 |
| Provas em conflito (o mesmo revogador, total e parcial) | 6 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 61.808 |
| Só revogação parcial: o resto continua desconhecido | 138 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 49 |
| Revogado (prova de revogação total) | 330 |
| Sem prova | 61.922 |

Revogações lidas nas normas revogatórias: 17.623 (sobre 15.316 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 312 | 9.947 | 951 | 91,5% |
| Relação do DRE (etiqueta) | 0 | 20.410 | 1.106 | 94,9% |

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

## Validação do parser contra os consolidados do DRE

Amostra: 177 diplomas consolidados (de 8.381), comparando os artigos do parser com os fragmentos de artigo dos `.versoes.json`.

| Texto | Diplomas | Mesmo n.º de artigos | Números e epígrafes iguais | Mesmas partes | Epígrafes iguais |
| --- | --: | --: | --: | --: | --: |
| Atual (`.md`) | 177 | 97,2% | 96,0% | 98,3% | 6.444 de 6.554 |
| Original (1.ª versão) | 152 | 98,7% | 98,7% | 98,0% | 5.115 de 5.170 |

Diferenças (texto atual):

- `data/portugal/decretos-leis/1988/decreto-lei-5-a-88.md`: parser 50, DRE 49; primeira diferença: {"posicao": 2, "parser": ["", "3.º", "Órgãos e serviços"], "dre": ["", "4.º", "Presidente"]}
- `data/portugal/decretos-leis/2000/decreto-lei-281-2000.md`: parser 22, DRE 22; primeira diferença: {"posicao": 5, "parser": ["", "4.º-A", ""], "dre": ["", "4.º-A", "Teor de enxofre máximo nos combustíveis navais utilizados em mares territoriais, zonas económicas exclusivas e zonas de controlo da poluição, incluindo zonas de controlo das emissões de SO(índice x) e pelos navios de passageiros que efetuam serviços regulares com partida ou destino em portos da União Europeia."]}
- `data/portugal/decretos-leis/2015/decreto-lei-163-2015.md`: parser 39, DRE 39; primeira diferença: {"posicao": 15, "parser": ["", "16.º", ""], "dre": ["", "16.º", "Contraordenações no âmbito do Regulamento (UE) 2015/340, da Comissão, de 20 de fevereiro de 2015, e da secção vi do Regulamento (UE) 2018/1139, do Parlamento Europeu e do Conselho, de 4 de julho de 2018"]}
- `data/portugal/portarias/2000/portaria-1226-du-2000.md`: parser 0, DRE 12; primeira diferença: null
- `data/portugal/portarias/2015/portaria-373-2015.md`: parser 56, DRE 55; primeira diferença: {"posicao": 19, "parser": ["", "20.º", "Escolas de formação de nadadores-salvadores profissionais"], "dre": ["", "21.º", "Organização interna"]}
- `data/portugal/portarias/2024/portaria-155-a-2024-1.md`: parser 10, DRE 8; primeira diferença: {"posicao": 5, "parser": ["", "6.º", "[...]"], "dre": ["", "6.º", "Alteração ao anexo iv da Portaria n.º 54-Q/2023, de 27 de fevereiro"]}
- `data/portugal/resolucoes-conselho-ministros/1997/resolucao-conselho-ministros-13-97.md`: parser 1, DRE 8; primeira diferença: {"posicao": 0, "parser": ["", "6.º", "Natureza e cálculo dos incentivos a fundo perdido"], "dre": ["", "1.º", "Candidaturas"]}
