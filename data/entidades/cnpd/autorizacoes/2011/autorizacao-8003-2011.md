---
schema_version: '1.0'
id: pt:cnpd:34696
title: Autorização da CNPD n.º 8003/2011
short_title: null
summary: CERRO – Consultório de Estomatologia, Radiologia e Reabilitação Oral, Lda. — Prescrição Eletronica
jurisdiction: regulator
territory: null
document_type: autorizacao-cnpd
document_type_label: Autorização da Comissão Nacional de Proteção de Dados
issuing_authority:
- Comissão Nacional de Proteção de Dados
proposing_entity: null
official_number: 8003/2011
official_date: '2011-07-28'
publication_date: null
publication: null
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes:
- 'Entidade: CERRO – Consultório de Estomatologia, Radiologia e Reabilitação Oral, Lda.'
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
  internal: pt:cnpd:34696
source:
  id: cnpd
  name: Comissão Nacional de Proteção de Dados
  official_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/34696
  metadata_url: https://www.cnpd.pt/decisoes/historico-de-decisoes/?year=2011&type=1
  content_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/34696
  consolidated_url: null
  retrieved_at: '2026-11-13T06:13:02Z'
  retrieval_method: Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API
  source_modified_at: null
integrity:
  source_sha256: 65ae77518ffcc32bae1cf7c3ccb27f33f1b231a214f71c760ac1f4a3f1c10eb7
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal CNPD
  collector_version: 0.1.0
  generated_by: leis-portugal collect cnpd
  generated_at: '2026-11-13T06:13:02Z'
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
  checked_at: '2026-11-13T06:13:02Z'
  warnings: []
  errors: []
---

# Autorização da CNPD n.º 8003/2011

1
Proc. n.º 10744/2011
AUTORIZAÇÃO Nº 8003/ 2011
I. Pedido de autorização
O Cerro – Consultório de Estomatologia, Radiologia e Reabilitação Oral, Lda. notificou à
CNPD um tratamento de dados pessoais decorrente do registo da informação no processo clínico electrónico de toda a informação relacionada com um episódio clínico e o acompanhamento das diferentes acções em todos os sectores e etapas de atendimento do utente, nas quais se incluem:
a) Registo clínico;
b) Prescrição medicamentosa através de receita electrónica;
c) Gestão de consultas;
d) Facturação.
No âmbito da prescrição electrónica há comunicação de dados para a ACSS, no âmbito do
Sistema de Conferência de Facturas de Medicamentos;
Os dados pessoais registados são: n.º de processo, nome, sexo, data de nascimento, morada, estado civil, profissão, filiação, habilitações literárias, n.º de BI/Passaporte/Carta de Condução,
NIF, n.º de utente, subsistema de saúde, seguro de saúde, regime de comparticipação medicamentosa/isenção, dados clínicos (anamnese, história clínica, exame físico, diagnóstico, prognóstico, MCD, terapêutica, dados sobre os medicamentos prescritos, número da Ordem dos Médicos do prescritor, código do local de prescrição e dados da receita - número da receita, data da prescrição, tipo de receita – renovável/ não renovável –, notas e avaliação de enfermagem, alta, pareceres médicos, processo cirúrgico). São ainda registados os dados de marcação de actos clínicos e de facturação.
A informação de prescrição fica associada ao tratamento relativo aos episódios de consulta.
O acesso à informação pelos médicos, enfermeiros e funcionários administrativos está definido por diferentes perfis de utilizadores e níveis de acesso.
O profissional de saúde com o perfil “médico” pode registar e aceder a toda a informação, estando a capacidade de prescrever apenas disponível para este perfil.

2
Para o perfil “enfermeiro” apenas está disponível a visualização da informação necessária para os actos de enfermagem, o registo sobre os medicamentos prescritos e sobre a administração do medicamento no episódio.
O utilizador com o perfil de “administrativo” tem acesso às funcionalidades estritamente necessárias à sua actividade, podendo aceder a uma grelha com todas as consultas agendadas e efectuadas, altas, MCD agendados e dados de facturação.
A receita é impressa e entregue ao utente ou, se em ambiente hospitalar, enviada para a farmácia hospitalar para requisição do medicamento.
Quanto aos dados automatizados, o sistema deve garantir uma separação lógica entre os dados referentes à saúde e os restantes dados pessoais, de natureza administrativa (art. 15.º n.º3 da Lei 67/98). Nesse sentido, o sistema informatizado deve estar estruturado, de modo a permitir o acesso à informação de acordo com os diferentes perfis de utilizador, com níveis de acesso e privilégios de manuseamento da informação distintos. Deverão ser atribuídas palavras-passe que disciplinem as autorizações de acesso.
O acesso à informação para avaliação do funcionamento da consulta, quer na vertente clínica, quer na vertente financeira é efectuado de forma agregada, sem acesso a dados de identificação do doente.
Cada acto de prescrição é enviado à ACSS, através da rede privada multimédia do Ministério da Saúde, em ficheiro XML, para integração no Sistema de Conferência de Facturas de
Medicamentos através de acesso ao sítio da ACSS, via RIS (Rede Interna da Saúde), em protocolo HTTPS. A autenticação na aplicação faz-se por login e password fornecidos pela
ACSS.
São comunicados os seguintes dados: Dados do utente (sexo, data de nascimento, localidade);
Dados sobre o medicamento (n.º de registo, quantidade, tipo de medicamento, produtos abrangidos pelo protocolo da Diabetes, descrição do manipulado, autorização para fornecimento de genérico); Dados do médico prescritor (n.º de prescritor atribuído pela Ordem dos Médicos); Local de prescrição e dados sobre a receita (n.º, data, tipo de receita, regime especial de comparticipação).

3
II. Apreciação Jurídica
Os dados pessoais recolhidos são pertinentes, necessários e não excessivos em relação à finalidade do tratamento (cf. artigo 5.º n.º 1 al. c) da Lei 67/98).
O tratamento de dados de saúde é realizado para fins de «medicina preventiva, de diagnóstico médico, de prestação de cuidados ou tratamentos médicos ou de gestão de serviços de saúde» (cf. artigo 7.º n.º 4 da Lei 67/98, de 26 de Outubro). Ao mesmo tempo, e tal como resulta do mesmo preceito, o tratamento desses dados é efectuado «por um profissional de saúde obrigado a sigilo ou por outra pessoa sujeita igualmente a segredo profissional».
A transmissão de dados à ACSS para integração no Sistema de Conferência de Facturas de
Medicamento já foi autorizada pela CNPD, designadamente nas Autorizações n.º 36/99 e 38/2001, apenas se alterando agora o suporte da comunicação.
A identificação dos utilizadores faz-se através de um nome de utilizador e password.
Quanto à segurança da informação, deve o responsável pelo tratamento adoptar regras de procedimento interno, de forma a analisar periodicamente os registos de acesso (logs), para garantir que os acessos à informação se efectuam de acordo com os princípios da necessidade e pertinência. Os logs e os relatórios de análise devem ser conservados durante o período máximo de conservação da informação, para efeitos de auditoria da CNPD no exercício das suas competências.
III. Decisão
Deste modo, a CNPD autoriza o tratamento de dados – cf. artigos 7.º n.º 2, e n.º4, 28.º n.º 1 al.
a), 23.º n.º 1 al. b) e 30º da Lei n.º 67/98 – com as condições acima referidas. Termos do tratamento:
1. Responsável: Cerro – Consultório de Estomatologia, Radiologia e Reabilitação Oral, Lda.
2. Categorias de dados pessoais tratados: n.º de processo, nome, sexo, data de nascimento, morada, estado civil, profissão, filiação, habilitações literárias, n.º de
BI/Passaporte/Carta de Condução, NIF, n.º de utente, subsistema de saúde, seguro de saúde, regime de comparticipação medicamentosa/isenção, dados clínicos (anamnese, história clínica, exame físico, diagnóstico, prognóstico, MCD, terapêutica, dados sobre os medicamentos

4 prescrito, número da Ordem dos Médicos do prescritor, código do local de prescrição e dados da receita - número da receita, data da prescrição, tipo de receita – renovável/ não renovável – notas e avaliação de enfermagem, alta, pareceres médicos, processo cirúrgico). São ainda registados os dados de marcação de consultas e de facturação.
3. Finalidade: Gestão do processo clínico e prescrição medicamentosa electrónica.
4. Entidades a quem podem ser transmitidos: ACSS, no âmbito do Sistema de Conferência de Facturas de Medicamentos, sem transmissão de dados pessoais dos utentes;
5. Forma de exercício do direito de acesso e rectificação: Por solicitação escrita ou pessoal. A informação de saúde é revelada por «intermediação médica» (cf. artigo 11.º n.º 5 da
Lei 67/98).
6. Eventuais interconexões: Não há.
7. Transferências de dados para países terceiros: Não há.
8. Tempo de conservação:
a) Dados de saúde – Nos termos do anexo à Portaria n.º 247/2000, de 8 de Maio;
b) Dados de facturação – 10 anos.
Esta Autorização é emitida no pressuposto de que o software em questão foi certificado pela ACSS.
Lisboa, 28 de Julho de 2011
Ana Roque, Luís Barroso, Carlos Campos Lobo, Helena Delgado António, Luís Paiva de
Andrade, Vasco Almeida
Luís Lingnau da Silveira (Presidente)
