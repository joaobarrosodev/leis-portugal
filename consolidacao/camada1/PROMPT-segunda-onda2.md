# Segunda leitura, onda 2 (desde a ronda 124)

Pedido comum aos leitores. Cada agente recebe só a pasta da ronda, o número do ficheiro (NN) e a pasta temporária.

1. Lê primeiro `consolidacao/camada1/PROMPT-segunda-leitura.md` e segue-o à letra.
2. O teu ficheiro é `segunda-NN.md` na pasta da ronda. Cada diploma traz a vista da verificação às cegas e, no fim, o que o verificador deu por justificado. Escreve a saída em `segunda-NN.json`, na mesma pasta. Lê o ficheiro com python, por partes: pode ter centenas de milhares de caracteres.
3. Regras de quem consolida, para teres em conta:
   - O texto de uma nova redação copia-se letra a letra do diploma que altera. O que a instrução não muda fica letra a letra como no texto atual.
   - O título de uma unidade revogada fica com o prefixo do texto atual («Art. 3.º - (Revogado.)»).
   - Uma instrução sobre artigos de outro diploma («os artigos X do Estatuto…, com a redacção dada pelo [este diploma]») não se aplica a este diploma nem ao anexo que o republica.
   - Uma norma cuja entrada em vigor depende de um facto futuro só se aplica se houver prova, no acervo, de que o facto aconteceu.
   - Uma revogação do diploma inteiro, sem exceções, não se consolida: se o consolidado tem todos os artigos «(Revogado.)» por essa revogação, dá `reparos`. Com exceções, a revogação aplica-se artigo a artigo.
   - Numa renumeração, cada título de divisão tem de ficar antes dos artigos que lhe pertencem na nova ordem. Se a vista tem «ORDEM DOS TÍTULOS E DOS ARTIGOS», confere-a.
4. Para procurar no acervo usa `grep -rl` em `data/`, a partir da raiz do worktree. Lê só os ficheiros de que precisas.
5. Se precisares de uma pasta temporária, cria-a com `mktemp -d` dentro de `$TMPDIR`. Não escrevas em mais nenhum sítio além dela e do teu ficheiro de saída, e não alteres nenhum ficheiro do repositório. Na dúvida, `duvida`.
6. Responde a todos os diplomas do ficheiro e confirma com python que o JSON é válido. No fim, diz em poucas linhas o veredicto de cada diploma (id e certo/reparos/duvida) e os problemas.
