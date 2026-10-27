---
schema_version: '1.0'
id: eu:celex:32026R2098:por
title: Regulamento de Execução (UE) 2026/2098 da Comissão, de 18 de setembro de 2026
short_title: null
summary: Regulamento de Execução (UE) 2026/2098 da Comissão, de 18 de setembro de 2026, que estabelece os elementos de metadados
  mínimos e as suas características a facultar pelos detentores dos dados de saúde no que se refere às descrições dos conjuntos
  de dados para a utilização secundária de dados de saúde eletrónicos nos termos do artigo 77.o, n.o 4, do Regulamento (UE)
  2025/327 que cria o Espaço Europeu de Dados de Saúde
jurisdiction: european_union
territory: null
document_type: regulation
document_type_label: Regulamento de Execução
issuing_authority:
- Comissão Europeia
- SANTE
proposing_entity: null
official_number: 2026/2098
official_date: null
publication_date: '2026-09-21'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L, 2026/2098, 21.9.2026
  number: '2098'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/a1db9a95-b554-11f1-81de-01aa75ed71a1.0020.01/DOC_1
entry_into_force_dates:
- '2026-10-11'
- '2029-03-26'
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
  celex: 32026R2098
  eli: http://data.europa.eu/eli/reg_impl/2026/2098/oj
  oj: oj:L_202602098
  dre: null
  dre_path: null
  internal: eu:celex:32026R2098:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32026R2098
  metadata_url: http://publications.europa.eu/resource/cellar/a1db9a95-b554-11f1-81de-01aa75ed71a1.0020
  content_url: http://publications.europa.eu/resource/cellar/a1db9a95-b554-11f1-81de-01aa75ed71a1.0020.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-10-22T04:00:24Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2026-09-21T02:54:36.154+02:00'
integrity:
  source_sha256: 75f87763e5c6e46f674cc16a7cd8945fbd3e126e673503c6e333f214c9d5c9bd
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-10-22T04:00:24Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: União Europeia, EUR-Lex / Publicações da União Europeia
  reference: https://eur-lex.europa.eu/content/legal-notice/legal-notice.html
  notes: Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos
    de documentação).
subjects:
- conjunto de dados
- dados pessoais
- fluxo de dados transfronteiriço
- intercâmbio de informação
- metadados
- proteção da vida privada
- proteção dos dados
- saúde em linha
- saúde pública
- sistema de saúde
relationships:
- type: based_on
  target: celex:32025R0327
  label: null
  source: http://publications.europa.eu/resource/cellar/531b8c37-f962-11ef-b7db-01aa75ed71a1
  date: '2025-03-05'
article_structure:
  article_count: 4
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-10-22T04:00:24Z'
  warnings: []
  errors: []
---

# REGULAMENTO DE EXECUÇÃO (UE) 2026/2098 DA COMISSÃO

de 18 de setembro de 2026

que estabelece os elementos de metadados mínimos e as suas características a facultar pelos detentores dos dados de saúde no que se refere às descrições dos conjuntos de dados para a utilização secundária de dados de saúde eletrónicos nos termos do artigo 77.º, n.º 4, do Regulamento (UE) 2025/327 que cria o Espaço Europeu de Dados de Saúde

(Texto relevante para efeitos do EEE)

A COMISSÃO EUROPEIA,

Tendo em conta o Tratado sobre o Funcionamento da União Europeia,

Tendo em conta o Regulamento (UE) 2025/327 do Parlamento Europeu e do Conselho, de 11 de fevereiro de 2025, relativo ao Espaço Europeu de Dados de Saúde e que altera a Diretiva 2011/24/UE e o Regulamento (UE) 2024/2847 [([^1])](http://publications.europa.eu/resource/cellar/a1db9a95-b554-11f1-81de-01aa75ed71a1.0020.03/DOC_1#ntr1-L_202602098PT.000101-E0001), nomeadamente o artigo 77.º, n.º 4, primeira frase,

Considerando o seguinte:

(1) O artigo 77.º, n.º 1, do Regulamento (UE) 2025/327 exige que os organismos responsáveis pelo acesso aos dados de saúde disponibilizem ao público catálogos de conjuntos de dados com uma descrição, sob a forma de metadados, dos conjuntos de dados disponíveis para a utilização secundária de dados de saúde eletrónicos, incluindo informações sobre a fonte, o âmbito, as principais características e a natureza dos dados de saúde eletrónicos nos conjuntos de dados e as condições de disponibilização desses dados.

(2) Para o efeito, e em conformidade com o artigo 60.º, n.º 3, do Regulamento (UE) 2025/327, cabe aos detentores dos dados de saúde comunicar aos organismos responsáveis pelo acesso aos dados de saúde essa descrição referente ao conjunto de dados que detêm, independentemente de os conjuntos de dados conterem dados de saúde eletrónicos pessoais e/ou não pessoais.

(3) Em conformidade com o artigo 60.º, n.º 3, do Regulamento (UE) 2025/327, os detentores dos dados de saúde são obrigados a verificar, no mínimo, anualmente, se as descrições dos conjuntos de dados são exatas e estão atualizadas. Esta verificação é essencial para assegurar a fiabilidade e a usabilidade dos catálogos de conjuntos de dados para a utilização secundária de dados de saúde eletrónicos.

(4) Conforme previsto no artigo 77.º, n.º 1, do Regulamento (UE) 2025/327, os catálogos de conjuntos de dados devem ser normalizados e legíveis por máquina, a fim de assegurar a interoperabilidade semântica e técnica entre todos os Estados-Membros. Esta interoperabilidade é necessária para permitir a interligação dos catálogos nacionais de conjuntos de dados e dos catálogos de conjuntos de dados de participantes autorizados com o catálogo da UE de conjuntos de dados estabelecido nos termos do artigo 79.º do referido regulamento. Por conseguinte, importa que os detentores dos dados de saúde, ao facultarem os elementos de metadados mínimos e as características desses elementos, adotem uma abordagem comum no que se refere aos metadados para as descrições dos conjuntos de dados.

(5) É conveniente que seja utilizado como um tal quadro de metadados o perfil de aplicação HealthDCAT (HealthDCAT-AP). O HealthDCAT-AP baseia-se no perfil de aplicação DCAT geral e consiste numa especificação técnica criada e mantida pela Comissão, concebida especificamente para apoiar a descrição dos conjuntos de dados de saúde disponibilizados para a utilização secundária de dados de saúde eletrónicos. Essas especificações são fornecidas em conformidade com as decisões operacionais dos organismos pertinentes criados nos termos dos artigos 92.º e 95.°, no âmbito do regime de governação do Espaço Europeu de Dados de Saúde.

(6) O presente regulamento contribui para a interoperabilidade das infraestruturas digitais de apoio ao Espaço Europeu de Dados de Saúde, incluindo as que estão associadas ao acesso transfronteiras aos dados. Foi realizada uma avaliação da interoperabilidade, cujo relatório será publicado no portal Europa Interoperável aquando da adoção do presente regulamento.

(7) As medidas previstas no presente regulamento estão em conformidade com o parecer do comité instituído pelo artigo 98.º, n.º 1, do Regulamento (UE) 2025/327,

ADOTOU O PRESENTE REGULAMENTO:

###### Artigo 1.º — Objeto e âmbito de aplicação

1. O presente regulamento estabelece os elementos de metadados mínimos no que se refere às descrições dos conjuntos de dados, bem como as características desses elementos, que os detentores dos dados de saúde são obrigados a facultar aos organismos responsáveis pelo acesso aos dados de saúde nos termos do artigo 60.º, n.º 3, do Regulamento (UE) 2025/327 para a utilização secundária de dados de saúde eletrónicos, bem como o quadro de metadados a utilizar para esse efeito.

2. O presente regulamento é igualmente aplicável, se for caso disso, aos participantes autorizados na infraestrutura «Dados de saúde @ UE» (HealthData@EU) quando facultam descrições dos conjuntos de dados nos termos do Regulamento (UE) 2025/327.

3. O presente regulamento não impede os detentores dos dados de saúde de facultarem elementos de metadados adicionais e as suas características a título voluntário, utilizando, para esse efeito, o quadro de metadados a que se refere o primeiro parágrafo.

###### Artigo 2.º — Definições

Para efeitos do disposto no presente regulamento, são aplicáveis as definições que constam do perfil de aplicação HealthDCAT-AP a que se refere a parte A do anexo.

###### Artigo 3.º — Requisitos relativos aos elementos de metadados mínimos

A lista dos elementos de metadados mínimos que os detentores dos dados de saúde devem facultar no que se refere às descrições dos conjuntos de dados, bem como as características desses elementos, constam da parte B do anexo.

Os detentores dos dados de saúde devem expressar os elementos de metadados mínimos enumerados na parte B do anexo utilizando as definições, a estrutura, as cardinalidades e os vocabulários controlados estabelecidos no perfil de aplicação HealthDCAT-AP, a que se referem as partes A e C do anexo.

###### Artigo 4.º — Entrada em vigor

O presente regulamento entra em vigor no vigésimo dia seguinte ao da sua publicação no *Jornal Oficial da União Europeia*.

O presente regulamento é aplicável a partir de 26 de março de 2029.

O presente regulamento é obrigatório em todos os seus elementos e diretamente aplicável em todos os Estados-Membros.

Feito em Bruxelas, em 18 de setembro de 2026.

***Pela Comissão***

***A Presidente***

**Ursula VON DER LEYEN**

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/a1db9a95-b554-11f1-81de-01aa75ed71a1.0020.03/DOC_1#ntc1-L_202602098PT.000101-E0001) [JO L, 2025/327, 5.3.2025, ELI: http://data.europa.eu/eli/reg/2025/327/oj](https://data.europa.eu/eli/reg/2025/327/oj).
