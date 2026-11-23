## Adenda da camada 1 (ronda 115)

Estes diplomas já foram pedidos antes e a resposta não passou. Alguns trazem, logo no início, os reparos dessa resposta. Valem as regras de cima, com mais estas.

### Imagens

- **Um anexo, quadro ou mapa que só existe em imagem e que o alterador substitui por inteiro**, com a imagem nova no texto do alterador («[(ver documento original)](endereço)»). Se o anexo tem título no texto atual («#### Título de divisão: ## Anexo …», com o «Corpo do anexo»), devolve-o em `anexos`. O `texto` é o corpo novo: as linhas da imagem do alterador, copiadas letra a letra.
- **Uma alteração parcial de um quadro em imagem** («é alterado o quadro…», «são aditados ao mapa…»). O `texto` é o corpo atual inteiro, uma linha em branco e as linhas da imagem do alterador.
- **Sem título de anexo no texto atual, ou sem imagem no alterador:** não inventes. Vai para `nao_aplicavel`.
- **As linhas de imagem que já estão no texto atual** («[(ver documento original)](endereço)», às vezes repetidas com o mesmo endereço) fazem parte do texto: num artigo ou anexo que reescreves, as que a instrução não muda copiam-se todas, como estão (ronda 116: a segunda leitura encontrou consolidados que as perdiam).

### `nao_aplicavel`

Uma linha por instrução que não aplicaste, separadas por «\n». A linha tem a forma «Alterador N, <instrução curta>: <motivo>». O motivo começa por uma destas expressões:

- `outro diploma`: a instrução é de outro diploma, e o original só lhe deu a redação ou aparece numa lista;
- `só em imagem`: o texto novo só vem em imagem e não há título de anexo onde o pôr;
- `não textual`: prorrogação, designação, «ao abrigo de», suspensão, declaração de inconstitucionalidade sem eliminar o texto;
- `revogação condicional`: «na parte em que contrarie»;
- `efeito adiado`: a revogação depende de um facto futuro;
- `sem texto`: o alterador não traz a alteração;
- `alvo incerto`: não se sabe com segurança onde se aplica. Diz porquê.

Se tudo ficou aplicado, `nao_aplicavel` é null.

### Ronda 117

Na ronda 116, as respostas recusadas falharam sobretudo nestes três pontos:

- **Substituir, não acrescentar.** Quando um alterador dá nova redação a um artigo, a um número ou a uma alínea, devolve o artigo inteiro com o texto em vigor e sem o texto antigo. O corpo antigo não pode ficar a seguir à nova redação, nem a seguir a «(Revogado.)», nem depois de um título de divisão dentro do artigo («##### Divisão de …»). Se esse título era a epígrafe do artigo revogado, põe-na em `epigrafe` e tira-a do corpo.
- **O texto vem das fontes, não dos reparos.** Cada parágrafo novo é copiado letra a letra do diploma que altera ou do texto atual. Um reparo pode dizer qual é o texto certo, mas só o usas se o encontras numa fonte. Se não o encontras, vai para `nao_aplicavel` com o motivo.
- **«(Revogado.)» é o corpo, não o título.** O título fica `###### Artigo N.º — Epígrafe` e o corpo é «(Revogado.)».
