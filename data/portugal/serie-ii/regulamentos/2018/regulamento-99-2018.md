---
schema_version: '1.0'
id: pt:dre:114657935:por
title: Regulamento n.º 99/2018
short_title: null
summary: Altera o Anexo I do Regulamento n.º 903-B/2015 que define os Requisitos Técnicos do Sistema Técnico do Jogo Online,
  publicado no Diário da República, 2.ª série, n.º 250, de 23 de dezembro de 2015, com as alterações introduzidas pelo Regulamento
  n.º 379-A/2016, publicado no Diário da República, 2.ª série, n.º 72, de 13 de abril de 2016
jurisdiction: portugal
territory: null
document_type: regulamento
document_type_label: Regulamento
issuing_authority:
- Economia - Instituto do Turismo de Portugal, I. P.
proposing_entity: null
official_number: 99/2018
official_date: null
publication_date: '2018-02-09'
publication:
  gazette: Diário da República
  reference: Diário da República n.º 29/2018, Série II de 2018-02-09
  number: '29'
  series: II
  supplement: null
  pages: 4639 - 4654
  pdf_url: https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf
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
  dre: '114657935'
  dre_path: /dr/detalhe/regulamento/99-2018-114657935
  internal: pt:dre:114657935:por
source:
  id: dre
  name: Diário da República Eletrónico
  official_url: https://diariodarepublica.pt/dr/detalhe/regulamento/99-2018-114657935
  metadata_url: null
  content_url: https://diariodarepublica.pt/dr/detalhe/regulamento/99-2018-114657935
  consolidated_url: null
  retrieved_at: '2026-11-13T06:26:41Z'
  retrieval_method: Endpoints screenservices (OutSystems) da aplicação web do DRE; não é uma API pública documentada
  source_modified_at: null
integrity:
  source_sha256: 7bb902f723170a21a053e9075b39e276364be274868e9d26b942b92b1df607cb
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal DRE
  collector_version: 0.1.0
  generated_by: leis-portugal collect dre
  generated_at: '2026-11-13T06:26:41Z'
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
- type: cites
  target: celex:32015L1535
  label: null
  source: null
- type: cites
  target: pt:dre:178510:por
  label: null
  source: null
- type: cites
  target: pt:dre:67098359:por
  label: null
  source: null
- type: cites
  target: pt:dre:72964679:por
  label: null
  source: null
- type: cites
  target: pt:dre:74146384:por
  label: null
  source: null
article_structure:
  article_count: 0
  section_count: 0
  extraction_method: Classes de parágrafo do TextoFormatado do DRE
derived_material:
  machine_generated: true
  notes: Markdown convertido do HTML TextoFormatado do DRE; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-11-13T06:26:41Z'
  warnings: []
  errors: []
---

# Regulamento n.º 99/2018

Altera o Anexo I do [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679) que define os Requisitos Técnicos do Sistema Técnico do Jogo Online, publicado no Diário da República, 2.ª série, n.º 250, de 23 de dezembro de 2015, com as alterações introduzidas pelo [Regulamento n.º 379-A/2016](https://diariodarepublica.pt/dr/detalhe/regulamento/379-a-2016-74146384) publicado no Diário da República, 2.ª série, n.º 72, de 13 de abril de 2016

Através do [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679), publicado no Diário da República, 2.ª série, n.º 250, de 23 de dezembro de 2015, foram aprovados os Requisitos Técnicos do Sistema Técnico do Jogo Online das entidades exploradoras.

O Anexo I ao referido Regulamento foi alterado pelo [Regulamento n.º 379-A/2016](https://diariodarepublica.pt/dr/detalhe/regulamento/379-a-2016-74146384), publicado no Diário da República, 2.ª série, n.º 72, de 13 de abril de 2016.

Verificou-se, no entanto, que esse Anexo contém algumas inexatidões, tendo sido, por isso, necessário proceder a alguns ajustamentos.

Assim, é retificado em todo o anexo as inexatidões dos formatos dos tipos de dados utilizados, quer na estrutura do XSD (XSD SCHEMA), quer nas regras de mapeamento (Regras de mapeamento para o modelo de dados da entidade exploradora), bem como a revisão dos comentários aos elementos e atributos, na CRIAÇÃO SISTEMÁTICA DE REPORTES, II. ESPECIFICAÇÃO DOS TIPOS DE RECOLHA DE DADOS para todas as categorias de dados V.1 Schema RESF_, V.2 Schema JGDR_, V.3 Schema SESS_, V.4 Schema AJOG_ e V.5 Schema TRAN_.

No II. CRIAÇÃO DE FICHEIROS DE DADOS DE JOGO, procedeu-se também a um ajustamento da hora limite para a colocação diária dos ficheiros de report no SAFE pelas Entidades Exploradoras, passando da 01:00 AM para as 04:00 AM.

Finalmente, procede-se à inserção de novos campos na estrutura do XSD Schema do V.6 Schema EXCL_ (CodAcao e Estado) e no V.2 Schema JGDR_ (cod_acao, estado e dur_suspensao), bem como a sua inclusão nas regras de mapeamento (Regras de mapeamento para o modelo de dados da entidade exploradora e nos comentários aos elementos e atributos, de forma a agilizar a gestão dos Autoexcluídos.

As alterações que agora se efetuam foram submetidas a prévia consulta pública. Porém, como não configuram modificações substanciais ao Anexo I do [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679), na redação dada pelo [Regulamento n.º 379-A/2016](https://diariodarepublica.pt/dr/detalhe/regulamento/379-a-2016-74146384), não se submeteram as mesmas ao procedimento previsto na Diretiva (UE) 2015/1535 do Parlamento Europeu e do Conselho, de 9 de setembro de 2015.

Assim, ao abrigo das disposições conjugadas do n.º 3 do artigo 35.º e do artigo 48.º do Regime Jurídico dos Jogos e Apostas Online (RJO), aprovado em anexo ao [Decreto-Lei n.º 66/2015](https://diariodarepublica.pt/dr/detalhe/decreto-lei/66-2015-67098359), de 29 de abril, com a alínea b) e m) do n.º 3 do artigo 7.º do [Decreto-Lei n.º 129/2012](https://diariodarepublica.pt/dr/detalhe/decreto-lei/129-2012-178510), de 22 de junho, na redação dada pelo [Decreto-Lei n.º 66/2015](https://diariodarepublica.pt/dr/detalhe/decreto-lei/66-2015-67098359), de 29 de abril, a Comissão de Jogos, deliberou:

1 - É alterado o Anexo I do [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679), publicado no Diário da República, 2.ª série, n.º 250, de 23 de dezembro de 2015, alterado pelo [Regulamento n.º 379-A/2016](https://diariodarepublica.pt/dr/detalhe/regulamento/379-a-2016-74146384), publicado no Diário da República, 2.ª série, n.º 72, de 13 de abril de 2016, nos termos do Anexo ao presente regulamento, que dele faz parte integrante.

2 - O presente regulamento entra em vigor no dia seguinte ao da sua publicação.

## ANEXO — Informação Técnica para entidades exploradoras de jogo online

Serviços de jogadores

A funcionalidade Serviços de Jogadores é considerada parte do Sistema técnico de jogo, aceitando-se por isso que esta funcionalidade possa ser implementada na infraestrutura da entidade exploradora.

No âmbito dos serviços de jogadores, as entidades eploradoras devem interagir com a infraestrutura de controlo Serviço de Regulação e Inspeção de Jogos (SRIJ) através de dois tipos de serviços de dados

I - SERVIÇO DE AUTOEXCLUSÃO DE JOGADORES

As funcionalidades garantidas pelo presente serviço são:

. Notificações de autoexclusão de jogadores

- As entidades exploradoras devem enviar ao SRIJ, num prazo máximo de 24 horas desde a receção do pedido, os dados dos jogadores que solicitam a sua autoexclusão ou que alterem ou revoguem um pedido anterior de autoexclusão.

- Notificações de alterações à base de jogadores autoexcluidos do SRIJ (onde é mantido o registo dos jogadores que solicitaram autoexclusão na página do SRIJ) serão enviadas a todas as entidades exploradoras em tempo real.

- As entidades exploradoras devem garantir a reação adequada às noificações mencionadas no ponto anterior e proceder à recolha da última versão da lista de jogadores autoexcluídos.

. Recolha da última versão da lista de jogadores autoexcluídos

- A entidade exploradora deve proceder ao download da última versão da lista de jogadores autoexcluídos transmitida pelo SRIJ.

A caracterização técnica e funcional deste serviço pode ser aferida nos seguintes pontos:

1 - Transferência da lista de jogadores autoexcluídos da entidade exploradora

As entidades exploradoras devem garantir diariamente a preparação de um ficheiro XML com uma lista (correspondente a 24 horas) dos jogadores autoexcluidos no seu sistema técnico de jogo, comprimi-lo, encriptá-lo e em seguida depositá-lo no seu Safe, no sub diretório:

/u01/app/oracle/mftxfer/[GameVault Code]/in/excl

Um processo dedicado de gestão de transferência de ficheiros iniciará a operação de transferência do ficheiro XML para a infraestrutura de controlo do SRIJ logo que detete a existência de novos dados dentro do filesystem em questão. A estrutura deste ficheiro encontra-se descrita no anexo sub capítulo V.6 Schema EXCL_.

O processo de encriptação do ficheiro encontra-se descrito no sub capítulo "processo de encriptação de ficheiros de dados".

2 - Recolha da lista de jogadores autoexcluidos do SRIJ

As entidades exploradoras devem invocar periodicamente o WebService ListaExcluidos para proceder à recolha da lista de jogadores autoexcluídos do SRIJ. Em seguida detalhar-se-á o WSDL correspondente a esse serviço:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Os dados devem ser enviados na forma de uma estrutura de XML. Em seguida detalhar-se-á o XSD correspondente:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

3 - Recolha (Inflow) das notificações de alteração de estado de jogadores autoexcluidos na lista do SRIJ

Sempre que se registe alguma alteração ao estado dos jogadores da lista de autoexcluidos do SRIJ, as entidades exploradoras serão imediatamente notificadas. O serviço designado "NotificacaoPedidoExclusao" faz o envio da informação para o sistema técnico de jogo de todas as entidades exploradoras utilizando a estrutura que se detalha em seguida:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

O sistema técnico de jogo das entidades exploradoras deve ser configurado de forma a cumprir todos os requisitos para garantir a comunicação com o WebService "NotificacaoPedidoExclusao".

II - SERVIÇO DE VERIFICAÇÃO DE IDENTIDADE DO JOGADOR

O sistema técnico de jogo das entidades exploradoras de jogo online deve, no âmbito do processo de registo dos jogadores, garantir a execução de uma validação da identidade dos jogadores.

A entidade exploradora deve verificar a identidade dos jogadores através dos seguintes métodos:

a) Diretamente no seu sistema técnico de jogo, através do cartão do cidadão ou da chave móvel digital.

b) Através da consulta em tempo real de uma base de dados de uma entidade pública, feita através de uma comunicação com o SRIJ.

Validação através do cartão de cidadão ou da chave móvel digital

A entidade exploradora deve garantir a utilização do mecanismo de registo de jogador autenticação.gov.pt (https://autenticacao.gov.pt/fa/Default.aspx) no seu sistema técnico de jogo, disponibilizado pela Agência para a Modernização Administrativa, IP (AMA I. P.).

No seguimento da emissão de cada licença de exploração de jogo online, o SRIJ irá enviar à AMA, I. P. a identificação da entidade exploradora licenciada, que deve por sua vez contactar esta agência e seguir os procedimentos necessários para integrar no processo de registo do seu sistema técnico de jogo um processo de validação baseado no serviço autenticação.gov.pt.

Este processo de verificação deve retornar ao sistema técnico de jogo da entidade exploradora informação relativamente ao nome, data de nascimento e número de identificação civil ligados ao cartão do cidadão ou da chave móvel digital utilizados no processo de registo de jogador.

Validação através do processo de validação de identidade do SRIJ

Com o objetivo de validar a informação ligada ao registo dos jogadores, o SRIJ irá mediar o acesso à base de dados de entidades públicas.

No âmbito do processo de validação da identidade do jogador, a entidade exploradora deve aceder, na infraestrutura de controlo do SRIJ, ao serviço PedidoVerificacaoIdentidadeTP.

Em seguida proceder-se-á à descrição detalhada do WSDL do serviço:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

O diagrama subjacente ao pedido é apresentado de seguida:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

A estrutura de XML é composta por quatro elementos:

«Nome» Nome do jogador

«NumeroIdentificacao» N.º de identificação civil

«TipoIdentificacao» Cartão de Cidadão

«DataNascimento» Data de nascimento do jogador

A informação é processada na infraestrutura de controlo do SRIJ e enviada para os serviços da base de dados da entidade pública, recebendo em seguida informação relativa ao Número de identificação civil, Nome completo e data de nascimento remetidos. A validação do pedido vai garantir informação para a resposta das seguintes questões:

a) A data de nascimento que corresponde ao n.º de identificação civil é válida?

b) O nome completo do cidadão que corresponde ao n.º de identificação civil é válido?

c) O cidadão que corresponde ao n.º de identificação civil enviado já faleceu?

d) Existe um cidadão registado com que o n.º de identificação civil enviado?

A informação enviada pelo serviço da base de dados de entidade pública é depois reportada ao sistema técnico da entidade exploradora.

A resposta do serviço incluirá os seguintes elementos:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Os principais elementos da estrutura de resposta do serviço RespostaVerificacaoTP são:

«SUCESSO»

«VALIDO»

«CODIGOERRO»

«MENSAGEMERRO»

«DETALHEERRO»

A estrutura total de informação que é redirecionada pelo SRIJ para o sistema técnico de jogo da entidade exploradora encontra-se incluída no esquema de XSD que detalhamos de seguida e corresponde ao elemento "RespostaVerificacaoTP":

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Requisitos de armazenamento de dados para as entidades exploradoras

I - CRIAÇÃO DE FICHEIROS DE DADOS DE JOGO

O SRIJ, de acordo com o enquadramento legal garantido pelo RJO, requer que as entidades exploradoras de jogo online façam o envio sistemático de informação ligada à atividade de jogo. Estes dados devem ser recolhidos no sistema técnico de jogo da entidade exploradora e enviados sobre a forma de um reporte de informação consolidado.

Os dados devem ser organizados em estruturas de XML com base em categorias pré-definidas e armazenadas numa estrutura de sistema de pastas do SAFE da entidade exploradora, como um ficheiro diário único, comprimido (ZIP) e encriptado.

Os ficheiros XML vão conter a atividade considerada relevante do sistema técnico de jogo da entidade exploradora durante o período de uma hora. Desta forma, deve ser produzido um ficheiro por cada hora do dia e por cada categoria de dados. Apenas o ficheiro de resumo financeiro da atividade de jogo da entidade exploradora e a lista diária de jogadores autoexcluídos devem ser produzidas numa base diária.

A entidade exploradora é responsável pela recolha e produção dos ficheiros XML para as seguintes categorias de dados:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

A entidade exploradora é responsável pela geração e colocação diária no SAFE, até às 04:00 AM (hora legal de Portugal Continental, determinada nos termos da legislação nacional e divulgada pelo Observatório Astronómico de Lisboa através dos servidores de NTP), de um ficheiro ZIP contendo quatro conjuntos de ficheiros XML horários, um ficheiro XML diário de resumo financeiro correspondentes à atividade do dia anterior, bem como um ficheiro diário com a lista de jogadores autoexcluídos do dia anterior.

A infraestrutura de controlo do SRIJ procede em seguida ao período de processamento, consubstanciado na recolha dos ficheiros encriptados colocados no SAFE, que decorrerá previsivelmente durante o intervalo da 01:00 AM às 12:00 PM (hora legal de Portugal Continental, determinada nos termos da legislação nacional e divulgada pelo Observatório Astronómico de Lisboa através dos servidores de NTP).

Se os dados que constam de um determinado ficheiro que tenha sido depositado no SAFE forem considerados inválidos pelo processo de recolha do SRIJ, a criação de um novo ficheiro ZIP para uma data específica será solicitada à entidade exploradora. Este novo ficheiro de dados reprocessado deverá em seguida ser comprimido, encriptado, e depositado no SAFE tal como detalhado no ponto "III - processo de encriptação de ficheiros de dados".

Os ficheiros devem ser nomeados com a extensão "rp.xml", para garantir o seu reconhecimento como "dados reprocessados" por parte do servidor de identificação do mecanismo de transferência de ficheiros do SRIJ e copiado para a estrutura de filesystem. As operações de reprocessamento não deverão ocorrer durante o periodo normal de processamento.

Nota importante: cada processo de reprocessamento e reenvio de dados deve obrigatoriamente incluir o ficheiro de resumo financeiro (ver o ponto V.1 Schema RESF_ para os detalhes da estrutura do ficheiro) junto com os restantes tipos de ficheiro que devem ser reprocessados.

II - REQUISITOS E ESPECIFICAÇÕES MINIMAS PARA O SAFE

As entidades exploradoras são responsáveis pela configuração de uma infraestrutura que deve garantir as funcionalidades associadas à atividade do SAFE, com os seguintes requisitos mínimos:

. Sistema operativo: Linux (Orientação: a versão Oracle Linux e Red hat já foi testada com a infraestrutura de controlo do SRIJ, tendo sido comprovada a sua compatibilidade);

. Rede de comunicação: uma conexão wide broadband (de pelo menos 20 Mbps) dedicada à infraestrutura de controlo do SRIJ;

. Um serviço de FTPS/SSH configurado no sistema operativo;

. Uma estrutura de pastas de ficheiros:

/u01/app/oracle/mftxfer/in;

/u01/app/oracle/mftxfer/in/excl;

/u01/app/oracle/mftxfer/in/out

III - PROCESSO DE ENCRIPTAÇÃO DE FICHEIROS DE DADOS

O registo de dados no SAFE é agrupado em categorias predefinidas. Cada uma dessas categorias deve ser assinada, comprimida e encriptada pela entidade exploradora utilizando para tal o formato e os procedimentos descritos no modelo de dados do SRIJ.

O SRIJ disponibiliza às entidades exploradoras certificados PKI Multicert 128 bits SSL/HTTPS para assinar, comprimir e encriptar os ficheiros comprimidos gravados e subsquentemente retidos no SAFE.

Os certificados Multicert 128 bits SSL/HTTPS são gerados de acordo com os seguintes requisitos:

. Recommendation ITU.T. X.509;

. RFC 5280;

. Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates, CA/Browser Forum.

E possuem as seguintes características técnicas:

. Identificação eletrónica segura e inequívoca de um servidor;

. Membership Server a uma entidade/organização;

. Identificação e autenticação segura contra servidores Web;

. Garantia de autenticidade, confidencialidade, não repúdio e integridade;

. 2048-bit RSA keys;

. Hash Algorithm - SHA256;

. Shelf Life de 3 anos;

. Integração e reconhecimento automático pelos principais browsers e aplicações de e-mail.

Como orientação, um processo de compressão e encriptação de ficheiros de jogo XML (obriga à criação do subfolder../mftxfer/bin) é descrito de seguida:

. Passo 1: Copia os ficheiros horários XML, o ficheiro diário XML de jogadores autoexcluídos e o ficheiro diário XML de resumo financeiro para o subfolder../mftxfer/in

. Passo 2: Posiciona-se no subfolder../mftxfer/bin

. Passo 3: Executa o seguinte script (que será disponibilizado pelo SRIJ)

» encripta.sh «certificate name» «date YYYYMMDD» «GameVault code»

Exemplo: » encripta.sh cert.pem 20150427 1AA

O shell script comprime os ficheiros XML dos subfolder 'in' para um ficheiro ZIP na pasta 'bin', encripta em seguida o ficheiro, gera o ficheiro de password rpasswd.pass.crypt, e cria um ficheiro ZIP final contendo os ficheiros referenciados.

. Passo 4: Move o ficheiro ZIP criado no Passo 3 para a pasta 'out'. Logo que o processo de Managed File Transfer da infraestrutura de controlo do SRIJ deteta novos ficheiros colocados no SAFE, inicia a sua transferência.

Criação Sistemática de Reportes

I - CONCEITOS DA ESTRUTURA DO MODELO DE DADOS DE JOGO ONLINE

Atividade de jogo online

Cada evento de jogo gravado deve ter um código específico único a cada entidade exploradora. O código de evento de jogo representa um evento aposta específico. Detalham-se em seguida alguns exemplos:

Uma aposta desportiva, um torneio de Poker, uma aposta num jogo de roleta, uma aposta hípica, uma aposta num jogo de baccara, uma aposta num jogo de blackjack, etc.

A cada jogador associado a um evento de jogo é atribuido um código de evento de jogador por entidade exploradora e por evento de jogo. Este código vai encontra-se sempre associado a todas as operações efetuadas pelo jogador, enquanto participante desse evento de jogo.

II - ESPECIFICAÇÃO DOS TIPOS DE RECOLHA DE DADOS

As entidades exploradoras devem recolhar e produzir os ficheiros XML com os seguintes tipos de dados:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Cada uma das categorias de dados vai ser em seguida detalhada.

V.1 Schema RESF_

Esta categoria deve incluir o reporte financeiro completo da atividade de jogo online da entidade exploradora (i.e., total apostas, total comissões) ao longo das 24 horas que correspondem ao dia em causa. Deve ser gerado um ficheiro por cada dia e como orientação à sua produção, os valores apresentados neste resumo global devem corresponder aos valores reportados nos XML schema para as mesmas variáveis nas restantes categorias de dados do modelo de dados.

Filename rules

NORMAL RESF_YYYYMMDD_[GameVault _code].xml

REPROCESSED RESF_YYYYMMDD_[GameVault _code]rp.xml

Exemplo: RESF_20150402_2AA.xml

XSD Schema

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data de produção do ficheiro de dados XML. Formato: YYYYMMDD

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

data_fin - Data de resumo de actividade financeira. Formato: YYYYMMDD

descricao - Descrição do tipo de jogo, aposta online.

licenca_exp - Código da licença de jogo online.

tipo_liq - Tipo de liquidez internacional - Sim: 1, Não: 0.

total_comissoes - Total de comissões gerado pela entidade exploradora ou operador de jogo online no período reportado, em euros.

total_ganhos - Total de ganhos gerado pela entidade exploradora ou operador de jogo online no período reportado, em euros.

total_apostas - Total de apostas gerado pela entidade exploradora ou operador de jogo online no periodo reportado, em euros.

total_reembolsos - Total de reembolsos gerado pela entidade exploradora ou operador de jogo online no periodo reportado, em euros.

V.2 Schema JGDR_

Esta categoria de dados deve incluir todos os novos registos de jogadores ou atualizações subsequentes de registos relativos a informação pessoal realizadas dentro do sistema técnico da entidade exploradora. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMAL JGDR_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSED JGDR_YYYYMMDDHH24_[GameVault _code]rp.xml

Example: JGDR_2015040221_2AA.xml

XSD Schema

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador único de jogador online na entidade exploradora.

conta_jog - Código de conta de jogador online.

tip_pag - Código de tipo de pagamento associado a conta de jogador online.

id_cidadao - Identificador de cidadão do jogador online.

id_tipocid - ID do tipo de identificador de cidadão. 0 BI, 1 CARTAO CIDADAO, 2 PASSAPORTE, 3 NUMERO IDENTIFIC FISCAL, 4 OUTRO.

timestp_reg - Timestamp de registo de alterações de dados do jogador online. Formato: YYYYMMDDHHMMSS

logon - Logon de entrada na entidade exploradora do jogo online.

alias_jog - Alias do jogador online.

nome - Nome completo do jogador online.

data_nascimento - Data de nascimento do jogador online. Formato: YYYYMMDD

nif - Numero de identificação fiscal do jogador online. 1 Cidadãos estrangeiros.

morada - Morada de residência do jogador online.

cod_postal - Código postal da morada de residência do jogador online. Formato: ####-###

id_nacao - Código alpha-2 -O3166 da nacionalidade do jogador online telefone - Contacto telefónico do jogador online.

email - Endereço eletrónico do jogador online.

resp_at - Resposta do serviço da autoridade tributária.

id_resp_at - Identificador de resposta do serviço de registo na autoridade tributária.

cod_acao - Código da alteração de estado da conta do Jogador.

estado - Estado da conta do Jogador.

dur_suspensao - Tempo da alteração em dias.

V.3 Schema SESS_

Esta categoria deve incluir os registos produzidos no sistema técnico de jogo durante uma sessão de um jogador online. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMAL SESS_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSED SESS_YYYYMMDDHH24_[GameVault _code]rp.xml

Example: SESS_2015040221_2AA.xml

XSD Schema

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador único de jogador online na entidade exploradora.

id_sessao - Identificador de sessão de entrada no operador.

timestp_acao - Timestamp de registo de sessão de jogador online. Formato: YYYYMMDDHHMMSS

tipo_log - Tipo de LOG de sessão. LOGIN ou LOGOUT.

dispositivo - Código de dispositivo de acesso. C computador, A Movel app, B Movel browser, T TV.

V.4 Schema AJOG_

Esta categoria deve incluir toda a atividade de jogo registada para o jogador dentro do sistema técnico de jogo da entidade exploradora. A atividade registada deve ser organizada em seis tipos de categorias de jogo: BlackJack, Baccara (Designação portuguesa: Ponto e Banca), Poker, Jogos de Fortuna e Azar, Apostas desportivas e Apostas hípicas. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMAL A JOG_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSED AJOG_YYYYMMDDHH24_[GameVault _code]rp.xml

Example: AJOG_2015040221_2AA.xml

XSD Schema

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador de jogador online na entidade exploradora.

logon - Username do jogador na entidade exploradora.

codigo - Código da conta de jogo do jogador na entidade exploradora ou operador de jogo online.

saldo_ini - Saldo inicial, em euros, da conta de jogo online.

saldo_mov - Saldo movimentado, em euros, na conta de jogo online.

saldo_final - Saldo atual, em euros, da conta de jogo online.

bonus_ini - Bónus inicial, em euros, na conta de jogo online.

bonus_mov - Bónus movimentado, em euros, na conta de jogo online.

bonus_final - Bónus atual, em euros, na conta de jogador online.

pinscr_ini - Saldo inicial, em euros, da conta de jogo online antes do pagamento dos prémios de inscrição.

pinscr_mov - Saldo movimentado, em euros, na conta de jogo online para pagamento dos prémios de inscrição.

pinscr_final - Saldo atual, em euros, da conta de jogo online depois do pagamento dos prémios de inscrição.

cod_ficha - Código externo de ficha de jogo, aposta online.

cod_aptr_jog - Código de aposta para utilização da entidade exploradora ou operador de jogo online.

ap_cruz - Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada.

timestp_ini - Ficha de jogo. Inicio da aposta, jogo online. Formato: YYYYMMDDHHMMSS

timestp_fim - Ficha de jogo. Fim da aposta, jogo online. Formato: YYYYMMDDHHMMSS

dathr_ini_evento - Datahora de inicio do evento. Formato: YYYYMMDDHH.

dathr_fim_evento - Datahora de fim do evento. Formato: YYYYMMDDHH.

cod_fichajog - Código externo de ficha de jogador atribuído pela entidade exploradora ou operador de jogo online.

id_sessao - Identificador de sessão de entrada no operador.

ip_jogador - IP da maquina do jogador online.

ip_regiao - Região do IP da maquina do jogador online.

cod_opejog - Código externo de operação de jogo, aposta online.

timestp - Timestamp da operação de jogo, aposta online. Formato: YYYYMMDDHHMMSS

id_inscricao - Identificador da inscrição do jogador.

id_partida - Identificador de partida de jogo.

descr - Descritivo do torneio, partida.

id_mesa - Identificador da mesa de jogo.

njog_max - Numero máximo de jogadores.

cartas_m - Lista de cartas existentes na mesa, separadas por hífen.

cartas_j - Lista de cartas do jogador online, separadas por hífen.

posicao_mesa - Lugar do jogador na mesa de jogo.

resultado - Resultado para cada jogador online. 0 Perdeu 1 Ganhou 3 Empate.

a_saldo_ini - Saldo, em euros, antes do inicio da aposta.

a_valor - Valor da aposta, em euros.

a_saldo_fim - Saldo, em euros, depois do fecho de aposta.

a_bonus_ini - Bónus do jogador online, em euros, antes do inicio da aposta.

a_bonus - Bónus da aposta, em euros.

a_bonus_fim - Bónus do jogador online, em euros, depois do fecho de aposta.

a_comissao - Comissão de aposta da entidade exploradora ou operador jogo online.

g_saldo_ini - Valor do saldo, em euros, antes do ganho de aposta.

g_ganho - Valor ganho, em euros, com a aposta.

g_saldo_fim - Valor do saldo, em euros, após ganho de aposta.

r_saldo_ini - Valor do saldo, em euros, antes do reembolso de aposta.

r_valor - Valor do reembolso, em euros.

r_saldo_fim - Valor do saldo, em euros, depois do reembolso de aposta.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador de jogador online na entidade exploradora.

logon - Username do jogador na entidade exploradora.

codigo - Código da conta de jogo do jogador na entidade exploradora ou operador de jogo online.

saldo_ini - Saldo inicial, em euros, da conta de jogo online.

saldo_mov - Saldo movimentado, em euros, na conta de jogo online.

saldo_final - Saldo atual, em euros, da conta de jogo online.

bonus_ini - Bónus inicial, em euros, na conta de jogo online.

bonus_mov - Bónus movimentado, em euros, na conta de jogo online.

bonus_final - Bónus atual, em euros, na conta de jogador online.

pinscr_ini - Saldo inicial, em euros, da conta de jogo online antes do pagamento dos prémios de inscrição.

pinscr_mov - Saldo movimentado, em euros, na conta de jogo online para pagamento dos prémios de inscrição.

pinscr_final - Saldo atual, em euros, da conta de jogo online depois do pagamento dos prémios de inscrição.

cod_ficha - Código externo de ficha de jogo, aposta online.

cod_aptr_jog - Código de aposta para utilização da entidade exploradora ou operador de jogo online.

timestp_ini - Ficha de jogo. Inicio da aposta, jogo online. Formato: YYYYMMDDHHMMSS

timestp_fim - Ficha de jogo. Fim da aposta, jogo online. Formato: YYYYMMDDHHMMSS

dathr_ini_evento - Datahora de inicio do evento. Formato: YYYYMMDDHH.

dathr_fim_evento - Datahora de fim do evento. Formato: YYYYMMDDHH.

ap_cruz - Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada.

cod_fichajog - Código externo de ficha de jogador atribuído pela entidade exploradora ou operador de jogo online.

id_sessao - Identificador de sessão de entrada no operador.

ip_jogador - IP da maquina do jogador online.

ip_regiao - Região do IP da maquina do jogador online.

cod_opejog - Código externo de operação de jogo, aposta online.

timestp - Timestamp da operação de jogo, aposta online. Formato: YYYYMMDDHHMMSS

id_inscricao - Identificador da inscrição do jogador.

id_partida - Identificador de partida de jogo.

descr - Descritivo do torneio, partida.

id_mesa - Identificador da mesa de jogo.

njog_max - Numero máximo de jogadores.

cartas_p - Lista de cartas existentes no ponto, separadas por hifen.

cartas_b - Lista de cartas existentes na banca, separadas por hifen.

a_local - Local de aposta. 4 Ponto 3 Empate 5 Banca diferencial - Diferencial aplicado pela mesa de jogo. Apenas Ponto e Banca Macau.

pontuacao_p - Pontuação ponto.

pontuacao_b - Pontuação banca.

resultado - Resultado para cada jogador online. 4 Ponto 3 Empate 5 Banca a_saldo_ini - Saldo, em euros, antes do inicio da aposta.

a_valor - Valor da aposta, em euros.

a_saldo_fim - Saldo, em euros, depois do fecho de aposta.

a_bonus_ini - Bónus do jogador online, em euros, antes do inicio da aposta.

a_bonus - Bónus da aposta, em euros.

a_bonus_fim - Bónus do jogador online, em euros, depois do fecho de aposta.

a_comissao - Comissão de aposta da entidade exploradora ou operador jogo online.

g_saldo_ini - Valor do saldo, em euros, antes do ganho de aposta.

g_ganho - Valor ganho, em euros, com a aposta.

g_saldo_fim - Valor do saldo, em euros, após ganho de aposta.

r_saldo_ini - Valor do saldo, em euros, antes do reembolso de aposta.

r_valor - Valor do reembolso, em euros.

r_saldo_fim - Valor do saldo, em euros, depois do reembolso de aposta.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador de jogador online na entidade exploradora.

logon - Username do jogador na entidade exploradora.

codigo - Código da conta de jogo do jogador na entidade exploradora ou operador de jogo online.

saldo_ini - Saldo inicial, em euros, da conta de jogo online.

saldo_mov - Saldo movimentado, em euros, na conta de jogo online.

saldo_final - Saldo atual, em euros, da conta de jogo online.

bonus_ini - Bónus inicial, em euros, na conta de jogo online.

bonus_mov - Bónus movimentado, em euros, na conta de jogo online.

bonus_final - Bónus atual, em euros, na conta de jogador online.

pinscr_ini - Saldo inicial, em euros, da conta de jogo online antes do pagamento dos prémios de inscrição.

pinscr_mov - Saldo movimentado, em euros, na conta de jogo online para pagamento dos prémios de inscrição.

pinscr_final - Saldo atual, em euros, da conta de jogo online depois do pagamento dos prémios de inscrição.

cod_fichjog - Código externo de ficha de jogo, aposta online.

cod_aptr_jog - Código de aposta para utilização da entidade exploradora ou operador de jogo online.

ap_cruz - Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada.

timestp_ini - Ficha de jogo. Inicio da aposta, jogo online. Formato: YYYYMMDDHHMMSS

timestp_fim - Ficha de jogo. Fim da aposta, jogo online. Formato: YYYYMMDDHHMMSS

dathr_ini_evento - Datahora de inicio do evento. Formato: YYYYMMDDHH.

dathr_fim_evento - Datahora de fim do evento. Formato: YYYYMMDDHH.

cod_fichajog - Código externo de ficha de jogador atribuido pela entidade exploradora ou operador de jogo online.

id_sessao - Identificador de sessão de entrada no operador.

ip_jogador - IP da maquina do jogador online.

ip_regiao - Região do IP da maquina do jogador online.

cod_opejog - Código externo de operação de jogo, aposta online.

timestp - Timestamp da operação de jogo, aposta online. Formato: YYYYMMDDHHMMSS

id_inscricao - Identificador da inscrição do jogador.

id_partida - Identificador de partida de jogo.

descr - Descritivo do torneio, partida.

torneio - Identifica se a operação se enquadra num torneio ou não. S sim, N não.

id_mesa - Identificador da mesa de jogo.

njog_min - Numero mínimo de jogadores.

njog_max - Numero máximo de jogadores.

comp_oper - Comparticipação da entidade exploradora ou operador de jogo online na partida, jogo de poker.

buyin - Buy in.

buyin_pool - Buy in pool.

a_lim_min - Limite mínimo de aposta do jogador online.

a_lim_max - Limite máximo de aposta do jogador online.

nr_creditos - Numero de fichas de jogo.

marca_jog - Jogador online que tem a mão ou botão. S tem ou botão, N não tem o botão cartas_m - Lista de cartas existentes na mesa, separadas por hífen.

cartas_j - Lista de cartas do jogador online, separadas por hífen.

posicao_mesa - Lugar do jogador na mesa de jogo.

resultado - Resultado para cada jogador online. 0 Perdeu 1 Ganhou 2 All In a_saldo_ini - Saldo, em euros, antes do inicio da aposta.

a_valor - Valor da aposta, em euros.

a_saldo_fim - Saldo, em euros, depois do fecho de aposta.

a_bonus_ini - Bónus do jogador online, em euros, antes do inicio da aposta.

a_bonus - Bónus da aposta, em euros.

a_bonus_fim - Bónus do jogador online, em euros, depois do fecho de aposta.

a_comissao - Comissão de aposta da entidade exploradora ou operador jogo online.

g_saldo_ini - Valor do saldo, em euros, antes do ganho de aposta.

g_ganho - Valor ganho, em euros, com a aposta.

g_saldo_fim - Valor do saldo, em euros, após ganho de aposta.

r_saldo_ini - Valor do saldo, em euros, antes do reembolso de aposta.

r_valor - Valor do reembolso, em euros.

r_saldo_fim - Valor do saldo, em euros, depois do reembolso de aposta.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador de jogador online na entidade exploradora.

logon - Username do jogador na entidade exploradora.

codigo - Código da conta de jogo do jogador na entidade exploradora ou operador de jogo online.

saldo_ini - Saldo inicial, em euros, da conta de jogo online.

saldo_mov - Saldo movimentado, em euros, na conta de jogo online.

saldo_final - Saldo atual, em euros, da conta de jogo online.

bonus_ini - Bónus inicial, em euros, na conta de jogo online.

bonus_mov - Bónus movimentado, em euros, na conta de jogo online.

bonus_final - Bónus atual, em euros, na conta de jogador online.

pinscr_ini - Saldo inicial, em euros, da conta de jogo online antes do pagamento dos prémios de inscrição.

pinscr_mov - Saldo movimentado, em euros, na conta de jogo online para pagamento dos prémios de inscrição.

pinscr_final - Saldo atual, em euros, da conta de jogo online depois do pagamento dos prémios de inscrição.

cod_ficha = Codigo externo de ficha de jogo, aposta online.

cod_aptr_jog = Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online.

ap_cruz = Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada.

timestp_ini = Ficha de jogo. Inicio da aposta, jogo online. Formato: YYYYMMDDHHMMSS

timestp_fim = Ficha de jogo. Fim da aposta, jogo online. Formato: YYYYMMDDHHMMSS

dathr_ini_evento = Datahora de inicio do evento. Formato: YYYYMMDDHHMMSS

dathr_fim_evento = Datahora de fim do evento. Formato: YYYYMMDDHHMMSS

cod_fichajog = Codigo externo de ficha de jogador atribuido pela entidade exploradora ou operador de jogo online.

id_sessao = Identificador de sessao de entrada no operador.

ip_jogador = IP da maquina do jogador online.

ip_regiao = Regiao do IP da maquina do jogador online.

cod_opejog = Codigo externo de operacao de jogo, aposta online.

timestp = Timestamp da operacao de jogo, aposta online. Formato: YYYYMMDDHHMMSS

descr_ap = Descritivo da aposta.

ro_result_nr = Resultado da aposta roleta numero.

ro_result_cor = Resultado roleta cor. V vermelho, P preto.

sm_result = Resultado da aposta slot machine.

bin_cartao = Lista de numeros do cartao de jogador de bingo separados por hifen.

bin_result = Resultado da aposta bingo.

a_saldo_ini - Saldo, em euros, antes do inicio da aposta.

a_valor - Valor da aposta, em euros.

a_saldo_fim - Saldo, em euros, depois do fecho de aposta.

a_bonus_ini - Bónus do jogador online, em euros, antes do inicio da aposta.

a_bonus - Bónus da aposta, em euros.

a_bonus_fim - Bónus do jogador online, em euros, depois do fecho de aposta.

a_comissao - Comissão de aposta da entidade exploradora ou operador jogo online.

g_saldo_ini - Valor do saldo, em euros, antes do ganho de aposta.

g_ganho - Valor ganho, em euros, com a aposta.

g_saldo_fim - Valor do saldo, em euros, após ganho de aposta.

r_saldo_ini - Valor do saldo, em euros, antes do reembolso de aposta.

r_valor - Valor do reembolso, em euros.

r_saldo_fim - Valor do saldo, em euros, depois do reembolso de aposta.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador de jogador online na entidade exploradora.

logon - Username do jogador na entidade exploradora.

codigo - Código da conta de jogo do jogador na entidade exploradora ou operador de jogo online.

saldo_ini - Saldo inicial, em euros, da conta de jogo online.

saldo_mov - Saldo movimentado, em euros, na conta de jogo online.

saldo_final - Saldo atual, em euros, da conta de jogo online.

bonus_ini - Bónus inicial, em euros, na conta de jogo online.

bonus_mov - Bónus movimentado, em euros, na conta de jogo online.

bonus_final - Bónus atual, em euros, na conta de jogador online.

pinscr_ini - Saldo inicial, em euros, da conta de jogo online antes do pagamento dos prémios de inscrição.

pinscr_mov - Saldo movimentado, em euros, na conta de jogo online para pagamento dos prémios de inscrição.

pinscr_final - Saldo atual, em euros, da conta de jogo online depois do pagamento dos prémios de inscrição.

cod_ficha - Codigo externo de ficha de jogo, aposta online.

cod_aptr_jog - Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online.

timestp_ini - Ficha de jogo. Inicio da aposta, jogo online. Formato: YYYYMMDDHHMMSS

timestp_fim - Ficha de jogo. Fim da aposta, jogo online. Formato: YYYYMMDDHHMMSS

dathr_ini_evento - Data/hora de inicio do evento. Formato: YYYYMMDDHHMMSS

dathr_fim_evento - Data/hora de fim do evento. Formato: YYYYMMDDHHMMSS

ap_cruz - Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada.

cod_fichajog - Codigo externo de ficha de jogador atribuido pela entidade exploradora ou operador de jogo online.

id_sessao - Identificador de sessao de entrada no operador.

ip_jogador - IP da maquina do jogador online.

ip_regiao - Regiao do IP da maquina do jogador online.

cod_opejog - Codigo externo de operacao de jogo, aposta online.

timestp - Timestamp da operacao de jogo, aposta online. Formato: YYYYMMDDHHMMSS

descr_ap - Descritivo do torneio, partida.

combinado - Identifica se a aposta e combinada ou nao. Mais do que um evento. S sim, N nao.

multipla - Identifica se a aposta e multipla ou nao. Mais do que um resultado. S sim, N nao.

cota_ap - Cota total da aposta desportiva.

resultado - Resultado da aposta desportiva.

a_saldo_ini - Saldo, em euros, antes do inicio da aposta.

a_valor - Valor da aposta, em euros.

a_saldo_fim - Saldo, em euros, depois do fecho de aposta.

a_bonus_ini - Bónus do jogador online, em euros, antes do inicio da aposta.

a_bonus - Bónus da aposta, em euros.

a_bonus_fim - Bónus do jogador online, em euros, depois do fecho de aposta.

a_comissao - Comissão de aposta da entidade exploradora ou operador jogo online.

g_saldo_ini - Valor do saldo, em euros, antes do ganho de aposta.

g_ganho - Valor ganho, em euros, com a aposta.

g_saldo_fim - Valor do saldo, em euros, após ganho de aposta.

r_saldo_ini - Valor do saldo, em euros, antes do reembolso de aposta.

r_valor - Valor do reembolso, em euros.

r_saldo_fim - Valor do saldo, em euros, depois do reembolso de aposta.

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador de jogador online na entidade exploradora.

logon - Username do jogador na entidade exploradora.

codigo - Código da conta de jogo do jogador na entidade exploradora ou operador de jogo online.

saldo_ini - Saldo inicial, em euros, da conta de jogo online.

saldo_mov - Saldo movimentado, em euros, na conta de jogo online.

saldo_final - Saldo atual, em euros, da conta de jogo online.

bonus_ini - Bónus inicial, em euros, na conta de jogo online.

bonus_mov - Bónus movimentado, em euros, na conta de jogo online.

bonus_final - Bónus atual, em euros, na conta de jogador online.

pinscr_ini - Saldo inicial, em euros, da conta de jogo online antes do pagamento dos prémios de inscrição.

pinscr_mov - Saldo movimentado, em euros, na conta de jogo online para pagamento dos prémios de inscrição.

pinscr_final - Saldo atual, em euros, da conta de jogo online depois do pagamento dos prémios de inscrição.

cod_ficha - Código externo de ficha de jogo, aposta online.

cod_aptr_jog - Código de aposta para utilização da entidade exploradora ou operador de jogo online.

ap_cruz - Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada.

timestp_ini - Ficha de jogo. Inicio da aposta, jogo online. Formato: YYYYMMDDHHMMSS

timestp_fim - Ficha de jogo. Fim da aposta, jogo online. Formato: YYYYMMDDHHMMSS

dathr_ini_evento - Datahora de inicio do evento. Formato: YYYYMMDDHHMMSS

dathr_fim_evento - Datahora de fim do evento. Formato: YYYYMMDDHHMMSS

cod_fichajog - Código externo de ficha de jogador atribuído pela entidade exploradora ou operador de jogo online.

id_sessao - Identificador de sessão de entrada no operador.

ip_jogador - IP da maquina do jogador online.

ip_regiao - Região do IP da maquina do jogador online.

cod_opejog - Código externo de operação de jogo, aposta online.

timestp - Timestamp da operação de jogo, aposta online. Formato: YYYYMMDDHHMMSS

descr_ap - Descritivo do torneio, partida.

cota - Cota da aposta hípica.

mutua - Identifica se a aposta e mutua ou não. S - Sim, N - Não.

resultado - Resultado da aposta hípica.

a_saldo_ini - Saldo, em euros, antes do inicio da aposta.

a_valor - Valor da aposta, em euros.

a_saldo_fim - Saldo, em euros, depois do fecho de aposta.

a_bonus_ini - Bónus do jogador online, em euros, antes do inicio da aposta.

a_bonus - Bónus da aposta, em euros.

a_bonus_fim - Bónus do jogador online, em euros, depois do fecho de aposta.

a_comissao - Comissão de aposta da entidade exploradora ou operador jogo online.

g_saldo_ini - Valor do saldo, em euros, antes do ganho de aposta.

g_ganho - Valor ganho, em euros, com a aposta.

g_saldo_fim - Valor do saldo, em euros, após ganho de aposta.

r_saldo_ini - Valor do saldo, em euros, antes do reembolso de aposta.

r_valor - Valor do reembolso, em euros.

r_saldo_fim - Valor do saldo, em euros, depois do reembolso de aposta.

V.5 Schema TRAN_

Esta categoria inclui o registo das transações registadas na conta do jogador no sistema técnico de jogo. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMAL TRAN_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSED TRAN_YYYYMMDDHH24_[GameVault _code]rp.xml

Example: TRAN_2015040214_2AA.xml

XSD Schema

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data/hora de produção do ficheiro de dados XML. Formato: YYYYMMDDHH.

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

codjogador - Identificador único de jogador online na entidade exploradora.

cod_conta - Código da conta de jogo do jogador na entidade exploradora ou operador de jogo online.

cod_optct - Tipo de transação financeira entre conta bancaria do jog. e conta da ent. exploradora de jogo online. DEBITO ou CREDITO

timestp_op - Timestamp de realização da operação. Formato: YYYYMMDDHHMMSS

saldo_ini - Saldo inicial da conta do jogador na entidade exploradora ou operador de jogo online antes da operação.

saldo_mov - Saldo movimentado na conta do jogador na entidade exploradora ou operador de jogo online durante a operação.

saldo_fim - Saldo final da conta do jogador na entidade exploradora ou operador de jogo online apos a operação.

V.6 Schema EXCL_

Esta categoria deve incluir informação sobre os pedidos de autoexclusão registados no sistema técnico de jogo. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMAL EXCL_YYYYMMDD_[GameVault _code].xml

REPROCESSED EXCL_YYYYMMDD_[GameVault _code]rp.xml

Example: EXCL_20150405_1AA.xml

XSD Schema

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2018/02/029000000/0463904654.pdf)

Comentário aos Elementos/Atributos

cod_expljog - Código externo da entidade exploradora ou operador de jogo online.

datahr - Data de produção do ficheiro de dados XML. Formato: YYYYMMDD

id_ficheiro - Identificador do ficheiro XML proveniente da entidade exploradora ou operador de jogo online. Único para cada dia/hora.

cod_cofre - Código externo de cofre de dados do jogo online.

IdTipoCid - ID do tipo de identificador de cidadão. 0 BI, 1 CARTAO CIDADAO, 2 PASSAPORTE, 3 NUMERO IDENTIFIC FISCAL, 4 OUTRO.

IdCidadao - Identificador de cidadão auto excluído.

Nome - Nome completo do cidadão autoexcluído.

IdNacao - Código alpha-2 ISO3166 da nacionalidade do cidadão auto excluído.

SitProfissional - Identificador de situação profissional de cidadão auto excluído.

Morada - Morada de residência do cidadão auto excluído.

CodPostal - Código postal da morada de residência do cidadão auto excluído.

Distrito - Nome do distrito de residência do cidadão autoexcluído.

Email - Endereço eletrónico do cidadão auto excluído.

Duracao - Número de meses de autoexclusão.

Motivo - Motivo de auto exclusão do jogo online.

DataInicio - Data de início do período de auto exclusão do jogo online. YYYYMMDDHHMMSS.

TipoDoc - Tipo de documento enviado pelo cidadão auto excluído. B Bilhete de Identidade, C Cartão Cidadão, P Passaporte

DocFrente - Imagem da frente de documento enviado por cidadão auto excluído.

DocVerso - Imagem do verso de documento enviado por cidadão auto excluído.

Motivo - Motivo de auto exclusão do jogo online.

CodAcao - Código da alteração de estado da conta do Jogador.

CodigoEstado - Estado da conta do Jogador.

* Este atributo deverá ser preenchido com a situação profissional e base na seguinte lista de códigos:

11 Trabalhador por conta própria

22 Trabalhador por conta de outrem

33 Profissional liberal

44 Estudante

55 Reformado

66 Estagiário

77 Sem atividade profissional

88 Desempregado

99 Outra

** A duração da auto-exclusão equivale ao número de meses. O atributo data_fim é calculado usando os atributos data_ini e duracao.

*** Imagem - Códigos HEX binários.

24 de janeiro de 2018. - A Vice-Presidente do Conselho Diretivo, Maria Teresa Rodrigues Monteiro.

311083816
