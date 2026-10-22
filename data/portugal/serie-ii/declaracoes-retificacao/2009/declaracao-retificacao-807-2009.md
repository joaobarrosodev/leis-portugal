---
schema_version: '1.0'
id: pt:dre:2205878:por
title: Declaração de Rectificação n.º 807/2009
short_title: null
summary: Rectificação do Anexo II, do Regulamento n.º 99/2009, publicado no Diário da República, n.º 37, 2.ª série, de 23
  de Fevereiro de 2009
jurisdiction: portugal
territory: null
document_type: declaracao-retificacao
document_type_label: Declaração de Retificação
issuing_authority:
- Icp - Autoridade Nacional de Comunicações, I. P.
proposing_entity: null
official_number: 807/2009
official_date: null
publication_date: '2009-03-16'
publication:
  gazette: Diário da República
  reference: Diário da República n.º 52/2009, Série II de 2009-03-16
  number: '52'
  series: II
  supplement: null
  pages: 10006 - 10012
  pdf_url: https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf
entry_into_force_dates: []
end_of_validity_date: null
legal_status: in_force
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
  dre: '2205878'
  dre_path: /dr/detalhe/declaracao-rectificacao/807-2009-2205878
  internal: pt:dre:2205878:por
source:
  id: dre
  name: Diário da República Eletrónico
  official_url: https://diariodarepublica.pt/dr/detalhe/declaracao-rectificacao/807-2009-2205878
  metadata_url: null
  content_url: https://diariodarepublica.pt/dr/detalhe/declaracao-rectificacao/807-2009-2205878
  consolidated_url: null
  retrieved_at: '2026-10-21T00:00:00Z'
  retrieval_method: Importação inicial do texto do DRE; substituído pela recolha direta quando o diploma é recolhido de novo
  source_modified_at: '2009-03-16T00:00:00Z'
integrity:
  source_sha256: 9a548092e8096b51627c44bbd6ab33caafc63914a816456c5eb6ad9deb5ec27a
  source_sha256_scope: imported_derived_markdown
provenance:
  collector: leis-portugal importador legalize-pt
  collector_version: 0.1.0
  generated_by: leis-portugal import legalize
  generated_at: '2026-10-21T00:00:00Z'
  notes: 'Importação inicial: texto do DRE convertido pelo projeto legalize-pt (https://github.com/legalize-dev/legalize-pt/blob/62e96e31607e96d8b3ce046c69ce34cf6f064634/pt/2009/DRE-2009-807-2205878.md).'
reuse:
  status: permitted
  attribution: Diário da República Eletrónico — Imprensa Nacional-Casa da Moeda
  reference: http://data.dre.pt/eli/dec-lei/83/2016/p/dr/pt/html
  notes: Acesso universal e gratuito ao Diário da República (artigo 3.º do Decreto-Lei n.º 83/2016) e regime de dados abertos
    (Lei n.º 68/2021). A edição eletrónica do DR é a que faz fé.
subjects: []
relationships: []
article_structure:
  article_count: 0
  section_count: 0
  extraction_method: Cabeçalhos Markdown '###### Artigo' do legalize-pt
derived_material:
  machine_generated: true
  notes: Markdown convertido pelo legalize-pt a partir do DRE e normalizado pelo leis-portugal; confirmar na fonte oficial.
validation:
  status: validated
  checked_at: '2026-10-21T00:00:00Z'
  warnings: []
  errors: []
---

# Declaração de Rectificação n.º 807/2009

O [Regulamento n.º 99/2009](https://diariodarepublica.pt/dr/detalhe/regulamento/99-2009-3173165) relativo à disponibilização às autoridades responsáveis pelos serviços de emergência das informações sobre a localização da pessoa que efectua a chamada para o número único de emergência europeu 112, foi publicado no Diário da República n.º 37, 2.ª série, de 23 de Fevereiro de 2009.

Tendo em consideração a versão enviada pelo ICP-ANACOM para a INCM, identificamos que o Anexo II - Especificação do layout do ficheiro BD-112L, foi publicado sem numeração identificadora dos seus vários pontos, uma incorrecção, cuja rectificação entendemos necessária.

Assim:

## ANEXO II — Especificação do layout do ficheiro BD-112L

0 - Introdução

Este documento especifica o "layout" do ficheiro de informação a disponibilizar, pelas Empresas que oferecem redes ou serviços telefónicos acessíveis ao público em local fixo (Empresas), às autoridades responsáveis pelos serviços de emergência, com o objectivo de criar e manter uma Base Dados de suporte à localização das pessoas que efectuam chamadas para o número único de emergência europeu 112.

A Base Dados referida será designada daqui em diante por BD-112L.

A informação a disponibilizar pelas Empresas corresponde à informação disponível nos seus sistemas de cadastro à data de envio.

1 - Abreviaturas

ANSI - American National Standards Institute

CLI - Calling Line Identification

DDI - Direct Dialling In

FTP - File Transfer Protocol

IEC - International Electrotechnical Commission

ISO - International Organization for Standardization

MSN - Multiple Subscriber Number

WGS84 - World Geodetic System Datum 84 (origem geocêntrica de referência)

2 - Formato do Ficheiro de Dados

O ficheiro de informação deve ser do tipo CSV (comma separated value), formato ISO/IEC 8859-1 (ANSI).

Os campos devem ser separados por ";" e não devem exceder os tamanhos indicados na tabela do ponto 5. Caso excedam o tamanho especificado serão truncados.

Todos os campos para os quais não existe informação para o seu preenchimento devem ficar vazios.

O ficheiro deverá ser de formato variável, sendo que o tamanho dos campos indicado no "layout" corresponde ao tamanho máximo que os diferentes campos podem ter, e não a um tamanho fixo dos campos. Os campos nunca deverão ser preenchidos com espaços à direita para perfazer a dimensão máxima.

3 - Periodicidade de envio

Sempre que existam alterações nos dados a disponibilizar, as Empresas devem enviar os respectivos registos até ao final do dia útil seguinte.

Se o volume de informação o justificar podem ser enviados vários ficheiros diários. Podem ainda ser enviados ficheiros nulos (sem registos) caso não existam dados a transmitir, de modo a garantir a periodicidade máxima de 7 dias de calendário como intervalo entre envio de ficheiros.

4 - Nome do Ficheiro de Dados

O formato do nome do ficheiro deve ser:

[Serviço]_[Nome operador]_[Data de envio da informação]_[Identificador do ficheiro].csv

Os componentes do nome do ficheiro não devem exceder os tamanhos indicados na tabela de descrição do header definida no ponto 5.

Exemplo: 112_OPERX_20070601_00001.csv

5 - Descrição do Ficheiro de Dados

5.1 - Desenho do registo

Header:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Detalhe:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Footer:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

5.2 - Notas

5.2.1 - Campos Obrigatórios

Os campos assinalados com (*) são de preenchimento obrigatório.

5.2.2 - Campos Facultativos

Os campos assinalados com (**) não são de preenchimento obrigatório mas a sua ausência não permite a correcta ordenação dos registos quando existe mais do que um número a informar.

5.2.3 - Campo 'Nome Operador' - valores possíveis e regras de preenchimento

Para efeitos da BD-112L, foram atribuídos os seguintes códigos a cada um dos Operadores já registados(1). De acordo com a especificação acordada para a BD-112L, o tamanho máximo destes códigos é de 8 caracteres.

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Estes códigos têm que ser usados com o número de caracteres atribuídos. Por exemplo:

Nome do Ficheiro de Dados: 112_OPR_20070524_00001

Header do Ficheiro de Dados: 112;OPR;20070524;00001

NOTA: Para efeitos de validação da BD-112L, a string "OPR" é diferente de "OPR", pelo que se for usado "OPR"originará um erro com o código do Operador

5.2.4 - Morada

Os campos Designativo de Morada, n.º de Porta, Andar, Apartamento e Edifício, podem ser enviados em campos separados ou concatenados no campo Morada.

5.2.5 - Extensão DDI

Se o telefone é uma extensão DDI o número de Telefone da Linha Principal deve ser obrigatoriamente preenchido e o tipo de serviço deve ser preenchido com "a05".

Nestes casos será enviado no registo de cada DDI a morada da linha principal excepto se existir no cadastro do operador informação mais fidedigna fornecida pelo cliente.

5.2.6 - Coordenadas Geográficas

As Coordenadas Geográficas devem ser codificadas de acordo com a norma WGS84.

Formato: FFGGMMSSSggmmsssRR:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

5.2.7 - Operação

O ficheiro de informação suporta 4 operações distintas:

5.2.7.1 - Telefone novo

Quando o registo ainda não existe na BD-112L.

O campo Operação deve ser preenchido com "n" e deve ser enviado o registo completo.

5.2.7.2 - Alteração de um telefone existente

Quando o registo já existe na BD-112L mas sofreu alterações.

O campo Operação deve ser preenchido com "a" e deve ser enviado o registo completo.

5.2.7.3 - Eliminação de um telefone

Quando o registo existe na BD-112L mas deve ser eliminado.

O campo Operação deve ser preenchido com "e" e não é necessário enviar o registo completo.

A efectiva eliminação dum número da BD-112L só deve ser efectuada após se encontrar garantida uma das seguintes condições:

Ter decorrido o período de quarentena de 3 meses

Ocorra um novo pedido válido de registo deste número, pelo mesmo ou outro operador

5.2.7.4 - Listar todos os registos

Permite a um operador ordenar a listagem de todos os seus registos activos na BD-112L.

O campo Operação deve ser preenchido com "l". Para reconfirmar esta acção e de modo a evitar a listagem total dos registos por uma situação de erro, adicionalmente, o campo mandatório Telefone deve também ser preenchido com o valor "123456789".

Na sequência desta acção, deverá ser gerado pelas autoridades responsáveis pelos serviços de emergência um ficheiro Output com todos os registos activos na BD-112L pertencentes a este operador, no formato idêntico ao ficheiro necessário submeter pelo operador para regenerar a "sua" BD-112L. Este ficheiro deverá ser depositado na pasta de Outbox, à semelhança dos ficheiros de erros e avisos.

6 - Requisitos para o Envio do Ficheiro de Dados

Para o envio dos ficheiros de dados deve ser assegurado o seguinte conjunto de requisitos:

As autoridades responsáveis pelos serviços de emergência providenciam um servidor para depósitos dos ficheiros de informação.

Neste servidor, cada Empresa possuirá uma área exclusiva para depósito dos seus ficheiros (pasta de Inbox).

O acesso às áreas de depósito estará salvaguardado por um "User" e respectiva "Password", sendo permitido à respectiva Empresa a alteração da sua "Password".

As autoridades responsáveis pelos serviços de emergência darão conhecimento individual a cada Operador, do endereço IP e dos respectivos "User" e "Password" de acesso.

A interligação ao servidor será efectuada via FTP através de método de acesso seguro, que permita a encriptação dos dados aquando do seu envio.

Para além da área de depósito, cada Empresa irá também ter assignada uma outra área para recolha das respostas (pasta de Outbox).

7 - Descrição do Ficheiro de Erros e de Avisos

As autoridades responsáveis pelos serviços de emergência implementarão um mecanismo que permita o reporte de erros e avisos sobre os ficheiros e informação depositados pelas Empresas. Para o efeito será gerado um ficheiro de "feedback" por cada ficheiro de dados depositado.

O ficheiro de erros e avisos, à semelhança do ficheiro de dados, deve ser do tipo CSV (comma separated value), no formato ISO/IEC 8859-1 (ANSI) e apresentar um nome que permita uma fácil correlação entre os dois ficheiros:

[Serviço]_[Nome operador]_[Data de envio da informação]_[Identificador do ficheiro].csv

Exemplo:

Ok_112_OPERX_20070601_00001.csv - Ficheiro vazio indicativo da inexistência de erros e avisos

Nok_112_OPERX_20070601_00001.csv - Ficheiro com as situações detectadas de erros ou avisos

7.1 - Desenho do registo

Header:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Detalhe:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Footer:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Tabela de valores dos códigos de erro:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Tabela de valores dos códigos de aviso:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

8 - Descrição do Ficheiro de Mensagens

As autoridades responsáveis pelos serviços de emergência implementarão um mecanismo que permita o reporte de mensagens sobre os ficheiros e informação depositados pelas Empresas.

Este ficheiro contém informações referentes a tentativas de inserções de números de telefone (CLI) já registados na BD-112L por outros operadores.

O ficheiro de mensagens, à semelhança do ficheiro de dados, deve ser do tipo CSV (comma separated value), no formato ISO/IEC 8859-1 (ANSI) e apresentar um nome que permita uma fácil correlação entre os dois ficheiros:

[Serviço]_[Nome operador]_[Data de envio da informação]_[Identificador do ficheiro].csv

Exemplo: CLI_112_OPERX_20070601_00001.csv

8.1 - Desenho do registo

Header:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Detalhe:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Footer:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

Tabela de valores dos códigos de aviso:

[([ver documento original](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf))](https://files.diariodarepublica.pt/2s/2009/03/052000000/1000610012.pdf)

(1) A atribuição de um código a um Operador não significa que este esteja a contribuir para a BD-112L

5 de Março de 2009. - O Vice-Presidente do Conselho de Administração, Alberto Souto de Miranda.
