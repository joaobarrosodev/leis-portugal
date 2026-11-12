---
schema_version: '1.0'
id: eu:celex:32025R0645:por
title: Regulamento Delegado (UE) 2025/645 da Comissão, de 1 de abril de 2025
short_title: null
summary: Regulamento Delegado (UE) 2025/645 da Comissão, de 1 de abril de 2025, que complementa o Regulamento (UE) 2023/1804
  do Parlamento Europeu e do Conselho no que diz respeito aos requisitos técnicos comuns para uma interface comum do programa
  de aplicações
jurisdiction: european_union
territory: null
document_type: regulation
document_type_label: Regulamento Delegado
issuing_authority:
- Comissão Europeia
- MOVE
proposing_entity: null
official_number: 2025/645
official_date: null
publication_date: '2025-06-18'
publication:
  gazette: Jornal Oficial da União Europeia
  reference: JO L, 2025/645, 18.6.2025
  number: '645'
  series: L
  supplement: null
  pages: null
  pdf_url: http://publications.europa.eu/resource/cellar/7d7eb793-4bdc-11f0-85ba-01aa75ed71a1.0020.01/DOC_1
entry_into_force_dates:
- '2025-04-14'
- '2025-07-08'
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
  celex: 32025R0645
  eli: http://data.europa.eu/eli/reg_del/2025/645/oj
  oj: oj:L_202500645
  dre: null
  dre_path: null
  internal: eu:celex:32025R0645:por
source:
  id: eurlex-cellar
  name: EUR-Lex / CELLAR
  official_url: https://eur-lex.europa.eu/legal-content/PT/TXT/?uri=CELEX%3A32025R0645
  metadata_url: http://publications.europa.eu/resource/cellar/7d7eb793-4bdc-11f0-85ba-01aa75ed71a1.0020
  content_url: http://publications.europa.eu/resource/cellar/7d7eb793-4bdc-11f0-85ba-01aa75ed71a1.0020.03/DOC_1
  consolidated_url: null
  retrieved_at: '2026-11-12T01:30:25Z'
  retrieval_method: CELLAR RDF + SPARQL + negociação de conteúdo XHTML
  source_modified_at: '2025-06-18T02:52:18.349+02:00'
integrity:
  source_sha256: 13b092d46633274684195a33ea506f18161bcf0942d48a94cd453c42205189c0
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal EUR-Lex/CELLAR
  collector_version: 0.1.0
  generated_by: leis-portugal collect eurlex
  generated_at: '2026-11-12T01:30:25Z'
  notes: null
reuse:
  status: permitted_with_conditions
  attribution: União Europeia, EUR-Lex / Publicações da União Europeia
  reference: https://eur-lex.europa.eu/content/legal-notice/legal-notice.html
  notes: Verificar o aviso jurídico aplicável; só o texto publicado no Jornal Oficial faz fé (as consolidações são instrumentos
    de documentação).
subjects:
- combustível de substituição
- distribuição de eletricidade
- hidrogénio
- infraestrutura do transporte
- interface de programação de aplicações
- mobilidade sustentável
- norma técnica
- recursos energéticos
- redução das emissões de gases
- tecnologia limpa
relationships:
- type: based_on
  target: celex:32023R1804
  label: null
  source: http://publications.europa.eu/resource/cellar/6337734c-58e4-11ee-9220-01aa75ed71a1
  date: '2023-09-22'
- type: cites
  target: celex:32010L0040
  label: null
  source: http://publications.europa.eu/resource/cellar/c2d58141-334a-4cd8-be0f-b9b9840d2efd
article_structure:
  article_count: 2
  section_count: 0
  extraction_method: Classes XHTML do CELLAR (oj-ti-art / title-article-norm)
derived_material:
  machine_generated: true
  notes: O Markdown é uma conversão derivada do XHTML do CELLAR; o conteúdo-fonte é identificado pelo URL e SHA-256.
validation:
  status: validated
  checked_at: '2026-11-12T01:30:25Z'
  warnings: []
  errors: []
---

# REGULAMENTO DELEGADO (UE) 2025/645 DA COMISSÃO

de 1 de abril de 2025

que complementa o Regulamento (UE) 2023/1804 do Parlamento Europeu e do Conselho no que diz respeito aos requisitos técnicos comuns para uma interface comum do programa de aplicações

A COMISSÃO EUROPEIA,

Tendo em conta o Tratado sobre o Funcionamento da União Europeia,

Tendo em conta o Regulamento (UE) 2023/1804 do Parlamento Europeu e do Conselho, de 13 de setembro de 2023, relativo à criação de uma infraestrutura para combustíveis alternativos e que revoga a Diretiva 2014/94/UE [([^1])](http://publications.europa.eu/resource/cellar/7d7eb793-4bdc-11f0-85ba-01aa75ed71a1.0020.03/DOC_1#ntr1-L_202500645PT.000101-E0001), nomeadamente o artigo 20.º, n.º 6, alínea b),

Considerando o seguinte:

(1) O artigo 20.º, n.º 2, do Regulamento (UE) 2023/1804 estabelece que, até 14 de abril de 2025, os operadores dos pontos de carregamento e dos pontos de abastecimento para combustíveis alternativos acessíveis ao público, ou os proprietários desses pontos, em conformidade com as disposições acordadas entre si, asseguram a disponibilização sem custos de dados estáticos e de dados dinâmicos relativos à infraestrutura para combustíveis alternativos por eles operada ou aos serviços intrinsecamente ligados a essa infraestrutura por eles prestados ou externalizados.

(2) A fim de proporcionar um acesso livre e sem restrições a esses dados e permitir um intercâmbio automatizado e uniforme de dados entre os operadores dos pontos de carregamento e abastecimento acessíveis ao público e os utilizadores de dados, o artigo 20.º, n.º 3, do Regulamento (UE) 2023/1804 exige que cada operador de pontos de carregamento e abastecimento de combustíveis alternativos acessíveis ao público ou, em conformidade com as disposições acordadas entre si, o proprietário desses pontos, crie uma interface do programa de aplicações (API).

(3) O presente regulamento estabelece requisitos técnicos comuns para uma API comum, a fim de permitir um intercâmbio automatizado e uniforme de dados entre os operadores dos pontos de carregamento e abastecimento de combustíveis alternativos acessíveis ao público e os utilizadores de dados.

(4) Os operadores de pontos de carregamento e abastecimento acessíveis ao público ou os proprietários desses pontos podem criar eles próprios essas API ou utilizar uma solução de protocolo para API desenvolvida pelos intervenientes no mercado pertinentes, incluindo prestadores terceiros. Essas soluções de protocolo para API devem cumprir os requisitos técnicos comuns para API estabelecidos no presente regulamento.

(5) A fim de promover especificamente a interoperabilidade, a convergência e uma maior transparência das API baseadas em soluções de protocolo desenvolvidas pelos intervenientes no mercado relevantes para os diferentes pontos de carregamento e pontos de abastecimento de combustíveis alternativos acessíveis ao público, é necessário introduzir uma série de requisitos técnicos comuns. Esses requisitos técnicos deverão assegurar um mínimo de compatibilidade, escalabilidade, robustez e segurança, a fim de permitir um intercâmbio automatizado e uniforme de dados entre os operadores de pontos de carregamento e de pontos de abastecimento de combustíveis alternativos acessíveis ao público e os utilizadores de dados em toda a União.

(6) A fim de assegurar o desenvolvimento previsível das API para os operadores de pontos de carregamento e abastecimento acessíveis ao público ou para os proprietários desses pontos, os requisitos técnicos comuns devem assegurar que as soluções de protocolo contêm informações sobre as API baseadas num plano de desenvolvimento técnico pormenorizado e acessível ao público, por exemplo num sítio Web específico, com os pormenores operacionais pertinentes que esclareçam a execução técnica e a continuidade ao longo do tempo. Este requisito deverá também facilitar o acesso dos operadores interessados da infraestrutura para combustíveis alternativos à documentação e a orientações atualizadas e acessíveis ao público com vista a uma utilização e integração sem descontinuidades pelos utilizadores dos dados, incluindo formação exaustiva e materiais de apoio técnico.

(7) Os requisitos técnicos comuns para uma API comum deverão adicionalmente facilitar o trabalho técnico dos Estados-Membros quando estes tornarem acessíveis os dados relativos à infraestrutura para combustíveis alternativos sob a forma de dados abertos através dos PAN, em conformidade com o artigo 20.º, n.º 4, do Regulamento (UE) 2023/1804 e a Diretiva 2010/40/UE do Parlamento Europeu e do Conselho [([^2])](http://publications.europa.eu/resource/cellar/7d7eb793-4bdc-11f0-85ba-01aa75ed71a1.0020.03/DOC_1#ntr2-L_202500645PT.000101-E0002), e em conformidade com as especificações adicionais dos regulamentos delegados adotados com base nessa diretiva.

(8) Prevendo a evolução futura e a aplicação do artigo 20.º, n.º 5, do Regulamento (UE) 2023/1804, os requisitos técnicos comuns para uma API comum devem contribuir para a criação técnica do ponto de acesso europeu comum que a Comissão deve estabelecer até 31 de dezembro de 2026. Tais requisitos técnicos comuns devem contribuir para o futuro funcionamento do ponto de acesso europeu comum, de modo que os utilizadores de dados possam aceder facilmente aos dados e comparar informações sobre as características da infraestrutura para combustíveis alternativos, como o preço, a acessibilidade, a disponibilidade ou a potência.

(9) O artigo 20.º, n.º 8, do Regulamento (UE) 2023/1804 exige que os atos delegados e os atos de execução a que se referem os n.^os^ 6 e 7 do mesmo artigo devem prever períodos transitórios razoáveis antes de as disposições neles contidas, ou as suas alterações, se tornarem vinculativas para os operadores ou proprietários de pontos de carregamento e de pontos de abastecimento para combustíveis alternativos. Por conseguinte, o presente regulamento deve ser aplicável a partir de 14 de abril de 2025, uma vez que essa data coincide com a data de aplicação do artigo 20.º, n.º 2, do Regulamento (UE) 2023/1804,

ADOTOU O PRESENTE REGULAMENTO:

###### Artigo 1.º — Requisitos técnicos comuns para uma interface comum do programa de aplicações

1. A interface do programa de aplicações (API), referida no artigo 20.º, n.º 3, do Regulamento (UE) 2023/1804, deve cumprir os seguintes requisitos técnicos comuns:

a) Ser tecnicamente compatível, se for caso disso, com os sistemas de gestão de *software* dos pontos de carregamento e abastecimento de combustíveis alternativos e com os pontos de acesso nacionais;

b) Facilitar a utilização pelos utilizadores dos dados, a fim de apoiar o desenvolvimento de serviços de informação de elevada qualidade sobre combustíveis alternativos;

c) Ser escalável e capaz de lidar com quantidades crescentes de dados em tempo real ao longo do tempo;

d) Ser robusta e capaz de fazer face a erros durante a execução;

e) Ser segura e incluir medidas de proteção pertinentes para evitar o acesso indevido aos dados;

f) Ser submetida a testes e validação regulares, a fim de assegurar a continuidade da compatibilidade e da fiabilidade;

g) Ser escalável, para apoiar a integração num portal Web específico de um ponto de acesso europeu comum que funcione como um portal de dados que facilite o acesso aos dados a que se refere o artigo 20.º, n.º 2, do Regulamento (UE) 2023/1804.

2. Sempre que os operadores de pontos de carregamento e pontos de abastecimento acessíveis ao público ou, em conformidade com as disposições acordadas entre si, os proprietários desses pontos dependam de uma solução de protocolo para a API a que se refere o artigo 20.º, n.º 3, do Regulamento (UE) 2023/1804, desenvolvida por outro interveniente no mercado ou prestador terceiro, devem assegurar, para além do disposto no n.º 1, que essa solução de protocolo cumpre os seguintes requisitos técnicos comuns:

a) Deve conter um plano de desenvolvimento técnico pormenorizado e acessível ao público, com calendários transparentes para esclarecer a execução técnica e a continuidade ao longo do tempo;

b) Deve providenciar documentação e orientações atualizadas e acessíveis ao público para a utilização e integração sem descontinuidades pelos utilizadores dos dados;

c) Deve fornecer formação exaustiva e apoio técnico aos utilizadores dos dados, a fim de facilitar o desenvolvimento e a implementação bem-sucedidos de serviços de informação;

d) Deve ser tecnicamente compatível, se for caso disso, com os requisitos de arquitetura dos pontos de acesso nacionais (PAN);

e) Deve ser escalável com vista à integração num portal Web específico de um ponto de acesso europeu comum para dados sobre combustíveis alternativos.

3. Se, à data de entrada em vigor do presente regulamento, os Estados-Membros já tiverem prescrito a utilização de uma API específica baseada em requisitos técnicos nacionais no seu território, esses requisitos técnicos nacionais para as API só são aplicáveis na medida em que cumpram o presente regulamento.

###### Artigo 2.º — Entrada em vigor e aplicação

O presente regulamento entra em vigor no vigésimo dia seguinte ao da sua publicação no *Jornal Oficial da União Europeia*.

É aplicável a partir de 14 de abril de 2025.

O presente regulamento é obrigatório em todos os seus elementos e diretamente aplicável em todos os Estados-Membros.

Feito em Bruxelas, em 1 de abril de 2025.

***Pela Comissão***

***A Presidente***

**Ursula VON DER LEYEN**

---

## Notas

> [(^1^)](http://publications.europa.eu/resource/cellar/7d7eb793-4bdc-11f0-85ba-01aa75ed71a1.0020.03/DOC_1#ntc1-L_202500645PT.000101-E0001) [JO L 234 de 22.9.2023, p. 1](http://publications.europa.eu/resource/oj/JOL_2023_234_R_TOC), ELI: [http://data.europa.eu/eli/reg/2023/1804/oj](http://data.europa.eu/eli/reg/2023/1804/oj).

> [(^2^)](http://publications.europa.eu/resource/cellar/7d7eb793-4bdc-11f0-85ba-01aa75ed71a1.0020.03/DOC_1#ntc2-L_202500645PT.000101-E0002) Diretiva 2010/40/UE do Parlamento Europeu e do Conselho, de 7 de julho de 2010, que estabelece um quadro para a implantação de sistemas de transporte inteligentes no transporte rodoviário, inclusive nas interfaces com outros modos de transporte ([JO L 207 de 6.8.2010, p. 1](http://publications.europa.eu/resource/oj/JOL_2010_207_R_TOC), ELI: [http://data.europa.eu/eli/dir/2010/40/oj](http://data.europa.eu/eli/dir/2010/40/oj)).
