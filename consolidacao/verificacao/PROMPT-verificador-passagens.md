# Verificação às cegas por passagem (ronda 70)

Prompt dado a cada subagente verificador (Sonnet) com uma vista de `llm_gigantes.py vistas`. As regras são as de `PROMPT-verificador.md` (e de "Verificação às cegas" no `README.md`), com estas diferenças.

Tens um ficheiro `vista-<id>-pK.md` com UMA passagem de UM diploma grande: os diplomas que alteram DESTA passagem, o texto ANTES dela (inteiro na vista ou num ficheiro `antes-<id>-pK.md`, indicado na vista) e os TRECHOS que mudaram entre o texto antes e o texto depois (parágrafos comparados por programa; nada vem de quem aplicou as alterações).

1. Lê os diplomas que alteram e lista TODAS as instruções deles dirigidas ao original (substituições, aditamentos, revogações, retificações, renumerações, epígrafes, republicações). Instrução que altera OUTRO diploma não é do original.
2. Para cada "#### ARTIGO: Trecho N" dá um veredicto: `certo` (o DEPOIS é a nova redação letra a letra, com o texto de ANTES onde a instrução diz "[...]"/"..."; um trecho apagado é certo se a instrução o elimina), `errado` (diferença de substância; escreve o texto esperado) ou `dúvida` (instrução ambígua ou dependente de outro diploma; explica). Grafia e pontuação que já estão no diploma que altera não são erro. Revogado: "N - (Revogado.)", "a) (Revogada.)", ou a epígrafe com "(Revogado.)". Revogação condicional ("na parte em que contrariem…") ou adiada para um facto futuro não se aplica: se foi aplicada, é `errado`.
3. Uma republicação "com a redação atual" do original (ou de um anexo dele) é o texto em vigor nessa data: um trecho que passa a ser a republicação é `certo` se for igual a ela.
4. `instrucoes_em_falta`: instruções do passo 1 sem efeito no texto depois (procura no texto ANTES a unidade que visavam: se ficou igual e a instrução a muda, falta). Só as destes alteradores. `artigos_a_mais`/`artigos_em_falta`: artigos, números ou alíneas a mais ou a menos. `fora_dos_artigos`: "sem alterações" se nada mais mudou indevidamente; senão, o que mudou.
5. Só usas a vista e o ficheiro `antes-…` que ela nomeia. Não leias mais nada (código, `data/`, registos de alterações, respostas, internet).

Saída: um ficheiro JSON (indicado na tarefa) com UM objeto:
`{"id": "<id do DIPLOMA>", "passagem": K, "artigos": [{"artigo": "Trecho N", "veredicto": "certo|errado|dúvida", "motivo": "...", "texto_esperado": "..."}], "instrucoes_em_falta": [], "artigos_a_mais": [], "artigos_em_falta": [], "fora_dos_artigos": "sem alterações"}`
Um item em `artigos` para cada "#### ARTIGO:" da vista, com a chave exata ("Trecho N"). Motivo curto. Confirma no fim que o JSON é válido e que deste veredicto a todos os trechos.
