---
schema_version: '1.0'
id: eu:celex:32026R1233:por
title: Regulamento de Execução (UE) 2026/1233 da Comissão, de 11 de junho de 2026
short_title: null
summary: Regulamento de Execução (UE) 2026/1233 da Comissão, de 11 de junho de 2026, que estabelece as especificações do serviço
  comum de endereçamento para o ambiente europeu de plataforma única para o setor marítimo
jurisdiction: european_union
territory: null
document_type: regulation
document_type_label: Regulamento de Execução
issuing_authority:
- Comissão Europeia
- MOVE
proposing_entity: null
official_number: 2026/1233
official_date: null
publication_date: '2026-06-12'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L, 2026/1233, 12.6.2026
  number: '1233'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.01/DOC_1
entry_into_force_dates:
- '2026-07-02'
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
  celex: 32026R1233
  eli: http://data.europa.eu/eli/reg_impl/2026/1233/oj
  oj: oj:L_202601233
  dre: null
  dre_path: null
  internal: eu:celex:32026R1233:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32026R1233
  metadata_url: http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020
  content_url: http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-10-22T03:46:01Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2026-06-12T03:05:16.959+02:00'
integrity:
  source_sha256: 71d1777d1960096533b6f42dab93e2d8b0ead694002efd7a5ec8e27296171f7b
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-10-22T03:46:01Z'
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
  target: celex:32023R2790
  label: null
  source: http://publications.europa.eu/resource/cellar/f7289f0e-9d46-11ee-b164-01aa75ed71a1
- type: cites
  target: celex:32024R0903
  label: null
  source: http://publications.europa.eu/resource/cellar/c008bcb6-e7ec-11ee-9ea8-01aa75ed71a1
article_structure:
  article_count: 3
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-10-22T03:46:01Z'
  warnings: []
  errors: []
---

# REGULAMENTO DE EXECUÇÃO (UE) 2026/1233 DA COMISSÃO

de 11 de junho de 2026

que estabelece as especificações do serviço comum de endereçamento para o ambiente europeu de plataforma única para o setor marítimo

(Texto relevante para efeitos do EEE)

A COMISSÃO EUROPEIA,

Tendo em conta o Tratado sobre o Funcionamento da União Europeia,

Tendo em conta o Regulamento (UE) 2019/1239 do Parlamento Europeu e do Conselho, de 20 de junho de 2019, que estabelece um ambiente europeu de plataforma única para o setor marítimo e que revoga a Diretiva 2010/65/UE [([^1])](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntr1-L_202601233PT.000101-E0001), nomeadamente o artigo 13.º,

Após consulta do Comité de Facilitação Digital dos Transportes e do Comércio,

Considerando o seguinte:

(1) No contexto do ambiente europeu de plataforma única para o setor marítimo estabelecido pelo Regulamento (UE) 2019/1239, os declarantes e os prestadores de serviços de dados (remetentes) podem cumprir as suas obrigações de declaração através de uma conexão sistema a sistema ao módulo de interface de declaração (RIM) das plataformas nacionais únicas para o setor marítimo (MNSW).

(2) O RIM, desenvolvido em conformidade com as especificações estabelecidas no Regulamento de Execução (UE) 2023/2790 da Comissão [([^2])](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntr2-L_202601233PT.000101-E0002), assegura a interoperabilidade técnica e a utilização de um conjunto harmonizado de mensagens para o intercâmbio de dados com as MNSW. Antes de os remetentes trocarem dados com a MNSW através do RIM, os dados de conexão têm de ser configurados manualmente. Tal é igualmente necessário em caso de alteração dos dados de conexão. O serviço comum de endereçamento deverá resolver este problema, facilitando a configuração automática da conexão direta de sistema a sistema.

(3) O serviço comum de endereçamento deverá utilizar a funcionalidade de descoberta dinâmica, que assegura a flexibilidade e escalabilidade da rede de MNSW. Os remetentes deverão poder utilizar o serviço comum de endereçamento para iniciar uma conexão de dados direta de sistema a sistema entre o respetivo ponto de acesso AS4 e um RIM, através da recuperação automática dos dados de conexão mais recentes de um RIM.

(4) O serviço comum de endereçamento deverá minimizar a necessidade de intervenções humanas e deverá, por conseguinte, reduzir proporcionalmente os custos e os riscos de erros, tornando a rede flexível em caso de alteração dos dados de conexão dos seus participantes, tais como informações sobre o ponto terminal e o certificado público.

(5) A fim de assegurar a interoperabilidade e a redução dos custos de execução, o serviço comum de endereçamento deverá basear-se nas mesmas tecnologias e normas utilizadas para o RIM.

(6) O nó localizador central deverá conter os identificadores dos participantes e a localização dos nós editores, e deverá ser alojado centralmente para assegurar que esses dados sejam mantidos atualizados no sistema de nomes de domínio (DNS) público.

(7) A fim de reforçar a resiliência do serviço e atenuar o risco de um único ponto de falha, cada Estado-Membro deverá dispor do seu próprio nó editor, que deverá conter todos os dados de conexão necessários do RIM correspondente.

(8) A fim de assegurar a escalabilidade e a flexibilidade também para as autoridades dos Estados-Membros que gerem as MNSW, os Estados-Membros deverão poder igualmente armazenar, nos respetivos nós editores, os dados de conexão dos pontos de acesso AS4 dos remetentes, em alternativa à pré-configuração manual desses dados no respetivo RIM.

(9) A fim de tornar o respetivo nó editor detetável para os utilizadores do serviço comum de endereçamento, assegurar a exatidão e a disponibilidade do endereço do nó editor no DNS público e impedir que os utilizadores do serviço comum de endereçamento descubram nós editores desativados ou inexistentes, os Estados-Membros deverão poder registar, atualizar e apagar os dados do respetivo nó editor através do nó localizador central.

(10) As plataformas nacionais únicas para o setor marítimo constituem um serviço público digital transfronteiriço na aceção do Regulamento (UE) 2024/903 do Parlamento Europeu e do Conselho [([^3])](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntr3-L_202601233PT.000101-E0003) («Regulamento Europa Interoperável»). O presente regulamento introduz novos requisitos vinculativos que afetam os serviços públicos digitais supramencionados e, nessa medida, está sujeito à obrigação de avaliação da interoperabilidade nos termos do artigo 3.º do Regulamento Europa Interoperável. Por conseguinte, realizou-se uma avaliação da interoperabilidade, devendo o relatório resultante ser publicado no portal Europa Interoperável,

ADOTOU O PRESENTE REGULAMENTO:

###### Artigo 1.º

Para efeitos do presente regulamento, são aplicáveis as definições constantes do artigo 1.º do Regulamento de Execução (UE) 2023/2790.

São igualmente aplicáveis as seguintes definições:

1) «descoberta dinâmica», um mecanismo que permite tanto aos pontos de acesso AS4 dos remetentes como aos RIM obter automaticamente os dados de conexão uns dos outros para iniciar uma conexão direta;

2) «eDelivery», um conjunto de especificações e normas técnicas para o intercâmbio de mensagens eletrónicas desenvolvido pela Comissão;

3) «nó localizador central», um localizador de metadados de serviços (SML) conforme com as especificações do perfil eDelivery [([^4])](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntr4-L_202601233PT.000101-E0004) que facilita a descoberta dinâmica através do sistema de nomes de domínio (DNS) público;

4) «nó editor», um editor de serviços de metadados (SMP) conforme com as especificações do perfil eDelivery [([^5])](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntr5-L_202601233PT.000101-E0005) que contém os dados de conexão dos módulos de interface de declaração (RIM) e dos pontos de acesso AS4 dos remetentes;

5) «serviço comum de endereçamento», o serviço a que se refere o artigo 2.º, n.º 10, do Regulamento (UE) 2019/1239.

###### Artigo 2.º

As especificações funcionais e técnicas, os mecanismos de controlo da qualidade e os procedimentos de implantação, manutenção e utilização do serviço comum de endereçamento constam do anexo do presente regulamento.

###### Artigo 3.º

O presente regulamento entra em vigor no vigésimo dia seguinte ao da sua publicação no *Jornal Oficial da União Europeia*.

O presente regulamento é obrigatório em todos os seus elementos e diretamente aplicável em todos os Estados-Membros.

Feito em Bruxelas, em 11 de junho de 2026.

***Pela Comissão***

***A Presidente***

**Ursula VON DER LEYEN**

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntc1-L_202601233PT.000101-E0001) [JO L 198 de 25.7.2019, p. 64](http://publications.europa.eu/resource/oj/JOL_2019_198_R_TOC). ELI: [http://data.europa.eu/eli/reg/2019/1239/oj](http://data.europa.eu/eli/reg/2019/1239/oj).

> [(^2^)](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntc2-L_202601233PT.000101-E0002) Regulamento de Execução (UE) 2023/2790 da Comissão, de 14 de dezembro de 2023, que estabelece as especificações funcionais e técnicas do módulo de interface de declaração das plataformas nacionais únicas para o setor marítimo ([JO L, 2023/2790, 18.12.2023, ELI: http://data.europa.eu/eli/reg_impl/2023/2790/oj](https://data.europa.eu/eli/reg_impl/2023/2790/oj)).

> [(^3^)](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntc3-L_202601233PT.000101-E0003) Regulamento (UE) 2024/903 do Parlamento Europeu e do Conselho, de 13 de março de 2024, que estabelece medidas para um elevado nível de interoperabilidade do setor público em toda a União (Regulamento Europa Interoperável) ([JO L, 2024/903, 22.3.2024, ELI: http://data.europa.eu/eli/reg/2024/903/oj](https://data.europa.eu/eli/reg/2024/903/oj)).

> [(^4^)](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntc4-L_202601233PT.000101-E0004) [https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/SML+service](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/SML+service).

> [(^5^)](http://publications.europa.eu/resource/cellar/e7d2b7d5-65f7-11f1-9b18-01aa75ed71a1.0020.03/DOC_1#ntc5-L_202601233PT.000101-E0005) [https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/SMP+software](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/SMP+software).
