# Escrever perguntas de leigo para cada artigo

Recebes um ficheiro `entrada-NN.jsonl`. Cada linha é um artigo em vigor de um código ou de uma lei geral portuguesa (o Código Civil, o Penal, os de processo, os dos impostos, o da Estrada, o do Trabalho e outros), com os campos `documento`, `chave`, `titulo`, `parte`, `epigrafe`, `texto` e `sha`. A `parte` e o `titulo` dizem-te de que código é o artigo.

Para cada artigo escreves **3 a 5 perguntas** como as faria uma pessoa sem formação jurídica que tem a dúvida a que o artigo responde. As perguntas vão ajudar a pesquisa a encontrar este artigo quando alguém escreve com as palavras do dia a dia.

Usa só o que vem na entrada. Não leias mais nenhum ficheiro, nem do repositório nem de fora. Em particular, nunca abras nada em `avaliacao/` nem em `rag/resultados/`.

## Formato
Uma linha JSON por artigo, no ficheiro de saída indicado, com o mesmo `documento` e a mesma `chave` da entrada:

`{"documento": "...", "chave": "...", "perguntas": ["...?", "...?", "...?"]}`

Escreve uma linha para todos os artigos da entrada, pela mesma ordem.

## As perguntas
- **Quem pergunta:** uma pessoa comum com um problema concreto. Um trabalhador ou o dono de uma pequena empresa, um inquilino ou um senhorio, um contribuinte, um condutor, um herdeiro, um pai ou uma mãe, alguém que foi vítima de um crime ou que foi acusado, alguém que tem um processo em tribunal ou uma questão com a câmara ou com as Finanças. Não é advogado e não sabe os termos técnicos.
- **Palavras do dia a dia**, em português de Portugal. Por área:
  - **trabalho e arrendamento:** patrão ou empresa (não «empregador»), inquilino (não «arrendatário»), senhorio (não «locador»), casa ou loja arrendada (não «locado»), despedir, horas extra, folga, baixa, recibo, renda, sair de casa;
  - **impostos:** as Finanças (não «a Autoridade Tributária» nem «a administração tributária»), pagar impostos, a declaração do IRS, o reembolso, descontar, passar fatura, recibos verdes, multa das Finanças (não «coima»), dívida às Finanças, penhora, vender a casa, a casa onde moro, herança, o IMI da casa, o selo do carro;
  - **crimes e processo penal:** fazer queixa à polícia (não «apresentar denúncia» nem «queixa-crime»), ser acusado, ir a tribunal, o juiz, ir preso, cadeia (não «pena de prisão efetiva»), pena suspensa, multa, ficar com cadastro, roubo, burla, agressão, a vítima, testemunha, advogado oficioso, ficar em prisão preventiva;
  - **processo civil e tribunais:** pôr um processo, meter em tribunal (não «propor uma ação»), ser processado (não «ser citado» nem «réu»), a outra parte, recorrer, o prazo para responder, penhorar o ordenado, cobrar uma dívida, as custas, a sentença;
  - **família e sucessões:** casar, divórcio, pensão de alimentos, guarda dos filhos (não «responsabilidades parentais»), herança, herdeiros, testamento, partilhas, união de facto, perfilhar, registar um filho, mudar de nome;
  - **administração pública e funcionários públicos:** a câmara, o Estado, um serviço público, um pedido que ficou sem resposta (não «indeferimento tácito»), reclamar de uma decisão, funcionário público, concurso, a função pública, uma obra pública, um contrato com o Estado, expropriarem-me o terreno;
  - **trânsito:** carta de condução, multa, tirar pontos à carta, apanhado com álcool, excesso de velocidade, estacionar, apreenderem o carro, seguro, acidente, peão, trotinete;
  - **empresas e negócios:** abrir uma empresa, sócio, quota, gerente, a empresa faliu, ficar falido, ações na bolsa, marca, patente, direitos de autor, publicidade enganosa, cooperativa.

  Uma palavra técnica só entra se uma pessoa comum também a usa (férias, salário, despedimento, contrato a prazo, IRS, IVA, IMI, herança, divórcio, penhora, insolvência, coima quando é a palavra da carta que a pessoa recebeu).
- **Varia o jeito.** Junta pelo menos dois destes:
  - uma pergunta direta («Quantos dias de férias tenho por ano?», «Quanto tempo tenho para pagar o IMI?»);
  - um caso concreto na 1.ª pessoa ou de alguém próximo («O meu irmão foi apanhado a conduzir com álcool. Fica sem carta?», «A minha mãe morreu sem testamento. Quem fica com a casa?»);
  - a dúvida de quem não sabe por onde começar («O que acontece se eu não pagar a renda dois meses?», «Recebi uma carta do tribunal a dizer que me estão a processar. E agora?»).
- **Cada pergunta tem resposta neste artigo**, mesmo que só em parte. As perguntas cobrem coisas diferentes que o artigo diz (o prazo, quem pode, o que acontece se…), não são cinco maneiras de dizer a mesma coisa.
- Num artigo curto, abstrato ou muito técnico (uma definição, um princípio, um âmbito, uma regra de processo, uma regra de cálculo), pergunta o que levaria uma pessoa a precisar dele: «O que conta como contrato de trabalho?», «Se vender a casa onde moro tenho de pagar imposto sobre o lucro?», «Posso faltar ao julgamento se for testemunha?». Se o artigo só interessa a quem trabalha na área (um contabilista, um notário, uma empresa cotada em bolsa), escreve as perguntas como as faria essa pessoa ou o cliente dela, com palavras simples.
- **Não cites** números de artigos, números nem alíneas, nem nomes de diplomas ou as suas siglas («Código Civil», «Código Penal», «Código da Estrada», «Código do IRS», «Lei Geral Tributária», «CPC», «CIRS», «NRAU», «Lei n.º…», «Decreto-Lei…»). Podes dizer «a lei». Podes falar do imposto ou da instituição pelo nome do dia a dia (o IRS, o IVA, o IMI, as Finanças, o registo civil, o notário), só não do código.
- Não copies frases do artigo. Uma pessoa comum não fala assim.
- Cada pergunta tem 4 a 40 palavras e acaba em «?». Escreve uma só pergunta por entrada da lista: pode ter uma frase de contexto antes.

## No fim
Escreve o ficheiro com a ferramenta Write. Confirma com um pequeno script Python que:
- cada linha é JSON válido;
- há uma linha para cada `chave` da entrada;
- cada linha tem 3 a 5 perguntas, diferentes entre si, cada uma com 4 a 40 palavras e a acabar em «?»;
- nenhuma pergunta tem «artigo», «alínea», «n.º», «.º», «Decreto», «Lei n.º», «Lei Geral Tributária», «Lei Geral do Trabalho em Funções Públicas», nem «Código» seguido do nome de um código («Código Civil», «Código Penal», «Código do…», «Código da…», «Código de Processo…»), nem uma sigla de código (CPC, CPP, CPA, CIRS, CIVA, CIMI, LGT, CSC, CIRE…).

Se o script encontrar um problema, corrige o ficheiro e volta a confirmar.

Responde só com uma linha: quantos artigos e quantas perguntas escreveste.
