---
schema_version: '1.0'
id: pt:cnpd:53396
title: Deliberação da CNPD n.º 485/2013
short_title: null
summary: COMISSÃO NACIONAL DE PROTECÇÃO DE DADOS — Recolha e tratamento de informação pela AT constantes de faturas e do ficheiro
  SAF-T
jurisdiction: regulator
territory: null
document_type: deliberacao-cnpd
document_type_label: Deliberação da Comissão Nacional de Proteção de Dados
issuing_authority:
- Comissão Nacional de Proteção de Dados
proposing_entity: null
official_number: 485/2013
official_date: '2013-04-23'
publication_date: null
publication: null
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes:
- 'Entidade: COMISSÃO NACIONAL DE PROTECÇÃO DE DADOS'
- 'Texto obtido por OCR em 31 de 31 página(s) (digitalização): pode ter erros de reconhecimento.'
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
  internal: pt:cnpd:53396
source:
  id: cnpd
  name: Comissão Nacional de Proteção de Dados
  official_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/53396
  metadata_url: https://www.cnpd.pt/decisoes/historico-de-decisoes/?year=2013&type=2
  content_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/53396
  consolidated_url: null
  retrieved_at: '2026-11-12T03:51:06Z'
  retrieval_method: Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API
  source_modified_at: null
integrity:
  source_sha256: 6bac46e60206c15a86cc416f05d6d6147cd4ec165538cdd8890e313820eb8b6f
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal CNPD
  collector_version: 0.1.0
  generated_by: leis-portugal collect cnpd
  generated_at: '2026-11-12T03:51:06Z'
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
  checked_at: '2026-11-12T03:51:06Z'
  warnings: []
  errors: []
---

# Deliberação da CNPD n.º 485/2013

Proc. n.º 1719/2013 | 1
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
Deliberação n.º 485/2013
. Introdução
Chegaram à Comissão Nacional de Protecção de Dados (CNPD) várias queixas relativas a uma alegada violação da privacidade dos cidadãos resultante do envio, pelos comerciantes e prestadores de serviços, dos dados pessoais de faturação para a Autoridade Tributária e Aduaneira (AT), através de um ficheiro de exportação de dados designado SAF-T (PT).
Nas queixas é afirmado que, desde o início do ano de 2013, dados pessoais dos consumidores, designadamente nome, morada, contactos telefónicos, bem como a discriminação dos produtos/serviços adquiridos estão a ser coligidos pela AT, em resultado da obrigação do envio mensal do referido SAF-T.
Foi, também, a CNPD contactada por vários órgãos de comunicação social no sentido de prestar declarações públicas sobre a matéria, designadamente sobre a conformidade com os princípios de proteção de dados do procedimento previsto para o reporte da informação de faturação à AT.
Estando em causa matéria de proteção de dados, promoveu a CNPD a abertura do presente processo.
Na sequência de declarações públicas da abertura do presente processo, a Comissão de Assuntos Constitucionais, Direitos Liberdades e Garantias da Assembleia da
República veio solicitar que, concluídas as averiguações, lhe fossem as mesmas remetidas, habilitando aquela Comissão com as informações necessárias ao exercício das suas atribuições constitucionais.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 2
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
No âmbito dos poderes de investigação e inquérito previstos na alínea a) do n.º 3 do artigo 22.° da Lei n.º 67/98, de 26 de outubro (LPD), foram praticados os atos e realizadas as investigações que se reputaram necessárias para o esclarecimento dos factos:
- Identificação dos programas de faturação certificados pela AT';
- Recolha de um ficheiro SAF-T de exemplo?;
- Validação no Portal das Finanças do ficheiro de exemplo descarregado para verificação da conformidade da estrutura do ficheiro?;
-Verificação junto da SMIprint - Artes Gráficas e Design, Lda do tipo e conteúdo de exportação de dados do ficheiro SAF-T;
- Verificação junto da Arte Viva - Cabeleireiros, Lda do tipo e conteúdo de exportação de dados do ficheiro SAF-T;
- Consulta das faturas carregadas pela Arte Viva, Lda, no interface e-Fatura, através do ficheiro SAF-T do mês de janeiro;
- Verificação do modelo de dados da base de dados do armazenamento da informação de faturação relevante comunicada à AT, quer via webservice, quer por submissão dos dados das faturas no Portal das Finanças, quer pelo carregamento dos ficheiros SAF-T;
- Consulta direta à base de dados onde é armazenada a informação de faturação comunicada à AT;
- Consulta, na AT, ao sistema de ficheiros onde são registados e agregados os
SAF-T submetidos eletronicamente;
- Verificação, na AT, de um ficheiro SAF-T, associado à exportação do mês de janeiro, da faturação de uma farmácia;
- Verificação junto do Portal das Finanças, em E-Fatura*, dos dados das "últimas faturas" de um contribuinte, relativas ao mês de fevereiro de 2013.
' Disponivel em http://www.portaldasfinancas.gov.pt/pt/Out/consultaProgCertificadosM24.action?pagina=34 2 Disponível em http://ftp.sage.pt/sage/saft/Exemplo_SAFT_v1_01.xml 3 Validador de SAF-T http://info.portaldasfinancas.gov.pl/apps/saft-pt01/ .
4 Disponivel em https://www.portaldasfinanças.gov.pt/pt/external/factemipf/painelAdquirente.action .
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 3
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
A AT colaborou com a CNPD, disponibilizando a informação solicitada e facultando o acesso aos sistemas de informação para cabal esclarecimento da situação em averiguação.
De igual modo, as empresas suprarreferidas prestaram toda a colaboração necessária.
II. Factos apurados
¡. Identificação dos programas de faturação certificados pela AT
Em 27 de fevereiro de 2013, foi consultado o Portal das Finanças para verificar quais os programas de faturação certificados pela AT, nos termos da Portaria n.º 363/2010, de 23 de junho.
Aí era indicada a existência de 1708 programas certificados e referido o dia 25 de fevereiro como data da última atualização da listagem.
No dia 15 de março, foi feita nova consulta, verificando-se que se encontravam certificados 1719 programas de faturação, tendo deixado de constar a informação relativa à data da atualização da listagem.
Contudo, pela cronologia das pesquisas efetuadas, é possível afirmar que os 11 novos programas foram adicionados à listagem depois de 25 de fevereiro de 2013.
Da listagem constam os seguintes campos: Nome do programa; Versão; Nome do
Produtor; N.° Certificado; Estado; Data Estado.
De acordo com declarações da AT prestadas aquando da fiscalização realizada no dia 4 de março de 2013, as novas versões dos programas não estão sujeitas a certificação. As aplicações de faturação que já se encontram certificadas só perdem essa certificação na eventualidade de se detetarem "anomalias graves" durante as inspeções.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 4
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
Declararam, também, que a certificação é efetuada por funcionários da carreira inspetiva (inspetores).
ii. Recolha de um ficheiro SAF-T de exemplo
No sentido de aferir quais os campos exigidos no ficheiro SAF-T, foi recolhido, no endereço suprarreferido, um ficheiro exemplo.
A atualidade e conformidade da estrutura do ficheiro foram aferidas através do upload, no interface existente para validação de estruturas de ficheiros SAF-T, disponibilizado no Portal das Finanças.
A estrutura do ficheiro de exemplo foi comparada com a estrutura dos ficheiros remetidos com as queixas que originaram o presente processo. Confirmou-se a sua coincidência.
Foi testada e confirmada a validação após modificações ao conteúdo do ficheiro de exemplo, nomeadamente no «CostumerTaxID» (o NIF foi alterado para 999999990).
Finalmente, alterou-se a estrutura do ficheiro e o sistema não o validou.
Verificação junto da SMIprint - Artes Gráficas e Design, Lda do tipo e conteúdo de exportação de dados do ficheiro SAF-T
Em 26 de fevereiro de 2013, foi feita uma inspeção à SMIprint - Artes Gráficas e
Design, Lda.
Verificou-se que esta empresa utiliza o software de faturação designado por eticadata
ERP, da empresa ETICADATA SOFTWARE, LDA, versão 9.90.08.1665.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 5
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Este software consta da listagem de programas de faturação certificados pela AT, com o certificado n.° 181, de 2-11-20105, embora aí se refira a versão 9.80.
A responsável pela empresa, devidamente identificada no auto de diligência, afirmou que a empresa não usa o conceito de "cliente genérico", sendo, em consequência, todas as faturas emitidas com nome e número de contribuinte do cliente.
Acrescentou, ainda, que os documentos relativos a orçamentos são processados com número de identificação fiscal (NIF) da entidade que pede a consulta.
Foi acedido e copiado o ficheiro SAF-T do mês de janeiro de 2013.
Verificou-se que a área que agrega os atributos e sub-atributos ‹Customer> apresenta todo o universo de clientes da empresa e não apenas aqueles que, no período a que respeita o SAF-T, tiveram qualquer relação comercial com a entidade.
O atributo ‹Customer> é constituído pelos sub-atributos <AccountID>,
‹CustomerTax|D>, ‹CompanyName», <AddressDetail>, «City>, «PostalCode> e
‹Country>.
No atributo ‹ProductDescription>, associado a cada produto que consta numa fatura, é apresentada a descrição original desse produto, como, por exemplo "Cartões Visita c.telado, imp. 4/4cor.".
No atributo ‹Description>, associado a cada produto, é apresentada a descrição modificada no momento da emissão da fatura, correspondendo a informação adicional ao trabalho efetuado, como seja "Cartões Visita c.telado, imp. 4/4cor. - Tiago Manso", deste modo identificando o nome que deve constar nos cartões de visita.
Confirmou-se que a informação exportada para a AT identifica o cliente, bem como o produto adquirido/serviço prestado correspondente à fatura, independentemente do cliente ter ou não solicitado a inclusão do NIF na fatura.
§ Disponível em http://www.portaldasfinancas.gov.pt/pt/consultaProgCertificadosM24.action
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 6
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Verificou-se que os dados das entidades que solicitaram orçamentos, ainda que nunca tenham sido clientes da empresa, também são incluídos no ficheiro SAF-T.
Constatou-se que existia o cliente identificado como "Desconhecido", com o NIF "000099999". No entanto, não estavam associadas quaisquer faturas a este cliente ou
NIF, no período a que se reporta o ficheiro.
iv. Verificação junto da Arte Viva - Cabeleireiros, Lda do tipo e conteúdo de exportação de dados do ficheiro SAF-T
Em 27 de fevereiro de 2013, foi feita uma inspeção à Arte Viva - Cabeleireiros, Lda.
Verificou-se que esta empresa utiliza o software de faturação designado por Sublime, da empresa Sublime Plateia, Lda, versão 1.2.1.14.
Este software consta da listagem de programas de faturação certificados pela AT, com o certificado n.° 1354, de 4-10-20116, embora aí se refira a versão 1.02.0001.
Foi acedido e copiado o ficheiro SAF-T resultante da exportação da faturação do período compreendido entre 1 e 31 de janeiro de 2013 e do período compreendido entre 1 e 27 de fevereiro de 2013.
Verificou-se que na introdução de clientes em sistema é usado o número "999999990", correspondente a consumidor final, para o atributo ‹CustomerTaxID>, nos casos em que o cliente não solicita a introdução do seu NIF na fatura.
Apesar da utilização daquele número de "consumidor final", cada elemento
‹Customer> do ficheiro SAF-T apresenta a designação do cliente no atributo
‹CompanyName>, bem como a respetiva morada:
‹Customer>
• Disponível em http://www.portaldasfinancas.gov.pt/pt/consultaProgCertificadosM24.action
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 7
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
<CustomerID>5</CustomerID>
‹AccountiD>Desconhecido</AccountID>
<CustomerTaxID>999999990</CustomerTaxID>
‹CompanyName>Patricia Serdeira </CompanyName>
‹BillingAddress>
<StreetName>Praceta Do Choupal, Nº30, 2° A</StreetName>
<AddressDetail > Praceta Do Choupal, N°30, 2° A </AddressDetail>
‹City>Parede</City>
<PostalCode>0000-000</PostalCode>
‹Country>PT</Country>
</BillingAddress>
</Customer>
Verificou-se que a área que agrega os atributos de ‹Customer> apresenta todo o universo de clientes da empresa e não apenas aqueles que, no período a que respeita o SAF-T, tiveram qualquer relação comercial com a entidade.
No atributo ‹ProductDescription>, associado a cada produto que consta numa fatura, é apresentada a descrição original desse produto (v.g. "Coloração Normal", "Limpeza de pele", "Perna inteira", "Perna Inteira + Virilha Sra", "Perna Inteira + Virilha Sr").
Confirmou-se que a informação exportada para a AT identifica o cliente, bem como o produto adquirido/serviço prestado correspondente à fatura.
Constatou-se que existia o cliente identificado como Consumidor Final", com o NIF "999999990", correspondendo ao «Costumer|D> "C24". No entanto, apesar da grande maioria das faturas não ter registado o NIF do cliente, a identificação, a morada e os produtos/serviços constam no SAF-T analisado e transmitido para a AT.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 8
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Consulta, na AT, ao sistema de ficheiros onde são registados e agregados os SAF-T submetidos eletronicamente
Em 4 de março de 2013, nas instalações da AT do Ed. Satélite, em Lisboa, foi verificado que os ficheiros SAF-T submetidos são mantidos num repositório de ficheiros, onde ficam a aguardar processamento.
A CNPD verificou que os SAF-T recebidos contêm toda a informação relativa à faturação, com discriminação dos produtos e, em grande parte dos casos, com a identificação dos clientes.
A CNPD verificou, também, situações sem NIF, aí constando o número 999999990, mas com nome e morada do adquirente.
Foi descrito, pela AT, o processamento efetuado à informação recebida, que consiste num mecanismo automático onde cada ficheiro SAF-T é lido e o seu conteúdo registado em base de dados. Este processamento é desencadeado por um batch configurado para ter uma periodicidade diária.
A base de dados referida é designada por factemi. Foi disponibilizada à CNPD, estando junto aos autos, a estrutura desta base de dados.
Do processamento atrás referido, informou a AT que não é registada em base de dados qualquer informação dos atributos ‹Product> do ficheiro SAF-T, acrescentando que a informação relativa ao produto que é registada em base de dados é recolhida dos sub-atributos ‹Line> de cada fatura e refere-se unicamente à base tributável, valor do IVA e valor total do artigo.
Clarificou que, relativamente à informação do adquirente, apenas é registado em base de dados o NIF e a informação recolhida nos atributos ‹Customer> do ficheiro SAF-T.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 9
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
Resumiu que apenas regista em base de dados a informação relativa à identificação do adquirente (NIF), do comerciante (NIF), identificação da fatura, preço total, taxa de
IVA e montante de IVA e que a restante informação recebida através dos ficheiros
SAF-T é ignorada.
Uma vez processados os ficheiros SAF-T, os dados das faturas ficam disponíveis para as entidades emitentes e adquirentes, via Portal das Finanças, no e-Fatura?.
Existe um interface, desenvolvido para uso interno, que, foi afirmado, tem como finalidade fazer pesquisas sobre a base de dados referida.
Foi, ainda, declarado que a informação recebida dos ficheiros SAF-T é excessiva para a finalidade e até contraproducente relativamente à exigência computacional que representa para os sistemas da AT.
Apesar de haver um processamento diário de dados, a carga de ficheiros, a quantidade de informação constante em cada um e as operações a efetuar para a extração das informações necessárias, não permitem que todos os ficheiros sejam processados no próprio dia.
Foi afirmado que, à data da inspeção, estava em fase final o processamento da informação de faturação de janeiro de 2013.
vi.
Consulta direta à base de dados onde é armazenada a informação de faturação comunicada à AT
Em 4 de março, nas instalações da AT do Ed. Satélite, em Lisboa, a CNPD consultou a base de dados, designada por factemi.
7 Acessível em https://www.portaldasfinancas.gov.pt/pt/external/factemipf/home.action
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 10
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
Confirmou-se que a estrutura da base de dados coincidia com o modelo anteriormente disponibilizado.
Selecionaram-se e consultaram-se as seguintes tabelas:
- GDT_documento_comercialo (contem todas as faturas e outros documentos comerciais comunicados à AT);
- GDT_registo_mensal_faturaso (informação global sobre as faturas de cada emitente);
-GDT_ficheiro_auditoria0 (regista informação identificativa do ficheiro SAF-T);
- GDT_parametrosO (indica o tipo de documento).
Foram consultados aleatoriamente registos de cada tabela, de modo a confirmar se a informação aí registada coincidia com o modelo de dados disponibilizado, o que se verificou.
vii.
Verificação, na AT, de um ficheiro SAF-T, associado à exportação do mês de janeiro, da faturação de uma farmácia
Em 4 de março de 2013, nas instalações da AT do Ed. Satélite, em Lisboa, a CNPD solicitou a consulta do ficheiro SAF-T de janeiro de 2013 de uma farmácia, por referência a um cliente, tendo a CNPD disponibilizado o NIF desse cliente.
Para agilizar a consulta, uma vez que se conhecia a identificação da entidade emitente da fatura, a procura foi restringida ao ficheiro SAF-T da Farmácia Bento Lino, Lda., com o NIF 505896028.
Foi identificado apenas um ficheiro SAF-T associado à Farmácia Bento Lino, Lda. e circunscrito o registo associado ao NIF disponibilizado pela CNPD.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 11
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
A informação constante identificava o NIF e nome do adquirente, os produtos adquiridos (por nome comercial do medicamento), quantidade e dados relativos ao preço e IVA.
Os dados relativos a esta fatura já se encontravam disponíveis no Portal da Finanças, em E-Fatura.
Foi igualmente verificado, no SAF-T da farmácia que existiam centenas de registos de faturas com discriminação do medicamento adquirido, por referência a um adquirente identificado e em muitos casos, com indicação da morada completa.
viii.
Verificação das faturas disponibilizadas no E-Fatura do Portal das
Finanças
Por acesso ao E-Fatura, por referência a um contribuinte identificado nos autos, constatou-se que são disponibilizadas três faturas. Estas faturas foram emitidas por entidades que não estão incluídas nas atividades económicas previstas no n.º 5 do artigo 3.° do Decreto-Lei n.º 198/2012, de 24 de agosto.
No quadro de apresentação da informação, além da identificação do comerciante emitente, do tipo (de documento), do n.º de fatura, da data de emissão, do IVA suportado e do valor total, existe um campo relativo ao setor (de atividade) onde se lê "outro".
É o caso de faturas da EPAL - Empresa Portuguesa de Águas Livres, SA e do Centro
Português de Serigrafia, Lda.
Relativa ao benefício fiscal obtido e ao correspondente IVA suportado a informação é de 0€.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 12
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
II.
Enquadramento legal a) Da obrigação de reporte à AT
O n.º 1 do artigo 172.° da Lei n.º 64-B/2011, de 30 de dezembro, que aprovou o orçamento do Estado para o ano de 2012 (LOE 2012), concede uma autorização legislativa ao Governo para instituir um regime que regule a transmissão eletrónica das faturas para reforço do combate à fraude e à evasão fiscal.
O n.º 2 do mesmo artigo, que estabelece o sentido e extensão da autorização, refere, na alínea h), a criação de uma dedução em sede de IRS, IMI ou IUC correspondente a "um valor até 5% do IVA suportado, e efetivamente pago, pelos sujeitos passivos na aquisição de bens e serviços".
O Decreto-Lei n.º 198/2012, de 24 de agosto, que concretiza a autorização legislativa concedida ao Governo, cria medidas de controlo da emissão de faturas e respetivos aspetos procedimentais, bem como um incentivo de natureza fiscal à exigência daqueles documentos por adquirentes que sejam pessoas singulares, através da alteração do Estatuto dos Benefícios Fiscais.
O incentivo corresponde à dedução à coleta do IRS do valor de 5% do IVA constante em faturas emitidas com NIF, nos setores de atividade abrangidos, com o valor máximo de 250 € por agregado familiar. As atividades abrangidas são a restauração e alojamento, cabeleireiros e reparação de veículos automóveis e de motociclos.
De entre as medidas de controlo de emissão das faturas está a obrigação dos sujeitos passivos de IVA comunicarem à AT, por transmissão eletrónica de dados, os elementos das faturas (cf. n.º 1 do artigo 3.° do Decreto-Lei n.º 198/2012, de 24 de agosto).
Nas FAQ® disponibilizadas no Portal das Finanças, à pergunta Em que consiste o novo regime de faturação? é dada a resposta Consiste na obrigatoriedade de emissão de 8 Disponível em http://info.portaldasfinanças.gov.pt/pt/faturas/faqs_cons.html.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 13
COMISSAO NACIONAL
DE PROTECÇAO DE DADOS fatura por todos os sujeitos passivos de IVA em todas as transmissões de bens ou prestações de serviços, incluindo nos casos em que os consumidores finais não as exijam, bem como na obrigação de comunicação de todos os elementos das faturas à
Autoridade Tributária e Aduaneira (AT).
A transmissão pode ser feita, em tempo real, por webservice, mediante a remessa do ficheiro SAF-T (PT), por inserção direta no Portal das Finanças, ou por outra via eletrónica a definir por Portaria do Ministro das Finanças.
b) Da Certificação dos Sistemas de Faturação
A utilização de programas eletrónicos de faturação implica a sua prévia certificação pela AT, com o objetivo de evitar a adulteração dos dados registados e dessa forma combater a evasão fiscal.
A Portaria n.º 363/2010, de 23 de junho, veio, nos termos do n.º 8 do artigo 123.° do
Código do Imposto sobre o Rendimento das Pessoas Coletivas, regulamentar essa certificação e alterar a estrutura de dados do ficheiro SAF-T.
Aí se definiram regras para garantir a fiabilidade da informação registada e só os programas informáticos que observassem os requisitos estabelecidos poderiam ser objeto de certificação.
Os requisitos cumulativos exigidos para a certificação, de acordo com o artigo 3.° da
Portaria n.º 363/2010, de 23 de junho, eram:
- Possibilidade de exportação do ficheiro SAF-T;
- Existência de encriptação através de um algoritmo de cifra assimétrica e de uma chave privada do conhecimento exclusivo do produtor do software;
- Existência de controlo de acesso, obrigando-se a mecanismos de autenticação de cada utilizador;
9 Sublinhado nosso
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 14
COMISSAO NACIONAL
DE PROTECÇAO DE DADOS
- Impossibilidade de, local ou remotamente, alterar a informação de natureza fiscal sem registar tal facto junto da informação original.
Para tal, as empresas produtoras de software, antes da comercialização dos programas de faturação, deveriam enviar à então DGCI uma declaração de modelo oficial aprovada por despacho do Ministro das Finanças e a chave pública que permitia validar a autenticidade e integridade do conjunto de dados requeridos, assinados com a respetiva chave de encriptação privada (cf. alíneas a) e b) do artigo 4.° da Portaria n.º 363/2010, de 23 de junho).
Esta Portaria veio a ser alterada pela Portaria n.º 22-A/2012, de 24 de janeiro, que, no que releva para a presente apreciação, acrescentou um requisito cumulativo aos já mencionados, requisito esse que consiste na observância dos "demais requisitos técnicos aprovados por despacho do diretor-geral da Autoridade Tributária e
Aduaneira" e alargou o seu âmbito de aplicação objetivo e subjetivo.
c) Do ficheiro SAF-T 1. Finalidade originária
O ficheiro SAF-T foi criado para fins de auditoria.
Tal como consta do preâmbulo da Portaria 321-A/2007, de 26 de março, os registos de faturação " são objecto de verificação pelos serviços de inspecção no âmbito das suas competências de controlo da situação tributária dos contribuintes.
Tendo em vista facilitar tal tarefa, face à diversidade de sistemas [de faturação], ..., a criação de um ficheiro normalizado com o objectivo de permitir uma exportação fácil, e em qualquer altura, de um conjunto predefinido de registos contabilísticos, num formato legível e comum, independente do programa utilizado, sem afectar a estrutura interna da base de dados do programa ou a sua funcionalidade.
A adopção deste modelo proporciona às empresas uma ferramenta que permite satisfazer os requisitos de obtenção de informação dos serviços de inspecção e facilita o seu tratamento, evitando a necessidade de especialização dos auditores nos
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 15
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS diversos sistemas, simplificando procedimentos e impulsionando a utilização de novas tecnologias".
Ademais, nos termos do artigo 1.°, in fine, da referida Portaria, tal ficheiro seria disponibilizado "sempre que solicitado pelos serviços de inspecção, no âmbito das suas competências".
Daqui resulta que este ficheiro, no âmbito daquela Portaria, constituía um instrumento de auditoria, apto a permitir a fiscalização do cumprimento das obrigações tributárias.
A estrutura de dados do ficheiro foi alterada com a Portaria n.º 1192/2009, de 8 de outubro, de modo a adaptá-lo ao Novo Sistema de Normalização Contabilística e a compatibilizá-lo com a obrigação de certificação dos sistemas de faturação.
A estrutura do ficheiro SAF-T inclui, entre outros, a identificação e contactos do vendedor/prestador de serviços, dados de identificação e contacto do cliente e do fornecedor (NIF, nome, morada, telefone, fax, e-mail e website), dados relativos ao produto (identificador do produto, família do produto, descrição do produto e respetivo código), dados das faturas/documentos de transporte e dados relativos ao pagamento.
Este ficheiro importa os dados dos programas de faturação e de gestão de clientes. De salientar que os programas de gestão de clientes contêm informação que excede a informação necessária para a finalidade do SAF-T.
2.Da utilização do SAF-T para comunicação dos elementos das faturas
A obrigação de comunicação dos elementos das faturas foi criada nos termos do disposto no artigo 3.° do Decreto-Lei n.º 198/2012, de 24 de agosto.
Nos termos deste artigo, tal obrigação cumpre-se por uma das seguintes vias:
- Por transmissão eletrónica de dados em tempo real, integrada em programa de faturação eletrónica, através de webservice,
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 16
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
- Por transmissão eletrónica de dados, mediante remessa de ficheiro normalizado estruturado com base no ficheiro SAF-T, contendo os elementos das faturas;
- Por inserção direta no E-Faturas;
- Por via eletrónica, através da submissão válida, no Portal das Finanças, de modelo oficial aprovado pela Portaria n.° 426-A/2012, de 28 de dezembro.
Os sujeitos passivos que estejam obrigados a produzir o ficheiro SAF-T, apenas podem utilizar uma das duas primeiras modalidades.
Foi assim alterada a finalidade originária deste ficheiro.
No Manual de Integração de Software"° para comunicação das faturas, emitido pela
Autoridade Tributária (AT), são dadas indicações aos sujeitos passivos da obrigação de comunicação das faturas.
No ponto 2.2, sob a epígrafe Comunicação das Faturas por SAF-T (PT) são mencionados os passos devidos para a comunicação em causa, a saber:
- Extração do ficheiro mensal SAF-T (PT);
- Envio do ficheiro no Portal das Finanças, site e-fatura".
Acrescenta, no ponto 2.2.1, relativo à extração do ficheiro SAF-T (PT), que "No início do mês seguinte, o sujeito passivo (comerciante) extrai do seu sistema de faturação o ficheiro SAF-T (PT) para o efeito de comunicação à AT das faturas emitidas no mês anterior.
O ficheiro XML para este efeito deve conter as seguintes tabelas do SAF-T (PT) e os respetivos elementos definidos na estrutura de dados disponível no seguinte endereço:
http://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/NEWS_SAF-T_PT.htm 1 - Cabeçalho (Header);
1° Disponível em http://info.portaldasfinancas.gov.pt/NR/rdonlyres/AC494AE7-7E41-41C9-991B-15C3F0126ABF/O/ComunicacaodosdadosdasfaturasaAT.pdf , versão com última atualização de 5-2-2013.
11 Página n.° 6 do Manual de Integração de Software
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 17
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS 2.2 - Tabela de Clientes (Customer);
2.5 - Tabela de Impostos (TaxTable);
4.1 - Documentos Comerciais de Clientes (SalesInvoice).".
Importa salientar a falta de clareza e até mesmo contradição nas instruções supra indicadas. Senão vejamos:
No ponto 2.2 é expressamente referida a diretriz de extração do ficheiro SAF-T e envio do ficheiro (não sendo referido qualquer outro ficheiro, apenas se pode ler esta indicação por referência ao ficheiro SAF-T);
No ponto 2.2.1 é referido: "o ficheiro XML para este efeito deve conter as seguintes tabelas do SAF-T", o que permite, com esforço interpretativo, afirmar que o ficheiro em causa é outro que não o SAF-T. No entanto, de entre as "tabelas" indicadas como obrigatórias deste ficheiro XML está a "tabela" 4.1
Sales/nvoices que inclui o produto/serviço adquirido.
Mais acrescenta que " Para efeitos de otimização 12 de envio do ficheiro, este deve conter apenas:
• Os Documentos Comerciais com data movimento do período em extração (Mês, Dia);
• Os Clientes que tenham referência nos Documentos Comerciais (deixando de fora os que não efetuaram transações comerciais no período);".
A mesma recomendação é formulada aos produtores de programas. Na página 16 do documento pode ler-se:
i Para otimização do envio, os produtores de software devem considerar implementar as seguintes características nos seus produtos:
1. Extrair a informação por mês ou por indicação de um determinado período (datas, por dia, etc.);
2. Extrair apenas a informação da tabela de clientes que tenham referência em documentos comerciais desse ficheiro, não incluindo os restantes;
12 Sublinhado nosso
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 18
COMISSAO NACIONAL
DE PROTECÇÃO DE DADOS
Estas otimizações têm dois efeitos: reduzem o tamanho do ficheiro e consequentemente ocupam menos espaço em disco; e consequentemente reduzem o tempo necessário para processar cada ficheiro.
Com redução do tamanho poupa-se espaço em disco e consumo de memória de cada processamento efetuado. Reduzindo a informação ao que é relevante em cada ficheiro permite acelerar o tempo de extração, validação local e consequentemente o tempo total de comunicação de faturas à AT.".
Apesar de no preâmbulo do Decreto-Lei n.° 198/2012, de 24 de agosto, se referir expressamente que será disponibilizada gratuitamente uma aplicação informática destinada a extrair dos ficheiros SAF-T os elementos relevantes das faturas a serem enviadas à AT, a verdade é que tal aplicação é do desconhecimento quer da CNPD, quer dos comerciantes, quer da própria AT.
Contactado o número telefónico de apoio ao E-Fatura 707 206 707, a operadora, quando questionada sobre a existência de tal aplicação, referiu desconhece-la e afirmou que a obrigação consistia no envio do próprio ficheiro SAF-T.
Embora o artigo 3° do Decreto-Lei n.º 198/2012 estabeleça que o procedimento da alínea b) do n.º 1 é a remessa de ficheiro normalizado com base no ficheiro SAF-T, todo o feixe de orientações da AT13 vai no sentido de envio do próprio ficheiro SAF-T, criando nos comerciantes a convicção desta obrigação.
IV. Apreciação a) O tratamento de dados pessoais resultante da comunicação
Nos termos da LPD, qualquer operação sobre dados pessoais integra o conceito de tratamento de dados pessoais, tal como descrito na alínea b) do artigo 3.° da referida lei.
13 Veja-se, como exemplo, no endereço https://www.portaldasfinancas.gov.pt/pt/external/factemipf/home.action o comando "Enviar Ficheiro SAF-T (PT)".
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 19
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Os ficheiros SAF-T enviados pelos comerciantes são arquivados numa diretoria do sistema de ficheiros, consubstanciando, pelo menos desde o momento do seu recebimento, um tratamento de dados pessoais da responsabilidade da AT.
É através de operações sobre estes dados pessoais que a AT extrai a informação para a base de dados factemi, que permite disponibilizar a informação no E-Fatura.
Assim, não pode deixar de concluir-se que a AT é responsável pelo tratamento de dados pessoais desde o recebimento da informação de faturação dos comerciantes, seu arquivamento, processamento posterior, disponibilização parcial em rede, bem como a conservação dos demais.
b) Natureza dos dados
A CNPD já havia referido no âmbito do Parecer n.º 44/2012, emitido a propósito do processo legislativo conducente à aprovação do Decreto-Lei n.º 198/2012, que a AT passaria a dispor de informação relativa a serviços e bens adquiridos por pessoas singulares, o que configuraria um tratamento de dados pessoais sensíveis, porque atinente à vida privada dos cidadãos.
A afirmação produzida no referido Parecer partia do pressuposto que apenas seriam tratados os dados elencados no n.º 4 do artigo 3.° do Decreto-Lei n.º 198/2012.
Todavia, a partir do momento em que se constatou que o ficheiro SAF-T estava a ser remetido na integra para a AT, concluiu-se que o universo de dados recebidos abrangia a discriminação de todas as prestações de serviços e bens adquiridos, pelo que, quando por referência a uma pessoa individual, a CNPD não tem dúvidas em afirmar que concretiza um tratamento de dados pessoais altamente intrusivo na esfera privada dos cidadãos, com uma dimensão quase universal.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 20
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Isto mesmo foi confirmado na inspeção à AT, designadamente quando se acedeu a informação existente no repositório de ficheiros, relativa ao SAF-T de uma farmácia, que discrimina, com o NIF e nome de um contribuinte, os medicamentos adquiridos.
Acresce que tal envio, como adiante se demonstrará, ocorre ao arrepio do diploma habilitante.
Do mesmo modo, confirmou-se que a AT está a receber de instituições prestadoras de cuidados de saúde, designadamente hospitais, informação das faturas com identificação do titular dos dados (nome e NIF), sem que este seja sujeito passivo de
IVA ou tenha solicitado a inclusão do seu NIF na fatura.
Ademais a AT pratica operações sobre estes dados pessoais, na medida em que os seleciona e exporta para a base de dados factemi, disponibilizando-os no Portal das
Finanças e tornando-os acessíveis para a generalidade dos funcionários da AT no interface dedicado para esse efeito.
Viram-se, assim, confirmados os receios transmitidos à CNPD nas queixas que originaram o presente processo.
c) Mecanismos Disponibilizados para a Comunicação
Conforme já se referiu, a obrigação de comunicação é cumprida pelas vias indicadas no artigo 3.° do Decreto-Lei n.° 198/2012.
Particulares reservas se suscitam relativamente ao mecanismo de comunicação utilizado por remessa de ficheiro normalizado estruturado com base no ficheiro SAF-T, porquanto foi possível apurar, no decurso do presente processo, que o que está a ser enviado é o próprio ficheiro SAF-T.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 21
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Tal operação, por implicar o envio de mais informação do que a prescrita no n.º 4 do artigo 3° do Decreto-Lei n.º 198/2012, viola, desde logo, o princípio da legalidade, sendo claramente desproporcional face à finalidade que o legislador pretendeu obter.
Assim, para o cumprimento desta obrigação, a lei é taxativa e indica quais os dados de cada fatura que devem ser comunicados. São eles: NIF do emitente; n.º e data da fatura; tipo de documento, NIF do adquirente que seja sujeito passivo de IVA, quando tenha sido inserido no ato de emissão, ou quando este, não sendo sujeito passivo de
IVA, o solicite; valor tributável; taxas aplicáveis; motivo justificativo da não aplicação de imposto; montante de IVA liquidado.
Qualquer dado pessoal tratado além dos transcritos fere de ilegalidade o tratamento em análise.
Para avaliação deste mecanismo de comunicação da informação não é despicienda a circunstância de os sistemas de faturação e de gestão de clientes estarem integrados ou se interrelacionem.
Assim, mesmo nas situações em que o cliente tenha solicitado anonimato, por via da inclusão da designação Consumidor Final e do número 999 999 990, e mesmo que o comerciante inscreva tais dados na fatura, os sistemas, automaticamente, podem importar da base de dados de clientes informação de identificação e morada do consumidor, o que compromete a proteção de dados.
São estes automatismos que justificam que, no caso do cabeleireiro fiscalizado, o simples facto de a prestação de serviço ou o bem adquirido estar associado a uma ficha de cliente, implique que o SAF-T extraia a identificação da base de dados de clientes, mesmo que esta informação não conste da fatura.
A CNPD alertou, no âmbito do Parecer n.º 44/2012, para a necessidade de correspondência cabal com o modelo de dados previsto no n.º 4 do artigo 3.° do
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 22
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Decreto-Lei n.º 198/2012, "para evitar o envio de informação adicional, mais detalhada, sobre os serviços adquiridos por pessoa singular".
Apesar do que é referido no preâmbulo do Decreto-Lei n.º 198/2012, não foi disponibilizada pela AT qualquer aplicação informática destinada a extrair dos ficheiros
SAF-T das empresas os elementos relevantes das faturas a serem enviadas à AT.
Contrariamente, as orientações da AT apontam para a submissão do próprio ficheiro
SAF-T.
A inexistência daquela aplicação informática, que permitiria a extração da informação relevante das faturas, conjugada com a prática aceite pela AT de recebimento do ficheiro SAF-T na íntegra, leva à conclusão que o meio previsto na alínea b) do n.º 1 do artigo 3.°, tal como se encontra em execução, não é meio idóneo para o cumprimento da obrigação fiscal.
Se, para a finalidade originária de auditoria, a estrutura do ficheiro SAF-T é a adequada, na medida em que tal informação é mantida pelos agentes económicos e o acesso da AT é pontual no âmbito das suas competências de inspeção, para a finalidade de combate à informalidade e evasão fiscal, a centralização na AT de toda a informação dos produtos consumidos pelos cidadãos, conduz a que o crivo da necessidade resvale no excesso e desproporcionalidade do resultado.
d) Do acesso à informação enviada através do ficheiro SAF-T
A informação remetida através dos ficheiros SAF-T fica guardada num repositório de ficheiros, para posterior processamento.
Foi descrito, pela AT, o processamento efetuado à informação recebida, que consiste num mecanismo automático onde cada ficheiro SAF-T é lido e o seu conteúdo
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 23
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS registado em base de dados. Este processamento é desencadeado por um batch configurado para ter uma periodicidade diária.
A informação das faturas que contenham NIF do adquirente, se este não for sujeito passivo de IVA, é importada para uma base de dados, designada por factemi e acessível quer através de um interface próprio para utilização da AT, quer no Portal das Finanças, no E-Fatura.
Contudo, a informação original, que corresponde ao ficheiro SAF-T enviado, mesmo após esse processamento, é conservada. Isto foi verificado pela CNPD na inspeção que efetuou.
A informação da fatura da farmácia referida em vii. do ponto II, relativo aos factos apurados, foi acedida no repositório de ficheiros e, apesar de já estar disponível no E-
Fatura, permanecia no dito repositório. Realça-se que o ficheiro SAF-T que continha a fatura em causa respeitava ao mês de janeiro e a CNPD acedeu a esse ficheiro em março.
Embora não tenha sido constituído qualquer interface para acesso ao repositório e a generalidade dos funcionários da AT não aceda à informação, não podem restar dúvidas de que a informação aí constante é acessível. Tanto assim é, que a CNPD teve acesso à informação e tal acesso foi-lhe dado pelo funcionário indicado pela AT.
e) Do princípio da boa-fé na relação entre o Estado e os cidadãos
Compete ao Estado, quer ao Estado-Legislador, quer ao Estado-Administração, ponderar as implicações das medidas que adota, sobretudo quando destas podem derivar restrições a direitos fundamentais.
Se neste processo o Estado-Legislador ponderou tais implicações, desde logo limitando as categorias de dados objeto de comunicação e prevendo a disponibilização gratuita de mecanismos adequados ao cumprimento da obrigação de modo
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 24
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS proporcional, já o Estado-Administração não cuidou de o fazer, quer ao nível dos procedimentos recomendados, quer pela mera circunstância de admitir receber e conservar dados que o legislador teve o cuidado de salvaguardar, excluindo-os de tratamento.
Não pode o Estado-Administração aligeirar a sua responsabilidade, fazendo-a recair exclusivamente sobre os comerciantes. A verdade é que estes são induzidos, como acima se demonstrou, a enviar os próprios ficheiros SAF-T.
Acresce que a utilização de programas eletrónicos de faturação implica a sua prévia certificação pela AT, com o objetivo de evitar a adulteração dos dados registados e dessa forma combater a evasão fiscal. Tal certificação abrange o ficheiro SAF-T.
A Portaria n.º 363/2010, de 23 de junho, veio, nos termos do n.º 8 do artigo 123.° do
Código do Imposto sobre o Rendimento das Pessoas Coletivas, regulamentar essa certificação e alterar a estrutura de dados do ficheiro SAF-T, aí se definindo as regras para garantir a fiabilidade da informação registada e só os programas informáticos que observassem os requisitos estabelecidos poderiam ser objeto de certificação.
Um regime de certificação pública 4 tem como efeito a criação de uma convicção generalizada de que o meio é o adequado para cumprir os requisitos legais.
14 Atenta a natureza e os efeitos desta certificação pública, a CNPD não pode deixar de referir que a certificação de sistemas informáticos obriga a uma especialização nessa área que ultrapassa o nível do utilizador.
Por outro lado, a prática de não certificar novas versões do programa original gera insegurança jurídica e risco para a qualidade da informação, comprometendo a própria finalidade da certificação.
Acresce que, se o utilizador tiver acesso à sua própria chave privada, apesar de esta estar hard-coded, tem a possibilidade de gerar as exportações, modificar os valores das faturas a enviar à AT e posteriormente gerar nova assinatura sobre os valores modificados, tornando a exportação "'autêntica".
Na medida em que se admite a utilização de programas de faturação desenvolvidos pelas próprias empresas que os irão utilizar, estas têm total controlo sobre a sua chave privada de encriptação.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 25
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
Os comerciantes, ao enviar o ficheiro SAF-T, estão confiantes de que estão a cumprir uma obrigação legal.
f) Da disponibilização no Portal das Finanças das faturas relativas ao incentivo fiscal
O Decreto-lei n.º 198/2012 veio criar um incentivo fiscal que corresponde à dedução à coleta do IRS do valor de 5% do IVA constante em faturas emitidas com NIF, nos setores de atividade abrangidos, com o valor máximo de 250 € por agregado familiar.
As atividades abrangidas são a restauração, alojamento e similares, cabeleireiros e reparação de veículos automóveis e de motociclos. É condição para a obtenção deste benefício que as pessoas singulares estejam identificadas como adquirentes de bens ou serviços através do NIF.
O n.° 5 do artigo 3° do Decreto-Lei n.º 198/2012 refere expressamente a obrigação da
AT de disponibilizar às pessoas singulares, no Portal das Finanças, os elementos das faturas que titulem prestações de serviço emitidas por sujeitos passivos enquadrados, para efeitos fiscais, de acordo com os setores de atividade ali referidos.
Ou seja, após a receção dos dados enviados pelos agentes económicos nos termos já mencionados, a AT, mensalmente, selecionaria as faturas de emitentes enquadrados nos setores de atividade indicados e disponibilizaria no E-Fatura do Portal das
Finanças os elementos das faturas elegíveis para o incentivo fiscal.
Ora, verificou-se que são disponibilizados naquela sede elementos de faturas relativos a qualquer setor de atividade, desde que delas conste o NIF do adquirente, se este não for sujeito passivo de IVA.
A AT, ao receber informação da faturação, independentemente do setor de atividade a que respeita, processa-a e disponibiliza-a, tendo sido criada a designação "outro" para os setores de atividade que estão fora da previsão legal.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 26
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS
Tal tratamento extravasa, também, o princípio da legalidade e os princípios de proteção de dados.
V. O projeto de decisão
Face à factualidade apurada e atenta a sua gravidade, a CNPD notificou o Diretor-
Geral da Autoridade Tributária e Aduaneira para, nos termos do disposto no n.º 1 do artigo 100.° do Código do Procedimento Administrativo, se pronunciar, querendo, no prazo de dez dias sobre o projeto de decisão, o qual previa a deliberação, ao abrigo da alínea b) do n.º 3 do artigo 22.° da LPD, nos seguintes termos:
- Ordenar a destruição imediata dos dados pessoais recolhidos em violação do disposto no n.º 4 do artigo 3.° do Decreto-Lei n.º 198/2012, de 24 de agosto;
- Ordenar a destruição imediata dos dados pessoais existentes na base de dados designada por factemi e disponibilizados no E-Fatura relativos a faturas emitidas por sujeitos passivos que não se encontrem enquadrados, para efeitos fiscais, nos setores de atividade previstos nas alíneas a) a d) do n.º 5 do artigo 3.° do Decreto-Lei n.º 198/2012, de 24 de agosto;
- Ordenar a proibição temporária de recebimento de informação do ficheiro
SAF-T para cumprimento da obrigação legal prevista na alínea b) do n.° 1 do artigo 3.° do Decreto-Lei n.° 198/2012, até à disponibilização gratuita pela AT da aplicação informática destinada a extrair dos ficheiros SAF-T os elementos relevantes das faturas, tal como previsto no preâmbulo do Decreto-Lei n.° 198/2012, de 24 de agosto;
- Comunicar à Comissão de Assuntos Constitucionais, Direitos, Liberdades e
Garantias da Assembleia da República o teor da presente decisão.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 27
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
VI. A audiência dos interessados
No dia 12 de abril de 2013, veio o Diretor-Geral da Autoridade Tributária e Aduaneira, nos termos e para os efeitos do disposto no artigo 100.° do Código do Procedimento
Administrativo, apresentar a sua pronúncia.
No dia 17 de abril de 2013, veio aquele responsável corrigir os pontos 20, 33 a 35 e 47 da pronúncia inicial, tendo substituído aquela versão por esta última, já com as devidas correções.
Os pontos 25. e seguintes daquela pronúncia são particularmente relevantes para a presente apreciação.
Daqueles pontos, tendo a AT considerado ser "de acolher previamente como válidas todas as considerações tecidas no seu [da CNPD] Projeto de Deliberação" (cfr. ponto 46 da pronúncia da AT), foi declarado que:
a) A AT efetuou a destruição integral dos ficheiros em file-system, tendo sido eliminados definitivamente todos os elementos dos ficheiros SAF-T que dele constavam;
b) No dia 9 de abril de 2013 foi indisponibilizada a consulta dos elementos das faturas correspondentes a aquisições efetuadas fora do âmbito do n.º 5 do artigo 3.° do Decreto-Lei n.° 198/2012;
c) A informação constante do E-Fatura foi expurgada dos elementos excedentes e individualizadores do consumo;
d) A AT disponibilizou, no dia 12 de abril de 2013, em produção, no Portal das
Finanças uma aplicação informática que permite extrair, a partir dos ficheiros
SAF-T, os elementos das faturas tipificados no n.º 4 do artigo 3.° do Decreto-
Lei n.° 198/2012;
e) Tal procedimento de extração passou a ser efetuado nos equipamentos informáticos das empresas, sendo transmitidos para a AT apenas os elementos das faturas descritos no n.º 4 do artigo 3.° do Decreto-Lei n.º 198/2012;
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 28
COMISSÃO NACIONAL
DE PROTECÇÃO DE DADOS f) A metodologia implementada passou a operar antes da receção de tais ficheiros na AT;
g) A AT emitiu uma comunicação, via e-mail (cujo teor juntou como anexo à sua pronúncia) a todas as empresas que anteriormente comunicaram os elementos das faturas à AT mediante submissão do ficheiro SAF-T (PT), informando-as das alterações aos procedimentos de comunicação.
Sem prejuízo da pronúncia da AT sobre o projeto de deliberação e das medidas corretivas que declarou ter promovido, a CNPD não deixará de acompanhar a solução implementada.
Acresce que, no que toca à informação a disponibilizar aos agentes económicos relativamente à alteração de procedimentos descritos pela AT, afigura-se manifestamente insuficiente o procedimento descrito supra, na alínea g), devendo a
AT proceder a uma ampla campanha informativa, utilizando os meios de comunicação institucional ao seu dispor para informar da correção dos procedimentos relativos ao envio dos elementos relevantes das faturas com base no ficheiro SAF-T, designadamente explicando que a extração dos dados do ficheiro SAF-T ocorre no equipamento informático do comerciante.
Atenta a sensibilidade da matéria e dos receios dos cidadãos que fizeram eco na opinião pública, recomenda-se que esta campanha informativa tenha o maior alcance possível.
O Manual de Integração de Software disponibilizado pela AT foi alterado conforme versões de 11.04.2013 e de 18.04.2013.
Correlacionada com o teor da presente Deliberação está a circunstância dos sistemas certificados de faturação, por permitirem o relacionamento das bases de dados de clientes com as bases de dados de faturação, automaticamente migrarem o NIF de determinado consumidor para a fatura e, consequentemente, para o ficheiro SAF-T, com a inerente comunicação de dados para a AT, ao arrepio das garantias ao nivel da
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 29
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS proteção de dados e da privacidade que o legislador imprimiu, quer no Decreto-Lei 198/2012, quer no Decreto-Lei n.° 197/2012, ambos de 24 de agosto.
No Decreto-Lei n.º 197/2012, com a alteração preconizada no seu artigo 2.° ao artigo 36.°, n.º 15 e 16, do CIVA, verifica-se que "a indicação na fatura da identificação e do domicílio do adquirente ou destinatário que não seja sujeito passivo não é obrigatória nas faturas de valor inferior a € 1000, salvo quando o adquirente ou destinatário solicite que a fatura contenha esses elementosi(sublinhado nosso). Apenas nos casos em que o adquirente expressamente o solicite deve constar nas faturas o NIF do adquirente (cf. n.° 16 do artigo 36.° do CIVA).
Assim, atentas as competências de certificação que recaem sob a AT, mostra-se imprescindível que a certificação previna a possibilidade de os sistemas gerarem os automatismos supra referidos, designadamente de importação do NIF da base de dados de clientes para a fatura, ainda que o cliente não o solicite, minimizando os riscos para a privacidade dos cidadãos, garantindo as condições legais do processamento da informação e, bem assim, garantindo a legalidade do tratamento de dados de faturação resultante da obrigação de envio da informação relevante das faturas, conforme resulta do n.º 4 do artigo 3.° do Decreto-Lei n.° 198/2012.
De igual modo, a AT deve assegurar que os programas de faturação já certificados são sujeitos às atualizações necessárias à conformidade legal decorrente das alterações introduzidas pelos Decretos-Lei n.°s 197/2012 e 198/2012, ambos de 24 de
Agosto.
No que respeita às pessoas singulares, deverão os programas de faturação garantir que apenas relativamente aos adquirentes que expressamente o solicitem seja o NIF aposto na fatura.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 30
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS
A este propósito, importa referir que os denominados "recibos verdes eletrónicos"s, porque têm a natureza de fatura-recibo, devem cumprir os mesmos requisitos.
A emissão de "recibo verde eletrónico" é efetuada diretamente no Portal das Finanças, pelo que todos os dados inseridos ficam centralmente registados.
A obrigação legal que impende sobre os emitentes de faturas de garantirem aos seus clientes, pessoas singulares, a opção de inserção do NIF não pode ser cumprida pelos sujeitos passivos obrigados à emissão do "recibo verde eletrónico".
Atentas as alterações legislativas efetuadas e já referidas, deverá o sistema sofrer as competentes atualizações, possibilitando a inserção do "consumidor final" no "recibo verde eletrónico", por referência ao NIF 999 999 990.
Esclarece-se que a CNPD não foi ouvida sobre a legislação dos "recibos verdes eletrónicos", apesar de esta conter matéria de proteção de dados.
VII. Decisão
Face à factualidade apurada, bem como pelas medidas corretivas entretanto adotadas pela AT, a CNPD delibera:
1. Recomendar à AT que proceda a uma ampla campanha informativa, utilizando os meios de comunicação institucional ao seu dispor para informar da correção dos procedimentos relativos ao envio dos elementos relevantes das faturas com base no ficheiro SAF-T, designadamente explicando que a extração dos dados do ficheiro SAF-T ocorre no equipamento informático do comerciante.
Atenta a sensibilidade da matéria e dos receios dos cidadãos que fizeram eco na opinião pública, recomenda-se que esta campanha informativa tenha o maior alcance possível;
15 Atualmente o recibo verde eletrónico passou a designar-se por "fatura-recibo", mas por clareza na identificação opta-se por manter a anterior designação.
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213 976 832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt

Proc. n.º 1719/2013 | 31
COMISSÃO NACIONAL
DE PROTECÇAO DE DADOS 2. Recomendar à AT que, no âmbito das suas competências de certificação de software de faturação, adeque o processo certificativo para que este previna a possibilidade de os sistemas gerarem o automatismo de importação do NIF da base de dados de clientes para a fatura, nos casos em que o cliente não o solicite. O mesmo vale para os programas já certificados.
3. Recomendar à AT que, no âmbito do sistema de emissão dos denominados "recibos verdes eletrónicos" (atual "fatura-recibo"), seja possível cumprir a obrigação legal que impende sobre os emitentes de faturas de garantirem aos seus clientes, pessoas singulares, a opção de inserção do "consumidor final", por referência ao NIF 999 999 990.
4. Comunicar à Comissão de Assuntos Constitucionais, Direitos, Liberdades e
Garantias da Assembleia da República o teor da presente deliberação.
5. Notificar os queixosos no âmbito do atual processo do teor da presente deliberação.
Lisboa, 23 de abril de 2013
Ana Roque (Relatora), Helena Delgado António, Carlos Campos Lobo, Vasco Almeida,
Luis Barroso, Luís Paiva de Andrade.
Filipa Calvão (Presidente)
Rua de São Bento, 148-3° • 1200-821 LISBOA
Tel: 213 928 400
Fax: 213976832 geral@cnpd.pt www.cnpd.pt 21 393 00 39
LINHA PRIVACIDADE
Dias úteis das 10 às 13 h duvidas@cnpd.pt
