# Comunicação: o que se pode dizer sobre o leis-portugal

Textos prontos para apresentar o projeto (redes sociais, apresentações, candidaturas, imprensa), com números que estão medidos. Para mudar um número, confirma-o primeiro na fonte indicada; se não estiver medido, não entra.

Números de 12 de novembro de 2026.

## Numa frase

> A legislação portuguesa em formato aberto: mais de 360 mil diplomas e atos, ligados às fontes oficiais e atualizados todos os dias.

## Ligações

- Site e descarga da aplicação: https://joaobarrosodev.github.io/leis-portugal/
- Repositório: https://github.com/joaobarrosodev/leis-portugal
- Índice de pesquisa: https://huggingface.co/datasets/joaobarrosodev/leis-portugal-indice

## Num parágrafo curto (redes sociais)

> O leis-portugal reúne num repositório público e gratuito a legislação portuguesa desde 1833, o direito da União Europeia em vigor e os acórdãos do Tribunal Constitucional. Cada texto liga à fonte oficial e o histórico de alterações fica registado. Tem também um protótipo de perguntas: responde com a lei e o artigo em vigor e, quando não tem a certeza, diz que não sabe.

## Em três parágrafos (apresentação, candidatura)

> O leis-portugal é um projeto open-source que reúne a legislação portuguesa num repositório público, em texto legível por pessoas e por máquinas. Tem mais de 360 mil registos: a 1.ª Série do Diário da República desde 1833, praticamente completa, legislação regional dos Açores e da Madeira, cerca de 54 mil atos da União Europeia e mais de 29 mil acórdãos do Tribunal Constitucional. Atualiza-se todos os dias a partir das fontes oficiais.
>
> Além do texto publicado, o projeto liga os diplomas entre si (cerca de um milhão de relações de alteração, revogação e citação) e guarda as versões, para se poder ler a lei como estava numa data. Nos diplomas alterados que o Diário da República não consolida, produz o texto em vigor, verificado às cegas e marcado como sem valor oficial.
>
> Por cima destes dados há um protótipo de perguntas. Quando responde, acerta em cerca de 95% das vezes. Responde a mais de 8 em cada 10 perguntas e, nas restantes, diz que não sabe em vez de inventar. Cita sempre a lei e o artigo, na redação em vigor. É um protótipo e não substitui um advogado. A aplicação para Mac e Windows descarrega-se em joaobarrosodev.github.io/leis-portugal.

## Números que se podem usar

| Frase | Fonte |
|---|---|
| Mais de 360 mil diplomas e atos | [README](README.md#o-que-já-existe-novembro-de-2026), [`reports/COBERTURA.md`](reports/COBERTURA.md) |
| 1.ª Série do Diário da República desde 1833, praticamente completa | [README](README.md#cobertura-e-progresso) |
| Cerca de 54 mil atos da UE (96% dos que estão em vigor) | [README](README.md#cobertura-e-progresso) |
| Mais de 29 mil acórdãos do Tribunal Constitucional (1983–2026) | [README](README.md#cobertura-e-progresso) |
| Cerca de um milhão de relações entre diplomas | [README](README.md#o-que-já-existe-novembro-de-2026) |
| Atualização diária, automática | [README](README.md#atualização-automática) |
| Quando responde, acerta em cerca de 95% | [`rag/README.md`](rag/README.md), teste de 530 perguntas e 281 em linguagem comum |
| Responde a mais de 8 em cada 10 perguntas | idem (83% no teste, 89% em linguagem comum) |
| Cerca de 4 em cada 5 perguntas recebem resposta certa | idem (79% e 84%) |
| Recusa perguntas sobre leis que não existem | idem (78 de 80) |

## O que não se pode dizer

| Não dizer | Porquê | Dizer antes |
|---|---|---|
| "Responde a 95% das perguntas de um advogado" | Os 95% contam só as perguntas a que responde. Não foi testado com perguntas de advogados e nenhum jurista reviu as respostas. | "Quando responde, acerta em cerca de 95%" |
| "Substitui um advogado" ou "aconselhamento jurídico" | Não analisa casos e não interpreta a lei. O repositório não é aconselhamento jurídico. | "Ajuda a encontrar o que diz a lei, com a fonte" |
| "Toda a legislação portuguesa" | Falta legislação local, parte da 2.ª Série e o texto de cerca de 70 mil diplomas antigos que só existem em PDF digitalizado. | "Praticamente toda a 1.ª Série desde 1833" |
| "Texto oficial" ou "versão oficial" | O texto em vigor produzido pelo projeto não tem valor oficial. A fonte oficial é o Diário da República. | "Com ligação à fonte oficial" |
| "Validado por juristas" | As respostas foram julgadas por modelos de IA, às cegas, e não por juristas. | "Medido às cegas" |
| "Sem erros" ou "100%" | Nenhuma medição dá 100% em perguntas novas, e a conversão automática pode ter erros. | O número medido, com a ressalva |

## Ressalva que acompanha qualquer número de qualidade

> Protótipo. Medido com juízes de IA às cegas, sem revisão de jurista. Não substitui um advogado nem a consulta do Diário da República.

## Imagem de partilha

[`.github/social-preview.png`](.github/social-preview.png) (1280×640) é a imagem que aparece quando se partilha o link do repositório. Põe-se à mão no GitHub, em Settings → General → Social preview. Gera-se com `python .github/social-preview.py`: se os números do README mudarem, atualizam-se no script e gera-se outra vez.
