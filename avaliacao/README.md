# Conjunto de avaliação

Perguntas com a resposta certa conhecida, para medir a fiabilidade de um sistema de pesquisa e resposta (RAG) sobre o acervo. É a fase 1 do [plano para um RAG jurídico fiável](../PLANO-RAG.md).

A meta é que pelo menos 95% das respostas **dadas** estejam certas: artigo certo, versão em vigor na data certa e citação que suporta a resposta. O sistema pode responder "não sei".

## Âmbito

Só perguntas cuja resposta está **escrita** num artigo: prazos, valores, quem pode o quê, se uma norma está em vigor, o que dizia numa data. Interpretação, casos concretos e jurisprudência ficam de fora; para essas o certo é "não sei".

## Estado

| Fase | Perguntas | Margem de erro a 95% | Para que serve |
|---|---:|---:|---|
| **Piloto** (concluído) | 59 | cerca de ±5,5 pontos | Testar o processo: se as perguntas saem boas, se a verificação às cegas funciona e se a comparação apanha os erros |
| **Conjunto completo** (concluído) | 593 | cerca de ±1,8 pontos | Medir a fiabilidade a sério, por tipo de pergunta |

60 perguntas não chegam para medir: um resultado de 95% tanto pode ser 90% como 100%. Com ~600 já se distingue 93% de 97%.

| Tipo | Piloto | Novas | Total | Onde |
|---|---:|---:|---:|---|
| Literais | 30 | 220 | 250 | `perguntas.jsonl` |
| Temporais | 12 | 90 | 102 | `perguntas.jsonl` |
| Revogadas | 7 | 48 | 55 | `perguntas.jsonl` |
| Sem resposta | 10 | 40 | 50 | `perguntas.jsonl` |
| Reais (FAQs oficiais) | — | 136 | 136 | `privado/perguntas-reais.jsonl` (fora do git) |
| **Total** | **59** | **534** | **593** | |

Os IDs têm falhas onde uma pergunta saiu do conjunto (`rev-004`, `lit-231`, `tmp-067`, `tmp-084`).

As novas foram tiradas com outras sementes de `amostra.py` (20261028 a 20261031), sem repetir diplomas do piloto. Ficaram de fora os diplomas que já caducaram na prática (os que "vigoram até" uma data passada), os anexos de republicação, os artigos só de alteração de outro diploma e os de entrada em vigor.

## FAQs oficiais: termos de reutilização

Verificado em 27/10/2026:

| Fonte | Termos encontrados | Usada |
|---|---|---|
| ePortugal (gov.pt) | Os [termos do gov.pt](https://www.gov.pt/termos-e-condicoes) permitem copiar e usar os conteúdos gratuitamente, citando o gov.pt como fonte, desde que o uso não tenha fins lucrativos | Não: as páginas de serviço não têm FAQs que citem artigos |
| Portal das Finanças (AT) | Não há termos de utilização nem aviso legal publicados (as ligações dão 404 e o rodapé não tem nenhuma) | Sim: 37 perguntas |
| Segurança Social | O portal passou para a Segurança Social Direta; as páginas de termos e de perguntas frequentes reencaminham para a área de autenticação | Não |
| ACT | O [portal](https://portal.act.gov.pt/Pages/PerguntasFrequentes.aspx) não tem termos de reutilização visíveis | Sim: 99 perguntas |

Como não é claro que se possam publicar, as perguntas reais ficam em `privado/` (no `.gitignore`) e servem só para avaliar. As perguntas foram reescritas por palavras nossas e a resposta vem do artigo que a FAQ cita, não do texto da FAQ; o URL da FAQ fica em `notas`. As FAQs da ACT citam os artigos por tema ("artigos 237.º a 247.º"); a `fonte` é o artigo desse conjunto que responde à pergunta.

Das FAQs do Portal das Finanças, só serviram as que citam códigos que se encontraram em versão atual no acervo. As de IRS e IRC ficaram de fora porque os registos dos Decretos-Leis n.os 442-A/88 e 442-B/88 só têm o texto de 1988. Corrigido em 27/10/2026: o texto atual destes códigos está no acervo, mas no consolidado do diploma que os republicou (o Código do IRS na Lei n.º 82-E/2014, o do IRC na Lei n.º 2/2014), e o `leis-portugal link` passou a ligar os originais a esses registos (`republished_by`). As FAQs de IRS e IRC podem entrar numa próxima versão do conjunto.

## Resultado do conjunto completo (27/10/2026)

As 537 perguntas novas passaram pelo mesmo processo do piloto: verificação literal, verificação às cegas pela sessão B (Sonnet, sem acesso às respostas) e comparação automática. No fim, todas as 593 passam `literal` e `compara`, sem pontos a rever.

| Tipo | Novas na 1.ª ronda | Confirmadas na 1.ª ronda | Assinaladas | Reformuladas | Retiradas | Final |
|---|---:|---:|---:|---:|---:|---:|
| Literais | 221 | 204 (92%) | 17 | 3 | 1 | 220 de 220 |
| Temporais | 92 | 87 (95%) | 5 | 1 | 2 | 90 de 90 |
| Revogadas | 48 | 46 (96%) | 2 | 0 | 0 | 48 de 48 |
| Sem resposta | 40 | 40 (100%) | 0 | 0 | 0 | 40 de 40 |
| Reais | 136 | 113 (83%) | 23 | 7 | 0 | 136 de 136 |
| **Total** | **537** | **490 (91%)** | **47** | **11** | **3** | **534 de 534** |

Com o piloto, o conjunto final tem 593 perguntas confirmadas: 457 em `perguntas.jsonl` e 136 em `privado/perguntas-reais.jsonl`.

| Ronda | Perguntas | Confirmadas | O que se fez |
|---|---:|---:|---|
| 1.ª | 537 | 490 | Revisão dos 47 pontos (abaixo) |
| 2.ª (reformuladas) | 9 | 7 | B ainda achou ambíguas `real-017` e `real-030`; reformuladas de novo |
| 3.ª (reformuladas) | 2 | 2 | — |

O que os 47 pontos eram:

- **Respostas iguais por outras palavras:** 21 (por exemplo, A "Não pode exceder três meses", B "Não excederá três meses"). A comparação por palavras não as apanha. Reescreveu-se a resposta de A com as palavras do artigo, sem mudar o sentido, e passaram a confirmar-se automaticamente.
- **Perguntas que remetem para outro artigo:** 11 (3 públicas e 8 reais), marcadas com `depende_de_outro`. São sobretudo as reais: as FAQs citam um artigo que remete para definições noutro (quem são os sujeitos passivos do artigo 2.º do CIVA, o artigo 366.º do Código do Trabalho, a verba 1.2 da Tabela Geral do Imposto do Selo).
- **Perguntas ambíguas ou mal formuladas:** 11, reformuladas e verificadas de novo às cegas (`lit-177`, `lit-205`, `lit-244`, `tmp-085`, `real-010`, `real-014`, `real-017`, `real-018`, `real-023`, `real-030`, `real-077`). Exemplo: "Que tarifa fixa a Portaria n.º 41/2020?" admitia o objeto ou o valor.
- **Perguntas retiradas:** 3. `lit-231` perguntava como são tributadas as rendas e o artigo só remete para um diploma futuro; `tmp-067` e `tmp-084` tinham dois regimes no mesmo artigo e a pergunta não dizia qual.
- **Respostas de A erradas:** nenhuma. Houve duas incompletas ou a mais: `real-010` listava só os familiares isentos de imposto do selo quando o artigo isenta também o Estado e outras entidades (a pergunta passou a ser só sobre os filhos), e `lit-116` acrescentava um prazo que a pergunta não pedia.
- **Sem resposta:** B recusou as 40, como no piloto.

As perguntas reais foram as mais difíceis (83% confirmadas à primeira, contra 92% a 100% nas outras), como se esperava: usam palavras do dia a dia ("ato isolado", "faturas pró-forma", "horas extraordinárias") e não as do artigo. É a medição mais próxima do uso real e deve ser mostrada à parte.

## Resultado do piloto (27/10/2026)

A sessão B (Sonnet, às cegas) chegou às mesmas respostas que a sessão A em todas as perguntas: 59 de 59 confirmadas pela comparação automática.

| Ronda | Perguntas | Confirmadas | Assinaladas por B | O que se fez |
|---|---:|---:|---:|---|
| 1.ª | 60 | 53 | 7 | Revisão abaixo |
| 2.ª (só as reformuladas) | 2 | 2 | 0 | — |
| **Final** | **59** | **59** | **0** | |

- **Respostas erradas de A:** nenhuma. B recusou as 10 sem resposta e indicou a revogação nas revogadas.
- **Perguntas mal formuladas:** 3. `lit-013` falava em "área" quando o artigo fala em número de corpos, e `rev-002` era ambígua; ambas foram reformuladas e voltaram a passar às cegas. `rev-004` era vaga e saiu do conjunto.
- **Perguntas que remetem para outro artigo:** `lit-016` e `lit-020`, marcadas com `depende_de_outro`.
- **Comparação:** a primeira versão marcava 34 pontos a rever, quase todos ruído (números escritos de outra forma, respostas iguais por outras palavras). Com as melhorias passou a 7, todos reais.
- **Amostragem:** os anexos de republicação davam texto histórico em vez do atual; passaram a ser excluídos antes de se escreverem as perguntas.

O processo funciona; foi o que se usou no conjunto completo (acima).

## Tipos de pergunta

| Tipo | Prefixo | Como se gera | Como se sabe a resposta certa |
|---|---|---|---|
| `literal` | `lit-` | Artigo de um diploma em vigor e consolidado | O excerto tem de estar no texto atual do artigo |
| `temporal` | `tmp-` | Artigo cuja redação mudou (`.versoes.json`) | O excerto tem de estar no texto do artigo na `data_referencia` (`version-at`) |
| `revogada` | `rev-` | Artigo de um diploma revogado (relação `repealed_by`) | A resposta certa diz que a norma foi revogada, e por que diploma |
| `sem_resposta` | `sem-` | Fora do âmbito, lei inexistente ou diploma que não trata do assunto | O certo é "não sei"; a verificação recebe um artigo distrator |
| `real` | `real-` | FAQs oficiais que citam artigos (Portal das Finanças e ACT), reescritas | O excerto tem de estar no texto atual do artigo que a entidade cita |

## Processo

1. **Amostragem** (`amostra.py`): escolhe artigos ao acaso no índice exportado (`leis-portugal export`), com semente fixa. Exclui artigos revogados, só de aprovação, com blocos de assinaturas e de **anexos de republicação**: o texto republicado é o dessa data, não o atual, e daria respostas certas erradas.
2. **Sessão A (geração):** lê os candidatos e escreve a pergunta, a resposta e o excerto do artigo que a suporta, em `perguntas.jsonl`.
3. **Verificação literal** (`verifica.py literal`): confirma que cada excerto está, letra a letra, no artigo citado (na data de referência, nas temporais) e que os números da resposta estão no excerto.
4. **Sessão B (verificação às cegas, outro modelo):** recebe `verifica.py cegas`, que tem só a pergunta, a data e o texto do artigo, **sem a resposta certa**. Responde a partir do texto e assinala perguntas ambíguas ou que dependem de outro artigo. Não pode abrir `perguntas.jsonl`.
5. **Comparação** (`verifica.py compara`): compara as respostas de B com as de A e lista o que não bate. Os números comparam-se sem separadores de milhares nem decimais a zero (`100 000 000,00` = `100 000 000`). As respostas sem números contam como iguais quando a de B tem pelo menos 80% das palavras com conteúdo da de A, ignorando as diferenças do Acordo Ortográfico.
6. **Discordâncias:** vão a uma terceira revisão, são corrigidas ou a pergunta sai do conjunto.
7. **Calibração (opcional):** revisão humana de ~20 perguntas ao acaso, para medir quanto confiar na verificação automática. Sem ela, o resultado escreve-se "95% segundo a verificação automática".

## Ficheiros

| Ficheiro | O que é |
|---|---|
| `perguntas.jsonl` | O conjunto de avaliação, com as respostas certas (sessão A) |
| `privado/perguntas-reais.jsonl` | As perguntas reais (FAQs oficiais), fora do git |
| `verificacao/entrada-piloto.jsonl` | A entrada da sessão B, sem as respostas |
| `verificacao/respostas-b-piloto.jsonl` | As respostas da sessão B |
| `verificacao/entrada-piloto-revistas.jsonl`, `respostas-b-piloto-revistas.jsonl` | Segunda ronda às cegas das perguntas reformuladas depois da revisão |
| `verificacao/entrada-completo.jsonl`, `respostas-b-completo.jsonl` | Entrada e respostas da sessão B para as perguntas novas de `perguntas.jsonl` (1.ª ronda) |
| `verificacao/entrada-completo-revistas.jsonl`, `respostas-b-completo-revistas.jsonl` | 2.ª ronda, só as reformuladas |
| `verificacao/respostas-b-final.jsonl` | Todas as respostas de B em vigor (piloto e completo, com as rondas seguintes por cima), uma por pergunta de `perguntas.jsonl` |
| `privado/entrada-reais*.jsonl`, `privado/respostas-b-reais*.jsonl` | O mesmo para as perguntas reais; `respostas-b-reais-final.jsonl` junta as três rondas |
| `amostra.py` | Amostragem dos candidatos |
| `verifica.py` | Verificação literal, entrada às cegas e comparação |
| `comum.py` | Leitura dos artigos de um registo (partilhada) |

## Formato

Uma pergunta por linha em `perguntas.jsonl`:

```json
{
  "id": "lit-001",
  "tipo": "literal",
  "pergunta": "…",
  "data_referencia": "2026-10-27",
  "fonte": {"documento": "pt:dre:…:por", "caminho": "data/…/….md", "titulo": "…", "artigo": "17.º", "epigrafe": "…"},
  "resposta": "…",
  "excerto": "texto literal do artigo que suporta a resposta"
}
```

- `fonte.artigo` é a chave do artigo no registo: `17.º` no diploma, `Anexo — …::17.º` num anexo. A numeração repete-se entre o diploma e os anexos (o Código do Trabalho, anexo da Lei n.º 7/2009, tem o seu próprio artigo 3.º).
- `depende_de_outro: true` (opcional) marca as perguntas cuja resposta completa precisa de outro artigo para o qual o texto remete. Servem para avaliar a pesquisa em vários artigos; a comparação não as volta a assinalar por isso.
- `revogada` tem ainda `revogado_por` (`documento`, `titulo`, `data`).
- `sem_resposta` tem `fonte: null` e `distrator` (mesmo formato de `fonte`).

Uma resposta por linha da sessão B: `{"id", "responde": bool, "resposta", "excerto", "ambigua": bool, "depende_de_outro": bool, "notas"}`.

## Comandos

```bash
python avaliacao/amostra.py --saida <pasta>
cd avaliacao && python verifica.py literal
cd avaliacao && python verifica.py cegas --saida verificacao/entrada-piloto.jsonl
cd avaliacao && python verifica.py compara --respostas verificacao/respostas-b-piloto.jsonl
cd avaliacao && python verifica.py compara --respostas verificacao/respostas-b-final.jsonl
cd avaliacao && python verifica.py literal --perguntas privado/perguntas-reais.jsonl
cd avaliacao && python verifica.py compara --perguntas privado/perguntas-reais.jsonl --respostas privado/respostas-b-reais-final.jsonl
```

As perguntas reais usam sempre `--perguntas privado/perguntas-reais.jsonl`.

Precisam do ambiente do projeto (`pip install -e .`) e de `exports/leis-portugal.sqlite`.

## Limites

- Perguntas geradas a partir de um artigo são mais fáceis do que as reais, porque usam as mesmas palavras. Cada tipo é medido e mostrado em separado.
- A amostra usa o estado de vigência que o DRE indica. Alguns diplomas "em vigor" já caducaram na prática (por exemplo, os que vigoravam só até uma data); na geração estes ficam de fora.
- As perguntas reais não se publicam (ver acima). Vêm de duas entidades e sobretudo do Código do Trabalho e dos códigos fiscais; ainda não cobrem IRS nem IRC (ver acima).
- Em alguns registos a numeração dos artigos repete-se sem cabeçalho `## Anexo` (por exemplo, a Portaria n.º 1532/2008 e o Decreto-Lei n.º 63/2020). Aí a chave `4.º` é ambígua e `comum.artigo` devolve o primeiro artigo com esse número; as duas perguntas afetadas saíram do conjunto.

## Conjunto difícil (frente C do plano, 28/10/2026)

424 perguntas novas, em cinco tipos que o conjunto anterior não tinha ou tinha pouco. **Medem-se à parte**: não entram nas contas do conjunto de 593, porque são mais difíceis e de natureza diferente. Ficaram abaixo do alvo de cerca de 550 (ver "O que falta").

| Tipo | Prefixo | Geradas | Confirmadas às cegas na 1.ª ronda | Revistas à mão | Retiradas | Finais | Onde |
|---|---|---:|---:|---:|---:|---:|---|
| Texto alterado | `alt-` | 100 | 62 | 38 | 1 | 99 | `perguntas.jsonl` |
| Compostas (2 a 3 artigos) | `cmp-` | 106 | 61 | 45 | 6 | 100 | `perguntas.jsonl` |
| Premissa errada | `pre-` | 50 | 34 | 16 | 0 | 50 | `perguntas.jsonl` |
| Sem resposta (novas) | `sem-` | 30 | 20 | 10 | 0 | 30 | `perguntas.jsonl` |
| Reais (novas áreas) | `real-` | 150 | 94 | 56 | 5 | 145 | `privado/perguntas-reais.jsonl` (fora do git) |
| **Total** | | **447** | **295** | **151** | **22** | **424** | |

- **Texto alterado:** diplomas em vigor alterados por outros e sem consolidação (`version_kind = original`, relação `amended_by`). A pergunta é sobre um artigo e a resposta certa depende de o artigo ter sido alterado: 49 `alterado: true` (a resposta é a redação nova, escrita no diploma alterador) e 50 `alterado: false` (o artigo não mudou, apesar de o diploma ter alterações). Verificou-se no diploma alterador, letra a letra, que o excerto está lá (`alterador.artigo`).
- **Compostas:** a resposta precisa de 2 ou 3 artigos do mesmo diploma, quase sempre com uma remissão de um para o outro; `fonte.artigos` e `excerto` são listas.
- **Premissa errada:** a pergunta afirma algo falso (prazo, valor, conteúdo de um artigo); o certo é corrigir. Tem `premissa`; `resposta` começa por "A premissa está errada".
- **Sem resposta:** valores delegados a portarias ausentes do acervo, interpretação, matérias do direito da União, regimes mistos. Mesmo formato que `sem_resposta` antigas (a verificação recebe um artigo distrator).
- **Reais:** FAQs oficiais da ANSR (Código da Estrada, 25), Portal da Habitação (NRAU e arrendamento, 30; Porta 65 Jovem, 15), ERS (saúde, 34; taxas moderadoras, IVG, transporte de doentes e mediação, 23), Autoridade Tributária (IVA, IRS, IRC, 11) e guias práticos do Instituto da Segurança Social (pensão de velhice, 11). Texto da FAQ fora do git; o URL fica em `notas`.

### O que a verificação às cegas apanhou

- **Entrada incompleta para a sessão B:** nas alteradas em que o alterador é uma portaria que altera muitos regulamentos (as do PRODER), `verifica.py cegas` mostrava a B os artigos errados do alterador; B dizia "não foi alterado" quando A dizia que sim (12 perguntas). Corrigiu-se a escolha das passagens (primeiro as que citam o diploma original) e repetiu-se a verificação dessas 12: B passou a concordar com A.
- **Respostas de A mais longas do que a de B:** 63 perguntas. Quando as palavras de B estavam contidas na resposta de A, a resposta de A foi encurtada para a de B (ficheiros finais). `resposta_original_a` não se guarda.
- **Revisão à mão:** nas 94 perguntas (68 públicas, 26 reais) em que a comparação por palavras ainda assinalava diferenças, leu-se a resposta de A e a de B; dizem o mesmo, com mais ou menos pormenor. Ficam com `revisto` e `compara` deixa de as assinalar por palavras ou números (as discordâncias de sentido, de `alterado` e de `premissa_errada` continuam a ser assinaladas).
- **Retiradas (8 na revisão, mais 3 depois):** `alt-069` (a pergunta não diz a categoria de veículo de que depende o limite), `cmp-022`, `cmp-026`, `cmp-031` (A e B respondem a coisas diferentes ou a pergunta junta dois assuntos), `real-211` e `real-248` (B não encontrou a resposta no artigo), `real-230` e `real-296` (o artigo tem condições que a pergunta não refere).
- **Remetem para outro artigo:** `depende_de_outro` nas perguntas que B marcou assim (sobretudo reais).
- **Sem resposta:** B recusou as 30.

Respostas de B: `verificacao/respostas-b-dificil-*.jsonl` (alteradas na 1.ª e 2.ª rondas, compostas, premissa errada, sem resposta) e `privado/respostas-b-reais-dificil.jsonl`. Entradas: `verificacao/entrada-dificil-*.jsonl` (a das alteradas repetida em `entrada-dificil-alt-v2.jsonl`) e `privado/entrada-reais-dificil.jsonl`. Instruções dadas à sessão B: `verificacao/instrucoes-sessao-b-dificil.md`. Perguntas antes de revistas: `verificacao/por-verificar-dificil-*.jsonl`, `privado/por-verificar-reais-dificil.jsonl`. As respostas de B em vigor de todas as perguntas estão em `respostas-b-final.jsonl` e `privado/respostas-b-reais-final.jsonl`.

### Formato dos tipos novos

- `texto_alterado`: `alterado` (bool), `alteradores` (lista de `{documento, titulo, caminho, data}`) e, quando `alterado`, `alterador` (`documento`, `titulo`, `caminho`, `artigo`, `data`): o artigo do alterador onde está a redação nova.
- `composta`: `fonte` = `{documento, caminho, titulo, artigos: [{artigo, epigrafe}, …]}` e `excerto` = lista, um por artigo, pela mesma ordem.
- `premissa_errada`: `premissa` (o que a pergunta afirma).
- `sem_resposta`: como antes.
- `revisto` (opcional): revisão manual das diferenças de palavras entre A e B.
- Resposta de B: além de `responde`, `ambigua` e `depende_de_outro`, `premissa_errada` e `alterado`.

### O que falta

- **Perguntas reais:** 107 em vez de cerca de 300. Estavam fechados ao acesso automático o AIMA, IMT, IAPMEI, ePortugal, DGC, CITE e CNPD; as páginas da Justiça (IRN) e a maior parte das FAQs de empresas não citam artigos; o guia de subsídio de desemprego do ISS é um PDF sem texto extraível sem ferramentas que não estavam disponíveis. Os temas de Estrangeiros e Consumidor ficaram só nas compostas.
- **Quantidade:** 279 públicas novas e 145 reais, 424 de uma meta de cerca de 550. Falta cerca de 170 reais. As compostas e alteradas atingiram a meta (100 cada, menos as retiradas).
- **Termos de reutilização:** não se encontraram nos sítios da ANSR e do ISS; o da ERS só tem política de privacidade. O Portal da Habitação (IHRU) não foi verificado. Por isso as reais continuam fora do git, só com o URL.
- **Calibração humana** (revisão de cerca de 20 perguntas ao acaso) por fazer.

### Fontes revogadas (28/10/2026)

O acervo marca os artigos revogados com uma nota "Revogado pelo/a …" no fim do artigo, e o texto do artigo pode continuar lá. Uma pergunta literal sobre um artigo assim tem como resposta certa um texto que já não vale.

- **Substituídas 20 literais** (`lit-008`, `011`, `022`, `037`, `052`, `089`, `096`, `098`, `114`, `120`, `125`, `152`, `153`, `154`, `160`, `161`, `194`, `196`, `204`, `232`) por 20 perguntas novas sobre artigos em vigor (`lit-252` a `lit-271`): 12 no mesmo diploma, 8 noutros diplomas tirados com a semente 20261202 de `amostra.py`, quando o diploma não tinha outro artigo utilizável (alguns estavam quase todos revogados, como o Decreto Regulamentar Regional n.º 28/2006/A). Verificação literal e às cegas como as outras: B confirmou 19 à primeira; na `lit-263` a resposta de A tinha mais pormenor do que a de B e ficou com a de B. Ficheiros: `verificacao/entrada-substituicao-literais.jsonl` e `verificacao/respostas-b-substituicao-literais.jsonl`; as notas de cada pergunta dizem qual substituem.
- **Conjunto difícil:** verificou-se a fonte de todas as perguntas, públicas e reais. Três compostas tinham como fonte artigos revogados do Código do Registo Civil e do NRAU (`cmp-023`, `cmp-029`, `cmp-071`) e foram retiradas; as reais passaram sem alterações. As perguntas temporais e revogadas apontam para artigos revogados por desenho e ficam como estão.
- **Depois desta substituição ficaram 730 perguntas em `perguntas.jsonl`** e 243 reais (hoje 736 e 281, ver a secção seguinte); a procura de fontes revogadas (nota "Revogado pelo/a" ou texto do artigo só "(Revogado)") dá zero nas literais, compostas, premissa errada, sem resposta e reais.

### Segunda volta das reais e compostas (28/10/2026)

Mais 44 perguntas: 38 reais e 6 compostas.

- **Reais:** 23 das FAQs da ERS sobre taxas moderadoras (Decreto-Lei n.º 113/2011), interrupção voluntária da gravidez (Portaria n.º 741-A/2007), transporte não urgente de doentes (Portaria n.º 142-B/2012) e mediação (Lei n.º 29/2013), e 15 do Porta 65 Jovem do Portal da Habitação (Decreto-Lei n.º 308/2007 e Portaria n.º 277-A/2010), `real-312` a `real-349` (menos `real-338`). Retirada 1 (`real-338`: a pergunta pedia classificar um primo como parente colateral, o que o texto não diz). Cada pergunta da ERS tem em `notas` o tema da FAQ; o texto da FAQ não vem para o git.
- **Compostas:** `cmp-103` a `cmp-108`, com os mesmos diplomas. B confirmou todas; uma resposta de A foi encurtada para a de B.
- **Verificação:** B confirmou 28 das 38 reais à primeira (os outros 10 diferiam só em pormenor; 6 revistos à mão e marcados `revisto`, 4 alinhados com a resposta de B, que era um subconjunto). Literal e comparação limpos: 736 públicas e 281 reais.
- **Termos de reutilização do Portal da Habitação (IHRU):** os [avisos legais](https://www.portaldahabitacao.pt/web/guest/avisos-legais) permitem copiar, importar ou utilizar gratuitamente a informação, para uso pessoal ou público, desde que sem fins lucrativos ou ofensivos e com referência à fonte. Verificado em 28/10/2026. Mesmo assim as perguntas ficam em `privado/` e só com o URL, como as outras reais.
- **Ficheiros:** `verificacao/entrada-dificil-cmp2.jsonl`, `respostas-b-dificil-cmp2.jsonl`, `privado/entrada-reais-dificil2.jsonl`, `privado/respostas-b-reais-dificil2.jsonl`.
