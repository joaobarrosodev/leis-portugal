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
