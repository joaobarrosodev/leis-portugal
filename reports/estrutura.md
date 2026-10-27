# Estrutura, entrada em vigor e vigência: cobertura

Gerado por `leis-portugal structure --dry-run` em 2026-10-27. Nenhum registo foi alterado.

## Artigos

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Registos portugueses e regionais | 304.801 | |
| Com texto | 212.164 | 100% |
| Com artigos identificados (artigos, bases ou cláusulas) | 63.662 | 30,0% |
| Só com números do dispositivo (`1.º`, `1 -`) | 58.220 | 27,4% |
| Artigos só nos anexos | 531 | 0,3% |
| Sem divisão (texto único) | 89.751 | 42,3% |

- Diplomas com artigos identificados por títulos `######` (o que o export conta hoje): 38.933; só em texto corrido (novos): 82.048.
- Em vigor com texto: 128.778; com artigos: 37.050 (28,8%); com artigos ou números: 76.353 (59,3%).
- Artigos com id: 967.031; números com id: 285.117.
- Diplomas com anexos com artigos: 6.429; com numeração repetida na mesma parte (chave `art-5-2`): 878; com ids repetidos: 0.

## Entrada em vigor

| | Diplomas | % dos com texto |
| --- | --: | --: |
| Data calculada a partir da cláusula | 30.926 | 14,6% |
| Só a regra (não dá para calcular) | 4.064 | 1,9% |
| Regra supletiva (5.º dia após a publicação) | 52.392 | 24,7% |
| Sem cláusula e sem regra supletiva | 124.782 | 58,8% |

- Produção de efeitos: 12.179 com data; 5.071 só com a regra.
- Com fim de vigência no texto: 227; com cláusulas parciais (só alguns artigos): 17.928.

Regras mais frequentes que ficam sem data:

- 126 × no dia seguinte ao da sua assinatura
- 113 × no dia útil seguinte ao da sua publicação
- 106 × na data da sua assinatura
- 82 × no N.º dia útil seguinte ao da sua publicação
- 82 × no primeiro dia útil seguinte ao da sua publicação
- 67 × no N.º dia útil do mês seguinte ao da sua publicação
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
| portugal / série I | 23.177 | 3.321 | 52.392 | 76.502 |
| portugal / série II | 2.940 | 409 | 0 | 41.995 |
| regional / série ? | 0 | 0 | 0 | 4 |
| regional / série I | 4.753 | 333 | 0 | 6.065 |
| regional / série II | 56 | 1 | 0 | 216 |

## Vigência desconhecida

Diplomas com `legal_status: unknown`: 113.906. Estado proposto com prova: **393** (not_in_force: 22, repealed: 371).

| Categoria | Diplomas |
| --- | --: |
| Caducado (vigência temporária já passada, sem alterações) | 22 |
| Provas em conflito (o mesmo revogador, total e parcial) | 9 |
| Só PDF e anterior a 1960: histórico, fora do índice de lei atual | 55.742 |
| Só revogação parcial: o resto continua desconhecido | 137 |
| Revogação sem âmbito conhecido (relação sem etiqueta) | 6 |
| Revogado (prova de revogação total) | 371 |
| Sem prova | 57.619 |

Revogações lidas nas normas revogatórias: 18.452 (sobre 15.987 diplomas).

Precisão das provas de revogação total nos diplomas cujo estado o DRE conhece:

| Prova | DRE: revogado | DRE: sem vigência | DRE: em vigor | Concordam |
| --- | --: | --: | --: | --: |
| Norma revogatória (texto) | 326 | 10.382 | 1.360 | 88,7% |
| Relação do DRE (etiqueta) | 0 | 20.762 | 1.261 | 94,3% |

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

Amostra: 265 diplomas consolidados (de 5.664), comparando os artigos do parser com os fragmentos de artigo dos `.versoes.json`.

| Texto | Diplomas | Mesmo n.º de artigos | Números e epígrafes iguais | Mesmas partes | Epígrafes iguais |
| --- | --: | --: | --: | --: | --: |
| Atual (`.md`) | 265 | 97,4% | 95,8% | 98,5% | 10.578 de 10.826 |
| Original (1.ª versão) | 228 | 97,8% | 96,9% | 97,4% | 8.607 de 8.801 |

Diferenças (texto atual):

- `data/portugal/decretos-governo/1984/decreto-governo-28-84.md`: parser 1, DRE 1; primeira diferença: {"posicao": 0, "parser": ["", "único", ""], "dre": ["", "Annexe 6.º", ""]}
- `data/portugal/decretos-leis/2013/decreto-lei-154-2013.md`: parser 35, DRE 34; primeira diferença: {"posicao": 19, "parser": ["", "20.º", "Efeitos do reconhecimento como projeto PIN"], "dre": ["", "21.º", "Simultaneidade dos procedimentos"]}
- `data/portugal/decretos-leis/2014/decreto-lei-187-2014.md`: parser 39, DRE 37; primeira diferença: {"posicao": 5, "parser": ["", "6.º", "Estrutura orgânica"], "dre": ["", "8.º", "Competência do Chefe do Estado-Maior da Força Aérea"]}
- `data/portugal/decretos-leis/2016/decreto-lei-64-2016.md`: parser 147, DRE 143; primeira diferença: {"posicao": 39, "parser": ["Anexo II — (a que se refere o artigo 6.º)", "4.º", "Âmbito de aplicação"], "dre": ["Anexo II — (a que se refere o artigo 6.º)", "6.º", "Procedimentos de diligência devida para as contas de menor valor"]}
- `data/portugal/decretos-leis/2017/decreto-lei-18-2017.md`: parser 120, DRE 117; primeira diferença: {"posicao": 44, "parser": ["Anexo II — ESTATUTOS DOS HOSPITAIS, CENTROS HOSPITALARES E INSTITUTOS PORTUGUESES DE ONCOLOGIA, E. P. E.", "5.º", "Órgãos"], "dre": ["Anexo II — ESTATUTOS DOS HOSPITAIS, CENTROS HOSPITALARES E INSTITUTOS PORTUGUESES DE ONCOLOGIA, E. P. E.", "6.º", "Composição e mandato"]}
- `data/portugal/decretos-leis/2022/decreto-lei-15-2022.md`: parser 463, DRE 463; primeira diferença: {"posicao": 385, "parser": ["ANEXO III — Bases da concessão da Rede Nacional de Distribuição de Eletricidade em Média e Alta Tensão", "V", ""], "dre": ["ANEXO III — Bases da concessão da Rede Nacional de Distribuição de Eletricidade em Média e Alta Tensão", "V", "Princípios aplicáveis às relações com a concessionária da rede nacional de transporte de eletricidade, produtores, distribuidores em baixa tensão, comercializadores, agregadores e outros utilizadores das redes"]}
- `data/portugal/decretos-leis/2023/decreto-lei-10-2023.md`: parser 162, DRE 162; primeira diferença: {"posicao": 46, "parser": ["", "47.º", ""], "dre": ["", "47.º", "Assunção de compromissos plurianuais relativos a contratos financiados pelo Fundo Europeu de Desenvolvimento Regional, pelo Fundo Social Europeu, pelo Fundo de Coesão e pelo Fundo para uma Transição Justa"]}
- `data/portugal/decretos/1980/decreto-50-80.md`: parser 51, DRE 51; primeira diferença: {"posicao": 26, "parser": ["Convention on International Trade in Endangered Species of Wild Fauna and Flora", "I", "Definitions"], "dre": ["Convention on International Trade in Endangered Species of Wild Fauna and Flora", "Article I", "Definitions"]}
- `data/portugal/portarias/1986/portaria-55-c-86.md`: parser 0, DRE 11; primeira diferença: null
- `data/portugal/portarias/2000/portaria-1226-du-2000.md`: parser 0, DRE 12; primeira diferença: null
- `data/portugal/regimentos/2007/regimento-assembleia-republica-1-2007.md`: parser 271, DRE 270; primeira diferença: null
