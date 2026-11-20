# Inventário da camada 1: tabelas geradas

Gerado a 2026-11-20 por `scripts/inventario_camada_1.py`, a partir de `leis-portugal.sqlite` (405830 registos portugueses). Não editar à mão: a leitura está em `reports/inventario-camada-1.md`.

## 1. Texto em vigor dos diplomas alterados

Prioritários da 1.ª Série, em vigor ou de vigência desconhecida, com `amended_by`.

| Classe | lei | lei-organica | lei-constitucional | decreto-lei | decreto-regulamentar | decreto-legislativo-regional | Total |
|---|--:|--:|--:|--:|--:|--:|--:|
| consolidado_dre | 472 | 11 | 0 | 1556 | 63 | 235 | 2337 |
| consolidado_leis_portugal | 48 | 1 | 0 | 660 | 60 | 74 | 843 |
| texto_noutro_registo | 3 | 0 | 0 | 24 | 1 | 10 | 38 |
| original_e_o_texto_em_vigor | 592 | 23 | 7 | 2496 | 273 | 234 | 3625 |
| alteracao_por_aplicar | 51 | 0 | 0 | 477 | 77 | 67 | 672 |
| alteracao_so_em_imagem | 1 | 0 | 0 | 14 | 1 | 0 | 16 |
| nao_triado | 218 | 17 | 0 | 375 | 22 | 53 | 685 |
| revogado_por_inteiro | 5 | 2 | 0 | 119 | 47 | 44 | 217 |
| sem_texto | 216 | 0 | 0 | 1041 | 0 | 0 | 1257 |
| **Total** | 1606 | 54 | 7 | 6762 | 544 | 717 | 9690 |

Consolidados em dia: 2957; com alterador publicado depois da última versão: 213; que o DRE mexeu depois da recolha: 35.

Portarias (só contagens): original_e_o_texto_em_vigor 10258, alteracao_por_aplicar 1689, consolidado_leis_portugal 1307, consolidado_dre 1097, alteracao_so_em_imagem 413, revogado_por_inteiro 409, nao_triado 305, sem_texto 99.

Marcas da vigência revista (`consolidacao/auditoria/vigencia-revista.jsonl`): no ficheiro, nao_vigora 166, por_confirmar 57, regime_anterior 194; nos prioritários deste universo, nao_vigora 29, por_confirmar 11, regime_anterior 4; nas portarias, nao_vigora 84, por_confirmar 35, regime_anterior 189.

## 2. Textos cujo texto em vigor está fora do registo que os aprovou (77)

| Texto de (origem) | Texto mais recente em | Parte | Artigos | Texto até | Origem aponta para lá | Origem servida como em vigor | Epígrafes iguais (mesmo n.º) | Outras cópias desatualizadas servidas |
|---|---|---|--:|---|---|---|---|---|
| Decreto-Lei n.º 400/82 | Decreto-Lei n.º 48/95 | (2.ª numeração) | 432 | 2026-09-01 | **não** | sim, texto de 1982-09-23 | sem epígrafes | Lei n.º 59/2007 (2007-09-04) |
| Decreto-Lei n.º 36/2003 | Decreto-Lei n.º 110/2018 | Anexo — Código da Propriedade Industrial | 375 | 2026-09-30 | **não** | não | 57/357 | Lei n.º 16/2008 (2008-04-01); Decreto-Lei n.º 143/2008 (2008-07-25) |
| Decreto-Lei n.º 132/93 | Decreto-Lei n.º 315/98 | (2.ª numeração) | 258 | 1998-10-20 | **não** | não | 234/248 | — |
| Decreto Legislativo Regional n.º 21/2007/A | Decreto Legislativo Regional n.º 23/2023/A | Anexo — ESTATUTO DO PESSOAL DOCENTE DA EDUCAÇÃO PRÉ-ESCOLAR  | 225 | 2026-01-01 | **não** | não | 23/225 | Decreto Legislativo Regional n.º 20/2022/A (2022-08-24); Decreto Legislativo Regional n.º 9/2024/A (2024-10-11); Decreto Legislativo Regional n.º 21/2025/A (2025-10-08) |
| Lei n.º 15/2005 | Lei n.º 145/2015 | Anexo — (a que se refere o artigo 2.º) | 234 | 2024-04-01 | **não** | não | 24/206 | — |
| Decreto-Lei n.º 114/94 | Lei n.º 72/2013 | Anexo — CÓDIGO DA ESTRADA | 199 | 2025-04-11 | sim | sim, texto de 1994-05-03 | 31/171 | Decreto-Lei n.º 2/98 (1998-01-31); Decreto-Lei n.º 265-A/2001 (2002-01-02); Decreto-Lei n.º 44/2005 (2021-01-09) |
| Decreto-Lei n.º 442-A/88 | Lei n.º 82-E/2014 | Anexo — Código do Imposto sobre o Rendimento das Pessoas Sin | 196 | 2026-05-25 | sim | sim, texto de 1988-11-30 | 15/140 | Decreto-Lei n.º 198/2001 (2001-07-03) |
| Decreto-Lei n.º 282/77 | Lei n.º 117/2015 | Anexo I — ESTATUTO DA ORDEM DOS MÉDICOS | 177 | 2024-04-01 | sim | sim, consolidação de 1994-08-25 | sem epígrafes | Lei n.º 117/2015 (2015-08-31) |
| Decreto-Lei n.º 442-B/88 | Lei n.º 2/2014 | Anexo — CÓDIGO DO IMPOSTO SOBRE O RENDIMENTO DAS PESSOAS COL | 171 | 2026-01-01 | sim | sim, texto de 1988-11-30 | 9/115 | Decreto-Lei n.º 198/2001 (2003-01-01) |
| Decreto-Lei n.º 139-A/90 | Decreto-Lei n.º 41/2012 | Anexo — ESTATUTO DA CARREIRA DOS EDUCADORES DE INFÂNCIA E DO | 156 | 2023-12-30 | **não** | sim, texto de 1990-04-28 | 96/148 | Decreto-Lei n.º 1/98 (1998-01-02); Decreto-Lei n.º 15/2007 (2007-01-19); Decreto-Lei n.º 270/2009 (2009-09-30) |
| Lei n.º 3/99 | Lei n.º 105/2003 | LEI DE ORGANIZAÇÃO E FUNCIONAMENTO DOS TRIBUNAIS JUDICIAIS ( | 154 | 2003-12-10 | **não** | não | 133/149 | — |
| Lei n.º 13/91 | Lei n.º 130/99 | Anexo — ESTATUTO POLÍTICO-ADMINISTRATIVO DA REGIÃO AUTÓNOMA  | 154 | 2000-06-26 | **não** | sim, consolidação de 1991-06-05 | sem epígrafes | — |
| Decreto-Lei n.º 119/92 | Lei n.º 123/2015 | Anexo I — ESTATUTO DA ORDEM DOS ENGENHEIROS | 153 | 2024-04-01 | **não** | sim, texto de 1992-06-30 | 1/91 | — |
| Decreto Legislativo Regional n.º 22/2005/A | Decreto Legislativo Regional n.º 18/2007/A | Anexo — Estatuto do Aluno dos Ensinos Básico e Secundário | 147 | 2023-02-18 | **não** | não | 3/78 | — |
| Decreto-Lei n.º 452/99 | Lei n.º 139/2015 | Anexo I — ESTATUTO DA ORDEM DOS CONTABILISTAS CERTIFICADOS | 136 | 2024-03-01 | **não** | sim, consolidação de 2009-10-31 | 1/98 | Decreto-Lei n.º 310/2009 (2009-10-26); Lei n.º 139/2015 (2015-09-07) |
| Decreto-Lei n.º 110/91 | Lei n.º 124/2015 | Anexo II — Republicação da Lei n.º 110/91, de 29 de agosto ( | 129 | 2024-03-01 | sim | não | 0/14 | Lei n.º 110/91 (2003-09-06); Lei n.º 44/2003 (2003-08-22) |
| Decreto Regulamentar n.º 9/2018 | Decreto Regulamentar n.º 4/2022 | ANEXO — (a que se refere o artigo 6.º) | 128 | 2022-09-30 | **não** | sim, texto de 2018-09-11 | 105/112 | — |
| Decreto-Lei n.º 394-B/84 | Decreto-Lei n.º 102/2008 | Anexo IV — CÓDIGO DO IMPOSTO SOBRE O VALOR ACRESCENTADO | 123 | 2026-09-01 | **não** | sim, texto de 1984-12-26 | sem epígrafes | Decreto-Lei n.º 195/89 (1989-06-12) |
| Decreto-Lei n.º 288/2001 | Lei n.º 131/2015 | Anexo — ESTATUTO DA ORDEM DOS FARMACÊUTICOS | 128 | 2024-03-01 | sim | sim, consolidação de 2009-05-25 | 15/121 | Lei n.º 131/2015 (2015-09-04) |
| Decreto-Lei n.º 368/91 | Lei n.º 125/2015 | Anexo — ESTATUTO DA ORDEM DOS MÉDICOS VETERINÁRIOS | 126 | 2024-03-01 | sim | sim, consolidação de 1997-11-09 | 16/92 | — |
| Lei n.º 51/2010 | Lei n.º 126/2015 | Anexo — ESTATUTO DA ORDEM DOS NUTRICIONISTAS | 124 | 2024-03-01 | sim | sim, consolidação de 2010-12-14 | 5/90 | — |
| Decreto-Lei n.º 349/99 | Lei n.º 157/2015 | Anexo I — ESTATUTO DA ORDEM DOS ENGENHEIROS TÉCNICOS | 124 | 2024-03-01 | **não** | sim, consolidação de 2023-07-27 | 1/80 | Lei n.º 47/2011 (2011-06-27); Lei n.º 157/2015 (2015-09-17) |
| Lei n.º 51/96 | Lei n.º 119/2015 | articulado | 122 | 2026-07-29 | **não** | não | 6/94 | — |
| Lei n.º 32/2003 | Lei n.º 27/2007 | articulado | 122 | 2021-02-17 | **não** | sim, consolidação de 2007-08-04 | 5/92 | Lei n.º 8/2011 (2011-04-11) |
| Decreto Legislativo Regional n.º 28/2011/A | Decreto Legislativo Regional n.º 6/2026/A | ANEXO — (a que se refere o artigo 11.º) | 116 | 2026-03-03 | **não** | sim, consolidação de 2025-09-30 | 116/116 | Decreto Legislativo Regional n.º 14/2024/A (2024-12-24) |
| Decreto-Lei n.º 174/98 | Lei n.º 101/2015 | Anexo — ESTATUTO DA ORDEM DOS ECONOMISTAS | 108 | 2024-03-01 | sim | sim, consolidação de 1998-06-27 | 0/103 | Lei n.º 101/2015 (2015-08-20) |
| Decreto-Lei n.º 173/98 | Lei n.º 112/2015 | Anexo II — Republicação do Decreto-Lei n.º 173/98, de 26 de  | 113 | 2024-03-01 | **não** | sim, consolidação de 2007-06-12 | 8/81 | Decreto-Lei n.º 228/2007 (2007-06-11) |
| Decreto-Lei n.º 183/98 | Lei n.º 159/2015 | Anexo — ESTATUTO DA ORDEM DOS BIÓLOGOS | 112 | 2024-03-01 | sim | sim, consolidação de 1998-07-04 | 3/76 | Lei n.º 159/2015 (2015-09-18) |
| Lei n.º 38/2012 | Lei n.º 81/2021 | articulado | 102 | 2022-06-01 | **não** | não | 2/82 | Lei n.º 93/2015 (2015-08-13) |
| Decreto-Lei n.º 178/2006 | Decreto-Lei n.º 73/2011 | Anexo II — (a que se refere o artigo 19.º) | 101 | 2021-07-01 | **não** | não | 92/94 | — |
| Decreto-Lei n.º 167/97 | Decreto-Lei n.º 55/2002 | ANEXO | 83 | 2002-03-11 | **não** | não | 50/82 | Decreto-Lei n.º 305/99 (1999-08-06) |
| Decreto-Lei n.º 328/93 | Decreto-Lei n.º 240/96 | [(ver documento original)](https://files.diariodarepublica.p | 80 | 1996-12-14 | **não** | não | 72/78 | — |
| Decreto Legislativo Regional n.º 4/2000/M | Decreto Legislativo Regional n.º 21/2006/M | ANEXO | 63 | 2006-06-21 | **não** | sim, texto de 2000-01-31 | 14/63 | — |
| Lei n.º 77/88 | Lei n.º 28/2003 | Anexo — Lei de Organização e Funcionamento dos Serviços da A | 67 | 2025-04-08 | sim | sim, consolidação de 1994-08-04 | 12/54 | Lei n.º 59/93 (1993-08-17) |
| Decreto-Lei n.º 337/90 | Lei n.º 5/98 | Anexo — Lei Orgânica do Banco de Portugal | 67 | 2021-01-01 | **não** | não | sem epígrafes | — |
| Decreto-Lei n.º 312/2007 | Decreto-Lei n.º 74/2008 | (2.ª numeração) | 69 | 2008-04-22 | **não** | sim, texto de 2007-09-17 | 69/69 | — |
| Decreto n.º 11-A/2020 | Decreto n.º 2-A/2021 | ANEXO V — (a que se refere o artigo 6.º) | 65 | 2021-01-07 | **não** | sim, texto de 2020-12-21 | 63/64 | — |
| Decreto Legislativo Regional n.º 17/2003/M | Decreto Legislativo Regional n.º 2/2005/M | ANEXO | 64 | 2005-03-30 | **não** | não | 64/64 | — |
| Decreto Legislativo Regional n.º 29/2004/A | Decreto Legislativo Regional n.º 43/2008/A | Republicação do [Decreto Legislativo Regional n.º 29/2004/A] | 63 | 2008-10-08 | **não** | não | 62/62 | — |
| Decreto-Lei n.º 211/2004 | Decreto-Lei n.º 69/2011 | Anexo II — Republicação do Decreto-Lei n.º 211/2004, de 20 d | 60 | 2011-06-15 | **não** | não | 48/57 | — |
| Decreto Legislativo Regional n.º 32/2011/A | Decreto Legislativo Regional n.º 12/2013/A | Anexo — ESTATUTO DO ALUNO DOS ENSINOS BÁSICO E SECUNDÁRIO | 55 | 2018-01-01 | **não** | não | 6/55 | — |
| Decreto-Lei n.º 224/82 | Lei n.º 3/83 | articulado | 57 | 1983-02-26 | **não** | não | 45/47 | — |
| Decreto-Lei n.º 394/99 | Decreto-Lei n.º 8-D/2002 | [Decreto-Lei n.º 349/99](https://diariodarepublica.pt/dr/det | 40 | 2002-01-15 | **não** | não | 33/38 | — |
| Decreto Legislativo Regional n.º 15/2006/A | Decreto Legislativo Regional n.º 17/2015/A | Republicação do [Decreto Legislativo Regional n.º 15/2006/A] | 44 | 2015-06-22 | **não** | não | 40/44 | — |
| Decreto Legislativo Regional n.º 5/2003/A | Decreto Legislativo Regional n.º 16/2023/A | Republicação do [Decreto Legislativo Regional n.º 5/2003/A]( | 43 | 2023-05-11 | **não** | sim, consolidação de 2018-05-12 | 34/43 | Decreto Legislativo Regional n.º 13/2008/A (2008-06-06); Decreto Legislativo Regional n.º 37/2008/A (2008-08-05); Decreto Legislativo Regional n.º 12/2010/A (2010-03-30); Decreto Legislativo Regional n.º 20/2011/A (2011-06-21); Decreto Legislativo Regional n.º 34/2011/A (2011-12-06); Decreto Legislativo Regional n.º 13/2012/A (2012-03-28); Decreto Legislativo Regional n.º 5/2018/A (2018-05-11) |
| Decreto Legislativo Regional n.º 34/2008/A | Decreto Legislativo Regional n.º 15/2009/A | ANEXO — (republicação do Decreto Legislativo Regional n.º 34 | 41 | 2009-08-06 | **não** | sim, texto de 2008-07-28 | 5/30 | — |
| Decreto Legislativo Regional n.º 17/2014/M | Decreto Legislativo Regional n.º 10/2019/M | Anexo | 40 | 2019-08-13 | **não** | sim, consolidação de 2016-08-18 | 38/39 | — |
| Decreto Legislativo Regional n.º 32/2017/M | Decreto Legislativo Regional n.º 16/2022/M | ANEXO — (a que se refere o artigo 4.º) | 38 | 2022-07-29 | **não** | sim, consolidação de 2017-09-16 | 38/38 | — |
| Decreto-Lei n.º 404-A/98 | Lei n.º 44/99 | Decreto-Lei n.º 404-A/98, de 18 de Dezembro (ANEXO) | 36 | 1999-06-11 | **não** | não | 34/35 | — |
| Decreto-Lei n.º 109-E/2021 | Decreto-Lei n.º 70/2025 | [a que se refere a alínea b) do artigo 1.º] (ANEXO) | 35 | 2025-04-29 | **não** | sim, consolidação de 2021-12-09 | 35/35 | — |
| Decreto-Lei n.º 104/2008 | Decreto-Lei n.º 270/2009 | Anexo (2.ª numeração) | 34 | 2009-09-30 | **não** | não | 32/33 | — |
| Decreto Legislativo Regional n.º 9/99/A | Decreto Legislativo Regional n.º 10/2003/A | Anexo II — (republicação a que faz referência o artigo 3.º) | 33 | 2004-03-24 | **não** | sim, consolidação de 2004-03-23 | 33/33 | — |
| Decreto-Lei n.º 212/2006 | Decreto-Lei n.º 234/2008 | (2.ª numeração) | 32 | 2008-12-02 | **não** | não | 31/31 | — |
| Decreto Legislativo Regional n.º 2/2017/A | Decreto Legislativo Regional n.º 10/2021/A | Anexo — Regulamento de Concurso do Pessoal Docente da Educaç | 31 | 2021-04-19 | **não** | sim, texto de 2017-04-11 | 29/29 | — |
| Lei n.º 33/2003 | Lei n.º 2/2006 | Estatutos da Rádio e Televisão de Portugal, SGPS, S. A. (ANE | 31 | 2006-02-14 | **não** | não | 27/27 | — |
| Decreto-Lei n.º 54/95 | Decreto-Lei n.º 43/98 | Anexo — REGULAMENTO DA CONTRIBUIÇÃO ESPECIAL | 29 | 2013-01-01 | **não** | sim, consolidação de 2012-12-31 | sem epígrafes | — |
| Decreto-Lei n.º 166/2000 | Decreto-Lei n.º 307/2001 | [Decreto-Lei n.º 166/2000](https://diariodarepublica.pt/dr/d | 30 | 2001-12-06 | **não** | sim, texto de 2000-08-05 | 28/28 | — |
| Decreto-Lei n.º 201/2006 | Decreto-Lei n.º 92/2009 | ANEXO — (a que se refere o artigo 3.º) | 30 | 2009-04-16 | **não** | sim, texto de 2006-10-27 | 23/30 | Decreto-Lei n.º 240/2007 (2007-06-21); Decreto-Lei n.º 44/2008 (2008-03-11) |
| Decreto-Lei n.º 287/93 | Decreto-Lei n.º 106/2007 | ANEXO — (a que se refere o artigo 3.º) | 26 | 2007-04-03 | **não** | sim, consolidação de 1993-08-20 | 23/26 | — |
| Decreto Regulamentar n.º 32/2007 | Decreto Regulamentar n.º 5/2013 | ANEXO — (a que se refere o artigo 2.º) | 27 | 2013-08-29 | **não** | não | 24/27 | — |
| Decreto-Lei n.º 144/2007 | Decreto-Lei n.º 69/2011 | Anexo III — Republicação do Decreto-Lei n.º 144/2007, de 27  | 27 | 2011-06-15 | **não** | não | 27/27 | — |
| Decreto Regulamentar n.º 8/2003 | Decreto Regulamentar n.º 61/2007 | ANEXO — (a que se refere o artigo 3.º) | 24 | 2007-05-09 | **não** | não | 24/24 | — |
| Lei n.º 65/93 | Lei n.º 94/99 | Regula o acesso aos documentos da Administração (ANEXO) | 21 | 1999-07-16 | **não** | não | 18/21 | — |
| Decreto-Lei n.º 59/2003 | Decreto-Lei n.º 104/2012 | ANEXO | 23 | 2012-05-16 | **não** | sim, consolidação de 2003-04-01 | 19/23 | — |
| Decreto Legislativo Regional n.º 4/2003/M | Decreto Legislativo Regional n.º 23/2008/M | Anexo II — Republicação do Decreto Legislativo Regional n.º  | 22 | 2012-07-03 | **não** | sim, consolidação de 2008-06-30 | 21/22 | — |
| Decreto-Lei n.º 32/95 | Decreto-Lei n.º 42/2007 | ESTATUTOS DA EDIA - EMPRESA DE DESENVOLVIMENTO E INFRA-ESTRU | 20 | 2007-02-22 | **não** | não | 17/20 | — |
| Decreto-Lei n.º 92/2008 | Decreto-Lei n.º 231/2008 | ANEXO — (a que se refere o n.º 1 do artigo 8.º) | 20 | 2008-11-28 | **não** | sim, consolidação de 2008-06-03 | 20/20 | — |
| Decreto-Lei n.º 112/2011 | Decreto-Lei n.º 152/2012 | ANEXO — (a que se refere o artigo 5.º) | 19 | 2012-07-12 | **não** | não | 15/19 | — |
| Decreto-Lei n.º 396/99 | Decreto-Lei n.º 71/2003 | Segunda alteração ao Decreto-Lei n.º 289/91, de 10 de Agosto | 19 | 2003-04-10 | **não** | sim, texto de 1999-10-13 | 16/16 | — |
| Decreto-Lei n.º 184/98 | Decreto-Lei n.º 116-B/2006 | ANEXO — (republicação do [Decreto-Lei n.º 184/98](https://di | 18 | 2006-06-16 | **não** | não | 18/18 | — |
| Decreto-Lei n.º 118/92 | Decreto-Lei n.º 129/2005 | Republicação do [Decreto-Lei n.º 118/92](https://diariodarep | 17 | 2005-08-11 | **não** | não | 12/13 | Decreto-Lei n.º 205/2000 (2000-09-01) |
| Decreto-Lei n.º 142/2000 | Decreto-Lei n.º 122/2005 | Regime jurídico do pagamento dos prémios de seguro (ANEXO) | 16 | 2005-07-29 | **não** | não | 13/15 | — |
| Decreto-Lei n.º 10/2001 | Decreto-Lei n.º 339-D/2001 | Anexo III — Republicação do Decreto-Lei n.º 10/2001, de 23 d | 16 | 2001-12-28 | **não** | não | 13/16 | — |
| Decreto-Lei n.º 78/97 | Decreto-Lei n.º 76/2006 | ANEXO II — (a que se refere o n.º 2 do artigo 13.º) | 15 | 2006-03-27 | **não** | não | 14/15 | — |
| Decreto-Lei n.º 195/2006 | Decreto-Lei n.º 48-A/2010 | Anexo II — (a que se refere o artigo 8.º) Decreto-Lei n.º 19 | 15 | 2010-05-13 | **não** | não | 15/15 | — |
| Decreto Legislativo Regional n.º 14/2024/A | Decreto Legislativo Regional n.º 6/2026/A | ANEXO — (a que se refere o artigo 4.º) | 13 | 2026-03-03 | **não** | sim, consolidação de 2024-12-24 | 12/12 | — |
| Decreto-Lei n.º 387/90 | Decreto-Lei n.º 314/97 | ANEXO | 12 | 1997-11-15 | **não** | sim, texto de 1990-12-10 | 8/10 | — |

## 2-B. Cópias com texto de outra data, em registos em vigor (703; as 60 maiores)

| Texto | Cópia em | Parte | Artigos | Texto da cópia até | Texto atual em | Texto atual até |
|---|---|---|--:|---|---|---|
| Anexo I — Republicação do Código das Sociedades Comerciais | Decreto-Lei n.º 76-A/2006 | Anexo I — Republicação do Código das Sociedades Co | 598 | 2006-03-29 | Decreto-Lei n.º 262/86 | 2026-09-01 |
| Anexo IV — Republicação do Código dos Valores Mobiliários, a | Lei n.º 35/2018 | Anexo IV — Republicação do Código dos Valores Mobi | 588 | 2018-07-20 | Decreto-Lei n.º 486/99 | 2026-09-01 |
| Anexo III — Republicação do Código dos Contratos Públicos | Decreto-Lei n.º 177/2026 | ANEXO II — (a que se refere o artigo 9.º) | 570 | 2026-09-04 | Decreto-Lei n.º 18/2008 | 2026-10-01 |
| Anexo I — Republicação do Regime Geral das Instituições de C | Lei n.º 23-A/2022 | Anexo — Republicação do Regime Geral das Instituiç | 545 | 2022-12-09 | Decreto-Lei n.º 298/92 | 2025-12-28 |
| CÓDIGO DE PROCESSO PENAL (ANEXO) | Lei n.º 48/2007 | CÓDIGO DE PROCESSO PENAL (ANEXO) | 535 | 2007-08-29 | Decreto-Lei n.º 78/87 | 2026-09-01 |
| CÓDIGO DE PROCESSO PENAL (ANEXO) | Lei n.º 59/98 | CÓDIGO DE PROCESSO PENAL (ANEXO) | 532 | 1998-08-25 | Decreto-Lei n.º 78/87 | 2026-09-01 |
| Anexo III — Republicação do Código dos Contratos Públicos | Decreto-Lei n.º 111-B/2017 | Anexo III — Republicação do Código dos Contratos P | 531 | 2018-01-01 | Decreto-Lei n.º 18/2008 | 2026-10-01 |
| Anexo IV — Republicação do Código dos Valores Mobiliários, a | Decreto-Lei n.º 357-A/2007 | ANEXO I — (a que se refere o artigo 20.º) | 504 | 2007-10-31 | Decreto-Lei n.º 486/99 | 2026-09-01 |
| Anexo I — Republicação do Regime Geral das Instituições de C | Lei n.º 35/2018 | Anexo V — Republicação do Regime Geral das Institu | 476 | 2018-07-20 | Decreto-Lei n.º 298/92 | 2025-12-28 |
| Anexo III — Republicação do Código dos Contratos Públicos | Decreto-Lei n.º 278/2009 | CÓDIGO DOS CONTRATOS PÚBLICOS (ANEXO) | 474 | 2009-10-02 | Decreto-Lei n.º 18/2008 | 2026-10-01 |
| Anexo I — Republicação do Regime Geral das Instituições de C | Lei n.º 23-A/2015 | Anexo I — Republicação do Regime Geral das Institu | 462 | 2015-03-26 | Decreto-Lei n.º 298/92 | 2025-12-28 |
| Anexo I — Republicação do Regime Geral das Instituições de C | Decreto-Lei n.º 157/2014 | ANEXO — (a que se refere o artigo 25.º) | 406 | 2014-10-24 | Decreto-Lei n.º 298/92 | 2025-12-28 |
| Anexo — CÓDIGO PENAL | Lei n.º 59/2007 | Anexo — CÓDIGO PENAL | 403 | 2007-09-04 | Decreto-Lei n.º 48/95 | 2026-09-01 |
| CÓDIGO DA PROPRIEDADE INDUSTRIAL (ANEXO II) | Decreto-Lei n.º 143/2008 | CÓDIGO DA PROPRIEDADE INDUSTRIAL (ANEXO) | 399 | 2008-07-25 | Decreto-Lei n.º 110/2018 | 2026-09-30 |
| Bases da concessão da rede nacional de transporte de eletric | Decreto-Lei n.º 99/2024 | Anexo — Republicação do Decreto-Lei n.º 15/2022, d | 365 | 2024-12-03 | Decreto-Lei n.º 15/2022 | 2026-08-28 |
| Republicação do Código do Registo Civil (ANEXO) | Decreto-Lei n.º 324/2007 | Republicação do Código do Registo Civil (ANEXO) | 344 | 2007-09-28 | Decreto-Lei n.º 131/95 | 2025-04-02 |
| Anexo — CÓDIGO DE PROCEDIMENTO E DE PROCESSO TRIBUTÁRIO | Lei n.º 118/2019 | Anexo II — (a que se refere o n.º 1 do artigo 12.º | 315 | 2019-09-17 | Decreto-Lei n.º 433/99 | 2025-07-01 |
| Anexo II — Republicação do Regime Geral dos Organismos de In | Decreto-Lei n.º 56/2018 | Anexo II — Republicação do Regime Geral dos Organi | 314 | 2018-07-09 | Lei n.º 16/2015 | 2023-05-29 |
| Anexo — ESTATUTO DOS MILITARES DAS FORÇAS ARMADAS | Decreto-Lei n.º 197-A/2003 | ANEXO — (republicação) | 313 | 2003-08-30 | Decreto-Lei n.º 236/99 | 2007-09-16 |
| Anexo — CÓDIGO DA INSOLVÊNCIA E DA RECUPERAÇÃO DE EMPRESAS | Decreto-Lei n.º 200/2004 | CÓDIGO DA INSOLVÊNCIA E DA RECUPERAÇÃO DE EMPRESAS | 304 | 2004-08-18 | Decreto-Lei n.º 53/2004 | 2024-11-10 |
| Anexo — CÓDIGO DE PROCEDIMENTO E DE PROCESSO TRIBUTÁRIO | Lei n.º 15/2001 | Anexo — CÓDIGO DE PROCEDIMENTO E DE PROCESSO TRIBU | 298 | 2001-06-05 | Decreto-Lei n.º 433/99 | 2025-07-01 |
| Anexo — ESTATUTO DOS MILITARES DAS FORÇAS ARMADAS | Decreto-Lei n.º 77/2023 | ANEXO VI — (a que se refere o artigo 10.º) | 289 | 2023-09-04 | Decreto-Lei n.º 90/2015 | 2023-09-05 |
| CÓDIGO DA PROPRIEDADE INDUSTRIAL (ANEXO II) | Lei n.º 16/2008 | CÓDIGO DA PROPRIEDADE INDUSTRIAL (ANEXO II) | 285 | 2008-04-01 | Decreto-Lei n.º 110/2018 | 2026-09-30 |
| Republicação do Decreto-Lei n.º 94-B/98, de 17 de Abril (ANE | Decreto-Lei n.º 251/2003 | Decreto-Lei n.º 94-B/98, de 17 de Abril (ANEXO) | 285 | 2003-10-14 | Decreto-Lei n.º 94-B/98 | 2016-01-01 |
| Republicação do Decreto-Lei n.º 94-B/98, de 17 de Abril (ANE | Decreto-Lei n.º 8-A/2002 | (2.ª numeração) | 273 | 2002-01-11 | Decreto-Lei n.º 94-B/98 | 2016-01-01 |
| Anexo — Republicação da Lei n.º 23/2007, de 4 de julho | Lei n.º 18/2022 | Anexo — Republicação da Lei n.º 23/2007, de 4 de j | 271 | 2022-08-25 | Lei n.º 23/2007 | 2026-09-11 |
| Anexo — Republicação da Lei n.º 23/2007, de 4 de julho | Lei n.º 102/2017 | ANEXO — (a que se refere o artigo 6.º) | 264 | 2017-08-28 | Lei n.º 23/2007 | 2026-09-11 |
| Anexo — ESTATUTO DO PESSOAL DOCENTE DA EDUCAÇÃO PRÉ-ESCOLAR  | Decreto Legislativo Regional n.º 20/2022/A | ANEXO — (a que se refere o artigo 3.º) | 255 | 2022-08-24 | Decreto Legislativo Regional n.º 23/2023/A | 2026-01-01 |
| Anexo — CÓDIGO DE PROCESSO DO TRABALHO Disposições fundament | Lei n.º 107/2019 | ANEXO — (a que se refere o artigo 8.º) | 249 | 2019-09-09 | Decreto-Lei n.º 480/99 | 2024-11-10 |
| Anexo I — Republicação do Regime Geral das Instituições de C | Decreto-Lei n.º 201/2002 | Regime Geral das Instituições de Crédito e Socieda | 248 | 2002-09-26 | Decreto-Lei n.º 298/92 | 2025-12-28 |
| ANEXO III — (a que se refere o artigo 9.º) | Lei n.º 67/2019 | ANEXO III — (a que se refere o artigo 9.º) | 248 | 2019-08-27 | Lei n.º 21/85 | 2025-07-25 |
| Republicação do [Decreto Legislativo Regional n.º 29/2011/A] | Decreto Legislativo Regional n.º 19/2016/A | Republicação do [Decreto Legislativo Regional n.º  | 246 | 2016-10-06 | Decreto Legislativo Regional n.º 29/2011/A | 2016-10-07 |
| CÓDIGO DO DIREITO DE AUTOR E DOS DIREITOS CONEXOS (ANEXO I) | Lei n.º 16/2008 | CÓDIGO DO DIREITO DE AUTOR E DOS DIREITOS CONEXOS  | 242 | 2008-04-01 | Decreto-Lei n.º 63/85 | 2024-01-01 |
| Anexo — Republicação da Lei n.º 23/2007, de 4 de julho | Lei n.º 29/2012 | ANEXO — (a que se refere o artigo 8.º) | 239 | 2012-08-09 | Lei n.º 23/2007 | 2026-09-11 |
| Anexo — CÓDIGO DE PROCESSO DO TRABALHO Disposições fundament | Decreto-Lei n.º 295/2009 | Código de Processo do Trabalho (ANEXO) | 235 | 2009-10-13 | Decreto-Lei n.º 480/99 | 2024-11-10 |
| Anexo II — Republicação do Decreto-Lei n.º 176/2006, de 30 d | Decreto-Lei n.º 128/2013 | ANEXO II — (a que se refere o artigo 12.º) | 229 | 2013-09-05 | Decreto-Lei n.º 176/2006 | 2026-07-01 |
| Anexo II — Republicação do Decreto-Lei n.º 176/2006, de 30 d | Decreto-Lei n.º 20/2013 | Anexo II — Republicação do Decreto-Lei n.º 176/200 | 226 | 2013-02-14 | Decreto-Lei n.º 176/2006 | 2026-07-01 |
| Anexo — ESTATUTO DO PESSOAL DOCENTE DA EDUCAÇÃO PRÉ-ESCOLAR  | Decreto Legislativo Regional n.º 9/2024/A | ANEXO — (a que se refere o artigo 1.º) | 225 | 2024-10-11 | Decreto Legislativo Regional n.º 23/2023/A | 2026-01-01 |
| Anexo — ESTATUTO DO PESSOAL DOCENTE DA EDUCAÇÃO PRÉ-ESCOLAR  | Decreto Legislativo Regional n.º 21/2025/A | ANEXO — (a que se refere o artigo 1.º) | 225 | 2025-10-08 | Decreto Legislativo Regional n.º 23/2023/A | 2026-01-01 |
| Republicação do Decreto-Lei n.º 94-B/98, de 17 de Abril (ANE | Decreto-Lei n.º 2/2009 | Republicação do Decreto-Lei n.º 94-B/98, de 17 de  | 223 | 2009-01-05 | Decreto-Lei n.º 94-B/98 | 2016-01-01 |
| ANEXO — (a que se refere o artigo 5.º) | Decreto-Lei n.º 81/2022 | ANEXO — (a que se refere o artigo 5.º) | 215 | 2022-12-06 | Decreto-Lei n.º 108/2018 | 2025-01-01 |
| Anexo — (republicação do Decreto-Lei n.º 224/84, de 6 de Jul | Decreto-Lei n.º 125/2013 | ANEXO — (a que se refere o artigo 9.º) | 214 | 2013-08-30 | Decreto-Lei n.º 224/84 | 2026-04-16 |
| CÓDIGO DO DIREITO DE AUTOR E DOS DIREITOS CONEXOS (ANEXO I) | Lei n.º 45/85 | Anexo — CÓDIGO DO DIREITO DE AUTOR E DOS DIREITOS  | 212 | 1985-09-17 | Decreto-Lei n.º 63/85 | 2024-01-01 |
| Republicação do Decreto Legislativo Regional n.º 29/2010/A,  | Decreto Legislativo Regional n.º 31/2012/A | Republicação do Decreto Legislativo Regional n.º 2 | 210 | 2012-07-06 | Decreto Legislativo Regional n.º 29/2010/A | 2026-01-01 |
| Republicação do Código de Processo nos Tribunais Administrat | Decreto-Lei n.º 214-G/2015 | Republicação do Código de Processo nos Tribunais A | 210 | 2015-10-02 | Lei n.º 15/2002 | 2024-11-10 |
| Republicação do Código de Processo nos Tribunais Administrat | Lei n.º 118/2019 | Anexo III — (a que se refere o n.º 2 do artigo 12. | 208 | 2019-09-17 | Lei n.º 15/2002 | 2024-11-10 |
| Anexo — (republicação do Decreto-Lei n.º 224/84, de 6 de Jul | Decreto-Lei n.º 116/2008 | Anexo — (republicação do Decreto-Lei n.º 224/84, d | 204 | 2008-07-04 | Decreto-Lei n.º 224/84 | 2026-04-16 |
| ANEXO — (a que se refere o artigo 16.º) | Lei n.º 32/2026 | ANEXO — (a que se refere o artigo 16.º) | 204 | 2026-07-20 | Lei n.º 62/2007 | 2026-08-01 |
| Anexo II — Republicação da Lei n.º 83/2017, de 18 de agosto | Lei n.º 58/2020 | Anexo II — Republicação da Lei n.º 83/2017, de 18  | 196 | 2020-08-31 | Lei n.º 83/2017 | 2026-07-01 |
| Republicação do Código de Processo nos Tribunais Administrat | Lei n.º 4-A/2003 | CÓDIGO DE PROCESSO NOS TRIBUNAIS ADMINISTRATIVOS ( | 192 | 2003-02-19 | Lei n.º 15/2002 | 2024-11-10 |
| ANEXO — (a que se refere o artigo 11.º) | Lei n.º 40-A/2016 | ANEXO — (a que se refere o artigo 11.º) | 190 | 2016-12-22 | Lei n.º 62/2013 | 2026-09-01 |
| CÓDIGO DA ESTRADA (ANEXO) | Decreto-Lei n.º 44/2005 | articulado | 189 | 2021-01-09 | Lei n.º 72/2013 | 2025-04-11 |
| CÓDIGO DA ESTRADA (ANEXO) | Decreto-Lei n.º 2/98 | CÓDIGO DA ESTRADA (ANEXO) | 177 | 1998-01-31 | Lei n.º 72/2013 | 2025-04-11 |
| CÓDIGO DA ESTRADA (ANEXO) | Decreto-Lei n.º 265-A/2001 | (2.ª numeração) | 177 | 2002-01-02 | Lei n.º 72/2013 | 2025-04-11 |
| Lei Eleitoral para a Assembleia Legislativa da Região Autóno | Lei Orgânica n.º 1-A/2025 | ANEXO — (a que se refere o artigo 5.º) | 175 | 2025-01-27 | Lei Orgânica n.º 1/2006 | 2025-01-28 |
| Republicação do [Decreto-Lei n.º 267/80](https://diariodarep | Lei Orgânica n.º 3/2026 | ANEXO — (a que se refere o artigo 4.º) | 173 | 2026-09-10 | Decreto-Lei n.º 267/80 | 2026-09-11 |
| Republicação do [Decreto-Lei n.º 380/99](https://diariodarep | Decreto-Lei n.º 316/2007 | Republicação do Decreto-Lei n.º 380/99, de 22 de S | 173 | 2007-11-06 | Decreto-Lei n.º 380/99 | 2015-07-13 |
| Republicação do [Decreto-Lei n.º 380/99](https://diariodarep | Decreto-Lei n.º 46/2009 | Republicação do [Decreto-Lei n.º 380/99](https://d | 173 | 2009-02-20 | Decreto-Lei n.º 380/99 | 2015-07-13 |
| Lei Eleitoral para a Assembleia Legislativa da Região Autóno | Lei Orgânica n.º 1/2009 | Lei Eleitoral para a Assembleia Legislativa da Reg | 171 | 2009-01-19 | Lei Orgânica n.º 1/2006 | 2025-01-28 |
| ANEXO — ([Decreto-Lei n.º 202/2004](https://diariodarepublic | Decreto-Lei n.º 201/2005 | ANEXO — ([Decreto-Lei n.º 202/2004](https://diario | 171 | 2005-11-24 | Decreto-Lei n.º 202/2004 | 2024-10-16 |

## 2-C. Cópias, em registos em vigor, de textos cujo registo mais recente já não vigora (63)

| Texto | Cópia em | Parte | Artigos | Texto da cópia até | Registo mais recente | Estado desse registo |
|---|---|---|--:|---|---|---|
| Anexo II — Republicação do Regime Geral dos Organismos de In | Decreto-Lei n.º 56/2018 | Anexo II — Republicação do Regime Geral dos Organi | 314 | 2018-07-09 | Lei n.º 16/2015 | repealed |
| Republicação do [Decreto-Lei n.º 380/99](https://diariodarep | Decreto-Lei n.º 316/2007 | Republicação do Decreto-Lei n.º 380/99, de 22 de S | 173 | 2007-11-06 | Decreto-Lei n.º 380/99 | repealed |
| Republicação do [Decreto-Lei n.º 380/99](https://diariodarep | Decreto-Lei n.º 46/2009 | Republicação do [Decreto-Lei n.º 380/99](https://d | 173 | 2009-02-20 | Decreto-Lei n.º 380/99 | repealed |
| Republicação do [Decreto-Lei n.º 380/99](https://diariodarep | Decreto-Lei n.º 310/2003 | (2.ª numeração) | 160 | 2003-12-10 | Decreto-Lei n.º 380/99 | repealed |
| Republicação do regime jurídico da criação, autonomia e gest | Decreto Legislativo Regional n.º 35/2006/A | Regime jurídico da criação, autonomia e gestão das | 145 | 2006-09-06 | Decreto Legislativo Regional n.º 12/2005/A | repealed |
| Republicação do regime jurídico da criação, autonomia e gest | Decreto Legislativo Regional n.º 17/2010/A | Regime jurídico da criação, autonomia e gestão das | 145 | 2010-04-13 | Decreto Legislativo Regional n.º 12/2005/A | repealed |
| Republicação do regime jurídico da criação, autonomia e gest | Decreto Legislativo Regional n.º 13/2013/A | Republicação do regime jurídico da criação, autono | 145 | 2013-08-30 | Decreto Legislativo Regional n.º 12/2005/A | repealed |
| Anexo III — Republicação do Decreto-Lei n.º 12/2006, de 20 d | Lei n.º 147/2015 | Anexo III — Republicação do Decreto-Lei n.º 12/200 | 125 | 2015-09-09 | Decreto-Lei n.º 12/2006 | repealed |
| Anexo I — Regime jurídico que regula o acesso à actividade d | Decreto-Lei n.º 242/2012 | Anexo — REGIME JURÍDICO DOS SERVIÇOS DE PAGAMENTO  | 122 | 2012-11-07 | Decreto-Lei n.º 317/2009 | repealed |
| Republicação do Decreto-Lei n.º 29/2006, de 15 de Fevereiro  | Decreto-Lei n.º 215-A/2012 | ANEXO — (a que se refere o artigo 6.º) | 110 | 2012-10-08 | Decreto-Lei n.º 29/2006 | repealed |
| Republicação do Decreto-Lei n.º 30/2006, de 15 de Fevereiro  | Decreto-Lei n.º 230/2012 | ANEXO — (a que se refere o artigo 6.º) | 107 | 2012-10-26 | Decreto-Lei n.º 30/2006 | repealed |
| ANEXO — (a que se refere o artigo 13.º) | Decreto-Lei n.º 231/2012 | ANEXO — (a que se refere o artigo 13.º) | 106 | 2012-10-26 | Decreto-Lei n.º 140/2006 | repealed |
| Anexo — Regime jurídico dos organismos de investimento colec | Decreto-Lei n.º 71/2010 | ANEXO I — (a que se refere o n.º 1 do artigo 11.º) | 102 | 2010-06-18 | Decreto-Lei n.º 252/2003 | repealed |
| Republicação da lei de enquadramento do Orçamento do Estado  | Lei Orgânica n.º 2/2002 | Republicação da lei de enquadramento do Orçamento  | 94 | 2002-08-28 | Lei n.º 41/2014 | not_in_force |
| Republicação do Decreto-Lei n.º 29/2006, de 15 de Fevereiro  | Decreto-Lei n.º 78/2011 | Republicação do Decreto-Lei n.º 29/2006, de 15 de  | 92 | 2011-06-20 | Decreto-Lei n.º 29/2006 | repealed |
| ANEXO — (a que se refere o artigo 7.º) | Decreto Regulamentar n.º 16/2015 | ANEXO — (a que se refere o artigo 7.º) | 90 | 2015-09-16 | Decreto Regulamentar n.º 43/87 | repealed |
| Republicação do Decreto-Lei n.º 30/2006, de 15 de Fevereiro  | Decreto-Lei n.º 77/2011 | Republicação do Decreto-Lei n.º 30/2006, de 15 de  | 89 | 2011-06-20 | Decreto-Lei n.º 30/2006 | repealed |
| ANEXO III — (a que se refere o artigo 9.º) | Decreto-Lei n.º 240/2012 | ANEXO III — (a que se refere o artigo 9.º) | 85 | 2012-11-06 | Decreto-Lei n.º 252/2000 | repealed |
| Aprova o regime de licenciamento de obras particulares | Decreto-Lei n.º 250/94 | articulado | 83 | 1994-10-15 | Decreto-Lei n.º 445/91 | repealed |
| Regime jurídico dos fundos de investimento imobiliário (ANEX | Decreto-Lei n.º 71/2010 | ANEXO II — (a que se refere o n.º 2 do artigo 11.º | 77 | 2010-06-18 | Decreto-Lei n.º 60/2002 | repealed |
| ANEXO II — (a que se refere o artigo 7.º) | Decreto-Lei n.º 83-A/2014 | ANEXO II — (a que se refere o artigo 7.º) | 65 | 2014-05-23 | Decreto-Lei n.º 132/2012 | repealed |
| Regime jurídico dos fundos de investimento imobiliário (ANEX | Decreto-Lei n.º 13/2005 | Regime jurídico dos fundos de investimento imobili | 61 | 2005-01-07 | Decreto-Lei n.º 60/2002 | repealed |
| Anexo I — Republicação do Decreto-Lei n.º 12/2004, de 9 de J | Decreto-Lei n.º 69/2011 | Anexo I — Republicação do Decreto-Lei n.º 12/2004, | 61 | 2011-06-15 | Decreto-Lei n.º 12/2004 | repealed |
| ANEXO | Decreto-Lei n.º 57/2002 | Anexo | 58 | 2002-03-11 | Decreto-Lei n.º 168/97 | repealed |
| ANEXO | Decreto-Lei n.º 139/99 | ANEXO | 57 | 1999-04-24 | Decreto-Lei n.º 168/97 | repealed |
| ANEXO — (a que se refere o artigo 5.º) | Decreto Legislativo Regional n.º 7/2014/M | ANEXO — (a que se refere o artigo 5.º) | 57 | 2014-07-25 | Decreto Legislativo Regional n.º 25/2013/M | repealed |
| Anexo II — (a que se refere o artigo 28.º) | Lei n.º 52/2018 | Anexo II — (a que se refere o artigo 28.º) | 56 | 2018-08-20 | Decreto-Lei n.º 118/2013 | repealed |
| Anexo II — (a que se refere o artigo 28.º) | Decreto-Lei n.º 194/2015 | Anexo — (a que se refere o artigo 7.º) | 55 | 2015-11-26 | Decreto-Lei n.º 118/2013 | repealed |
| Anexo II — (a que se refere o artigo 28.º) | Decreto-Lei n.º 251/2015 | ANEXO — (a que se refere o artigo 4.º) | 55 | 2015-11-25 | Decreto-Lei n.º 118/2013 | repealed |
| Anexo II — (a que se refere o artigo 28.º) | Decreto-Lei n.º 28/2016 | ANEXO — (a que se refere o artigo 4.º) | 55 | 2016-06-23 | Decreto-Lei n.º 118/2013 | repealed |
| ANEXO — (republicação) | Decreto-Lei n.º 54/2007 | ANEXO — (republicação) | 54 | 2007-03-12 | Decreto-Lei n.º 135/2004 | repealed |
| ANEXO II — (a que se refere o artigo 7.º) | Decreto-Lei n.º 199/2012 | ANEXO II — (a que se refere o artigo 7.º) | 48 | 2012-08-24 | Decreto-Lei n.º 61/2011 | repealed |
| ANEXO — (a que se refere o artigo 9.º) | Lei n.º 72/2014 | ANEXO — (a que se refere o artigo 9.º) | 48 | 2014-09-02 | Lei n.º 68/93 | repealed |
| [Decreto-Lei n.º 251/98](https://diariodarepublica.pt/dr/det | Lei n.º 106/2001 | [Decreto-Lei n.º 251/98](https://diariodarepublica | 46 | 2001-08-31 | Decreto-Lei n.º 251/98 | repealed |
| [Decreto-Lei n.º 251/98](https://diariodarepublica.pt/dr/det | Decreto-Lei n.º 41/2003 | [Decreto-Lei n.º 251/98](https://diariodarepublica | 46 | 2003-03-11 | Decreto-Lei n.º 251/98 | repealed |
| ANEXO | Decreto-Lei n.º 383/98 | ANEXO | 45 | 1998-11-27 | Decreto-Lei n.º 278/87 | repealed |
| ANEXO — (a que se refere o artigo 6.º) | Decreto-Lei n.º 73/2017 | ANEXO — (a que se refere o artigo 6.º) | 45 | 2017-06-21 | Decreto-Lei n.º 298/2007 | repealed |
| ANEXO I — (a que se refere o n.º 1 do artigo 7.º) | Decreto-Lei n.º 253/2012 | ANEXO — (a que se refere o artigo 5.º) | 44 | 2012-11-27 | Decreto-Lei n.º 28/2008 | repealed |
| ANEXO I — (a que se refere o n.º 1 do artigo 7.º) | Decreto-Lei n.º 137/2013 | ANEXO I — (a que se refere o n.º 1 do artigo 7.º) | 44 | 2013-10-07 | Decreto-Lei n.º 28/2008 | repealed |
| [a que se refere a alínea f) do artigo 40.º] (ANEXO VII) | Decreto-Lei n.º 114/2011 | [a que se refere a alínea f) do artigo 40.º] (ANEX | 41 | 2011-11-30 | Decreto-Lei n.º 35/2004 | repealed |
| Republicação do Decreto-Lei n.º 233/2004, de 14 de Dezembro  | Decreto-Lei n.º 233/2004 | articulado | 39 | 2004-12-14 | Decreto-Lei n.º 154/2009 | not_in_force |
| Republicação do Decreto-Lei n.º 233/2004, de 14 de Dezembro  | Decreto-Lei n.º 243-A/2004 | Republicação (ANEXO) | 39 | 2004-12-31 | Decreto-Lei n.º 154/2009 | not_in_force |
| ANEXO — (a que se refere o artigo 4.º) | Decreto Legislativo Regional n.º 16/2020/A | ANEXO — (a que se refere o artigo 4.º) | 38 | 2020-07-06 | Decreto Legislativo Regional n.º 7/2017/A | repealed |
| ANEXO — (a que se refere o artigo 4.º) | Decreto Legislativo Regional n.º 4/2021/A | ANEXO — (a que se refere o artigo 3.º) | 38 | 2021-03-03 | Decreto Legislativo Regional n.º 7/2017/A | repealed |
| ANEXO — (a que se refere o artigo 7.º) | Decreto Regulamentar n.º 3/89 | articulado | 35 | 1989-01-28 | Decreto Regulamentar n.º 43/87 | repealed |
| Aprova o regime dos contratos de trabalho dos profissionais  | Lei n.º 28/2011 | (2.ª numeração) | 32 | 2011-06-16 | Lei n.º 4/2008 | repealed |
| Anexo II — Republicação do Regime Geral dos Organismos de In | Decreto-Lei n.º 144/2019 | ANEXO I | 31 | 2019-09-23 | Lei n.º 16/2015 | repealed |
| Anexo II — Republicação do Decreto-Lei n.º 345/98, de 9 de n | Lei n.º 23-A/2015 | Anexo II — Republicação do Decreto-Lei n.º 345/98, | 29 | 2015-03-26 | Decreto-Lei n.º 345/98 | repealed |
| Anexo — (a que se refere o artigo 11.º) | Decreto-Lei n.º 26/2015 | Anexo — (a que se refere o artigo 11.º) | 27 | 2015-02-06 | Decreto-Lei n.º 178/2012 | repealed |
| Republicação do [Decreto Legislativo Regional n.º 12/2014/A] | Decreto Legislativo Regional n.º 9/2016/A | Republicação do [Decreto Legislativo Regional n.º  | 27 | 2016-05-18 | Decreto Legislativo Regional n.º 12/2014/A | repealed |
| Decreto-Lei n.º 423/91, de 30 de Outubro (ANEXO) | Lei n.º 31/2006 | Decreto-Lei n.º 423/91, de 30 de Outubro (ANEXO) | 23 | 2006-07-21 | Decreto-Lei n.º 423/91 | repealed |
| ANEXO — (a que se refere o artigo 6.º) | Lei n.º 13/2017 | ANEXO — (a que se refere o artigo 6.º) | 20 | 2017-05-02 | Lei n.º 50/2007 | repealed |
| Anexo — Decreto-Lei n.º 314/78, de 27 de Outubro - Organizaç | Lei n.º 31/2003 | Anexo — Decreto-Lei n.º 314/78, de 27 de Outubro - | 19 | 2003-08-22 | Decreto-Lei n.º 314/78 | repealed |
| Estatuto das denominações de origem e indicação geográfica d | Decreto-Lei n.º 97/2020 | Estatuto das denominações de origem e indicação ge | 19 | 2020-11-16 | Decreto-Lei n.º 173/2009 | repealed |
| Anexo III — (a que se refere o artigo 8.º) Decreto-Lei n.º 6 | Decreto-Lei n.º 48-A/2010 | Anexo III — (a que se refere o artigo 8.º) Decreto | 17 | 2010-05-13 | Decreto-Lei n.º 65/2007 | repealed |
| ANEXO — (a que se refere o artigo 4.º) | Decreto-Lei n.º 74/2015 | ANEXO — (a que se refere o artigo 4.º) | 16 | 2015-05-11 | Decreto-Lei n.º 187/2002 | repealed |
| Anexo — (a que se refere o artigo 3.º) | Decreto-Lei n.º 391/2007 | Anexo — (a que se refere o artigo 3.º) | 16 | 2007-12-13 | Decreto-Lei n.º 460/77 | repealed |
| Republicação do [Decreto-Lei n.º 251/2002](https://diariodar | Decreto-Lei n.º 27/2005 | Republicação do [Decreto-Lei n.º 251/2002](https:/ | 16 | 2005-02-04 | Decreto-Lei n.º 251/2002 | repealed |
| ANEXO — (a que se refere o artigo 4.º) | Decreto Legislativo Regional n.º 12/2017/M | ANEXO — (a que se refere o artigo 4.º) | 15 | 2017-05-22 | Decreto Legislativo Regional n.º 23/2000/M | repealed |
| Republicação do [Decreto Legislativo Regional n.º 10/2014/A] | Decreto Legislativo Regional n.º 13/2015/A | Republicação do [Decreto Legislativo Regional n.º  | 14 | 2015-04-27 | Decreto Legislativo Regional n.º 10/2014/A | repealed |
| ANEXO | Decreto Legislativo Regional n.º 8/2017/A | ANEXO | 13 | 2017-10-10 | Decreto Legislativo Regional n.º 11/2008/A | repealed |
| Estabelece a Lei Orgânica dos Tribunais Judiciais | Lei n.º 79/79 | articulado | 12 | 1979-12-28 | Decreto-Lei n.º 269/78 | repealed |
| Anexo II — Republicação da Lei n.º 77/2019, de 2 de setembro | Decreto-Lei n.º 78/2021 | Anexo II — Republicação da Lei n.º 77/2019, de 2 d | 11 | 2021-09-24 | Lei n.º 77/2019 | repealed |

## 3. Vigência desconhecida (prioritários, 1.ª Série)

| Classe | lei | lei-organica | lei-constitucional | decreto-lei | decreto-regulamentar | decreto-legislativo-regional | Total |
|---|--:|--:|--:|--:|--:|--:|--:|
| revogado_segundo_a_relacao_do_dre | 4 | 1 | 0 | 14 | 1 | 0 | 20 |
| temporario_ou_orcamental | 17 | 2 | 0 | 15 | 2 | 34 | 70 |
| ato_de_alteracao | 217 | 20 | 0 | 503 | 21 | 165 | 926 |
| alterado_depois_e_sem_revogacao | 35 | 1 | 0 | 73 | 8 | 9 | 126 |
| sem_indicio_de_revogacao | 479 | 7 | 0 | 567 | 33 | 221 | 1307 |
| **Total** | 752 | 31 | 0 | 1172 | 65 | 429 | 2449 |

Leis e decretos-leis de vigência desconhecida por ano de publicação (desde 2010):

| Ano | Desconhecida | Publicados | % |
|---|--:|--:|--:|
| 2014 | 93 | 291 | 32 |
| 2015 | 286 | 436 | 66 |
| 2016 | 96 | 144 | 67 |
| 2017 | 194 | 295 | 66 |
| 2018 | 139 | 199 | 70 |
| 2019 | 202 | 306 | 66 |
| 2020 | 103 | 260 | 40 |
| 2021 | 182 | 296 | 61 |
| 2022 | 112 | 162 | 69 |
| 2023 | 188 | 256 | 73 |
| 2024 | 131 | 194 | 68 |
| 2025 | 137 | 244 | 56 |
| 2026 | 31 | 316 | 10 |

## 6. Lista de controlo dos diplomas centrais

| Área | Diploma | Aprovado por | Texto em vigor em | Vigência | Texto até | Em dia | Problemas |
|---|---|---|---|---|---|---|---|
| constitucional | Constituição da República Portuguesa | Decreto de Aprovação da Constituição | Decreto de Aprovação da Constituição (dre) | in_force | 2005-08-17 | sim | «artigo 149.º da Constituição» não chega ao registo certo (veio: Decreto-Lei n.º 149/94, articulado, artigo 8.º) |
| constitucional | Lei do Tribunal Constitucional | Lei n.º 28/82 | Lei n.º 28/82 (dre) | in_force | 2024-01-01 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 85/89 (texto de 1989-09-07), Lei n.º 88/95 (texto de 1995-09-01), Lei Orgânica n.º 1/2018 (texto de 2018-04-19); há outro registo do mesmo diploma com texto: pt:dre:377508:por (original, unknown) |
| constitucional | Lei Eleitoral da Assembleia da República | Lei n.º 14/79 | Lei n.º 14/79 (dre) | in_force | 2026-07-24 | sim | — |
| constitucional | Lei da Nacionalidade | Lei n.º 37/81 | Lei n.º 37/81 (dre) | in_force | 2026-05-19 | sim | 5 cópia(s) com texto de outra data servida(s) como em vigor: Lei Orgânica n.º 2/2006 (texto de 2006-04-17), Lei Orgânica n.º 9/2015 (texto de 2015-07-29), Lei Orgânica n.º 2/2018 (texto de 2018-07-05), Lei Orgânica n.º 2/2020 (texto de 2020-11-10), Lei Orgânica n.º 1/2024 (texto de 2024-03-05) |
| constitucional | Lei de Enquadramento Orçamental | Lei n.º 151/2015 | Lei n.º 151/2015, Anexo — (a que se refere o artigo 2.º) (dre) | in_force | 2022-01-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 37/2018 (texto de 2018-08-07), Lei n.º 41/2020 (texto de 2020-08-18) |
| civil | Código Civil | Decreto-Lei n.º 47344 | Decreto-Lei n.º 47344, Anexo — CÓDIGO CIVIL (dre) | in_force | 2026-07-01 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 31/2003 (texto de 2003-08-22), Lei n.º 6/2006 (texto de 2019-02-13), Lei n.º 31/2012 (texto de 2012-08-14) |
| civil | Cláusulas contratuais gerais | Decreto-Lei n.º 446/85 | Decreto-Lei n.º 446/85 (dre) | in_force | 2023-12-27 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 220/95 (texto de 1995-09-15) |
| civil | Responsabilidade do produtor | Decreto-Lei n.º 383/89 | Decreto-Lei n.º 383/89 (dre) | in_force | 2001-06-23 | sim | — |
| civil | Regime da propriedade horizontal (complementar) | Decreto-Lei n.º 268/94 | Decreto-Lei n.º 268/94 (dre) | in_force | 2022-04-10 | sim | — |
| civil | Direito real de habitação periódica | Decreto-Lei n.º 275/93 | Decreto-Lei n.º 275/93 (dre) | in_force | 2021-07-28 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 180/99 (texto de 1999-05-22), Decreto-Lei n.º 37/2011 (texto de 2011-03-10) |
| civil | Lei-Quadro das Fundações | Lei n.º 24/2012 | Lei n.º 24/2012, Anexo — (a que se refere o artigo 2.º) (dre) | in_force | 2022-01-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 150/2015 (texto de 2015-09-10), Lei n.º 67/2021 (texto de 2021-08-25) |
| família | União de facto | Lei n.º 7/2001 | Lei n.º 7/2001 (dre) | in_force | 2019-02-10 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 23/2010 (texto de 2010-08-30) |
| família | Proteção de crianças e jovens em perigo | Lei n.º 147/99 | Lei n.º 147/99, Anexo — Lei de protecção de crianças e j (dre) | in_force | 2025-04-02 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 142/2015 (texto de 2015-09-08) |
| família | Regime Geral do Processo Tutelar Cível | Lei n.º 141/2015 | Lei n.º 141/2015 (dre) | in_force | 2017-06-23 | sim | — |
| família | Lei Tutelar Educativa | Lei n.º 166/99 | Lei n.º 166/99, Anexo — LEI TUTELAR EDUCATIVA (dre) | in_force | 2015-02-14 | sim | — |
| família | Regime do maior acompanhado | Lei n.º 49/2018 | — (nao triado) | unknown | — | — | vigência desconhecida; alterado e sem texto em vigor (nao triado; 2 `amended_by`) |
| família | Regime Jurídico do Processo de Adoção | Lei n.º 143/2015 | Lei n.º 143/2015 (dre) | in_force | 2023-08-18 | sim | — |
| família | Procriação medicamente assistida | Lei n.º 32/2006 | Lei n.º 32/2006 (dre) | in_force | 2022-01-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 58/2017 (texto de 2017-07-25) |
| família | Apadrinhamento civil | Lei n.º 103/2009 | Lei n.º 103/2009 (dre) | in_force | 2015-10-08 | sim | — |
| arrendamento | Novo Regime do Arrendamento Urbano (NRAU) | Lei n.º 6/2006 | Lei n.º 6/2006 (dre) | in_force | 2024-02-04 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 31/2012 (texto de 2012-08-14), Lei n.º 79/2014 (texto de 2014-12-19) |
| arrendamento | Arrendamento rural | Decreto-Lei n.º 294/2009 | — (original sem alteracoes) | in_force | — | — | — |
| arrendamento | Arrendamento apoiado | Lei n.º 81/2014 | Lei n.º 81/2014 (dre) | in_force | 2023-05-30 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 32/2016 (texto de 2016-08-24) |
| arrendamento | Alojamento local | Decreto-Lei n.º 128/2014 | Decreto-Lei n.º 128/2014 (dre) | in_force | 2024-11-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 62/2018 (texto de 2018-08-22) |
| arrendamento | Lei de Bases da Habitação | Lei n.º 83/2019 | — (nao triado) | unknown | — | — | vigência desconhecida; alterado e sem texto em vigor (nao triado; 1 `amended_by`) |
| arrendamento | Obras em prédios arrendados | Decreto-Lei n.º 157/2006 | Decreto-Lei n.º 157/2006 (dre) | in_force | 2019-06-20 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 30/2012 (texto de 2012-08-14), Lei n.º 43/2017 (texto de 2017-06-14) |
| processo civil | Código de Processo Civil | Lei n.º 41/2013 | Lei n.º 41/2013 (dre) | in_force | 2025-10-22 | sim | — |
| processo civil | Regulamento das Custas Processuais | Decreto-Lei n.º 34/2008 | Decreto-Lei n.º 34/2008, Anexo III — Regulamento das Custas Proce (dre) | in_force | 2026-08-06 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 7/2012 (texto de 2012-02-13); «artigo 21.º do Regulamento das Custas Processuais» chega ao registo certo mas a outro artigo (veio: Decreto-Lei n.º 34/2008, Anexo III — Regulamento das Custas Processuais, artigo 39.º) |
| processo civil | Lei da Organização do Sistema Judiciário | Lei n.º 62/2013 | Lei n.º 62/2013 (dre) | in_force | 2026-09-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 40-A/2016 (texto de 2016-12-22) |
| processo civil | Regime da organização e funcionamento dos tribunais judiciais | Decreto-Lei n.º 49/2014 | Decreto-Lei n.º 49/2014 (dre) | in_force | 2022-01-04 | sim | — |
| processo civil | Lei da Arbitragem Voluntária | Lei n.º 63/2011 | — (original e o texto em vigor) | in_force | — | — | 1 `amended_by` e sem consolidação: a triagem diz que nenhum muda o texto |
| processo civil | Lei da Mediação | Lei n.º 29/2013 | — (original sem alteracoes) | in_force | — | — | — |
| processo civil | Julgados de paz | Lei n.º 78/2001 | Lei n.º 78/2001 (dre) | in_force | 2024-04-04 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 54/2013 (texto de 2013-07-31) |
| processo civil | Acesso ao direito e aos tribunais (apoio judiciário) | Lei n.º 34/2004 | Lei n.º 34/2004 (dre) | in_force | 2023-10-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 47/2007 (texto de 2007-08-28) |
| processo civil | Injunção e ação especial de cumprimento | Decreto-Lei n.º 269/98 | Decreto-Lei n.º 269/98, Anexo (dre) | in_force | 2020-01-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 107/2005 (texto de 2005-07-01) |
| processo civil | Regime do inventário notarial | Lei n.º 117/2019 | — (original sem alteracoes) | unknown | — | — | vigência desconhecida |
| processo civil | Estatuto da Ordem dos Advogados | Lei n.º 145/2015 | Lei n.º 145/2015 (dre) | in_force | 2024-04-01 | sim | — |
| processo civil | Estatuto dos Magistrados Judiciais | Lei n.º 21/85 | Lei n.º 21/85 (dre) | in_force | 2025-07-25 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 67/2019 (texto de 2019-08-27) |
| processo civil | Estatuto do Ministério Público | Lei n.º 68/2019 | Lei n.º 68/2019 (dre) | in_force | 2026-03-29 | sim | — |
| processo civil | Estatuto da Ordem dos Solicitadores e dos Agentes de Execução | Lei n.º 154/2015 | Lei n.º 154/2015 (dre) | in_force | 2024-04-01 | sim | — |
| penal | Código Penal | Decreto-Lei n.º 400/82 | Decreto-Lei n.º 48/95, (2.ª numeração) (dre) | in_force | 2026-09-01 | sim | o original não aponta para o registo com o texto em vigor (sem `republished_by` «Texto em vigor»); 3 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 400/82 (texto de 1982-09-23), Decreto-Lei n.º 400/82 (texto de 1982-09-23), Lei n.º 59/2007 (texto de 2007-09-04) |
| penal | Código de Processo Penal | Decreto-Lei n.º 78/87 | Decreto-Lei n.º 78/87, (2.ª numeração) (dre) | in_force | 2026-09-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 59/98 (texto de 1998-08-25), Lei n.º 48/2007 (texto de 2007-08-29); «artigo 263.º do Código de Processo Penal» não chega ao registo certo (veio: Decreto-Lei n.º 48/95, articulado, artigo 264.º) |
| penal | Código da Execução das Penas | Lei n.º 115/2009 | Lei n.º 115/2009 (dre) | in_force | 2023-08-20 | sim | «artigo 6.º do Código da Execução das Penas e Medidas Privativas da Liberdade» chega ao registo certo mas a outro artigo (veio: Lei n.º 115/2009, Anexo — CÓDIGO DA EXECUÇÃO DAS PENAS E MEDIDAS PRIVATIVAS DA LIBERDADE, artigo 133.º) |
| penal | Regime Geral das Contraordenações | Decreto-Lei n.º 433/82 | Decreto-Lei n.º 433/82 (dre) | in_force | 2025-01-14 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 244/95 (texto de 1995-09-14) |
| penal | Lei da droga (tráfico e consumo) | Decreto-Lei n.º 15/93 | Decreto-Lei n.º 15/93 (dre) | in_force | 2023-10-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 18/2009 (texto de 2009-05-11) |
| penal | Consumo de estupefacientes | Lei n.º 30/2000 | Lei n.º 30/2000 (dre) | in_force | 2023-11-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 114/2011 (texto de 2011-11-30) |
| penal | Violência doméstica | Lei n.º 112/2009 | Lei n.º 112/2009 (dre) | in_force | 2021-08-17 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 129/2015 (texto de 2015-09-03) |
| penal | Lei do Cibercrime | Lei n.º 109/2009 | Lei n.º 109/2009 (dre) | in_force | 2026-08-25 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 79/2021 (texto de 2021-11-24) |
| penal | Regime jurídico das armas e munições | Lei n.º 5/2006 | Lei n.º 5/2006 (dre) | in_force | 2019-09-24 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 17/2009 (texto de 2009-05-06), Lei n.º 12/2011 (texto de 2011-04-27), Lei n.º 50/2019 (texto de 2019-07-24) |
| penal | Branqueamento de capitais e financiamento do terrorismo | Lei n.º 83/2017 | Lei n.º 83/2017 (dre) | in_force | 2026-07-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 58/2020 (texto de 2020-08-31) |
| penal | Regime penal dos jovens adultos | Decreto-Lei n.º 401/82 | — (original sem alteracoes) | in_force | — | — | — |
| penal | Crimes de responsabilidade dos titulares de cargos políticos | Lei n.º 34/87 | Lei n.º 34/87 (dre) | in_force | 2022-03-21 | sim | — |
| penal | Infrações antieconómicas e contra a saúde pública | Decreto-Lei n.º 28/84 | Decreto-Lei n.º 28/84 (dre) | in_force | 2024-02-14 | sim | — |
| penal | Regime jurídico do cheque sem provisão | Decreto-Lei n.º 454/91 | Decreto-Lei n.º 454/91 (dre) | in_force | 2015-10-04 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 316/97 (texto de 1997-11-19) |
| penal | Identificação criminal | Lei n.º 37/2015 | Lei n.º 37/2015 (dre) | in_force | 2022-10-31 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 14/2022 (texto de 2022-08-02) |
| penal | Estatuto da Vítima | Lei n.º 130/2015 | Lei n.º 130/2015 (dre) | in_force | 2023-10-01 | sim | — |
| penal | Lei de combate ao terrorismo | Lei n.º 52/2003 | Lei n.º 52/2003 (dre) | in_force | 2026-09-01 | sim | — |
| penal | Proteção de testemunhas | Lei n.º 93/99 | Lei n.º 93/99 (dre) | in_force | 2023-02-15 | sim | — |
| penal | Lei de Saúde Mental | Lei n.º 35/2023 | — (original sem alteracoes) | unknown | — | — | vigência desconhecida |
| penal | Regime Geral da Prevenção da Corrupção | Decreto-Lei n.º 109-E/2021 | Decreto-Lei n.º 109-E/2021 (dre) | in_force | 2026-09-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 70/2025 (texto de 2025-04-29) |
| penal | Proteção de denunciantes | Lei n.º 93/2021 | — (original sem alteracoes) | unknown | — | — | vigência desconhecida |
| penal | Regime Geral das Infrações Tributárias (RGIT) | Lei n.º 15/2001 | Lei n.º 15/2001 (dre) | in_force | 2026-06-08 | sim | «artigo 8.º do Regime Geral das Infrações Tributárias» chega ao registo certo mas a outro artigo (veio: Lei n.º 15/2001, Anexo — REGIME GERAL DAS INFRACÇÕES TRIBUTÁRIAS, artigo 49.º) |
| trabalho | Código do Trabalho | Lei n.º 7/2009 | Lei n.º 7/2009 (dre) | in_force | 2025-04-26 | sim | — |
| trabalho | Regulamentação do Código do Trabalho | Lei n.º 105/2009 | Lei n.º 105/2009 (dre) | in_force | 2023-05-01 | sim | — |
| trabalho | Código de Processo do Trabalho | Decreto-Lei n.º 480/99 | Decreto-Lei n.º 480/99, Anexo — CÓDIGO DE PROCESSO DO TRABALHO D (dre) | in_force | 2024-11-10 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 295/2009 (texto de 2009-10-13), Lei n.º 107/2019 (texto de 2019-09-09); «artigo 101.º do Código de Processo do Trabalho» não chega ao registo certo (veio: Lei n.º 13/2023, articulado, artigo 20.º) |
| trabalho | Acidentes de trabalho e doenças profissionais | Lei n.º 98/2009 | Lei n.º 98/2009 (dre) | in_force | 2024-11-10 | sim | — |
| trabalho | Segurança e saúde no trabalho | Lei n.º 102/2009 | Lei n.º 102/2009 (dre) | in_force | 2019-10-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 3/2014 (texto de 2014-01-28) |
| trabalho | Contraordenações laborais e de segurança social | Lei n.º 107/2009 | Lei n.º 107/2009 (dre) | in_force | 2023-05-01 | sim | — |
| trabalho | Lei Geral do Trabalho em Funções Públicas | Lei n.º 35/2014 | Lei n.º 35/2014 (dre) | in_force | 2025-01-01 | sim | «artigo 23.º da Lei Geral do Trabalho em Funções Públicas» não chega ao registo certo (veio: Decreto Legislativo Regional n.º 23/2023/A, Anexo — ESTATUTO DO PESSOAL DOCENTE DA EDUCAÇÃO PRÉ-ESCOLAR E DOS ENSINOS BÁSICO E SECUNDÁRIO DA REGIÃO AUTÓNOMA DOS AÇORES, artigo 108.º) |
| trabalho | Contrato de serviço doméstico | Decreto-Lei n.º 235/92 | Decreto-Lei n.º 235/92 (dre) | in_force | 2023-05-01 | sim | — |
| trabalho | Fundos de compensação do trabalho | Lei n.º 70/2013 | Lei n.º 70/2013 (dre) | in_force | 2024-01-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 115/2023 (texto de 2023-12-15) |
| trabalho | SIADAP | Lei n.º 66-B/2007 | Lei n.º 66-B/2007 (dre) | in_force | 2024-10-01 | sim | — |
| trabalho | Estatuto do pessoal dirigente | Lei n.º 2/2004 | Lei n.º 2/2004 (dre) | in_force | 2025-01-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 64/2011 (texto de 2011-12-22) |
| trabalho | Estatuto da Aposentação | Decreto-Lei n.º 498/72 | Decreto-Lei n.º 498/72 (dre) | in_force | 2023-03-04 | sim | — |
| segurança social | Código dos Regimes Contributivos | Lei n.º 110/2009 | Lei n.º 110/2009 (dre) | in_force | 2026-01-01 | sim | — |
| segurança social | Regulamentação do Código dos Regimes Contributivos | Decreto Regulamentar n.º 1-A/2011 | Decreto Regulamentar n.º 1-A/2011 (dre) | in_force | 2026-01-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto Regulamentar n.º 6/2018 (texto de 2018-07-02) |
| segurança social | Lei de Bases da Segurança Social | Lei n.º 4/2007 | Lei n.º 4/2007 (dre) | in_force | 2013-12-31 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 83-A/2013 (texto de 2013-12-30) |
| segurança social | Pensões de invalidez e velhice | Decreto-Lei n.º 187/2007 | Decreto-Lei n.º 187/2007 (dre) | in_force | 2025-03-31 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 16-A/2021 (texto de 2021-02-25) |
| segurança social | Proteção na doença | Decreto-Lei n.º 28/2004 | Decreto-Lei n.º 28/2004 (dre) | in_force | 2024-03-01 | sim | — |
| segurança social | Proteção na parentalidade | Decreto-Lei n.º 91/2009 | Decreto-Lei n.º 91/2009 (dre) | in_force | 2026-08-14 | sim | — |
| segurança social | Proteção no desemprego | Decreto-Lei n.º 220/2006 | Decreto-Lei n.º 220/2006 (dre) | in_force | 2026-08-14 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 72/2010 (texto de 2010-06-18) |
| segurança social | Rendimento social de inserção | Lei n.º 13/2003 | Lei n.º 13/2003 (dre) | partially_in_force | 2026-08-14 | sim | — |
| segurança social | Abono de família | Decreto-Lei n.º 176/2003 | Decreto-Lei n.º 176/2003 (dre) | in_force | 2026-05-26 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 245/2008 (texto de 2008-12-18), Decreto-Lei n.º 133/2012 (texto de 2012-06-27) |
| segurança social | Prestação social para a inclusão | Decreto-Lei n.º 126-A/2017 | Decreto-Lei n.º 126-A/2017 (dre) | in_force | 2026-08-14 | sim | — |
| segurança social | Indexante dos apoios sociais | Lei n.º 53-B/2006 | Lei n.º 53-B/2006 (dre) | in_force | 2024-11-01 | sim | — |
| segurança social | Estatuto do Cuidador Informal | Lei n.º 100/2019 | Lei n.º 100/2019 (dre) | in_force | 2024-11-11 | sim | — |
| fiscal | Código do IRS | Decreto-Lei n.º 442-A/88 | Lei n.º 82-E/2014, Anexo — Código do Imposto sobre o Rendim (dre) | in_force | 2026-05-25 | **não** | o DRE mexeu no consolidado a 2026-11-16, depois da recolha; numeração diferente da do original: só 15 de 140 artigos com o mesmo número têm a mesma epígrafe; 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 442-A/88 (texto de 1988-11-30), Decreto-Lei n.º 198/2001 (texto de 2001-07-03) |
| fiscal | Código do IRC | Decreto-Lei n.º 442-B/88 | Lei n.º 2/2014, Anexo — CÓDIGO DO IMPOSTO SOBRE O RENDIM (dre) | in_force | 2026-01-01 | sim | numeração diferente da do original: só 9 de 115 artigos com o mesmo número têm a mesma epígrafe; 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 442-B/88 (texto de 1988-11-30), Decreto-Lei n.º 198/2001 (texto de 2003-01-01) |
| fiscal | Código do IVA | Decreto-Lei n.º 394-B/84 | Decreto-Lei n.º 102/2008, Anexo IV — CÓDIGO DO IMPOSTO SOBRE O VAL (dre) | in_force | 2026-09-01 | **não** | o DRE mexeu no consolidado a 2026-11-11, depois da recolha; o original não aponta para o registo com o texto em vigor (sem `republished_by` «Texto em vigor»); 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 394-B/84 (texto de 1984-12-26), Decreto-Lei n.º 195/89 (texto de 1989-06-12) |
| fiscal | Regime do IVA nas Transações Intracomunitárias (RITI) | Decreto-Lei n.º 290/92 | Decreto-Lei n.º 290/92, Anexo — Regime do IVA nas Transacções In (dre) | in_force | 2025-03-29 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 102/2008 (texto de 2008-08-18), Lei n.º 47/2020 (texto de 2020-08-24) |
| fiscal | Código do IMI e Código do IMT | Decreto-Lei n.º 287/2003 | Decreto-Lei n.º 287/2003 (dre) | in_force | 2026-05-25 | sim | — |
| fiscal | Código do Imposto do Selo | Lei n.º 150/99 | Lei n.º 150/99, Anexo I — CÓDIGO DO IMPOSTO DO SELO (dre) | in_force | 2025-07-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 287/2003 (texto de 2003-11-12) |
| fiscal | Código dos Impostos Especiais de Consumo | Decreto-Lei n.º 73/2010 | Decreto-Lei n.º 73/2010 (dre) | in_force | 2026-01-01 | **não** | o DRE mexeu no consolidado a 2026-11-09, depois da recolha; «artigo 5.º do Código dos Impostos Especiais de Consumo» chega ao registo certo mas a outro artigo (veio: Decreto-Lei n.º 73/2010, Anexo — CÓDIGO DOS IMPOSTOS ESPECIAIS DE CONSUMO, artigo 1.º) |
| fiscal | Código do ISV e Código do IUC | Lei n.º 22-A/2007 | Lei n.º 22-A/2007 (dre) | in_force | 2026-08-05 | sim | «artigo 8.º do Código do Imposto sobre Veículos» não chega ao registo certo (veio: Lei n.º 21/2021, articulado, artigo 7.º) |
| fiscal | Lei Geral Tributária | Decreto-Lei n.º 398/98 | Decreto-Lei n.º 398/98, Anexo — Lei geral tributária (dre) | in_force | 2025-07-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 15/2001 (texto de 2001-06-05) |
| fiscal | Código de Procedimento e de Processo Tributário | Decreto-Lei n.º 433/99 | Decreto-Lei n.º 433/99, Anexo — CÓDIGO DE PROCEDIMENTO E DE PROC (dre) | in_force | 2025-07-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 15/2001 (texto de 2001-06-05), Lei n.º 118/2019 (texto de 2019-09-17) |
| fiscal | Estatuto dos Benefícios Fiscais | Decreto-Lei n.º 215/89 | Decreto-Lei n.º 215/89, Anexo — ESTATUTO DOS BENEFÍCIOS FISCAIS (dre) | in_force | 2026-08-18 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 108/2008 (texto de 2008-06-26) |
| fiscal | Regime Complementar do Procedimento de Inspeção Tributária | Decreto-Lei n.º 413/98 | Decreto-Lei n.º 413/98 (dre) | in_force | 2026-06-08 | sim | — |
| fiscal | Código Fiscal do Investimento | Decreto-Lei n.º 162/2014 | Decreto-Lei n.º 162/2014 (dre) | in_force | 2026-08-22 | sim | — |
| fiscal | Regime de bens em circulação | Decreto-Lei n.º 147/2003 | Decreto-Lei n.º 147/2003 (dre) | in_force | 2025-03-29 | sim | — |
| fiscal | Regras de faturação | Decreto-Lei n.º 28/2019 | Decreto-Lei n.º 28/2019 (dre) | in_force | 2025-07-01 | sim | — |
| fiscal | Lei das Finanças Locais | Lei n.º 73/2013 | Lei n.º 73/2013 (dre) | in_force | 2026-08-18 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 51/2018 (texto de 2018-08-16) |
| comercial | Código Comercial | Carta de Lei de 28 de junho de 1888 | — | — | — | — | não está no acervo; «artigo 2.º do Código Comercial» não chega ao registo certo (veio: Decreto-Lei n.º 403/86, Anexo — CÓDIGO DO REGISTO COMERCIAL, artigo 68.º) |
| comercial | Código das Sociedades Comerciais | Decreto-Lei n.º 262/86 | Decreto-Lei n.º 262/86, Anexo — CÓDIGO DAS SOCIEDADES COMERCIAIS (dre) | in_force | 2026-09-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 76-A/2006 (texto de 2006-03-29) |
| comercial | Código do Registo Comercial | Decreto-Lei n.º 403/86 | Decreto-Lei n.º 403/86, Anexo — CÓDIGO DO REGISTO COMERCIAL (dre) | in_force | 2024-03-31 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 76-A/2006 (texto de 2006-03-29); «artigo 59.º do Código do Registo Comercial» não chega ao registo certo (veio: Lei n.º 89/2017, articulado, artigo 9.º) |
| comercial | Código dos Valores Mobiliários | Decreto-Lei n.º 486/99 | Decreto-Lei n.º 486/99, Anexo — CÓDIGO DOS VALORES MOBILIÁRIOS (dre) | in_force | 2026-09-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 357-A/2007 (texto de 2007-10-31), Lei n.º 35/2018 (texto de 2018-07-20); «artigo 212.º do Código dos Valores Mobiliários» não chega ao registo certo (veio: Decreto-Lei n.º 261/95, articulado, artigo 250.º) |
| comercial | Regime Geral das Instituições de Crédito e Sociedades Financeiras | Decreto-Lei n.º 298/92 | Decreto-Lei n.º 298/92, (2.ª numeração) (dre) | in_force | 2025-12-28 | sim | 6 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 201/2002 (texto de 2002-09-26), Decreto-Lei n.º 1/2008 (texto de 2008-01-03), Decreto-Lei n.º 157/2014 (texto de 2014-10-24), Lei n.º 23-A/2015 (texto de 2015-03-26), Lei n.º 35/2018 (texto de 2018-07-20), Lei n.º 23-A/2022 (texto de 2022-12-09) |
| comercial | Código da Propriedade Industrial | Decreto-Lei n.º 110/2018 | Decreto-Lei n.º 110/2018 (dre) | in_force | 2026-09-30 | sim | «artigo 9.º do Código da Propriedade Industrial» chega ao registo certo mas a outro artigo (veio: Decreto-Lei n.º 110/2018, Anexo — Código da Propriedade Industrial, artigo 374.º) |
| comercial | Código do Direito de Autor e dos Direitos Conexos | Decreto-Lei n.º 63/85 | Decreto-Lei n.º 63/85, Anexo — CÓDIGO DO DIREITO DE AUTOR E DOS (dre) | in_force | 2024-01-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 45/85 (texto de 1985-09-17), Lei n.º 16/2008 (texto de 2008-04-01); «artigo 115.º do Código do Direito de Autor e dos Direitos Conexos» chega ao registo certo mas a outro artigo (veio: Decreto-Lei n.º 63/85, Anexo — CÓDIGO DO DIREITO DE AUTOR E DOS DIREITOS CONEXOS, artigo 177.º) |
| comercial | Código Cooperativo | Lei n.º 119/2015 | Lei n.º 119/2015 (dre) | in_force | 2026-07-29 | sim | «artigo 62.º do Código Cooperativo» não chega ao registo certo (veio: Decreto-Lei n.º 49/2014, articulado, artigo 53.º) |
| comercial | Lei da Concorrência | Lei n.º 19/2012 | Lei n.º 19/2012 (dre) | in_force | 2022-09-16 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 17/2022 (texto de 2022-08-17) |
| comercial | Regime jurídico do contrato de seguro | Decreto-Lei n.º 72/2008 | Decreto-Lei n.º 72/2008 (dre) | in_force | 2026-04-16 | sim | — |
| comercial | Atividade seguradora e resseguradora | Lei n.º 147/2015 | Lei n.º 147/2015 (dre) | in_force | 2026-09-01 | sim | — |
| comercial | Estabelecimento individual de responsabilidade limitada | Decreto-Lei n.º 248/86 | Decreto-Lei n.º 248/86 (dre) | in_force | 2007-01-18 | sim | — |
| comercial | Contrato de agência | Decreto-Lei n.º 178/86 | Decreto-Lei n.º 178/86 (dre) | in_force | 1993-04-18 | sim | — |
| comercial | Locação financeira | Decreto-Lei n.º 149/95 | Decreto-Lei n.º 149/95 (dre) | in_force | 2008-03-26 | sim | — |
| comercial | Atividades de comércio, serviços e restauração (RJACSR) | Decreto-Lei n.º 10/2015 | Decreto-Lei n.º 10/2015 (dre) | in_force | 2023-03-25 | sim | — |
| comercial | Práticas individuais restritivas do comércio | Decreto-Lei n.º 166/2013 | Decreto-Lei n.º 166/2013 (dre) | in_force | 2022-01-01 | sim | — |
| comercial | Atrasos de pagamento nas transações comerciais | Decreto-Lei n.º 62/2013 | — (original e o texto em vigor) | in_force | — | — | 1 `amended_by` e sem consolidação: a triagem diz que nenhum muda o texto |
| comercial | Registo Nacional de Pessoas Coletivas | Decreto-Lei n.º 129/98 | Decreto-Lei n.º 129/98 (dre) | in_force | 2018-06-26 | sim | — |
| comercial | Registo Central do Beneficiário Efetivo | Lei n.º 89/2017 | Lei n.º 89/2017, Anexo — Regime Jurídico do Registo Centr (dre) | in_force | 2025-11-01 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 89/2017 (texto de 2020-09-01), Lei n.º 58/2020 (texto de 2020-08-31), Lei n.º 58/2020 (texto de 2020-08-31) |
| comercial | Sistema de Normalização Contabilística | Decreto-Lei n.º 158/2009 | Decreto-Lei n.º 158/2009 (dre) | in_force | 2025-12-06 | sim | — |
| comercial | Serviços de pagamento e moeda eletrónica | Decreto-Lei n.º 91/2018 | Decreto-Lei n.º 91/2018 (dre) | in_force | 2025-12-24 | sim | — |
| comercial | Estatuto das IPSS | Decreto-Lei n.º 119/83 | Decreto-Lei n.º 119/83, Anexo (dre) | in_force | 2026-07-12 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 172-A/2014 (texto de 2015-08-02), Decreto Legislativo Regional n.º 9/2015/M (texto de 2020-03-26), Decreto Legislativo Regional n.º 4/2020/M (texto de 2020-03-25) |
| insolvência | Código da Insolvência e da Recuperação de Empresas | Decreto-Lei n.º 53/2004 | Decreto-Lei n.º 53/2004, Anexo — CÓDIGO DA INSOLVÊNCIA E DA RECUP (dre) | in_force | 2024-11-10 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 200/2004 (texto de 2004-08-18); «artigo 153.º do Código da Insolvência e da Recuperação de Empresas» chega ao registo certo mas a outro artigo (veio: Decreto-Lei n.º 53/2004, Anexo — CÓDIGO DA INSOLVÊNCIA E DA RECUPERAÇÃO DE EMPRESAS, artigo 301.º) |
| insolvência | Estatuto do administrador judicial | Lei n.º 22/2013 | Lei n.º 22/2013 (dre) | in_force | 2022-04-11 | sim | — |
| insolvência | Regime extrajudicial de recuperação de empresas | Lei n.º 8/2018 | — (nao triado) | unknown | — | — | vigência desconhecida; alterado e sem texto em vigor (nao triado; 1 `amended_by`) |
| administrativo | Código do Procedimento Administrativo | Decreto-Lei n.º 4/2015 | Decreto-Lei n.º 4/2015 (dre) | in_force | 2023-02-11 | sim | — |
| administrativo | Código de Processo nos Tribunais Administrativos | Lei n.º 15/2002 | Lei n.º 15/2002, Anexo — CÓDIGO DE PROCESSO NOS TRIBUNAIS (dre) | in_force | 2024-11-10 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 4-A/2003 (texto de 2003-02-19), Decreto-Lei n.º 214-G/2015 (texto de 2015-10-02), Lei n.º 118/2019 (texto de 2019-09-17); «artigo 97.º do Código de Processo nos Tribunais Administrativos» não chega ao registo certo (veio: Lei n.º 114/2017, articulado, artigo 270.º) |
| administrativo | Estatuto dos Tribunais Administrativos e Fiscais | Lei n.º 13/2002 | Lei n.º 13/2002, Anexo — ESTATUTO DOS TRIBUNAIS ADMINISTR (dre) | in_force | 2025-07-25 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 107-D/2003 (texto de 2003-12-31), Decreto-Lei n.º 214-G/2015 (texto de 2015-10-02), Lei n.º 114/2019 (texto de 2019-09-12) |
| administrativo | Responsabilidade civil extracontratual do Estado | Lei n.º 67/2007 | Lei n.º 67/2007 (dre) | in_force | 2008-07-18 | sim | — |
| administrativo | Acesso aos documentos administrativos | Lei n.º 26/2016 | Lei n.º 26/2016 (dre) | in_force | 2021-08-27 | sim | — |
| administrativo | Código das Expropriações | Lei n.º 168/99 | Lei n.º 168/99, Anexo — CÓDIGO DAS EXPROPRIAÇÕES (dre) | in_force | 2026-08-09 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 56/2008 (texto de 2008-09-04); «artigo 50.º do Código das Expropriações» chega ao registo certo mas a outro artigo (veio: Lei n.º 168/99, Anexo — CÓDIGO DAS EXPROPRIAÇÕES, artigo 1.º) |
| administrativo | Regime jurídico das autarquias locais | Lei n.º 75/2013 | Lei n.º 75/2013 (dre) | in_force | 2024-03-01 | sim | — |
| administrativo | Lei-quadro dos institutos públicos | Lei n.º 3/2004 | Lei n.º 3/2004 (dre) | in_force | 2022-10-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 105/2007 (texto de 2007-04-03), Decreto-Lei n.º 5/2012 (texto de 2012-01-17) |
| administrativo | Lei de Organização e Processo do Tribunal de Contas | Lei n.º 98/97 | Lei n.º 98/97 (dre) | in_force | 2023-10-07 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 48/2006 (texto de 2006-08-29), Lei n.º 20/2015 (texto de 2015-03-09) |
| administrativo | Lei dos compromissos e pagamentos em atraso | Lei n.º 8/2012 | Lei n.º 8/2012 (dre) | in_force | 2026-06-02 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 22/2015 (texto de 2015-03-17) |
| administrativo | Entrada, permanência, saída e afastamento de estrangeiros | Lei n.º 23/2007 | Lei n.º 23/2007 (dre) | in_force | 2026-09-11 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 29/2012 (texto de 2012-08-09), Lei n.º 102/2017 (texto de 2017-08-28), Lei n.º 18/2022 (texto de 2022-08-25) |
| administrativo | Lei do asilo | Lei n.º 27/2008 | Lei n.º 27/2008 (dre) | in_force | 2026-09-11 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 26/2014 (texto de 2014-05-05) |
| administrativo | Licenciamento zero | Decreto-Lei n.º 48/2011 | Decreto-Lei n.º 48/2011 (dre) | in_force | 2015-03-01 | sim | — |
| contratação pública | Código dos Contratos Públicos | Decreto-Lei n.º 18/2008 | Decreto-Lei n.º 18/2008, Anexo — CÓDIGO DOS CONTRATOS PÚBLICOS (dre) | in_force | 2026-10-01 | **não** | o DRE mexeu no consolidado a 2026-11-11, depois da recolha; 3 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 278/2009 (texto de 2009-10-02), Decreto-Lei n.º 111-B/2017 (texto de 2018-01-01), Decreto-Lei n.º 177/2026 (texto de 2026-09-04) |
| contratação pública | Medidas especiais de contratação pública | Lei n.º 30/2021 | Lei n.º 30/2021 (dre) | in_force | 2026-10-01 | sim | — |
| consumo | Lei de Defesa do Consumidor | Lei n.º 24/96 | Lei n.º 24/96 (dre) | in_force | 2023-07-05 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 47/2014 (texto de 2014-07-28) |
| consumo | Venda de bens de consumo e conteúdos digitais | Decreto-Lei n.º 84/2021 | — (original sem alteracoes) | unknown | — | — | vigência desconhecida |
| consumo | Contratos celebrados à distância e fora do estabelecimento | Decreto-Lei n.º 24/2014 | Decreto-Lei n.º 24/2014 (dre) | in_force | 2023-04-03 | sim | — |
| consumo | Práticas comerciais desleais | Decreto-Lei n.º 57/2008 | Decreto-Lei n.º 57/2008 (dre) | in_force | 2023-04-03 | sim | — |
| consumo | Serviços públicos essenciais | Lei n.º 23/96 | Lei n.º 23/96 (dre) | in_force | 2019-08-28 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 12/2008 (texto de 2008-02-26) |
| consumo | Livro de reclamações | Decreto-Lei n.º 156/2005 | Decreto-Lei n.º 156/2005 (dre) | in_force | 2026-05-27 | sim | — |
| consumo | Crédito aos consumidores | Decreto-Lei n.º 133/2009 | Decreto-Lei n.º 133/2009 (dre) | in_force | 2025-12-10 | sim | — |
| consumo | Crédito à habitação | Decreto-Lei n.º 74-A/2017 | Decreto-Lei n.º 74-A/2017 (dre) | in_force | 2026-05-02 | sim | — |
| consumo | Código da Publicidade | Decreto-Lei n.º 330/90 | Decreto-Lei n.º 330/90 (dre) | in_force | 2026-09-21 | sim | «artigo 2.º do Código da Publicidade» não chega ao registo certo (veio: Decreto-Lei n.º 38/2003, articulado, artigo 4.º) |
| consumo | Resolução alternativa de litígios de consumo | Lei n.º 144/2015 | Lei n.º 144/2015 (dre) | in_force | 2021-07-28 | sim | — |
| consumo | Viagens organizadas | Decreto-Lei n.º 17/2018 | Decreto-Lei n.º 17/2018 (dre) | in_force | 2021-07-28 | sim | — |
| consumo | Práticas comerciais com redução de preço | Decreto-Lei n.º 70/2007 | Decreto-Lei n.º 70/2007 (dre) | in_force | 2023-04-03 | sim | — |
| consumo | Comércio eletrónico | Decreto-Lei n.º 7/2004 | Decreto-Lei n.º 7/2004 (dre) | in_force | 2026-04-20 | sim | — |
| estrada | Código da Estrada | Decreto-Lei n.º 114/94 | Lei n.º 72/2013, Anexo — CÓDIGO DA ESTRADA (dre) | in_force | 2025-04-11 | sim | numeração diferente da do original: só 31 de 171 artigos com o mesmo número têm a mesma epígrafe; 4 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 114/94 (texto de 1994-05-03), Decreto-Lei n.º 2/98 (texto de 1998-01-31), Decreto-Lei n.º 265-A/2001 (texto de 2002-01-02), Decreto-Lei n.º 44/2005 (texto de 2021-01-09) |
| estrada | Regulamento da Habilitação Legal para Conduzir | Decreto-Lei n.º 138/2012 | Decreto-Lei n.º 138/2012, Anexo — [a que refere a alínea b) do art (dre) | in_force | 2026-06-09 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 37/2014 (texto de 2014-03-14), Decreto-Lei n.º 40/2016 (texto de 2016-07-29) |
| estrada | Regulamento de Sinalização do Trânsito | Decreto Regulamentar n.º 22-A/98 | Decreto Regulamentar n.º 22-A/98 (dre) | in_force | 2021-08-25 | sim | — |
| estrada | Seguro obrigatório de responsabilidade civil automóvel | Decreto-Lei n.º 291/2007 | Decreto-Lei n.º 291/2007 (dre) | in_force | 2025-03-20 | sim | — |
| estrada | Fiscalização da condução sob influência do álcool | Lei n.º 18/2007 | — (original sem alteracoes) | in_force | — | — | — |
| estrada | Inspeções técnicas de veículos | Decreto-Lei n.º 144/2012 | Decreto-Lei n.º 144/2012 (dre) | in_force | 2025-03-13 | sim | — |
| estrada | TVDE | Lei n.º 45/2018 | Lei n.º 45/2018 (dre) | in_force | 2026-09-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 59/2026 (texto de 2026-08-25) |
| dados pessoais | Lei de execução do RGPD | Lei n.º 58/2019 | — (nao triado) | unknown | — | — | vigência desconhecida; alterado e sem texto em vigor (nao triado; 1 `amended_by`) |
| dados pessoais | Dados pessoais em matéria penal | Lei n.º 59/2019 | — (nao triado) | unknown | — | — | vigência desconhecida; alterado e sem texto em vigor (nao triado; 1 `amended_by`) |
| dados pessoais | Privacidade nas comunicações eletrónicas | Lei n.º 41/2004 | Lei n.º 41/2004 (dre) | in_force | 2022-11-14 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 46/2012 (texto de 2012-08-29) |
| dados pessoais | Organização e funcionamento da CNPD | Lei n.º 43/2004 | Lei n.º 43/2004 (dre) | in_force | 2019-08-09 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 58/2019 (texto de 2019-08-08) |
| dados pessoais | Videovigilância pelas forças de segurança | Lei n.º 95/2021 | — (nao triado) | unknown | — | — | vigência desconhecida; alterado e sem texto em vigor (nao triado; 1 `amended_by`) |
| dados pessoais | Segurança privada | Lei n.º 34/2013 | Lei n.º 34/2013 (dre) | in_force | 2019-09-06 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 46/2019 (texto de 2019-07-08) |
| dados pessoais | Lei das Comunicações Eletrónicas | Lei n.º 16/2022 | Lei n.º 16/2022 (dre) | in_force | 2026-01-15 | sim | — |
| dados pessoais | Carta Portuguesa de Direitos Humanos na Era Digital | Lei n.º 27/2021 | Lei n.º 27/2021 (dre) | in_force | 2022-08-12 | sim | — |
| registos | Código do Registo Predial | Decreto-Lei n.º 224/84 | Decreto-Lei n.º 224/84, (2.ª numeração) (dre) | in_force | 2026-04-16 | sim | 3 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 533/99 (texto de 1999-12-11), Decreto-Lei n.º 116/2008 (texto de 2008-07-04), Decreto-Lei n.º 125/2013 (texto de 2013-08-30); «artigo 79.º do Código do Registo Predial» não chega ao registo certo (veio: Decreto-Lei n.º 312/90, articulado, artigo 1.º) |
| registos | Código do Registo Civil | Decreto-Lei n.º 131/95 | Decreto-Lei n.º 131/95, Anexo — Código do Registo Civil (dre) | in_force | 2025-04-02 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 324/2007 (texto de 2007-09-28); «artigo 153.º do Código do Registo Civil» não chega ao registo certo (veio: Despacho Normativo n.º 229/91, articulado, artigo ) |
| registos | Código do Notariado | Decreto-Lei n.º 207/95 | Decreto-Lei n.º 207/95 (dre) | in_force | 2025-01-01 | sim | «artigo 4.º do Código do Notariado» chega ao registo certo mas a outro artigo (veio: Decreto-Lei n.º 207/95, articulado, artigo 1.º) |
| registos | Registo automóvel | Decreto-Lei n.º 54/75 | Decreto-Lei n.º 54/75 (dre) | in_force | 2019-08-21 | sim | — |
| registos | Regulamento Emolumentar dos Registos e Notariado | Decreto-Lei n.º 322-A/2001 | Decreto-Lei n.º 322-A/2001 (dre) | in_force | 2026-08-24 | sim | — |
| registos | Estatuto do Notariado | Decreto-Lei n.º 26/2004 | Decreto-Lei n.º 26/2004 (dre) | in_force | 2024-03-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 155/2015 (texto de 2015-09-15) |
| registos | Cartão de cidadão | Lei n.º 7/2007 | Lei n.º 7/2007 (dre) | in_force | 2024-07-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 32/2017 (texto de 2017-06-01), Lei n.º 61/2021 (texto de 2021-08-19) |
| urbanismo | Regime Jurídico da Urbanização e da Edificação | Decreto-Lei n.º 555/99 | Decreto-Lei n.º 555/99 (dre) | in_force | 2026-10-01 | sim | 5 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 177/2001 (texto de 2001-06-04), Lei n.º 60/2007 (texto de 2007-09-04), Decreto-Lei n.º 26/2010 (texto de 2010-03-30), Decreto-Lei n.º 136/2014 (texto de 2014-09-09), Decreto-Lei n.º 108/2026 (texto de 2026-08-03) |
| urbanismo | Regime Jurídico dos Instrumentos de Gestão Territorial | Decreto-Lei n.º 80/2015 | Decreto-Lei n.º 80/2015 (dre) | in_force | 2025-04-14 | sim | — |
| urbanismo | Lei de bases da política de solos e ordenamento do território | Lei n.º 31/2014 | Lei n.º 31/2014 (dre) | in_force | 2024-03-04 | sim | — |
| urbanismo | Regulamento Geral das Edificações Urbanas | Decreto-Lei n.º 38382 | Decreto-Lei n.º 38382 (dre) | in_force | 2026-08-03 | sim | — |
| urbanismo | Reabilitação urbana | Decreto-Lei n.º 307/2009 | Decreto-Lei n.º 307/2009 (dre) | in_force | 2026-08-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 32/2012 (texto de 2012-08-14) |
| urbanismo | Reserva Agrícola Nacional | Decreto-Lei n.º 73/2009 | Decreto-Lei n.º 73/2009 (dre) | in_force | 2023-06-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 199/2015 (texto de 2015-09-16) |
| urbanismo | Reserva Ecológica Nacional | Decreto-Lei n.º 166/2008 | Decreto-Lei n.º 166/2008 (dre) | in_force | 2026-07-04 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 239/2012 (texto de 2012-11-02), Decreto-Lei n.º 124/2019 (texto de 2019-08-28) |
| urbanismo | Avaliação de impacte ambiental | Decreto-Lei n.º 151-B/2013 | Decreto-Lei n.º 151-B/2013 (dre) | in_force | 2024-12-18 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 11/2023 (texto de 2023-02-10) |
| urbanismo | Lei de Bases do Ambiente | Lei n.º 19/2014 | — (alteracao por aplicar) | in_force | — | — | alterado e sem texto em vigor (alteracao por aplicar; 1 `amended_by`) |
| urbanismo | Lei da Água | Lei n.º 58/2005 | Lei n.º 58/2005 (dre) | in_force | 2024-01-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 130/2012 (texto de 2012-06-22) |
| urbanismo | Regime Geral da Gestão de Resíduos | Decreto-Lei n.º 102-D/2020 | Decreto-Lei n.º 102-D/2020 (dre) | in_force | 2025-05-23 | **não** | o DRE mexeu no consolidado a 2026-11-12, depois da recolha |
| urbanismo | Regulamento Geral do Ruído | Decreto-Lei n.º 9/2007 | Decreto-Lei n.º 9/2007 (dre) | in_force | 2007-08-06 | sim | — |
| urbanismo | Acessibilidades | Decreto-Lei n.º 163/2006 | Decreto-Lei n.º 163/2006 (dre) | in_force | 2024-03-04 | sim | — |
| urbanismo | Segurança contra incêndio em edifícios | Decreto-Lei n.º 220/2008 | Decreto-Lei n.º 220/2008 (dre) | in_force | 2021-07-28 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 224/2015 (texto de 2015-10-09), Lei n.º 123/2019 (texto de 2019-10-18) |
| urbanismo | Empreendimentos turísticos | Decreto-Lei n.º 39/2008 | Decreto-Lei n.º 39/2008 (dre) | in_force | 2021-07-28 | sim | 4 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 228/2009 (texto de 2009-09-14), Decreto-Lei n.º 15/2014 (texto de 2014-01-23), Decreto-Lei n.º 186/2015 (texto de 2015-09-03), Decreto-Lei n.º 80/2017 (texto de 2017-06-30) |
| saúde e educação | Lei de Bases da Saúde | Lei n.º 95/2019 | — (nao triado) | unknown | — | — | vigência desconhecida; alterado e sem texto em vigor (nao triado; 1 `amended_by`) |
| saúde e educação | Estatuto do Serviço Nacional de Saúde | Decreto-Lei n.º 52/2022 | Decreto-Lei n.º 52/2022 (dre) | in_force | 2025-04-02 | sim | — |
| saúde e educação | Estatuto do Medicamento | Decreto-Lei n.º 176/2006 | Decreto-Lei n.º 176/2006 (dre) | in_force | 2026-07-01 | sim | 2 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 20/2013 (texto de 2013-02-14), Decreto-Lei n.º 128/2013 (texto de 2013-09-05) |
| saúde e educação | Lei de Bases do Sistema Educativo | Lei n.º 46/86 | Lei n.º 46/86 (dre) | in_force | 2026-08-08 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 49/2005 (texto de 2005-08-30) |
| saúde e educação | Estatuto do Aluno e Ética Escolar | Lei n.º 51/2012 | Lei n.º 51/2012 (dre) | in_force | 2012-09-05 | sim | — |
| saúde e educação | Regime jurídico das instituições de ensino superior | Lei n.º 62/2007 | Lei n.º 62/2007 (dre) | in_force | 2026-08-01 | sim | 1 cópia(s) com texto de outra data servida(s) como em vigor: Lei n.º 32/2026 (texto de 2026-07-20) |
| saúde e educação | Estatuto da Carreira Docente | Decreto-Lei n.º 139-A/90 | Decreto-Lei n.º 41/2012, Anexo — ESTATUTO DA CARREIRA DOS EDUCADO (dre) | in_force | 2023-12-30 | sim | o original não aponta para o registo com o texto em vigor (sem `republished_by` «Texto em vigor»); numeração diferente da do original: só 96 de 148 artigos com o mesmo número têm a mesma epígrafe; 4 cópia(s) com texto de outra data servida(s) como em vigor: Decreto-Lei n.º 139-A/90 (texto de 1990-04-28), Decreto-Lei n.º 1/98 (texto de 1998-01-02), Decreto-Lei n.º 15/2007 (texto de 2007-01-19), Decreto-Lei n.º 270/2009 (texto de 2009-09-30) |

## 8. O que o índice não lê como artigos

Registos portugueses com texto. «Em vigor»: `in_force` ou `partially_in_force` no DRE. O leitor conhece `###### Artigo`, `###### ARTIGO`, `###### Base`, `###### 1.º` e os anexos `## Anexo` e `## ANEXO`; aqui conta-se o que fica por ler como unidade. Destino das unidades dos registos em vigor: em blocos de ~300 palavras, dentro do texto de um artigo, cortada (para lá dos 30 000 caracteres do pedaço) e fora do índice (antes do primeiro artigo do diploma ou do anexo).

| Unidade | Registos | Em vigor | Dos quais prioritários | Vigência desconhecida | Unidades (em vigor) | Em blocos | Dentro de um artigo | Cortadas | Fora do índice |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| «Base N» solta no texto | 284 | 219 | 170 | 23 | 6689 | 2932 | 1728 | 2012 | 17 |
| «Cláusula N» | 1803 | 209 | 11 | 1285 | 4307 | 3580 | 427 | 90 | 210 |
| títulos de nível 6 de outra forma | 517 | 272 | 62 | 139 | 1066 | 766 | 127 | 19 | 154 |

Em vigor, em blocos, com «Artigo 1.º … Art. 2.º …» no início das linhas (teto, por expressão regular): 8750 registos (3991 prioritários, 1469 portarias), 114415 artigos.

Leis em vigor ou de vigência desconhecida com bases soltas no texto:

| Lei | Data | Vigência | Sumário | No índice | Bases | Citada por vigentes |
|---|---|---|---|---|--:|--:|
| Lei n.º 2103 | 1960-03-22 | in_force | Promulga as bases do abastecimento de água às populações rurais | blocos | 19 | 6 |
| Lei n.º 2107 | 1961-04-05 | in_force | Promulga as bases para a execução do Plano de construções para o ensino primário no contin | blocos | 25 | 68 |
| Lei n.º 2108 | 1961-04-18 | in_force | Promulga as bases para a execução do plano de desenvolvimento e beneficiação das redes de  | blocos | 17 | 3 |
| Lei n.º 2112 | 1962-02-17 | in_force | Promulga as bases para assegurar o funcionamento dos órgãos de governo do Estado da Índia | blocos | 10 | 7 |
| Lei n.º 2113 | 1962-04-11 | in_force | Promulga as bases da organização judiciária | blocos | 23 | 4 |
| Lei n.º 2114 | 1962-06-15 | in_force | Promulga as bases do arrendamento rural | blocos | 29 | 4 |
| Lei n.º 2119 | 1963-06-24 | in_force | Promulga as alterações à Lei Orgânica do Ultramar Português | blocos | 33 | 17 |
| Lei n.º 2122 | 1964-01-14 | in_force | Promulga as bases para os reembolsos dos custos de linhas novas de energia eléctrica | blocos | 5 | 2 |
| Lei n.º 2123 | 1964-12-14 | in_force | Promulga as bases para a execução do Plano Intercalar de Fomento do continente e ilhas adj | blocos | 14 | 23 |
| Lei n.º 2126 | 1965-06-21 | in_force | Promulga as bases que alteram o Decreto-Lei n.º 28219 (uso de acendedores e isqueiros) | blocos | 6 | 0 |
| Lei n.º 2127 | 1965-08-03 | in_force | Promulga as bases do regime jurídico dos acidentes de trabalho e doenças profissionais | blocos | 51 | 49 |
| Lei n.º 2129 | 1966-08-20 | in_force | Promulga as bases sobre a preferência dos cônjuges no provimento de lugares de professores | blocos | 8 | 1 |
| Lei n.º 2132 | 1967-05-26 | in_force | Promulga o regime jurídico da caça | blocos | 70 | 10 |
| Lei n.º 2133 | 1967-12-20 | in_force | Promulga as bases em que o Governo promoverá a execução do III Plano de Fomento para o per | blocos | 11 | 14 |
| Lei n.º 2137 | 1968-12-26 | in_force | Considera eleitores da Assembleia Nacional todos os cidadãos portugueses, maiores ou emanc | blocos | 2 | 2 |
| Lei n.º 2144 | 1969-05-29 | in_force | Promulga a reorganização das Casas do Povo e os regimes de previdência rural - Revoga o De | blocos | 33 | 14 |
| Lei n.º 4/70 | 1970-04-29 | in_force | Autoriza o Governo a instituir tribunais de família, que constituirão órgãos judiciais ord | blocos | 6 | 3 |
| Lei n.º 5/70 | 1970-06-06 | in_force | Determina que seja livre a circulação de mercadorias nacionais ou nacionalizadas entre as  | blocos | 7 | 14 |
| Lei n.º 6/70 | 1970-06-08 | in_force | Insere disposições relativas à realização de acordos colectivos sobre a comercialização de | blocos | 10 | 1 |
| Lei n.º 8/70 | 1970-06-18 | in_force | Autoriza as federações dos grémios da lavoura, os organismos de coordenação económica e os | blocos | 7 | 2 |
| Lei n.º 1/71 | 1971-01-29 | in_force | Determina que sejam designados pelas respectivas corporações os vogais que fazem parte dos | blocos | 8 | 1 |
| Lei n.º 2/71 | 1971-04-12 | in_force | Estabelece o regime de actividade de seguros e resseguros - Cria o Conselho Nacional de Se | blocos | 26 | 5 |
| Lei n.º 5/71 | 1971-11-05 | in_force | Promulga as bases relativas à lei de imprensa | blocos | 42 | 2 |
| Lei n.º 8/71 | 1971-12-09 | in_force | Promulga as bases relativas à actividade teatral - Revoga várias disposições legislativas | blocos | 37 | 6 |
| Lei n.º 2/72 | 1972-05-10 | in_force | Promulga as base sobre organização judiciária | blocos | 6 | 4 |
| Lei n.º 3/72 | 1972-05-27 | in_force | Promulga as bases sobre fomento industrial - Revoga as Leis n.os 2005 e 2052 | blocos | 29 | 15 |
| Lei n.º 5/72 | 1972-06-23 | in_force | Promulga as bases sobre a revisão da Lei Orgânica do Ultramar | blocos | 78 | 52 |
| Lei n.º 2/73 | 1973-02-10 | in_force | Institui o registo nacional de identificação | blocos | 8 | 2 |
| Lei n.º 6/73 | 1973-08-13 | in_force | Promulga a Lei de Terras do Ultramar | blocos | 33 | 2 |
| Lei n.º 8/73 | 1973-12-26 | in_force | Organização e execução do IV Plano de Fomento (1974-1979) | blocos | 18 | 6 |
| Lei n.º 22/92 | 1992-08-14 | in_force | Altera a Lei n.º 2127, de 3 de Agosto de 1965, estabelecendo a igualdade de direitos relat | blocos | 2 | 0 |
| Lei n.º 161/99 | 1999-09-14 | in_force | Primeira alteração, por apreciação parlamentar, do Decreto-Lei n.º 394-A/98, de 15 de Deze | artigos | 3 | 11 |
| Lei n.º 27/2002 | 2002-11-08 | in_force | Aprova o novo regime jurídico da gestão hospitalar e procede à primeira alteração à Lei n. | artigos | 3 | 66 |
| Lei n.º 30/2006 | 2006-07-11 | in_force | Procede à conversão em contra-ordenações de contravenções e transgressões em vigor no orde | artigos | 2 | 12 |
| Lei n.º 95/2019 | 2019-09-04 | unknown | Aprova a Lei de Bases da Saúde e revoga a Lei n.º 48/90, de 24 de agosto, e o Decreto-Lei  | artigos | 37 | 24 |

## 8-B. Em vigor no DRE e sem um artigo aberto e não revogado no índice (75)

| Classe | Prioritários | Portarias | Outros | Total |
|---|--:|--:|--:|--:|
| pedaços abertos, todos revogados | 37 | 12 | 9 | 58 |
| todos os pedaços fechados, com ligação ao registo que tem o texto | 17 | 0 | 0 | 17 |

Revogações publicadas que ainda não produziram efeitos (os artigos contam como em vigor até lá): 197 artigos em 15 registos (5 em que são todos os artigos em vigor do registo); por data de efeitos: 2026-11-28 5, 2026-12-01 1, 2026-12-31 133, 2027-01-01 16, 2027-03-01 41, 2032-07-04 1.
