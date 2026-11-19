# Respondedor: aplicar declarações de retificação ao texto em vigor

Prompt dado a cada subagente respondedor (Opus) de `consolidacao/retificacoes_llm.py`.

Tens um ficheiro `entrada-NN.jsonl`, com um diploma por linha. Cada diploma traz:

- `retificacoes`: as declarações de retificação que o DRE lhe liga, cada uma com o texto;
- `texto_em_vigor`: o texto consolidado de hoje, em linhas numeradas («L123: …»), sem ligações.

Quando `texto_parcial` é true, vêm só as linhas relevantes e todos os títulos: as linhas que não vês existem, mas não são para mexer.

Para cada retificação, aplica ao texto em vigor as instruções **dirigidas a este diploma**:

1. **O que se aplica:** «onde se lê … deve ler-se …», supressões («suprimindo o n.º 4.º») e palavras ou frases omitidas, quando dizem respeito a texto que está nas linhas.
2. **Outro diploma:** uma declaração pode retificar vários diplomas, e as instruções para outro não se aplicam. Se a retificação corrige um diploma que alterou este («na redação que conferiu…») e o trecho que ele deu está no texto em vigor, aplica-a a esse trecho.
3. **Uma troca por linha alterada:** `linha` é o número N de «LN», e `texto_atual` é o texto dessa linha exatamente como está na entrada, sem o «LN: ». `texto_novo` é a linha inteira depois da retificação.
   - Muda só o que a retificação manda. O resto da linha fica igual, letra a letra, incluindo a pontuação e as maiúsculas.
   - Numa supressão de um parágrafo inteiro, `texto_novo` é "".
   - Uma linha de título («###### Artigo 5.º — Epígrafe», «### Capítulo II — …») continua título do mesmo nível. Pode mudar a epígrafe, o número ou o nome, se a retificação o mandar.
   - Não juntes nem partas linhas.
4. **Não aplicar, com o motivo** (`nao_aplicadas`), quando a instrução:
   - é a um quadro, mapa, tabela ou planta em imagem («(ver documento original)»);
   - é só ao sumário, ao título do diploma, à data ou ao número da publicação;
   - é a um trecho que já não está no texto, porque uma alteração posterior o reescreveu;
   - já está aplicada (o texto já diz o que deve ler-se);
   - é de outro diploma;
   - te deixa em dúvida sobre onde ou como aplicar.

   Na dúvida, não apliques: um texto por retificar é melhor do que um texto errado.
5. Não inventes texto. Uma republicação integral do diploma não se aplica aqui: vai em `nao_aplicadas` com o motivo «republicação».

## Saída

Um ficheiro `resposta-NN.jsonl`, na mesma pasta e com o mesmo NN, com uma linha JSON por diploma da entrada e todos os diplomas:

```json
{"id": "<id do diploma>", "retificacoes": [{"retificacao": "<id da retificação>", "trocas": [{"linha": 123, "texto_atual": "…", "texto_novo": "…"}], "nao_aplicadas": [{"instrucao": "<resumo curto>", "motivo": "imagem|metadados|reescrito depois|já aplicada|outro diploma|republicação|dúvida: …"}]}]}
```

Cada retificação da entrada tem de aparecer, mesmo com `trocas` vazio. Escreve o ficheiro com a ferramenta Write. Confirma que cada linha é JSON válido e que cada `texto_atual` é igual, carácter a carácter, à linha L correspondente.

## Ronda r2

As 7 retificações reprovadas às cegas na 1.ª ronda (6 em dúvida e 1 errada) foram refeitas na sessão principal (Opus), com o reparo do verificador, em `resposta-r2-01.jsonl`. As regras são as de cima, e mais estas duas, que a 1.ª ronda já seguia sem as escrever:

- a troca segue a retificação à letra, sem pontuação que ela não traz;
- uma troca de nome leva consigo as contrações e as concordâncias que dependem dele (ao → à, obrigado → obrigada), e nada mais.

## Ronda im: imagens, anexos omitidos e republicações

As 11 da classe `imagem_ou_republicacao` foram respondidas na sessão principal (Opus), em `resposta-im-01.jsonl`. Uma troca pode ter `com_ligacoes: true`: `texto_atual` e `texto_novo` são então o Markdown cru, para trocar o endereço de uma imagem republicada ou para inserir, a seguir a uma linha, o anexo que a retificação publica. Não se aplica o que um alterador posterior substituiu (um anexo, uma planta, um número reescrito), com o motivo «reescrito depois». Numa republicação integral, só entram os parágrafos que o alterador posterior não reescreveu e cuja redação de hoje (a da republicação do alterador, quando a há) é a da retificação.
