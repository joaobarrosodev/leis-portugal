# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-11-20. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 405.854 | |
| Com texto | 303.294 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 89.512 | 29,5% |
| Só com números do dispositivo (`1.º`, `1 -`) | 74.380 | 24,5% |
| Artigos só nos anexos | 1.886 | 0,6% |
| Sem divisão (texto único) | 137.516 | 45,3% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 63.539; só em texto corrido (novos): 99.327.
- Em vigor com texto: 135.209; com artigos: 39.207 (29,0%); com artigos ou números: 79.054 (58,5%).
- Artigos com id: 1.741.391; números com id: 400.682.
- Diplomas com anexos com artigos: 10.475; com numeração repetida na mesma parte (chave `art-5-2`): 1.532; com ids repetidos: 0.

## Entrada em vigor

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Data calculada a partir da cláusula | 41.338 | 13,6% |
| Só a regra (não dá para calcular) | 10.605 | 3,5% |
| Regra supletiva (5.º dia após a publicação) | 52.415 | 17,3% |
| Sem cláusula e sem regra supletiva | 198.936 | 65,6% |

- Produção de efeitos: 13.676 com data; 5.858 só com a regra.
- Com fim de vigência no texto: 271; com cláusulas parciais (só alguns artigos): 25.537.

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
| portugal / série I | 23.225 | 3.326 | 52.415 | 80.448 |
| portugal / série II | 13.277 | 6.934 | 0 | 111.945 |
| regional / série ? | 0 | 0 | 0 | 5 |
| regional / série I | 4.756 | 333 | 0 | 6.111 |
| regional / série II | 80 | 12 | 0 | 427 |

## Vigência desconhecida

Diplomas com `legal_status: unknown`: 204.852. Estado proposto com prova: **697** (not_in_force: 26, repealed: 671).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 26 |
| Provas em conflito (o mesmo revogador, total e parcial) | 7 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 61.890 |
| Só revogação parcial: o resto continua desconhecido | 168 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 51 |
| Revogado (prova de revogação total) | 671 |
| Sem prova | 142.039 |

Revogações lidas nas normas revogatórias: 17.666 (sobre 15.564 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 289 | 9.625 | 834 | 92,2% |
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

Amostra: 179 diplomas consolidados (de 8.533), comparando os artigos do parser com os fragmentos de artigo dos `.versoes.json`.

| Texto | Diplomas | Mesmo n.º de artigos | Números e epígrafes iguais | Mesmas partes | Epígrafes iguais |
| --- | --: | --: | --: | --: | --: |
| Atual (`.md`) | 179 | 98,3% | 97,2% | 98,9% | 7.904 de 7.950 |
| Original (1.ª versão) | 149 | 99,3% | 99,3% | 99,3% | 5.945 de 5.958 |

Diferenças (texto atual):

- `data/portugal/decretos-leis/2009/decreto-lei-71-2009.md`: parser 88, DRE 87; primeira diferença: {"posicao": 74, "parser": ["Anexo — REGULAMENTO CONSULAR", "63.º", "Funções culturais, educativas, económicas, comerciais, sociais e outras"], "dre": ["Anexo — REGULAMENTO CONSULAR", "64.º", "Funções culturais e educativas"]}
- `data/portugal/decretos-leis/2024/decreto-lei-17-2024.md`: parser 163, DRE 163; primeira diferença: {"posicao": 45, "parser": ["", "46.º", ""], "dre": ["", "46.º", "Assunção de compromissos plurianuais relativos a contratos financiados pelo Fundo Europeu de Desenvolvimento Regional, pelo Fundo Social Europeu, pelo Fundo de Coesão e pelo Fundo para Uma Transição Justa"]}
- `data/portugal/decretos-leis/2024/decreto-lei-99-2024.md`: parser 455, DRE 455; primeira diferença: {"posicao": 376, "parser": ["Parte 2", "V", ""], "dre": ["Anexo — Republicação do Decreto-Lei n.º 15/2022, de 14 de janeiro", "V", "Princípios aplicáveis às relações com a concessionária da rede nacional de transporte de eletricidade, produtores, distribuidores em baixa tensão, comercializadores, agregadores e outros utilizadores das redes"]}
- `data/portugal/portarias/1999/portaria-387-99.md`: parser 25, DRE 28; primeira diferença: {"posicao": 0, "parser": ["Anexo — REGULAMENTO DE AUTORIZAÇÕES ESPECIAIS DE TRÂNSITO", "1.º", "Âmbito de aplicação"], "dre": ["", "1.º", ""]}
- `data/portugal/portarias/2013/portaria-55-2013.md`: parser 5, DRE 6; primeira diferença: null
