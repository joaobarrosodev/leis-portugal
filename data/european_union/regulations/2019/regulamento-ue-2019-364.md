---
schema_version: '1.0'
id: eu:celex:32019R0364:por
title: Regulamento de Execução (UE) 2019/364 da Comissão, de 13 de dezembro de 2018
short_title: null
summary: Regulamento de Execução (UE) 2019/364 da Comissão, de 13 de dezembro de 2018, que estabelece as normas técnicas de
  execução no que se refere ao formato dos pedidos de registo e extensão do registo dos repositórios de transações em conformidade
  com o Regulamento (UE) 2015/2365 do Parlamento Europeu e do Conselho (Texto relevante para efeitos do EEE.)
jurisdiction: european_union
territory: null
document_type: regulation
document_type_label: Regulamento de Execução
issuing_authority:
- Comissão Europeia
- FISMA
proposing_entity: null
official_number: 2019/364
official_date: null
publication_date: '2019-03-22'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L 81 de 22.3.2019
  number: '81'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.01/DOC_1
entry_into_force_dates:
- '2019-04-11'
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
  celex: 32019R0364
  eli: http://data.europa.eu/eli/reg_impl/2019/364/oj
  oj: oj:JOL_2019_081_R_0009
  dre: null
  dre_path: null
  internal: eu:celex:32019R0364:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32019R0364
  metadata_url: http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018
  content_url: http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-11-12T01:08:41Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2025-02-13T09:16:28.130+01:00'
integrity:
  source_sha256: a4ea60f43dc0d02c8dc67b160bf155e49c6c17bb9901c7362384483be1507373
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-11-12T01:08:41Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: União Europeia, EUR-Lex / Publicações da União Europeia
  reference: https://eur-lex.europa.eu/content/legal-notice/legal-notice.html
  notes: Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos
    de documentação).
subjects:
- Autoridade Europeia dos Valores Mobiliários e dos Mercados
- arquivo
- especificação técnica
- informação comercial
- memorização de dados
- norma técnica
- regulamentação financeira
relationships:
- type: based_on
  target: celex:32015R2365
  label: null
  source: http://publications.europa.eu/resource/cellar/b73101cd-a953-11e5-b528-01aa75ed71a1
  date: '2015-12-23'
- type: cites
  target: celex:32009L0065
  label: null
  source: http://publications.europa.eu/resource/cellar/0baaf4bd-450e-4b61-8bfd-6d7bad1f97cf
- type: cites
  target: celex:32010R1095
  label: null
  source: http://publications.europa.eu/resource/cellar/d6206116-a910-4ffa-b6cd-f14b1b503568
- type: cites
  target: celex:32019R0359
  label: null
  source: http://publications.europa.eu/resource/cellar/36e4922c-4c73-11e9-a8ed-01aa75ed71a1
article_structure:
  article_count: 2
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-11-12T01:08:41Z'
  warnings: []
  errors: []
---

# REGULAMENTO DE EXECUÇÃO (UE) 2019/364 DA COMISSÃO

de 13 de dezembro de 2018

que estabelece as normas técnicas de execução no que se refere ao formato dos pedidos de registo e extensão do registo dos repositórios de transações em conformidade com o Regulamento (UE) 2015/2365 do Parlamento Europeu e do Conselho

(Texto relevante para efeitos do EEE)

A COMISSÃO EUROPEIA,

Tendo em conta o Tratado sobre o Funcionamento da União Europeia,

Tendo em conta o Regulamento (UE) 2015/2365 do Parlamento Europeu e do Conselho, de 25 de novembro de 2015, relativo à transparência das operações de financiamento através de valores mobiliários e de reutilização e que altera o Regulamento (UE) n.º 648/2012 [([^1])](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntr1-L_2019081PT.01012501-E0001), nomeadamente o artigo 5.º, n.º 8,

Considerando o seguinte:

(1) Um formato uniforme para os pedidos de registo e de extensão do registo dos repositórios de transações, dirigidos à Autoridade Europeia dos Valores Mobiliários e dos Mercados (ESMA), deverá assegurar que todas as informações exigidas nos termos do Regulamento Delegado (UE) 2019/359 da Comissão [([^2])](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntr2-L_2019081PT.01012501-E0002) são apresentadas à ESMA e por ela facilmente identificadas.

(2) A fim de facilitar a identificação das informações apresentadas pelo repositório de transações, todos os documentos incluídos no pedido devem ter um número de referência único.

(3) Em conformidade com o artigo 1.º, n.º 3, do Regulamento Delegado (UE) 2019/359, caso o repositório de transações requerente considere que algum dos requisitos do Regulamento Delegado (UE) 2019/359 não lhe é aplicável, deve indicar claramente esse requisito no seu pedido, justificando também a sua não-aplicabilidade. Esses requisitos e respetivas justificações devem ser claramente identificados no pedido de registo ou de extensão do registo.

(4) Todas as informações apresentadas à ESMA no âmbito de um pedido de registo ou de extensão do registo de um repositório de transações devem ser fornecidas em suporte duradouro, como definido na Diretiva 2009/65/CE do Parlamento Europeu e do Conselho [([^3])](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntr3-L_2019081PT.01012501-E0003), para permitir o seu armazenamento para futura utilização e reprodução.

(5) O presente regulamento tem por base o projeto de normas técnicas de execução apresentado pela ESMA à Comissão Europeia nos termos do procedimento previsto no artigo 15.º do Regulamento (UE) n.º 1095/2010 do Parlamento Europeu e do Conselho [([^4])](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntr4-L_2019081PT.01012501-E0004).

(6) A ESMA realizou igualmente consultas públicas abertas sobre estes projetos de normas técnicas de execução, analisou os seus potenciais custos e benefícios e solicitou o parecer do Grupo de Interessados do Setor dos Valores Mobiliários e dos Mercados, estabelecido em conformidade com o artigo 37.º do Regulamento (UE) n.º 1095/2010,

ADOTOU O PRESENTE REGULAMENTO:

###### Artigo 1.º — Formato dos pedidos de registo e de extensão do registo

1. Os pedidos de registo ou de extensão do registo devem ser apresentados de acordo com o formato estabelecido no anexo.

2. O repositório de transações deve atribuir um número de referência único a cada documento que apresenta e deve identificar claramente a qual dos requisitos específicos previstos no Regulamento Delegado (UE) 2019/359 se refere cada documento.

3. Os pedidos de registo ou de extensão do registo devem indicar claramente os motivos pelos quais não são apresentadas informações referentes a um determinado requisito.

4. Os pedidos de registo ou de extensão do registo devem ser apresentados em suporte duradouro, conforme definido no artigo 2.º, n.º 1, alínea m), da Diretiva 2009/65/CE.

###### Artigo 2.º — Entrada em vigor

O presente regulamento entra em vigor no vigésimo dia seguinte ao da sua publicação no *Jornal Oficial da União Europeia*.

O presente regulamento é obrigatório em todos os seus elementos e diretamente aplicável em todos os Estados-Membros.

Feito em Bruxelas, em 13 de dezembro de 2018.

***Pela Comissão***

***O Presidente***

**Jean-Claude JUNCKER**

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntc1-L_2019081PT.01012501-E0001) [JO L 337 de 23.12.2015, p. 1](http://publications.europa.eu/resource/oj/JOL_2015_337_R_TOC).

> [(^2^)](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntc2-L_2019081PT.01012501-E0002) Regulamento Delegado (UE) 2019/359 da Comissão, de 13 de dezembro de 2018, que complementa o Regulamento (UE) 2015/2365 do Parlamento Europeu e do Conselho no que diz respeito às normas técnicas de regulamentação que especificam os dados dos pedidos de registo e de extensão do registo como repositório de transações (ver a página 45 do presente Jornal Oficial).

> [(^3^)](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntc3-L_2019081PT.01012501-E0003) Diretiva 2009/65/CE do Parlamento Europeu e do Conselho, de 13 de julho de 2009, que coordena as disposições legislativas, regulamentares e administrativas respeitantes a alguns organismos de investimento colectivo em valores mobiliários (OICVM) ([JO L 302 de 17.11.2009, p. 32](http://publications.europa.eu/resource/oj/JOL_2009_302_R_TOC)).

> [(^4^)](http://publications.europa.eu/resource/cellar/343b75c6-4c74-11e9-a8ed-01aa75ed71a1.0018.03/DOC_1#ntc4-L_2019081PT.01012501-E0004) Regulamento (UE) n.º 1095/2010 do Parlamento Europeu e do Conselho, de 24 de novembro de 2010, que cria uma Autoridade Europeia de Supervisão (Autoridade Europeia dos Valores Mobiliários e dos Mercados) ([JO L 331 de 15.12.2010, p. 84](http://publications.europa.eu/resource/oj/JOL_2010_331_R_TOC)).
