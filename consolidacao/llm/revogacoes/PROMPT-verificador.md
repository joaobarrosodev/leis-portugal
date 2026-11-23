# Verificador às cegas: revogações registadas só como `repealed_by`

Prompt dado a cada subagente verificador (Sonnet) de `consolidacao/revogacoes.py`.

Lês um ficheiro `verificacao-entrada-K.jsonl`, com um item por linha. Cada item é um par (consolidado, diploma que revoga) e traz:

- `texto_do_alterador` e `rotulos_dre`: o diploma que revoga e o que o DRE diz que ele revoga;
- `alteracoes_feitas`: as mudanças ao consolidado. Cada uma tem `paragrafo_antes` e `paragrafo_depois`, em Markdown cru; «(parágrafo apagado)» quer dizer que a linha saiu. Traz também o `contexto` (o título acima e os parágrafos vizinhos) e, às vezes, `nota_do_respondedor`, que não é prova;
- `efeitos`: a data de efeitos que o respondedor pôs (ou null);
- `nao_aplicadas`: o que ficou por aplicar e porquê.

Para cada item, decide se as mudanças aplicam corretamente a revogação a este consolidado. Confirma:

1. **A disposição está no texto do diploma que revoga e é dirigida a este consolidado.** O número e a data que ela cita são os dele. Se é de outro diploma, qualquer mudança é `errado`.
2. **Cada mudança revoga exatamente o que a disposição revoga, e no sítio certo.** Um artigo inteiro fica com o título igual e o corpo «(Revogado.)». Um número fica «N - (Revogado.)» e uma alínea «a) (Revogada.)». Não se revoga nada a mais, nem um artigo excetuado. Uma revogação condicional («na parte em que contrarie», «no que se refere a…») aplicada ao texto é `errado`.
3. **Não fica nada por revogar** do que a disposição revoga e está nas mudanças à volta. O que ficou por aplicar tem de estar em `nao_aplicadas`, com um motivo que se vê no item.
4. **A data de efeitos.** Se o texto do diploma que revoga dá uma data de efeitos própria, `efeitos` tem de ser essa data. Se não dá, tem de ser null.

Veredicto por item: `certo`, `errado` (diz qual mudança e porquê) ou `duvida` (diz porquê). Na dúvida, `duvida`.

Saída: `verificacao-saida-K.jsonl`, na mesma pasta, uma linha por item: `{"n": <n>, "veredicto": "certo|errado|duvida", "motivo": "<uma frase>"}`. Usa o `n` do item. Lê o ficheiro com python, um item de cada vez.

**Itens sem mudanças** (`alteracoes_feitas` vazio): o respondedor diz que nada se aplica. Confirma no texto do diploma que revoga que o motivo de cada `nao_aplicadas` é verdadeiro. Por exemplo, «outro diploma» quer dizer que a disposição revoga outro diploma e não este. Se for verdadeiro, é `certo`. Se a disposição revoga partes deste consolidado e nada foi aplicado, é `errado`.

**2.ª passagem (`r2v`).** Nos itens desta passagem, `texto_do_alterador` é o texto que o respondedor leu. Quando o diploma que revoga é grande, são só os artigos que mencionam este consolidado (`texto_do_alterador_cortado` diz se ainda assim foi cortado). Os itens sem mudanças, ou com o motivo «já aplicada», trazem também `texto_em_vigor`: as linhas do consolidado de hoje que o respondedor viu, numeradas («L123: …»). Usa-as para confirmar «já aplicada» (a linha já diz «(Revogado.)») e para ver se o que a disposição revoga existe no texto. `texto_em_vigor_parcial` true quer dizer que há linhas que não vês. Uma disposição que não está no texto que tens continua a ser `duvida`.

**Entrada em vigor diferida.** Se o diploma que revoga só entra em vigor algum tempo depois de publicado («entra em vigor 90 dias após a publicação») e não dá à revogação uma data própria, `efeitos` null é `certo`. A entrada em vigor do diploma calcula-se à parte, a partir dos metadados.
