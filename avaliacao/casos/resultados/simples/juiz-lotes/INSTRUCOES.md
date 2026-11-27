# Instruções para os juízes dos casos (medição experimental)

Julgas, às cegas em relação aos outros juízes, a análise que um sistema deu a um caso de advogado. Para cada caso tens o caso completo com a resposta de referência (`casos.jsonl`: narrativa, leis pensadas, questões, artigos essenciais, conclusão, prazos e o que fica fora da lei escrita) e a análise do sistema (`analise` e os rótulos dos artigos que citou).

A resposta de referência foi escrita e revista por modelos, sem jurista. Se achares que a referência está errada, diz isso em `nota` e julga pela lei: lê o artigo com `avaliacao/casos/artigo.py ler <caminho> "<chave>"` (no worktree). Não abras outros ficheiros de `avaliacao/` nem de `rag/`.

Para cada caso, responde:
- `leis_pensadas`: para cada lei pensada com `serve` diferente de `sim`, o sistema disse que não serve ou que serve só em parte, com o motivo certo? Conta `acertou` e `total`.
- `prazos`: `certos`, `errados` (algum prazo mal contado ou dado como aberto quando já passou, ou o contrário), `em_falta` (a referência tem um prazo decisivo e o sistema não o dá) ou `nao_ha`.
- `erros`: afirmações jurídicas erradas que levariam o advogado a agir mal (uma frase cada). Imprecisões menores não contam.
- `veredicto`:
  - `certa`: a análise chega ao mesmo resultado prático da referência (o que fazer e o que esperar), sem erros, e trata as leis pensadas que não servem;
  - `parcial`: sem erros, mas falta uma parte decisiva (uma questão, um prazo, uma lei pensada por corrigir);
  - `errada`: tem pelo menos um erro;
  - `recusa`: o sistema não respondeu.
- `nota`: uma frase.

Escreve em `juiz-<letra>-NN.jsonl` uma linha JSON por caso: `{"id", "leis_pensadas": {"acertou", "total"}, "prazos", "erros": [], "veredicto", "nota"}`.
