---
schema_version: '1.0'
id: eu:celex:32018R0278:por
title: Regulamento de Execução (UE) 2018/278 da Comissão, de 23 de fevereiro de 2018
short_title: null
summary: Regulamento de Execução (UE) 2018/278 da Comissão, de 23 de fevereiro de 2018, que altera o anexo do Regulamento
  (UE) n.° 1305/2014 no que diz respeito à estrutura das mensagens, ao modelo de dados e mensagens, da base de dados operacionais
  dos vagões e unidades intermodais, e para adotar uma norma informática para o nível de comunicação da interface comum
jurisdiction: european_union
territory: null
document_type: regulation
document_type_label: Regulamento de Execução
issuing_authority:
- Comissão Europeia
- MOVE
proposing_entity: null
official_number: 2018/278
official_date: null
publication_date: '2018-02-24'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L 54 de 24.2.2018
  number: '54'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.01/DOC_1
entry_into_force_dates:
- '2018-03-16'
end_of_validity_date: '2026-03-01'
legal_status: repealed
notes: []
language: por
version:
  kind: original
  label: Texto original publicado no Jornal Oficial
  language: por
  consolidation_date: null
identifiers:
  celex: 32018R0278
  eli: http://data.europa.eu/eli/reg_impl/2018/278/oj
  oj: oj:JOL_2018_054_R_0004
  dre: null
  dre_path: null
  internal: eu:celex:32018R0278:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32018R0278
  metadata_url: http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018
  content_url: http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-10-26T12:27:18Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2025-02-13T05:30:17.832+01:00'
integrity:
  source_sha256: 3bdff1828317e49c3136f9ba967b930ae503e21ce12c159e9ae00a2b6d266ca9
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-10-26T12:27:18Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: União Europeia, EUR-Lex / Publicações da União Europeia
  reference: https://eur-lex.europa.eu/content/legal-notice/legal-notice.html
  notes: Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos
    de documentação).
subjects:
- especificação técnica
- harmonização das normas
- norma europeia
- norma técnica
- rede ferroviária
- rede transeuropeia
- telemática
- transporte a grande velocidade
relationships:
- type: amends
  target: celex:32014R1305
  label: null
  source: http://publications.europa.eu/resource/cellar/7e792480-81cb-11e4-89f7-01aa75ed71a1
  date: '2014-12-12'
- type: based_on
  target: celex:32016L0797
  label: null
  source: http://publications.europa.eu/resource/cellar/eaefba25-22d0-11e6-86d0-01aa75ed71a1
  date: '2016-05-26'
- type: cites
  target: celex:32016R0796
  label: null
  source: http://publications.europa.eu/resource/cellar/268f3f19-22d1-11e6-86d0-01aa75ed71a1
- type: repealed_by
  target: celex:32026R0253
  label: null
  source: http://publications.europa.eu/resource/cellar/beb9a1a1-0621-11f1-825d-01aa75ed71a1
  date: '2026-02-10'
article_structure:
  article_count: 2
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-10-26T12:27:18Z'
  warnings: []
  errors: []
---

# REGULAMENTO DE EXECUÇÃO (UE) 2018/278 DA COMISSÃO

de 23 de fevereiro de 2018

que altera o anexo do Regulamento (UE) n.º 1305/2014 no que diz respeito à estrutura das mensagens, ao modelo de dados e mensagens, da base de dados operacionais dos vagões e unidades intermodais, e para adotar uma norma informática para o nível de comunicação da interface comum

A COMISSÃO EUROPEIA,

Tendo em conta o Tratado sobre o Funcionamento da União Europeia,

Tendo em conta a Diretiva (UE) 2016/797 do Parlamento Europeu e do Conselho, de 11 de maio de 2016, relativa à interoperabilidade do sistema ferroviário na União Europeia [([^1])](http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.03/DOC_1#ntr1-L_2018054PT.01001101-E0001), nomeadamente o artigo 5.º, n.º 11,

Considerando o seguinte:

(1) O artigo 19.º do Regulamento (UE) 2016/796 do Parlamento Europeu e do Conselho [([^2])](http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.03/DOC_1#ntr2-L_2018054PT.01001101-E0002) requer que a Agência Ferroviária Europeia («Agência») dirija recomendações à Comissão sobre as especificações técnicas de interoperabilidade («ETI») e a sua revisão, nos termos do artigo 5.º da Diretiva (UE) 2016/797 e, bem assim, que assegure que as ETI se adaptem ao progresso técnico, às tendências do mercado e às exigências sociais.

(2) Em 23 de setembro de 2017, a Comissão solicitou à Agência que emitisse uma recomendação nos termos do artigo 5.º, n.º 2, da Diretiva (UE) 2016/797 para a revisão das especificações técnicas de interoperabilidade relativas ao subsistema de «aplicações telemáticas para os serviços de mercadorias» do sistema ferroviário da União («ETI ATM»).

(3) Em 18 de outubro de 2017, a Agência emitiu uma recomendação sobre a ETI ATM, a fim de atualizar a estrutura das mensagens ETI ATM, o modelo de dados e mensagens, a base de dados operacionais dos vagões e unidades intermodais (WIMO), e para adotar uma norma informática para o nível de comunicação da interface comum. Estas alterações foram introduzidas com vista a ultrapassar a anterior lógica proprietária e para permitir uma aplicação mais rápida e menos onerosa desta ferramenta na comunidade de utilizadores da ETI ATM. Os processos de referência foram revistos em conformidade.

(4) As disposições do anexo do Regulamento (UE) n.º 1305/2014 da Comissão [([^3])](http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.03/DOC_1#ntr3-L_2018054PT.01001101-E0003) relacionadas com a ETI ATM devem ser alteradas a fim de definir a arquitetura de implementação da interface comum em consonância com a estrutura de mensagens anteriormente descrita.

(5) As medidas previstas no presente regulamento estão em conformidade com o parecer do comité instituído pelo artigo 51.º, n.º 1, da Diretiva (UE) 2016/797,

ADOTOU O PRESENTE REGULAMENTO:

###### Artigo 1.º

O anexo do Regulamento (UE) n.º 1305/2014 é alterado em conformidade com o anexo do presente regulamento.

###### Artigo 2.º

O presente regulamento entra em vigor no vigésimo dia seguinte ao da sua publicação no *Jornal Oficial da União Europeia*.

O presente regulamento é obrigatório em todos os seus elementos e diretamente aplicável em todos os Estados-Membros.

Feito em Bruxelas, em 23 de fevereiro de 2018.

***Pela Comissão***

***O Presidente***

**Jean-Claude JUNCKER**

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.03/DOC_1#ntc1-L_2018054PT.01001101-E0001) [JO L 138 de 26.5.2016, p. 44](http://publications.europa.eu/resource/oj/JOL_2016_138_R_TOC).

> [(^2^)](http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.03/DOC_1#ntc2-L_2018054PT.01001101-E0002) Regulamento (UE) 2016/796 do Parlamento Europeu e do Conselho, de 11 de maio de 2016, relativo à Agência Ferroviária da União Europeia e que revoga o Regulamento (CE) n.º 881/2004 ([JO L 138 de 26.5.2016, p. 1](http://publications.europa.eu/resource/oj/JOL_2016_138_R_TOC)).

> [(^3^)](http://publications.europa.eu/resource/cellar/86561dee-1932-11e8-ac73-01aa75ed71a1.0018.03/DOC_1#ntc3-L_2018054PT.01001101-E0003) Regulamento (UE) n.º 1305/2014 da Comissão, de 11 de dezembro de 2014, sobre a especificação técnica de interoperabilidade relativa ao subsistema «Aplicações telemáticas para o transporte de mercadorias» do sistema ferroviário da União Europeia e que revoga o Regulamento (CE) n.º 62/2006 ([JO L 356 de 12.12.2014, p. 438](http://publications.europa.eu/resource/oj/JOL_2014_356_R_TOC)).
