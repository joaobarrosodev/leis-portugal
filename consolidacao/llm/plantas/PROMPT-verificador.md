# Verificador às cegas: a planta das zonas de caça com o n.º 1.º reescrito

Prompt dado a cada subagente verificador (Sonnet) de `consolidacao/plantas_n1.py`.

Lês um ficheiro `verificacao-entrada-K.jsonl`, com um item por linha. Cada item é uma portaria de concessão de caça (`diploma`) e o último alterador que reescreveu o n.º 1.º dela (`alterador`). Traz:

- `texto_do_alterador`: o texto do alterador, sem as ligações;
- `n1_do_consolidado`: o n.º 1.º que está hoje no consolidado;
- `linha_da_planta_antes` e `linha_da_planta_depois`: a linha da imagem da planta no consolidado, antes e depois da troca, em Markdown cru.

Para cada item, decide se a troca está certa. Confirma quatro coisas:

1. O alterador dá ao n.º 1.º desta portaria uma redação que remete para a «planta anexa à presente portaria», ou seja, a planta do alterador. Confirma também que o alterador é desta portaria: o número e a data que ele cita são os do `diploma`.
2. O `n1_do_consolidado` é essa redação, com diferenças só de grafia, espaços ou ligações.
3. A linha depois difere da de antes só no endereço da imagem.
4. O endereço novo é de um PDF do Diário da República da data do alterador. O caminho `…/1s/AAAA/MM/…` dá o ano e o mês da publicação, que têm de bater com a data do alterador, quando o texto a mostra.

Veredicto por item: `certo`, `errado` (diz porquê) ou `duvida` (diz porquê). Na dúvida, `duvida`.

Saída: `verificacao-saida-K.jsonl`, na mesma pasta, uma linha por item: `{"n": <n>, "id": "<id do item>", "veredicto": "certo|errado|duvida", "motivo": "<uma frase>"}`. Lê o ficheiro com python, um item de cada vez.
