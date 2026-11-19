# Verificador às cegas: retificações aplicadas ao texto em vigor

Prompt dado a cada subagente verificador (Sonnet) de `consolidacao/retificacoes_llm.py`.

Lês um ficheiro `verificacao-entrada-K.jsonl`, com um item por linha. Cada item traz:

- `texto_da_retificacao`: uma declaração de retificação do Diário da República;
- `alteracoes_feitas`: as mudanças feitas ao texto em vigor do `diploma`, com o parágrafo antes e depois. «(parágrafo apagado)» quer dizer que o parágrafo saiu;
- `nao_aplicadas`: o que ficou por aplicar e porquê.

Para cada item, decide se as alterações feitas aplicam corretamente a retificação a este diploma:

1. Cada mudança corresponde a uma instrução da retificação dirigida a ESTE diploma: «onde se lê … deve ler-se …», supressão ou omissão. Uma declaração pode retificar vários diplomas. Uma instrução a um diploma que alterou este vale para o trecho que ele deu.
2. A mudança está no sítio que a retificação indica (artigo, número, alínea), quando isso se vê pelo parágrafo.
3. O parágrafo antes tem o que a retificação diz que se lê. Diferenças só de grafia, espaços, aspas ou pontuação não contam. Se tem outra coisa (outro número, outra alínea, outra redação), a mudança é especulativa: `duvida`.
4. O parágrafo depois tem exatamente o que deve ler-se e nada mais mudou. Ignora as ligações, os espaços e a diferença entre aspas « » e ' '. A pontuação tem de estar certa: nada de pontos duplicados nem de pontuação perdida.
5. Instruções que não aparecem nas alterações não são erro.

Veredicto por item: `certo`, `errado` (diz qual mudança e porquê) ou `duvida` (diz porquê). Na dúvida, `duvida`.

Saída: `verificacao-saida-K.jsonl`, na mesma pasta, com uma linha por item: `{"n": <n>, "veredicto": "certo|errado|duvida", "motivo": "<uma frase>"}`. Usa o `n` do item. Lê o ficheiro por partes se for grande.

## Ronda r2 (`verificacao-entrada-r2.jsonl`)

Na ronda r2 cada mudança traz também `contexto`: o título acima (`titulo_acima`, por exemplo o anexo ou o artigo), os parágrafos antes e depois, e `reescrito_depois`, a nota «> Alterado pelo/a …» quando o parágrafo foi reescrito por um alterador. Usa-o para ver o sítio (regra 2), sobretudo quando o parágrafo é curto («2.º», «2.º ciclo»). Um parágrafo com `reescrito_depois` não é o texto que a retificação corrigiu: uma mudança nele é `errado`, salvo se a própria retificação o visar.

Duas regras de aplicação, as mesmas que o respondedor segue:

- A mudança segue a retificação à letra. A pontuação que a retificação não traz não se acrescenta, e a sua falta não é erro.
- Uma retificação que troca um nome («onde se lê "Clube de …" deve ler-se "Associação de …"») leva consigo as contrações e as concordâncias que dependem dele (ao → à, do → da, o → a, obrigado → obrigada). Não contam como mudanças a mais; outra mudança qualquer conta.

Saída: `verificacao-saida-r2.jsonl` (ou `-r3`, na ronda r3, com as mesmas regras).

## Ronda im (`verificacao-entrada-im.jsonl`): imagens, anexos omitidos e republicações

Aqui as retificações republicam um mapa ou uma planta em imagem, publicam um anexo que tinha ficado por publicar, ou republicam o diploma inteiro. As regras são as de cima, mais estas:

- Numa mudança com `com_ligacoes: true`, o antes e o depois são o Markdown cru, com as ligações. Numa imagem republicada, só muda o endereço da imagem («(ver documento original)»), que tem de ser o da imagem que a retificação publica (está no `texto_da_retificacao`).
- Uma inserção vem como a linha de antes, uma linha em branco e o que se insere. O que se insere tem de ser o que a retificação publica, sem nada a mais nem a menos, salvo um título curto que diga o que é, com as palavras da própria retificação.
- Numa republicação integral, cada mudança tem de pôr o parágrafo como está na republicação, sem outras diferenças. A forma dos títulos não conta (número e epígrafe na mesma linha, ou em duas).
- `nota_do_respondedor` é o que o respondedor diz para justificar a mudança. Não é prova: confirma-a com o texto da retificação.

Saída: `verificacao-saida-im.jsonl`.

## Ronda r4 (`verificacao-entrada-r4.jsonl`): trocas que tinham ficado de fora

São trocas que completam retificações já aplicadas. Cada uma traz `prova_do_respondedor`: um trecho do DR original (por OCR do PDF) ou do alterador posterior, com a fonte. Duas regras a mais:

- Quando o «onde se lê» difere do parágrafo (outra alínea, uma palavra a mais), a mudança é `certo` só se: a prova mostra que o parágrafo é o que o DR publicou; o sítio é único (no número indicado só há um trecho que a instrução pode visar); e o depois tem exatamente o «deve ler-se». Senão, `duvida`.
- Um parágrafo com `reescrito_depois` pode ser o que a retificação corrige se o alterador só o renumerou sem lhe mudar o texto («3 - (Actual n.º 5.)»), e a prova o mostra.

Saída: `verificacao-saida-r4.jsonl`.
