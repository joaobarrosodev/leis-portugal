# Instruções para a revisão

Obrigado por aceitar rever este trabalho. O `leis-portugal` é um sistema que responde a perguntas sobre legislação portuguesa a partir dos artigos que encontra no acervo. Até agora, todas as respostas foram avaliadas por modelos de IA. A sua revisão é a primeira feita por uma pessoa com formação jurídica, e serve para saber quanto valem esses números.

Há duas revisões, que pode fazer em separado:

1. **Respostas** (cerca de 160): uma pergunta, a resposta do sistema e o texto dos artigos que ele leu.
2. **Consolidações** (150 artigos): um artigo de um diploma alterado, no original e na versão consolidada pelo `leis-portugal`, com o texto dos diplomas que o alteram.

Cada revisão tem um **pacote** para ler (`pacote.html`, abre em qualquer browser e imprime-se) e uma **folha** para preencher (`folha.csv`, abre no Excel). O número de cada linha da folha é o número no pacote.

## Como trabalhar

- **Não precisa de abrir o Diário da República** para a maior parte dos casos: o texto integral dos artigos está no pacote. As ligações oficiais estão lá para quando quiser confirmar.
- **Sessões de 1 a 2 horas, no máximo.** A ordem é aleatória de propósito. Medimos a concordância no primeiro e no último terço para ver se o cansaço pesa.
- **Registe os minutos** que levou em cada linha, mesmo aproximados. Serve para planear as próximas revisões.
- **Use "duvida" sem receio.** Se não conseguir decidir sem uma pesquisa demorada, é melhor "duvida" do que um palpite. As dúvidas contam-se à parte.
- **Não sabemos o que espera.** Não lhe mostramos os vereditos dos avaliadores automáticos nem a resposta que tínhamos como certa. Julgue pela lei.

## 1. Respostas

Leia a pergunta, a data de referência (a resposta deve valer para essa data), a resposta, os avisos e os artigos. Os artigos que a resposta cita estão marcados com uma barra à esquerda.

### Veredicto (coluna `veredicto`)

Quando o sistema respondeu:

| Valor | Quando |
|---|---|
| `certa` | A conclusão está certa e a base legal é a exata, sem omissões relevantes para o que se pergunta. |
| `reservas` | A conclusão principal está certa, mas falta uma exceção, condição ou prazo secundário. |
| `errada` | A conclusão principal está errada, aplica uma norma revogada ou desatualizada, ou inventa uma regra. |
| `duvida` | Não consegue decidir sem uma pesquisa demorada. |

A fronteira entre `reservas` e `errada` é a conclusão. Se quem lê a resposta e age de acordo com ela fica bem, é `reservas`. Se fica mal (perde um prazo, paga o que não deve, julga ter um direito que não tem), é `errada`. Uma remissão secundária em falta, por si só, não torna uma resposta errada.

Quando o sistema não respondeu:

| Valor | Quando |
|---|---|
| `recusa_correta` | Não havia resposta segura na lei do acervo: lei inexistente, pedido de aconselhamento sobre um caso concreto, jurisprudência, lei estrangeira, ou artigos que de facto não respondem. |
| `recusa_indevida` | A resposta estava na lei, e de preferência nos artigos que o sistema leu e rejeitou. |
| `duvida` | Não consegue decidir. |

### Gravidade (coluna `gravidade`, só nas `reservas`)

- `menor`: a omissão importa em alguns casos (uma exceção pouco comum, um prazo acessório).
- `forma`: não muda nada para quem pergunta (designação, numeração, citação incompleta).

Uma resposta `errada` é sempre grave. Não precisa de preencher a gravidade.

### Causa (coluna `causa`, nas `reservas`, `errada` e `recusa_indevida`)

Escolha a principal; se houver outra, diga-a na nota.

| Valor | O que é |
|---|---|
| `pesquisa` | O sistema não encontrou a norma certa: leu outro diploma, um artigo vizinho, ou o regime geral em vez do especial. |
| `versao` | Usou uma redação de outra data: o texto original de um artigo depois alterado, ou uma data de entrada em vigor ou de produção de efeitos errada. |
| `vigencia` | Tratou como em vigor uma norma revogada ou caducada, ou o contrário. |
| `consolidacao` | O artigo citado vem de uma versão consolidada pelo `leis-portugal` (o aviso diz "sem valor oficial") e é essa versão que está errada. |
| `leitura` | O artigo é o certo, mas a resposta diz outra coisa: um número, um prazo, uma condição ou uma exceção trocados ou omitidos. |
| `interpretacao` | A resposta precisava de outra norma (uma remissão, o regime especial, a articulação entre diplomas) ou de jurisprudência. |
| `outra` | Explique na nota. |

### Base (coluna `base_certa`)

`sim` se tudo o que a resposta afirma está escrito nos artigos citados; `nao` se a resposta afirma algo que não está lá, mesmo que seja verdade.

### Nota (coluna `nota`)

Uma frase quando não é `certa`: o que está mal e, se souber, qual é a norma certa. É a coluna mais útil para corrigir o sistema.

### Segunda volta

Depois de entregar a folha, fazemos as contas. Nas respostas em que o seu veredicto e o dos avaliadores automáticos não coincidem (contamos que sejam poucas), mandamos-lhe uma `segunda-volta.html`. Tem a resposta que tínhamos como certa e pergunta se essa referência estava certa, incompleta ou errada. Serve para saber se o erro estava no sistema ou no nosso conjunto de avaliação.

## 2. Consolidações

O DRE não consolida milhares de diplomas alterados. Para esses, o `leis-portugal` aplica as alterações publicadas, por regras ou com um modelo de IA, e marca o resultado como "sem valor oficial". Cada número do pacote é **um artigo** (ou o corpo de um anexo). Mostra o original publicado e a versão consolidada lado a lado, e, por baixo, os artigos dos diplomas alteradores que falam deste diploma.

A pergunta é sempre a mesma: **a versão consolidada é exatamente a redação que resulta das alterações publicadas?**

| `veredicto` | Quando |
|---|---|
| `certo` | É a redação em vigor depois das alterações indicadas. |
| `errado` | Não é. |
| `duvida` | Não dá para decidir com o que está no pacote (por exemplo, a alteração está num quadro só em imagem). |

Quando é `errado`, preencha o `erro`:

| `erro` | O que é |
|---|---|
| `mal_aplicada` | Uma instrução de alteração foi aplicada, mas mal: palavra, número ou alínea errados, no sítio errado, ou só em parte. |
| `esquecida` | Uma instrução dirigida a este artigo não foi aplicada. |
| `sem_instrucao` | O artigo mudou sem que nenhum diploma alterador o mande. |
| `condicional` | Foi aplicada uma revogação ou alteração condicional, adiada ou com ressalvas como se fosse imediata e pura. |
| `forma` | O conteúdo está certo e só a forma não: epígrafe, numeração, nota de alteração. |
| `outro` | Explique na nota. |

E a `gravidade`: `grave` se muda o sentido da norma, `menor` se muda um pormenor, `forma` se não muda nada.

Alguns números trazem o aviso "o DRE diz *Altera Artigo X*, mas a versão consolidada deixou este artigo igual". Nesses, diga se havia de facto uma alteração ao texto (`errado`, `esquecida`) ou não (`certo`; o DRE às vezes assinala alterações que não mudam a letra do artigo).

## 3. Perguntas diretas

Estas não têm folha: responda por escrito como achar melhor, com a fundamentação que entender. São dúvidas que o sistema não consegue resolver sozinho.

1. **Entrada em vigor antes de 30/07/1983.** Para os diplomas sem cláusula de entrada em vigor, usamos a regra supletiva da lei formulário (Lei n.º 74/98, art. 2.º, n.º 2; antes, Lei n.º 6/83). Que regra supletiva se aplica aos diplomas publicados antes de 30/07/1983, e por que períodos?
2. **Regiões autónomas e estrangeiro.** A regra supletiva é a mesma para os diplomas nacionais nos Açores e na Madeira, e para os diplomas regionais? Mudou ao longo do tempo?
3. **"Dia útil".** Nas cláusulas como "no primeiro dia útil seguinte ao da sua publicação", que dias contam como não úteis: sábados, feriados nacionais, feriados municipais, tolerâncias de ponto?
4. **"É revogada toda a legislação em contrário".** Há algum critério seguro para dar como revogado um diploma concreto a partir de uma norma revogatória genérica, ou é sempre uma questão de interpretação caso a caso?
5. **Revogação com exceções.** Quando uma lei revoga outra "com exceção dos artigos…" (como a Lei n.º 7/2009 fez ao Código do Trabalho de 2003), os artigos ressalvados continuam em vigor sem limite, ou há que ver também se foram depois revogados tacitamente?
6. **Caducidade.** Nos diplomas temporários (leis do Orçamento, regimes excecionais da COVID-19, apoios com prazo), quando se deve dizer "caducado" e não "em vigor"? Há casos em que normas destes diplomas continuam a produzir efeitos depois do prazo?
7. **Produção de efeitos.** Quando um diploma entra em vigor numa data e produz efeitos noutra (retroativa ou diferida), qual das duas deve o sistema usar para dizer "a redação em vigor na data X"?
8. **Consolidações sem valor oficial.** Para um advogado, a versão consolidada pelo `leis-portugal`, com a indicação "sem valor oficial" e uma nota com o diploma alterador em cada artigo, é útil? O que teria de dizer para ser usada com segurança?
