---
schema_version: '1.0'
id: pt:cnpd:7788
title: Autorização da CNPD n.º 16/2005
short_title: null
summary: INSTITUTO DE INFORMÁTICA DO MINISTÉRIO DAS FINANÇAS — Biometria, acesso,impressão digital
jurisdiction: regulator
territory: null
document_type: autorizacao-cnpd
document_type_label: Autorização da Comissão Nacional de Proteção de Dados
issuing_authority:
- Comissão Nacional de Proteção de Dados
proposing_entity: null
official_number: 16/2005
official_date: '2005-01-25'
publication_date: null
publication: null
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes:
- 'Entidade: INSTITUTO DE INFORMÁTICA DO MINISTÉRIO DAS FINANÇAS'
- 'Texto obtido por OCR em 7 de 7 página(s) (digitalização): pode ter erros de reconhecimento.'
language: por
version:
  kind: original
  label: Texto da decisão publicada no site da CNPD
  language: por
  consolidation_date: null
identifiers:
  celex: null
  eli: null
  oj: null
  dre: null
  dre_path: null
  internal: pt:cnpd:7788
source:
  id: cnpd
  name: Comissão Nacional de Proteção de Dados
  official_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/7788
  metadata_url: https://www.cnpd.pt/decisoes/historico-de-decisoes/?year=2005&type=1
  content_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/7788
  consolidated_url: null
  retrieved_at: '2026-11-13T14:33:38Z'
  retrieval_method: Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API
  source_modified_at: null
integrity:
  source_sha256: bc5a367421685ff077c781dea8a66bb66b8ff9b523e81d2b38c5dedc36aa587e
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal CNPD
  collector_version: 0.1.0
  generated_by: leis-portugal collect cnpd
  generated_at: '2026-11-13T14:33:38Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: Comissão Nacional de Proteção de Dados (www.cnpd.pt) — todos os direitos reservados
  reference: https://www.cnpd.pt/avisos-legais-e-outras-informacoes/
  notes: Reprodução total ou parcial permitida com distribuição gratuita, integridade dos documentos e citação expressa do
    site com a menção de direitos reservados; uso pessoal, associativo ou profissional, sem fins comerciais ou publicitários.
    Só a cópia certificada tem valor legal.
subjects: []
relationships: []
article_structure: null
derived_material:
  machine_generated: true
  notes: null
validation:
  status: validated
  checked_at: '2026-11-13T14:33:38Z'
  warnings: []
  errors: []
---

# Autorização da CNPD n.º 16/2005

COMISSAO NACIONAL
DE PROTECÇÃO DE DADOS
Proc. 1754/2003
AUTORIZAÇÃO N.° 16 /2005 1. O Instituto de Informática do Ministério das Finanças colocou nos seus serviços um sistema biométrico para controlo e registo de acessos a locais reservados, nomeadamente ao Centro de Processamento de Dados.
A CNPD proferiu projecto de autorização. O IIMF veio alterar o sistema que estava a utilizar.
Veio, agora, notificar à CNPD um tratamento de dados biométricos (impressão digital).
Refere o seguinte:
a) Na base de dados central é apenas guardada informação referente ao código do cartão que valida a utilização do mesmo no sistema, mas não existe qualquer informação referente ao utilizador;
b) Quando o utilizador apresenta o cartão ao terminal, é validado o cartão e comparada a informação biométrica residente no cartão com a informação obtida na leitura biométrica do momento;
c) Em face da confirmação ou não confirmação, são executados os procedimentos programados no terminal.
d) Este processo inclui uma validação biométrica, mas não necessita de constituir uma base de dados central. A base de dados de referência é a que existe no cartão, que tem a característica pessoal e móvel.
Apreciação jurídica do tratamento de dados biométricos 1. Os sistemas biométricos são constituídos por um sistema informático - que integra hardware (computador e respectivos periféricos necessários, em função do tipo de técnica utilizada) e software respectivo, adquiridos junto do respectivo fornecedor -funcionando de forma similar. É possível diferenciar as seguintes fases distintas: a fase da captura do dado biométrico («módulo de inscrição»), a fase da apresentação do
Rua de São Bento, 148 - 3.° — 1200-821 LISBOA — Telefone: 213 928 400 - Fax: 213 976 832
E-mail: geral@cnpd.pt
Internet: http://www.cnpd.pt

2
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS interessado perante o leitor, que irá obter as suas características biométricas, procedendo o sistema à comparação, em tempo real, com o modelo armazenado e, em seguida, à resposta adequada (fase da «identificação»/«autenticação»).
Conforme a tecnologia, procede-se ao armazenamento da informação recolhida e à «codificação» dos dados recolhidos através de «um processo de algoritmização»(') que, de forma automática, gera "a respectiva chave binária - também denominada «assinatura biométrica» - identificativa da pessoa em causa. Este template, que é armazenado na respectiva base de dados ou num cartão (o caso deste processo), será relacionado com a identificação do utilizador, por forma a assegurar o respectivo «processo de identificação».
Por isso, quando o utilizador solicita a identificação perante o sistema, a sua característica fisica, captada pelo sensor de forma analógica, é convertida e representada digitalmente a fim de que, internamente, possa ser comparada com o modelo biométrico («template»).
No caso em apreço o sistema biométrico já não utiliza a tecnologia de digitalização da imagem recolhida, fazendo a «codificação» dos dados recolhidos. Ou seja, não estaremos perante um ficheiro que digitaliza as características da impressão digital, mas perante um ficheiro que regista os modelos ou templates (chave binária), de forma encriptada, representativos do valor ou padrão numeralizado das características da impressão digital de cada utilizador.
Em resultado da identificação do utilizador através do seu número de funcionário o sistema faz a comparação entre o template e a captação das características da impressão digital apresentadas ao leitor; a resposta representa o resultado do procedimento de «identificação»/«autentição», em função da opção escolhida.
De referir, igualmente, que o sistema biométrico que, através do processo de algoritmização, gerou o template que representa numericamente a característica biométrica captada, não permite, em geral, fazer a reversão e, por conseguinte, () Sobre o conceito de algoritmo e suas características veja-se Claudio Gutiérrez - "El algoritmo
Informático" (in http://www.claudigutierrez.com/el algoritmo_informatico.html).
() Veja-se in http://www.imasters.com.br/web/conteudo/coluna_segurança.asp?codColuna=231 um artigo de Alexandre Lopes - "Biometria", 9/9/2002 e Didier Godart - "Sécurité Informatique", Risques,
Stratégies et Solutions, Editions de la Chambre de Commerce et d'Industrie, Belgique, 2002, pág. 168.
Rua de São Bento, 148 - 3.° — 1200-821 LISBOA — Telefone: 213 928 400 - Fax: 213 976 832
E-mail: geral@cnpd.pt
Internet: http://www.cnpd.pt

COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS descodificar e reproduzir, de forma digitalizada, a imagem da característica biométrica.
No caso em apreço não é possível a reversão nem existe uma base de dados de características biométricas. Este aspecto é, no nosso ponto de vista, fundamental em termos de protecção da privacidade uma vez que o responsável do tratamento não dispõe de uma base de dados das características da impressão digital de cada trabalhador.
2. O tratamento de dados biométricos, porque estamos perante dados pessoais, deve respeitar todas as condições estabelecidas na Lei 67/98, nomeadamente():
• O tratamento deve ser feito com respeito pela reserva da vida privada (artigo 2.°)
e para finalidades determinadas, explícitas e legítimas (art. 5.° n.° 1 al. b);
• Os dados devem ser adequados, pertinentes e não excessivos em relação à finalidade e proporcionados com objectivos que se pretendem atingir (art. 5.° n.° 1 al. c);
• O responsável só pode proceder ao tratamento se, de acordo com a natureza dos dados (artigo 6.° e 7.°), estiverem preenchidas "condições de legitimidade";
O responsável deve fazer a notificação destes tratamentos à CNPD (art. 27.° n.° 1).
3. No caso em apreço os dados recolhidos são necessários à finalidade que se pretende atingir - o registo do acesso a locais reservados - não se afigurando que sejam excessivos.
A eventual «invasão da privacidade» deve ser abordada nas duas fases do tratamento:
() Veja-se, no mesmo sentido, o Parecer n.º 11/2002, de 3 de Dezembro, pág. 10. Os dados biométricos são apresentados como sinais objectivos e inalteráveis, mas com características específicas que nos levam a considerar que devem ter uma protecção diferente em relação a outros dados de identificação - v.g. o nome, a data ou o local de nascimento. A comprovar esta ideia refere-se que o artigo 25.º n.° 8 do projecto de lei francesa, que visa transpor a Directiva 95/46/CE, impõe um regime de autorização da CNIL - sem estabelecer as condições em que tal autorização pode ser dada ou recusada - em relação ao tratamento de dados biométricos necessários ao controlo da identidade das pessoas.
Rua de São Bento, 148 - 3.° — 1200-821 LISBOA — Telefone: 213 928 400 - Fax: 213 976 832
E-mail: geral@cnpd.pt
Internet: http://www.cnpd.pt

COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS a) Na fase da captura das características biométricas e do seu subsequente armazenamento no sistema;
b) Na fase de autenticação/identificação com o objectivo de assegurar o reconhecimento do utilizador perante o sistema.
4. A operação de captação de dados biométricos - que implica a cooperação/anuência do trabalhador através da «exposição» da respectiva parte do seu corpo (dedo) para tratamento das características da sua identidade pessoal - não pode ser realizada com violação da sua identidade pessoal (art. 26.° da CRP), com lesão da sua integridade física* (art. 25.° n.° 1 da CRP) ou com intromissão na intimidade da vida privada.
Para apreciação do «grau de intromissão» pensamos que é fundamental considerar a forma como se obtêm os elementos de identificação e as finalidades que estão na base da colheita de características físicas dos trabalhadores (v.g. se representam finalidades discriminatórias).
Em relação à colheita de dados biométricos em apreço (impressão digital) a captação não tem qualquer implicação com a integridade física do trabalhador(). Efectivamente, a finalidade visada ou a forma como os elementos da identidade são captados não têm, pelo menos, implicações no recato ou no pudor. Por isso, não nos parece que a simples operação de recolha, em exclusivo, para os fins indicados possa afectar o direito à identidade pessoal e da intimidade da vida privada, garantidas constitucionalmente no artigo 26.° da CRP.
Importa, por outro lado, assegurar que a submissão à operação de recolha não se poderá traduzir numa discriminação ou violação do dever de respeito e dignidade do trabalhador. Ora, a finalidade que está subjacente à captação destes dados não envolve qualquer discriminação ou desconfiança em relação ao trabalhador. Pensamos que não é (*) Veja-se, no mesmo sentido, Jennifer Stoddart - in Des Technologies de Surveillance sous
Surveillance" - La 23. Conférence Internationale des Commissaires à la Protection des Données, Paris, 24/26 de Setembro de 2001, pág. 113. Este autor, reportando-se à lei que regula o quadro jurídico das tecnologias de informação no Québec, salienta que, no capítulo dos direitos fundamentais, se prevê que ninguém pode exigir que a identidade de uma pessoa seja estabelecida por meio de um processo ou de um dispositivo que se traduza numa agressão à sua integridade física".
() A abordagem das implicações desta tecnologia para a saúde não está, como é óbvio, no âmbito das competências desta CNPD.
Rua de São Bento, 148 - 3.° — 1200-821 LISBOA — Telefone: 213 928 400 - Fax: 213 976 832
E-mail: geral@cnpd.pt
Internet: http://www.cnpd.pt

COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS o dado biométrico em si mesmo que pode afectar o direito à privacidade da pessoa, mas a finalidade com que é utilizado e os riscos que apresenta para a própria pessoa (risco de discriminação ou de cruzamento com outros sistemas, consequências produzidas em razão da sua falta de fiabilidade, efeitos na sua esfera pessoal no caso de falsificação ou usurpação da característica biométrica).
Assim, apresentando-se o dado biométrico como o meio adequado para assegurar uma «finalidade legitima» da entidade empregadora, considera a CNPD que a utilização desta tecnologia não envolve, na «fase da captura e armazenamento da característica biométrica» num cartão, qualquer violação dos direitos de personalidade do trabalhador.
Para que o trabalhador possa cooperar no «processo de identificação» é necessário, como é óbvio, que seja assegurada uma efectiva informação prévia, por parte da entidade empregadora, em relação às finalidades determinantes da recolha, aos destinatários e às condições de utilização daqueles dados, em cumprimento do disposto no artigo 10.° n.º 1 da Lei 67/98.
5. Estando assente que o tratamento se insere no âmbito de uma finalidade legítima, importa averiguar se o armazenamento em cartão das características biométricas se apresenta como adequado - conforme com o princípio da proporcionalidade - e se o tratamento está fundamentado numa «condição de legitimidade» legalmente prevista.
Conforme resulta do Parecer da CNPD n.º 11/2002, de 3 de Dezembro, o princípio da proporcionalidade "impõe que qualquer tratamento de dados pessoais, atenta a sua finalidade concreta, deva ser avaliado em termos de idoneidade e de intervenção mínima", o que envolve uma ponderação, casuística, entre a finalidade visada e o risco de utilização indevida dos dados para outras finalidades(*).
Num «balaceamento» dos interesses em presença - dos trabalhadores e do responsável do tratamento - considera a CNPD que o tratamento do template da impressão digital, (°) A ideia de proibir o tratamento com fundamento na existência de perigo de ser utilizado para outras finalidades - v.g. policiais - parece-nos demasiado redutora. Estas preocupações não têm sido evidenciadas em relação ao tratamento de outros dados - cf. no domínio das telecomunicações, no registo de entradas e saídas com utilização de cartões magnéticos, no âmbito do sistema «VIA VERDE» ou na videovigilância. Graças à «codificação» dos templates e à dificuldade de aceder às chaves de desencriptação é mais difícil aceder aos dados biométricos do que aos tratamentos constantes de "bases de dados".
Rua de São Bento, 148 - 3.° — 1200-821 LISBOA — Telefone: 213 928 400 - Fax: 213 976 832
E-mail: geral@cnpd.pt
Internet: http://www.cnpd.pt

COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS da forma e para a finalidade delineada, não apresenta riscos em relação aos direitos de personalidade dos trabalhadores que possam sobrepor-se aos interesses legítimos do responsável (artigo 6.° alínea e) da Lei 67/98).
Deste modo, a CNPD autoriza o tratamento de dados biométricos (impressão digital) -cf. artigo 7º n.º 2, 28.° n.º 1 al. a), 23.° n.º 1 al. b), 27° e 30.° da Lei 67/98 -consignando, em especial, que a informação biométrica não pode ser utilizada para outra finalidade que não seja a finalidade declarada. Termos do tratamento:
1. Responsável: Instituto de Informática do Ministério das Finanças 2. Categorias de dados pessoais tratados: número de funcionário, nome.
3. Finalidade: registo de acesso a locais reservados. Registo de assiduidade.
4. Entidades a quem podem ser transmitidos: Não há comunicação de dados a terceiros.
5. Forma de exercício do direito de acesso e rectificação: Por solicitação ao responsável.
6. Eventuais interconexões: Não há.
7. Transferências de dados para países terceiros: Não há.
8. Prazos de conservação: Os dados deverão ser eliminados logo que o funcionário deixa de prestar serviço para entidade responsável ou quando deixe de poder ter acesso às zonas reservadas.
Lisboa, 25 de Janeiro de 2005 treden
Amadeu Guerra (relator)
alexandes
Alexandre Pinheiro
Luís Durão Barroso
Rua de São Bento, 148 - 3.° — 1200-821 LISBOA — Telefone: 213 928 400 - Fax: 213 976 832
E-mail: geral@cnpd.pt
Internet: http://www.cnpd.pt

COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Eduardo Campos
Ana Luísa Geraldes
Luís Lingnau da Silveira (Presidente)
Rua de São Bento, 148 - 3.° — 1200-821 LISBOA — Telefone: 213 928 400 - Fax: 213 976 832
E-mail: geral@cnpd.pt
Internet: http://www.cnpd.pt
