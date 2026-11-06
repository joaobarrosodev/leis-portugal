# Verificação às cegas de textos consolidados

Prompt dado a cada subagente verificador (Sonnet) das rondas 6 em diante, com uma vista de `cegas_vista.py`.

Tens um ficheiro `vista-NNN.md` com vários diplomas. Para cada um: o texto do diploma que altera, a lista dos artigos do consolidado IGUAIS ao original, e o ORIGINAL e o CONSOLIDADO dos artigos que DIFEREM (mais os artigos do original que não estão no consolidado).

Regras:
1. Lê o diploma que altera e lista TODAS as instruções dirigidas ao original (substituições, aditamentos, revogações, retificações, renumerações, epígrafes). Instrução que altera OUTRO diploma ("o artigo 5.º do Decreto-Lei X, na redação dada pelo [original]") não é do original: não se aplica.
2. Para cada artigo que difere, dá um veredicto: `certo` (se a instrução o altera, o consolidado é a nova redação letra a letra, com o texto original no lugar de cada "[...]"; se não o altera, igual ao original), `errado` (qualquer diferença de substância; escreve o texto esperado) ou `dúvida` (instrução ambígua ou dependente de outro diploma; explica). Grafia, pontuação e espaços que já estão no diploma que altera não são erro.
3. Artigo revogado: mantém título e epígrafe e o corpo fica "(Revogado.)" (manter a epígrafe NÃO é erro); número revogado "N - (Revogado.)"; alínea "a) (Revogada.)". Revogação condicional ("na parte em que contrariem…") não se aplica ao texto: se o consolidado a aplicou, é `errado`.
4. Por diploma lista à parte: `instrucoes_em_falta` (instruções do passo 1 sem efeito no consolidado; se visavam um artigo da lista dos IGUAIS, também aqui), `artigos_a_mais`, `artigos_em_falta` e `fora_dos_artigos` (texto fora dos artigos que tenha mudado; "sem alterações" se nada mudou).
5. Só usas o ficheiro de vista. Não leias mais nada nesta pasta nem o código.
6. Títulos `###### Artigo N.º — Epígrafe` do consolidado não são erro quando "Títulos normalizados: true".

Saída: um ficheiro JSON (indicado na tarefa) com uma lista, um objeto por diploma, TODOS os diplomas do ficheiro:
`{"id": "<id do DIPLOMA>", "artigos": [{"artigo": "<chave exacta do ARTIGO: ...>", "veredicto": "certo|errado|dúvida", "motivo": "...", "texto_esperado": "..."}], "instrucoes_em_falta": [], "artigos_a_mais": [], "artigos_em_falta": [], "fora_dos_artigos": "sem alterações"}`
Um item em `artigos` para cada "#### ARTIGO:" (diferem e removidos). Motivo curto. Escreve o JSON com a ferramenta Write; confirma que são válidos e que respondes a todos os ids da vista (conta os "## DIPLOMA").

## Diplomas sem artigos (texto corrido)

Quando um diploma vem com "TEXTO DO ORIGINAL (inteiro…)" e "TRECHOS DO CONSOLIDADO QUE DIFEREM", o original não tem artigos: portaria, resolução ou despacho em texto corrido. Os "ARTIGO: Trecho N" são os parágrafos que mudaram (os outros são iguais ao original, que tens inteiro: uma instrução que visava um deles vai em `instrucoes_em_falta`). Um trecho `certo` copia letra a letra a nova redação do diploma que altera, com o texto original onde a instrução diz "[...]". As notas "> Alterado pelo/a …" já foram retiradas. A chave de `artigos` é "Trecho N", tal como aparece.
