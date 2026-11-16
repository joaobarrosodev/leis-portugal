# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-11-16. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 405.785 | |
| Com texto | 303.225 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 89.495 | 29,5% |
| Só com números do dispositivo (`1.º`, `1 -`) | 74.362 | 24,5% |
| Artigos só nos anexos | 1.883 | 0,6% |
| Sem divisão (texto único) | 137.485 | 45,3% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 63.518; só em texto corrido (novos): 99.315.
- Em vigor com texto: 135.183; com artigos: 39.201 (29,0%); com artigos ou números: 79.044 (58,5%).
- Artigos com id: 1.740.849; números com id: 400.592.
- Diplomas com anexos com artigos: 10.467; com numeração repetida na mesma parte (chave `art-5-2`): 1.532; com ids repetidos: 0.

## Entrada em vigor

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Data calculada a partir da cláusula | 41.322 | 13,6% |
| Só a regra (não dá para calcular) | 10.602 | 3,5% |
| Regra supletiva (5.º dia após a publicação) | 52.415 | 17,3% |
| Sem cláusula e sem regra supletiva | 198.886 | 65,6% |

- Produção de efeitos: 13.670 com data; 5.851 só com a regra.
- Com fim de vigência no texto: 271; com cláusulas parciais (só alguns artigos): 25.525.

Regras mais frequentes que ficam sem data:

- 173 × no dia útil seguinte ao da sua publicação no diário da república
- 169 × no dia útil seguinte ao da sua publicação
- 159 × no primeiro dia útil seguinte ao da sua publicação no diário da república
- 127 × no dia seguinte ao da sua assinatura
- 116 × no primeiro dia útil seguinte ao da sua publicação
- 108 × na data da sua assinatura
- 108 × no primeiro dia útil seguinte à sua publicação no diário da república
- 95 × no N.º dia útil seguinte ao da sua publicação
- 95 × no primeiro dia útil após a sua publicação no diário da república
- 89 × no primeiro dia útil do mês seguinte ao da sua publicação
- 81 × no dia seguinte ao da sua aprovação
- 80 × após publicação no diário da república
- 78 × no ano letivo N/N
- 73 × no dia útil seguinte à sua publicação no diário da república
- 70 × no N.º dia útil do mês seguinte ao da sua publicação

Por jurisdição e série:

| | Com data | Só regra | Supletiva | Sem cláusula |
| --- | --: | --: | --: | --: |
| portugal / série I | 23.216 | 3.324 | 52.415 | 80.448 |
| portugal / série II | 13.271 | 6.933 | 0 | 111.895 |
| regional / série ? | 0 | 0 | 0 | 5 |
| regional / série I | 4.755 | 333 | 0 | 6.111 |
| regional / série II | 80 | 12 | 0 | 427 |

## Vigência desconhecida

Diplomas com `legal_status: unknown`: 204.814. Estado proposto com prova: **696** (not_in_force: 26, repealed: 670).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 26 |
| Provas em conflito (o mesmo revogador, total e parcial) | 7 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 61.890 |
| Só revogação parcial: o resto continua desconhecido | 168 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 51 |
| Revogado (prova de revogação total) | 670 |
| Sem prova | 142.002 |

Revogações lidas nas normas revogatórias: 17.696 (sobre 15.587 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 292 | 9.635 | 840 | 92,2% |
| Relação do DRE (etiqueta) | 0 | 20.605 | 1.123 | 94,8% |

**Texto contra o DRE.** 742 diplomas que o DRE dá em vigor têm uma revogação total lida na norma revogatória de outro diploma do acervo (749 provas). Cada prova tem um segmento: a identidade do diploma ligado (o número do rótulo, a data citada até 20 dias antes da publicação, a entidade e a série) e os sinais contra (alteração registada no DRE depois do revogador, outro revogador ou revogação parcial no DRE, repristinação, declaração de retificação, "legislação em contrário").

| Segmento | Provas | Amostra às cegas | Certos | Precisão ponderada | Wilson 95 % |
| --- | --: | --: | --: | --: | --: |
| a: identidade confirmada (número e data), nacional, sem sinais contra | 515 | 95 | 89 | 93,6% | 86,7% – 97,0% |
| b: só o número confirmado (sem data citada), nacional, sem sinais contra | 36 | 29 | 22 | 75,9% | 57,9% – 87,8% |
| c: algum sinal contra (identidade suspeita, série, alteração posterior, conflito no DRE, repristinação, retificação) ou regional | 198 | 26 | 16 | 61,4% | 41,6% – 78,0% |

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

## Validação do parser contra os consolidados do DRE

Amostra: 179 diplomas consolidados (de 8.404), comparando os artigos do parser com os fragmentos de artigo dos `.versoes.json`.

| Texto | Diplomas | Mesmo n.º de artigos | Números e epígrafes iguais | Mesmas partes | Epígrafes iguais |
| --- | --: | --: | --: | --: | --: |
| Atual (`.md`) | 179 | 97,8% | 95,5% | 98,9% | 6.603 de 6.731 |
| Original (1.ª versão) | 148 | 98,0% | 97,3% | 99,3% | 5.139 de 5.259 |

Diferenças (texto atual):

- `data/portugal/decretos-leis/1988/decreto-lei-5-a-88.md`: parser 50, DRE 49; primeira diferença: {"posicao": 2, "parser": ["", "3.º", "Órgãos e serviços"], "dre": ["", "4.º", "Presidente"]}
- `data/portugal/decretos-leis/2000/decreto-lei-281-2000.md`: parser 22, DRE 22; primeira diferença: {"posicao": 5, "parser": ["", "4.º-A", ""], "dre": ["", "4.º-A", "Teor de enxofre máximo nos combustíveis navais utilizados em mares territoriais, zonas económicas exclusivas e zonas de controlo da poluição, incluindo zonas de controlo das emissões de SO(índice x) e pelos navios de passageiros que efetuam serviços regulares com partida ou destino em portos da União Europeia."]}
- `data/portugal/decretos-leis/2015/decreto-lei-163-2015.md`: parser 39, DRE 39; primeira diferença: {"posicao": 15, "parser": ["", "16.º", ""], "dre": ["", "16.º", "Contraordenações no âmbito do Regulamento (UE) 2015/340, da Comissão, de 20 de fevereiro de 2015, e da secção vi do Regulamento (UE) 2018/1139, do Parlamento Europeu e do Conselho, de 4 de julho de 2018"]}
- `data/portugal/portarias/2000/portaria-1177-2000.md`: parser 13, DRE 15; primeira diferença: {"posicao": 8, "parser": ["", "9.º", ""], "dre": ["", "8.º-A", ""]}
- `data/portugal/portarias/2015/portaria-50-2015.md`: parser 80, DRE 77; primeira diferença: {"posicao": 7, "parser": ["", "8.º", "Objetivos"], "dre": ["", "9.º", "Critérios de elegibilidade"]}
- `data/portugal/portarias/2023/portaria-175-2023.md`: parser 8, DRE 6; primeira diferença: null
- `data/regional/acores/decretos-legislativos-regionais/2020/decreto-legislativo-regional-1-2020-a.md`: parser 93, DRE 93; primeira diferença: {"posicao": 49, "parser": ["", "48.º", ""], "dre": ["", "48.º", "Décima quarta alteração ao Decreto Legislativo Regional n.º 8/2002/A, de 10 de abril, na sua atual redação, que estabelece o regime jurídico da atribuição do acréscimo regional à retribuição mínima mensal garantida, do complemento regional de pensão e da remuneração complementar regional"]}
- `data/regional/acores/decretos-legislativos-regionais/2021/decreto-legislativo-regional-15-a-2021-a.md`: parser 91, DRE 91; primeira diferença: {"posicao": 88, "parser": ["", "91.º", ""], "dre": ["", "91.º", "Alteração do limite mínimo de autofinanciamento das associações beneficiárias de apoio no âmbito do Programa de Incentivo ao Associativismo Juvenil, designado de PIAJ, e Programa de Apoio ao Empreendedorismo Social das Associações de Juventude, designado por PAESAJ"]}
