# Escrever perguntas de leigo para cada artigo

Recebes um ficheiro `entrada-NN.jsonl`. Cada linha é um artigo em vigor de um código, de uma lei geral ou de uma lei avulsa portuguesa (o Código Civil, o Penal, os de processo, os dos impostos, o da Estrada, o do Trabalho e outros; e as leis, decretos-leis e portarias da saúde, da segurança social, da habitação, do consumo e da família), com os campos `documento`, `chave`, `titulo`, `parte`, `epigrafe`, `texto` e `sha`. A `parte` e o `titulo` dizem-te de que diploma é o artigo.

Para cada artigo escreves **3 a 5 perguntas** como as faria uma pessoa sem formação jurídica que tem a dúvida a que o artigo responde. As perguntas vão ajudar a pesquisa a encontrar este artigo quando alguém escreve com as palavras do dia a dia.

Usa só o que vem na entrada. Não leias mais nenhum ficheiro, nem do repositório nem de fora. Em particular, nunca abras nada em `avaliacao/` nem em `rag/resultados/`.

## Formato
Uma linha JSON por artigo, no ficheiro de saída indicado, com o mesmo `documento` e a mesma `chave` da entrada:

`{"documento": "...", "chave": "...", "perguntas": ["...?", "...?", "...?"]}`

Escreve uma linha para todos os artigos da entrada, pela mesma ordem.

## As perguntas
- **Quem pergunta:** uma pessoa comum com um problema concreto. Um trabalhador ou o dono de uma pequena empresa, um inquilino ou um senhorio, um contribuinte, um condutor, um herdeiro, um pai ou uma mãe, alguém que foi vítima de um crime ou que foi acusado, alguém que tem um processo em tribunal ou uma questão com a câmara ou com as Finanças, um doente ou quem cuida dele, alguém que se vai reformar ou ficou desempregado, um cliente de uma loja ou de um banco, um condómino. Não é advogado e não sabe os termos técnicos.
- **Palavras do dia a dia**, em português de Portugal. Por área:
  - **trabalho e arrendamento:** patrão ou empresa (não «empregador»), inquilino (não «arrendatário»), senhorio (não «locador»), casa ou loja arrendada (não «locado»), despedir, horas extra, folga, baixa, recibo, renda, sair de casa;
  - **impostos:** as Finanças (não «a Autoridade Tributária» nem «a administração tributária»), pagar impostos, a declaração do IRS, o reembolso, descontar, passar fatura, recibos verdes, multa das Finanças (não «coima»), dívida às Finanças, penhora, vender a casa, a casa onde moro, herança, o IMI da casa, o selo do carro;
  - **crimes e processo penal:** fazer queixa à polícia (não «apresentar denúncia» nem «queixa-crime»), ser acusado, ir a tribunal, o juiz, ir preso, cadeia (não «pena de prisão efetiva»), pena suspensa, multa, ficar com cadastro, roubo, burla, agressão, a vítima, testemunha, advogado oficioso, ficar em prisão preventiva;
  - **processo civil e tribunais:** pôr um processo, meter em tribunal (não «propor uma ação»), ser processado (não «ser citado» nem «réu»), a outra parte, recorrer, o prazo para responder, penhorar o ordenado, cobrar uma dívida, as custas, a sentença;
  - **família e sucessões:** casar, divórcio, pensão de alimentos, guarda dos filhos (não «responsabilidades parentais»), herança, herdeiros, testamento, partilhas, união de facto, perfilhar, registar um filho, mudar de nome;
  - **administração pública e funcionários públicos:** a câmara, o Estado, um serviço público, um pedido que ficou sem resposta (não «indeferimento tácito»), reclamar de uma decisão, funcionário público, concurso, a função pública, uma obra pública, um contrato com o Estado, expropriarem-me o terreno;
  - **trânsito:** carta de condução, multa, tirar pontos à carta, apanhado com álcool, excesso de velocidade, estacionar, apreenderem o carro, seguro, acidente, peão, trotinete;
  - **saúde:** o centro de saúde, o hospital, as urgências, o médico de família, a consulta, a cirurgia, a lista de espera, pagar a consulta ou a taxa moderadora, a ambulância para ir a uma consulta, o atestado de incapacidade, a percentagem de incapacidade, o testamento vital, cuidar de um familiar doente, o cuidador, a interrupção da gravidez ou o aborto, os tratamentos para engravidar, a inseminação, a fertilização in vitro, a barriga de aluguer, os dadores de esperma ou de óvulos, fazer queixa do hospital, ver o meu processo clínico;
  - **segurança social:** a Segurança Social (não «a instituição de segurança social»), o RSI ou rendimento social de inserção, ter um acidente no trabalho ou a caminho do trabalho, o seguro de acidentes de trabalho, uma doença profissional, ficar com uma incapacidade, precisar de ajuda de outra pessoa para o dia a dia, a reforma (não «pensão de velhice»), reformar-me mais cedo, quanto vou receber de reforma, a pensão de invalidez, a pensão de viuvez, o subsídio de desemprego, ficar desempregado, a baixa por doença, a licença de maternidade ou de paternidade, o abono dos filhos, os descontos, um apoio para pessoas com deficiência, um complemento para idosos, os rendimentos lá de casa;
  - **habitação:** o empréstimo da casa, o banco, a prestação da casa, pagar o empréstimo antes do tempo, a casa da câmara ou a habitação social, a renda da habitação social, as obras na casa arrendada, o condomínio, o administrador do condomínio, as partes comuns do prédio, a reunião de condóminos, pôr o inquilino na rua (despejo), o contrato de arrendamento;
  - **consumo:** a loja, comprei, devolver, trocar, a garantia, avariou, o reembolso, comprar pela internet, cancelar uma encomenda, o livro de reclamações, fazer uma reclamação, saldos e promoções, o preço na etiqueta, o crédito para comprar o carro ou um eletrodoméstico, as letras pequenas do contrato, a viagem organizada, a agência de viagens, a fatura da luz, da água ou do telefone, cortarem-me a luz, um produto com defeito que me fez mal;
  - **família e crianças:** a guarda dos filhos, a pensão de alimentos que o pai ou a mãe não paga, a comissão de proteção de crianças, retirarem os filhos aos pais, adotar uma criança, ser padrinho de uma criança, violência doméstica, ser agredida pelo marido ou pelo companheiro, a casa abrigo, viver juntos sem casar, divórcio na conservatória, viver com um amigo ou um familiar e partilhar as despesas;
  - **mediação e justiça:** resolver um problema sem ir a tribunal, um mediador, chegar a acordo, o acordo vale como uma sentença?, a mediação é confidencial?, quanto custa;
  - **benefícios fiscais e transporte de mercadorias:** pagar menos imposto, não pagar IMI durante uns anos, descontos no IRS por ter filhos ou por poupar, a isenção de imposto, a guia de transporte, a fatura que acompanha as mercadorias na carrinha, ser parado pela GNR com a mercadoria;
  - **empresas e negócios:** abrir uma empresa, sócio, quota, gerente, a empresa faliu, ficar falido, ações na bolsa, marca, patente, direitos de autor, publicidade enganosa, cooperativa.

  Uma palavra técnica só entra se uma pessoa comum também a usa (férias, salário, despedimento, contrato a prazo, IRS, IVA, IMI, herança, divórcio, penhora, insolvência, coima quando é a palavra da carta que a pessoa recebeu).
- **Varia o jeito.** Junta pelo menos dois destes:
  - uma pergunta direta («Quantos dias de férias tenho por ano?», «Quanto tempo tenho para pagar o IMI?»);
  - um caso concreto na 1.ª pessoa ou de alguém próximo («O meu irmão foi apanhado a conduzir com álcool. Fica sem carta?», «A minha mãe morreu sem testamento. Quem fica com a casa?»);
  - a dúvida de quem não sabe por onde começar («O que acontece se eu não pagar a renda dois meses?», «Recebi uma carta do tribunal a dizer que me estão a processar. E agora?»).
- **Cada pergunta tem resposta neste artigo**, mesmo que só em parte. As perguntas cobrem coisas diferentes que o artigo diz (o prazo, quem pode, o que acontece se…), não são cinco maneiras de dizer a mesma coisa.
- Num artigo curto, abstrato ou muito técnico (uma definição, um princípio, um âmbito, uma regra de processo, uma regra de cálculo), pergunta o que levaria uma pessoa a precisar dele: «O que conta como contrato de trabalho?», «Se vender a casa onde moro tenho de pagar imposto sobre o lucro?», «Posso faltar ao julgamento se for testemunha?». Se o artigo só interessa a quem trabalha na área (um contabilista, um notário, uma empresa cotada em bolsa), escreve as perguntas como as faria essa pessoa ou o cliente dela, com palavras simples.
- **Não cites** números de artigos, números nem alíneas, nem nomes de diplomas ou as suas siglas («Código Civil», «Código Penal», «Código da Estrada», «Código do IRS», «Lei Geral Tributária», «CPC», «CIRS», «NRAU», «Lei n.º…», «Decreto-Lei…», «Lei de Defesa do Consumidor», «Estatuto do Cuidador Informal», «Estatuto dos Benefícios Fiscais», «EBF», «regime jurídico de…»). Podes dizer «a lei». Podes falar do imposto ou da instituição pelo nome do dia a dia (o IRS, o IVA, o IMI, as Finanças, o registo civil, o notário), só não do código.
- Não copies frases do artigo. Uma pessoa comum não fala assim.
- Cada pergunta tem 4 a 40 palavras e acaba em «?». Escreve uma só pergunta por entrada da lista: pode ter uma frase de contexto antes.

## No fim
Escreve o ficheiro com a ferramenta Write. Confirma com um pequeno script Python que:
- cada linha é JSON válido;
- há uma linha para cada `chave` da entrada;
- cada linha tem 3 a 5 perguntas, diferentes entre si, cada uma com 4 a 40 palavras e a acabar em «?»;
- nenhuma pergunta tem «artigo», «alínea», «n.º», «.º», «Decreto», «Lei n.º», «Lei Geral Tributária», «Lei Geral do Trabalho em Funções Públicas», nem «Código» seguido do nome de um código («Código Civil», «Código Penal», «Código do…», «Código da…», «Código de Processo…»), nem uma sigla de código (CPC, CPP, CPA, CIRS, CIVA, CIMI, LGT, CSC, CIRE…), nem «regime jurídico», «lei de bases», «Lei de Defesa do Consumidor», «Estatuto do Cuidador», «Estatuto do Utente», «Estatuto dos Benefícios Fiscais» ou «EBF».

Se o script encontrar um problema, corrige o ficheiro e volta a confirmar.

Responde só com uma linha: quantos artigos e quantas perguntas escreveste.
