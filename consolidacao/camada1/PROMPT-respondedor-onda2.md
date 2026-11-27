# Respondedor, onda 2 (desde a ronda 125)

Pedido comum aos respondedores. Cada agente recebe só a pasta da ronda, os números dos grupos e a pasta temporária.

Aplicas alterações legislativas portuguesas a textos de diplomas. Os teus pedidos estão em `grupos.txt`, na pasta da ronda: lê com python as linhas dos teus grupos (as que começam por «N|»). Os pedidos estão separados por vírgulas no segundo campo. Faz um pedido de cada vez.

Para cada pedido:
1. Lê o `REGRAS.md` da mesma subpasta, inteiro, com a adenda do fim, incluindo «Ronda 117». Basta uma vez por subpasta.
2. Lê o pedido com python, por partes:
   - primeiro, os reparos do início, se os houver, e os diplomas que alteram;
   - depois, procura no texto atual os artigos ou unidades que as instruções visam.
   Um pedido grande não precisa de ser lido de seguida.
3. Segue as regras à letra:
   - Uma nova redação substitui o artigo inteiro e nunca se acrescenta ao texto antigo.
   - Cada parágrafo novo copia-se letra a letra de uma fonte. O que não tem fonte vai para `nao_aplicavel`.
   - Uma unidade revogada mantém o título com o prefixo do texto atual («Art. 3.º - (Revogado.)» num diploma que escreve «Art. 3.º - …»).
   - Numa renumeração, nunca troques as designações dos títulos de divisão para as acertar com a nova ordem (ver REGRAS).
   - Quando um alterador revoga o diploma inteiro sem exceções, não o apliques artigo a artigo: diz em `nao_aplicavel` «revogado por inteiro». Com exceções, aplica a revogação aos artigos que não ficam ressalvados.
   - Uma instrução sobre artigos de outro diploma («os artigos X do Estatuto…, com a redacção dada pelo [este diploma]») não se aplica a este diploma nem ao anexo que o republica: vai para `nao_aplicavel` como «outro diploma».
   - Uma norma cuja entrada em vigor depende de um facto futuro vai para `nao_aplicavel` como «efeito adiado», salvo se o pedido mostrar que o facto aconteceu.
4. O texto atual pode ser uma versão consolidada pelo DRE. Nesse caso, aplica só as instruções dos diplomas que alteram listados no pedido.
5. Escreve `resposta-NNN.json` na mesma subpasta, com o mesmo NNN do pedido. Copia o texto com python a partir do pedido. Valida com python que o JSON é válido e que responde a todos os ids.

Ficheiros auxiliares só na tua pasta temporária (cria-a com `mkdir -p`). Nunca escrevas fora dela e das tuas respostas, e não leias outros ficheiros do repositório. No fim, responde só com uma linha por pedido: «NNN: N artigos/trocas, nao_aplicavel: sim|não».
