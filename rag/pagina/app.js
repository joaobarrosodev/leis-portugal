"use strict";

const CODIGO = document.querySelector('meta[name="codigo"]').content;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

let estado = null;
let escolhida = "claude";
let porAvaliar = null; // id da última resposta ainda sem avaliação

const PASSOS_CHAVE = {
  claude: [
    ["Cria uma conta (ou entra) em ", "conta", "platform.claude.com", "."],
    ["Carrega créditos na conta, na parte de faturação (Billing). A API é paga por uso.", null, null, ""],
    ["Abre a ", "chaves", "página das chaves", ", carrega em Create Key, dá-lhe um nome (por exemplo \"leis-portugal\") e copia a chave. Começa por sk-ant- e só é mostrada uma vez."],
  ],
  openai: [
    ["Cria uma conta (ou entra) em ", "conta", "platform.openai.com", "."],
    ["Adiciona créditos na parte de faturação (Billing).", null, null, ""],
    ["Abre a ", "chaves", "página das chaves", ", cria uma chave nova (Create new secret key) e copia-a. Só é mostrada uma vez."],
  ],
  gemini: [
    ["Entra com a tua conta Google no ", "conta", "Google AI Studio", "."],
    ["Abre a ", "chaves", "página das chaves", " e cria uma chave (Create API key). Copia-a."],
    ["Para mais pedidos, ou para o Gemini 4 Carbon, ativa a faturação (Set up billing) na mesma página.", null, null, ""],
  ],
};

async function api(caminho, dados) {
  const opcoes = { headers: { "X-Codigo": CODIGO } };
  if (dados !== undefined) {
    opcoes.method = "POST";
    opcoes.headers["Content-Type"] = "application/json";
    opcoes.body = JSON.stringify(dados);
  }
  const r = await fetch(caminho, opcoes);
  const corpo = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(corpo.erro || `Erro ${r.status}`);
  return corpo;
}

function el(tag, texto, classe) {
  const e = document.createElement(tag);
  if (texto) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

/* ---------------------------------------------------------------- estado e faixa */

async function atualizarEstado() {
  estado = await api("/api/estado");
  const ia = $("#ia-atual");
  ia.hidden = false;
  ia.textContent = estado.com_chave ? estado.descricao : "Sem IA: mostra o artigo mais provável";
  const faixa = $("#faixa-estado");
  const p = estado.dados.progresso;
  const emCurso = ["a descarregar", "a verificar", "a descomprimir"].includes(p.fase);
  faixa.replaceChildren();
  if (emCurso) {
    faixa.hidden = false;
    const pct = p.total ? Math.floor((100 * p.feito) / p.total) : 0;
    faixa.append(el("div", p.fase === "a descarregar" ? `A descarregar os dados: ${(p.feito / 1e9).toFixed(2)} de ${(p.total / 1e9).toFixed(2)} GB (${pct}%). Podes fechar e voltar: continua onde parou.` : `Quase pronto: ${p.fase}…`));
    const barra = el("progress");
    barra.max = 100;
    barra.value = pct;
    faixa.append(barra);
    setTimeout(atualizarEstado, 1500);
  } else if (estado.estado === "a preparar") {
    faixa.hidden = false;
    faixa.textContent = "A preparar a pesquisa (da primeira vez, o modelo de pesquisa é descarregado: ~0,6 GB)…";
    setTimeout(atualizarEstado, 2000);
  } else if (estado.estado === "sem dados") {
    faixa.hidden = false;
    if (p.fase === "erro") faixa.append(el("div", `A descarga falhou: ${p.mensagem}`, "aviso aviso-vermelho"));
    if (estado.dados.pode_descarregar) {
      faixa.append(el("div", "Falta descarregar a legislação para pesquisar neste computador (cerca de 5 GB da primeira vez, com os modelos de pesquisa). Só é preciso uma vez; depois atualiza-se sozinha."));
      const b = el("button", "Descarregar os dados", "botao");
      b.type = "button";
      b.addEventListener("click", async () => {
        await api("/api/dados/descarregar", {});
        atualizarEstado();
      });
      faixa.append(b);
    } else {
      faixa.append(el("div", "Ainda não há dados para pesquisar neste computador. No repositório, corre ./perguntar uma vez para construir o índice." + (estado.erro ? ` (${estado.erro})` : "")));
    }
  } else {
    faixa.hidden = true;
  }
  return estado;
}

/* ---------------------------------------------------------------- passo a passo */

function irPara(n) {
  $$(".passo").forEach((p) => (p.hidden = p.dataset.passo !== String(n)));
  $$(".passos li").forEach((li) => li.classList.toggle("atual", li.dataset.passo === String(n)));
  if (n === 3) prepararPassosChave();
  if (n === 4) prepararModelos($("#modelo"), escolhida);
}

function desenharEscolhas() {
  const caixa = $("#escolha-ia");
  caixa.replaceChildren();
  for (const [nome, p] of Object.entries(estado.provedores)) {
    const b = el("button", "", "escolha");
    b.type = "button";
    b.setAttribute("role", "radio");
    b.setAttribute("aria-checked", String(nome === escolhida));
    const titulo = el("strong", p.nome);
    const selo = nome === estado.medido.provedor ? el("span", "medido: cerca de 95%", "selo selo-medido") : el("span", "não medido", "selo selo-nao");
    titulo.append(selo);
    b.append(titulo, el("span", nome === estado.medido.provedor ? `Recomendado. Modelo ${estado.medido.modelo}, o único com qualidade medida.` : `Modelo ${p.modelo}. Funciona da mesma forma, mas a qualidade não foi medida.`));
    b.addEventListener("click", () => {
      escolhida = nome;
      desenharEscolhas();
    });
    caixa.append(b);
  }
}

function prepararPassosChave() {
  const p = estado.provedores[escolhida];
  $$(".nome-ia").forEach((s) => (s.textContent = p.nome));
  const lista = $("#passos-chave");
  lista.replaceChildren();
  for (const [antes, ligacao, textoLigacao, depois] of PASSOS_CHAVE[escolhida]) {
    const li = el("li", antes);
    if (ligacao) {
      const a = el("a", textoLigacao);
      a.href = p[ligacao];
      a.target = "_blank";
      a.rel = "noopener";
      li.append(a, document.createTextNode(depois));
    }
    lista.append(li);
  }
}

function prepararModelos(select, nome, atual) {
  const p = estado.provedores[nome];
  select.replaceChildren();
  for (const m of p.modelos) {
    const o = el("option", m === estado.medido.modelo ? `${m} (medido)` : m);
    o.value = m;
    select.append(o);
  }
  select.value = atual && p.modelos.includes(atual) ? atual : p.modelo;
}

async function testarChave(nome, modelo, chave, saida) {
  saida.textContent = "A testar…";
  try {
    const r = await api("/api/configurar", { provedor: nome, modelo, chave });
    saida.textContent = r.mensagem;
    saida.style.color = r.ok ? "var(--verde-claro)" : "var(--vermelho)";
    if (r.ok) estado = r.estado;
    return r.ok;
  } catch (e) {
    saida.textContent = e.message;
    saida.style.color = "var(--vermelho)";
    return false;
  }
}

function prepararAssistente() {
  $("#percebi").addEventListener("change", (e) => ($("#comecar").disabled = !e.target.checked));
  $$("[data-ir]").forEach((b) => b.addEventListener("click", () => irPara(Number(b.dataset.ir))));
  $("#sem-ia").addEventListener("click", async () => {
    await api("/api/sem-ia", {});
    mostrarPrincipal();
  });
  $("#testar").addEventListener("click", async () => {
    const ok = await testarChave(escolhida, $("#modelo").value, $("#chave").value, $("#resultado-chave"));
    if (ok) {
      $("#chave").value = "";
      setTimeout(mostrarPrincipal, 900);
    }
  });
}

/* ---------------------------------------------------------------- perguntas */

function mostrarPrincipal() {
  $("#assistente").hidden = true;
  $("#principal").hidden = false;
  atualizarEstado();
  $("#pergunta").focus();
}

async function avaliar(id, dados) {
  try {
    await api("/api/avaliar", { id, ...dados });
  } catch (_) {
    /* sem rede local: não há nada a fazer */
  }
}

function desenharResposta(r) {
  const c = $("#modelo-resposta").content.firstElementChild.cloneNode(true);
  $(".r-pergunta", c).textContent = r.pergunta;
  if (r.pesquisa_por) {
    const p = $(".r-pesquisa", c);
    p.hidden = false;
    p.textContent = `Pesquisa por: ${r.pesquisa_por}`;
  }
  const corpo = $(".r-corpo", c);
  if (r.erro) {
    corpo.append(el("div", `Erro da IA: ${r.erro}`, "aviso aviso-vermelho"));
    const b = el("button", "Abrir Definições", "botao-pequeno");
    b.type = "button";
    b.addEventListener("click", abrirDefinicoes);
    corpo.append(b);
  } else if (!r.responde) {
    corpo.classList.add("nao-sei");
    corpo.append(el("span", "Não sei.", "titulo-nao-sei"), document.createTextNode(`Porquê: ${r.motivo}. É preferível dizer que não sabe do que arriscar uma resposta errada.`));
  } else if (r.com_llm) {
    corpo.textContent = r.texto;
  } else {
    corpo.append(el("div", "Sem IA: este é o artigo mais provável, não uma resposta escrita.", "nota"));
    corpo.append(el("strong", r.citacoes[0]?.rotulo || ""), el("div", r.citacoes[0]?.texto || "", "texto-artigo"));
  }

  const avisos = $(".r-avisos", c);
  for (const a of r.avisos) avisos.append(el("div", a, "aviso aviso-ouro"));
  if (r.em_falta.length) avisos.append(el("div", `Não está no acervo: ${r.em_falta.join(", ")}`, "aviso aviso-ouro"));
  if (r.aviso_modelo) avisos.append(el("div", r.aviso_modelo, "aviso aviso-verde"));

  if (r.com_llm && r.responde && r.citacoes.length) {
    const f = $(".r-fontes", c);
    f.hidden = false;
    for (const art of r.citacoes) {
      const li = el("li");
      const d = el("details");
      d.append(el("summary", art.rotulo), el("div", art.texto, "texto-artigo"));
      li.append(d);
      $("ul", f).append(li);
    }
  }
  if (r.jurisprudencia.length) {
    const j = $(".r-juris", c);
    j.hidden = false;
    for (const a of r.jurisprudencia) {
      const li = el("li");
      const texto = `Acórdão n.º ${a.numero}${a.data ? `, de ${a.data}` : ""}: ${a.sentido}`;
      if (a.url) {
        const link = el("a", texto);
        link.href = a.url;
        link.target = "_blank";
        link.rel = "noopener";
        li.append(link);
      } else li.textContent = texto;
      $("ul", j).append(li);
    }
    if (r.jurisprudencia_resto.length) $("ul", j).append(el("li", "e mais: " + r.jurisprudencia_resto.map((x) => `${x.n} ${x.sentido.toLowerCase()}`).join("; ")));
  }
  if (r.outros.length) {
    const o = $(".r-outros", c);
    o.hidden = false;
    for (const art of r.outros) {
      const d = el("details");
      d.append(el("summary", art.rotulo), el("div", art.texto, "texto-artigo"));
      const li = el("li");
      li.append(d);
      $("ul", o).append(li);
    }
  }

  const caixaAvaliar = $(".r-avaliar", c);
  const fechar = () => {
    $$("button", caixaAvaliar).forEach((b) => (b.hidden = true));
    $(".r-esperado", caixaAvaliar).hidden = true;
    caixaAvaliar.firstElementChild.hidden = true;
    $(".r-gravado", caixaAvaliar).hidden = false;
    if (porAvaliar === r.id) porAvaliar = null;
  };
  $('[data-certo="1"]', caixaAvaliar).addEventListener("click", () => {
    avaliar(r.id, { certo: true });
    fechar();
  });
  $('[data-certo="0"]', caixaAvaliar).addEventListener("click", () => {
    $(".r-esperado", caixaAvaliar).hidden = false;
    $(".r-esperado textarea", caixaAvaliar).focus();
  });
  $("[data-enviar]", caixaAvaliar).addEventListener("click", () => {
    avaliar(r.id, { certo: false, esperado: $(".r-esperado textarea", caixaAvaliar).value });
    fechar();
  });
  return c;
}

async function perguntar(evento) {
  evento.preventDefault();
  const pergunta = $("#pergunta").value.trim();
  if (!pergunta) return;
  if (porAvaliar) {
    avaliar(porAvaliar, {}); // a anterior fica gravada sem avaliação
    porAvaliar = null;
  }
  const botao = $("#perguntar");
  botao.disabled = true;
  const espera = el("div", "A procurar nos artigos e a escrever a resposta… pode demorar até um minuto.", "cartao a-pensar");
  $("#respostas").prepend(espera);
  try {
    const r = await api("/api/perguntar", { pergunta, data: $("#data").value || undefined });
    espera.replaceWith(desenharResposta(r));
    porAvaliar = r.id;
    $("#pergunta").value = "";
  } catch (e) {
    espera.replaceWith(el("div", e.message, "aviso aviso-vermelho"));
  } finally {
    botao.disabled = false;
  }
}

/* ---------------------------------------------------------------- definições */

function abrirDefinicoes() {
  const sel = $("#def-provedor");
  sel.replaceChildren();
  for (const [nome, p] of Object.entries(estado.provedores)) {
    const o = el("option", nome === estado.medido.provedor ? `${p.nome} (medido)` : p.nome);
    o.value = nome;
    sel.append(o);
  }
  sel.value = estado.provedor;
  prepararModelos($("#def-modelo"), estado.provedor, estado.modelo);
  $("#def-atual").textContent = estado.com_chave ? `A usar: ${estado.descricao}.` : "Sem chave: mostra o artigo mais provável, sem resposta escrita.";
  $("#def-resultado").textContent = "";
  const d = estado.dados;
  $("#def-atualizar").hidden = !d.pode_descarregar;
  $("#def-dados").textContent = d.versao ? `Dados de ${d.versao}.` : "";
  $("#def-chave").value = "";
  $("#definicoes").showModal();
}

function prepararDefinicoes() {
  $("#abrir-definicoes").addEventListener("click", abrirDefinicoes);
  $("#def-provedor").addEventListener("change", (e) => prepararModelos($("#def-modelo"), e.target.value));
  $("#def-guardar").addEventListener("click", async () => {
    const nome = $("#def-provedor").value;
    const chave = $("#def-chave").value;
    if (!chave) {
      $("#def-resultado").textContent = "Cola a chave para a testar (a chave guardada não sai do cofre).";
      return;
    }
    if (await testarChave(nome, $("#def-modelo").value, chave, $("#def-resultado"))) {
      $("#def-chave").value = "";
      atualizarEstado();
    }
  });
  $("#def-atualizar").addEventListener("click", async () => {
    const saida = $("#def-dados");
    saida.textContent = "A procurar…";
    const r = await api("/api/dados/atualizacao", {});
    if (!r.ok) return (saida.textContent = r.mensagem);
    if (!r.nova) return (saida.textContent = "Os dados estão atualizados.");
    saida.textContent = `Há dados novos (${r.nova}). A descarregar em segundo plano: podes continuar a perguntar.`;
    await api("/api/dados/descarregar", {});
    atualizarEstado();
  });
  $("#def-apagar").addEventListener("click", async () => {
    const r = await api("/api/esquecer", { provedor: $("#def-provedor").value });
    estado = r.estado;
    $("#def-resultado").textContent = "Chave apagada deste computador.";
    atualizarEstado();
  });
}

/* ---------------------------------------------------------------- arranque */

async function arrancar() {
  prepararAssistente();
  prepararDefinicoes();
  $("#formulario").addEventListener("submit", perguntar);
  $("#pergunta").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) $("#formulario").requestSubmit();
  });
  await atualizarEstado();
  if (estado.configurado) {
    mostrarPrincipal();
  } else {
    escolhida = estado.provedor;
    desenharEscolhas();
    $("#assistente").hidden = false;
    irPara(1);
  }
}

arrancar().catch((e) => {
  document.body.append(el("div", `Não foi possível abrir: ${e.message}`, "aviso aviso-vermelho"));
});
