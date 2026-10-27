---
schema_version: '1.0'
id: eu:celex:32023R2790:por
title: Regulamento de Execução (UE) 2023/2790 da Comissão, de 14 de dezembro de 2023
short_title: null
summary: Regulamento de Execução (UE) 2023/2790 da Comissão, de 14 de dezembro de 2023, que estabelece as especificações funcionais
  e técnicas do módulo de interface de declaração das plataformas nacionais únicas para o setor marítimo
jurisdiction: european_union
territory: null
document_type: regulation
document_type_label: Regulamento de Execução
issuing_authority:
- Comissão Europeia
- MOVE
proposing_entity: null
official_number: 2023/2790
official_date: null
publication_date: '2023-12-18'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L, 2023/2790, 18.12.2023
  number: '2790'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.01/DOC_1
entry_into_force_dates:
- '2024-01-07'
- '2025-08-15'
end_of_validity_date: '9999-12-31'
legal_status: in_force
notes: []
language: por
version:
  kind: original
  label: Texto original publicado no Jornal Oficial
  language: por
  consolidation_date: null
identifiers:
  celex: 32023R2790
  eli: http://data.europa.eu/eli/reg_impl/2023/2790/oj
  oj: oj:L_202302790
  dre: null
  dre_path: null
  internal: eu:celex:32023R2790:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32023R2790
  metadata_url: http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020
  content_url: http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-10-26T12:43:25Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2023-12-18T02:57:18.317+01:00'
integrity:
  source_sha256: 3e7a806ee7db0d02fba03ea6d327e3da07b3838ee5d6153709d427b734b886b3
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-10-26T12:43:25Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: União Europeia, EUR-Lex / Publicações da União Europeia
  reference: https://eur-lex.europa.eu/content/legal-notice/legal-notice.html
  notes: Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos
    de documentação).
subjects:
- Estado-Membro UE
- cooperação administrativa
- especificação técnica
- instalação portuária
- intercâmbio de informação
- interface de programação de aplicações
- norma técnica
- política portuária comum
- segurança marítima
- transporte marítimo
relationships:
- type: based_on
  target: celex:32019R1239
  label: null
  source: http://publications.europa.eu/resource/cellar/b4cf0abe-ae8d-11e9-9d01-01aa75ed71a1
  date: '2019-07-25'
- type: cites
  target: celex:32014R0910
  label: null
  source: http://publications.europa.eu/resource/cellar/23b61856-2e82-11e4-8c3c-01aa75ed71a1
- type: cites
  target: celex:32015R2446
  label: null
  source: http://publications.europa.eu/resource/cellar/c73754bc-ae35-11e5-b528-01aa75ed71a1
- type: cites
  target: celex:32016R0679
  label: null
  source: http://publications.europa.eu/resource/cellar/3e485e15-11bd-11e6-ba9a-01aa75ed71a1
- type: cites
  target: celex:32018R1725
  label: null
  source: http://publications.europa.eu/resource/cellar/999029ee-ed62-11e8-b690-01aa75ed71a1
- type: cites
  target: celex:32023R0204
  label: null
  source: http://publications.europa.eu/resource/cellar/a6d5d0a5-a368-11ed-b508-01aa75ed71a1
article_structure:
  article_count: 4
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-10-26T12:43:25Z'
  warnings: []
  errors: []
---

# REGULAMENTO DE EXECUÇÃO (UE) 2023/2790 DA COMISSÃO

de 14 de dezembro de 2023

que estabelece as especificações funcionais e técnicas do módulo de interface de declaração das plataformas nacionais únicas para o setor marítimo

(Texto relevante para efeitos do EEE)

A COMISSÃO EUROPEIA,

Tendo em conta o Tratado sobre o Funcionamento da União Europeia,

Tendo em conta o Regulamento (UE) 2019/1239 do Parlamento Europeu e do Conselho, de 20 de junho de 2019, que estabelece um ambiente europeu de plataforma única para o setor marítimo e que revoga a Diretiva 2010/65/UE [([^1])](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntr1-L_202302790PT.000101-E0001), nomeadamente o artigo 6.º, n.º 1, e o artigo 12.º, n.º 4,

Após consulta do Comité de Facilitação Digital dos Transportes e do Comércio,

Considerando o seguinte:

(1) As especificações do módulo de interface de declaração devem basear-se numa tecnologia facilmente acessível, fácil de instalar e integrar em todas as plataformas nacionais únicas para o setor marítimo (MNSW) e permitir uma integração e manutenção harmoniosas no futuro.

(2) As especificações funcionais e técnicas do módulo de interface de declaração devem basear-se nas diretrizes de conceção do modelo de arquitetura de soluções de requisitos de interoperabilidade (HL SAT) de alto nível, a fim de permitir a rastreabilidade entre requisitos de interoperabilidade de alto nível e pormenorizados.

(3) Tendo em conta que os remetentes utilizam diferentes sistemas de comunicação e que as MNSW são implementadas utilizando diferentes tecnologias, o módulo de interface de declaração deve assentar em tecnologias que permitam o intercâmbio de informações entre diferentes sistemas de informação que utilizam um protocolo normalizado, permitindo uma maior interoperabilidade.

(4) As obrigações de comunicação enumeradas no anexo do Regulamento (UE) 2019/1239 podem exigir que os declarantes apresentem dados pessoais através do módulo de interface de declaração, que deve trocar as informações de forma que quaisquer dados pessoais sejam tratados em conformidade com o Regulamento (UE) 2018/1725 [([^2])](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntr2-L_202302790PT.000101-E0002) e o Regulamento (UE) 2016/679 [([^3])](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntr3-L_202302790PT.000101-E0003) do Parlamento Europeu e do Conselho.

(5) Uma vez que o módulo de interface de declaração é desenvolvido e atualizado pela Comissão e distribuído aos Estados-Membros para integração, a distribuição de novas versões do módulo de interface de declaração, a monitorização da correta instalação do *software* e a atualização do guia de implementação das mensagens devem ser geridas centralmente, tendo em conta, sempre que possível, os requisitos de segurança informática das MNSW.

(6) A fim de garantir a estabilidade, a segurança e o desempenho do módulo de interface de declaração, os Estados-Membros devem poder monitorizar o tráfego da rede e analisar ocorrências, erros e exceções do sistema, bem como integrar estas informações nos seus sistemas e processos de monitorização existentes. Para o efeito, o módulo de interface de declaração deve oferecer funcionalidades adequadas que permitam registar e armazenar eventos e fornecer informações sobre o tráfego da rede aos Estados-Membros.

(7) Para garantir o intercâmbio de informações seguro através do módulo de interface de declaração, os remetentes devem autenticar-se. Para o efeito, o sistema comum de gestão de registo e acesso de utilizadores deve ter um serviço de autenticação central e um registo central como componentes essenciais. Estes componentes devem trabalhar em conjunto para permitir a autenticação do remetente em todos os módulos da interface de declaração, fornecendo um mecanismo de autenticação unificado.

(8) A fim de trocar informações de forma segura utilizando o módulo de interface de declaração e assegurar que os utilizadores são reconhecidos a nível da UE quando acedem a qualquer um dos módulos de interface de declaração, os remetentes devem obter um certificado qualificado de selos eletrónicos conforme com os requisitos estabelecidos pelo Regulamento (UE) n.º 910/2014 do Parlamento Europeu e do Conselho [([^4])](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntr4-L_202302790PT.000101-E0004).

(9) A fim de se dispor de um registo único para os remetentes trocarem informações através das interfaces de declaração harmonizadas em diferentes Estados-Membros, os Estados-Membros devem poder registar os remetentes no registo central. Tal deverá reduzir os encargos com registos múltiplos para operações transfronteiriças em várias MNSW. Quaisquer dados pessoais constantes do registo central devem ser tratados em conformidade com os Regulamentos (UE) 2018/1725 e (UE) 2016/679.

(10) A fim de minimizar a dependência dos Estados-Membros em relação aos serviços centrais e tendo em conta que as MNSW podem já ser apoiadas por serviços nacionais de autenticação, os Estados-Membros devem também ser autorizados a reutilizar os seus próprios serviços nacionais de autenticação e registos nacionais para autenticar os remetentes que pretendam utilizar o módulo de interface de declaração, em alternativa ao sistema de gestão de registo e acesso de utilizadores do ambiente europeu de plataforma única para o setor marítimo (EMSWe).

(11) A fim de permitir que os Estados-Membros integrem corretamente o módulo de interface de declaração e o sistema de gestão de registo e acesso de utilizadores com as MNSW, o presente regulamento deve ser aplicável a partir da mesma data que o Regulamento (UE) 2019/1239.

(12) A Autoridade Europeia para a Proteção de Dados foi consultada em conformidade com o disposto no artigo 42.º, n.º 1, do Regulamento (UE) 2018/1725 e emitiu um parecer em 18 de outubro de 2023,

ADOTOU O PRESENTE REGULAMENTO:

###### Artigo 1.º — Definições

Para efeitos do presente regulamento, entende-se por:

1) «Módulo de interface de declaração», uma componente informática mediadora da MNSW a que se refere o artigo 2.º, n.º 4, do Regulamento (UE) 2019/1239;

2) «Remetente», um declarante ou prestador de serviços de dados que opera o sistema informático que envia mensagens eletrónicas para uma MNSW ou as recebe através do módulo de interface de declaração;

3) «formalidade» uma formalidade, tal como definido no artigo 1.º do Regulamento de Execução (UE) 2023/204 da Comissão [([^5])](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntr5-L_202302790PT.000101-E0005);

4) «AS4», um protocolo de mensagens baseado em serviços Web para o intercâmbio seguro de mensagens entre duas partes;

5) «Mensagem», a representação digital de formalidades ou mensagens de resposta utilizadas para o intercâmbio entre o remetente e a MNSW;

6) «Ponto de acesso AS4», um *software* operativo de servidor compatível com o protocolo de mensagens AS4 e com os requisitos do módulo de interface de declaração, que permite o envio e a receção de informações em nome de um remetente de e para o módulo de interface de declaração;

7) «Núcleo MNSW», um componente técnico da MNSW com o qual o módulo de interface de declaração está integrado;

8) «Validação da sintaxe», o processo que consiste em verificar se uma mensagem eletrónica está isenta de erros de programação, estruturais ou estilísticos;

9) «Validação semântica», um processo em que é verificada a conformidade dos dados com regras específicas em matéria de dados no âmbito de uma formalidade;

10) «Guia de implementação de mensagens», uma especificação funcional que estabelece normas e mensagens a trocar entre os remetentes e as MNSW através do módulo de interface de declaração;

11) «Registo», um processo em que uma pessoa singular ou coletiva se identifica e cria uma conta junto da autoridade referida no artigo 12.º, n.º 2, do Regulamento (UE) 2019/1239;

12) «Identificação», a identificação eletrónica como definido no artigo 3.º, ponto 1), do Regulamento (UE) n.º 910/2014;

13) «Meio de identificação eletrónica», uma identificação eletrónica como definido no artigo 3.º, ponto 2), do Regulamento (UE) n.º 910/2014;

14) «Autenticação», uma autenticação como definido no artigo 3.º, ponto 5), do Regulamento (UE) n.º 910/2014;

15) «Certificado», um certificado qualificado de selo eletrónico definido no artigo 3.º, ponto 30), do Regulamento (UE) n.º 910/2014, emitido por um prestador qualificado de serviços de confiança na aceção do artigo 3.º, ponto 20), do Regulamento (UE) n.º 910/2014;

16) «Número EORI», um número de identificação na aceção do artigo 1.º, ponto 18), do Regulamento Delegado (UE) 2015/2446 da Comissão [([^6])](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntr6-L_202302790PT.000101-E0006);

17) «Sistema de gestão de registo e acesso de utilizadores do EMSWe», um sistema gerido pela Comissão que engloba um registo central e um serviço de autenticação central e assegura o reconhecimento mútuo dos meios de identificação eletrónica e da autenticação para o intercâmbio de dados transfronteiriços seguro entre os remetentes e as MNSW através do módulo de interface de declaração;

18) «Registo central», um registo gerido pela Comissão que contém os dados de registo dos remetentes fornecidos pelos Estados-Membros com o objetivo de facilitar a autenticação dos remetentes;

19) «Registo nacional», um registo gerido por um Estado-Membro que detém os dados de registo dos remetentes e pode ser utilizado para facilitar a autenticação dos remetentes se forem cumpridos os requisitos do serviço de autenticação central;

20) «Serviço de autenticação central», um serviço gerido pela Comissão que autentica remetentes que utilizam o módulo de interface de declaração;

21) «Serviço nacional de autenticação», um serviço gerido por um Estado-Membro que pode ser utilizado para autenticar remetentes que utilizam o módulo de interface de declaração.

###### Artigo 2.º

O módulo de interface de declaração deve cumprir as especificações funcionais e técnicas constantes da parte I do anexo.

A fim de ajudar a integrar o módulo de interface de declaração nas MNSW, a Comissão, em estreita colaboração com os coordenadores nacionais do EMSWe, deve:

— definir orientações para testar e configurar o módulo de interface de declaração para integração nas respetivas MNSW,

— definir e manter, com a assistência da Agência Europeia da Segurança Marítima, o guia de implementação de mensagens.

###### Artigo 3.º

O registo central e o serviço de autenticação central são criados em conformidade com as especificações técnicas, as normas e os procedimentos constantes da parte II do anexo.

###### Artigo 4.º

O presente regulamento entra em vigor no vigésimo dia seguinte ao da sua publicação no *Jornal Oficial da União Europeia*.

É aplicável a partir de 15 de agosto de 2025.

O presente regulamento é obrigatório em todos os seus elementos e diretamente aplicável em todos os Estados-Membros.

Feito em Bruxelas, em 14 de dezembro de 2023.

***Pela Comissão***

***A Presidente***

**Ursula VON DER LEYEN**

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntc1-L_202302790PT.000101-E0001) [JO L 198 de 25.7.2019, p. 64](http://publications.europa.eu/resource/oj/JOL_2019_198_R_TOC).

> [(^2^)](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntc2-L_202302790PT.000101-E0002) Regulamento (UE) 2018/1725 do Parlamento Europeu e do Conselho, de 23 de outubro de 2018, relativo à proteção das pessoas singulares no que diz respeito ao tratamento de dados pessoais pelas instituições e pelos órgãos e organismos da União e à livre circulação desses dados, e que revoga o Regulamento (CE) n.º 45/2001 e a Decisão n.º 1247/2002/CE ([JO L 295 de 21.11.2018, p. 39](http://publications.europa.eu/resource/oj/JOL_2018_295_R_TOC)).

> [(^3^)](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntc3-L_202302790PT.000101-E0003) Regulamento (UE) 2016/679 do Parlamento Europeu e do Conselho, de 27 de abril de 2016, relativo à proteção das pessoas singulares no que diz respeito ao tratamento de dados pessoais e à livre circulação desses dados e que revoga a Diretiva 95/46/CE (Regulamento Geral sobre a Proteção de Dados) ([JO L 119 de 4.5.2016, p. 1](http://publications.europa.eu/resource/oj/JOL_2016_119_R_TOC)).

> [(^4^)](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntc4-L_202302790PT.000101-E0004) Regulamento (UE) n.º 910/2014 do Parlamento Europeu e do Conselho, de 23 de julho de 2014, relativo à identificação eletrónica e aos serviços de confiança para as transações eletrónicas no mercado interno e que revoga a Diretiva 1999/93/CE ([JO L 257 de 28.8.2014, p. 73](http://publications.europa.eu/resource/oj/JOL_2014_257_R_TOC)).

> [(^5^)](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntc5-L_202302790PT.000101-E0005) Regulamento de Execução (UE) 2023/204 da Comissão de 28 de outubro de 2022, que estabelece as especificações técnicas, as normas e os procedimentos com vista a estabelecer um ambiente europeu de plataforma única para o setor marítimo nos termos do Regulamento (UE) 2019/1239 do Parlamento Europeu e do Conselho ([JO L 33 de 3.2.2023, p. 1](http://publications.europa.eu/resource/oj/JOL_2023_033_R_TOC)).

> [(^6^)](http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1.0020.03/DOC_1#ntc6-L_202302790PT.000101-E0006) Regulamento Delegado (UE) 2015/2446 da Comissão, de 28 de julho de 2015, que completa o Regulamento (UE) n.º 952/2013 do Parlamento Europeu e do Conselho, com regras pormenorizadas relativamente a determinadas disposições do Código Aduaneiro da União ([JO L 343 de 29.12.2015, p. 1](http://publications.europa.eu/resource/oj/JOL_2015_343_R_TOC)).
