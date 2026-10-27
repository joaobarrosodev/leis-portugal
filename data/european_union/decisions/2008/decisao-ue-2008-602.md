---
schema_version: '1.0'
id: eu:celex:32008D0602:por
title: '2008/602/CE: Decisão da Comissão, de 17 de Junho de 2008'
short_title: null
summary: '2008/602/CE: Decisão da Comissão, de 17 de Junho de 2008 , que estabelece a arquitectura física e os requisitos
  das interfaces nacionais e da infra-estrutura de comunicação entre o VIS Central e as interfaces nacionais durante a fase
  de desenvolvimento [notificada com o número C(2008) 2693]'
jurisdiction: european_union
territory: null
document_type: decision
document_type_label: Decisão
issuing_authority:
- Comissão Europeia
proposing_entity: null
official_number: 2008/602
official_date: null
publication_date: '2008-07-23'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L 194 de 23.7.2008
  number: '194'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.02/DOC_1
entry_into_force_dates:
- '2008-06-17'
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
  celex: 32008D0602
  eli: http://data.europa.eu/eli/dec/2008/602/oj
  oj: oj:JOL_2008_194_R_0003_01
  dre: null
  dre_path: null
  internal: eu:celex:32008D0602:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32008D0602
  metadata_url: http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018
  content_url: http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-10-26T12:06:53Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2025-10-29T13:56:01.039+01:00'
integrity:
  source_sha256: 716696b2cc3d264b4cca4393f51940fc4edc7e2f7bd8e2cb13abca1eded4e82f
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-10-26T12:06:53Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: União Europeia, EUR-Lex / Publicações da União Europeia
  reference: https://eur-lex.europa.eu/content/legal-notice/legal-notice.html
  notes: Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos
    de documentação).
subjects:
- entrada de estrangeiros
- especificação técnica
- política de vistos da UE
- proteção dos dados
- rede de transmissão
- sistema de informação
relationships:
- type: based_on
  target: celex:32004D0512
  label: null
  source: http://publications.europa.eu/resource/cellar/4351f6b1-7db8-4caa-9742-5438ee8f2e4f
  date: '2004-06-24'
- type: cites
  target: celex:31999D0437
  label: null
  source: http://publications.europa.eu/resource/cellar/f37cd7cb-c869-4550-b648-9a55aee621b4
- type: cites
  target: celex:32000D0365
  label: null
  source: http://publications.europa.eu/resource/cellar/db604d34-f377-416d-98b8-cf08b36efb22
- type: cites
  target: celex:32001R2424
  label: null
  source: http://publications.europa.eu/resource/cellar/ab465d63-90cf-40bf-8430-66f88b0bd04b
- type: cites
  target: celex:32002D0192
  label: null
  source: http://publications.europa.eu/resource/cellar/be5fb69e-961e-4335-b8ed-1e4d76f365b5
- type: cites
  target: celex:32008D0146
  label: null
  source: http://publications.europa.eu/resource/cellar/4a2ea03b-1112-4634-89be-45028919975a
- type: cites
  target: celex:32008D0261
  label: null
  source: http://publications.europa.eu/resource/cellar/a59be1de-c018-49b8-98db-90745c04efd1
article_structure:
  article_count: 2
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-10-26T12:06:53Z'
  warnings: []
  errors: []
---

# DECISÃO DA COMISSÃO

de 17 de Junho de 2008

que estabelece a arquitectura física e os requisitos das interfaces nacionais e da infra-estrutura de comunicação entre o VIS Central e as interfaces nacionais durante a fase de desenvolvimento

[notificada com o número C(2008) 2693]

(Os textos em línguas alemã, búlgara, checa, eslovaca, eslovena, espanhola, estónia, finlandesa, francesa, grega, húngara, italiana, letã, lituana, maltesa, neerlandesa, polaca, portuguesa, romena e sueca são os únicos que fazem fé)

(2008/602/CE)

A COMISSÃO DAS COMUNIDADES EUROPEIAS,

Tendo em conta o Tratado que institui a Comunidade Europeia,

Tendo em conta a Decisão 2004/512/CE do Conselho, de 8 de Junho de 2004, que estabelece o Sistema de Informação sobre Vistos (VIS) [([^1])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr1-L_2008194PT.01000301-E0001), nomeadamente a alínea a) do artigo 4.º,

Considerando o seguinte:

(1) A Decisão 2004/512/CE instituiu o VIS como um sistema de intercâmbio de dados em matéria de vistos entre Estados-Membros e conferiu o mandato à Comissão para desenvolver o VIS.

(2) A Comissão e os Estados-Membros devem estabelecer disposições adequadas, em especial no que respeita aos elementos da Interface Nacional situada em cada Estado-Membro.

(3) Nos termos da Decisão 2000/365/CE do Conselho, de 29 de Maio de 2000, sobre o pedido do Reino Unido da Grã-Bretanha e da Irlanda do Norte para participar em algumas das disposições do acervo de Schengen [([^2])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr2-L_2008194PT.01000301-E0002), o Reino Unido não participou na adopção da Decisão 2004/512/CE e não está por ela vinculado nem sujeito à sua aplicação, uma vez que constitui um desenvolvimento das disposições do acervo de Schengen. O Reino Unido não é, por conseguinte, destinatário da presente decisão da Comissão.

(4) Nos termos da Decisão 2002/192/CE do Conselho, de 28 de Fevereiro de 2002, sobre o pedido da Irlanda para participar em algumas das disposições do acervo de Schengen [([^3])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr3-L_2008194PT.01000301-E0003), a Irlanda não participou na adopção da Decisão 2004/512/CE e não está por ela vinculada nem sujeita à sua aplicação, uma vez que constitui um desenvolvimento das disposições do acervo de Schengen. A Irlanda não é, por conseguinte, destinatária da presente decisão da Comissão.

(5) Em conformidade com o artigo 5.º do Protocolo relativo à posição da Dinamarca, anexo ao Tratado da União Europeia e ao Tratado que institui a Comunidade Europeia, a Dinamarca decidiu em 13 de Agosto de 2004 transpor a Decisão 2004/512/CE para o direito dinamarquês. Por conseguinte, a Decisão 2004/512/CE vincula a Dinamarca nos termos do direito internacional e a Dinamarca, por força do mesmo, deve executar a presente decisão.

(6) No que diz respeito à Islândia e à Noruega, a presente decisão constitui um desenvolvimento das disposições do acervo de Schengen na acepção do acordo celebrado pelo Conselho da União Europeia e a República da Islândia e o Reino da Noruega relativo à associação destes Estados à execução, à aplicação e ao desenvolvimento do acervo de Schengen [([^4])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr4-L_2008194PT.01000301-E0004), que faz parte do domínio referido no ponto B do artigo 1.º da Decisão 1999/437/CE do Conselho, de 17 de Maio de 1999, relativa a determinadas regras de aplicação do Acordo celebrado pelo Conselho da União Europeia com a República da Islândia e o Reino da Noruega relativo à associação dos dois Estados à execução, à aplicação e ao desenvolvimento do acervo de Schengen [([^5])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr5-L_2008194PT.01000301-E0005).

(7) No que diz respeito à Suíça, a presente decisão constitui um desenvolvimento das disposições do acervo de Schengen na acepção do acordo celebrado entre a União Europeia, a Comunidade Europeia e a Confederação Suíça relativo à associação deste Estado à execução, à aplicação e ao desenvolvimento do acervo de Schengen, que faz parte do domínio referido no ponto B do artigo 1.º do Decisão 1999/437/CE, em conjugação com artigo 3.º da Decisão 2008/146/CE do Conselho, respeitante à celebração, em nome da Comunidade Europeia, do referido Acordo [([^6])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr6-L_2008194PT.01000301-E0006).

(8) No que diz respeito ao Liechtenstein, a presente decisão constitui um desenvolvimento das disposições do acervo de Schengen na acepção do protocolo entre a União Europeia, a Comunidade Europeia, a Confederação Suíça e o Principado do Liechtenstein relativo à adesão do Principado do Liechtenstein ao Acordo entre a União Europeia, a Comunidade Europeia e a Confederação Suíça relativo à associação da Confederação Suíça à execução, à aplicação e ao desenvolvimento do acervo de Schengen, que faz parte do domínio referido no ponto B do artigo 1.º da Decisão 1999/437/CE do Conselho, de 17 de Maio de 1999, em conjugação com o artigo 3.º da Decisão 2008/261/CE do Conselho, de 28 de Fevereiro de 2008, respeitante à assinatura, em nome da Comunidade Europeia, e à aplicação provisória de certas disposições do Protocolo entre a União Europeia, a Comunidade Europeia, a Confederação Suíça e o Principado do Liechtenstein relativo à adesão do Principado do Liechtenstein ao Acordo entre a União Europeia, a Comunidade Europeia e a Confederação Suíça relativo à associação da Confederação Suíça à execução, à aplicação e ao desenvolvimento do acervo de Schengen [([^7])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr7-L_2008194PT.01000301-E0007).

(9) As medidas previstas na presente decisão são conformes com o parecer do Comité criado pelo n.º 1 do artigo 5.º do Regulamento (CE) n.º 2424/2001 do Conselho, de 6 de Dezembro de 2001, relativo ao desenvolvimento da segunda geração do Sistema de Informação de Schengen (SIS II) [([^8])](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntr8-L_2008194PT.01000301-E0008),

ADOPTOU A PRESENTE DECISÃO:

###### Artigo 1.º

A arquitectura física e os requisitos das interfaces nacionais e da infra-estrutura de comunicação entre o VIS Central e as interfaces nacionais durante a fase de desenvolvimento são os indicados no anexo.

###### Artigo 2.º

São destinatários da presente decisão o Reino da Bélgica, a República da Bulgária, a República Checa, a República Federal da Alemanha, a República da Estónia, a República Helénica, o Reino de Espanha, a República Francesa, a República Italiana, a República de Chipre, a República da Letónia, a República da Lituânia, o Grão-Ducado do Luxemburgo, a República da Hungria, a República de Malta, o Reino dos Países Baixos, a República da Áustria, a República da Polónia, a República Portuguesa, a Roménia, a República da Eslovénia, a República Eslovaca, a República da Finlândia e o Reino da Suécia.

Feito em Bruxelas, em 17 de Junho de 2008.

***Pela Comissão***

**Jacques BARROT**

***Vice-Presidente***

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc1-L_2008194PT.01000301-E0001) [JO L 213 de 15.6.2004, p. 5](http://publications.europa.eu/resource/oj/JOL_2004_213_R_TOC).

> [(^2^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc2-L_2008194PT.01000301-E0002) [JO L 131 de 1.6.2000, p. 43](http://publications.europa.eu/resource/oj/JOL_2000_131_R_TOC).

> [(^3^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc3-L_2008194PT.01000301-E0003) [JO L 64 de 7.3.2002, p. 20](http://publications.europa.eu/resource/oj/JOL_2002_064_R_TOC).

> [(^4^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc4-L_2008194PT.01000301-E0004) [JO L 176 de 10.7.1999, p. 36](http://publications.europa.eu/resource/oj/JOL_1999_176_R_TOC).

> [(^5^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc5-L_2008194PT.01000301-E0005) [JO L 176 de 10.7.1999, p. 31](http://publications.europa.eu/resource/oj/JOL_1999_176_R_TOC).

> [(^6^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc6-L_2008194PT.01000301-E0006) [JO L 53 de 27.2.2008, p.1](http://publications.europa.eu/resource/oj/JOL_2008_053_R_TOC).

> [(^7^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc7-L_2008194PT.01000301-E0007) [JO L 83 de 26.3.2008, p. 3](http://publications.europa.eu/resource/oj/JOL_2008_083_R_TOC).

> [(^8^)](http://publications.europa.eu/resource/cellar/da2fe35d-3d49-414c-84d3-b9a409b57071.0018.03/DOC_1#ntc8-L_2008194PT.01000301-E0008) [JO L 328 de 13.12.2001, p. 4](http://publications.europa.eu/resource/oj/JOL_2001_328_R_TOC). Regulamento alterado pelo Regulamento (CE) n.º 1988/2006 ([JO L 411 de 30.12.2006, p. 1](http://publications.europa.eu/resource/oj/JOL_2006_411_R_TOC)).
