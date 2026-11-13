---
schema_version: '1.0'
id: pt:cnpd:30732
title: Autorização da CNPD n.º 3782/2011
short_title: null
summary: Casa de Repouso Alexandrina Bartolomeu,Lda — Gestão de processos Clínicos
jurisdiction: regulator
territory: null
document_type: autorizacao-cnpd
document_type_label: Autorização da Comissão Nacional de Proteção de Dados
issuing_authority:
- Comissão Nacional de Proteção de Dados
proposing_entity: null
official_number: 3782/2011
official_date: '2011-04-11'
publication_date: null
publication: null
entry_into_force_dates: []
end_of_validity_date: null
legal_status: unknown
notes:
- 'Entidade: Casa de Repouso Alexandrina Bartolomeu,Lda'
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
  internal: pt:cnpd:30732
source:
  id: cnpd
  name: Comissão Nacional de Proteção de Dados
  official_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/30732
  metadata_url: https://www.cnpd.pt/decisoes/historico-de-decisoes/?year=2011&type=1
  content_url: https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/30732
  consolidated_url: null
  retrieved_at: '2026-11-13T07:24:18Z'
  retrieval_method: Histórico de decisões do site da CNPD (páginas HTML) e descarga do PDF de cada decisão; não é uma API
  source_modified_at: null
integrity:
  source_sha256: 85c8b0981719105f29920f298904c110d221a9044597a3a55d49755086adb957
  source_sha256_scope: official_source_content_bytes
provenance:
  collector: leis-portugal CNPD
  collector_version: 0.1.0
  generated_by: leis-portugal collect cnpd
  generated_at: '2026-11-13T07:24:18Z'
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
  checked_at: '2026-11-13T07:24:18Z'
  warnings: []
  errors: []
---

# Autorização da CNPD n.º 3782/2011

1
Proc. n.º 3696/2011
AUTORIZAÇÃO Nº 3782/ 2011
I. Pedido de autorização
A Casa de Repouso Alexandrina Bartolomeu, Lda notificou à CNPD um tratamento de dados pessoais decorrente do registo da informação no processo clínico electrónico, utilizando a aplicação ICARE-EHR, de toda a informação relacionada com um episódio clínico e o acompanhamento das diferentes acções em todos os sectores e etapas de atendimento do utente, nas quais se incluem:
a) Registo clínico;
b) Prescrição medicamentosa através de receita electrónica;
c) Gestão de consultas;
d) Facturação.
No âmbito da prescrição electrónica há comunicação de dados para a ACSS, no âmbito do
Sistema de Conferência de Facturas de Medicamentos;
Os dados pessoais registados são: n.º de processo, nome, sexo, data de nascimento, morada, estado civil, profissão, filiação, habilitações literárias, n.º de BI/Passaporte/Carta de Condução,
NIF, n.º de utente, subsistema de saúde, seguro de saúde, regime de comparticipação medicamentosa/isenção, fotografia do utente, dados clínicos (anamnese, história clínica, exame físico, diagnóstico, prognóstico, MCD, terapêutica, dados sobre os medicamentos prescrito, número da Ordem dos Médicos do prescritor, código do local de prescrição e dados da receita - número da receita, data da prescrição, tipo de receita – renovável/ não renovável –, notas e avaliação de enfermagem, alta, pareceres médicos, processo cirúrgico). São ainda registados os dados de marcação de consultas e de facturação.
A informação de prescrição fica associada ao tratamento relativo aos episódios de consulta.
A receita é impressa e entregue ao utente ou, se em ambiente hospitalar, enviada para a farmácia hospitalar para requisição do medicamento.

2
O acesso à informação pelos médicos, enfermeiros e funcionários administrativos está definido por diferentes perfis de utilizadores e níveis de acesso.
O profissional de saúde com o perfil “médico” pode registar e aceder a toda a informação, estando a capacidade de prescrever apenas disponível para este perfil.
Para o perfil “enfermeiro” apenas está disponível a visualização da informação necessária para os actos de enfermagem, o registo sobre os medicamentos prescritos e sobre a administração do medicamento no episódio.
O utilizador com o perfil de “administrativo” tem acesso às funcionalidades estritamente necessárias à sua actividade, podendo aceder a uma grelha com todas as consultas agendadas e efectuadas, altas, MCD agendados e dados de facturação.
A recolha dos dados de identificação, designadamente os constantes do Cartão do Cidadão, pode ser feita por leitura do chip do mesmo.
O acesso à informação para avaliação do funcionamento da consulta, quer na vertente clínica, quer na vertente financeira é efectuado de forma agregada, sem acesso a dados de identificação do doente.
Cada acto de prescrição é enviado à ACSS, através da rede privada multimédia do Ministério da Saúde, em ficheiro XML, para integração no Sistema de Conferência de Facturas de
Medicamentos através de acesso ao sítio da ACSS, via RIS (Rede Interna da Saúde), em protocolo HTTPS. A autenticação na aplicação faz-se por login e password fornecidos pela
ACSS.
São comunicados os seguintes dados: Dados do utente (sexo, data de nascimento, localidade);
Dados sobre o medicamento (n.º de registo, quantidade, tipo de medicamento, produtos abrangidos pelo protocolo da Diabetes, descrição do manipulado, autorização para fornecimento de genérico); Dados do médico prescritor (n.º de prescritor atribuído pela Ordem

3 dos Médicos); Local de prescrição e dados sobre a receita (n.º, data, tipo de receita, regime especial de comparticipação).
O Data Center da CimpleCare, Lda está localizado em Portugal.
Finalmente, importa ainda ter em conta que o software ICARE-EHR é propriedade da
CimpleCare, Lda, entidade que armazena a informação e que, por força de contrato com o responsável, assegura as medidas de segurança indicadas. Esta entidade assume a qualidade de subcontratada.
II. Apreciação Jurídica
Os dados pessoais recolhidos são pertinentes, necessários e não excessivos em relação à finalidade do tratamento (cf. artigo 5.º n.º 1 al. c) da Lei 67/98).
O tratamento de dados de saúde é realizado para fins de «medicina preventiva, de diagnóstico médico, de prestação de cuidados ou tratamentos médicos ou de gestão de serviços de saúde» (cf. artigo 7.º n.º 4 da Lei 67/98, de 26 de Outubro). Ao mesmo tempo, e tal como resulta do mesmo preceito, o tratamento desses dados é efectuado «por um profissional de saúde obrigado a sigilo ou por outra pessoa sujeita igualmente a segredo profissional».
A transmissão de dados à ACSS para integração no Sistema de Conferência de Facturas de
Medicamento já foi autorizada pela CNPD, designadamente nas Autorizações n.º 36/99 e 38/2001, apenas se alterando agora o suporte da comunicação.
Em relação ao tratamento da fotografia do doente admite-se que a sua recolha e subsequente tratamento seja útil ao profissional de saúde no âmbito do acompanhamento e prestação de cuidados de saúde. Embora se possa admitir que este dado não é imprescindível à finalidade, não se pode considerar que o mesmo é excessivo e não pertinente à luz do artigo 5.º n.º 1 alínea c) da Lei 67/98.

4
Assim, a CNPD admite que a fotografia seja tratada desde que – depois de assegurada uma informação sobre as finalidades – seja obtido o consentimento expresso do titular (cf. artigo 7.º, n.º2 da Lei 67/98).
Esta informação não pode ser utilizada para outra finalidade ou cedida a terceiros (cf. artigo 5.º n.º 1 al. b) da Lei 67/98, de 26 de Outubro.
A identificação dos utilizadores faz-se através de um nome de utilizador e password.
Quanto à segurança da informação, deve o responsável pelo tratamento adoptar regras de procedimento interno, de forma a analisar periodicamente os registos de acesso (logs), para garantir que os acessos à informação se efectuam de acordo com os princípios da necessidade e pertinência. Os logs e os relatórios de análise devem ser conservados durante o período máximo de conservação da informação, para efeitos de auditoria da CNPD no exercício das suas competências.
Relativamente à subcontratação com a CimpleCare, Lda, deve o responsável cumprir o disposto no artigo 14º da LPD, designadamente estabelecer um contrato ou acto jurídico com a subcontratada que a vincule ao cumprimento das obrigações de segurança do tratamento, previstas no n.º 1 do artigo 14º e, por se tratar de dados sensíveis, do artigo 15º, ambos da
LPD.
Nesse contrato ou acto jurídico, o qual revestirá a forma escrita, com valor probatório legalmente reconhecido, deve constar que o subcontratante apenas actua mediante instruções do responsável pelo tratamento e que lhe incumbe a obrigação de pôr em prática as medidas técnicas e organizativas adequadas para proteger os dados pessoais contra a destruição acidental ou ilícita, a perda acidental, a alteração, a difusão ou acesso não autorizados, bem como para garantir um nível de segurança adequado em relação aos riscos inerentes ao tratamento e à natureza dos dados a proteger (cf. artigo 14º da Lei n.º 67/98).
A CNPD determina, ao abrigo do n.º 4 do artigo 15º da LPD, que a circulação da informação em rede, porque pode pôr em risco direitos, liberdades e garantias dos titulares, deve ser encriptada.

5
Independentemente das medidas de segurança adoptadas pela entidade responsável pelo tratamento, é a esta que cabe assegurar o resultado da efectiva segurança da informação e dos dados tratados.
III. Decisão
Deste modo, a CNPD autoriza o tratamento de dados – cf. artigos 7.º n.º 2, e n.º4, 28.º n.º 1 al.
a), 23.º n.º 1 al. b) e 30º da Lei n.º 67/98 – com as condições acima referidas.
Termos do tratamento:
1. Responsável: Casa de Repouso Alexandrina Bartolomeu, Lda 2. Categorias de dados pessoais tratados: n.º de processo, nome, sexo, data de nascimento, morada, estado civil, profissão, filiação, habilitações literárias, n.º de
BI/Passaporte/Carta de Condução, NIF, n.º de utente, subsistema de saúde, seguro de saúde, regime de comparticipação medicamentosa/isenção, fotografia do utente, dados clínicos (anamnese, história clínica, exame físico, diagnóstico, prognóstico, MCD, terapêutica, dados sobre os medicamentos prescrito, número da Ordem dos Médicos do prescritor, código do local de prescrição e dados da receita - número da receita, data da prescrição, tipo de receita – renovável/ não renovável – notas e avaliação de enfermagem, alta, pareceres médicos, processo cirúrgico). São ainda registados os dados de marcação de consultas e de facturação.
3. Finalidade: Gestão do processo clínico e prescrição medicamentosa electrónica.
4. Entidades a quem podem ser transmitidos: ACSS, no âmbito do Sistema de Conferência de Facturas de Medicamentos, sem transmissão de dados pessoais dos utentes;
5. Forma de exercício do direito de acesso e rectificação: Por solicitação escrita ou pessoal. A informação de saúde é revelada por «intermediação médica» (cf. artigo 11.º n.º 5 da
Lei 67/98).
6. Eventuais interconexões: Não há.
7. Transferências de dados para países terceiros: Não há.
8. Tempo de conservação:
a) Dados de saúde – Nos termos do anexo à Portaria n.º 247/2000, de 8 de Maio;
b) Dados de facturação – 10 anos

6
Deve ser dado conhecimento da presente autorização a todos os intervenientes no circuito da informação, designadamente aos utilizadores do sistema e ao subcontratado.
Lisboa, 11 de Abril de 2011
Ana Roque, Luís Barroso, Carlos Campos Lobo, Helena Delgado António, Luís Paiva de
Andrade, Vasco Almeida
Luís Lingnau da Silveira (Presidente)
