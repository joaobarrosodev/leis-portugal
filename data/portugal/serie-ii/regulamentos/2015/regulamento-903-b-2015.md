---
schema_version: '1.0'
id: pt:dre:72964679:por
title: Regulamento n.º 903-B/2015
short_title: null
summary: Regulamento que define os Requisitos Técnicos do Sistema Técnico do Jogo Online
jurisdiction: portugal
territory: null
document_type: regulamento
document_type_label: Regulamento
issuing_authority:
- Economia - Instituto do Turismo de Portugal, I. P.
proposing_entity: null
official_number: 903-B/2015
official_date: null
publication_date: '2015-12-23'
publication:
  gazette: Diário da República
  reference: Diário da República n.º 250/2015, 1º Suplemento, Série II de 2015-12-23
  number: '250'
  series: II
  supplement: null
  pages: 37588-(3) a 37588-(35)
  pdf_url: https://files.diariodarepublica.pt/2s/2015/12/250000001/0000300035.pdf
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes: []
language: por
version:
  kind: original
  label: Texto publicado no Diário da República
  language: por
  consolidation_date: null
identifiers:
  celex: null
  eli: null
  oj: null
  dre: '72964679'
  dre_path: /dr/detalhe/regulamento/903-b-2015-72964679
  internal: pt:dre:72964679:por
source:
  id: dre
  name: Diário da República Eletrónico
  official_url: https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679
  metadata_url: null
  content_url: https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679
  consolidated_url: null
  retrieved_at: '2026-11-13T06:00:15Z'
  retrieval_method: Endpoints screenservices (OutSystems) da aplicação web do DRE; não é uma API pública documentada
  source_modified_at: null
integrity:
  source_sha256: 318709001d3c8d864ac3f6090f39babfbbe31337d5c4777f53faeedc8c064e0e
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal DRE
  collector_version: 0.1.0
  generated_by: leis-portugal collect dre
  generated_at: '2026-11-13T06:00:15Z'
  notes: null
reuse:
  status: permitted
  attribution: Diário da República Eletrónico — Imprensa Nacional-Casa da Moeda
  reference: http://data.dre.pt/eli/dec-lei/83/2016/p/dr/pt/html
  notes: Acesso universal e gratuito ao Diário da República (artigo 3.º do Decreto-Lei n.º 83/2016) e regime de dados abertos
    (Lei n.º 68/2021). A edição eletrónica do DR é a que faz fé.
subjects:
- Especificação Técnica
- Jogos de Fortuna e Azar
- Jogos e Apostas Online
- Normas de Segurança
- Regulamento
- Segurança da Informação
relationships:
- type: amended_by
  target: pt:dre:74146384:por
  label: Alterado o Anexo I, pelo(a) Regulamento n.º 379-A/2016 - Diário da República n.º 72/2016, 2º Suplemento, Série II
    de 2016-04-13
  source: https://diariodarepublica.pt/dr/analise-juridica/informacoes-gerais/regulamento/379-a-2016-74146384
  date: '2016-04-13'
- type: amended_by
  target: pt:dre:114657935:por
  label: Alterado o Anexo I do presente Regulamento pelo(a) Regulamento n.º 99/2018 - Diário da República n.º 29/2018, Série
    II de 2018-02-09
  source: https://diariodarepublica.pt/dr/analise-juridica/informacoes-gerais/regulamento/99-2018-114657935
  date: '2018-02-09'
- type: cites
  target: pt:dre:191534:por
  label: null
  source: null
- type: cites
  target: pt:dre:239857:por
  label: null
  source: null
- type: cites
  target: pt:dre:483411:por
  label: null
  source: null
- type: cites
  target: pt:dre:58585556:por
  label: null
  source: null
- type: cites
  target: pt:dre:67098359:por
  label: null
  source: null
article_structure:
  article_count: 41
  section_count: 0
  extraction_method: Classes de parágrafo do TextoFormatado do DRE
derived_material:
  machine_generated: true
  notes: Markdown convertido do HTML TextoFormatado do DRE; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-11-13T06:00:15Z'
  warnings: []
  errors: []
---

# Regulamento n.º 903-B/2015

Regulamento que define os Requisitos Técnicos do Sistema Técnico do Jogo Online

1 - Enquadramento Legal

1.1 - Âmbito

O [Decreto-Lei n.º 66/2015](https://diariodarepublica.pt/dr/detalhe/decreto-lei/66-2015-67098359), de 29 de abril, aprovou o Regime Jurídico dos Jogos e Apostas Online (adiante designado por "RJO"), nas suas diversas categorias e tipos, que podem ser exploradas pelos titulares de licença concedida pelo Serviço de Regulação e Inspeção de Jogos (adiante designado por "SRIJ").

1.2 - Objeto

O presente documento tem por objeto desenvolver e descrever os requisitos mínimos, as especificações técnicas e os mecanismos de controlo aos mesmos associados, nos termos dos requisitos estabelecidos no RJO para o sistema técnico de jogo das entidades exploradoras e que com eles devem estar conformes, tendo em vista assegurar a proteção da ordem pública, combater a fraude, prevenir os comportamentos viciantes, proteger os direitos dos menores e salvaguardar os direitos dos jogadores.

As entidades exploradoras, para obterem uma licença, devem ter o seu sistema técnico de jogo certificado, nos termos do programa de certificação definido pelo SRIJ, para a exploração do jogo e das apostas online.

1.3 - Destinatários

O presente documento é dirigido às entidades exploradoras e aos organismos de certificação.

1.4 - Versão

Só a versão portuguesa é legalmente vinculativa, servindo a versão inglesa como mero instrumento de orientação.

1.5 - Definições

(De acordo com as definições constantes do RJO)

"Momento da aposta": O período de tempo que decorre entre o início e o fim do período de aceitação de apostas, denominando-se como "apostas pré-evento", se efetuadas o mais tardar até ao início do ou dos eventos a que respeitam, ou como "apostas em direto", se efetuadas no decurso do ou dos eventos;

"Infraestrutura de controlo": A infraestrutura técnica, gerida pelo SRIJ, para armazenamento e tratamento, em tempo real, dos dados relacionados com a atividade de jogos e apostas online, obtidos através da infraestrutura de entrada e registo;

"Componentes críticos": Hardware, software ou outros componentes que devem existir, em condições de operacionalidade, para que o sistema de jogo online funcione adequadamente;

"Evento": A prova desportiva ou a corrida de cavalos;

"Infraestrutura de entrada e registo": A infraestrutura técnica, gerida pela entidade exploradora, pela qual deve ser encaminhado todo o tráfego de dados entre o jogador e a plataforma de jogo e para a qual devem ser reportadas todas as demais operações relacionadas com a atividade de jogos e apostas online, com vista ao seu registo e reporte para a infraestrutura de controlo;

"Sistema técnico de jogo": O conjunto de hardware e software, gerido pela entidade exploradora, que constitui o interface entre a entidade exploradora e o jogador, pelo qual deve ser encaminhado todo o tráfego de dados entre o jogador e a plataforma de jogo e que inclui a presença na Internet, a infraestrutura de entrada e registo e a plataforma de jogo, integrando bases de dados, o software de jogos e apostas online, o gerador de números aleatórios, os módulos de gestão e todo o demais hardware e software em que se suporte a exploração desta atividade;

"Jogo de fortuna ou azar": O jogo que implica o dispêndio de uma quantia em dinheiro e cujo resultado é contingente por assentar exclusiva ou fundamentalmente na sorte;

"Jogos e apostas online": Os jogos de fortuna ou azar, as apostas desportivas à cota, as apostas hípicas, mútuas e à cota, em que são utilizados quaisquer mecanismos, equipamentos ou sistemas que permitem produzir, armazenar ou transmitir documentos, dados e informações, quando praticados à distância, através de suportes eletrónicos, informáticos, telemáticos e interativos ou quaisquer outros meios;

"Plataforma de jogo": A infraestrutura técnica, gerida pela entidade exploradora, onde se desenvolve a atividade de jogos e apostas online, que integra as bases de dados, o software de jogo, o gerador de números aleatórios, os módulos de gestão e todo o demais hardware e software em que se suporte a exploração desta atividade;

"Software de jogo": As componentes aplicacionais responsáveis pela dinâmica, regras e lógica dos jogos e apostas online;

"Apresentação (skin) do jogo": A designação e apresentação gráfica, personalização ou suporte, de um jogo, através dos quais o software de jogo é apresentado;

"Receita bruta": O valor que resulta da dedução do quantitativo atribuído em prémios ao montante total das apostas realizadas;

"Licença": O título habilitante para explorar uma determinada categoria de jogos ou apostas online;

"Log": Uma tabela que regista automaticamente dados que não devem ser manipulados após o respetivo registo inicial. Quaisquer alterações ao log ocorrerão através do registo de novas entradas em vez de alteração ou eliminação dos registos existentes;

"Mapeamento (mapping)": O processo mediante o qual ao número escalonado produzido por um gerador de números aleatórios é atribuído um símbolo ou valor utilizável e aplicável no jogo em curso (por ex., o número ajustado à escala 51 poderá ter correspondência com o Ás de espadas);

"Entidade exploradora": A entidade titular de uma ou mais licenças portuguesas de jogos ou apostas online;

"Conta de pagamento": Uma conta aberta num prestador de serviços de pagamento, na aceção da alínea a) do artigo 2.º do [Decreto-Lei n.º 317/2009](https://diariodarepublica.pt/dr/detalhe/decreto-lei/317-2009-483411), de 30 de outubro, alterado pelos Decretos-Leis n.os [242/2012](https://diariodarepublica.pt/dr/detalhe/decreto-lei/242-2012-191534), de 7 de novembro, e [157/2014](https://diariodarepublica.pt/dr/detalhe/decreto-lei/157-2014-58585556), de 24 de outubro;

"Jogador": O indivíduo maior de idade que participa nos jogos e apostas online;

"Conta de jogador": A conta associada ao registo de cada jogador, na qual devem ser creditados e debitados todos os movimentos decorrentes da atividade de jogos e apostas online;

"Registo de jogador": O registo único que permite ao jogador aceder à plataforma de jogo da entidade exploradora e do qual constam, nomeadamente, os dados, que permitem a identificação do jogador e os que possibilitam a realização de transações entre este e a entidade exploradora;

"Sessão do jogador": A troca de informações interativa entre um jogador e a plataforma de jogo, entre o momento em que o jogador acede ao sistema técnico de jogo online e o momento em que o jogador sai do sistema, voluntária ou involuntariamente;

"Amplitude": A dimensão efetiva da produção (output) do gerador de números aleatórios. Um gerador de números aleatórios de 32 bits proporciona 232 resultados possíveis (4.29 x 109). Se se considerar uma saída de 64 bits, pode obter-se 1.8 X 1019 resultados diferentes do gerador de números aleatórios;

"Gerador de números aleatórios": O componente de software ou hardware que, garantindo a aleatoriedade, gera os resultados numéricos que são utilizados pela entidade exploradora para determinar o resultado dos jogos de fortuna ou azar;

"Organismo de Certificação Reconhecido": A entidade, incluída numa lista publicada pelo SRIJ, à qual é reconhecida capacidade para certificar sistemas técnicos de jogo;

"Relatório": Extração de dados de um ou mais logs;

"Tipo de resultado": A pergunta subjacente à aposta desportiva ou à aposta hípica sobre um ou vários factos que ocorrem no decurso de determinado período de tempo de um ou vários eventos;

"%RTP": A percentagem esperada de valores totais de aposta que determinado jogo devolverá ao jogador a longo prazo. A %RTP pode ser calculada através de uma abordagem teórica ou de uma abordagem simulada. O método de cálculo utilizado depende do tipo de jogo;

"Ajuste de escala": O método utilizado para transformar o resultado não processado do gerador de números aleatórios na produção necessária/utilizável, por exemplo, a produção em bruto de um gerador de números aleatórios terá normalmente uma amplitude muito superior à necessária para o uso a que se destina (por exemplo: os geradores de números aleatórios de 32 bits têm mais de dois biliões de resultados possíveis, mas (por exemplo) podem ter de determinar apenas quais de entre 52 cartas tirar). Do ajuste de escala exige-se que divida a produção em bruto em números mais pequenos e utilizáveis. Estes números "ajustados à escala" podem depois ser aplicados, nomeadamente a números de cartas, números de registo, símbolos, específicos. A produção em bruto de um gerador de números aleatórios terá, por vezes, uma amplitude muito inferior ao necessário para o uso a que se destina (por exemplo, valores decimais entre 0 e 1). Nestes casos, é necessário o "ajuste de escala" para aumentar a produção em bruto para números maiores utilizáveis;

"Semente": O valor utilizado como base para a iteração seguinte da função que forma o algoritmo do gerador de números aleatórios (i.e., na maioria dos casos, o último valor). O termo 'semente' é frequentemente mal utilizado no caso dos geradores de números aleatórios algorítmicos, i.e., é vulgar ter-se a ideia errada de que uma semente é o valor inicial de um gerador de números aleatórios, e, uma vez iniciado, a semente deixa de ter qualquer uso, a menos que o gerador de números aleatórios seja reiniciado;

"Autoexclusão": Um processo pelo qual um jogador se autoexclui voluntariamente da prática de jogos e apostas online. Os jogadores têm direito a autoexcluir-se diretamente na presença na Internet da entidade exploradora ou no sítio na Internet do SRIJ. O período de autoexclusão tem a duração mínima de três meses e perdura até à data indicada pelo jogador ou, na falta dessa indicação, por tempo indeterminado. Sem prejuízo do período de duração mínima de três meses indicado, o jogador pode comunicar o termo da autoexclusão ou, tendo o mesmo sido fixado, a sua antecipação, os quais se tornam eficazes decorrido o prazo de um mês sobre aquela comunicação.

"Informação sensível": A informação de caráter sensível relacionada com empresas ou indivíduos;

"Realização de testes": Realização de testes aprofundados ao sistema técnico de jogo da entidade exploradora, análise dos dados nele compreendidos e avaliação dos resultados no que se refere aos requisitos estabelecidos pelo SRIJ, determinando se estes são ou não satisfeitos;

"Pausa de inatividade do utilizador": Um período de tempo definido num sistema técnico de jogo online que é utilizado para determinar quanto tempo o jogador não esteve ativo no sistema de jogo;

"Presença na Internet": O interface disponível na Internet através do qual o jogador se relaciona com a entidade exploradora no âmbito da atividade de jogos e apostas online;

2 - Infraestrutura de entrada e registo

As especificações técnicas que se seguem são conformes com as cláusulas seguintes do RJO:

###### Artigo 4.º, alínea k)

###### Artigo 26.º

###### Artigo 28.º

###### Artigo 32.º

Artigo 34.º, alíneas a), b), c) e d)

###### Artigo 37.º

###### Artigo 39.º

###### Artigo 40.º

###### Artigo 41.º

2.1 - Descrição

A infraestrutura de entrada e registo (adiante designada por IER) faz parte do sistema técnico de jogo. É a infraestrutura que as entidades exploradoras devem implementar e instalar em território nacional para permitir o controlo e inspeção da atividade de jogos pelo SRIJ.

Consequentemente, todo o acesso à plataforma de jogo e todo o tráfego entre o jogador e a plataforma de jogo relativo à atividade de jogo e apostas online tem de ser encaminhado através da IER, devendo as demais operações relacionadas com a atividade de jogo e apostas online que ocorram em qualquer dos componentes do sistema técnico de jogo ser sempre reportadas à IER.

Para fins de auditoria, a IER deve ter a capacidade de registar todos os dados relativos à atividade de jogo e apostas online e reportá-los à Infraestrutura de Controlo (adiante designada por IC).

A IER deve permitir, a todo o tempo, o acesso do SRIJ à demais informação existente na mesma.

A entidade exploradora tem igualmente de estabelecer e manter um canal de comunicação segura e exclusiva com a IC gerida pelo SRIJ. A comunicação destina-se a assegurar a transferência de dados, descarregamento (download) de dados, gestão de notificações e validação da informação relativa ao jogador.

A IER é composta pelos seguintes componentes:

. Gateway da entidade exploradora;

. Safe

Considera-se que a IER contém componentes críticos e, como tal, o nível de segurança deve ser igual ao da segurança da plataforma de jogo e do restante sistema técnico de jogo.

Nas páginas seguintes, descreve-se cada um dos componentes da IER e no diagrama infra o módulo básico da respetiva arquitetura.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2015/12/250000001/0000300035.pdf)

2.1.1 - Gateway da entidade exploradora

As especificações técnicas que se seguem são conformes com o Artigo 28.º e 34.º do RJO

A entidade exploradora está obrigada a instalar um Gateway dedicado, para o qual devem ser redirecionados todos os acessos dos jogadores (web, acesso móvel, outros) que se estabeleçam a partir de localizações situadas em território português (vindas de um endereço IP português) ou que façam uso de contas de jogadores registados em Portugal. Assim, o acesso à presença na Internet via Gateway só pode ser efetuado através do domínio de topo da Internet com a terminação ".pt" relativa a Portugal. A entidade exploradora deve assegurar, sempre que necessário, o acesso a dados do gateway em formato utilizável para eventual processo de auditoria.

2.1.2 - Safe

As especificações técnicas que se seguem são conformes com o Artigo 32.º, n.os 1 e 3, do RJO

A entidade exploradora deve instalar uma infraestrutura dedicada (Safe), localizada no território português, que garanta o armazenamento seguro dos dados de jogo e apostas, consoante as categorias definidas. A estrutura de pastas do Safe deve ser construída com base na estrutura e frequência especificadas de acordo com o modelo de dados definido pelo SRIJ.

A entidade exploradora deve proporcionar o acesso permanente do SRIJ ao Safe, para fins de consulta/recolha de dados, como parte integrante do controlo e inspeção da atividade de jogo.

A transferência de dados para o SRIJ é efetuada por recurso a protocolo FTPS e a transferência de dados entre o Captor e o Safe deve ser efetuada utilizando protocolo seguro definido pela entidade exploradora (FTPS, HTTPS ou outro equivalente).

A entidade exploradora deve armazenar os dados dos últimos 120 meses, dos quais os últimos 24 meses devem estar acessíveis de imediato no Safe e os restantes 96 meses podem estar armazenados num suporte de registo digital.

2.1.3 - Referencial de tempo do sistema

Todos os elementos da plataforma de jogo e a IER, serão sincronizados com uma fonte de referência de tempo única e fiável. Os registos do reporte de informação serão efetuados utilizando a hora legal de Portugal Continental, determinada nos termos da legislação nacional e divulgada pelo Observatório Astronómico de Lisboa através dos servidores de NTP.

2.1.4 - Encriptação e integridade dos dados

As especificações técnicas que se seguem são conformes com as alíneas f) e g) do n.º 3 do Artigo 32.º do RJO

Os dados que serão registados no Safe serão agrupados em categorias predefinidas. Cada categoria deve ser assinada, comprimida e encriptada pela entidade exploradora, utilizando o formato e os procedimentos descritos no Modelo de Dados do SRIJ.

O SRIJ fornecerá às entidades exploradoras uma Chave Pública Multicert para a encriptação dos ficheiros comprimidos do Safe e o respetivo roteiro. As chaves da Multicert são emitidas de acordo com os standards internacionais ITU X.509 version 3 e RFC 5280.

2.2 - Ambiente das entidades exploradoras

As especificações técnicas que se seguem são conformes com as alíneas a) e b) do Artigo 34.º

O ambiente das entidades exploradoras (plataforma de jogo e captor) pode localizar-se fora do território português.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2015/12/250000001/0000300035.pdf)

2.2.1 - Plataforma de jogo

As especificações técnicas que se seguem são conformes com as cláusulas seguintes do RJO:

Artigo 13.º, alínea d), subalíneas iii) e ix)

Artigo 26.º, n.º 1, alíneas d), e), f), g), i), j), k), n) e o)

###### Artigo 30.º

###### Artigo 32.º

###### Artigo 33.º

###### Artigo 38.º, n.º 1

###### Artigo 40.º

###### Artigo 41.º

A plataforma de jogo online é constituída pela infraestrutura de hardware e software que funciona como o principal interface entre os jogadores e as entidades exploradoras de jogo, oferecendo aos jogadores as ferramentas necessárias para abrir e fechar contas, registar e alterar os dados de identificação, depositar ou levantar fundos das respetivas contas de jogo e visualizar o detalhe das respetivas atividades ou os respetivos extratos e relatórios.

A plataforma de jogo inclui qualquer presença na Internet que mostre informações relevantes para os jogadores relativamente aos jogos propostos pela entidade exploradora, assim como qualquer software cliente (client software) que o jogador tenha de descarregar (download) para interagir com a plataforma. A plataforma de jogo permite à entidade exploradora gerir as contas de jogo dos jogadores, assim como as transações financeiras, fornecer informações sobre os resultados do jogo, tratar e divulgar (input) os resultados no âmbito de torneios, eventos hípicos e desportivos, ativar ou desativar registos e contas de jogador e estabelecer todos os parâmetros configuráveis.

Os componentes seguintes fazem parte da plataforma de jogo:

. O software de jogo, que é constituído por todos os módulos ou componentes de software que possibilitam a gestão de cada um dos jogos ou eventos, o desenvolvimento e implementação das regras de cada jogo, atividade ou evento acessível a partir da plataforma de jogo.

. As bases de dados que coligem os dados pessoais dos jogadores, as relacionadas com todas as transações efetuadas pelos jogadores e as informações sobre, nomeadamente os resultados das corridas de cavalo ou dos eventos desportivos e coeficientes.

. Os instrumentos/sistemas de pagamento (payment gateways), que possibilitam a execução das transações económicas entre os jogadores e a entidade exploradora de jogo, contendo a funcionalidade lógica necessária para garantir a transferência de fundos pelo método de pagamento utilizado pelo jogador para a entidade exploradora e da entidade exploradora para o jogador.

. O gerador de números aleatórios, que é o componente de software ou de hardware que, através de procedimentos que garantem a sua aleatoriedade, gera os resultados numéricos aleatórios que são utilizados pela entidade exploradora para determinar os resultados de cada jogo para o qual o mesmo é utilizado.

. Os controlos internos que são constituídos pelo sistema de controlos e procedimentos administrativos e contabilísticos utilizados pela entidade exploradora para desenvolver a atividade de exploração de jogo e apostas online.

Para além do anteriormente referido, é necessário implementar as seguintes funções:

. Captor/Serviços do captor;

. Serviços dos jogadores.

Nas páginas seguintes, descreve-se cada um destes componentes.

2.2.2 - Captor

As especificações técnicas que se seguem são conformes com os artigos 32.º, n.os 1, 2 e 3 do RJO

A entidade exploradora deve implementar um Captor, funcionalidade destinada a realizar a extração sistemática de dados da plataforma de jogo e a transmissão sistemática para o Safe, garantindo a recolha, validação, formatação e armazenamento seguros dos dados relacionados com o jogo e apostas e assegurando a respetiva integridade, disponibilidade e confidencialidade.

A formatação (XML), compressão e encriptação (ZIP) e o armazenamento dos dados devem ser implementados de acordo com o atual Modelo de Dados de Jogo Online do SRIJ.

Os serviços do Captor devem ser capazes de extrair informação a qualquer momento, e de a submeter ao dispositivo Captor. Para o caso de indisponibilidade do dispositivo Captor, deve estar instalada uma funcionalidade que assegure a transmissão subsequente e integral de registos.

2.2.3 - Serviços dos jogadores

As especificações técnicas que se seguem são conformes com as cláusulas seguintes do RJO:

Artigo 26.º, n.º 1, alíneas c), d) e i)

###### Artigo 28.º, n.º 1

###### Artigo 32.º, n.º 2, alínea e)

###### Artigo 37.º

###### Artigo 39.º

A funcionalidade dos serviços dos jogadores é considerada parte do sistema técnico de jogo. É aceite que esta funcionalidade pode ser implementada pela entidade exploradora no seu ambiente de jogo (plataforma de jogo).

A funcionalidade dos serviços dos jogadores, necessária para que a plataforma técnica de jogo funcione, consiste em:

. Redirecionamento do jogador para o domínio (.pt) da presença na Internet da entidade exploradora se:

. Todas as ligações a uma presença na Internet pertencente à entidade exploradora vierem de um endereço IP português ou

. For utilizada uma conta de jogador registada em Portugal.

. Verificação da identidade do jogador

. A plataforma de jogo deve efetuar verificações da identidade do jogador como parte do processo de registo de jogador,

. Autoexclusão do jogador

. Os jogadores podem autoexcluir-se de jogar diretamente na plataforma de jogo das entidades exploradoras segundo critérios definidos;

. Os jogadores podem revogar uma anterior autoexclusão de jogar na plataforma de jogo das entidades exploradoras segundo critérios definidos.

. Notificações de autoexclusão do jogador

. As entidades exploradoras devem comunicar ao SRIJ a identidade dos jogadores que se autoexcluam ou revoguem uma anterior autoexclusão no prazo máximo de 24 horas a contar da data de receção da comunicação em questão;

. As entidades exploradoras devem criar uma lista com a identificação dos jogadores autoexcluídos na sua plataforma de jogo;

. A notificação de qualquer alteração à lista central de autoexclusão de jogadores mantida pelo SRIJ (com a identificação dos jogadores autoexcluídos no sítio na Internet do SRIJ) será enviada a todas as entidades exploradoras em tempo real;

. É imposto às entidades exploradoras que atuem na sequência de tais notificações, descarregando (downloading) a lista de autoexclusão em vigor.

. Descarregamento (download) da lista de autoexclusão de jogadores

. A entidade exploradora deve descarregar (download) a lista de autoexclusão transmitida pelo SRIJ;

. A lista de autoexclusão deve ser utilizada para/na gestão do acesso de jogadores à plataforma de jogo da entidade exploradora;

. Deve ser igualmente realizada uma verificação de autoexclusão como parte do processo de registo de jogador.

2.3 - Desempenho e Segurança

Artigo 32.º, n.os 3, alínea g), 4 e 5

2.3.1 - Segurança

A IER é considerada um componente crítico tal como a plataforma de jogo, pelo que o respetivo grau de segurança deve ser, no mínimo, igual ao grau de segurança da plataforma de jogo.

O modelo de dados impõe que a informação integrada no mecanismo de segurança seja encriptada no final, não sendo porém, exigido que se encontre encriptada a todo o tempo. A cadeia de custódia da chave de encriptação deve ser incluída na conceção do mecanismo de segurança da IER.

A entidade exploradora deve incluir na conceção da IER, um plano de prevenção de perdas de informação, o tempo de recuperação de desastres e um plano de continuidade de negócio.

2.3.2 - Desempenho

O captor deve ser capaz de tratar e registar a informação contida no sistema técnico de jogo (transaction information).

Salvo em circunstâncias excecionais devidamente justificadas, o captor deve ser concebido de forma que a informação seja tratada, formatada e registada no Safe, no mínimo, à velocidade da plataforma de jogo.

O Safe terá uma capacidade ou um fluxo mínimo de comunicações na Internet, suficiente para que o SRIJ possa aceder ao mesmo e proceder ao descarregamento (download) e análise de dados.

O sistema do Safe deve ter um desempenho igual ou superior ao necessário para assegurar o fluxo de comunicação descrito supra, independentemente de outras operações a realizar.

2.3.3 - Indisponibilidade

A entidade exploradora deve descontinuar a prática dos jogos no caso de:

. Indisponibilidade do seu Gateway;

. Indisponibilidade do Captor de assegurar o reporte horário;

. Indisponibilidade do Safe por um período superior a 24 horas (se a indisponibilidade for inferior a 24 horas, a entidade exploradora pode manter a sua atividade de jogo, desde que o Captor esteja apto a assegurar o registo da informação até que esse limite de tempo seja alcançado ou que a IER seja reposta).

Consequentemente, é essencial que a IER seja concebida com uma elevada disponibilidade e que o tempo de inatividade acumulado do Captor e/ou do Safe não seja superior a 4 horas por mês.

2.3.4 - Prevenção da Perda de Dados

A IER é um componente crítico e, como tal, as entidades exploradoras devem implementar um procedimento que minimize o risco de perda de dados.

Em caso de perda de informação da IER, a entidade exploradora deve assegurar um novo procedimento de extração da informação perdida no prazo de uma semana.

Qualquer perda de informação que afete a IER deve ser reportada ao SRIJ, com efeitos imediatos, indicando a avaliação da perda de informação e o plano de ação a implementar para a sua recuperação.

A entidade exploradora tem de dispor de um procedimento documentado para controlar a qualidade dos dados da IER e possuir condições para retificar eventuais dados incorretos com uma nova recuperação de dados no prazo máximo de uma semana.

2.3.5 - Continuidade da Atividade de Negócio

Dado que a indisponibilidade da IER envolve a suspensão da prática de jogo, a entidade exploradora deve implementar um procedimento que assegure a continuidade de negócio e permita o retomar das operações em menos de um mês, em caso de um potencial desastre da IER.

Um eventual desastre que afete a IER deve ser comunicado imediatamente ao SRIJ, indicando a avaliação da perda e o plano de ação a implementar para a sua resolução.

2.3.6 - Conservação da Informação

O Safe deve manter os dados durante o período mínimo de 10 anos.

As entidades exploradoras de jogos têm a obrigação de assegurar e possibilitar ao SRIJ o acesso online à informação, pelo menos, dos últimos 24 meses de atividade, guardada no Safe.

As entidades exploradoras devem dispor de um processo de recuperação da informação a partir de um suporte digital localizado no Safe por um prazo de oito anos consecutivos.

3 - Infraestrutura de controlo

As especificações técnicas que se seguem são conformes com as cláusulas seguintes do RJO:

###### Artigo 4.º alínea j)

###### Artigo 7.º, n.º 1

Artigo 26.º, n.os 1, alíneas d), e), f), g), i), j), l), m), n), o), p) e q), e 2

###### Artigo 32.º

###### Artigo 36.º

###### Artigo 37.º

###### Artigo 39.º, n.º 3

Artigo 47.º n.os 5, 6 e 7

3.1 - Componentes da Infraestrutura de Controlo

O desenvolvimento e operação da IC são da responsabilidade do SRIJ.

A troca de dados deve ser efetuada de forma segura para garantir a confidencialidade, a integridade, a disponibilidade e a rastreabilidade entre todos os dispositivos e módulos que interagem com a IC.

3.2 - Ambiente do Regulador

O SRIJ detém as competências de controlo e inspeção da atividade de jogos e apostas online que executa através de auditorias no local, auditorias remotas e análise dos dados de jogo e apostas.

O SRIJ terá sistemas instalados para facilitar:

. O mecanismo de autoexclusão do jogador na sua presença na Internet,

. As notificações de autoexclusão do jogador para as entidades exploradoras;

. A lista dos jogadores autoexcluídos no sítio na Internet do SRIJ para descarregamento (download) pelas entidades exploradoras;

. A funcionalidade de verificação da identidade dos jogadores;

. O serviço de recolha de dados do Safe.

O SRIJ proporcionará a funcionalidade mediante a qual as entidades exploradoras serão notificadas eletronicamente das alterações eventualmente introduzidas na lista de autoexclusão de jogadores, mantida pelo SRIJ.

É imposto à entidade exploradora que implemente um sistema de comunicação e descarregamento (download) seguro da lista de autoexclusão de jogadores, na medida que esta sofre alterações em tempo real.

3.2.1 - Quadro da Interação com as Entidades Exploradoras

[(ver documento original)](https://files.diariodarepublica.pt/2s/2015/12/250000001/0000300035.pdf)

O diagrama supra sumariza as interações entre a entidade exploradora licenciada e o SRIJ:

. Genericamente, no âmbito da sua atividade de inspeção, o SRIJ procederá a auditorias periódicas ou auditorias ad-hoc na IER e na plataforma de jogo da entidade exploradora, as quais serão realizadas em colaboração com as entidades exploradoras, sendo-lhe, feitas recomendações técnicas ou organizativas para reparação das vulnerabilidades identificadas;

. Após a certificação, o software de jogo deve ser sujeito a homologação (type-approval) efetuada pelo SRIJ, com o objetivo de verificar o nível de segurança e a conformidade com as regras de cada jogo;

. Os elementos que constem do Safe devem poder ser acedidos remotamente e no local, mediante solicitação, com o objetivo de realização das várias operações de controlo necessárias;

. O SRIJ solicitará à entidade exploradora que forneça os dados de supervisão, com uma determinada periodicidade previamente estabelecida, ou mediante solicitação, em função das suas necessidades para efeitos de controlo e inspeção;

. Finalmente, as entidades exploradoras devem, ao criar uma conta de jogador, verificar se o requerente não consta do seu registo de jogadores autoexcluídos. Esta verificação será, ainda, realizada cada vez que o jogador tenta iniciar uma sessão.

3.2.2 - Infraestrutura de armazenamento de dados (Data Warehouse)

O SRIJ dispõe de uma infraestrutura de armazenamento de dados (Data Warehouse), que consulta o Safe de cada entidade exploradora, a intervalos de tempo específicos (localização de armazenamento predefinida) para detetar e recolher novos dados.

Quando houver dados disponíveis, os dados diários são transferidos do Safe para a IC, onde serão desencriptados (desencriptação garantida pela Chave Privada Multicert), descomprimidos e integrados em partições de bases de dados definidos.

3.2.3 - Necessidades de Reporte Adicional

Para além dos dados fornecidos sistematicamente, de acordo com o definido no modelo de dados, o SRIJ pode, periodicamente, solicitar relatórios ou dados mais detalhados ou produzidos, de acordo com critérios de busca mais precisos.

A entidade exploradora deve ter meios para extrair dados do seu sistema, de acordo com os critérios estabelecidos pelo SRIJe no prazo que para o efeito lhe seja fixado.

Estes relatórios complementarão a informação que pode ser obtida do Safe, bem como a informação transmitida sistemática e automaticamente para o sistema informático do SRIJ (IC).

A natureza e o formato específico dos dados serão indicados caso a caso pelo SRIJ, consoante os respetivos requisitos.

3.3 - Modelo de dados

Do modelo de dados consta a finalidade dos dados a registar, o prazo de atualização desses dados e os requisitos de disponibilidade e acesso pelo SRIJ.

Os dados são armazenados numa estrutura de ficheiros num formato estruturado em XML, tal como definido no esquema do modelo de dados (Definição de Esquema XSD-XML).

3.3.1 - Criação do Relatório Sistemático

Nos termos do RJO, as entidades exploradoras estão obrigadas ao envio sistemático de dados ao SRIJ. Estes dados são extraídos da plataforma de jogo e dos sistemas centralizados internos da entidade exploradora, sob a forma de um relatório de dados consolidado. Uma vez que o formato e o conteúdo dos relatórios solicitados está previamente definido, os mesmos podem posteriormente vir a ser alterados. A funcionalidade de criação de relatórios deve, pois, permitir a sua adequação às exigências do SRIJ.

O SRIJ impõe que as entidades exploradoras produzam e armazenem os dados sistematicamente. Estes dados são extraídos da plataforma de jogo e dos sistemas internos da entidade exploradora, montados em estruturas XML de acordo com categorias predefinidas e depositados numa determinada pasta do sistema de ficheiros do Safe, como um ficheiro diário único comprimido (ZIP) e encriptado.

3.3.2 - Tipos de Ficheiros

A entidade exploradora é responsável pela produção de ficheiros XML e ficheiros ZIP, os quais são armazenados no Safe, em localizações predefinidas.

Os ficheiros horários XML devem abranger a integralidade da atividade da presença na Internet e no sistema técnico de jogo da entidade exploradora durante o período de uma hora, o que significa que tem de ser produzido um ficheiro XML por hora e por categoria de dados, como definido.

Os ficheiros ZIP são produzidos diariamente para cada categoria. Os ficheiros XML relativos a cada categoria são agrupados, zipados e subsequentemente encriptados com uma Chave Pública Multicert.

3.3.3 - Frequência da Criação de Dados

Os ficheiros XML são produzidos de hora em hora.

Os ficheiros ZIP são produzidos diariamente.

3.3.4 - Tipos de Categoria

A entidade exploradora é responsável pela recolha e produção de ficheiros XML para as seguintes categorias:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2015/12/250000001/0000300035.pdf)

4 - Processo de Certificação

As especificações técnicas que se seguem são conformes com o artigo 35.º do RJO

4.1 - Princípios da Certificação

O RJO impõe que os sistemas técnicos de jogo das entidades exploradoras sejam certificados para a exploração e prática de jogos e apostas online.

O processo de certificação é estabelecido para assegurar a conformidade do sistema técnico de jogo com todos os seus requisitos e especificações, a execução dos jogos de forma correta e a segurança envolvente do sistema de jogo.

Os requisitos do programa de certificação foram concebidos para os diferentes tipos de jogos e apostas, com base numa avaliação do tipo de importância do jogo e do risco em relação, nomeadamente com a extensão, prevalência, natureza e dimensão do prémio e do risco de os jogadores serem induzidos em erro.

Um Organismo de Certificação Reconhecido (OCR) procederá às auditorias e aos testes ao sistema técnico de jogo da entidade exploradora. Os testes e auditorias têm de ser adaptados à oferta concreta de jogos e apostas de cada entidade exploradora.

Cabe à entidade exploradora a responsabilidade de recorrer ao OCR para a realização das necessárias auditorias, testes e obtenção de certificações. As entidades exploradoras devem gerir o processo de certificação, tendo de assegurar que são sempre efetuadas as auditorias e testes marcados.

A entidade exploradora deve assegurar que o jogo é disponibilizado através da plataforma de jogo certificada, inclusive nos casos em que ocorra o acesso de jogadores estrangeiros e estes se encontrem a jogar simultaneamente com jogadores nacionais.

4.2 - Requisitos da Certificação

No sentido de assegurar o cumprimento das normas técnicas apropriadas, o OCR tem de cumprir critérios mínimos. Cabe às entidades exploradoras escolher um organismo certificador, de entre os reconhecidos pelo SRIJ e que constam de lista disponibilizada para o efeito.

O OCR tem de assegurar e atestar que os requisitos do SRIJ referentes à realização de testes e auditorias se mostram satisfeitos, bem como relatar em que medida o sistema técnico de jogo da entidade exploradora preenche os requisitos constantes do RJO e as especificações constantes do presente documento no período de auditoria ou de testes.

A título absolutamente excecional, pode ser aceite que o organismo certificador ateste a certificação mesmo que não tenham sido satisfeitos todos os requisitos descritos no presente documento. Neste caso, as certificações têm de ser sustentadas por uma avaliação de risco, tendo em consideração os objetivos do RJO. A avaliação de risco será baseada na norma internacional "ISO/IEC 31010 Gestão de risco - Técnicas de avaliação de risco", devendo o relatório referir, expressamente, se este método foi utilizado.

4.2.1 - Compilação das certificações

Cabe ao ORC da entidade exploradora assegurar que todos os requisitos previstos no presente documento foram avaliados, sendo responsável por todo o processo de certificação. Caso um requisito seja irrelevante para determinada entidade exploradora devido à gama de jogos que propõe, este facto deve ser referido no relatório de certificação.

Os relatórios de testes e de auditoria que constituam a base da certificação têm de ser identificados no relatório. A data da certificação deve ser igualmente indicada no relatório.

4.3 - Aprovação de Tipos

4.3.1 - Jogos e apostas online

As normas de realização de testes e de auditoria dos sistemas técnicos de jogos e apostas online, bem como dos jogos propostos pelas entidades exploradoras são estabelecidas para assegurar que as funcionalidades do sistema e dos próprios jogos funcionam adequadamente e em respeito pelo RJO e demais regulamentos complementares. A apresentação das funcionalidades do jogo tem de satisfazer os requisitos especificados na Secção 5 para a conta de jogador, incluindo as funções relacionadas com as condições gerais, a gestão das contas de jogador, a prática de jogo responsável, a gestão de fundos de jogadores e relatórios aos mesmos associados.

A funcionalidade do sistema de jogo especificada na Secção 6, deve ser testada para assegurar que tem correspondência com o que está a ser apresentado ao jogador, o que inclui funções relacionadas com a apresentação visual e com a execução dos jogos, nomeadamente jogos e apostas par-a-par (peer-to-peer), funções de gestão de jogo, incluindo jogos incompletos e falhas na operação, bem como o registo cronológico (logging) das transações de jogo e de outras transações.

5 - Registo dos Jogadores e Contas de Jogo

As especificações técnicas que se seguem são conformes com as cláusulas seguintes do RJO:

###### Artigo 6.º, alínea d)

###### Artigo 9.º, n.º 3

Artigo 13., alínea d), subalíneas iv) e vi)

Artigo n.º 26.º, n.º 1, alíneas c), k), m) e n)

###### Artigo n.º 28

###### Artigo n.º 30

###### Artigo n.º 37

###### Artigo n.º 38

###### Artigo n.º 39

###### Artigo n.º 40

###### Artigo n.º 41

###### Artigo n.º 42

###### Artigo n.º 93 — 5.1 - Parte geral

5.1.1 - Termos e condições

1 - O sistema técnico de jogo deve exigir aos jogadores que aceitem expressamente os termos e condições da entidade exploradora aquando do registo do jogador, incluindo quando esse registo seja efetuado através de dispositivos de acesso restrito, tais como telemóveis ou tablets.

2 - O sistema técnico de jogo só pode permitir que o jogador jogue a dinheiro após este ter aceitado os termos e condições da entidade exploradora. O sistema técnico de jogo deve registar esta ação num log.

3 - Os termos e condições da entidade exploradora devem conter a menção de que o jogador está a celebrar um contrato com a entidade exploradora.

4 - Os termos e condições da entidade exploradora devem conter a menção de que apenas as licenças emitidas pela entidade de controlo, inspeção e regulação são válidas em Portugal.

5 - Dos termos e condições da entidade exploradora deve constar que o jogador expressamente aceita a política de privacidade estabelecida pela entidade exploradora, qual a informação mínima que lhe é solicitada, a finalidade a que a mesma se destina e as condições em que pode ser divulgada.

6 - Dos termos e condições da entidade exploradora deve constar que o jogador autoriza a entidade exploradora a confirmar os dados pessoais com vista a verificar a sua identidade.

7 - Dos termos e condições da entidade exploradora deve constar que é proibida a prática de jogos e apostas online a menores de 18 anos, devendo o sistema técnico de jogo conter mecanismos que impeçam os menores e outros grupos socialmente vulneráveis de se registarem como jogadores.

8 - Dos termos e condições da entidade exploradora deve constar que os jogadores só podem agir em seu nome e por sua conta, bem como quais as consequências da violação dessa obrigação.

9 - Dos termos e condições da entidade exploradora deve constar o procedimento através do qual podem ser apresentadas reclamações pelos jogadores, bem como o modo como as mesmas serão tratadas.

10 - Dos termos e condições da entidade exploradora deve constar que o sistema técnico de jogo cumpre e observa as leis em vigor relativas ao branqueamento de capitais e ao financiamento do terrorismo.

11 - Dos termos e condições da entidade exploradora deve constar que o jogador fica sujeito ao cumprimento dos princípios e regras decorrentes da legislação em matéria de proteção de dados pessoais, bem como ao controlo e fiscalização da Comissão Nacional de Proteção de Dados, no exercício das suas competências legais. Deve ainda constar dos termos e condições que as pessoas que, no exercício das suas funções, tenham conhecimento dos dados pessoais no âmbito do RJO, ficam obrigadas a sigilo profissional, mesmo após o termo das suas funções, nos termos do artigo 17.º da [Lei n.º 67/98](https://diariodarepublica.pt/dr/detalhe/lei/67-1998-239857), de 26 de outubro.

12 - Dos termos e condições da entidade exploradora deve constar a forma como, de acordo com o regulamento para o efeito aprovado pelo SRIJ, são tratados pela entidade exploradora os fundos existentes nas contas de jogadores que não estejam a ser utilizadas nos casos em que ocorra, nomeadamente, uma das situações abaixo indicadas:

. Contas de jogador desativadas;

. Contas de jogador canceladas;

. Contas de jogador suspensas.

13 - Dos termos e condições da entidade exploradora deve constar o modo como os jogadores se podem autoexcluir, bem como a forma como pode fixar limites máximos de depósito e de aposta.

14 - Dos termos e condições da entidade exploradora deve constar que é proibido recorrer a empréstimos para jogar e ainda que as entidades exploradoras de jogos e apostas online, assim como os respetivos órgãos sociais, os seus trabalhadores e os demais colaboradores, estão proibidos de conceder empréstimos aos jogadores ou disponibilizar, direta ou indiretamente, dispositivos que permitam aos jogadores concederem empréstimos entre si.

15 - Dos termos e condições da entidade exploradora deve constar a forma como são tratadas as infrações às regras da entidade exploradora.

16 - Quando não for possível aquando do registo apresentar os termos e condições de forma integral ao jogador, nomeadamente por se tratar de uma versão para dispositivos móveis, deve aquele ser advertido da forma como poderá aceder à versão integral dos termos e condições da entidade exploradora. Os termos e condições podem, por exemplo, ser disponibilizados na presença na Internet da entidade exploradora e/ou remetidos por correio e/ou e-mail.

5.1.2 - Presença na Internet da Entidade Exploradora

1 - A entidade exploradora deve prever os procedimentos e dispositivos necessários para instalar uma presença na Internet com o nome do respetivo domínio subordinado à identificação ".pt", para a exploração dos jogos e apostas online, para o qual devem ser redirecionados todos os acessos que se estabeleçam a partir de localizações situadas em território português ou que façam uso de contas de jogadores registados em Portugal.

2 - A entidade exploradora não pode incluir na sua presença na Internet quaisquer outros conteúdos para além dos relativos aos jogos e apostas online autorizados pelas respetivas licenças.

3 - A presença na Internet deve dispor de mecanismos que permitam aos jogadores autoexcluírem-se da prática de jogos e apostas online.

4 - A presença na Internet da entidade exploradora deve prestar aos jogadores informações completas sobre os seus direitos e deveres. Os jogadores têm direito, nomeadamente, a:

. Receber os prémios que lhes sejam devidos;

. Jogar livremente e sem qualquer tipo de coação;

. Dispor, em qualquer momento, de informação sobre as quantias jogadas ou apostadas e sobre o saldo da respetiva conta de jogador;

. Identificar-se, de um modo seguro, junto da entidade exploradora;

. Ver garantida a sua privacidade e a proteção de dados disponibilizados à entidade exploradora para efeitos do seu registo de jogador;

. Conhecer, a todo o momento, a identificação e os contactos da entidade exploradora e, caso pretendam apresentar reclamação, o modo como devem proceder;

. Ter disponível, na sua presença na Internet, informação sobre a prática de jogo responsável;

. Dispor de informação clara, verdadeira, completa e atualizada sobre as regras dos jogos e apostas online, os instrumentos de pagamento admitidos, os valores mínimos e máximos de aposta e as regras de cálculo e de pagamento dos prémios;

. Dispor de informação sobre o modo de aceder aos seus dados pessoais;

. Dispor de informação sobre as proibições de jogar, nomeadamente no que se refere aos menores, aos declarados incapazes ou àqueles que, voluntária ou judicialmente, estejam impedidos de jogar;

. Dispor de alertas contra as práticas excessivas de jogos e apostas online e sobre o direito de autoexclusão dos jogadores;

. Dispor dos contactos das entidades que prestam apoio a jogadores com problemas de dependência e adição;

. Conter o logótipo e os contactos da entidade exploradora e da entidade de controlo, inspeção e regulamentação;

. Dispor de referência relativa à licença da entidade exploradora para a exploração de jogos e apostas online;

. Dispor da informação necessária para que possam proceder a uma escolha consciente das suas atividades como jogadores, promovendo um comportamento de jogo moderado, não compulsivo e responsável.

5 - Os jogadores estão obrigados, nomeadamente, a:

. Identificar-se perante a entidade exploradora, de acordo com as regras estabelecidas no RJO;

. Indicar, no ato de registo na presença na Internet, uma conta de pagamento de que sejam titulares e na qual devem ser creditados todos os montantes transferidos a partir da conta de jogador;

. Fornecer à entidade exploradora cópia de documento comprovativo da titularidade da conta de pagamento acima referida, para efeitos de recebimento dos saldos da conta de jogador;

. Não perturbar o normal funcionamento dos jogos e apostas online;

. Cumprir a lei, bem como os regulamentos, instruções e orientações da entidade de controlo, inspeção e regulação.

6 - A presença na Internet da entidade exploradora deve informar quais os instrumentos de pagamento que são admitidos nas operações dos jogos e apostas online.

. Só são permitidos instrumentos de pagamento eletrónicos que utilizem moeda com curso legal em Portugal;

. Para o provisionamento da conta de jogador, as entidades exploradoras só podem admitir instrumentos de pagamento fornecidos por prestadores de serviços de pagamentos devidamente autorizado pelas autoridades competentes dos respetivos países ou jurisdições e que permitam a correta a identificação do ordenante da operação de pagamento.

5.1.3 - Licença e Supervisão

1 - A homepage da presença na Internet da entidade exploradora deve fazer referência à licença para exploração de jogos e apostas online com a identificação das categorias e tipos de jogos e apostas que pode explorar. Deve ainda fazer referência de que a entidade exploradora está sujeita ao controlo, regulação e inspeção do SRIJ.

2 - A homepage da presença na Internet da entidade exploradora deve apresentar, em local visível, o logótipo da entidade de controlo, inspeção e regulação e permitir a ligação ao sítio na Internet do SRIJ.

5.1.4 - Reclamações

1 - As reclamações dos jogadores devem ficar registadas num log, que conterá, entre outras, as seguintes informações:

. Os fundamentos da reclamação;

. A identificação do jogador;

. A hora e data da ocorrência;

. O tempo de resolução das reclamações e

. O resultado da apreciação da reclamação (aceite/parcialmente aceite/rejeitada).

5.2 - Registo e conta de jogador

5.2.1 - Registo do jogador e verificação do processo

1 - No processo de registo do jogador o sistema técnico de jogo deve recolher e guardar a seguinte informação sobre o jogador:

. Nome completo (conforme cartão de cidadão/bilhete de identidade ou outro documento admitido, nos termos do RJO);

. Data de nascimento;

. Nacionalidade;

. Profissão;

. Morada de residência;

. País de residência;

. Número de identificação civil, do passaporte ou de outro documento admitido, nos termos do RJO;

. Número de identificação fiscal;

. Endereço de correio eletrónico;

. Elementos identificadores da conta de pagamento.

A entidade exploradora deve verificar a identidade dos jogadores por um dos seguintes meios:

a) Mediante consulta às bases de dados de entidade pública, efetuada, em tempo real, através de ligação à entidade de controlo, inspeção e regulação;

b) Diretamente na respetiva presença na Internet, através do cartão do cidadão ou da chave móvel digital.

O sistema técnico de jogo deve ter implementados, nos módulos de criação dos registos de jogadores, os mecanismos necessários para dar cumprimento à obrigação de verificação da identidade dos jogadores.

Se o jogador não dispuser de cartão do cidadão ou de chave móvel digital, o sistema técnico de jogo deve aceitar um número de identificação a partir de um documento emitido pelo país de origem do jogador e que constituirá a identificação daquele (por exemplo, carta de condução, passaporte ou equivalente, com fotografia e data de nascimento).

O registo de jogador só se torna efetivo depois de verificada a respetiva identidade e confirmada a inexistência de proibição de jogar, momento a partir do qual o jogador pode dar início à prática de jogos de apostas online.

2 - A cada jogador só é permitido um registo ativo por presença na Internet, sendo, após o mesmo se tornar efetivo, validados pela entidade exploradora um nome de utilizador único e uma senha exclusiva para o acesso.

3 - O sistema técnico de jogo deve assegurar que o jogador tem 18 ou mais anos.

4 - O sistema técnico de jogo deve registar a hora em que os dados relativos à identificação do jogador foram recebidos. Esta informação só deverá estar acessível a utilizadores autorizados.

5 - O sistema técnico de jogo deve confirmar, em cada login, que o jogador não está registado na base de dados da entidade exploradora como autoexcluído.

6 - O sistema técnico de jogo deve guardar a informação recolhida em cada login relativa à autoexclusão do jogador, guardando em registo a confirmação do estado do jogador, obtida a partir da base de dados de jogadores autoexcluídos da entidade exploradora.

7 - O sistema técnico de jogo deve permitir uma conexão encriptada (tipo da SSL) para a transferência de dados do jogador.

5.2.2 - Acesso à conta de jogador

1 - O sistema técnico de jogo deve criar uma conta de jogador associada ao registo de cada jogador, com uma identificação única, onde se processam e registam todas as transações realizadas. A cada jogador só é permitido ter uma conta de jogador em cada presença na Internet.

O sistema técnico de jogo deve conter controlos técnicos que permitam a deteção de tentativas para a existência de múltiplas contas.

O sistema técnico de jogo deve conter mecanismos que impeçam a criação de contas anónimas ou em nome de terceiros.

2 - O sistema técnico de jogo deve garantir que as operações realizadas na conta de jogador identificam, de forma inequívoca, a origem das transações e deve dispor de mecanismos que permitam a transferência do saldo da conta do jogador para a conta de pagamento indicada e titulada pelo mesmo.

O jogador deve ser o titular da conta de pagamento acima referida.

3 - O sistema técnico de jogo deve garantir que a conta de jogador não pode, em nenhuma circunstância, apresentar saldo negativo.

4 - O sistema técnico de jogo deve garantir que não são permitidas transferências de dinheiro entre contas de jogadores.

5 - A conta de jogador só pode ser movimentada por iniciativa deste.

6 - Os procedimentos de desativação, de suspensão e cancelamento das contas de jogador são definidos em regulamento pela entidade de controlo, inspeção e regulação.

7 - O sistema técnico de jogo deve assegurar a existência de processos, procedimentos e medidas tecnológicas que garantam o não repúdio dos atos praticados.

8 - O sistema técnico de jogo deve assegurar que as contas dos jogadores não são utilizadas para outros fins que não os jogos e apostas online.

9 - O sistema técnico de jogo deve, no mínimo, permitir que o jogador aceda a informação sobre o saldo da conta de jogador, a atividade de jogo (incluindo apostas, prémios e perdas), depósitos, levantamentos e outras transações relacionadas com a conta de jogador.

A informação deve estar disponível online na conta de jogador durante, pelo menos, 90 dias.

10 - A entidade exploradora deve ser capaz de, a pedido do jogador, fornecer os extratos de conta que apresentem todas as transações na conta de jogador nos últimos 12 meses.

O processo de gerar e disponibilizar esta informação pode ser um processo manual.

5.2.3 - Alterações aos dados do jogador

1 - O sistema técnico de jogo deve limitar o modo pelo qual o jogador que não tem cartão de cidadão ou chave móvel digital pode gerar uma nova senha de acesso ou alterar a senha de acesso à conta de jogador, aos seguintes meios:

. Através de pessoal autorizado;

. Através de canais de comunicação conhecidos, como o endereço de correio eletrónico do jogador, um número de telefone ou outro semelhante.

2 - O sistema técnico de jogo deve registar e guardar informação sobre as alterações às senhas, como descrito no ponto anterior.

3 - O sistema técnico de jogo deve guardar as alterações aos dados do jogador num log auditável.

4 - O sistema técnico de jogo deve permitir guardar documentos que comprovem que as alterações aos dados de identificação dos jogadores são válidas.

5 - O sistema técnico de jogo deve fornecer uma conexão encriptada (tipo da SSL) para alterações dos dados de identificação do jogador.

5.2.4 - Criação e desativação de contas de jogador

1 - O sistema técnico de jogo deve permitir apenas ao pessoal autorizado a criação e desativação de contas de jogador.

Pessoal autorizado é aquele que, de acordo com o conteúdo funcional do seu trabalho, está autorizado a criar e a desativar contas de jogador

2 - O sistema técnico de jogo deve registar num log cada vez que a conta de jogador é desativada e incluir informação sobre o saldo da conta, a razão para a desativação, assim como a identificação do funcionário que desativou a conta.

3 - O sistema técnico de jogo deve ser capaz de gerar relatórios que listem as contas de jogador, agrupadas por estado "ativas" ou "desativadas" e respetivos saldos, com a identificação das razões para a desativação, se for o caso, e o funcionário responsável.

5.3 - Comportamento responsável

5.3.1 - Suspensão

1 - O sistema técnico de jogo deve providenciar os meios através dos quais o pessoal da entidade exploradora, com autorização para o efeito, pode suspender o acesso do jogador ao jogo.

2 - O sistema técnico de jogo deve manter uma lista de jogadores suspensos, indicando a razão para a respetiva suspensão.

3 - Imediatamente após uma suspensão o sistema técnico de jogo não pode aceitar novas apostas ou depósitos do jogador em questão.

4 - A suspensão deve obstar a que o jogador transfira fundos para a respetiva conta de jogador.

5.3.2 - Autolimitações do jogador

1 - O sistema técnico de jogo deve disponibilizar aos jogadores opções que facilmente lhes permitam impor limites à sua atividade de jogo.

2 - O sistema técnico de jogo deve conter mecanismos que facilmente permitam aos jogadores impor limites nos montantes depositados nas respetivas contas de jogador. O jogador deve, pelo menos, ser capaz de definir os seguintes limites de depósitos:

a) Valor limiar para o total diário de depósitos na conta de jogador;

b) Valor limiar para o total semanal de depósitos na conta de jogador, e

c) Valor limiar para o total mensal de depósitos na conta de jogador.

3 - O sistema técnico de jogo deve conter mecanismos que facilmente permitam aos jogadores impor limites nas apostas efetuadas O jogador deve, pelo menos, ser capaz de definir os seguintes limites de aposta:

a) Valor máximo para o total diário de apostas a partir da conta de jogador;

b) Valor máximo para o total semanal de apostas a partir da conta de jogador;

c) Valor máximo para o total mensal de apostas a partir da conta de jogador.

4 - Assim que um pedido de redução do limite de depósito ou do limite de apostas é recebido de um jogador, o novo limite deve ser implementado imediatamente para todas as futuras interações de jogo.

Esta redução dos limites deverá ser implementada, pelo menos, no momento em que o jogador faça login, quando este se encontre "logged out" da presença na Internet.

5 - O sistema técnico de jogo deve assegurar um desfasamento de, pelo menos, 24 horas a partir do momento em que o jogador solicita um limite menos restritivo nos montantes de depósito ou das apostas até à respetiva implementação pela entidade exploradora.

6 - O sistema técnico de jogo deve disponibilizar mecanismos que permitam ao jogador autoexcluir-se da prática de jogos e apostas online. O jogador deve, no mínimo, ter a opção de escolher entre:

a) Breves pausas de jogo (prazos de reflexão);

b) Autoexclusão por um período mínimo de três meses;

c) Autoexclusão por período indeterminado.

A entidade exploradora pode prever opções de prazos de reflexão.

7 - Imediatamente após a autoexclusão do jogador, o sistema técnico de jogo não deve permitir novas apostas ou depósitos pelo jogador Simultaneamente o jogador deve ser informado sobre a possibilidade de receber aconselhamento e tratamento em entidades que prestem apoio a jogadores com problemas de dependência e adição.

8 - Um jogador autoexcluído por um período determinado não está impedido de efetuar levantamentos de fundos da sua conta de jogador.

9 - Se o jogador se autoexclui por tempo indeterminado (i.e., não indicando o termo da autoexclusão) a respetiva conta de jogador deve ser cancelada.

10 - Imediatamente após a autoexclusão do jogador por tempo indeterminado, o sistema técnico de jogo deve informar o jogador que o saldo disponível na conta de jogador será transferido para a conta de pagamento titulada pelo jogador.

11 - Os jogadores têm direito a aceder a informação acerca da sua eventual autoexclusão.

5.3.3 - Informação para proteção do jogador

1 - O sistema técnico de jogo deve permitir ao jogador o acesso a "Informação para Proteção do Jogador".

2 - A "Informação para Proteção do Jogador" deve indicar que é proibida a prática de jogos e apostas online a menores de idade (com menos de 18 anos) e fornecer informações sobre o jogo responsável e os perigos da dependência e da adição ao jogo. Nessa informação podem existir links para a realização de testes de autoavaliação, reconhecidos pela indústria, e simples de preencher.

3 - A "Informação para Proteção do Jogador" deve disponibilizar os contactos de entidades que prestem apoio a jogadores com problemas de dependência e adição.

4 - A "Informação para Proteção do Jogador" deve remeter para links que contenham software ou outros programas que permitam aos jogadores configurar seus computadores para impedir o acesso a presenças na Internet de jogo online.

5 - A "Informação para Proteção do Jogador" deve conter a informação ou disponibilizar links para páginas que contenham informação acerca dos procedimentos a seguir para que o jogador possa impor limites à sua atividade de jogo.

6 - A "Informação sobre Proteção do Jogador" deve conter informação ou disponibilizar links para páginas que contenham informação acerca dos termos e condições aplicáveis aos jogadores.

7 - A "Informação para Proteção do Jogador" deve conter informação ou disponibilizar links para páginas que contenham informação sobre o tipo de transações autorizadas, as transações que ocorrem na conta de jogador ou para extratos de conta.

8 - A "Informação para Proteção do Jogador" deve conter informação ou disponibilizar links para páginas que contenham informação sobre a importância do jogador manter a confidencialidade dos dados de acesso ao seu login e à conta de jogador.

9 - A "Informação para Proteção do Jogador" deve conter informação ou disponibilizar links para páginas que contenham informação sobre a forma como os jogadores podem detetar acessos não autorizados às suas contas de jogador.

10 - No momento do login do jogador o sistema técnico de jogo deve mostrar a hora e data da última sessão do jogador.

11 - A "Informação para Proteção do Jogador" deve estar visível e em posição de destaque na presença na Internet da entidade exploradora e deve ser acessível a partir de todas as páginas.

5.4 - Conta de jogador

5.4.1 - Depósitos

1 - O sistema técnico de jogo deve informar, clara e especificamente, o jogador de todas as restrições relativas a depósitos e ao acesso aos montantes com eles relacionados.

Se existir um desfasamento entre a data do depósito e a data da disponibilidade do montante depositado, que provoque um atraso na possibilidade de aceder a esses montantes, deve o jogador ser informado clara e especificamente antes do depósito ser feito.

2 - Quando o jogador faz um depósito, o sistema técnico de jogo deve, de forma inequívoca, fornecer informação sobre todas as taxas e encargos a que o mesmo poderá ser sujeito.

Se forem cobradas taxas por depósitos efetuados ou relativa a levantamentos ou libertação de montantes depositados o jogador deverá ser informado clara e especificamente da existência das referidas taxa antes de realizar qualquer depósito na conta do jogador.

3 - O sistema técnico de jogo só pode aceitar depósitos numa conta de jogador através de instrumentos de pagamento fornecidos por prestadores de serviços de pagamento devidamente autorizados pelas autoridades competentes dos respetivos países ou jurisdições, devendo ser identificada, de forma inequívoca, a origem daqueles depósitos.

O sistema técnico de jogo só deve permitir o uso de instrumentos de pagamento eletrónicos que utilizem moeda com curso legal em Portugal.

4 - O sistema técnico de jogo deve creditar a conta do jogador imediatamente após o recebimento do depósito do jogador.

5 - O sistema técnico de jogo deve conter um log auditável que apresenta todos os montantes depositados. Esse log deve, no mínimo, incluir:

. Data e hora do depósito;

. Instrumento de pagamento utilizado;

. Identificação do jogador;

. Montante do depósito;

. Tipo de transação (i.e., transferência bancária, pagamento de serviços).

6 - O sistema técnico de jogo deve permitir gerar relatórios que mostram com precisão todos os fundos depositados.

7 - O sistema técnico de jogo deve permitir gerar relatórios que mostram com precisão todos os fundos depositados na conta de jogador discriminados por instrumento de pagamento.

8 - O sistema técnico de jogo deve permitir gerar relatórios que mostram com precisão todas as tentativas rejeitadas de depósitos de fundos.

5.4.2 - Levantamentos

1 - O sistema técnico de jogo só deve permitir o levantamento dos saldos das contas de jogadores após a verificação da identificação do jogador.

2 - O sistema técnico de jogo não pode permitir levantamentos das contas de jogadores que resultem num saldo negativo da conta de jogador.

3 - O sistema técnico de jogo deve permitir aos jogadores levantar os saldos disponíveis existentes na sua conta de jogador.

O disposto nos números anteriores não impede a entidade exploradora de realizar controlos sobre, nomeadamente, a frequência dos levantamentos e a verificação da identidade.

4 - O sistema técnico de jogo deve conter mecanismos que permitam a transferência do saldo da conta de jogador unicamente para a conta de pagamento indicada e titulada pelo mesmo, que tiver sido utilizada para creditar aquela. Se o instrumento de pagamento utilizado pelo jogador não permitir a devolução do saldo da conta de jogador para uma conta de pagamento, deve o mesmo ser transferido para uma conta bancária indicada pelo jogador e da qual este seja titular.

5 - O sistema técnico de jogo deve informar, clara e especificamente, o jogador de todas as restrições relativas a levantamentos da conta de jogador.

Se existir um desfasamento entre a data do levantamento e a data da disponibilidade do montante correspondente que provoca um atraso na possibilidade do jogador aceder ao saldo da sua conta de jogador, deve este ser informado clara e especificamente antes do levantamento ser feito.

6 - Quando o jogador faz um levantamento, o sistema técnico de jogo deve, de forma inequívoca, fornecer informação sobre todas as taxas e encargos a que o mesmo poderá ser sujeito.

Se forem cobradas taxas por levantamentos ou libertação de saldos, o jogador deverá ser informado clara e especificamente da existência das referidas taxa antes de realizar qualquer levantamento na conta do jogador.

7 - O sistema técnico de jogo deve conter um log auditável que apresenta todos os montantes levantados. Esse log deve, no mínimo, incluir:

. Data e hora do levantamento;

. Identificação do jogador;

. Montante do levantamento;

. Tipo de transação (i.e., transferência bancária).

8 - O sistema técnico de jogo deve permitir gerar relatórios que mostram com precisão todos os montantes levantados das contas de jogador.

9 - O sistema técnico de jogo deve permitir gerar relatórios que mostram com precisão todas as tentativas rejeitadas de levantamentos de saldos.

5.4.3 - Outras transações do jogador

1 - O sistema técnico de jogo deve garantir que as transações feitas na conta de jogador identificam inequivocamente as origens das transações.

2 - O sistema técnico de jogo deve dispor de mecanismos que previnam a criação de contas anónimas ou em nome de terceiros.

3 - O sistema técnico de jogo deve garantir que não são permitidas transferências de fundos entre contas de jogadores.

4 - O sistema técnico de jogo deve debitar a conta do jogador imediatamente após uma aposta ter sido efetuada.

5 - O sistema técnico de jogo não pode permitir a realização de uma aposta que resulta no saldo negativo da conta de jogador.

6 - O sistema técnico de jogo deve creditar imediatamente na conta de jogador todos os prémios.

7 - O sistema técnico de jogo deve manter um registo com todas as transações efetuadas na conta de jogador relativamente a cada jogo.

8 - O sistema técnico de jogo deve permitir gerar relatórios com os registos referidos no número anterior.

5.4.4 - Bónus

1 - O sistema técnico de jogo deve informar, clara e especificamente, o jogador dos bónus creditados nas contas do jogador.

2 - O sistema técnico de jogo deve informar, clara e especificamente, o jogador dos termos, condições e restrições associados à atribuição e utilização de bónus creditados nas contas do jogador.

3 - O sistema técnico de jogo deve conter um log auditável que apresenta todos os bónus creditados nas contas do jogador.

4 - O sistema técnico de jogo deve assegurar que os bónus creditados nas contas de jogador são utilizados apenas para jogar e que não são convertíveis em dinheiro, ou seja, que não podem ser levantados.

5.5 - Relatórios

5.5.1 - Regras gerais

1 - Os relatórios previstos no presente capítulo devem permitir a reconciliação de todas as transações financeiras, bem como das responsabilidades de cada jogador.

2 - O sistema técnico de jogo deve permitir analisar transações suspeitas e usar a informação como base para gerar relatórios para efeitos de prevenção de branqueamento de capitais e financiamento de terrorismo.

3 - O sistema técnico de jogo deve permitir analisar desvios nas apostas de um jogador face aos padrões de jogo e usar a informação como base para gerar relatórios.

4 - O sistema técnico de jogo deve permitir a análise de contas de jogador inativas e utilizar essa informação como base para gerar relatórios.

5 - O sistema técnico de jogo deve permitir gerar relatórios que identifiquem contas de jogador que foram canceladas com saldo positivo.

6 - O sistema técnico de jogo deve permitir gerar relatórios sobre todos os registos de jogador (completos ou incompletos).

7 - O sistema técnico de jogo deve permitir gerar relatórios sobre todos os jogadores registados, com informações sobre as respetivas contas (incluindo contas de jogador inativas e desativadas) e as datas dos respetivos registos.

8 - O sistema técnico de jogo deve permitir gerar relatórios sobre todos os jogadores suspensos e/ou autoexcluídos.

9 - O sistema técnico de jogo deve permitir gerar relatórios com a identificação de todos os jogadores que fixaram limites de jogo, bem como os respetivos limites.

10 - O sistema técnico de jogo deve permitir gerar relatórios, que abarquem um período de um ano, sobre todos os cancelamentos e desativações de contas de jogador, incluindo os fundamentos que estiveram subjacentes.

11 - O sistema técnico de jogo deve permitir gerar relatórios sobre cada conta de jogador, se assim o for solicitado, prestando informação, nomeadamente, sobre:

. Depósitos;

. Apostas;

. Prémios;

. Levantamentos;

. Contas de jogador inativas por mais de 90 dias.

6 - Estrutura e funcionalidade dos jogos

As especificações técnicas que se seguem são conformes com as cláusulas seguintes do RJO:

###### Artigo 5.º

###### Artigo 7.º

###### Artigo 19.º, alínea b) — Artigo 26.º, n.º 1, alíneas i) e q), e n.º 2

###### Artigo 30.º — Artigo 32.º, n.º 3, alínea e) e Artigo 33.º

Artigo 36.º, n.º 8 e n.º 9

###### Artigo 37.º

###### Artigo 38.º, n.º 1, alíneas d) e g)

6.1 - Funcionalidades do Jogo

6.1.1 - Participação

1 - O sistema técnico de jogo só pode disponibilizar aos jogadores as categorias e tipos de jogos e apostas online que a entidade exploradora está autorizada a explorar, de acordo com o RJO, e nos termos que constam da licença que lhe foi emitida.

2 - O sistema técnico de jogo só deve permitir a prática de jogos e apostas online através da conta de jogador quando o processo de verificação da identidade do jogador tiver sido corretamente concluído.

O RJO prevê que constitui obrigação da entidade exploradora verificar a identidade dos jogadores.

De acordo com o RJO, as entidades exploradoras são também obrigadas a que o sistema técnico de jogo contenha mecanismos que garantam que a informação relativa à autenticação e identificação dos jogadores é segura.

O RJO prevê o acervo de obrigações a que a entidade exploradora está obrigada no âmbito do processo de registo de jogadores e ainda os meios de que dispõe para a verificação da identidade dos jogadores.

O RJO prevê ainda que os jogadores têm direito a identificar-se junto da entidade exploradora, de forma segura, bem como a ver garantida a sua privacidade e a proteção dos dados disponibilizados à entidade exploradora para efeitos do seu registo como jogador.

3 - O sistema técnico de jogo deve assegurar que a participação dos jogadores em todos os jogos exige o consentimento destes. Não é permitido obrigar um jogador a jogar só pelo facto de este selecionar um determinado jogo (i.e., os jogadores não podem ser forçados a jogar).

4 - O sistema técnico de jogo deve assegurar que todas as ações dos jogadores são tomadas de forma consciente. O ato de clicar em imagens de ação, tais como "jogar", "ficar", "pedir cartas" e "dobrar", só podem ser aceites quando o jogador tiver tido tempo suficiente para ponderar as consequências da sua ação (i.e., cliques repetidos numa imagem de ação não devem ser aceites, nem executados).

O RJO prevê, entre outras, a obrigação da entidade exploradora disponibilizar ao jogador, na sua presença na Internet, toda a informação acerca dos seus direitos e deveres, de forma clara, verdadeira, completa e atualizada, incluindo as relativas às regras dos jogos e apostas online, aos instrumentos de pagamento admitidos, aos valores mínimos e máximos de aposta e às regras de cálculo e de pagamento dos prémios.

O jogador tem também direito a ter informação necessária para que proceda a uma escolha consciente das suas atividades como jogador, promovendo comportamentos de jogo moderado, não compulsivo e responsável, poder jogar livremente e sem qualquer tipo de coação, e ainda dispor, em qualquer momento, de informação sobre as quantias jogadas ou apostadas e sobre o saldo da respetiva conta de jogador.

A entidade exploradora deve também garantir a integridade, a disponibilidade, a confidencialidade e todos os demais atributos de segurança dos jogos e apostas online, assegurando a honestidade do jogo.

6.1.2 - Jogo justo e imparcial

1 - Os jogos devem ser apresentados de forma a transmitir aos jogadores informações corretas acerca das possibilidades de ganho, apresentando, de forma precisa, todas as hipóteses de resultado de cada jogo.

2 - Os jogos devem ser apresentados de forma a permitir que os jogadores tenham uma perceção clara sobre se podem influenciar o resultado.

3 - O sistema técnico de jogo deve garantir que todos os jogos apresentados e que têm na sua base um resultado aleatório têm efetivamente a probabilidade de produzir um qualquer resultado de cada vez que são jogados. A menos que a alteração dessa probabilidade tenha sido comunicada aos jogadores como parte das regras do jogo.

O retorno para o jogador não deve poder ser manipulado pelo Sistema técnico de jogo ou por interferência manual para garantir um retorno constante para o jogador.

4 - Os jogos devem funcionar independentemente das características dos equipamentos do jogador e/ou do canal de comunicação.

Os jogos não devem poder adaptar-se ao comportamento do jogador.

5 - Os jogos que envolvam a simulação de objetos físicos (tais como dados e roletas) deverão evidenciar um resultado verdadeiro e justo, de acordo com o comportamento do equivalente objeto físico, i.e., deverão reproduzir as características e utensílios utilizados numa mesa física e emular as operações e seu funcionamento.

Conceitos como "near-miss", que pode ser definido como toda a ação do sistema técnico de jogo que possa dar a perceção ao jogador que ele esteve perto de alcançar um ganho, não são considerados como justos e corretos.

Jogos que dão ao jogador a perceção de que tem o controlo sobre o resultado do jogo quando não o tem (i.e., quando o resultado é completamente aleatório), não são permitidos. A menos que o jogador tenha sido devidamente informado de que, no caso especifico, a sua escolha não tenha influência no resultado do jogo.

O retorno do jogo para o jogador não pode ser manipulado pelo sistema ou ser objeto de interferência manual de forma a manter-se um constante retorno para o jogador. Exceto no caso de jogos metamórficos e se o jogador ter sido devidamente informado.

Os jogos não podem adaptar-se ao comportamento do jogador. Exceto no caso de jogos metamórficos e se o jogador ter sido devidamente informado.

6.1.3 - Jogos de demonstração

Os jogos de demonstração são jogos sem recurso a dinheiro (jogos grátis e jogos para divertimento), que devem ser disponibilizados com as mesmas características dos jogos a dinheiro, devendo apresentar, de igual forma, de modo correto e equilibrado, a hipótese de ganhar, para não criar no jogador a perceção de que a hipótese de ganhar é maior do que é na realidade.

6.1.4 - Duração do jogo

O período de tempo para os jogadores tomarem decisões no jogo é definido pela entidade exploradora, mas não pode ser inferior a 3 segundos.

O ciclo de jogo deve ser interpretado como o tempo que decorre desde o início do jogo até que o resultado seja apresentado ao jogador (por exemplo, num jogo de póquer o ciclo de jogo decorre desde a distribuição das cartas até ao show down).

6.1.5 - Regras do jogo

1 - Todos os jogos devem ter associadas as respetivas regras e instruções de jogo.

2 - As regras do jogo não podem ser alteradas durante o jogo.

3 - Os jogos devem ser explorados e praticados de acordo com as regras que, em cada momento, estiverem em vigor.

6.1.6 - Instruções, informações e regras do jogo

1 - As instruções devem ser escritas em língua portuguesa (devendo encontrar-se gramatical e sintaticamente corretas), sem prejuízo de poderem ser disponibilizadas noutra língua por opção do jogador. Não será obrigatória a tradução de termos técnicos comuns utilizados internacionalmente nas regras e atividade de jogo.

2 - O idioma base deve ser sempre o português (se várias idiomas forem utilizados).

3 - As regras do jogo devem estar disponíveis para os jogadores, independentemente dos equipamentos/aplicações utilizados.

4 - As regras e as instruções do jogo devem ser as mesmas em todos os idiomas utilizados.

5 - Todas as instruções e informações devem ser precisas e específicas.

6 - As regras e as instruções do jogo devem estar disponíveis sem ser necessário jogar.

7 - As regras e as instruções do jogo (incluindo restrições ao jogo e como jogar) devem estar disponíveis durante todo o jogo e ser acessíveis em todas as páginas da presença na Internet relacionadas com o jogo

8 - O nome do jogo deverá estar visível para o jogador no momento em que se encontrar a fazer a sua aposta.

9 - As regras do jogo devem indicar todos os potenciais prémios, assim como o maior prémio possível por aposta unitária, associado à aposta do jogador.

10 - As funções associadas a cada "botão" de ação devem ser indicadas de forma clara.

Estas instruções deverão estar localizadas no próprio "botão".

6.2 - Apresentação Visual

6.2.1 - Jogos

1 - O sistema técnico de jogo deve assegurar que o nome do jogo é visível em todas as páginas da presença na Internet relacionadas com o jogo.

O nome do jogo pode estar visível no topo da página principal da janela ou na janela secundária em que o jogo está a decorrer.

2 - O sistema técnico de jogo deve assegurar que o saldo da conta do jogador é apresentado ou facilmente acessível em todas as páginas da presença na Internet relacionadas com o jogo.

3 - O sistema técnico de jogo deve apresentar ao jogador, em cada jogo, o montante da aposta que este está a realizar, bem como o valor da aposta unitária e o da aposta total.

4 - Se o resultado do jogo puder ser afetado por fatores externos ao jogador, o sistema técnico do jogo deve alertar o jogador para esse facto, providenciando o link onde conste a informação necessária ao seu esclarecimento.

5 - O sistema técnico de jogo deve exibir um relógio que permita ao jogador verificar há quanto tempo está a jogar (exceto para o jogo fornecido através de telemóveis e dispositivos com capacidades semelhantes de exibição limitada).

6.2.2 - Ações do jogo

1 - O sistema técnico de jogo deve disponibilizar ao jogador o valor atual da sua aposta, bem como as possibilidades de aposta que pode realizar.

2 - O sistema técnico de jogo deve apresentar graficamente todos os prémios possíveis e todas as combinações de prémios possíveis.

3 - O sistema técnico de jogo deve informar claramente qual o valor máximo da aposta.

4 - O sistema técnico de jogo deve informar claramente qual o valor mínimo da aposta.

6.2.3 - Resultados do jogo

1 - O sistema técnico de jogo deve apresentar, de modo claro e inequívoco, os resultados do jogo.

2 - O sistema técnico de jogo deve apresentar, por um período de tempo adequado, o resultado do jogo.

3 - O sistema técnico de jogo deve apresentar, de modo claro e inequívoco, os prémios do jogo.

6.2.4 - Regras dos jogos de fortuna ou azar

As regras dos jogos de fortuna ou azar devem estar de acordo com a regulamentação aplicável.

6.3 - Gestão das funções do jogo

6.3.1 - Ativação e desativação dos jogos

1 - O sistema técnico de jogo deve conter os meios que permitam imediatamente ativar e desativar jogos individuais.

2 - O sistema técnico de jogo deve conter os meios que permitam imediatamente ativar e desativar todos os jogos.

3 - O sistema técnico de jogo deve conter os meios que permitam imediatamente ativar e desativar as atividades de jogo de cada jogador.

4 - A informação sobre qualquer ativação e desativação deverá ser guardada num log.

5 - Quando um jogo está desativado, não deverá ser apresentado na página da Internet, e permanecerá indisponível durante todo o período da desativação.

6 - Quando um jogo é desativado o jogador deverá poder concluir qualquer jogo que esteja em curso. Caso tal não seja possível o jogador deve ser imediatamente notificado desse fato pelo sistema técnico de jogo.

7 - Quando um jogo multi-state (i.e., um jogo que consiste em várias etapas) é desativado os jogadores deverão poder completar os jogos em curso no próximo login. Se tal não for possível, o sistema técnico do jogo deverá informar os jogadores sobre este facto.

6.3.2 - Jogos incompletos

1 - Sem prejuízo do disposto na regulamentação aplicável a cada tipo de jogo e ou aposta, o sistema técnico de jogo deve permitir ao jogador completar quaisquer jogos incompletos.

Consideram-se jogos incompletos quando ocorra, nomeadamente, uma das seguintes situações:

a) Perda de comunicações;

b) Reinicialização do sistema;

c) Jogos que foram desativados/ativados;

d) Reinicialização do dispositivo do jogador;

e) Encerramento anormal da aplicação cliente/servidor.

2 - Após o jogador voltar a estabelecer ligação com o sistema técnico do jogo, o sistema deve exibir os jogos incompletos e permitir ao jogador completá-los, quando aplicável.

3 - O sistema técnico de jogo deve assegurar que todos os jogos incompletos são contabilizados e que o jogador conhece o estado desses jogos e da sua aposta. Apostas que estão bloqueadas em jogos incompletos e que podem ser finalizados devem ser apresentadas separadamente na conta de jogador.

4 - Jogos incompletos devem ser resolvidos no prazo de 90 dias. As regras específicas dos jogos a fixar pela entidade exploradora devem prever o que sucede com as apostas do jogador.

5 - Sempre que não for possível completar um jogo incompleto, o sistema técnico de jogo deve conseguir calcular os montantes que sejam devidos ao jogador, nos termos da regulamentação aplicável.

6.3.3 - Processo de tratamento de erros

1 - Sem prejuízo do disposto na regulamentação aplicável a cada tipo de jogo e ou aposta, as entidades exploradoras devem fixar o processo de tratamento de erros no sistema técnico.

2 - O sistema técnico de jogo deve apresentar a mensagem "ocorreu um erro; todos os pagamentos e apostas são anulados", ou equivalente.

3 - O sistema técnico de jogo deverá registar todos os erros do sistema, incluindo a sua causa e solução, dentro das possibilidades técnicas do sistema técnico de jogo.

4 - O sistema técnico de jogo deve permitir gerar um relatório que contenha, nomeadamente, a identificação do erro ocorrido, a respetiva causa e a sua solução.

6.3.4 - Sessões do jogador e sequência de jogo

1 - O sistema técnico de jogo deve assegurar que o jogador não pode iniciar um novo jogo até que o jogo em curso esteja completado e que todos os logs e saldos das contas de jogador se encontrem atualizados, a menos que o jogo seja retomado em suporte técnico diferente.

O disposto no número anterior não impede um jogador de jogar vários jogos diferentes ao mesmo tempo.

2 - O sistema técnico de jogo deve conter uma funcionalidade que permita ao jogador acesso a todos os elementos essenciais da última jogada em que tenha participado, nomeadamente o resultado e valores apostados, seja através da reconstituição visual do jogo, seja através de descrição das jogadas.

3 - O jogo do jogador e/ou o saldo da conta de jogador não podem ser negativamente afetados em caso de avarias ou reinicializações do sistema técnico de jogo ou de partes do mesmo.

6.3.5 - Terminais dos utilizadores

1 - O sistema técnico do jogo deve ser capaz de identificar diferentes tipos de terminais e versões, mantendo um registo dos mesmos. Exceto por razões técnicas devidamente justificadas, o sistema técnico do jogo registará o uso de uma solução específica fornecida para dispositivos móveis.

2 - O uso de quaisquer terminais que utilizem interfaces gráficas menores que os habituais (i.e., dispositivos móveis em vez de computadores pessoais), poderão disponibilizar conteúdos que não sejam integralmente visíveis tal como o são nos terminais que utilizam interfaces gráficas maiores. O sistema técnico do jogo, por razões estritamente técnicas, resultantes das características dos terminais, poderá oferecer diferentes funcionalidades nos diferentes tipos de terminais.

3 - O jogador deverá ser informado acerca de quaisquer limitações na informação ou nas funcionalidades do terminal, bem como, se for o caso, nas aplicações (apps) a que eventualmente recorra para jogar, devendo, em qualquer uma das situações, expressamente aceitar essas limitações.

4 - A entidade exploradora deverá mitigar quaisquer riscos que resultem da falta de informação ou de funcionalidades de um determinado terminal, devendo disponibilizar a mesma informação através de outros meios.

5 - A menos que exista um obstáculo técnico devidamente justificado, todas as informações que aparecem no interface também devem aparecer no interface móvel. Se não for possível incluir todas as informações ou ligações no interface do jogo, estes deverão ser oferecidos a partir de um link, menu ou outro aplicativo no mesmo terminal.

6 - O sistema técnico do jogo não deverá processar jogos de terminais, se os mesmos não dispuserem de todos os recursos mínimos necessários para se jogar sem problemas técnicos e sem desvantagens para o jogador.

6.3.6 - Registos e Logs

1 - As ações do jogador devem ser registadas num log, como informação da sessão, desde o momento em que o jogador faz login até ao momento em que faz logout.

O jogo do jogador e/ou o saldo da conta de jogador não podem ser negativamente afetados em caso de interrupção de uma sessão provocada pelo sistema técnico de jogo.

2 - O sistema técnico de jogo deve armazenar informações sobre a sessão.

A informação da sessão de jogo deve incluir, nomeadamente:

. Um número de identificação (ID) do jogador;

. A hora de início e de fim da sessão;

. Os detalhes relativos ao equipamento do jogador;

. O montante total apostado durante a sessão;

. O montante total ganho durante a sessão;

. O montante total depositado na conta de jogador durante a sessão (com indicação da data e hora);

. O montante total levantado da conta de jogador durante a sessão (com indicação da data e hora);

. A hora da última confirmação da sessão;

. A razão para encerrar a sessão;

. As informações sobre o jogo durante a sessão.

3 - O sistema técnico de jogo deve registar os dados relativos ao jogador. Os dados do jogador deverão incluir, nomeadamente:

. Os elementos de identificação do jogador;

. Os elementos e saldo da conta de jogador;

. O estado do jogador: suspensão ou autoexclusão, se aplicável;

. Eventuais contas de jogo anteriores e o motivo para o seu cancelamento/ desativação;

. A informação da sessão.

4 - O sistema técnico de jogo deve gravar informações sobre os jogos jogados. A informação sobre os jogos jogados deve incluir, nomeadamente:

. O ID do jogador;

. A identificação e versão do jogo;

. A hora de início do jogo baseado no sistema técnico de jogo;

. O saldo da conta de jogador à hora do início do jogo;

. As apostas (data e hora);

. A contribuição para jackpots;

. O estado do jogo (nomeadamente em curso, /completo);

. O resultado do jogo (data e hora);

. O prémio de jackpot (se relevante);

. A hora do fim do jogo baseado no sistema técnico de jogo;

. Os prémios;

. O saldo da conta de jogador à hora do fim do jogo;

. Todos os jogos inacabados e a respetiva razão;

. A informação sobre todos os jogos em que o jogador participou.

6 - O sistema técnico de jogo deverá gravar informações sobre eventos relevantes. A informação sobre eventos relevantes deve incluir, nomeadamente:

. Os prémios mais elevados (a ser determinado pela entidade exploradora);

. As transferências elevadas de fundos (transferências individuais e totais durante um determinado período de tempo);

. As alterações nos parâmetros de jogo;

. As alterações nos parâmetros do jackpot;

. Os jackpots recém-criados;

. A participação dos jogadores em jackpots;

. O payout do jackpot;

. A descontinuação do jackpot;

. Os jogadores autoexcluídos e suspensos (incluindo os pedidos de cancelamento de suspensão /exclusão, bem como a anulação efetiva de uma suspensão ou exclusão).

7 - O sistema técnico de jogo deve gravar eventos, incluindo, nomeadamente:

. A criação de uma conta de jogador e desativação/cancelamento da conta de jogador;

. Alterações nos dados do jogador;

. Alterações nos parâmetros de jogo e do jackpot;

. Criação ou descontinuação de jackpots;

. Prémios de jackpot;

. Transferências de elevados montantes de dinheiro;

. Perda de comunicação com o equipamento de um jogador ou time out.

6.3.7 - Armazenamento de dados

1 - O sistema técnico de jogo deve guardar os dados relacionados com a atividade de jogos e apostas online pelo período de 10 anos.

6.4 - Jackpots

6.4.1 - Regras

1 - Sem prejuízo do disposto na regulamentação aplicável a cada tipo de jogo e ou aposta, as entidades exploradoras devem fixar as regras específicas que, em cada jogo e ou aposta, são aplicáveis aos jackpots

6.4.2 - Imparcialidade e transparência

2 - O sistema técnico de jogo deve assegurar que os montantes efetivos transferidos no caso de um jackpot correspondem ao que se encontra estabelecido nas regras que o regem.

3 - O sistema técnico de jogo deve assegurar que o retorno para o jogador corresponde ao valor que ele tem a expectativa de receber, independentemente da base de aposta unitária do jogo.

4 - Se existe um valor mínimo de aposta para o desencadear de um jackpot, o jogo corrente (excluindo o jackpot) deve mostrar o retorno efetivo ao jogador.

5 - O sistema técnico de jogo deve assegurar que todos os jogadores que contribuem para um jackpot têm uma hipótese de o ganhar, no decorrer do jogo em questão.

6 - O sistema técnico de jogo deve assegurar que a probabilidade de ganhar o jackpot é diretamente proporcional à contribuição do jogador para o mesmo.

6.4.3 - Estruturação de um Jackpot

1 - O sistema técnico de jogo deve manter um rigoroso controlo de acesso ao processo de alterações das configurações do jackpot (parâmetros do jackpot). As alterações feitas após o início do jackpot deverão ser reduzidas ao mínimo necessário.

2 - O Sistema técnico de jogo deve garantir a existência de uma funcionalidade de base que mantenha inalterada a configuração dos jackpots em vigor, no caso de os parâmetros base serem alterados antes da distribuição dos prémios.

3 - Os parâmetros do jackpot não devem ser afetados pelas funcionalidades utilizadas para descontinuação ou ativação do jackpot.

6.4.4 - Notificação do jackpot

1 - O sistema técnico de jogo deve garantir que o montante atual do jackpot é apresentado em todos os equipamentos dos jogadores participantes.

2 - O sistema técnico de jogo deve atualizar o montante do jackpot em todos os equipamentos dos jogadores participantes, pelo menos, a cada 30 segundos.

3 - Depois de desencadeado um jackpot, o sistema técnico de jogo deve assegurar que um jogador premiado é imediatamente notificado.

4 - Depois de desencadeado um jackpot, o sistema técnico de jogo deve informar todos os jogadores participantes do seu valor.

6.4.5 - Iniciadores de um Jackpot

1 - O sistema técnico de jogo deve manter um registo detalhado, exaustivo e adequado para auditoria, no qual devem ser apresentados todos os jackpots.

6.4.6 - Reporte do jackpot

1 - O sistema técnico de jogo deve manter um registo detalhado, exaustivo e adequado para auditoria, no qual deve ser registado o estado de cada jackpot, bem como a seguinte informação:

. Data e hora;

. Configuração;

. Contribuições;

. Iniciadores;

. Prémios;

. Identificação de colaboradores autorizados que acederam ao sistema.

2 - O sistema técnico de jogo deve registar o estado do jackpot em suporte redundante e tolerante ao erro.

3 - O sistema técnico de jogo deve permitir reconstituir os valores e prémios dos jackpots, tomando por base as contribuições dos jogadores.

6.4.7 - Jackpots descontinuados

1 - O sistema técnico de jogo deve mostrar de uma forma clara se um jackpot não se encontra disponível para um jogador.

2 - O sistema técnico de jogo deve garantir que toda a informação de retorno ao jogador está correta, independentemente do jackpot estar ou não disponível para o jogador.

3 - O sistema técnico de jogo deve garantir que a descontinuação de um jackpot não afeta a sua configuração.

6.5 - Apostas

6.5.1 - Configuração geral

1 - O sistema técnico de jogo deve manter um registo atualizado de todos os jogos e apostas explorados no âmbito da licença emitida pelo SRIJ.

2 - O registo deve conter, pelo menos:

. Data e hora;

. O conjunto de resultados possíveis;

. A aposta do jogador;

. A aposta da entidade exploradora, se aplicável

. O resultado;

3 - O sistema técnico de jogo deve garantir a realização de análises e a produção periódica de relatórios com o objetivo de prevenir, nomeadamente, casos de fraude e conluio.

4 - O sistema técnico de jogo deve apresentar os resultados dos eventos para os quais foram colocadas apostas.

6.6 - Jogos disputados entre jogadores (Peer-to-peer)

6.6.1 - Configuração Geral

1 - O sistema técnico de jogo deve manter um registo de todos os jogadores.

2 - O sistema técnico de jogo deve incluir funcionalidades que impeçam o jogador de jogar contra si próprio.

3 - O sistema técnico de jogo deve dispor de funcionalidades que permitam perceber se o mesmo equipamento está a ser simultaneamente utilizado por mais do que um jogador num jogo "jogador contra jogador" (peer-to-peer).

4 - O sistema técnico de jogo deve, sempre que possível, incluir uma salvaguarda para que o mesmo equipamento não seja utilizado simultaneamente por mais do que um jogador num jogo "jogador contra jogador" (peer-to-peer).

6.6.2 - Regras e informação

1 - As regras descritas em 5.1.1, 6.1.5 e 6.1.6 são igualmente aplicáveis a atividades de jogo jogador contra jogador (peer-to-peer games).

2 - As regras devem incluir a proibição dos jogadores jogarem contra si próprios, através da mesma ou de outra entidade exploradora.

3 - As regras devem proibir o conluio entre jogadores.

4 - As regras devem proibir a utilização de meios tecnológicos de automação (bots) pelos jogadores.

5 - As regras devem prever de forma clara e acessível as comissões, taxas e quaisquer outros custos que possam ser aplicados aos jogadores.

6.6.3 - Monitorização

1 - O sistema técnico de jogo deve conter funcionalidades técnicas que permitam constantemente identificar e divulgar ações e atividades suspeitas em tempo real.

2 - O sistema técnico de jogo dever permitir analisar ações e atividades suspeitas e produzir os correspondentes relatórios.

3 - O sistema técnico de jogo deve dispor de funcionalidades técnicas que permitam detetar o uso de meios tecnológicos de automação (bots) pelos jogadores.

6.7 - Requisitos para o Gerador de Números Aleatórios

6.7.1 - Conformidade do gerador de números aleatórios

1 - A geração de resultados em jogos de fortuna ou azar deve basear-se num gerador de números aleatórios (GNA), bem como em funcionalidades relevantes de suporte à sua atividade (por exemplo, semente do algoritmo, mapeamento, shuffling).

2 - Os GNA devem, de um modo geral, ser reconhecidos como uma fonte criptograficamente segura para geração de números aleatórios.

3 - Os resultados do GNA devem passar nos seguintes testes estatísticos:

. Conjunto de testes DIEHARD (Marsaglia);

. NIST (National Institute of Standards and Technology) Statistical Test Suite; ou

. Um conjunto de testes semelhantes do mesmo nível.

Os testes devem ser realizados com um conjunto de dados que sejam considerados pela OCR como suficientes para garantir resultados estatísticos válidos.

4 - Os resultados do GNA devem ser estatisticamente independentes.

5 - Os resultados do GNA devem conter um desvio padrão estatisticamente relevante.

6 - Os resultados do GNA devem ser imprevisíveis para quem não disponha de informação relativa ao seu algoritmo, ao seu modo de implementação e ao valor atual da sua semente (seed).

7 - O GNA deve passar em todos os testes durante o período de carga máxima. Carga máxima é definida como o nível de performance em que o sistema técnico de jogo não consegue sustentar a iteração com o jogador.

6.7.2 - Graus de Liberdade e Mapeamento

1 - Os resultados produzidos por um GNA devem ser distribuídos dentro de limites estatísticos expectáveis, nomeadamente replicando uma distribuição normal.

2 - A série de números selecionada pelo GNA deve assegurar uma probabilidade suficientemente aproximada ao resultado desejado e esperado por parte do jogador.

3 - O mapeamento e escalonamento de símbolos e eventos de jogo produzidos por um determinado GNA devem garantir que esses resultados possam ser posteriormente validados através de testes de aleatoriedade feitos ao GNA de origem dos mesmos.

4 - A entidade exploradora deve conseguir verificar que os resultados produzidos pelo GNA são os mesmos que foram utilizados e registados para o evento de jogo.

5 - Se as regras do jogo obrigam à produção antecipada de uma sequência ou mapeamento de unidades ou eventos de jogo (ex.: localização de objetos escondidos num labirinto), só pode ser produzida uma nova sequência ou mapeamento quando isso for permitido pelas regras do jogo.

6 - A menos que tal seja referido nas regras do jogo, os eventos de jogo baseados em aleatoriedade devem ser independentes (não relacionados com) de outros eventos do jogo em curso ou de jogos anteriores.

7 - Resultados aleatórios que decidem jogos, apenas podem ser afetados ou controlados pela combinação de valores numéricos produzidos por um GNA certificado e pelas regras do jogo.

6.7.3 - Processos de Gestão de Erros

1 - Se o sistema técnico de jogo utiliza um GNA baseado em hardware, deve ser garantida a utilização de um mecanismo de prevenção (fail-safe) para desativar o jogo no caso de se detetarem erros no equipamento.

2 - Se o GNA for baseado em software, o sistema técnico de jogo deverá garantir uma monitorização contínua dos resultados e a desativação dos jogos no caso de falha do GNA.

6.7.4 - Introdução da semente do algoritmo (Seeding)

1 - O sistema técnico de jogo deve garantir a segurança do GNA através da adoção de um método apropriado e eficiente para a introdução e reintrodução da semente do algoritmo (seeding e re-seeding).

6.7.5 - Segurança

1 - Um resultado do GNA ao ser mapeado e escalonado para um símbolo ou um evento de jogo deve ser imediatamente aplicado ao jogo, de acordo com as respetivas regras.

7 - Sistema de Gestão de Segurança de Informação

As especificações técnicas que se seguem são conformes com os n.os 4 e 5 do artigo 32.º do RJO

A presente secção apresenta os requisitos de segurança relativos à segurança da informação que têm de ser satisfeitos pelas entidades exploradoras. O SRIJ baseou os requisitos de segurança no Anexo A à norma internacional ISO/IEC 27001: 2013.

Esta norma é aplicável desde outubro de 2013, devendo as entidades exploradoras fazer auditar os seus sistemas de segurança nos termos dela constantes.

7.1 - Políticas de Segurança da Informação

7.1.1 - Política de Segurança da Informação

1 - As entidades exploradoras devem dispor de políticas e procedimentos de segurança documentados e divulgados por todos os colaboradores e, se aplicável, a entidades externas que tenham acesso, pelos serviços que prestam, aos componentes críticos do sistema técnico de jogo.

2 - A entidade exploradora tem de planear e realizar avaliações periódicas resultantes de alterações significativas e atualizar os procedimentos nessa conformidade.

7.2 - Gestão de Recursos Humanos

7.2.1 - Durante a Contratação

1 - O plano de segurança relativa aos colaboradores da entidade exploradora deve incluir a gestão do recrutamento, as atividades de formação e a rescisão da contratação, com particular atenção ao controlo de acesso à informação e componentes críticos.

7.2.2 - Rescisão ou Alteração da Contratação

1 - A entidade exploradora deve dispor de uma política para a criação, alteração e rescisão de acesso do utilizador ao sistema de jogo e aos sistemas de negócio. Com base nesta política, deve ser desenhado um procedimento formal, que assegure o seguinte:

. Que exista uma descrição de funções detalhada para cada colaborador;

. Que o acesso do utilizador ao sistema de jogo e aos sistemas de atividade esteja de acordo com a descrição de funções de cada colaborador;

. Que o acesso do utilizador esteja adaptado por forma a refletir qualquer alteração à descrição de funções; e

. Que o acesso do utilizador cesse com a rescisão do contrato do pessoal.

Devem existir políticas e procedimentos relativos ao acesso de utilizadores ao sistema técnico de jogo, bem como para consultores e demais terceiros, caso esse acesso lhes seja concedido.

7.3 - Gestão de Ativos

7.3.1 - Tratamento dos Suportes de Informação

1 - A entidade exploradora deve implementar procedimentos para a gestão de todos os suportes passíveis de serem removidos de instalações seguras. Todos os suportes que possam conter dados com informação crítica devem ser apagados ou destruídos antes de serem removidos ou reutilizados.

7.4 - Controlo de Acessos

7.4.1 - Política de Controlo de Acessos

1 - A entidade exploradora deve dispor de políticas de controlo de acessos destinadas a proteger o Equipamentos que suporta os sistemas e o acesso dos utilizadores aos sistemas.

7.4.2 - Acesso de Utilizadores

1 - O sistema técnico de jogo e os sistemas de negócio devem fazer aplicar o uso de senhas (passwords) fortes no que toca ao acesso de utilizadores aos sistemas, assim como de logouts ou protetores de ecrã temporizados para pontos de acesso inativos.

7.4.3 - Gestão do Acesso de Utilizadores

1 - A autorização para a concessão de acesso ao sistema técnico de jogo e aos sistemas de negócio deve ser restringida ao menor número de colaboradores possível. Tanto o sistema técnico de jogo como os sistemas de negócio devem admitir contas de utilizador com graus diferenciados de acesso e de privilégios para que a política e procedimentos relativos à gestão dos recursos humanos) possa ser implementada.

2 - As senhas (passwords) iniciais devem ser alteradas para uma senha escolhida pelo utilizador quando da sua primeira entrada no sistema (login).

7.4.4 - Controlo e Segurança do Acesso ao Sistema Operativo

1 - Todos os utilizadores dispõem de uma identificação/identificador único e o sistema técnico de jogo e os sistemas de negócio devem utilizar técnicas de autenticação adequadas para assegurar a confirmação da identidade de cada utilizador quando da sua entrada no sistema (login).

2 - Devem ser utilizados controlos de encaminhamento para controlar os acessos ao sistema operativo dos componentes mais importantes. Essa importância deriva da classificação dos componentes constantes no programa de gestão de alterações do SRIJ).

3 - Quando um sistema operativo é instalado num dispositivo que faça parte do sistema técnico de jogo, somente as funções estritamente necessárias para os fins desse dispositivo devem ser instaladas/ativadas. As funcionalidades e programas com capacidade para cancelar os controlos (override) do sistema e das aplicações não devem nunca ser instalados no sistema técnico de jogo e nos sistemas de negócio da entidade exploradora.

7.4.5 - Controlo e Segurança de Acesso para Aplicações e Informações

1 - Todos os utilizadores dispõem de um identificador/identificador único de utilizador exclusivamente para uso pessoal, sendo que o sistema técnico de jogo e os sistemas de negócio devem aplicar técnicas de autenticação adequadas para comprovar a identidade apresentada por cada utilizador, aquando da entrada no sistema (login).

2 - A informação sensível deve ser armazenada e encriptada, devendo o sistema técnico de jogo e os sistemas de negócio dispor de restrições de controlo de acesso reforçadas no que se refere a esta informação.

7.5 - Criptografia

7.5.1 - Controlo criptográfico

1 - As chaves/códigos de encriptação devem ser armazenadas num suporte de armazenamento seguro e redundante.

7.6 - Segurança Física e Ambiental

7.6.1 - Localização e Proteção do Equipamento

1 - Os sistemas informáticos devem residir fisicamente num centro de dados, que garanta que o acesso físico aos componentes críticos do sistema fique restringido ao pessoal autorizado.

2 - Devem ser garantidos equipamentos de suporte adequados, tais como energia, refrigeração e equipamento de supressão de incêndio, tendo em conta a escala dos componentes críticos do sistema.

7.6.2 - Alienação ou Reutilização Seguras do Equipamento

1 - A entidade exploradora deve implementar procedimentos destinados à gestão dos suportes passíveis de ser removidos das instalações seguras, devendo os suportes que contenham dados críticos ser apagados ou destruídos em segurança antes de serem alienados, removidos ou reutilizados.

7.6.3 - Equipamento com Utilizador Ausente

1 - O sistema técnico de jogo e os sistemas de negócio devem aplicar logouts (fecho de sessão) ou protetores de ecrã temporizados para pontos de acesso inativos.

7.7 - Gestão da Segurança das Operações

7.7.1 - Procedimentos e Responsabilidades Operacionais

1 - O sistema técnico de jogo e os sistemas de negócio devem ser capazes de se desligar em segurança, em caso de falha de energia elétrica. É necessária energia de emergência para assegurar a integridade dos dados, logs e cópias de segurança, assim como assegurar que os jogos em curso possam ser concluídos.

7.7.2 - Planeamento e Monitorização do Sistema

1 - O sistema técnico de jogo e os sistemas de negócio devem proceder ao registo do desempenho do sistema e dispor de uma funcionalidade que forneça relatórios de desempenho.

2 - A utilização dos recursos do sistema técnico de jogo deve ser monitorizada e ajustada, sendo efetuadas projeções dos requisitos de capacidade futura, por forma a assegurar um desempenho adequado do sistema.

7.7.3 - Separação dos Ambientes de Desenvolvimento, Teste ou Qualidade e Operacional

1 - A entidade exploradora deve garantir a operação em segurança do sistema técnico de jogo através da separação dos sistemas e tarefas de desenvolvimento, testes ou qualidade e produção.

7.7.4 - Proteção contra Código Malicioso

1 - O sistema técnico de jogo e os sistemas de negócio devem dispor de ferramentas de deteção e prevenção de intrusão e inserção não autorizadas de qualquer código.

7.7.5 - Cópias de Segurança da Informação

1 - O sistema técnico de jogo e os sistemas de negócio devem ter capacidade para produzir cópias de segurança dos dados críticos, garantindo a sua recuperação integral a partir de cópias de segurança.

2 - O sistema técnico de jogo e os sistemas de negócio devem permitir a recuperação integral dos dados essenciais desde o momento da produção da última cópia de segurança até ao momento em que tenha ocorrido a falha do sistema.

7.7.6 - Registo e Monitorização

1 - O sistema técnico de jogo e os sistemas de negócio devem manter registos de auditoria (audit logs), que registem:

. As atividades do utilizador, exceções e eventos de segurança de informação;

. As atividades do administrador e dos utilizadores operacionais de sistema da entidade exploradora; e

. As falhas do Sistema, a respetiva análise e as medidas corretivas tomadas.

2 - Estes registos de auditoria (audit logs) devem ser conservados durante um período adequado não inferior a 6 meses, e protegidos contra o acesso não autorizado.

3 - O sistema técnico de jogo e os sistemas de negócio devem registar todas as falhas e monitorizar a utilização e a operacionalidade dos componentes críticos.

4 - Deve proceder-se a uma análise regular e periódica dos registos de auditoria (audit logs), e tomadas medidas conforme os factos identificados.

7.7.7 - Referencial de Tempo do Sistema e Sincronização

1 - O sistema de jogo e os sistemas de negócio têm de ser submetidos, em intervalos adequados, a uma sincronização dos relógios, através de um servidor referencial de tempo universal, que possa, por exemplo, ser utilizado para entradas (log) de registo.

7.8 - Gestão da Segurança de Comunicações

7.8.1 - Gestão de Segurança da Rede

1 - O sistema de jogo e os sistemas de negócio devem ser implementados para que dispositivos no mesmo domínio de transmissão não admitam quaisquer caminhos de rede alternativos que permitam contornar a firewall.

2 - As firewalls devem ser dedicadas, devendo apenas conter contas administrativas e aplicações relacionadas com a sua operação.

3 - O acesso à firewall deve ser restringido aos postos de trabalho que façam parte da base de configuração, devendo ser rejeitados todos os pacotes de dados oriundos de qualquer outro local que não esses postos de trabalho.

4 - As firewalls devem manter um registo de auditoria (audit logs) das alterações de parâmetros que afetem as autorizações de ligação à firewall e de todas as tentativas de acesso, bem ou mal sucedidas, que sejam efetuadas.

7.8.2 - Utilização das Redes Públicas

1 - Caso a entidade exploradora utilize redes públicas para o seu tráfego de dados entre subsistemas geograficamente dispersos, a informação deve ser encriptada e os subsistemas devem obrigar a autenticação.

2 - Todas as comunicações entre subsistemas geograficamente dispersos devem proporcionar proteção contra:

. Transmissão incompleta;

. Mis-routing (alteração de roteamento), alteração não autorizada de mensagens;

. Divulgação não autorizada;

. Duplicação não autorizada de mensagens; ou

. Repetição não autorizada de mensagens.

3 - A entidade exploradora deve utilizar um DNS primário e um DNS secundário seguro. O DNS secundário deve estar lógica e fisicamente separado do DNS primário.

7.8.3 - Segurança dos Serviços de Rede

1 - O sistema técnico de jogo e os sistemas de negócio devem aplicar restrições para o controlo de acesso às funções de rede, sendo o acesso dos utilizadores apenas possível através deste controlo de acesso. O sistema técnico de jogo e os sistemas de negócio devem impedir o acesso interno e externo não autorizado às funções de rede.

7.8.4 - Segregação de Redes

1 - O sistema técnico de jogo e os sistemas de negócio devem utilizar redes segregadas, de modo que os grupos de funções, utilizadores e subsistemas relacionadas sejam segregados entre si.

7.9 - Aquisição, Desenvolvimento e Manutenção de Sistemas de Informação

7.9.1 - Processamento Correto de Aplicações

1 - A entrada de dados (input) nas aplicações deve ser validada, para assegurar que os dados se mostram no contexto apropriado e não podem prejudicar o sistema de jogo e os sistemas de negócio.

2 - A validação/reconciliação automática deve ser incorporada nas aplicações, para impedir a corrupção ou interferência.

3 - A saída de dados (output) das aplicações deve ser validada, para assegurar o correto tratamento da informação armazenada.

7.10 - Gestão das Relações com os Fornecedores

7.10.1 - Segurança de Terceiros

1 - Quando a entidade exploradora necessite de serviços de terceiros que envolvam o acesso ao sistema técnico de jogo, aos sistemas de negócio, às redes de comunicação ou o acesso às instalações, produtos ou serviços relacionados com a prática de jogos, essas entidades devem cumprir os requisitos de segurança aplicáveis a terceiros da entidade exploradora.

2 - O sistema técnico de jogo deve autenticar qualquer acesso oriundo de outros sistemas e componentes (por ex., portas de ligação de sistemas de pagamento) e do pessoal de manutenção.

3 - Os serviços prestados por terceiros devem incluir, nos contratos, a realização de verificações e medidas de segurança, e têm de ser periodicamente auditados e monitorizados.

7.11 - Gestão de Incidentes de Segurança

7.11.1 - Incidentes de Segurança

1 - A entidade exploradora deve dispor de um processo documentado relativo à gestão de incidentes de segurança, devendo ser comunicados ao SRIJ, logo que possível, quaisquer incidentes que afetem a integridade e confidencialidade do sistema técnico de jogo.

2 - Os incidentes de segurança devem ser registados e documentar de forma clara e concisamente, os factos, os impactos e as medidas tomadas.

7.12 - Gestão da Continuidade de Negócio

7.12.1 - Plano de Continuidade de Negócio

1 - A entidade exploradora deve dispor de um Plano de Continuidade de Negócio destinado à recuperação da atividade de jogo de um desastre operacional irreversível, incluindo as medidas técnicas, humanas e organizacionais que assegurem a continuidade da prestação dos serviços e uma replicação do sistema de jogo, que garanta a continuidade da exploração normal do sistema.

2 - A entidade exploradora deve ajustar a sua infraestrutura e os seus processos e implementar as medidas necessárias para estabelecer objetivos alcançáveis no Plano de Continuidade de Negócio.

3 - Em caso de desastre operacional irreversível, a entidade exploradora deve informar imediatamente o SRIJ, efetuando uma estimativa do respetivo impacto e do tempo previsto de recuperação.

8 - Auditorias e Controlos de Segurança

A presente secção apresenta os requisitos que as entidades exploradoras têm de satisfazer para assegurar a segurança global do sistema técnico de jogo e dos sistemas de negócio relacionados, através de auditorias à segurança, testes de segurança e análise de vulnerabilidades.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2015/12/250000001/0000300035.pdf)

As especificações técnicas que se seguem são conformes com o artigo 36.º do RJO

8.1 - Requisitos das Auditorias de Segurança

8.1.1 - Auditorias de Segurança Anuais

1 - Anualmente é realizada uma auditoria de segurança para avaliar a conformidade com os requisitos de segurança das operações dos jogos e apostas online genericamente descritas no presente documento.

2 - As auditorias e inspeções de segurança abrangem:

. A segurança física e as inspeções que têm de ser realizadas nas instalações da entidade exploradora são executadas de acordo com as melhores práticas;

O acesso às instalações e a todos os recursos do sistema técnico de jogo da entidade exploradora deve ser facultado à entidade que realiza os testes;

. A segurança lógica, realizada através de testes remotos ou nas instalações da entidade exploradora, quer sejam intrusivos ou outros, que devem ser realizados de acordo com o definido nas respetivas secções;

Estas auditorias e inspeções devem ser agendadas com antecedência.

3 - A entidade exploradora tem de proporcionar às pessoas nomeadas pela entidade que realiza os testes, os meios e recursos necessários para a execução das auditorias e inspeções.

Estas auditorias e inspeções podem incluir, por exemplo:

. Apresentações técnicas e funcionais, efetuadas pela entidade exploradora, dos sistemas instalados na plataforma de jogos;

. Análise técnica e detalhada desses sistemas nos ambientes proporcionados pela entidade exploradora.

4 - A entidade exploradora tem de proceder à correção no prazo de 48 horas de qualquer vulnerabilidade de severidade alta (7,0 + CVSS (Common Vulnerability Scoring System scale)) encontrada durante as auditorias de segurança. Caso uma medida de segurança impeça que as vulnerabilidades sejam diretamente corrigidas, a entidade exploradora deve sugerir soluções temporárias para impedir que estas vulnerabilidades relevantes sejam exploradas. O plano de ação associado a esta situação, a elaborar pela entidade exploradora, deve ser ser enviado ao SRIJ.

8.2 - Testes de Segurança

8.2.1 - Enquadramento dos Teste de Segurança

1 - Os requisitos do SRIJ relativamente aos Testes de Segurança são parcialmente inspirados na norma Payment Card Industry - Data Security Standard (PCI-DSS) e no guia de realização de testes do OWASP.

2 - Anualmente, são realizados testes de intrusão para avaliar a conformidade com os requisitos descritos neste documento.

8.2.2 - Objetivo dos Testes de Segurança

1 - Ao realizar os testes de segurança, o Organismo de Certificação Reconhecido deve procurar explorar as eventuais vulnerabilidades do sistema de jogo da entidade exploradora. O teste de segurança deve abranger, nomeadamente, os pontos fracos detetados durante a análise de vulnerabilidades.

8.2.3 - Componentes Protegidos

1 - O sistema de jogo e os sistemas de negócio existentes no ambiente de produção da entidade exploradora devem estar protegidos contra qualquer ataque de intrusos. Em particular, os componentes que contenham informação sensível relativa aos jogadores devem estar protegidos.

2 - A entidade exploradora pode minimizar o risco de acesso não autorizado procedendo à segmentação das redes internas, incluindo os subsistemas que comunicam informação sensível através de redes públicas.

8.2.4 - Atualização do Software e do Hardware

1 - Cabe à entidade exploradora, a responsabilidade pela manutenção dos componentes do sistema com um grau de atualização que assegure a mais elevada segurança possível e não comprometa a integridade dos sistemas. Deste modo, o risco de acesso não autorizado à informação sensível é minimizado.

2 - Em caso de atualização de componentes da entidade exploradora, tem de ser realizada uma nova análise de vulnerabilidades para garantir que a integridade dos sistemas se mantém intacta.

3 - São necessários testes de segurança, na sequência de atualizações ou alterações significativas à infraestrutura ou à sua utilização, (por exemplo, a instalação de novos componentes do sistema, a adição de uma sub-rede ou a adição de um servidor de Internet), e no caso de a análise de vulnerabilidades ter elementos com uma pontuação de 4 ou superior na escala CVSS. O que se considera de alterações "significativas" depende, em grande medida, da montagem (set-up) de um dado ambiente, pelo que não pode ser definido enquanto tal pelo SRIJ. Uma alteração é, contudo, considerada significativa se uma versão atualizada ou uma alteração puder afetar ou proporcionar acesso a informação sensível e/ou aos componentes.

4 - A entidade certificadora pode permitir que os testes de segurança acima descritos sejam realizados por uma função interna dedicada na entidade exploradora que esteja a efetuar testes de segurança dos sistemas. Esta função deve ser realizada por técnicos especializados com as competências adequadas, assim como ser segregada, em termos organizacionais, da função que implemente as alterações ao sistema.

5 - Caso os testes de segurança sejam realizados por recursos internos da entidade exploradora, a entidade certificadora deve avaliar, aprovar e certificar os testes de três em três meses. O relatório deve indicar claramente se este foi o método utilizado.

8.2.5 - Processo dos Testes de Segurança

1 - A entidade certificadora pode utilizar a escala CVSS ou um sistema de pontuação idêntico de igual qualidade para avaliar se os sistemas da entidade exploradora têm um nível adequado.

2 - Ao executar testes de segurança, a entidade certificadora deve procurar acessos não autorizados aos sistemas da entidade exploradora. As tentativas de acesso não autorizado serão realizadas até ao mais alto nível de acesso possível, sendo finalizadas com e sem credenciais de acesso disponíveis (testes do tipo whitebox/blackbox).

3 - Através deste acesso, será testada a lógica da atividade, nomeadamente segundo a lista (mínima) de cenários seguinte:

. Manipulação da recolha e armazenamento de dados no Safe da Infraestrutura de Entrada e Registo;

. Manipulação da geração de resultados;

. Efeitos na execução de jogos;

. Fraude com os fundos de jogadores;

. Furto de fundos de jogadores;

. Manipulação de registos de auditoria;

. Acesso a informação sensível;

. Manipulação de informação sensível.

8.3 - Análise de Vulnerabilidades

8.3.1 - Enquadramento da Análise de Vulnerabilidades

1 - Os requisitos do SRIJ relativamente à Análise de Vulnerabilidades são parcialmente inspirados na norma Payment Card Industry - Data Security Standard (PCI-DSS).

2 - Devem ser realizadas análises de vulnerabilidades trimestrais para avaliar a conformidade em relação aos requisitos descritos neste documento.

8.3.2 - Objetivo da Análise de Vulnerabilidades

1 - Ao executar a análise de vulnerabilidades, a entidade certificadora deve verificar a existência de vulnerabilidades na infraestrutura técnica da entidade exploradora, as quais podem, potencialmente, ser utilizadas para obter acesso não autorizado através de interfaces públicos.

8.3.3 - Componentes Protegidos

1 - O sistema de jogo e os sistemas de atividade do ambiente de produção da entidade exploradora devem estar protegidos dos ataques de intrusos. Em particular, devem estar protegidos, os componentes que contenham informação sensível respeitante aos jogadores.

2 - A entidade exploradora pode minimizar o risco de acesso não autorizado procedendo à segmentação das redes internas, incluindo os subsistemas que comunicam a informação sensível através das redes públicas.

8.3.4 - Atualização do Software e do Hardware

1 - Cabe à entidade exploradora a responsabilidade pela manutenção dos componentes do sistema com um grau de atualização que assegure a mais elevada segurança possível, não comprometendo a integridade dos sistemas. Deste modo, o risco de acesso não autorizado à informação sensível é minimizado.

2 - Em caso de atualização de componentes da entidade exploradora, tem de ser realizada uma nova análise de vulnerabilidades para garantir que a integridade dos sistemas se mantém intacta e não foi comprometida.

3 - É necessário proceder à análise de vulnerabilidades na sequência de atualizações ou alterações significativas à infraestrutura ou à sua utilização (por exemplo, a instalação de novos componentes do sistema, a adição de uma sub-rede ou a adição de um servidor de Internet). O que se considera alterações "significativas" depende, em grande medida, da montagem (set-up) de um dado ambiente, pelo que não pode ser definido enquanto tal pelo SRIJ. Uma alteração é, contudo, considerada significativa se uma versão atualizada ou uma alteração puder afetar ou proporcionar acesso a informação sensível e/ou aos componentes.

4 - A entidade certificadora pode permitir que os varrimentos de vulnerabilidades descritos acima sejam realizados por um recurso interno dedicado da entidade exploradora que efetue o varrimento de vulnerabilidades dos sistemas. Esta função deve ser realizada por técnicos especializados com as adequadas competências, assim como ser segregada, em termos organizacionais, da função que implemente as alterações ao sistema.

5 - Caso a análise de vulnerabilidades seja realizada por um recurso interno dedicado da entidade exploradora, a entidade certificadora deve avaliar, aprovar e certificar estes resultados de três em três meses. O relatório de certificação deve indicar claramente se este foi o método utilizado.

8.3.5 - Processo de Análise de Vulnerabilidades

1 - O organismo de realização de testes reconhecido pode utilizar a escala CVSS ou um sistema de pontuação idêntico e de igual qualidade para avaliar se os sistemas da entidade exploradora dispõem de um nível de segurança adequado.

2 - No caso de a análise de vulnerabilidades ter elementos com uma pontuação de 4 ou superior na escala CVSS, a entidade exploradora tem de reparar as vulnerabilidades detetadas e proceder a nova análise.

3 - Se a análise detetar, no sistema da entidade exploradora, vulnerabilidades que não possam ser reparadas no prazo de validade da análise anterior, a certificação tem de ser acompanhada de um plano de reparações e devem ser instalados controlos de compensação. Estas vulnerabilidades devem estar reparadas na análise trimestral seguinte.

8.4 - Controlo do Jogo e das Apostas pela Entidade Exploradora

8.4.1 - Indicadores de Controlo de Jogo

1 - Em complemento dos elementos estritamente técnicos, a entidade exploradora deve descrever com precisão, documentar e implementar diversos sistemas destinados a monitorizar, supervisionar e controlar o jogo e as apostas.

2 - A entidade exploradora deve indicar os diferentes indicadores e intervalos de alerta instalados, assim como os procedimentos de reação subsequente que tenham sido definidos.

3 - A entidade exploradora deve assegurar que, caso um limiar de alerta seja ultrapassado, os dados sistemáticos associados ao alerta serão igualmente enviados ao SRIJ.

8.4.2 - Verificações e Auditorias Periódicas

1 - A entidade exploradora deve implementar verificações periódicas para apurar se os requisitos aplicáveis estão a ser consistentemente respeitados. Estas verificações devem incluir, no mínimo:

. Inspeção diária realizada pelo pessoal e pela gestão (tanto quanto possível integrada nos procedimentos e sistemas da atividade);

. Auditorias internas periódicas e de amostragem aleatória;

. Auditorias externas, quando necessárias para documentar satisfatoriamente que os requisitos aplicáveis são satisfeitos;

. Processamento e arquivamento dos resultados do controlo;

. Comunicação imediata ao SRIJ em caso de deteção de erros ou infrações e de suspeita de erros ou infrações praticados pela entidade exploradora. A comunicação deve incluir a avaliação que a entidade exploradora faz das consequências do erro ou infração.

8.4.3 - Procedimentos Comerciais

1 - A entidade exploradora é responsável por elaborar, documentar e seguir os procedimentos relevantes, destinados a apoiar e assegurar que a entidade exploradora cumpre com os requisitos aplicáveis. Os procedimentos comerciais devem incluir, no mínimo:

. A entidade exploradora deve assegurar a monitorização de todos os componentes e a transmissão de dados de todo o sistema técnico de jogo, incluindo, nomeadamente, comunicação, pacotes de dados, redes, o Safe, o gerador de números aleatórios (RNG), o sistema de jogo, bem como os componentes e as transmissões de dados de quaisquer terceiros envolvidos, com o objetivo de assegurar a integridade, a fiabilidade e a acessibilidade;

. A entidade exploradora deve assegurar a existência de procedimentos de segurança e de recuperação, para impedir a perda de dados;

. A entidade exploradora deve assegurar os procedimentos de manutenção e segurança, com o objetivo de assegurar operações seguras e fiáveis.

8.4.4 - Funções do Pessoal

1 - A entidade exploradora deve estar adequadamente organizada e dispor de um quadro de pessoal adaptado às necessidades da oferta dos seus produtos, de acordo com o RJO e com os requisitos estabelecidos pelo SRIJ.

2 - Para além dos requisitos relativos às funções e ao pessoal previstos no âmbito do processo de atribuição e emissão das licenças, a entidade exploradora deve estabelecer, no mínimo, as funções organizacionais que a seguir se indicam. As funções devem ser sempre ocupadas por pessoas cujo nome seja referido [nomes individuais], que serão responsáveis pela respetiva área, tal como indicado em seguida:

. Responsável pelo software de jogo e pelas operações de jogo, que assegura, nomeadamente, que a prática de jogos é estruturada e explorada de modo apropriado e fiável, sem erros nem batota;

. Responsável pela segurança da TI, que assegura, nomeadamente, que todas as formas de hardware, software e networks de TI utilizadas pela entidade exploradora funcionam com a segurança apropriada;

. Responsável pela área financeira, que assegura, nomeadamente, que o SRIJ recebe atempadamente o montante de Imposto Especial de Jogo Online, nos termos fixados no RJO;

. Responsável pelas políticas, procedimentos e controlos, com o objetivo de prevenir, impedir e detetar o branqueamento de capitais e o financiamento do terrorismo, tendo em vista assegurar o cumprimento as normas e regulamentos aplicáveis nestas matérias.

3 - O pessoal acima identificado deve possuir as qualificações e a experiência necessárias para assumir as funções e responsabilidade atribuídas. A entidade exploradora deve, ainda, assegurar que lhes são atribuídos os poderes bastantes para estabelecer medidas e implementar as alterações necessárias para assegurar o cumprimento dos requisitos.

4 - Estas pessoas constituem-se como os contactos de ligação no decurso das auditorias e controlos, devendo fornecer e prestar contas de toda a informação e documentação que, relativamente à sua área, o SRIJ possa exigir.

9 - Programa de Gestão de Alterações

As especificações técnicas que se seguem são conformes com os n.os 3 e 4 do artigo 12.º, artigo 13.º, artigos 32.º a 35.º e artigos 37.º a 44.º do RJO

9.1 - Enquadramento da Gestão de Alterações

O objetivo deste programa de gestão de alterações é a definição dos meios pelos quais as entidades exploradoras de jogos e apostas online podem efetuar alterações de modo suficientemente justificado e controlado para que possam ser aprovadas, na medida em que causam um impacto não significativo na eficiência da atividade, no âmbito de situações de rotina em que se considere que tais alterações não põem em risco os princípios e objetivos subjacentes ao RJO.

Este enquadramento geral da gestão de alterações ao sistema técnico de jogo estabelece as bases necessárias para a implementação de um programa de gestão de alterações.

Exige-se à entidade exploradora que:

. Delegue responsabilidades e poderes relativamente à gestão de alterações;

. Crie um plano de alterações formal, que defina a estrutura da gestão de alterações;

. Identifique e classifique os componentes do sistema técnico de jogo para a gestão de configurações;

. Registe as alterações num registo de alterações; e

. Determine uma configuração de base para o sistema técnico de jogo no seu todo.

Na classificação dos componentes, pode ser relevante ponderar as diferenças entre as categorias de jogos e apostas e os tipos de jogos, bem como os diferentes riscos envolvidos.

9.2 - Responsabilidade pela Gestão de Alterações

9.2.1 - Responsabilidades da Entidade Exploradora pela Gestão de Alterações

A entidade exploradora é a única responsável pelas alterações introduzidas no seu sistema técnico de jogo, independentemente de essas alterações terem sido por si efetuadas ou por terceiro, por conta da entidade exploradora.

A entidade exploradora deve clarificar e definir as responsabilidades e os poderes referentes à implementação e à aprovação do processo de alterações.

9.2.2 - Pessoal responsável pela Gestão de Alterações

A entidade exploradora deve nomear um ou mais elementos do seu pessoal para assumir a responsabilidade global pelas alterações ao sistema. Os responsáveis podem organizar-se em comissão de controlo de alterações.

Os responsáveis devem envolver outros elementos destacados do pessoal da entidade exploradora para assegurar a elevada qualidade das alterações.

Antes da aprovação de alterações ao sistema, os responsáveis devem confirmar que:

. A proposta de alteração ao sistema está conforme com o Programa de Certificação do SRIJ e com a certificação anteriormente obtida;

. A proposta de alteração ao sistema é necessária;

. A proposta de alteração ao sistema foi devidamente ponderada, documentada e categorizada;

. As consequências da implementação da alteração não comprometem a integridade do sistema técnico de jogo; e

. O processo das medidas planeadas, aquando da implementação da alteração ao sistema, em termos de documentação, hardware e/ou software, está conforme com o n.º 9.7 do presente documento.

9.3 - Planeamento da Gestão de Alterações

A gestão de alterações da entidade exploradora deve ser documentada num plano de gestão de alterações, que estabeleça o quadro global da gestão de alterações ao sistema.

O plano de gestão de alterações da entidade exploradora deve:

. Ser documentado;

. Ser aprovado pela direção/administração [senior management],pelo gestor responsável;

. Ser objeto de controlo interno adequado;

. Identificar o procedimento de gestão da configuração a ser utilizado;

. Descrever as responsabilidades e os poderes do pessoal no que se refere às alterações ao sistema técnico de jogo e aos seus componentes, assim como assegurar que o ciclo de vida dos componentes é descrito.

9.4 - Gestão da Configuração

A entidade exploradora deve aplicar um determinado grau de gestão da configuração, que produza uma perspetiva geral do sistema técnico de jogo, identificando cada um dos componentes. Quando os componentes tiverem sido registados e classificados no registo de componentes, a configuração base é criada, o que assegura a possibilidade de identificação de alterações ao sistema técnico de jogo em futuras certificações.

O objetivo é possibilitar a identificação dos componentes de configuração dos sistemas, de modo a que o impacte das alterações a cada componente seja considerado no contexto dos objetivos e normas regulamentares.

A gestão da configuração constante do presente documento destina-se a complementar a gestão de configuração atualmente utilizada pela entidade exploradora.

Caso a entidade exploradora não aplique ao seu sistema técnico de jogo qualquer gestão de configuração, considera-se que o presente documento contém os requisitos mínimos da gestão da configuração.

9.4.1 - Estrutura do Sistema Técnico de Jogo e Definição dos Componentes

A estrutura do sistema técnico de jogo é composta pelos componentes de hardware e de software definidos e pelas respetivas inter-relações e interdependências.

Os componentes serão definidos no registo de componentes, tendo por base o facto de as suas características funcionais e físicas poderem ser ou não geridas separadamente.

A definição basear-se-á:

. Nos requisitos regulamentares;

. Na avaliação da criticidade, considerando em que medida os componentes sejam críticos em termos de riscos para a confidencialidade, a integridade, a disponibilidade e a rastreabilidade;

. No facto de a tecnologia, o design ou o desenvolvimento serem novos ou modificados; e

. Nos interfaces com outros componentes.

O número de componentes de configuração selecionados deve otimizar a capacidade de controlar o processo de desenvolvimento do sistema técnico de jogo. Considerando o ciclo de vida do produto, a definição dos componentes deve ser iniciada o mais cedo possível e sujeita a uma avaliação regular à medida que o produto evolui.

9.4.2 - Inscrição de Componentes num Registo de Componentes

A entidade exploradora e os seus fornecedores devem inscrever todos os componentes definidos num registo de componentes.

A entidade exploradora pode livremente estabelecer o nível de pormenorização do registo de componentes. Se o grau de pormenorização for baixo - por ex., se o sistema técnico de jogo for o único componente -, qualquer alteração a este componente imporia um elevado grau de gestão e controlo. Um elevado nível de pormenorização possibilitaria ajustar a escala do grau de gestão e controlo de acordo com a importância do papel desempenhado por cada componente no sistema técnico de jogo.

A informação seguinte deve ser registada para cada componente:

. A definição do componente;

. Um número de identificação único;

. O número da versão;

. As características identificadoras;

. O titular responsável pelas alterações ao componente;

. A classificação relativa à confidencialidade, integridade, disponibilidade e rastreabilidade;

. Controlo da soma/Valor "hash" relativos aos componentes classificados como substancialmente relevantes; e

. A localização geográfica, caso se trate de um componente de hardware.

Estas informações constituirão o suporte para possibilitar à entidade certificadora e ao SRIJ determinar se o componente foi alterado, por comparação com a configuração de base.

9.4.3 - Classificação dos Componentes

Todos os componentes definidos devem ser classificados segundo os quatro critérios seguintes:

. Confidencialidade: a informação confidencial respeitante ao jogador (por ex., identificação e informação de transações);

. Integridade: a integridade do sistema técnico de jogo, a sua funcionalidade e a informação armazenada no sistema;

. Disponibilidade: a disponibilidade da informação respeitante ao jogador;

. Rastreabilidade: a atividade do utilizador (incluindo jogadores, pessoal e terceiros) relativamente ao componente.

Deve ser atribuído a cada componente um código de relevância de acordo coma escala abaixo identificada, tendo por base a relevância do componente para atingir ou assegurar cada um dos critérios acima referidos:

. 1: sem relevância (o componente não tem qualquer impacto negativo nos critérios);

. 2: alguma relevância (o componente pode ter algum impacto nos critérios); e

. 3: relevância substancial (os critérios estão relacionados com o componente ou dependem do mesmo).

A atribuição do código de relevância mais elevado a um dos quatro critérios determina a classificação do componente.

9.4.4 - Classificação de componentes de hardware em servidores virtuais (computação em nuvem)

Caso a entidade exploradora utilize um ambiente de servidor virtual, este facto pode afetar a classificação destes componentes de hardware.

9.4.4.1 - Ambiente de servidor virtual privado

Nas situações em que a entidade exploradora utilize um ambiente de servidor privado para suportar o sistema técnico de jogo, o hardware de suporte deve ter a redundância e capacidade adequadas, para assegurar o desempenho contínuo do sistema, mesmo em caso de defeito de um componente de hardware, garantindo assim um desempenho contínuo e ininterrupto do sistema de jogo até que o erro seja corrigido. Nesta situação, é permitido classificar os componentes de hardware com um código de relevância inferior.

Nas situações em que o hardware físico combinado, que suporta a camada de virtualização, não disponha de redundância e capacidade adequadas para mitigar o defeito de um componente de hardware, não conseguindo assim assegurar um desempenho contínuo e ininterrupto do sistema técnico de jogo até que o erro tenha sido corrigido, cada um desses componentes de hardware deve ser classificado com um código de relevância superior.

9.4.4.2 - Ambiente de servidor público

Nas situações em que um fornecedor está a suportar a entidade exploradora com um ambiente de servidor virtual (nuvem), os componentes de hardware no ambiente de servidor não serão classificados, desde que o fornecedor esteja a observar as condições seguintes:

. O fornecedor não pode fazer parte da empresa da entidade exploradora nem estar de qualquer forma ligado à atividade da entidade exploradora;

. O fornecedor é certificado nos termos da norma internacional ISO/IEC 27001;

. O hardware que suporta o ambiente de servidor virtual deve ter a redundância e capacidade adequadas, para assegurar o desempenho contínuo do sistema, mesmo em caso de defeito de um componente de hardware, garantindo assim um desempenho contínuo e ininterrupto do sistema técnico de jogo até que o erro seja corrigido.

9.5 - Inscrição das Alterações num Registo de Alterações

As alterações introduzidas no sistema técnico de jogo certificado devem ser inscritas, com data, num registo de alterações. O registo de alterações constituirá o suporte para possibilitar à entidade certificadora e ao regulador inspecionar e auditar as alterações efetuadas em cada um dos componentes por comparação com a configuração de base.

9.6 - Configuração de Base do Sistema Técnico de Jogo

A configuração base é estabelecida, durante a certificação inicial do sistema técnico de jogo da entidade exploradora,

A configuração de base permite que quer a entidade certificadora quer o regulador inspecionem todas as alterações aos componentes, de modo a seja possível rastrear todas as eventuais alterações desde a configuração base inicial até à realização da auditoria.

Em resultado de cada processo de certificação é estabelecida uma nova configuração base, que servirá de suporte às alterações até ao período de certificação seguinte.

9.7 - Processo de Gestão de Alterações

Todas as alterações ao sistema serão controladas. O grau de controlo depende do impacto que se espera que a alteração tenha no sistema técnico de jogo certificado e nos objetivos e normas regulamentares.

O processo de gestão de alterações será documentado no registo de alterações, devendo a documentação incluir:

. A descrição da alteração;

. A classificação da alteração em termos de complexidade, recursos e escalonamento;

. A justificação da alteração;

. A avaliação da alteração;

. A descrição da forma como a alteração será aprovada; e

. A descrição da forma como a alteração será implementada e verificada.

9.7.1 - Justificação da Alteração

Antes da aprovação formal de qualquer alteração), a proposta de alteração deve ser fundamentada e documentada no registo de alterações.

A proposta de alteração deve incluir as seguintes informações:

. O(s) componente(s) e a documentação com o(s) mesmo(s) relacionada a alterar, incluindo o número de identificação único, o número da versão e o estado;

. A descrição da proposta alteração;

. Uma lista de outros componentes e da documentação relacionada que possam ser afetados pela alteração;

. O pessoal que executa a proposta de alteração, assim como a data da proposta;

. O motivo da alteração; e

. A categoria da alteração.

O processamento da alteração e as decisões e disposições com o mesmo relacionadas, devem ser permanentemente documentados.

9.7.2 - Avaliação da alteração

A proposta de alteração deve ser avaliada e documentada no registo de alterações. A avaliação deve ser realizada de acordo com os requisitos do RJO. A avaliação de riscos deve basear-se na norma internacional "ISO/IEC 31010 Risk management - Risk assessment techniques" (Gestão de Riscos - Técnicas de avaliação de Riscos).

A avaliação da alteração deve incluir:

. O efeito esperado da alteração;

. A descrição do risco associado à alteração;

. A descrição do efeito da alteração na conformidade regulamentar do titular da licença; e

. O impacto da alteração na confidencialidade, integridade, disponibilidade e rastreabilidade do sistema técnico de jogo.

9.7.3 - Aprovação da alteração

Deve ser estabelecido um processo que assegure que todas as propostas de alteração e as avaliações de alteração às mesmas associadas são apresentadas para aprovação formal, dando lugar à sua aprovação ou rejeição.

As decisões relativas a alterações, incluindo as respetivas considerações, devem ser inscritas no registo de alterações.

9.7.4 - Implementação e verificação de alterações

Esta secção aplica-se às alterações aos componentes classificados com o código de relevância 2 ou 3. Os componentes classificados com o código de relevância 1 não são relevantes para os critérios previstos no n.º 9.4.3, pelo que as alterações a estes componentes não necessitam da aprovação de entidade certificadora.

Após a implementação de uma alteração, será verificada a conformidade com a alteração aprovada, sendo a verificação inscrita no registo de alterações.

9.7.5 - Alterações a componentes classificados com o código de relevância 3

A entidade certificadora deve apreciar e aprovar a avaliação da alteração efetuada pela entidade exploradora no que se refere a todas as alterações aos componentes do sistema técnico de jogo classificados com o código de relevância 3 ("relevância importante/substancial").

Antes da implementação, todas as alterações aos componentes classificados com o código de relevância 3 têm de ser aprovadas pelo SRIJ.

A entidade certificadora deve certificar todas as alterações durante a implementação ou imediatamente após a mesma. Estas certificações devem ser incluídas no relatório apresentado de três em três meses.

A entidade certificadora pode admitir alterações sem certificação quando a entidade exploradora disponha de recursos próprios que garantam a qualidade da gestão de alterações. Esta função deve ser desempenhada por pessoal com as adequadas competências e segregada, em termos organizacionais, da função que implemente essas mesmas alterações.

As alterações consideradas de extrema urgência (por ex., alterações para resolver problemas de segurança do sistema técnico de jogo) podem ocorrer antes da certificação pela entidade certificadora e da aprovação formal do SRIJ, devendo no entanto ser obrigatoriamente comunicadas.

9.7.6 - Alterações a componentes classificados com o código de relevância 2

A entidade certificadora deve apreciar e aprovar a avaliação da alteração efetuada pela entidade exploradora, considerando todas as alterações aos componentes do sistema técnico de jogo classificados com o código de relevância 2 ("alguma relevância").

A entidade certificadora deve certificar estas alterações de três em três meses.

Estas certificações devem ser incluídas no relatório apresentado de três em três meses.

A entidade certificadora deve efetuar a análise do risco envolvido nas alterações com base num método de amostragem apropriado, tendo em conta a relevância verificada e o risco envolvido na alteração, não sendo necessária uma auditoria completa a todas as alterações.

9.8 - Relatórios a partir do Registo de Componentes e do Registo de Alterações

Quando solicitado pelo SRIJ ou pela entidade certificadora, a entidade exploradora poderá gerar os seguintes relatórios com base nas informações constantes do registo de componentes e do registo de alterações

. Relatório de todos os componentes, incluindo as informações registadas a partir do registo de componentes;

. Relatório do historial de alterações de determinado componente;

. Relatório da localização geográfica de todos os componentes de hardware; e,

. Relatório de todas as alterações verificadas.

9.9 - Aprovação Prévia de uma Alteração pelo SRIJ

As alterações aos componentes classificados como de elevado nível de relevância têm de ser submetidas à prévia aprovação do SRIJ, de acordo com o documento intitulado Procedimentos da Gestão de Alterações, como adiante se indica.

9.9.1 - Gerador de Números Aleatórios

A implementação de um novo gerador de números aleatórios e as alterações a um gerador de números aleatórios existente, devem ser objeto de notificação ao SRIJ, com um mínimo de cinco dias úteis de antecedência relativamente à implementação ou à introdução da alteração.

9.9.2 - Novos jogos e alterações na oferta de jogos existente

Os requisitos técnicos da IER, o Safe e a utilização de registos de rastreio são descritos no documento intitulado "Modelo de Dados".

9.9.2.1 - Implementação de novos jogos

A implementação de novos jogos da mesma categoria e tipo que não afete a forma como a entidade exploradora utiliza os registos do Modelo de Dados do SRIJ, pode iniciar-se sem notificação prévia ao SRIJ.

Mediante solicitação da entidade exploradora, o SRIJ pode autorizar a exploração e prática de novos tipos de jogos, desde as respetivas regras de execução já tenham sido aprovadas, e após a devida certificação e homologação das alterações introduzidas no sistema técnico de jogo.

A oferta de novos jogos que utilizem registos do Modelo de Dados do SRIJ que não tenham sido previamente utilizados pela entidade exploradora, serão submetidos para aprovação ao SRIJ, no mínimo, cinco dias úteis antes de a oferta desses jogos, devendo juntamente com a notificação ser apresentados exemplos dos registos do Modelo de Dados a utilizar.

9.9.2.2 - Alterações na oferta de jogos existente

As alterações à oferta de jogos existente, desde que não afetem a forma como a entidade exploradora utiliza os registos do Modelo de Dados do SRIJ, podem iniciar-se sem notificação prévia ao SRIJ.

As alterações à oferta de jogos existente que afetem a utilização dos registos do Modelo de Dados do SRIJ, devem ser apresentadas pela entidade exploradora ao SRIJ, para aprovação, no mínimo, cinco dias úteis antes de a oferta ser alterada, sendo a notificação acompanhada de exemplos dos registos do Modelo de Dados.

## ANEXO 1 — Informação Técnica para entidades exploradoras de jogo online

[(ver documento original)](https://files.diariodarepublica.pt/2s/2015/12/250000001/0000300035.pdf)

21 de dezembro de 2015. - A Vice-Presidente do Conselho Diretivo, Maria Teresa Rodrigues Monteiro.

209215868
