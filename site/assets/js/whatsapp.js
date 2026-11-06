/* Seletor de lojas + WhatsApp + dataLayer + UTM/gclid. Sem dependencias. */
(function () {
  "use strict";
  var D = window.PONTOMED;
  window.dataLayer = window.dataLayer || [];

  /* ---------- Atribuicao (UTM / gclid) ---------- */
  var KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "gclid", "gbraid", "wbraid"];
  var STORE = "pm_attr";
  function readAttr() { try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch (e) { return {}; } }
  function captureAttr() {
    var p = new URLSearchParams(location.search), found = {}, any = false;
    KEYS.forEach(function (k) { if (p.get(k)) { found[k] = p.get(k); any = true; } });
    if (!any) return;
    found.ts = new Date().toISOString();
    found.landing = location.pathname;
    try { localStorage.setItem(STORE, JSON.stringify(found)); } catch (e) {}
  }
  captureAttr();

  /* ---------- Utilidades ---------- */
  function shuffle(a) {
    a = a.slice();
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function ok(v) { return v && String(v).indexOf("PREENCHER") === -1; }
  function loja(id) { return D.lojas.filter(function (l) { return l.id === id; })[0]; }
  function produtoDaPagina() { return document.body.getAttribute("data-produto") || "geral"; }

  /* Mensagem pre-preenchida: curta, educada e sem citar a loja (cada loja tem o proprio botao) */
  function mensagem(l, produtoId, tipo) {
    var p = D.produtos[produtoId];
    var mn = document.body.getAttribute("data-modelo-nome");
    var inicio = "Olá! Vim pelo site e gostaria de ";
    if (!p) return inicio + "mais informações.";
    var objeto;
    if (mn) {
      var art = /a$/i.test(mn.split(" ")[0]) ? "a" : "o";   /* ex.: "a Cadeira Higiênica", "o Andador Com 4 Rodas" */
      objeto = art + " " + mn;
    } else {
      var plural = { "cadeira-de-rodas": "cadeiras de rodas", "cadeira-de-banho": "cadeiras de banho e higiênicas",
                     "botas-ortopedicas-e-imobilizadores": "botas ortopédicas e imobilizadores" };
      objeto = plural[produtoId] || p.nome.toLowerCase();    /* ex.: "cadeiras de rodas", "muletas" */
    }
    if (tipo === "aluguel") return inicio + "alugar " + objeto + ".";
    if (tipo === "venda") return inicio + "comprar " + objeto + ".";
    return inicio + "mais informações sobre " + objeto + ".";
  }
  function waUrl(l, produtoId, tipo) {
    return "https://wa.me/" + (ok(l.whatsapp) ? l.whatsapp : "") + "?text=" + encodeURIComponent(mensagem(l, produtoId, tipo));
  }

  function push(evento, extra) {
    var a = readAttr();
    var obj = { event: evento, pagina_origem: location.pathname };
    var mod = document.body.getAttribute("data-modelo"); if (mod) obj.modelo = mod;
    for (var k in extra) obj[k] = extra[k];
    KEYS.forEach(function (key) { if (a[key]) obj[key] = a[key]; });
    window.dataLayer.push(obj);
  }
  window.PMTrack = push;

  /* ---------- Modal seletor de lojas ---------- */
  var dlg, listEl, titleEl, ctx = {};

  function build() {
    dlg = document.createElement("dialog");
    dlg.className = "wa-modal";
    dlg.setAttribute("aria-labelledby", "wa-title");
    dlg.innerHTML =
      '<form method="dialog" class="wa-modal__close"><button aria-label="Fechar">&times;</button></form>' +
      '<h2 id="wa-title"></h2>' +
      '<p class="wa-modal__sub">Escolha a loja mais próxima de você. Você será levado ao WhatsApp dela.</p>' +
      '<ul class="wa-modal__list"></ul>';
    document.body.appendChild(dlg);
    listEl = dlg.querySelector("ul");
    titleEl = dlg.querySelector("h2");
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }

  function open(produtoId, tipo) {
    if (!dlg) build();
    ctx = { produto: produtoId, tipo: tipo };
    var verbo = tipo === "aluguel" ? "alugar" : tipo === "venda" ? "comprar" : "falar com a gente";
    titleEl.textContent = "Qual loja fica mais perto de você?";
    dlg.querySelector(".wa-modal__sub").textContent =
      "Escolha a loja mais próxima para " + verbo + ". Você será levado ao WhatsApp dela.";
    listEl.innerHTML = "";
    shuffle(D.lojas).forEach(function (l) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.className = "wa-modal__loja";
      a.href = waUrl(l, produtoId, tipo);
      a.target = "_blank"; a.rel = "noopener";
      a.innerHTML = "<strong></strong><span></span>";
      a.querySelector("strong").textContent = l.nome;
      a.querySelector("span").textContent = ok(l.endereco) ? l.endereco : "Endereço: [PREENCHER]";
      a.addEventListener("click", function () {
        push("whatsapp_click", { loja: l.id, produto: produtoId, tipo: tipo === "aluguel" || tipo === "venda" ? tipo : "informacao" });
        setTimeout(function () { dlg.close(); }, 200);
      });
      li.appendChild(a); listEl.appendChild(li);
    });
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
  }

  /* Cliques: [data-wa] abre seletor; [data-wa-loja] vai direto para a loja */
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-wa],[data-wa-loja],[data-track]");
    if (!t) return;
    if (t.hasAttribute("data-wa")) {
      e.preventDefault();
      open(t.getAttribute("data-produto") || produtoDaPagina(), t.getAttribute("data-tipo") || "duvida");
    } else if (t.hasAttribute("data-wa-loja")) {
      e.preventDefault();
      var l = loja(t.getAttribute("data-wa-loja"));
      var pr = t.getAttribute("data-produto") || produtoDaPagina();
      var tp = t.getAttribute("data-tipo") || "duvida";
      push("whatsapp_click", { loja: l.id, produto: pr, tipo: tp === "aluguel" || tp === "venda" ? tp : "informacao" });
      window.open(waUrl(l, pr, tp), "_blank", "noopener");
    } else {
      var kind = t.getAttribute("data-track");
      push(kind === "telefone" ? "telefone_click" : "como_chegar_click", { loja: t.getAttribute("data-loja") || "geral" });
    }
  });

  /* Botao flutuante em todas as paginas */
  var fab = document.createElement("button");
  fab.className = "wa-fab";
  fab.setAttribute("data-wa", "");
  fab.setAttribute("data-tipo", "duvida");
  fab.setAttribute("aria-label", "Falar pelo WhatsApp");
  fab.innerHTML = '<svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true"><path fill="currentColor" d="M16 3C9 3 3.4 8.6 3.4 15.5c0 2.3.6 4.4 1.7 6.3L3 29l7.4-1.9c1.8 1 3.800 1.500 5.600 1.500 7 0 12.600-5.600 12.600-12.500S23 3 16 3zm0 22.800c-1.800 0-3.500-.5-5-1.400l-.4-.2-4.400 1.100 1.200-4.300-.3-.4a10 10 0 0 1-1.500-5.400C5.600 10 10.300 5.400 16 5.400s10.400 4.600 10.400 10.100S21.700 25.800 16 25.800zm5.700-7.500c-.3-.2-1.800-.9-2.100-1s-.5-.2-.7.200-.8 1-1 1.200-.4.200-.7.100a8.300 8.300 0 0 1-4.100-3.600c-.3-.5.300-.5.900-1.600.1-.2 0-.4 0-.5l-1-2.300c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.100-.8.400s-1 1-1 2.500 1.100 2.900 1.200 3.100 2.100 3.300 5.100 4.500c1.900.8 2.600.9 3.600.7.600-.1 1.800-.7 2-1.400s.3-1.300.2-1.400-.3-.2-.6-.4z"/></svg><span>WhatsApp</span>';
  document.body.appendChild(fab);

  window.PM = { shuffle: shuffle, ok: ok, loja: loja, open: open };
})();
