# Casos de advogado (26/11/2026)

39 casos escritos como um advogado os poria na app: «o contexto é este, aconteceu isto ao meu cliente, estou a pensar usar estas leis». Cada um tem a resposta de referência: os artigos que decidem, se as leis pensadas servem, o que fazer, os prazos contados e o que fica a depender de prova. É o primeiro passo do objetivo de análise de caso: medir antes de construir o fluxo.

## O conjunto

| Área | Casos | Base | Média | Alta |
|---|--:|--:|--:|--:|
| Trabalho | 9 | 2 | 4 | 3 |
| Arrendamento e condomínio | 5 | 1 | 1 | 3 |
| Consumo e contratos | 5 | 1 | 1 | 3 |
| Família e sucessões | 5 | 1 | 2 | 2 |
| Responsabilidade civil, viação e seguros | 5 | 1 | 1 | 3 |
| Empresas, insolvência e dívidas | 5 | 1 | 2 | 2 |
| Administrativo, fiscal e contraordenações | 5 | 1 | 2 | 2 |
| **Total** | **39** | **8** | **13** | **18** |

- 161 artigos essenciais (2 a 5 por caso) e 56 leis pensadas que não servem ou servem só em parte, em 34 casos.
- Factos de 2025 e 2026 e data de referência 26/11/2026: vale o texto em vigor hoje.
- Penal e processo penal ficaram de fora desta primeira versão.

**Como se fizeram.**
- **Escrita:** 8 subagentes Opus, um por área, com as regras de [`REGRAS.md`](REGRAS.md). Não podiam abrir as perguntas de avaliação nem o código da pesquisa. Leram cada artigo do acervo com [`artigo.py`](artigo.py), o mesmo leitor do índice.
- **Verificação mecânica:** `artigo.py verificar` confirma que cada artigo existe com a chave e a epígrafe ditas e que não está revogado. Confirma também que o excerto está no texto, letra a letra. Dá 0 erros.
- **Revisão adversarial:** 2 subagentes Opus, 20 casos cada, a procurar erros e não a confirmar. Das 40 versões escritas, 27 passaram sem mudança e 12 foram corrigidas:
  - prazos que caíam num domingo ou em férias judiciais;
  - uma narrativa que se contradizia;
  - uma norma decisiva em falta (a letra pequena das cláusulas gerais);
  - uma infração permanente que mudava a prescrição.

  Saiu 1 caso por repetir outro (o antigo `caso-trab-04`).
- **Sem jurista.** A referência foi escrita e revista por modelos. Antes de valer como referência real, precisa de uma revisão por um advogado, que pode ser feita sem lhe mostrar o produto.

## Medição de base (26/11/2026)

### Pesquisa, como a app 0.1.1

O índice é o publicado na versão `2026-11-24.2`, com o reranker cruzado e 30 candidatos. O script é [`medir.py`](medir.py) e o resultado está em `rag/resultados/casos-base.json`.

| | Texto inteiro numa consulta (a app hoje) | Uma consulta por questão (questões escritas à mão) |
|---|--:|--:|
| Essenciais em 1.º | 7 de 161 | 17 de 161 |
| Essenciais nos 8 primeiros | 33 de 161 (20 %) | 48 de 161 (30 %) |
| Essenciais nos 30 primeiros | 43 de 161 | 81 de 161 |
| Casos com todos os essenciais nos 8 primeiros | 1 de 39 | 1 de 39 |
| Casos com pelo menos um essencial nos 8 primeiros | 21 de 39 | 30 de 39 |

- A pesquisa encontra o diploma certo (o Código do Trabalho, o Código Civil) mas não o artigo. Um texto longo, com muitos factos, puxa artigos que partilham palavras com a narrativa.
- Em 27 dos 39 casos a melhor nota do reranker fica abaixo de 3. Com o limiar da app, a resposta seria «não sei».
- As instruções do LLM da app 0.1.1 mandam recusar «aconselhamento sobre um caso concreto». Com a app tal como está, a análise de caso não existe.

**Citações sem «artigo» (26/11/2026).** Os advogados citam «o 394.º do CT» ou «359.º e seguintes do CT», e a pesquisa só reconhecia «artigo 394.º». O `rag/referencias.py` passou a contar um número com «º» quando vem logo seguido de «do/da» e de um código («12.º ano» e «4.º esquerdo» ficam de fora). Com o texto inteiro, os essenciais nos 8 primeiros passam de 33 para 39 (7 ganhos, 1 perda) e os em 1.º de 7 para 12; os casos cobertos ficam em 1 (`rag/resultados/casos-artigo-solto.json`). Nas 1.298 perguntas de avaliação nenhuma muda de referências, por isso a medição de sempre não se altera. Só chega à app numa versão nova.

### Análise com um LLM (experimental)

Um subagente Opus analisa cada caso só com os artigos dados, com as regras de [`INSTRUCOES-resposta.md`](INSTRUCOES-resposta.md). Depois, 2 juízes Opus julgam a análise, às cegas um do outro, com a referência na mão: o juiz «a» é exigente e o «b» é cético ([`INSTRUCOES-juiz.md`](INSTRUCOES-juiz.md)). Uma análise só conta como certa quando os dois juízes lhe dão «certa». O script é [`juizes.py`](juizes.py) e os resultados estão em `rag/resultados/casos-llm-*.json`.

| | Contexto ideal | Os 16 artigos da pesquisa |
|---|--:|--:|
| Certas (os 2 juízes) | 38 de 39 | **5 de 39** |
| Parciais (juiz a / b) | 1 / 0 | 27 / 26 |
| Erradas para algum juiz | 1 | 3 |
| Recusas | 0 | 4 |
| Essenciais no contexto | 161 de 161 | 40 de 161 |
| Leis pensadas que não servem, assinaladas | 56 de 56 / 57 de 57 | 22 de 56 |
| Prazos certos (juiz a / b) | 37 / 36 | 9 / 12 |

- **Contexto ideal:** os artigos essenciais e úteis da referência, mais os das leis pensadas, por uma ordem baralhada, com o script [`exportar_ideal.py`](exportar_ideal.py). Mede o raciocínio sem a pesquisa. É um teto otimista: quem escreveu, quem respondeu e quem julgou são todos Opus, e os artigos dados são os da própria referência.
- **Os 16 artigos da pesquisa:** os primeiros da consulta de texto inteiro, como a app os daria ao LLM, mas 16 e não 8.
- **As 3 erradas** são prazos dados como abertos ou mal contados, quando o artigo do prazo não estava no contexto:
  - a renovação do arrendamento por um ano em vez de três (`caso-arr-02`);
  - a suspensão da deliberação já fora de prazo e os 60 dias da anulação contados da carta (`caso-arr-05`);
  - a suspensão da deliberação social fora de prazo (`caso-emp-01`).

  É o erro mais perigoso para um advogado.
- **Por área, certas com a pesquisa:** trabalho 2 de 9, arrendamento 1 de 5, consumo 1 de 5, empresas 1 de 5; família, responsabilidade e administrativo 0 de 5 cada.

### O caso partido em consultas (experimental, 26/11/2026)

Dois subagentes Opus receberam só o pedido do advogado, sem a referência, e escreveram 3 a 6 consultas curtas por caso, uma por questão jurídica e no vocabulário da lei, com o nome do código e sem números de artigos ([`decomposicao/INSTRUCOES.md`](decomposicao/INSTRUCOES.md)). À parte, puderam listar os artigos que achavam decisivos. Fizeram 224 consultas e listaram 200 artigos prováveis. A pesquisa faz uma busca por consulta, como a 0.1.1, e intercala os resultados: o 1.º de cada consulta, depois o 2.º, e assim por diante. Na variante «com artigos», cada artigo provável é mais uma busca, e entra o seu 1.º resultado (`medir.py --decomposicao`, `rag/resultados/casos-decomposto.json`).

| | Texto inteiro | Consultas | Consultas e artigos prováveis |
|---|--:|--:|--:|
| Essenciais em 1.º | 7 | 32 | 31 |
| Essenciais nos 8 primeiros | 33 de 161 | 125 de 161 | 127 de 161 |
| Essenciais nos 16 primeiros | — | 141 | 144 |
| Casos com todos os essenciais nos 8 primeiros | 1 de 39 | 16 de 39 | 18 de 39 |
| Casos com todos os essenciais nos 16 primeiros | — | 23 de 39 | 25 de 39 |

Depois a análise com o LLM: os 16 primeiros da variante com artigos, as mesmas instruções e os mesmos dois juízes (`rag/resultados/casos-llm-decomposto.json`).

| Análise com LLM | Texto inteiro | Consultas e artigos prováveis | Contexto ideal |
|---|--:|--:|--:|
| Certas (os 2 juízes) | 5 de 39 | **31 de 39** | 38 de 39 |
| Erradas | 3 | 1 | 1 |
| Leis pensadas que não servem, assinaladas (juiz a) | 22 de 56 | 55 de 57 | 56 de 56 |
| Prazos certos (juiz a) | 9 | 32 | 37 |

- **Concordância:** os dois juízes dão o mesmo veredicto a cada um dos 39 casos.
- **A errada** é o `caso-arr-01`: o sistema manda repetir a resolução por carta registada, mas sem domicílio convencionado a lei exige notificação avulsa ou contacto pessoal (art. 9.º, n.º 7, do NRAU).
- **As 7 parciais:** 3 do trabalho, 3 da responsabilidade civil e 1 do arrendamento.
- **Por área, certas:**

  | Área | Certas |
  |---|--:|
  | Consumo, família, empresas e administrativo | 5 de 5 cada |
  | Trabalho | 6 de 9 |
  | Arrendamento | 3 de 5 |
  | Responsabilidade civil | 2 de 5 |

- **Ressalvas:**
  - Quem partiu os casos, quem respondeu, quem julgou e quem escreveu os casos são todos o mesmo modelo, e o modelo conhece a lei por si.
  - Sem jurista, isto mostra o caminho e não é um número para dizer em público.
  - Na app, partir o caso exige um passo de LLM antes da pesquisa, como a reescrita.

### A peça do sistema e outro modelo (26/11/2026, tarde)

**A peça do sistema.** O passo de partir o caso está em `rag/caso.py`, com as regras em `rag/CASO-PARTIR.md` e `rag/CASO-ANALISE.md`, que são as desta medição. O `medir.py --decomposicao` passou a pesquisar com `rag.caso.pesquisar`. Com as consultas do Opus, dá as mesmas posições que a medição da manhã nos 39 casos e nos 161 essenciais, sem nenhuma diferença (`rag/resultados/casos-fluxo.json`).

**Outro modelo.** O Sonnet e o Haiku escreveram as consultas dos 39 casos com as mesmas regras e sem a referência (`decomposicao-sonnet/`, `decomposicao-haiku/`). Depois um Sonnet analisou os casos com as regras de `rag/CASO-ANALISE.md`, primeiro com os artigos que as suas consultas encontraram e depois com os 16 artigos que o Opus teve. Os juízes são os mesmos dois Opus, com as mesmas instruções.

| Consultas escritas por | Opus | Sonnet | Haiku |
|---|--:|--:|--:|
| Consultas / artigos prováveis | 224 / 200 | 220 / 173 | 197 / 85 |
| Essenciais em 1.º | 31 | 24 | (a medir) |
| Essenciais nos 8 primeiros | 127 de 161 | 116 de 161 | (a medir) |
| Essenciais nos 16 dados ao LLM | 144 | 131 | — |
| Casos com todos os essenciais nos 8 | 18 | 16 | (a medir) |

| Análise com LLM (os 2 juízes) | Certas | Erradas para algum juiz |
|---|--:|--:|
| Opus parte o caso, Opus analisa (manhã) | 31 de 39 | 1 |
| Opus parte o caso, Sonnet analisa | **30 de 39** | 1 |
| Sonnet parte o caso, Sonnet analisa | **22 de 39** | 6 |

- **A perda vem de partir o caso, não de analisar.** Com os mesmos artigos, o Sonnet analisa quase como o Opus: 30 contra 31 certas, e a mesma errada (`caso-arr-01`, a carta registada em vez da notificação avulsa). Quando é o Sonnet a partir o caso, faltam 13 essenciais no contexto e as certas descem para 22.
- **As 6 erradas do Sonnet de ponta a ponta:**
  - `caso-adm-05`: nenhum dos 4 essenciais no contexto, e falha o limite máximo da prescrição da contraordenação;
  - `caso-cons-02`: deixa a consumidora a responder pela depreciação, quando a falta de informação a isenta;
  - `caso-fam-02`: erra uma conta de datas (2051 em vez de 2033);
  - `caso-arr-01`: a mesma errada do Opus;
  - `caso-trab-03` e `caso-trab-05`: errada para um dos juízes.
- **Concordância dos juízes:** 35 de 39 casos com o mesmo veredicto no Sonnet de ponta a ponta e 36 de 39 com os artigos do Opus.
- **Ressalvas:** os juízes são Opus e a referência foi escrita por Opus. Isto não é o mesmo que um jurista. No contexto do Opus, as análises de um dos lotes do Sonnet passaram as 400 palavras pedidas (439 a 525).
- **O que fica:** partir o caso é o passo que pede o modelo melhor. A análise, com os artigos certos, aguenta um modelo mais barato.

Os ficheiros estão em `resultados/sonnet/` e `resultados/sonnet-contexto-opus/`, e os números em `rag/resultados/casos-llm-sonnet.json`, `casos-llm-sonnet-ctxopus.json` e `casos-fluxo-sonnet.json`.

**O que isto quer dizer.** Com os artigos certos à frente, o raciocínio chega lá em quase todos os casos (com a ressalva acima). Com a pesquisa de hoje, chega em 5 de 39. Partir o caso em consultas jurídicas, com o código e o vocabulário da lei, leva a 31 de 39. As questões do advogado sozinhas não chegam, porque não trazem o código e perdem a narrativa. O que falta, por ordem:
1. Fazer do passo de partir o caso uma peça do sistema e medi-la também com outro modelo. A peça está em `rag/caso.py` (26/11/2026), com as regras em `rag/CASO-PARTIR.md` e `rag/CASO-ANALISE.md`, as mesmas desta medição. O `medir.py --decomposicao` passou a usar essa pesquisa. As consultas escritas pelo Sonnet e pelo Haiku, com as mesmas regras, estão em `decomposicao-sonnet/` e `decomposicao-haiku/`. A medição delas ainda não está feita.
2. Garantir os artigos dos prazos e das formalidades, onde estão as erradas.
3. Pôr um advogado a rever os casos e as análises.

## Ficheiros

- `casos.jsonl`: os 39 casos.
- `REGRAS.md`: como se escrevem e o que não se pode abrir.
- `artigo.py`: ler artigos do acervo e verificar os casos.
- `medir.py`: a medição da pesquisa (e a exportação para o LLM, `--exportar`).
- `exportar_ideal.py`: a exportação do contexto ideal.
- `INSTRUCOES-resposta.md` e `INSTRUCOES-juiz.md`: as regras de quem responde e de quem julga.
- `juizes.py`: preparar os lotes dos juízes e contar.
- `decomposicao/`: as instruções e as consultas escritas para cada caso.
- `resultados/`: as análises e os veredictos de cada juiz, por medição (`ideal`, `pesquisa`, `decomposto`).
