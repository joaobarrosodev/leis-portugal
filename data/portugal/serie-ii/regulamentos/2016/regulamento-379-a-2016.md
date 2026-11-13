---
schema_version: '1.0'
id: pt:dre:74146384:por
title: Regulamento n.º 379-A/2016
short_title: null
summary: Altera o Anexo I do Regulamento n.º 903-B/2015 que define os Requisitos Técnicos do Sistema Técnico do Jogo Online,
  publicado no Diário da República, 2.ª série, n.º 250, de 23 de dezembro de 2015
jurisdiction: portugal
territory: null
document_type: regulamento
document_type_label: Regulamento
issuing_authority:
- Economia - Instituto do Turismo de Portugal, I. P.
proposing_entity: null
official_number: 379-A/2016
official_date: null
publication_date: '2016-04-13'
publication:
  gazette: Diário da República
  reference: Diário da República n.º 72/2016, 2º Suplemento, Série II de 2016-04-13
  number: '72'
  series: II
  supplement: null
  pages: 12164-(5) a 12164-(21)
  pdf_url: https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf
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
  dre: '74146384'
  dre_path: /dr/detalhe/regulamento/379-a-2016-74146384
  internal: pt:dre:74146384:por
source:
  id: dre
  name: Diário da República Eletrónico
  official_url: https://diariodarepublica.pt/dr/detalhe/regulamento/379-a-2016-74146384
  metadata_url: null
  content_url: https://diariodarepublica.pt/dr/detalhe/regulamento/379-a-2016-74146384
  consolidated_url: null
  retrieved_at: '2026-11-13T06:06:03Z'
  retrieval_method: Endpoints screenservices (OutSystems) da aplicação web do DRE; não é uma API pública documentada
  source_modified_at: null
integrity:
  source_sha256: 895a931d0432812074b67b28042ac20959b67c3ff382488d47eaf35bffecbf7e
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal DRE
  collector_version: 0.1.0
  generated_by: leis-portugal collect dre
  generated_at: '2026-11-13T06:06:03Z'
  notes: null
reuse:
  status: permitted
  attribution: Diário da República Eletrónico — Imprensa Nacional-Casa da Moeda
  reference: http://data.dre.pt/eli/dec-lei/83/2016/p/dr/pt/html
  notes: Acesso universal e gratuito ao Diário da República (artigo 3.º do Decreto-Lei n.º 83/2016) e regime de dados abertos
    (Lei n.º 68/2021). A edição eletrónica do DR é a que faz fé.
subjects:
- Especificação Técnica
- Inspecção Geral de Jogos
- Jogos de Fortuna e Azar
- Jogos e Apostas Online
- Normas de Segurança
- Regulamento
- Segurança da Informação
relationships:
- type: amended_by
  target: pt:dre:114657935:por
  label: Alterado o Anexo I do Regulamento 903-B/2015, de 23-dez, na redação do presente regulamento pelo(a) Regulamento n.º
    99/2018 - Diário da República n.º 29/2018, Série II de 2018-02-09
  source: https://diariodarepublica.pt/dr/analise-juridica/informacoes-gerais/regulamento/99-2018-114657935
  date: '2018-02-09'
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
article_structure:
  article_count: 0
  section_count: 0
  extraction_method: Classes de parágrafo do TextoFormatado do DRE
derived_material:
  machine_generated: true
  notes: Markdown convertido do HTML TextoFormatado do DRE; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-11-13T06:06:03Z'
  warnings: []
  errors: []
---

# Regulamento n.º 379-A/2016

Altera o Anexo I do [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679) que define os Requisitos Técnicos do Sistema Técnico do Jogo Online, publicado no Diário da República, 2ª série, n.º 250, de 23 de dezembro de 2015.

Através do [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679), publicado no Diário da República, 2.ª série, n.º 250, de 23 de dezembro de 2015, a Comissão de Jogos aprovou os requisitos técnicos do sistema técnico do jogo online.

Constatou-se, porém, que, por um lado, o anexo ao regulamento foi publicado com algumas inexatidões e, por outro, que se afigura necessário proceder a algumas retificações e alterações de mero pormenor.

Assim, é retificado em todo o anexo as inexatidões do formato dia hora de "YYYYMMDD HH24MISS" para "YYYYMMDDHH24MISS".

Por outro lado, procede-se a alterações nos SERVIÇOS DE JOGADORES, II. SERVIÇOS DE VERIFICAÇÃO DE IDENTIDADE DO JOGADOR onde são modificados no processo de validação de identidade do SRIJ a estrutura dos diagramas de PedidoVerificaçãoTP e de RespostaVerificaçãoTP e os principais elementos da estrutura de pedido e resposta do serviço PedidoVerificaçãoTP e RespostaVerificacaoTP.

Na CRIAÇÃO SISTEMÁTICA DE REPORTES, II. ESPECIFICAÇÃO DOS TIPOS DE RECOLHA DE DADOS é modificada a categorias de dados V.1 Schema RESF_ e nesta bem como nas categorias de dados V.2 Schema JGDR_, V.3 Schema SESS_, V.4 Schema AJOG_ e V.5 Schema TRAN_ no XSD Schema são alterados os comandos da estrutura XML de «xs:element name="id_ficheiro" type="xs:short" /» para «xs:element name="id_ficheiro" type="xs:int" e ainda na tabela SCHEMA:AJOG dos diversos jogos e apostas as regras de mapeamento para o modelo de dados da entidade exploradora é aumentado o tamanho dos atributos cod_aptr_jog e cod_opejog de varchar2(6) para varchar2(22) e no Schema:AJOG_«fortazar» é alterado o tamanho do atributo sm_result de VARCHAR2 (50) para VARCHAR2 (1000).

Finalmente, procede-se à alteração da estrutura do XSD Schema do V.1 Schema RESF_ para ajustar o formato definido para a organização dos dados ao tipo de estrutura pretendida para os requisitos do reporte de informação.

Considerando que o [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679) foi disponibilizado no sítio da Internet do Serviço de Regulamentação e Inspeção de Jogos para consulta pública e que as alterações agora introduzidas não modificam substancial ou materialmente os requisitos técnicos definidos naquele Regulamento, não se submeteu a presente alteração a audiência ou consulta pública.

Assim, ao abrigo das disposições conjugadas do n.º 3 do artigo 35.º e do artigo 48.º do Regime Jurídico dos Jogos e Apostas Online (RJO), aprovado em anexo ao [Decreto-Lei n.º 66/2015](https://diariodarepublica.pt/dr/detalhe/decreto-lei/66-2015-67098359), de 29 de abril, com a alínea b) e m) do n.º 3 do artigo 7.º do [Decreto-Lei n.º 129/2012](https://diariodarepublica.pt/dr/detalhe/decreto-lei/129-2012-178510), de 22 de junho, na redação dada pelo [Decreto-Lei n.º 66/2015](https://diariodarepublica.pt/dr/detalhe/decreto-lei/66-2015-67098359), de 29 de abril, a Comissão de Jogos, na reunião de 10 de março de 2016, deliberou:

1 - É alterado o Anexo I do [Regulamento n.º 903-B/2015](https://diariodarepublica.pt/dr/detalhe/regulamento/903-b-2015-72964679), que define os requisitos técnicos do sistema técnico do jogo online, publicado no Diário da República, 2.ª série, n.º 250, de 23 de dezembro de 2015, de acordo com o Anexo ao presente regulamento, que dele faz parte integrante.

2 - O presente regulamento entra em vigor no dia seguinte ao da sua publicação.

12 de abril de 2016. - A Vice-Presidente do Conselho Diretivo, Maria Teresa Rodrigues Monteiro.

ANEXO

Informação Técnica para entidades exploradoras de jogo online

SERVIÇOS DE JOGADORES

A funcionalidade Serviços de Jogadores é considerada parte do Sistema técnico de jogo, aceitando-se por isso que esta funcionalidade possa ser implementada na infraestrutura da entidade exploradora.

No âmbito dos serviços de jogadores, as entidades exploradoras devem interagir com a infraestrutura de controlo Serviço de Regulação e Inspeção de Jogos (SRIJ) através de dois tipos de serviços de dados

I - SERVIÇO DE AUTOEXCLUSÃO DE JOGADORES

As funcionalidades garantidas pelo presente serviço são

. Notificações de autoexclusão de jogadores

- As entidades exploradoras devem enviar ao SRIJ, num prazo máximo de 24 horas desde a receção do pedido, os dados dos jogadores que solicitam a sua autoexclusão ou que alterem ou revoguem um pedido anterior de autoexclusão.

- Notificações de alterações à base de jogadores autoexcluídos do SRIJ (onde é mantido o registo dos jogadores que solicitaram autoexclusão na página do SRIJ) serão enviadas a todas as entidades exploradoras em tempo real.

- As entidades exploradoras devem garantir a reação adequada às notificações mencionadas no ponto anterior e proceder à recolha da última versão da lista de jogadores autoexcluídos.

. Recolha da última versão da lista de jogadores autoexcluídos

- A entidade exploradora deve proceder ao download da última versão da lista de jogadores autoexcluídos transmitida pelo SRIJ.

A caracterização técnica e funcional deste serviço podem ser aferidas nos seguintes pontos:

1 - Transferência da lista de jogadores autoexcluídos da entidade exploradora

As entidades exploradoras devem garantir diariamente a preparação de um ficheiro XML com uma lista (correspondente a 24 horas) dos jogadores autoexcluídos no seu sistema técnico de jogo, comprimi-lo, encriptá-lo e em seguida depositá-lo no seu Safe, no sub diretório:

/u01/app/oracle/mftxfer/[GameVault Code]/in/excl

Um processo dedicado de gestão de transferência de ficheiros iniciará a operação de transferência do ficheiro XML para a infraestrutura de controlo do SRIJ logo que detete a existência de novos dados dentro do filesystem em questão. A estrutura deste ficheiro encontra-se descrita no anexo sub capítulo V.6 Schema EXCL_.

O processo de encriptação do ficheiro encontra-se descrito no sub capítulo "processo de encriptação de ficheiros de dados".

2 - Recolha da lista de jogadores autoexcluídos do SRIJ

As entidades exploradoras devem invocar periodicamente o WebService ListaExcluidos para proceder à recolha da lista de jogadores autoexcluídos do SRIJ. Em seguida detalhar-se-á o WSDL correspondente a esse serviço:

«?xml version= '1.0' encoding= 'UTF-8' ?»

«wsdl:definitions

name="ListaExcluidos" targetNamespace="http://www.turismodeportugal.pt/ListaExcluidos/ListaExcluidos"

xmlns:tns="http://www.turismodeportugal.pt/ListaExcluidos/ListaExcluidos"

xmlns:inp1="http://www.turismodeportugal.pt/SRJSchema/ListaExcluidos"

xmlns:xsd="http://www.w3.org/2001/XMLSchema"

xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"

xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"

»

«wsdl:types»

«xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"»

«xsd:import namespace="http://www.turismodeportugal.pt/SRJSchema/ListaExcluidos" schemaLocation="../xsd/SRJJogoOnlineListaExcluidos.xsd"/»

«/xsd:schema»

«/wsdl:types»

«wsdl:message name="requestMessage"»

«wsdl:part name="part" element="inp1:PedidoListaExcluidos"/»

«/wsdl:message»

«wsdl:message name="replyMessage"»

«wsdl:part name="part" element="inp1:RespostaListaExcluidos"/»

«/wsdl:message»

«wsdl:portType name="listaexcluidos_ptt"»

«wsdl:operation name="getlistaexcluidos"»

«wsdl:input message="tns:requestMessage"/»

«wsdl:output message="tns:replyMessage"/»

«/wsdl:operation»

«/wsdl:portType»

«wsdl:binding name="listaexcluidos_bind" type="tns:listaexcluidos_ptt"«

«soap:binding transport="http://schemas.xmlsoap.org/soap/http"/»

«wsdl:operation name="getlistaexcluidos"»

«soap:operation style="document" soapAction="getlistaexcluidos"/»

«wsdl:input»

«soap:body use="literal" namespace="http://www.turismodeportugal.pt/ListaExcluidos/ListaExcluidos"/»

«/wsdl:input»

«wsdl:output»

«soap:body use="literal" namespace="http://www.turismodeportugal.pt/ListaExcluidos/ListaExcluidos"/»

«/wsdl:output»

«/wsdl:operation»

«/wsdl:binding»

«/wsdl:definitions»

Os dados devem ser enviados na forma de uma estrutura de XML. Em seguida detalhar-se-á o XSD correspondente:

«?xml version="1.0" encoding="windows-1252" ?»

«xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"

xmlns:srjlex="http://www.turismodeportugal.pt/SRJSchema/ListaExcluidos" targetNamespace="http://www.turismodeportugal.pt/SRJSchema/ListaExcluidos" elementFormDefault="qualified"»

«xsd:element name="PedidoListaExcluidos" type="srjlex:PedidoListaExcluidosType"/»

«xsd:element name="RespostaListaExcluidos" type="srjlex:ListaCidadaoExcluidoType"«

«xsd:annotation»

«xsd:documentation»A sample element«/xsd:documentation»

«/xsd:annotation»

«/xsd:element»

«xsd:complexType name="ListaCidadaoExcluidoType"»

«xsd:sequence»

«xsd:element name="Sucesso" type="xsd:boolean"/»

«xsd:element name="ListaCidadaoExcludo" minOccurs="0"»

«xsd:complexType»

«xsd:sequence»

«xsd:element name="CidadaoExcluido" type="srjlex:CidadaoExcluidoType" minOccurs="1"/»

«/xsd:sequence»

«/xsd:complexType»

«/xsd:element»

«xsd:element name="MensagemErro" minOccurs="0" maxOccurs="1" type="xsd:string"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="CidadaoExcluidoType"»

«xsd:sequence»

«xsd:element name="IdTipoCid" type="srjlex:int1"/»

«xsd:element name="IdCidadao" type="srjlex:string20"/»

«xsd:element name="IdNacao" type="srjlex:string2"/»

«xsd:element name="DataInicio" type="xsd:date"/»

«xsd:element name="DataFim" type="xsd:date"/»

«xsd:element name="Confirmado"»

«xsd:simpleType»

«xsd:restriction»

«xsd:simpleType»

«xsd:list itemType="xsd:string"/»

«/xsd:simpleType»

«xsd:enumeration value="S"/»

«xsd:enumeration value="N"/»

«/xsd:restriction»

«/xsd:simpleType»

«/xsd:element»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="PedidoListaExcluidosType"»

«xsd:sequence»

«xsd:element name="CodEntidadeExploradora" type="srjlex:string3"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:simpleType name="string20"»

«xsd:restriction base="xsd:string"»

«xsd:maxLength value="20"/»

«/xsd:restriction»

«/xsd:simpleType»

«xsd:simpleType name="string3"»

«xsd:restriction base="xsd:string"»

«xsd:length value="3"/»

«/xsd:restriction»

«/xsd:simpleType»

«xsd:simpleType name="string2"»

«xsd:restriction base="xsd:string"»

«xsd:maxLength value="2"/»

«/xsd:restriction»

«/xsd:simpleType»

«xsd:simpleType name="int1"»

«xsd:restriction base="xsd:int"»

«xsd:totalDigits value="1"/»

«/xsd:restriction»

«/xsd:simpleType»

«/xsd:schema»

3 - Recolha (Inflow) das notificações de alteração de estado de jogadores autoexcluídos na lista do SRIJ

Sempre que se registe alguma alteração ao estado dos jogadores da lista de autoexcluídos do SRIJ, as entidades exploradoras serão imediatamente notificadas. O serviço designado "NotificacaoPedidoExclusao" faz o envio da informação para o sistema técnico de jogo de todas as entidades exploradoras utilizando a estrutura que se detalha em seguida:

«?xml version="1.0" encoding="windows-1252" ?»

«xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"

xmlns:srjnpe="http://www.turismodeportugal.pt/SRJSchema/NotificacaoPedidoExclusao"

targetNamespace="http://www.turismodeportugal.pt/SRJSchema/NotificacaoPedidoExclusao"

elementFormDefault="qualified"»

«xsd:element name="NotificacaoPedidoExclusao" type="srjnpe:NotificacaoPedidoExclusaoType"»

«xsd:annotation»

«xsd:documentation»A sample element«/xsd:documentation»

«/xsd:annotation»

«/xsd:element»

«xsd:element name="RespostaNotificacaoPedidoExclusao"

type="srjnpe:RespostaNotificacaoPedidoExclusaoType"/»

«xsd:complexType name="NotificacaoPedidoExclusaoType"»

«xsd:sequence»

«xsd:element name="IdCidadao" type="srjnpe:string20"/»

«xsd:element name="IdTipoCid" type="srjnpe:int1"/»

«xsd:element name="IdNacao" type="srjnpe:string2"/»

«xsd:element name="DataInicio" type="xsd:date"/»

«xsd:element name="DataFim" type="xsd:date"/»

«xsd:element name="Confirmado"»

«xsd:simpleType»

«xsd:restriction»

«xsd:simpleType»

«xsd:list itemType="xsd:string"/»

«/xsd:simpleType»

«xsd:enumeration value="S"/»

«xsd:enumeration value="N"/»

«/xsd:restriction»

«/xsd:simpleType»

«/xsd:element»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="RespostaNotificacaoPedidoExclusaoType"»

«xsd:sequence»

«xsd:element name="Sucesso" type="xsd:boolean"/»

«xsd:element name="MensagemErro" type="xsd:string"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:simpleType name="string20"»

«xsd:restriction base="xsd:string"»

«xsd:maxLength value="20"/»

«/xsd:restriction»

«/xsd:simpleType»

«xsd:simpleType name="string2"»

«xsd:restriction base="xsd:string"»

«xsd:maxLength value="2"/»

«/xsd:restriction»

«/xsd:simpleType»

«xsd:simpleType name="int1"»

«xsd:restriction base="xsd:int"»

«xsd:totalDigits value="1"/»

«/xsd:restriction»

«/xsd:simpleType»

«/xsd:schema»

O sistema técnico de jogo das entidades exploradoras deve ser configurado de forma a cumprir todos os requisitos para garantir a comunicação com o WebService "NotificacaoPedidoExclusao".

II - SERVIÇO DE VERIFICAÇÃO DE IDENTIDADE DO JOGADOR

O sistema técnico de jogo das entidades exploradoras de jogo online deve, no âmbito do processo de registo dos jogadores, garantir a execução de uma validação da identidade dos jogadores.

A entidade exploradora validar deve verificar a identidade dos jogadores através dos seguintes métodos:

a) Diretamente no seu sistema técnico de jogo, através do cartão do cidadão ou da chave móvel digital.

b) Através da consulta em tempo real de uma base de dados de uma entidade pública, feita através de uma comunicação com o SRIJ.

Validação através do cartão de cidadão ou da chave móvel digital

A entidade exploradora deve garantir a utilização do mecanismo de registo de jogador autenticação.gov.pt (https://autenticacao.gov.pt/fa/Default.aspx) no seu sistema técnico de jogo, disponibilizado pela Agência para a Modernização Administrativa, IP (AMA I.P.).

No seguimento da emissão de cada licença de exploração de jogo online, o SRIJ irá enviar à AMA, I.P. a identificação da entidade exploradora licenciada, que deve por sua vez contactar esta agência e seguir os procedimentos necessários para integrar no processo de registo do seu sistema técnico de jogo um processo de validação baseado no serviço autenticação.gov.pt.

Este processo de verificação deve retornar ao sistema técnico de jogo da entidade exploradora informação relativamente ao nome, data de nascimento e número de identificação civil ligados ao cartão do cidadão ou da chave móvel digital utilizados no processo de registo de jogador.

Validação através do processo de validação de identidade do SRIJ

Com o objetivo de validar a informação ligada ao registo dos jogadores, o SRIJ irá mediar o acesso à base de dados de entidades públicas.

No âmbito do processo de validação da identidade do jogador, a entidade exploradora deve aceder, na infraestrutura de controlo do SRIJ, ao serviço PedidoVerificacaoIdentidadeTP.

Em seguida proceder-se-á à descrição detalhada do WSDL do serviço:

«wsdl:definitions name="PedidoVerificacaoIdentidade" targetNamespace=" http://www.turismodeportugal.pt/MediacaoRegisto/PedidoVerificacaoIdentidadeTP" xmlns:tns="http://www.turismodeportugal.pt/MediacaoRegisto/PedidoVerificacaoIdentidadeTP" xmlns:inp1="http://www.turismodeportugal.pt/SRJSchema/VerificacaoIdentidade" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://schemas.xmlsoap.org/wsdl/soap12/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"»

«wsdl:types»

«xsd:schema»

«xsd:import namespace="http://www.turismodeportugal.pt/SRJSchema/VerificacaoIdentidade" schemaLocation="../xsd/SRJJogoOnlineVerificacaoIdentidade.xsd"/»

«/xsd:schema»

«/wsdl:types»

«wsdl:message name="requestMessage"»

«wsdl:part name="part" element="inp1:PedidoVerificacaoTP"/»

«/wsdl:message»

«wsdl:message name="replyMessage"»

«wsdl:part name="part" element="inp1:RespostaVerificacaoTP"/»

«/wsdl:message»

«wsdl:portType name="verificacaoidentidade_ptt"»

«wsdl:operation name="verificacaoidentidade"»

«wsdl:input message="tns:requestMessage"/»

«wsdl:output message="tns:replyMessage"/»

«/wsdl:operation»

«/wsdl:portType»

«wsdl:binding name="verificacaoidentidade_bind" type="tns:verificacaoidentidade_ptt"»

«soap12:binding transport="http://www.w3.org/2003/05/soap/bindings/HTTP/"/»

«wsdl:operation name="verificacaoidentidade"»

«soap12:operation style="document" soapAction="verificacaoidentidade" soapActionRequired="false"/»

«wsdl:input»

«soap12:body use="literal" namespace="http://www.turismodeportugal.pt/MediacaoRegisto/PedidoVerificacaoIdentidadeTP"/»

«/wsdl:input»

«wsdl:output»

«soap12:body use="literal" namespace="http://www.turismodeportugal.pt/MediacaoRegisto/PedidoVerificacaoIdentidadeTP"/»

«/wsdl:output»

«/wsdl:operation»

«/wsdl:binding»

«/wsdl:definitions»

O diagrama subjacente ao pedido é apresentado de seguida:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

A estrutura de XML é composta por quatro elementos:

«Nome» Nome do jogador

«NumeroIdentificacao» Nº de identificação civil

«TipoIdentificacao» Cartão de Cidadão

«DataNascimento» Data de nascimento do jogador

A informação é processada na infraestrutura de controlo do SRIJ e enviada para os serviços da base de dados da entidade pública, recebendo em seguida informação relativa ao Número de identificação civil, Nome completo e data de nascimento remetidos. A validação do pedido vai garantir informação para a resposta das seguintes questões:

a) A data de nascimento que corresponde ao nº de identificação civil é válida?

b) O nome completo do cidadão que corresponde ao nº de identificação civil é válido?

c) O cidadão que corresponde ao nº de identificação civil enviado já faleceu?

d) Existe um cidadão registado com que o nº de identificação civil enviado?

A informação enviada pelo serviço da base de dados de entidade pública é depois reportada ao sistema técnico da entidade exploradora.

A resposta do serviço incluirá os seguintes elementos:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Os principais elementos da estrutura de resposta do serviço RespostaVerificacaoTP são:

«SUCESSO»

«VALIDO»

«CODIGOERRO»

«MENSAGEMERRO»

«DETALHEERRO»

A estrutura total de informação que é redirecionada pelo SRIJ para o sistema técnico de jogo da entidade exploradora encontra-se incluída no esquema de XSD que detalhamos de seguida e corresponde ao elemento "RespostaVerificacaoTP":

«?xml version="1.0" encoding="windows-1252" ?»

«xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"

xmlns:srjvid="http://www.turismodeportugal.pt/SRJSchema/VerificacaoIdentidade"

targetNamespace="http://www.turismodeportugal.pt/SRJSchema/VerificacaoIdentidade"

elementFormDefault="qualified"»

«xsd:element name="PedidoVerificacaoJogadorOnlineRegistado" type="srjvid:PedidoVerificacaoJogadorRegistadoType"/»«xsd:element name="RespostaVerificacaoJogadorOnlineRegistado" type="srjvid:RespostaVerificacaoJogadorRegistadoType"/»

«xsd:element name="PedidoVerificacaoTP" type="srjvid:PedidoVerificacaoTPType"»

«xsd:annotation»

«xsd:documentation»A sample element«/xsd:documentation»

«/xsd:annotation»

«/xsd:element»

«xsd:element name="RespostaVerificacaoTP" type="srjvid:RespostaVerificacaoTPType"/»

«xsd:element name="PedidoVerificacao" type="srjvid:PedidoVerificacaoType"/»

«xsd:element name="RespostaVerificacao" type="srjvid:RespostaVerificacaoType"/»

«xsd:complexType name="PedidoVerificacaoJogadorRegistadoType"»

«xsd:sequence»

«xsd:element maxOccurs="1" minOccurs="0" name="NumeroIdentificacaoJogador" type="xsd:string"/»

«xsd:element maxOccurs="1" minOccurs="0" name="TipoIdentificacaoJogador" type="xsd:string"/»

«xsd:element maxOccurs="1" minOccurs="0" name="NifJogador" type="xsd:int"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="RespostaVerificacaoJogadorRegistadoType"»

«xsd:sequence»

«xsd:element name="Sucesso" type="xsd:boolean"/»

«xsd:element name="JogadorValido" type="srjvid:stringSN" minOccurs="1" maxOccurs="1"/»

«xsd:element name="MensagemErro" type="xsd:string" maxOccurs="1" minOccurs="0"/»

«xsd:element name="DetalheErro" type="xsd:string" maxOccurs="1" minOccurs="0"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="PedidoVerificacaoTPType"»

«xsd:sequence»

«xsd:group ref="srjvid:group1" maxOccurs="1" minOccurs="0"/»

«xsd:group ref="srjvid:group2" maxOccurs="1" minOccurs="0"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="PedidoVerificacaoType"»

«xsd:sequence»

«xsd:element name="Nif" type="xsd:int"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="RespostaVerificacaoTPType"»

«xsd:sequence»

«xsd:element name="Sucesso" type="xsd:boolean"/»

«xsd:element name="Valido" type="srjvid:stringSN" minOccurs="0" maxOccurs="1"/»

«xsd:element name="CodigoErro" type="srjvid:string10" minOccurs="0" maxOccurs="1"/»

«xsd:element name="MensagemErro" type="xsd:string" minOccurs="0" maxOccurs="1"/»

«xsd:element name="DetalheErro" type="xsd:string" minOccurs="0" maxOccurs="1"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:complexType name="RespostaVerificacaoType"»

«xsd:sequence»

«xsd:choice maxOccurs="1"»

«xsd:element name="NomeValido" type="srjvid:stringSN"/»

«xsd:element name="NomeCompleto" type="xsd:string"/»

«/xsd:choice»

«xsd:element name="NifValido" type="srjvid:stringSN" maxOccurs="1"/»

«xsd:choice maxOccurs="1"»

«xsd:element name="DataNascimentoValida" type="srjvid:stringSN" minOccurs="1"/»

«xsd:element name="MaiorDeIdade" type="srjvid:stringSN"/»

«/xsd:choice»

«xsd:element name="Falecido" type="srjvid:stringSN" minOccurs="0" maxOccurs="1"/»

«/xsd:sequence»

«/xsd:complexType»

«xsd:group name="group1"»

«xsd:sequence»

«xsd:element name="CodEntidadeExploradora" type="srjvid:string3"/»

«xsd:element name="Nome" type="xsd:string"/»

«xsd:element name="NumeroIdentificacao" type="xsd:string"/»

«xsd:element name="TipoIdentificacao" type="xsd:int"/»

«xsd:element name="DataNascimento" type="xsd:date"/»

«/xsd:sequence»

«/xsd:group»

«xsd:group name="group2"»

«xsd:sequence»

«xsd:element name="Nif" type="xsd:int" maxOccurs="1" minOccurs="0"/»

«xsd:element name="NumeroIdentificacao" type="xsd:string" maxOccurs="1" minOccurs="0"/»

«xsd:element name="TipoIdentificacao" type="xsd:int" maxOccurs="1" minOccurs="0"/»

«/xsd:sequence»

«/xsd:group»

«xsd:simpleType name="string10"»

«xsd:restriction base="xsd:string"»

«xsd:maxLength value="10"/»

«xsd:minLength value="10"/»

«/xsd:restriction»

«/xsd:simpleType»

«xsd:simpleType name="string3"»

«xsd:restriction base="xsd:string"»

«xsd:maxLength value="3"/»

«xsd:minLength value="3"/»

«/xsd:restriction»

«/xsd:simpleType»

«xsd:simpleType name="stringSN"»

«xsd:restriction base="xsd:string"»

«xsd:enumeration value="S"/»

«xsd:enumeration value="N"/»

«/xsd:restriction»

«/xsd:simpleType»

«/xsd:schema»

REQUISITOS DE ARMAZENAMENTO DE DADOS PARA AS ENTIDADES EXPLORADORAS

I - CRIAÇÃO DE FICHEIROS DE DADOS DE JOGO

O SRIJ, de acordo com o enquadramento legal garantido pelo RJO, requer que as entidades exploradoras de jogo online façam o envio sistemático de informação ligada à atividade de jogo. Estes dados devem ser recolhidos no sistema técnico de jogo da entidade exploradora e enviados sobre a forma de um reporte de informação consolidado.

Os dados devem ser organizados em estruturas de XML com base em categorias pré-definidas e armazenadas numa estrutura de sistema de pastas do SAFE da entidade exploradora, como um ficheiro diário único, comprimido (ZIP) e encriptado.

Os ficheiros XML vão conter a atividade considerada relevante do sistema técnico de jogo da entidade exploradora durante o período de uma hora. Desta forma, deve ser produzido um ficheiro por cada hora do dia e por cada categoria de dados. Apenas o ficheiro de resumo financeiro da atividade de jogo da entidade exploradora e a lista diária de jogadores autoexcluídos devem ser produzidas numa base diária.

A entidade exploradora é responsável pela recolha e produção dos ficheiros XML para as seguintes categorias de dados:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

A entidade exploradora é responsável pela geração e colocação diária no SAFE, até às 01:00 AM (hora legal de Portugal Continental,determinada nos termos da legislação nacional e divulgada pelo Observatório Astronómico de Lisboa através dos servidores de NTP), de um ficheiro ZIP contendo, pelo menos, quatro conjuntos de ficheiros XML horários, um ficheiro XML diário de resumo financeiro correspondentes à atividade do dia anterior, bem como um ficheiro diário com a lista de jogadores autoexcluídos do dia anterior.

A infraestrutura de controlo do SRIJ procede em seguida ao período de processamento, consubstanciado na recolha dos ficheiros encriptados colocados no SAFE, que decorrerá previsivelmente durante o intervalo da 01:00 AM às 12:00 PM (hora legal de Portugal Continental,determinada nos termos da legislação nacional e divulgada pelo Observatório Astronómico de Lisboa através dos servidores de NTP).

Se os dados que constam de um determinado ficheiro que tenha sido depositado no SAFE forem considerados inválidos pelo processo de recolha do SRIJ, a criação de um novo ficheiro para uma data hora específica será solicitada à entidade exploradora. Este novo ficheiro de dados reprocessado deverá em seguida ser comprimido, encriptado, e depositado no SAFE tal como detalhado no ponto "III - processo de encriptação de ficheiros de dados".

Os ficheiros devem ser nomeados com a extensão "rp.xml", para garantir o seu reconhecimento como "dados reprocessados" por parte do servidor de identificação do mecanismo de transferência de ficheiros do SRIJ e copiado para a estrutura de filesystem. As operações de reprocessamento não deverão ocorrer durante o periodo normal de processamento.

Nota importante: cada processo de reprocessamento e reenvio de dados deve obrigatoriamente incluir o ficheiro de resumo financeiro (ver o ponto V.1 Schema RESF_ para os detalhes da estrutura do ficheiro) junto com os restantes tipos de ficheiro que devem ser reprocessados.

II - REQUISITOS E ESPECIFICAÇÕES MINIMAS PARA O SAFE

As entidades exploradoras são responsáveis pela configuração de uma infraestrutura que deve garantir as funcionalidades associadas à atividade do SAFE, com os seguintes requisitos mínimos:

. Sistema operativo: Linux (Orientação: a versão Oracle Linux e Red hat já foi testatada com a infraestrutura de controlo do SRIJ, tendo sido comprovada a sua compatibilidade);

. Rede de comunicação: uma conexão wide broadband (de pelo menos 20 Mbps) dedicada à infraestrutura de controlo do SRIJ;

. Um serviço de FTPS configurado no sistema operativo;

. Uma estrutura de pastas de ficheiros:

/u01/app/oracle/mftxfer/in;

/u01/app/oracle/mftxfer/in/excl;

/u01/app/oracle/mftxfer/in/out

III - PROCESSO DE ENCRIPTAÇÃO DE FICHEIROS DE DADOS

O registo de dados no SAFE é agrupado em categorias pré-definidas. Cada uma dessas categorias deve ser assinada, comprimida e encriptada pela entidade exploradora utilizando para tal o formato e os procedimentos descritos no modelo de dados do SRIJ.

O SRIJ disponibiliza às entidades exploradoras certificados PKI Multicert 128 bits SSL/HTTPS para assinar, comprimir e encriptar os ficheiros comprimidos gravados e subsquentemente retidos no SAFE.

Os certificados Multicert 128 bits SSL/HTTPS são gerados de acordo com os seguintes requisitos:

. Recommendation ITU.T. X.509;

. RFC 5280;

. Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates, CA / Browser Forum.

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

. Passo 3: Executa o seguinte script (que serádisponibilizado pelo SRIJ)

» encripta.sh «certificate name» «date YYYYMMDD» «GameVault code»

Examplo: » encripta.sh cert.pem 20150427 1AA

O shell script comprime os ficheiros XML dos subfolder 'in' para um ficheiro ZIP na pasta 'bin', encripta em seguida o ficheiro, gera o ficheiro de password rpasswd.pass.crypt, e cria um ficheiro ZIP final contendo os ficheiros referenciados.

. Passo 4: Move o ficheiro ZIP criado no Passo 3 para a pasta 'out'. Logo que o processo de Managed File Transfer da infraestrutura de controlo do SRIJ deteta novos ficheiros colocados no SAFE, inicia a sua transferência.

CRIAÇÃO SISTEMÁTICA DE REPORTES

I - CONCEITOS DA ESTRUTURA DO MODELO DE DADOS DE JOGO ONLINE

Atividade de jogo online

Cada evento de jogo gravado deve ter um código específico único a cada entidade exploradora. O código de evento de jogo representa um evento aposta específico. Detalham-se em seguida alguns exemplos:

Uma aposta desportiva, um torneio de Poker, uma aposta num jogo de roleta, uma aposta hípica, uma aposta num jogo de baccara, uma aposta num jogo de blackjack, etc..

A cada jogador associado a um evento de jogo é atribuido um código de evento de jogador por entidade exploradora e por evento de jogo. Este código vai encontra-se sempre associado a todas as operações efetuadas pelo jogador, enquanto participante desse evento de jogo.

II - ESPECIFICAÇÃO DOS TIPOS DE RECOLHA DE DADOS

As entidades exploradoras devem recolhar e produzir os ficheiros XML com os seguintes tipos de dados:

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Cada uma das categorias de dados vai ser em seguida detalhada.

V.1 Schema RESF_

Esta categoria deve incluir o reporte financeiro completo da atividade de jogo online da entidade exploradora (i.e., total apostas, total comissões) ao longo das 24 horas que correspondem ao dia em causa. Deve ser gerado um ficheiro por cada dia e como orientação à sua produção, os valores apresentados neste resumo global devem corresponder aos valores reportados nos XML schema para as mesmas variáveis nas restantes categorias de dados do modelo de dados.

Filename rules

NORMAL RESF_YYYYMMDD_[GameVault _code].xml

REPROCESSED RESF_YYYYMMDD_[GameVault _code]rp.xml

Exemplo: RESF_20150402_2AA.xml

XSD Schema

«?xml version="1.0" encoding="UTF-8"?»

«xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"

attributeFormDefault="unqualified" elementFormDefault="qualified"»

«xs:element name="tipo_liq" type="xs:byte"/»

«xs:element name="total_comissoes" type="xs:decimal"/»

«xs:element name="total_ganhos" type="xs:decimal"/»

«xs:element name="total_apostas" type="xs:decimal"/»

«xs:element name="total_reembolsos" type="xs:decimal"/»

«xs:element name="descricao" type="xs:string"/»

«xs:element name="licenca_exp" type="xs:string"/»

«xs:element name="liq_int"»

«xs:complexType»

«xs:sequence»

«xs:element ref="tipo_liq"/»

«xs:element ref="total_comissoes" minOccurs="0" /»

«xs:element ref="total_ganhos" minOccurs="0" /»

«xs:element ref="total_apostas"/»

«xs:element ref="total_reembolsos" minOccurs="0" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="data_fin" type="xs:int"/»

«xs:element name="tipo_jogo"»

«xs:complexType mixed="true"»

«xs:sequence»

«xs:element ref="descricao"/»

«xs:element ref="licenca_exp"/»

«xs:element ref="liq_int" maxOccurs="2" minOccurs="1"/»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="cod_entexpl" type="xs:byte"/»

«xs:element name="datahr" type="xs:int"/»

«xs:element name="datahr" type="xs:int" /»

«xs:element name="cod_cofre" type="xs:string"/»

«xs:element name="resumo_activ"»

«xs:complexType»

«xs:sequence»

«xs:element ref="data_fin"/»

«xs:element ref="tipo_jogo"/»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="ficheiro"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_entexpl"/»

«xs:element ref="datahr"/»

«xs:element ref="id_ficheiro"/»

«xs:element ref="cod_cofre"/»

«xs:element ref="resumo_activ"/»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«/xs:schema»

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

data_fin = 'Data de resumo de actividade financeira. NOT NULL'

tipo_jogo = 'Descricao do tipo de jogo, aposta online. NOT NULL'

licenca_exp = 'Codigo da licenca de jogo online. NOT NULL'

tipo_liq='Tipo de liquidez. Internacional Sim 1, Nao 0.'

total_comissoes = 'Total de comissoes gerado pela entidade exploradora, operador de jogo online no periodo reportado, em euros.'

total_ganhos = 'Total de ganhos gerado pela entidade exploradora, operador de jogo online no periodo reportado, em euros.'

total_apostas = 'Total de apostas gerado pela entidade exploradora, operador de jogo online no periodo reportado, em euros. NOT NULL'

total_reembolsos = 'Total de reembolsos gerado pela entidade exploradora, operador de jogo online no periodo reportado, em euros.'

V.2 Schema JGDR_

Esta categoria de dados deve incluir todos os novos registos de jogadores ou atualizações subsequentes de registos relativos a informação pessoal realizadas dentro do sistema técnico da entidade exploradora. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMAL JGDR_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSED JGDR_YYYYMMDDHH24_[GameVault_ode]rp.xml

Example: JGDR_2015040221_2AA.xml

XSD Schema

«?xml version="1.0" encoding="UTF-8"?»

«xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" attri-buteFormDefault="unqualified" elementFormDefault="qualified"»

«xs:element name="codjogador" type="xs:string" /»

«xs:element name="conta_jog" type="xs:string" /»

«xs:element name="tip_pag" type="xs:string" /»

«xs:element name="logon" type="xs:string" /»

«xs:element name="id_cidadao" type="xs:string" /»

«xs:element name="id_tipocid" type="xs:string" /»

«xs:element name="timestp_reg" type="xs:string" /»

«xs:element name="alias_jog" type="xs:string" /»

«xs:element name="nome" type="xs:string" /»

«xs:element name="data_nascimento" type="xs:string" /»

«xs:element name="nif" type="xs:string" /»

«xs:element name="morada" type="xs:string" /»

«xs:element name="cod_postal" type="xs:string" /»

«xs:element name="id_nacao" type="xs:string" /»

«xs:element name="telefone" type="xs:string" /»

«xs:element name="email" type="xs:string" /»

«xs:element name="resp_at" type="xs:string" /»

«xs:element name="id_resp_at" type="xs:string" /»

«xs:element name="jogador"»

«xs:complexType mixed="true"»

«xs:sequence»

«xs:element ref="codjogador" /»

«xs:element ref="conta_jog" /»

«xs:element ref="tip_pag" /»

«xs:element ref="logon" /»

«xs:element ref="id_cidadao" /»

«xs:element ref="id_tipocid" /»

«xs:element ref="timestp_reg" /»

«xs:element ref="alias_jog" /»

«xs:element ref="nome" /»

«xs:element ref="data_nascimento" /»

«xs:element ref="nif" /»

«xs:element ref="morada" /»

«xs:element ref="cod_postal" /»

«xs:element ref="id_nacao" /»

«xs:element ref="telefone" /»

«xs:element ref="email" /»

«xs:element ref="resp_at" /»

«xs:element ref="id_resp_at" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="cod_entexpl" type="xs:byte" /»

«xs:element name="datahr" type="xs:int" /»

«xs:element name="id_ficheiro" type="xs:int" /»

«xs:element name="cod_cofre" type="xs:string" /»

«xs:element name="registos_jogador"»

«xs:complexType»

«xs:sequence»

«xs:element ref="jogador" maxOccurs="unbounded" minOccurs="0" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="ficheiro"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_entexpl" /»

«xs:element ref="datahr" /»

«xs:element ref="id_ficheiro" /»

«xs:element ref="cod_cofre" /»

«xs:element ref="registos_jogador" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«/xs:schema»

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

id_jogexpl = 'Identificador unico de jogador online na entidade exploradora. NOT NULL'

conta_jog = 'Codigo de conta de jogador online. NOT NULL'

tipo_pag = 'Codigo de tipo de pagamento associado a conta de jogador online. NOT NULL'

id_cidadao = 'Identificador de cidadao do jogador online. NOT NULL'

id_tipocid = 'ID do tipo de identificador de cidadao. 0 BI, 1 CARTAO CIDADAO, 2 PASSAPORTE, 3 NUMERO IDENTIFIC FISCAL, 4 OUTRO. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MSS. NOT NULL'

timestp_reg = 'Timestamp de registo de alteracoes de dados do jogador online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

logon = 'Logon de entrada na entidade exploradora do jogo online. NOT NULL'

alias_jog = 'Alias do jogadoe online.'

nome = 'Nome completo do jogador online. NOT NULL'

data_nascimento = 'Data de nascimento do jogador online. NOT NULL'

nif = 'Numero de identificacao fiscal do jogador online. 1 Cidadaos estrangeiros.'

morada = 'Morada de residencia do jogador online NOT NULL.'

cod_postal = 'Codigo postal da morada de residencia do jogador online. NOT NULL'

id_nacao = 'Codigo alpha-2 =O3166 da nacionalidade do jogador online. NOT NULL'

telefone = 'Contacto telefonico do jogador online. NOT NULL'

email = 'Endereco electronico do jogador online. NOT NULL'

resp_at = 'Resposta do serviço da autoridade tributaria.'

id_resp_at = 'Identificador de resposta do servico de registo na autoridade tributaria.'

V.3 Schema SESS_

Esta categoria deve incluir os registos produzidos no sistema técnico de jogo durante uma sessão de um jogador online. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMALSESS_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSEDSESS_YYYYMMDDHH24_[GameVault _code]rp.xml

Example: SESS_2015040221_2AA.xml

XSD Schema

«?xml version="1.0" encoding="UTF-8"?»

«xs:schema xmlns:xs=http://www.w3.org/2001/XMLSchema

attributeFormDefault="unqualified" elementFormDefault="qualified"»

«xs:element name="codjogador" type="xs:string" /»

«xs:element name="id_sessao" type="xs:string" /»

«xs:element name="timestp_acao" type="xs:string" /»

«xs:element name="tipo_log" type="xs:string" /»

«xs:element name="dispositivo" type="xs:string" /»

«xs:element name="jogador"»

«xs:complexType mixed="true"»

«xs:sequence»

«xs:element ref="codjogador" /»

«xs:element ref="id_sessao" /»

«xs:element ref="timestp_acao" /»

«xs:element ref="tipo_log" /»

«xs:element ref="dispositivo" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="cod_entexpl" type="xs:byte" /»

«xs:element name="datahr" type="xs:int" /»

«xs:element name="id_ficheiro" type="xs:int" /»

«xs:element name="cod_cofre" type="xs:string" /»

«xs:element name="registos_log"»

«xs:complexType»

«xs:sequence»

«xs:element ref="jogador" maxOccurs="unbounded" minOccurs="0" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="ficheiro"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_entexpl" /»

«xs:element ref="datahr" /»

«xs:element ref="id_ficheiro" /»

«xs:element ref="cod_cofre" /»

«xs:element ref="registos_log" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«/xs:schema»

Mapping rules to the regulator online-gambling data model

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

id_jogexpl = 'Identificador unico de jogador online na entidade exploradora. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

id_sessao = 'Identificador de sessao de entrada no operador. NOT NULL'

timestp_acao = 'Timestamp de registo de sessao de jogador online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

tipo_log = 'Tipo de LOG de sessao. LOGIN ou LOGOUT. NOT NULL'

dispositivo = 'Codigo de dispositivo de acesso. C computador, A Movel app, B Movel browser, T TV.'

V.4 Schema AJOG_

Esta categoria deve incluir toda a atividade de jogo registada para o jogador dentro do sistema técnico de jogo da entidade exploradora. A atividade registada deve ser organizada em seis tipos de categorias de jogo: BlackJack, Baccara (Designação portuguesa: Ponto e Banca), Poker, Jogos de Fortuna e Azar, Apostas despotivas e Apostas hípicas. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMALAJOG_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSEDAJOG_YYYYMMDDHH24_[GameVault _code]rp.xml

Example: AJOG_2015040221_2AA.xml

XSD Schema

«?xml version="1.0" encoding="UTF-8"?»

«xs:schema xmlns:xs=http://www.w3.org/2001/XMLSchema

attributeFormDefault="unqualified" elementFormDefault="qualified"»

«xs:element name="codigo" type="xs:string" /»

«xs:element name="saldo_ini" type="xs:string" /»

«xs:element name="saldo_mov" type="xs:string" /»

«xs:element name="saldo_fim" type="xs:string" /»

«xs:element name="bonus_ini" type="xs:string" /»

«xs:element name="bonus_mov" type="xs:string" /»

«xs:element name="bonus_fim" type="xs:string" /»

«xs:element name="pinscr_ini" type="xs:string" /»

«xs:element name="pinscr_mov" type="xs:string" /»

«xs:element name="pinscr_fim" type="xs:string" /»

«xs:element name="cod_ficha" type="xs:string" /»

«xs:element name="cod_aptr_jog" type="xs:string" /»

«xs:element name="ap_cruz" type="xs:string" /»

«xs:element name="timestp_ini" type="xs:string" /»

«xs:element name="timestp_fim" type="xs:string" /»

«xs:element name="dathr_ini_evento" type="xs:string" /»

«xs:element name="dathr_fim_evento" type="xs:string" /»

«xs:element name="cod_fichajog" type="xs:string" /»

«xs:element name="id_sessao" type="xs:string" /»

«xs:element name="ip_jogador" type="xs:string" /»

«xs:element name="ip_regiao" type="xs:string" /»

«xs:element name="cod_opejog" type="xs:string" /»

«xs:element name="timestp" type="xs:string" /»

«xs:element name="descr_ap" type="xs:string" /»

«xs:element name="combinado" type="xs:string" /»

«xs:element name="multipla" type="xs:string" /»

«xs:element name="cota_ap" type="xs:string" /»

«xs:element name="resultado" type="xs:string" /»

«xs:element name="a_saldo_ini" type="xs:string" /»

«xs:element name="a_valor" type="xs:string" /»

«xs:element name="a_saldo_fim" type="xs:string" /»

«xs:element name="a_bonus_ini" type="xs:string" /»

«xs:element name="a_bonus" type="xs:string" /»

«xs:element name="a_bonus_fim" type="xs:string" /»

«xs:element name="g_saldo_ini" type="xs:string" /»

«xs:element name="a_comissao" type="xs:string" /»

«xs:element name="g_ganho" type="xs:string" /»

«xs:element name="g_saldo_fim" type="xs:string" /»

«xs:element name="r_saldo_ini" type="xs:string" /»

«xs:element name="r_valor" type="xs:string" /»

«xs:element name="r_saldo_fim" type="xs:string" /»

«xs:element name="cota" type="xs:string" /»

«xs:element name="mutua" type="xs:string" /»

«xs:element name="id_inscricao" type="xs:string" /»

«xs:element name="id_partida" type="xs:string" /»

«xs:element name="descr" type="xs:string" /»

«xs:element name="torneio" type="xs:string" /»

«xs:element name="id_mesa" type="xs:string" /»

«xs:element name="njog_min" type="xs:string" /»

«xs:element name="njog_max" type="xs:string" /»

«xs:element name="comp_oper" type="xs:string" /»

«xs:element name="buyin" type="xs:string" /»

«xs:element name="buyin_pool" type="xs:string" /»

«xs:element name="a_lim_min" type="xs:string" /»

«xs:element name="a_lim_max" type="xs:string" /»

«xs:element name="nr_creditos" type="xs:string" /»

«xs:element name="marca_jog" type="xs:string" /»

«xs:element name="cartas_m" type="xs:string" /»

«xs:element name="cartas_j" type="xs:string" /»

«xs:element name="posicao_mesa" type="xs:string" /»

«xs:element name="cartas_p" type="xs:string" /»

«xs:element name="cartas_b" type="xs:string" /»

«xs:element name="a_local" type="xs:string" /»

«xs:element name="diferencial" type="xs:string" /»

«xs:element name="pontuacao_p" type="xs:string" /»

«xs:element name="pontuacao_b" type="xs:string" /»

«xs:element name="ro_result_nr" type="xs:string" /»

«xs:element name="ro_result_cor" type="xs:string" /»

«xs:element name="sm_result" type="xs:string" /»

«xs:element name="bin_cartao" type="xs:string" /»

«xs:element name="bin_result" type="xs:string" /»

«xs:element name="sport"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_ficha" /»

«xs:element ref="cod_aptr_jog" /»

«xs:element ref="ap_cruz" /»

«xs:element ref="timestp_ini" /»

«xs:element ref="timestp_fim" /»

«xs:element ref="dathr_ini_evento" /»

«xs:element ref="dathr_fim_evento" /»

«xs:element ref="cod_fichajog" /»

«xs:element ref="id_sessao" /»

«xs:element ref="ip_jogador" /»

«xs:element ref="ip_regiao" /»

«xs:element ref="cod_opejog" /»

«xs:element ref="timestp" /»

«xs:element ref="descr_ap" /»

«xs:element ref="combinado" /»

«xs:element ref="multipla" /»

«xs:element ref="cota_ap" /»

«xs:element ref="resultado" /»

«xs:element ref="a_saldo_ini" /»

«xs:element ref="a_valor" /»

«xs:element ref="a_saldo_fim" /»

«xs:element ref="a_bonus_ini" /»

«xs:element ref="a_bonus" /»

«xs:element ref="a_bonus_fim" /»

«xs:element ref="g_saldo_ini" /»

«xs:element ref="a_comissao" /»

«xs:element ref="g_ganho" /»

«xs:element ref="g_saldo_fim" /»

«xs:element ref="r_saldo_ini" /»

«xs:element ref="r_valor" /»

«xs:element ref="r_saldo_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="hipica"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_ficha" /»

«xs:element ref="cod_aptr_jog" /»

«xs:element ref="ap_cruz" /»

«xs:element ref="timestp_ini" /»

«xs:element ref="timestp_fim" /»

«xs:element ref="dathr_ini_evento" /»

«xs:element ref="dathr_fim_evento" /»

«xs:element ref="cod_fichajog" /»

«xs:element ref="id_sessao" /»

«xs:element ref="ip_jogador" /»

«xs:element ref="ip_regiao" /»

«xs:element ref="cod_opejog" /»

«xs:element ref="timestp" /»

«xs:element ref="descr_ap" /»

«xs:element ref="cota" /»

«xs:element ref="mutua" /»

«xs:element ref="resultado" /»

«xs:element ref="a_saldo_ini" /»

«xs:element ref="a_valor" /»

«xs:element ref="a_saldo_fim" /»

«xs:element ref="a_bonus_ini" /»

«xs:element ref="a_bonus" /»

«xs:element ref="a_bonus_fim" /»

«xs:element ref="a_comissao" /»

«xs:element ref="g_saldo_ini" /»

«xs:element ref="g_ganho" /»

«xs:element ref="g_saldo_fim" /»

«xs:element ref="r_saldo_ini" /»

«xs:element ref="r_valor" /»

«xs:element ref="r_saldo_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="poker"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_ficha" /»

«xs:element ref="cod_aptr_jog" /»

«xs:element ref="ap_cruz" /»

«xs:element ref="timestp_ini" /»

«xs:element ref="timestp_fim" /»

«xs:element ref="dathr_ini_evento" /»

«xs:element ref="dathr_fim_evento" /»

«xs:element ref="cod_fichajog" /»

«xs:element ref="id_sessao" /»

«xs:element ref="ip_jogador" /»

«xs:element ref="ip_regiao" /»

«xs:element ref="cod_opejog" /»

«xs:element ref="timestp" /»

«xs:element ref="id_inscricao" /»

«xs:element ref="id_partida" /»

«xs:element ref="descr" /»

«xs:element ref="torneio" /»

«xs:element ref="id_mesa" /»

«xs:element ref="njog_min" /»

«xs:element ref="njog_max" /»

«xs:element ref="comp_oper" /»

«xs:element ref="buyin" /»

«xs:element ref="buyin_pool" /»

«xs:element ref="a_lim_min" /»

«xs:element ref="a_lim_max" /»

«xs:element ref="nr_creditos" /»

«xs:element ref="marca_jog" /»

«xs:element ref="cartas_m" /»

«xs:element ref="cartas_j" /»

«xs:element ref="posicao_mesa" /»

«xs:element ref="resultado" /»

«xs:element ref="a_saldo_ini" /»

«xs:element ref="a_valor" /»

«xs:element ref="a_saldo_fim" /»

«xs:element ref="a_bonus_ini" /»

«xs:element ref="a_bonus" /»

«xs:element ref="a_bonus_fim" /»

«xs:element ref="a_comissao" /»

«xs:element ref="g_saldo_ini" /»

«xs:element ref="g_ganho" /»

«xs:element ref="g_saldo_fim" /»

«xs:element ref="r_saldo_ini" /»

«xs:element ref="r_valor" /»

«xs:element ref="r_saldo_fim" /»

«xs:element ref="pinscr_ini" /»

«xs:element ref="pinscr_mov" /»

«xs:element ref="pinscr_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="pbanca"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_ficha" /»

«xs:element ref="cod_aptr_jog" /»

«xs:element ref="ap_cruz" /»

«xs:element ref="timestp_ini" /»

«xs:element ref="timestp_fim" /»

«xs:element ref="dathr_ini_evento" /»

«xs:element ref="dathr_fim_evento" /»

«xs:element ref="cod_fichajog" /»

«xs:element ref="id_sessao" /»

«xs:element ref="ip_jogador" /»

«xs:element ref="ip_regiao" /»

«xs:element ref="cod_opejog" /»

«xs:element ref="timestp" /»

«xs:element ref="id_inscricao" /»

«xs:element ref="id_partida" /»

«xs:element ref="descr" /»

«xs:element ref="id_mesa" /»

«xs:element ref="njog_max" /»

«xs:element ref="cartas_p" /»

«xs:element ref="cartas_b" /»

«xs:element ref="a_local" /»

«xs:element ref="diferencial" /»

«xs:element ref="pontuacao_p" /»

«xs:element ref="pontuacao_b" /»

«xs:element ref="resultado" /»

«xs:element ref="a_saldo_ini" /»

«xs:element ref="a_valor" /»

«xs:element ref="a_saldo_fim" /»

«xs:element ref="a_bonus_ini" /»

«xs:element ref="a_bonus" /»

«xs:element ref="a_bonus_fim" /»

«xs:element ref="a_comissao" /»

«xs:element ref="g_saldo_ini" /»

«xs:element ref="g_ganho" /»

«xs:element ref="g_saldo_fim" /»

«xs:element ref="r_saldo_ini" /»

«xs:element ref="r_valor" /»

«xs:element ref="r_saldo_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="bjack"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_ficha" /»

«xs:element ref="cod_aptr_jog" /»

«xs:element ref="ap_cruz" /»

«xs:element ref="timestp_ini" /»

«xs:element ref="timestp_fim" /»

«xs:element ref="dathr_ini_evento" /»

«xs:element ref="dathr_fim_evento" /»

«xs:element ref="cod_fichajog" /»

«xs:element ref="id_sessao" /»

«xs:element ref="ip_jogador" /»

«xs:element ref="ip_regiao" /»

«xs:element ref="cod_opejog" /»

«xs:element ref="timestp" /»

«xs:element ref="id_inscricao" /»

«xs:element ref="id_partida" /»

«xs:element ref="descr" /»

«xs:element ref="id_mesa" /»

«xs:element ref="njog_max" /»

«xs:element ref="cartas_m" /»

«xs:element ref="cartas_j" /»

«xs:element ref="posicao_mesa" /»

«xs:element ref="resultado" /»

«xs:element ref="a_saldo_ini" /»

«xs:element ref="a_valor" /»

«xs:element ref="a_saldo_fim" /»

«xs:element ref="a_bonus_ini" /»

«xs:element ref="a_bonus" /»

«xs:element ref="a_bonus_fim" /»

«xs:element ref="a_comissao" /»

«xs:element ref="g_saldo_ini" /»

«xs:element ref="g_ganho" /»

«xs:element ref="g_saldo_fim" /»

«xs:element ref="r_saldo_ini" /»

«xs:element ref="r_valor" /»

«xs:element ref="r_saldo_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="fortazar"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_ficha" /»

«xs:element ref="cod_aptr_jog" /»

«xs:element ref="ap_cruz" /»

«xs:element ref="timestp_ini" /»

«xs:element ref="timestp_fim" /»

«xs:element ref="dathr_ini_evento" /»

«xs:element ref="dathr_fim_evento" /»

«xs:element ref="cod_fichajog" /»

«xs:element ref="id_sessao" /»

«xs:element ref="ip_jogador" /»

«xs:element ref="ip_regiao" /»

«xs:element ref="cod_opejog" /»

«xs:element ref="timestp" /»

«xs:element ref="descr_ap" /»

«xs:element ref="ro_result_nr" /»

«xs:element ref="ro_result_cor" /»

«xs:element ref="sm_result" /»

«xs:element ref="bin_cartao" /»

«xs:element ref="bin_result" /»

«xs:element ref="a_saldo_ini" /»

«xs:element ref="a_valor" /»

«xs:element ref="a_saldo_fim" /»

«xs:element ref="a_bonus_ini" /»

«xs:element ref="a_bonus" /»

«xs:element ref="a_bonus_fim" /»

«xs:element ref="a_comissao" /»

«xs:element ref="g_saldo_ini" /»

«xs:element ref="g_ganho" /»

«xs:element ref="g_saldo_fim" /»

«xs:element ref="r_saldo_ini" /»

«xs:element ref="r_valor" /»

«xs:element ref="r_saldo_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="codjogador" type="xs:string" /»

«xs:element name="logon" type="xs:string" /»

«xs:element name="conta_jog"»

«xs:complexType»

«xs:sequence»

«xs:element ref="codigo" /»

«xs:element ref="saldo_ini" /»

«xs:element ref="saldo_mov" /»

«xs:element ref="saldo_fim" /»

«xs:element ref="bonus_ini" /»

«xs:element ref="bonus_mov" /»

«xs:element ref="bonus_fim" /»

«xs:element ref="pinscr_ini" /»

«xs:element ref="pinscr_mov" /»

«xs:element ref="pinscr_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="apostas"»

«xs:complexType»

«xs:sequence»

«xs:element ref="sport" minOccurs="0" maxOccurs="unbounded" /»

«xs:element ref="hipica" minOccurs="0" maxOccurs="unbounded" /»

«xs:element ref="poker" minOccurs="0" maxOccurs="unbounded" /»

«xs:element ref="pbanca" minOccurs="0" maxOccurs="unbounded" /»

«xs:element ref="bjack" minOccurs="0" maxOccurs="unbounded" /»

«xs:element ref="fortazar" minOccurs="0" maxOccurs="unbounded" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="jogador"»

«xs:complexType mixed="true"»

«xs:sequence»

«xs:element ref="codjogador" /»

«xs:element ref="logon" /»

«xs:element ref="conta_jog" /»

«xs:element ref="apostas" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="cod_entexpl" type="xs:byte" /»

«xs:element name="datahr" type="xs:int" /»

«xs:element name="id_ficheiro" type="xs:int" /»

«xs:element name="cod_cofre" type="xs:string" /»

«xs:element name="registos_jogo"»

«xs:complexType»

«xs:sequence»

«xs:element ref="jogador" maxOccurs="

unbounded" minOccurs="0" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="ficheiro"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_entexpl" /»

«xs:element ref="datahr" /»

«xs:element ref="id_ficheiro" /»

«xs:element ref="cod_cofre" /»

«xs:element ref="registos_jogo" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«/xs:schema»

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

id_jogexpl = 'Identificador de jogador online na entidade exploradora. NOT NULL'

cod_cntjog = 'Codigo da conta de jogo do jogador na entidade exploradora ou operador de jogo online. NOT NULL'

sal_jog_ini = 'Saldo inicial, em euros, da conta de jogo online. NOT NULL'

sal_jog_mov = 'Saldo movimentado, em euros, na conta de jogo online.'

sal_jog_final = 'Saldo actual, em euros, da conta de jogo online.'

bon_jog_ini = 'Bonus inicial, em euros, na conta de jogo online. NOT NULL'

bon_jog_mov = 'Bonus movimentado, em euros, na conta de jogo online.'

bon_jog_final = 'Bonus actual, em euros, na conta de jogador online.'

cod_fichjog = 'Codigo externo de ficha de jogo, aposta online. NOT NULL'

cod_aptr_jog = 'Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online. NOT NULL'

timestp_ini = 'Ficha de jogo. Inicio da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

timestp_fim = 'Ficha de jogo. Fim da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM.'

dathr_ini_evento = 'Datahora de inicio do evento. YYYYMMDDHH24MISS.'

dathr_fim_evento = 'Datahora de fim do evento. YYYYMMDDHH24MISS.'

ap_cruz = 'Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada. NOT NULL'

cod_fjoga = 'Codigo externo de ficha de jogador atribuido pela entidade exploradora de jogo online. NOT NULL'

id_sessao = 'Identificador de sessao de entrada no operador.'

ip_jogador = 'IP da maquina do jogador online.'

regiao_ip = 'Regiao do IP da maquina do jogador online.'

cod_opejog = 'Codigo externo de operacao de jogo, aposta online. NOT NULL'

timestp = 'Timestamp da operacao de jogo, aposta online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

id_inscricao = 'Identificador da inscricao do jogador. NOT NULL'

id_partida = 'Identificador de partida de jogo. NOT NULL'

descr = 'Descritivo do torneio, partida. NOT NULL'

id_mesa = 'Identificador da mesa de jogo. NOT NULL'

njog_max = 'Numero maximo de jogadores.'

cartas_m = 'Lista de cartas existentes na mesa, separadas por hifen.'

cartas_j = 'Lista de cartas do jogador online, separadas por hifen.'

posicao_mesa = 'Lugar do jogador na mesa de jogo.'

resultado = 'Resultado para cada jogador online. 0 Perdeu 1 Ganhou 3 Empate.'

a_saldo_ini = 'Saldo, em euros, antes do inicio da aposta.'

a_valor = 'Valor da aposta, em euros.'

a_saldo_fim = 'Saldo, em euros, depois do fecho de aposta.'

a_bonus_ini = 'Bonus do jogador online, em euros, antes do inicio da aposta.'

a_bonus = 'Bonus da aposta, em euros.'

a_bonus_fim = 'Bonus do jogador online, em euros, depois do fecho de aposta.'

a_comissao = 'Comissao de aposta da entidade exploradora ou operador jogo online.'

g_saldo_ini = 'Valor do saldo, em euros, antes do ganho de aposta.'

g_ganho = 'Valor ganho, em euros, com a aposta.'

g_saldo_fim = 'Valor do saldo, em euros, apos ganho de aposta.'

r_saldo_ini = 'Valor do saldo, em euros, antes do reembolso de aposta.'

r_valor = 'Valor do reembolso, em euros.'

r_saldo_fim = 'Valor do saldo, em euros, depois do reembolso de aposta.'

reg_ctrl = 'Controle interno de entrada de registos.'

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

id_jogexpl = 'Identificador de jogador online na entidade exploradora. NOT NULL'

cod_cntjog = 'Codigo da conta de jogo do jogador na entidade exploradora ou operador de jogo online. NOT NULL'

sal_jog_ini = 'Saldo inicial, em euros, da conta de jogo online. NOT NULL'

sal_jog_mov = 'Saldo movimentado, em euros, na conta de jogo online.'

sal_jog_final = 'Saldo actual, em euros, da conta de jogo online.'

bon_jog_ini = 'Bonus inicial, em euros, na conta de jogo online. NOT NULL'

bon_jog_mov = 'Bonus movimentado, em euros, na conta de jogo online.'

bon_jog_final = 'Bonus actual, em euros, na conta de jogador online.'

cod_fichjog = 'Codigo externo de ficha de jogo, aposta online. NOT NULL'

cod_aptr_jog = 'Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online. NOT NULL'

timestp_ini = 'Ficha de jogo. Inicio da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

timestp_fim = 'Ficha de jogo. Fim da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM.'

dathr_ini_evento = 'Datahora de inicio do evento. YYYYMMDDHH24MISS.'

dathr_fim_evento = 'Datahora de fim do evento. YYYYMMDDHH24MISS.'

ap_cruz = 'Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada. NOT NULL'

cod_fjoga = 'Codigo externo de ficha de jogador atribuido pela entidade exploradora de jogo online. NOT NULL'

id_sessao = 'Identificador de sessao de entrada no operador.'

ip_jogador = 'IP da maquina do jogador online.'

regiao_ip = 'Regiao do IP da maquina do jogador online.'

cod_opejog = 'Codigo externo de operacao de jogo, aposta online. NOT NULL'

timestp = 'Timestamp da operacao de jogo, aposta online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

id_inscricao = 'Identificador da inscricao do jogador. NOT NULL'

id_partida = 'Identificador de partida de jogo. NOT NULL'

descr = 'Descritivo do torneio, partida. NOT NULL'

id_mesa = 'Identificador da mesa de jogo. NOT NULL'

njog_max = 'Numero maximo de jogadores.'

cartas_p = 'Lista de cartas existentes no ponto, separadas por hifen.'

cartas_b = 'Lista de cartas existentes na banca, separadas por hifen.'

a_local = 'Local de aposta. 4 Ponto 3 Empate 5 Banca'

diferencial = 'Diferencial aplicado pela mesa de jogo. Apenas Ponto e Banca Macau.'

pont_ponto = 'Pontuacao ponto.'

pont_banca = 'Pontuacao banca.'

resultado = 'Resultado para cada jogador online. 4 Ponto 3 Empate 5 Banca'

a_saldo_ini = 'Saldo, em euros, antes do inicio da aposta.'

a_valor = 'Valor da aposta, em euros.'

a_saldo_fim = 'Saldo, em euros, depois do fecho de aposta.'

a_bonus_ini = 'Bonus do jogador online, em euros, antes do inicio da aposta.'

a_bonus = 'Bonus da aposta, em euros.'

a_bonus_fim = 'Bonus do jogador online, em euros, depois do fecho de aposta.'

a_comissao = 'Comissao de aposta da entidade exploradora ou operador jogo online.'

g_saldo_ini = 'Valor do saldo, em euros, antes do ganho de aposta.'

g_ganho = 'Valor ganho, em euros, com a aposta.'

g_saldo_fim = 'Valor do saldo, em euros, apos ganho de aposta.'

r_saldo_ini = 'Valor do saldo, em euros, antes do reembolso de aposta.'

r_valor = 'Valor do reembolso, em euros.'

r_saldo_fim = 'Valor do saldo, em euros, depois do reembolso de aposta.'

reg_ctrl = 'Controle interno de entrada de registos.'

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

id_jogexpl = 'Identificador de jogador online na entidade exploradora. NOT NULL'

cod_cntjog = 'Codigo da conta de jogo do jogador na entidade exploradora ou operador de jogo online. NOT NULL'

sal_jog_ini = 'Saldo inicial, em euros, da conta de jogo online. NOT NULL'

sal_jog_mov = 'Saldo movimentado, em euros, na conta de jogo online.'

sal_jog_final = 'Saldo actual, em euros, da conta de jogo online.'

bon_jog_ini = 'Bonus inicial, em euros, na conta de jogo online. NOT NULL'

bon_jog_mov = 'Bonus movimentado, em euros, na conta de jogo online.'

bon_jog_final = 'Bonus actual, em euros, na conta de jogador online.'

cod_fichjog = 'Codigo externo de ficha de jogo, aposta online. NOT NULL'

cod_aptr_jog = 'Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online. NOT NULL'

timestp_ini = 'Ficha de jogo. Inicio da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

timestp_fim = 'Ficha de jogo. Fim da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM.'

dathr_ini_evento = 'Datahora de inicio do evento. YYYYMMDDHH24MISS.'

dathr_fim_evento = 'Datahora de fim do evento. YYYYMMDDHH24MISS.'

ap_cruz = 'Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada. NOT NULL'

cod_fjoga = 'Codigo externo de ficha de jogador atribuido pela entidade exploradora de jogo online. NOT NULL'

id_sessao = 'Identificador de sessao de entrada no operador.'

ip_jogador = 'IP da maquina do jogador online.'

regiao_ip = 'Regiao do IP da maquina do jogador online.'

cod_opejog = 'Codigo externo de operacao de jogo, aposta online. NOT NULL'

timestp = 'Timestamp da operacao de jogo, aposta online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

id_inscricao = 'Identificador da inscricao do jogador. NOT NULL'

id_partida = 'Identificador de partida de jogo. NOT NULL'

descr = 'Descritivo do torneio, partida. NOT NULL'

torneio = 'Identifica se a operacao se enquadra num torneio ou nao. S sim, N nao. NOT NULL'

id_mesa = 'Identificador da mesa de jogo. NOT NULL'

njog_min = 'Numero minimo de jogadores.'

njog_max = 'Numero maximo de jogadores.'

comp_oper = 'Comparticipacao da entidade exploradora de jogo online na partida, jogo de poker.'

buyin = 'Buy in'

buyin_pool = 'Buy in pool.'

a_lim_min = 'Limite minimo de aposta do jogador online.'

a_lim_max = 'Limite maximo de aposta do jogador online.'

nr_creditos = 'Numero de fichas de jogo.'

marca_jog = 'Jogador online que tem a mao ou botao. S tem ou botao, N nao tem o botao'

cartas_m = 'Lista de cartas existentes na mesa, separadas por hifen.'

cartas_j = 'Lista de cartas do jogador online, separadas por hifen.'

posicao_mesa = 'Lugar do jogador na mesa de jogo.'

resultado = 'Resultado para cada jogador online. 0 Perdeu 1 Ganhou 2 All In'

a_saldo_ini = 'Saldo, em euros, antes do inicio da aposta.'

a_valor = 'Valor da aposta, em euros.'

a_saldo_fim = 'Saldo, em euros, depois do fecho de aposta.'

a_bonus_ini = 'Bonus do jogador online, em euros, antes do inicio da aposta.'

a_bonus = 'Bonus da aposta, em euros.'

a_bonus_fim = 'Bonus do jogador online, em euros, depois do fecho de aposta.'

a_comissao = 'Comissao de aposta da entidade exploradora ou operador jogo online.'

g_saldo_ini = 'Valor do saldo, em euros, antes do ganho de aposta.'

g_ganho = 'Valor ganho, em euros, com a aposta.'

g_saldo_fim = 'Valor do saldo, em euros, apos ganho de aposta.'

r_saldo_ini = 'Valor do saldo, em euros, antes do reembolso de aposta.'

r_valor = 'Valor do reembolso, em euros.'

r_saldo_fim = 'Valor do saldo, em euros, depois do reembolso de aposta.'

pinscr_ini = 'Valor inicial de premio de inscricao em torneio de poker, em euros.'

pinscr_mov = 'Valor movimentado de premio de inscricao em torneio de poker, em euros.'

pinscr_fim = 'Valor final de premio de inscricao em torneio de poker, em euros.'

reg_ctrl = 'Controle interno de entrada de registos.'

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog3 = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

id_jogexpl = 'Identificador de jogador online na entidade exploradora. NOT NULL'

cod_cntjog = 'Codigo da conta de jogo do jogador na entidade exploradora ou operador de jogo online. NOT NULL'

sal_jog_ini = 'Saldo inicial, em euros, da conta de jogo online. NOT NULL'

sal_jog_mov = 'Saldo movimentado, em euros, na conta de jogo online.'

sal_jog_final = 'Saldo actual, em euros, da conta de jogo online.'

bon_jog_ini = 'Bonus inicial, em euros, na conta de jogo online. NOT NULL'

bon_jog_mov = 'Bonus movimentado, em euros, na conta de jogo online.'

bon_jog_final = 'Bonus actual, em euros, na conta de jogador online.'

cod_fichjog = 'Codigo externo de ficha de jogo, aposta online. NOT NULL'

cod_aptr_jog = 'Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online. NOT NULL'

timestp_ini = 'Ficha de jogo. Inicio da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

timestp_fim = 'Ficha de jogo. Fim da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM.'

dathr_ini_evento = 'Datahora de inicio do evento. YYYYMMDDHH24MISS.'

dathr_fim_evento = 'Datahora de fim do evento. YYYYMMDDHH24MISS.'

ap_cruz = 'Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada. NOT NULL'

cod_fjoga = 'Codigo externo de ficha de jogador atribuido pela entidade exploradora de jogo online. NOT NULL'

id_sessao = 'Identificador de sessao de entrada no operador.'

ip_jogador = 'IP da maquina do jogador online.'

regiao_ip = 'Regiao do IP da maquina do jogador online.'

cod_opejog = 'Codigo externo de operacao de jogo, aposta online. NOT NULL'

timestp = 'Timestamp da operacao de jogo, aposta online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

descr = 'Descritivo da aposta. NOT NULL'

ro_result_nr = 'Resultado da aposta roleta numero.'

ro_result_cor = 'Resultado roleta cor. V vermelho, P preto.'

sm_result = 'Resultado da aposta slot machine.'

bin_cartao = 'Lista de numeros do cartao de jogador de bingo separados por hifen. '

bin_result = 'Resultado da aposta bingo.'

a_saldo_ini = 'Saldo, em euros, antes do inicio da aposta.'

a_valor = 'Valor da aposta, em euros.'

a_saldo_fim = 'Saldo, em euros, depois do fecho de aposta.'

a_bonus_ini = 'Bonus do jogador online, em euros, antes do inicio da aposta.'

a_bonus = 'Bonus da aposta, em euros.'

a_bonus_fim = 'Bonus do jogador online, em euros, depois do fecho de aposta.'

a_comissao = 'Comissao de aposta da entidade exploradora ou operador jogo online.'

g_saldo_ini = 'Valor do saldo, em euros, antes do ganho de aposta.'

g_ganho = 'Valor ganho, em euros, com a aposta.'

g_saldo_fim = 'Valor do saldo, em euros, apos ganho de aposta.'

r_saldo_ini = 'Valor do saldo, em euros, antes do reembolso de aposta.'

r_valor = 'Valor do reembolso, em euros.'

r_saldo_fim = 'Valor do saldo, em euros, depois do reembolso de aposta.'

reg_ctrl = 'Controle interno de entrada de registos.'

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

id_jogexpl = 'Identificador de jogador online na entidade exploradora. NOT NULL'

cod_cntjog = 'Codigo da conta de jogo do jogador na entidade exploradora ou operador de jogo online. NOT NULL'

sal_jog_ini = 'Saldo inicial, em euros, da conta de jogo online. NOT NULL'

sal_jog_mov = 'Saldo movimentado, em euros, na conta de jogo online.'

sal_jog_final = 'Saldo actual, em euros, da conta de jogo online.'

bon_jog_ini = 'Bonus inicial, em euros, na conta de jogo online. NOT NULL'

bon_jog_mov = 'Bonus movimentado, em euros, na conta de jogo online.'

bon_jog_final = 'Bonus actual, em euros, na conta de jogador online.'

cod_fichjog = 'Codigo externo de ficha de jogo, aposta online. NOT NULL'

cod_aptr_jog = 'Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online. NOT NULL'

timestp_ini = 'Ficha de jogo. Inicio da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

timestp_fim = 'Ficha de jogo. Fim da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM.'

dathr_ini_evento = 'Datahora de inicio do evento. YYYYMMDDHH24MISS.'

dathr_fim_evento = 'Datahora de fim do evento. YYYYMMDDHH24MISS.'

ap_cruz = 'Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada. NOT NULL'

cod_fjoga = 'Codigo externo de ficha de jogador atribuido pela entidade exploradora de jogo online. NOT NULL'

id_sessao = 'Identificador de sessao de entrada no operador.'

ip_jogador = 'IP da maquina do jogador online.'

regiao_ip = 'Regiao do IP da maquina do jogador online.'

cod_opejog = 'Codigo externo de operacao de jogo, aposta online. NOT NULL'

timestp = 'Timestamp da operacao de jogo, aposta online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

descr = 'Descritivo do torneio, partida. NOT NULL'

combi = 'Identifica se a aposta e combinada ou nao. Mais do que um evento. S sim, N nao. NOT NULL'

multi = 'Identifica se a aposta e multipla ou nao. Mais do que um resultado. S sim, N nao. NOT NULL'

cota = 'Cota total da aposta desportiva. NOT NULL'

resultado = 'Resultado da aposta desportiva.'

a_saldo_ini = 'Saldo, em euros, antes do inicio da aposta.'

a_valor = 'Valor da aposta, em euros.'

a_saldo_fim = 'Saldo, em euros, depois do fecho de aposta.'

a_bonus_ini = 'Bonus do jogador online, em euros, antes do inicio da aposta.'

a_bonus = 'Bonus da aposta, em euros.'

a_bonus_fim = 'Bonus do jogador online, em euros, depois do fecho de aposta.'

a_comissao = 'Comissao de aposta da entidade exploradora ou operador jogo online.'

g_saldo_ini = 'Valor do saldo, em euros, antes do ganho de aposta.'

g_ganho = 'Valor ganho, em euros, com a aposta.'

g_saldo_fim = 'Valor do saldo, em euros, apos ganho de aposta.'

r_saldo_ini = 'Valor do saldo, em euros, antes do reembolso de aposta.'

r_valor = 'Valor do reembolso, em euros.'

r_saldo_fim = 'Valor do saldo, em euros, depois do reembolso de aposta.'

reg_ctrl = 'Controle interno de entrada de registos.'

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

id_jogexpl = 'Identificador de jogador online na entidade exploradora. NOT NULL'

cod_cntjog = 'Codigo da conta de jogo do jogador na entidade exploradora ou operador de jogo online. NOT NULL'

sal_jog_ini = 'Saldo inicial, em euros, da conta de jogo online. NOT NULL'

sal_jog_mov = 'Saldo movimentado, em euros, na conta de jogo online.'

sal_jog_final = 'Saldo actual, em euros, da conta de jogo online.'

bon_jog_ini = 'Bonus inicial, em euros, na conta de jogo online. NOT NULL'

bon_jog_mov = 'Bonus movimentado, em euros, na conta de jogo online.'

bon_jog_final = 'Bonus actual, em euros, na conta de jogador online.'

cod_fichjog = 'Codigo externo de ficha de jogo, aposta online. NOT NULL'

cod_aptr_jog = 'Codigo de aposta para utilizacao da entidade exploradora ou operador de jogo online. NOT NULL'

timestp_ini = 'Ficha de jogo. Inicio da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

timestp_fim = 'Ficha de jogo. Fim da aposta, jogo online. YYYYMMDDHH24MISS.FF TZH:TZM.'

dathr_ini_evento = 'Datahora de inicio do evento. YYYYMMDDHH24MISS.'

dathr_fim_evento = 'Datahora de fim do evento. YYYYMMDDHH24MISS.'

ap_cruz = 'Identifica se a ficha de jogador de refere a um jogo ou aposta cruzada. NOT NULL'

cod_fjoga = 'Codigo externo de ficha de jogador atribuido pela entidade exploradora de jogo online. NOT NULL'

id_sessao = 'Identificador de sessao de entrada no operador.'

ip_jogador = 'IP da maquina do jogador online.'

regiao_ip = 'Regiao do IP da maquina do jogador online.'

cod_opejog = 'Codigo externo de operacao de jogo, aposta online. NOT NULL'

timestp = 'Timestamp da operacao de jogo, aposta online. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

descr = 'Descritivo do torneio, partida.NOT NULL '

cota = 'Cota da aposta hipica. NOT NULL'

mutua = 'Identifica se a aposta e mutua ou nao. S sim, N nao. NOT NULL'

resultado = 'Resultado da aposta hipica.'

a_saldo_ini = 'Saldo, em euros, antes do inicio da aposta.'

a_valor = 'Valor da aposta, em euros.'

a_saldo_fim = 'Saldo, em euros, depois do fecho de aposta.'

a_bonus_ini = 'Bonus do jogador online, em euros, antes do inicio da aposta.'

a_bonus = 'Bonus da aposta, em euros.'

a_bonus_fim = 'Bonus do jogador online, em euros, depois do fecho de aposta.'

a_comissao = 'Comissao de aposta da entidade exploradora ou operador jogo online.'

g_saldo_ini = 'Valor do saldo, em euros, antes do ganho de aposta.'

g_ganho = 'Valor ganho, em euros, com a aposta.'

g_saldo_fim = 'Valor do saldo, em euros, apos ganho de aposta.'

r_saldo_ini = 'Valor do saldo, em euros, antes do reembolso de aposta.'

r_valor = 'Valor do reembolso, em euros.'

r_saldo_fim = 'Valor do saldo, em euros, depois do reembolso de aposta.'

reg_ctrl = 'Controle interno de entrada de registos.'

V.5 Schema TRAN_

Esta categoria inclui o registo das transações registadas na conta do jogador no sistema técnico de jogo. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMAL TRAN_YYYYMMDDHH24_[GameVault _code].xml

REPROCESSEDTRAN_YYYYMMDDHH24_[GameVault _code]rp.xml

Example: TRAN_2015040214_2AA.xml

XSD Schema

«?xml version="1.0" encoding="UTF-8"?»

«xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"

attributeFormDefault="unqualified" elementFormDefault="qualified"»

«xs:element name="codjogador" type="xs:string" /»

«xs:element name="cod_conta" type="xs:string" /»

«xs:element name="cod_optct" type="xs:string" /»

«xs:element name="timestp_op" type="xs:string" /»

«xs:element name="saldo_ini" type="xs:string" /»

«xs:element name="saldo_mov" type="xs:string" /»

«xs:element name="saldo_fim" type="xs:string" /»

«xs:element name="conta"»

«xs:complexType mixed="true"»

«xs:sequence»

«x s:element ref="codjogador" /»

« xs:element ref="cod_conta" /»

« xs:element ref="cod_optct" /»

« xs:element ref="timestp_op" /»

« xs:element ref="saldo_ini" /»

« xs:element ref="saldo_mov" /»

« xs:element ref="saldo_fim" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="cod_entexpl" type="xs:byte" /»

«xs:element name="datahr" type="xs:int" /»

«xs:element name="id_ficheiro" type="xs:int" /»

«xs:element name="cod_cofre" type="xs:string" /»

«xs:element name="registos_conta"»

«xs:complexType»

«xs:sequence»

«xs:element ref="conta" maxOccurs="unbounded" minOccurs="0" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="ficheiro"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_entexpl" /»

«xs:element ref="datahr" /»

«xs:element ref="id_ficheiro" /»

«xs:element ref="cod_cofre" /»

«xs:element ref="registos_conta" /»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«/xs:schema»

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

cod_expljog = 'Codigo externo da entidade exploradora ou operador de jogo online. NOT NULL'

cod_cofjog = 'Codigo externo de cofre de dados do jogo online. NOT NULL'

id_ficheiro = 'Identificador do ficheiro XML proveniente da entidade exploradora de jogo online. NOT NULL'

id_jogexpl = 'Identificador unico de jogador online na entidade exploradora. NOT NULL'

cod_cntjog = 'Codigo da conta de jogo do jogador na entidade exploradora ou operador de jogo online. NOT NULL'

data_hr = 'Datahora de producao do ficheiro de dados XML. YYYYMMDDHH24MISS. NOT NULL'

cod_optct = 'Tipo de transacao financeira entre conta bancaria do jog. e conta da ent. exploradora de jogo online. DEBITO ou CREDITO. NOT NULL'

timestp_op = 'Timestamp de realizacao da operacao. YYYYMMDDHH24MISS.FF TZH:TZM. NOT NULL'

saldo_ini = 'Saldo inicial da conta do jogador na entidade exploradora ou operador de jogo online antes da operacao. NOT NULL'

saldo_mov = 'Saldo movimentado na conta do jogador na entidade exploradora ou operador de jogo online durante a operacao.'

saldo_fim = 'Saldo final da conta do jogador na entidade exploradora ou operador de jogo online apos a operacao. NOT NULL'

V.6 Schema EXCL_

Esta categoria deve incluir informação sobre os pedidos de autoexclusão registados no sistema técnico de jogo. A entidade exploradora deve produzir um ficheiro por cada hora do dia a que respeita o reporte.

Filename rules

NORMALEXCL_YYYYMMDD_[GameVault _code].xml

REPROCESSEDEXCL_YYYYMMDD_[GameVault _code]rp.xml

Example: EXCL_20150405_1AA.xml

XSD Schema

«?xml version="1.0"?»

«xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"

attributeFormDefault="unqualified" elementFormDefault="qualified"»

«xs:element name="IdTipoCid" type="xs:string"/»

«xs:element name="IdCidadao" type="xs:string"/»

«xs:element name="Nome" type="xs:string"/»

«xs:element name="IdNacao" type="xs:string"/»

«xs:element name="SitProfissional" type="xs:byte"/»

«xs:element name="Morada" type="xs:string"/»

«xs:element name="CodPostal" type="xs:string"/»

«xs:element name="Distrito" type="xs:string"/»

«xs:element name="Email" type="xs:string"/»

«xs:element name="Duracao" type="xs:byte"/»

«xs:element name="DataInicio" type="xs:int"/»

«xs:element name="TipoDoc" type="xs:string"/»

«xs:element name="DocFrente" type="xs:string"/»

«xs:element name="DocVerso" type="xs:string"/»

«xs:element name="Motivo" type="xs:string"/»

«xs:element name="RegistoPedidoExclusao"»

«xs:complexType»

«xs:sequence»

«xs:element ref="IdTipoCid"/»

«xs:element ref="IdCidadao"/»

«xs:element ref="Nome"/»

«xs:element ref="IdNacao"/»

«xs:element ref="SitProfissional"/»

«xs:element ref="Morada"/»

«xs:element ref="CodPostal"/»

«xs:element ref="Distrito"/»

«xs:element ref="Email"/»

«xs:element ref="Duracao"/»

«xs:element ref="DataInicio"/»

«xs:element ref="TipoDoc"/»

«xs:element ref="DocFrente"/»

«xs:element ref="DocVerso"/»

«xs:element ref="Motivo"/»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="cod_entexpl" type="xs:byte"/»

«xs:element name="datahr" type="xs:int"/»

«xs:element name="id_ficheiro" type="xs:short"/»

«xs:element name="cod_cofre" type="xs:string"/»

«xs:element name="ListaPedidosExclusao"»

«xs:complexType»

«xs:sequence»

«xs:element ref="RegistoPedidoExclusao" minOccurs="0" maxOccurs="unbounded"/»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«xs:element name="ficheiro"»

«xs:complexType»

«xs:sequence»

«xs:element ref="cod_entexpl"/»

«xs:element ref="datahr"/»

«xs:element ref="id_ficheiro"/»

«xs:element ref="cod_cofre"/»

«xs:element ref="ListaPedidosExclusao"/»

«/xs:sequence»

«/xs:complexType»

«/xs:element»

«/xs:schema»

Regras de mapeamento para o modelo de dados da entidade exploradora

[(ver documento original)](https://files.diariodarepublica.pt/2s/2016/04/072000002/0000500021.pdf)

Comentário aos Elementos/Atributos

nif = 'Numero de identificacao fiscal do cidadao auto excluido.'

id_cidadao = 'Identificador de cidadao auto excluido. NOT NULL'

id_tipocid = 'ID do tipo de identificador de cidadao. 0 BI, 1 CARTAO CIDADAO, 2 PASSAPORTE, 3 NUMERO IDENTIFIC FISCAL, 4 OUTRO. NOT NULL'

nome = 'Nome completo do cidadao auto excluido. NOT NULL'

morada = 'Morada de residencia do cidadao auto excluido. NOT NULL'

cod_postal = 'Codigo postal da morada de residencia do cidadao auto excluido. NOT NULL'

id_nacao = 'Codigo alpha-2 ISO3166 da nacionalidade do cidadao auto excluido. NOT NULL'

email = 'Endereco electronico do cidadao auto excluido. NOT NULL'

id_sitpr = 'Identificador de situacao profissional de cidadao auto excluido. NOT NULL'

motivo = 'Motivo de auto exclusao do jogo online. NOT NULL'

data_ini = 'Data de inicio do periodo de auto exclusao do jogo online. YYYYMMDDHH24MISS. NOT NULL'

data_fim = 'Data de fim do periodo de auto exclusao do jogo online. YYYYMMDDHH24MISS.'

tipo_doc = 'Tipo de documento enviado pelo cidadao auto excluido. B Bilhete de Identidade, C Cartao Cidadao, P Passaporte. NOT NULL'

doc_frente = 'Imagem da frente de documento enviado por cidadao auto excluido.'

doc_verso = 'Imagem do verso de documento enviado por cidadao auto excluido.'

distrito = 'Nome do distrito de residencia do cidadao autoexcluido.'

* Corresponds to the attribute id_cidadao when id_tipocid = 3.

** This attribute must be filled in with two-digit codes from the occupation/professsional status list provided below:

11 Trabalhador por conta propria

22 Trabalhador por conta de outrem

33 Profissional liberal

44 Estudante

55 Reformado

66 Estagiario

77 Sem atividade profissional

88 Desempregado

99 Outra

*** The duration of self-exclusion in months. data_fim attribute calculated using attributes data_ini and duracao.

*** Image binary HEX codes.

209503977
