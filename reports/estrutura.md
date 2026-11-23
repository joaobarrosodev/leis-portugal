# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-11-23. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 405.894 | |
| Com texto | 303.334 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 89.545 | 29,5% |
| Só com números do dispositivo (`1.º`, `1 -`) | 74.381 | 24,5% |
| Artigos só nos anexos | 1.886 | 0,6% |
| Sem divisão (texto único) | 137.522 | 45,3% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 63.591; só em texto corrido (novos): 99.309.
- Em vigor com texto: 135.226; com artigos: 39.228 (29,0%); com artigos ou números: 79.068 (58,5%).
- Artigos com id: 1.742.001; números com id: 400.692.
- Diplomas com anexos com artigos: 10.478; com numeração repetida na mesma parte (chave `art-5-2`): 1.531; com ids repetidos: 0.

## Entrada em vigor

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Data calculada a partir da cláusula | 41.351 | 13,6% |
| Só a regra (não dá para calcular) | 10.605 | 3,5% |
| Regra supletiva (5.º dia após a publicação) | 52.426 | 17,3% |
| Sem cláusula e sem regra supletiva | 198.952 | 65,6% |

- Produção de efeitos: 13.676 com data; 5.857 só com a regra.
- Com fim de vigência no texto: 271; com cláusulas parciais (só alguns artigos): 25.526.

Regras mais frequentes que ficam sem data:

- 173 × no dia útil seguinte ao da sua publicação no diário da república
- 169 × no dia útil seguinte ao da sua publicação
- 160 × no primeiro dia útil seguinte ao da sua publicação no diário da república
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
| portugal / série I | 23.234 | 3.323 | 52.426 | 80.455 |
| portugal / série II | 13.281 | 6.936 | 0 | 111.953 |
| regional / série ? | 0 | 0 | 0 | 5 |
| regional / série I | 4.756 | 334 | 0 | 6.112 |
| regional / série II | 80 | 12 | 0 | 427 |

## Vigência desconhecida

Diplomas com `legal_status: unknown`: 204.869. Estado proposto com prova: **697** (not_in_force: 26, repealed: 671).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 26 |
| Provas em conflito (o mesmo revogador, total e parcial) | 7 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 61.890 |
| Só revogação parcial: o resto continua desconhecido | 168 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 51 |
| Revogado (prova de revogação total) | 671 |
| Sem prova | 142.056 |

Revogações lidas nas normas revogatórias: 17.635 (sobre 15.538 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 295 | 9.606 | 828 | 92,3% |
| Relação do DRE (etiqueta) | 0 | 20.605 | 1.132 | 94,8% |

**Texto contra o DRE.** 736 diplomas que o DRE dá em vigor têm uma revogação total lida na norma revogatória de outro diploma do acervo (743 provas). Cada prova tem um segmento: a identidade do diploma ligado (o número do rótulo, a data citada até 20 dias antes da publicação, a entidade e a série) e os sinais contra (alteração registada no DRE depois do revogador, outro revogador ou revogação parcial no DRE, repristinação, declaração de retificação, "legislação em contrário").

| Segmento | Provas | Amostra às cegas | Certos | Precisão ponderada | Wilson 95 % |
| --- | --: | --: | --: | --: | --: |
| a: identidade confirmada (número e data), nacional, sem sinais contra | 511 | 95 | 89 | 93,6% | 86,7% – 97,0% |
| b: só o número confirmado (sem data citada), nacional, sem sinais contra | 34 | 29 | 22 | 75,9% | 57,9% – 87,8% |
| c: algum sinal contra (identidade suspeita, série, alteração posterior, conflito no DRE, repristinação, retificação) ou regional | 198 | 26 | 16 | 61,4% | 41,6% – 78,0% |

Amostra de 2026-11-14 (seed 20261114, 150 casos nunca verificados, estratificada por segmento e tipo): verificadores às cegas e auditoria de todos os "não" e de 20 "sim" (43 de 45 concordam; prevalece a auditoria). A primeira amostra (2026-11-13, 113 casos: 78 certos, 69,0%) serviu para afinar a regra e não conta para a medida. Os erros que ficam: outro diploma com o mesmo número e data próxima (só a matéria os distingue), ressalvas de situações em curso noutro artigo e revogações diferidas. Nenhum segmento chega aos 98%: o estado do DRE não se substitui por esta prova. Só os casos verificados entram, como prova manual (`vigencia-manual.jsonl`). Lista, segmentos e veredictos: `vigencia-texto-contra-dre.jsonl`.

As propostas, com as provas e a proveniência de cada uma, estão em `vigencia-proposta.jsonl`.

### Como se resolve com prova

- **Só uma revogação total fixa o estado** (`repealed`). Conta a norma revogatória de outro diploma do acervo ("É revogado o [Decreto-Lei n.º 253/86]…", com a ligação ao diploma) e a etiqueta da relação do DRE ("Revogado pelo DEC LEI…"). Proveniência: `norma revogatória: <id do revogador>#<artigo>` ou `DRE repealed_by: <id>`.
- **Revogação parcial não resolve**: "os artigos 3.º e 5.º do…" ou "Revogado o nº 5 pela…" ficam registados como prova, mas o resto do diploma continua de vigência desconhecida (não se conclui que está em vigor).
- **Revogações condicionais ou diferidas não contam** ("a partir da entrada em vigor da portaria…", "mantido transitoriamente…"), e uma ligação noutro papel ("na redação dada pelo…", "aprovado pelo…") também não.
- **Relação `repealed_by` sem etiqueta**: não diz se é total ou parcial; fica "por confirmar" até haver o texto do revogador.
- **Caducidade**: só quando o próprio diploma fixa o fim ("vigora até 31 de dezembro de 2013"), a data já passou e o diploma não foi alterado depois (uma alteração pode ter prorrogado a vigência). Proveniência: `cláusula de vigência: <artigo>`.
- **Declarações de retificação** não têm vigência própria: seguem o diploma retificado (relação `corrects`).
- **Só PDF e anteriores a 1960**: sem texto não há prova; ficam marcados como históricos e saem do índice de lei atual, sem mudar `legal_status`.
- Ao escrever nos registos, o estado proposto vai para `legal_status` e as provas para `legal_status_basis`; um conflito entre provas (total num lado, parcial noutro) não muda nada.

### Em vigor por inferência (sem revogação conhecida)

É a única regra que dá um estado sem prova. O DRE deixou de preencher a vigência nos diplomas de 2014 em diante; esta regra dá-os como `in_force` quando nada diz o contrário:

> Diploma legislativo da 1.ª Série publicado de 2014 em diante, com texto, sem revogação conhecida (nenhuma relação «revogado por» no DRE e nenhuma norma revogatória lida no acervo), sem vigência limitada no sumário ou no texto e com a data de entrada em vigor, quando conhecida, já passada.

- **Marca:** `legal_status_basis.source: sem_revogacao_conhecida`, `inferred: true`, `dre_status: unknown` e a regra em `rule`. Não há provas (`evidence` vazio): é a falta delas que a regra usa.
- **Desfaz-se sozinha:** se aparecer uma revogação, uma caducidade ou um estado do DRE, o estado inferido sai. `leis-portugal structure --sem-vigencia-inferida` devolve todos a `unknown`.
- **Diplomas:** 1.893 (decreto-legislativo-regional: 321, decreto-lei: 913, decreto-regulamentar: 49, lei: 583, lei-organica: 27).
- **Ficam de fora, de vigência desconhecida:** com a entrada em vigor ainda por chegar: 5; anteriores a 2014: 7; com alguma prova de revogação ou caducidade, mesmo parcial: 45; temporários pelo sumário: 348; com vigência limitada no próprio texto: 140.
- **Amostra conferida (2026-11-20):** 300 diplomas ao acaso, 283 aceites pela regra; 0 com revogação e 1 com vigência limitada que a regra não viu (Lei n.º 51/2023: lei de política criminal para o biénio de 2023-2025, já findo; a regra do sumário foi alargada depois). Limite superior do erro a 95 %: 1,7 %.
- **O que quer dizer:** que não se conhece revogação nem caducidade. Um ato de alteração fica «em vigor» mesmo com o conteúdo já gasto.
- Lista: `vigencia-inferida.jsonl`.

## Validação do parser contra os consolidados do DRE

Amostra: 177 diplomas consolidados (de 8.577), comparando os artigos do parser com os fragmentos de artigo dos `.versoes.json`.

| Texto | Diplomas | Mesmo n.º de artigos | Números e epígrafes iguais | Mesmas partes | Epígrafes iguais |
| --- | --: | --: | --: | --: | --: |
| Atual (`.md`) | 177 | 96,6% | 95,5% | 97,2% | 5.568 de 5.825 |
| Original (1.ª versão) | 149 | 99,3% | 98,0% | 97,3% | 4.735 de 4.885 |

Diferenças (texto atual):

- `data/portugal/despachos-normativos/1984/despacho-normativo-131-84.md`: parser 0, DRE 21; primeira diferença: null
- `data/portugal/despachos-normativos/1984/despacho-normativo-150-84.md`: parser 0, DRE 2; primeira diferença: null
- `data/portugal/leis/2004/lei-55-b-2004.md`: parser 79, DRE 79; primeira diferença: {"posicao": 44, "parser": ["", "45.º", ""], "dre": ["", "45.º", "Transposição da Directiva n.º 2003/123/CE, do Conselho, de 22 de Dezembro, que altera a Directiva n.º 90/435/CEE, de 23 de Julho, relativa ao regime fiscal comum aplicável às sociedades mãe e sociedades afiliadas de Estados membros diferentes"]}
- `data/portugal/portarias/1999/portaria-564-99.md`: parser 5, DRE 33; primeira diferença: {"posicao": 2, "parser": ["Anexo — PROTOCOLO DO CENTRO DE REABILITAÇÃO PROFISSIONAL DE GAIA", "XX", "Plano de atividades, orçamento e relatórios de controlo orçamental"], "dre": ["Anexo — PROTOCOLO DO CENTRO DE REABILITAÇÃO PROFISSIONAL DE GAIA", "I", "Denominação"]}
- `data/portugal/portarias/2003/portaria-953-2003.md`: parser 0, DRE 3; primeira diferença: null
- `data/portugal/portarias/2005/portaria-590-a-2005.md`: parser 0, DRE 5; primeira diferença: null
- `data/portugal/portarias/2008/portaria-1532-2008.md`: parser 359, DRE 357; primeira diferença: {"posicao": 166, "parser": ["Anexo — Regulamento técnico de segurança contra incêndio em edifícios", "162.º", "Critérios de segurança"], "dre": ["Anexo — Regulamento técnico de segurança contra incêndio em edifícios", "163.º", "Utilização de meios portáteis e móveis de extinção"]}
- `data/portugal/portarias/2025/portaria-219-2025-1.md`: parser 24, DRE 24; primeira diferença: {"posicao": 16, "parser": ["Anexo — Republicação da Portaria n.º 243/2020, de 14 de outubro", "9.º", ""], "dre": ["Anexo — Republicação da Portaria n.º 243/2020, de 14 de outubro", "9.º", "Circulação para fora de uma área demarcada, e a partir das respetivas zonas infetadas para as zonas-tampão, de vegetais especificados que tenham sido cultivados em locais de produção autorizados situados nessa área demarcada"]}
