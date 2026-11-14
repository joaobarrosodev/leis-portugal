# Revisão por jurista

Todas as medições do protótipo de perguntas e das consolidações foram feitas por modelos de IA: as perguntas foram geradas a partir dos artigos, verificadas por outra sessão, e as respostas julgadas por quatro juízes que são o mesmo modelo. Esta revisão dá o primeiro número que não depende do Claude, e diz quanto valem os outros.

As instruções para o jurista estão em [`INSTRUCOES.md`](INSTRUCOES.md). Este ficheiro é o protocolo: o que se amostra, porquê, e o que se mede.

## O que se revê

### Respostas: cerca de 160

Tiradas das medições com juízes mais recentes (`MEDICOES` em [`../juristas.py`](../juristas.py)): `teste-reescrito`, `sinteticas-reescrito`, `texto-alterado-2323`, `ue-reescrito` e `ue-reescrito-2`. Quando uma pergunta foi medida em várias, conta a mais recente.

| Bloco | n | Para que serve |
|---|--:|---|
| Principal: respostas dadas, por tipo | 125 | A fiabilidade segundo o jurista, por tipo: reais 40, texto alterado 20, compostas 15, premissa errada 10, literais 10, temporais 10, revogadas 10, UE 10 |
| Recusas de perguntas com resposta | 10 | Os falsos "não sei": a resposta estava na lei e o sistema recusou. Primeiro as recusas em que o sistema leu artigos, para o jurista ver o que foi rejeitado |
| Recusas de perguntas sem resposta | 10 | Se o sistema se cala quando deve: lei inexistente, jurisprudência, aconselhamento, caso concreto |
| Controlos | até 15 | Respostas que os juízes deram como não certas, fora da amostra principal: medem a concordância no sentido em que os juízes dizem "errada" |

Na semente 20261114, os juízes dão como não certas só 17 das 938 respostas dadas e julgadas: 3 caem na amostra principal e as outras 14 são os controlos. Não há mais.

O que conta é **o que o sistema mostrou**. No modo estrito, o travão pode recusar depois de o LLM escrever uma resposta. Os juízes julgaram essa resposta, mas ela não chegou a quem perguntou. Para o jurista, estas perguntas são recusas, e o veredicto dos juízes não entra na concordância.

### Consolidações: 150 artigos

A unidade é o **artigo consolidado**, não o diploma. Os erros acontecem ao nível do artigo, e 150 artigos medem melhor do que 50 diplomas pelo mesmo tempo de leitura. Com 0 erros, o limite superior a 95 % é de cerca de 3/n (regra de três): 2 % em 150, 6 % em 50. Por caminho, o n é menor, e o limite também sobe.

| Bloco | n | O que é |
|---|--:|---|
| `llm` | 45 | Artigos com alterações aplicadas por um LLM |
| `corrido` | 35 | Diplomas sem artigos identificados (texto corrido, `consolidacao/llm_corrido.py`): a unidade é a passagem que mudou, com o parágrafo do artigo onde está como contexto. São mais de metade dos diplomas consolidados |
| `regra` | 30 | Artigos com alterações aplicadas por regras |
| `anexo` | 20 | Artigos e corpos de anexo alterados, incluindo os quadros lidos pelas coordenadas do PDF |
| `visado` | 20 | Artigos que o DRE dá como alterados ou revogados (no histórico, "Altera Artigo 5.º", ou no rótulo de uma relação, "Revogados os arts. 37.º, 61.º e 62.º…") e que o consolidado deixou **iguais** ao original |

No máximo 3 unidades do mesmo diploma. As populações de cada bloco ficam em `chave.jsonl` (`meta.populacao`).

O bloco `visado` existe porque nenhuma amostra de artigos alterados apanha uma **instrução esquecida**: um artigo que devia ter mudado e não mudou. Nem todos são erros. O DRE assinala alterações que não mudam a letra do artigo, e há revogações com ressalvas que a consolidação deixa de fora de propósito (ver `consolidacao/README.md`). Exemplo da preparação desta amostra: o DRE diz que o DL 189/77 revogou os arts. 37.º, 61.º e 62.º do DL 44131, "excepto na parte que é integrada naquele diploma", e o consolidado aplicou só o DL 284/78. Por isso este bloco mede-se à parte e não entra na taxa de erro dos caminhos.

A leitura dos rótulos do DRE é simples: só a primeira lista de artigos do rótulo, e não as que vêm depois de "com excepção de". Um falso candidato custa ao jurista um "certo" rápido.

## Independência

- O jurista não vê os ids, o tipo de pergunta, a resposta de referência nem os vereditos dos juízes. Isso fica na `chave.jsonl`, que não lhe é enviada.
- A ordem é aleatória, para que os blocos não se reconheçam pela posição e o cansaço não caia sempre no mesmo tipo.
- Só na **segunda volta**, e só nas respostas em que jurista e juízes discordam, o jurista vê a resposta de referência e diz se ela estava certa. É assim que se separa o erro do sistema do erro do conjunto de avaliação (as perguntas foram geradas e verificadas por modelos).

## O que se mede (`importar`)

`python avaliacao/juristas.py importar --nome <nome>` escreve `avaliacao/juristas/<nome>.json`, só com contagens.

**Respostas:**
- **Fiabilidade por tipo**, estrita (`certa`) e com reservas (`certa` + `reservas`), com o intervalo de Wilson a 95 %. O total da amostra principal não é proporcional à população, porque é por quotas: cita-se por tipo.
- **Recusas**: indevidas no bloco com resposta e corretas no bloco sem resposta.
- **Concordância juízes–jurista**: a tabela 2×2 (juízes certa/não × jurista certa/não), o kappa de Cohen (estrito e com reservas) e o número que mais importa: **respostas que os juízes deram como certas e o jurista como erradas**.
- **Causas**, para saber onde investir (pesquisa, versão, vigência, consolidação, leitura, interpretação).
- **Respostas sem base nos artigos citados.**
- **Cansaço**: a concordância no primeiro e no último terço da ordem de leitura, e os minutos totais.
- **Segunda volta**: referências erradas ou incompletas, e veredictos que o jurista muda.

**Consolidações**, por caminho e nos artigos alterados em conjunto:
- taxa de erro e de erro grave, com o intervalo de Wilson, e a regra de três quando há 0 erros;
- os erros por tipo (`mal_aplicada`, `esquecida`, `sem_instrucao`, `condicional`, `forma`);
- à parte, no bloco `visado`, quantos são instruções esquecidas de facto.

## O que se faz com o resultado

- **Se o jurista confirma os juízes** (kappa alto, quase nenhuma "certa pelos juízes, errada pelo jurista"), os números do `rag/README.md` passam a poder dizer "confirmados por um jurista numa amostra de N". Até lá, continuam com a ressalva "juízes do mesmo modelo, sem jurista".
- **Se não confirma**, os números dos juízes deixam de se citar e passam a valer os do jurista. A causa mais frequente diz qual é a próxima frente.
- **Consolidações**: a taxa de erro grave por caminho decide se um caminho continua a entrar em `data/` e qual o aviso que o RAG mostra.
- **As perguntas diretas** (secção 3 das instruções) vão para `src/leis_portugal/domain/entry_into_force.py` e para as regras de vigência, com a fonte da resposta.

## Passo a passo

```bash
python avaliacao/juristas.py respostas --nome respostas-1 [--privado-de <checkout principal>]
python avaliacao/juristas.py consolidacoes --nome consolidacoes-1   # cerca de 5 min (lê todo o data/)
```

Enviar ao jurista: `avaliacao/privado/juristas/<nome>/pacote.html` e `folha.csv`, com `avaliacao/juristas/INSTRUCOES.md`. Nunca a `chave.jsonl`.

Com a folha preenchida em `avaliacao/privado/juristas/<nome>/folha.csv`:

```bash
python avaliacao/juristas.py importar --nome respostas-1
```

O `importar` diz o que falta ou está mal na folha (valores fora da lista, causa em falta). Quando a folha está completa e há discordâncias, escreve `segunda-volta.html` e `segunda-volta.csv` para enviar ao jurista. Com a segunda volta preenchida, correr o `importar` outra vez.

Os pacotes, as folhas e as chaves ficam em `avaliacao/privado/` (fora do git): têm as perguntas reais, cujos termos de reutilização não são claros (ver [`../README.md`](../README.md)). Só o resumo com as contagens vai para o git.

## Tempo previsto

Sem medição ainda: a coluna `minutos` serve para isso. Como ordem de grandeza, contando 4 a 6 minutos por resposta e 3 a 5 por artigo consolidado, são 11 a 16 horas para as respostas e 8 a 12 para as consolidações, em sessões de 1 a 2 horas. Se for demais, cortam-se as quotas (`QUOTAS` e `QUOTAS_CONSOLIDACAO` em `juristas.py`) antes de se tirar a amostra, nunca depois.
