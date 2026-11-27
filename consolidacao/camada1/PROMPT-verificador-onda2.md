# Verificador às cegas, onda 2 (desde a ronda 124)

Pedido comum aos verificadores das rondas da onda 2. Cada agente recebe só a pasta, o número do grupo e a pasta temporária.

1. Lê primeiro `consolidacao/camada1/PROMPT-verificador-115.md` e segue-o à letra, incluindo a secção da ronda 115, que vale para todas as rondas seguintes.
2. As tuas vistas são as do teu grupo em `grupos.txt`, na pasta da ronda: a linha começa pelo número do grupo e um espaço. Para cada `vista-NNN.md`, escreve `resposta-NNN.json` na mesma pasta.
3. Lê as vistas com python, por partes, diploma a diploma. Uma vista pode ter centenas de milhares de caracteres: nunca a leias de uma vez. Não leias outros ficheiros além do prompt, de `grupos.txt` e das tuas vistas.
4. Regras para os veredictos:
   - Uma instrução só é justificada se confirmares o motivo no texto do diploma que altera que está na vista. O que não vês na vista não é justificado.
   - Num artigo que mudou, o texto antigo que fique a seguir à nova redação ou a «(Revogado.)» é `errado`.
   - Uma instrução sobre artigos de outro diploma («os artigos X do Estatuto…, com a redacção dada pelo [este diploma]»), aplicada a este diploma ou ao anexo que o republica, é `errado`.
   - Uma norma cuja entrada em vigor depende de um facto futuro só pode estar aplicada se a vista mostrar que o facto aconteceu.
   - Uma revogação do diploma inteiro, sem exceções, não se aplica artigo a artigo. Se o consolidado tem todos os artigos «(Revogado.)» por essa revogação, isso vai em `fora_dos_artigos` e o diploma não passa.
   - Se a vista tem a secção «ORDEM DOS TÍTULOS E DOS ARTIGOS», confere-a como ela diz.
5. Dá um veredicto a CADA «#### ARTIGO:» da vista, sem saltar nenhum.
6. Ficheiros auxiliares só na tua pasta temporária (cria-a com `mkdir -p`). Nunca escrevas fora dela e das tuas respostas.
7. No fim, confirma com python que cada resposta é JSON válido, que responde a todos os «## DIPLOMA» da vista e que tem um item por cada «#### ARTIGO:». Responde só com uma linha por vista: «NNN: diplomas, artigos certo/errado/dúvida, instruções em falta, justificadas».

## «Nada a aplicar» (pastas `nada-NNN`)

O consolidado é igual ao texto atual, e a secção «O QUE QUEM CONSOLIDOU DIZ QUE NÃO APLICOU» diz porquê.
- Confirma cada motivo no texto do diploma que altera.
- Uma instrução dirigida a este diploma sem motivo confirmado vai para `instrucoes_em_falta`; as confirmadas vão para `instrucoes_justificadas`.
- Responde só com uma linha por vista: «NNN: diplomas, instruções em falta, justificadas».
