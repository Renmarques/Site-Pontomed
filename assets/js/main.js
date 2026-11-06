/* Precos, lista de lojas, menu e schema de ofertas. Le tudo de data.js */
(function () {
  "use strict";
  var D = window.PONTOMED, PM = window.PM;
  var SEM_PRECO = "Consulte o valor pelo WhatsApp";

  function brl(n) { var i = Number(n) % 1 === 0; return "R$ " + Number(n).toLocaleString("pt-BR", { minimumFractionDigits: i ? 0 : 2, maximumFractionDigits: 2 }); }

  /* Preco: de um modelo ou o menor entre os modelos do produto */
  function valor(prodId, modeloId, tipo, campo) {
    var p = D.produtos[prodId]; if (!p) return null;
    var lista = modeloId ? p.modelos.filter(function (m) { return m.id === modeloId; }) : p.modelos;
    var vals = lista.map(function (m) { return tipo === "venda" ? m.venda.preco : m.aluguel[campo]; })
                    .filter(function (v) { return typeof v === "number"; });
    if (!vals.length) return null;
    return { v: Math.min.apply(null, vals), aPartir: !modeloId && lista.length > 1 };
  }

  document.querySelectorAll("[data-preco]").forEach(function (el) {
    var prod = el.getAttribute("data-preco");
    var r = valor(prod, el.getAttribute("data-modelo"), el.getAttribute("data-tipo"), el.getAttribute("data-campo"));
    if (!r) { el.textContent = el.hasAttribute("data-curto") ? "Consulte" : SEM_PRECO; el.classList.add("sem-preco"); return; }
    var prefixo = (r.aPartir || el.hasAttribute("data-a-partir")) ? "a partir de " : "";
    el.textContent = prefixo + brl(r.v) + (el.getAttribute("data-sufixo") || "");
    el.classList.remove("sem-preco");
  });

  /* Lista de lojas em ordem aleatoria a cada visita (nenhuma loja em destaque) */
  document.querySelectorAll("[data-lojas-lista]").forEach(function (box) {
    PM.shuffle(D.lojas).forEach(function (l) {
      var a = document.createElement("a");
      a.className = "loja-card";
      a.href = "/loja-" + l.id;
      a.innerHTML = "<strong></strong><span class=\"loja-end\"></span><span class=\"loja-hora\"></span><span class=\"loja-tel\"></span><em>Ver loja &rarr;</em>";
      a.querySelector("strong").textContent = l.nome;
      a.querySelector(".loja-end").textContent = PM.ok(l.endereco) ? l.endereco : "Endereço: [PREENCHER]";
      a.querySelector(".loja-hora").textContent = PM.ok(l.horario) ? l.horario : "";
      a.querySelector(".loja-tel").textContent = PM.ok(l.whatsapp) ? String(l.whatsapp).replace(/^55(\d{2})(\d{5})(\d{4})$/, "($1) $2-$3") : "";
      box.appendChild(a);
    });
  });

    /* Chamada das lojas no topo da Home (ordem aleatoria) */
  document.querySelectorAll("[data-lojas-pills]").forEach(function (box) {
    box.innerHTML = "";
    PM.shuffle(D.lojas).forEach(function (l) {
      var a = document.createElement("a"); a.href = "/loja-" + l.id; a.textContent = l.nome; box.appendChild(a);
    });
  });

    /* Foto do banner: usa assets/img/hero.(webp|jpg|jpeg|png) se existir; senao fica a ilustracao */
  (function () {
    var el = document.querySelector("[data-hero-foto]"); if (!el) return;
    var nomes = ["hero.webp", "hero.jpg", "hero.jpeg", "hero.png"], i = 0;
    (function tenta() {
      if (i >= nomes.length) return;
      var im = new Image(), src = "/assets/img/" + nomes[i++];
      im.onload = function () {
        el.src = src; el.width = im.naturalWidth; el.height = im.naturalHeight; el.className = "foto";
        el.alt = "Entregador da Ponto Med entregando uma caixa a uma cliente em casa";
        var h = el.closest(".hero"); if (h) { h.classList.add("com-foto"); h.style.setProperty("--hero-foto", "url(" + src + ")"); }
      };
      im.onerror = tenta; im.src = src;
    })();
  })();

  /* Depoimentos (Home): so aparecem os que foram preenchidos com texto real */
  document.querySelectorAll("[data-depoimentos]").forEach(function (box) {
    var lista = (D.depoimentos || []);
    if (!lista.length) { box.parentNode.removeChild(box); return; }
    lista.forEach(function (d) {
      var c = document.createElement("figure"); c.className = "depo";
      c.innerHTML = '<div class="depo__est" aria-label="5 estrelas">★★★★★</div><blockquote></blockquote><figcaption></figcaption>';
      c.querySelector("blockquote").textContent = "“" + d.texto + "”";
      c.querySelector("figcaption").textContent = d.nome;
      box.appendChild(c);
    });
  });

  /* Estrelas da nota do Google: preenchimento proporcional a nota real */
  document.querySelectorAll("[data-stars]").forEach(function (e) {
    var n = parseFloat(String(D.site.avaliacaoGoogle).replace(",", "."));
    if (n > 0 && n <= 5) e.style.setProperty("--p", (n / 5 * 100) + "%"); else e.style.display = "none";
  });

  /* Abas de filtro da categoria */
  document.querySelectorAll(".abas").forEach(function (box) {
    var cards = document.querySelectorAll(".mcard[data-aba]");
    box.addEventListener("click", function (e) {
      var b = e.target.closest(".aba"); if (!b) return;
      box.querySelectorAll(".aba").forEach(function (x) { x.classList.toggle("is-on", x === b); });
      var f = b.getAttribute("data-filtro");
      cards.forEach(function (c) { c.hidden = !!f && c.getAttribute("data-aba") !== f; });
    });
  });

  /* Menu mobile */
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("menu");
  if (btn && nav) btn.addEventListener("click", function () {
    var o = nav.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", o ? "true" : "false");
  });

  document.querySelectorAll("[data-requer]").forEach(function (e) { if (!PM.ok(D.site[e.getAttribute("data-requer")])) e.style.display = "none"; });
  document.querySelectorAll("[data-ano]").forEach(function (e) { e.textContent = new Date().getFullYear(); });
  document.querySelectorAll("[data-site]").forEach(function (e) { e.textContent = D.site[e.getAttribute("data-site")]; });

  /* Paginas de loja: dados, mapa, "como chegar" e schema LocalBusiness */
  var lojaId = document.body.getAttribute("data-loja");
  var L = lojaId && PM.loja(lojaId);
  if (L) {
    var temEnd = PM.ok(L.endereco), q = encodeURIComponent(L.endereco + ", Rio de Janeiro, RJ");
    document.querySelectorAll("[data-loja-campo]").forEach(function (el) {
      var c = el.getAttribute("data-loja-campo"), v = L[c];
      if (PM.ok(v)) el.textContent = c === "whatsapp" ? String(v).replace(/^55(\d{2})(\d{5})(\d{4})$/, "($1) $2-$3") : v;
    });
    var cc = document.querySelector("[data-como-chegar]");
    if (cc && temEnd) cc.href = "https://www.google.com/maps/dir/?api=1&destination=" + q;
    var mapa = document.querySelector("[data-mapa]");
    if (mapa && temEnd) {
      mapa.className = ""; mapa.removeAttribute("style"); mapa.textContent = "";
      var f = document.createElement("iframe");
      f.src = "https://www.google.com/maps?q=" + q + "&output=embed";
      f.title = "Mapa da loja Ponto Med " + L.nome;
      f.loading = "lazy"; f.referrerPolicy = "no-referrer-when-downgrade";
      f.style.cssText = "width:100%;aspect-ratio:16/9;border:0;border-radius:16px";
      mapa.appendChild(f);
    }
    if (temEnd) {
      var s = document.createElement("script"); s.type = "application/ld+json";
      var obj = { "@context": "https://schema.org", "@type": ["MedicalBusiness", "LocalBusiness"],
        "name": "Ponto Med " + L.nome, "url": D.site.dominio + "/loja-" + L.id,
        "address": { "@type": "PostalAddress", "streetAddress": L.endereco, "addressLocality": "Rio de Janeiro", "addressRegion": "RJ", "addressCountry": "BR" },
        "parentOrganization": { "@type": "Organization", "name": "Ponto Med" } };
      obj.telephone = D.site.telefoneLink;
      obj.areaServed = D.site.areaAtendida.map(function (n) { return { "@type": "City", "name": n }; });
      obj.address.addressRegion = "RJ";
      if (L.horarioSchema) obj.openingHours = L.horarioSchema;
      s.textContent = JSON.stringify(obj); document.head.appendChild(s);
    }
  }

  /* Schema de ofertas (so quando houver preco real; evita schema invalido) */
  var prodId = document.body.getAttribute("data-produto"), modId = document.body.getAttribute("data-modelo") || null;
  var node = document.getElementById("schema-produto");
  if (prodId && node && D.produtos[prodId]) {
    var data = JSON.parse(node.textContent), offers = [];
    var v = valor(prodId, modId, "venda");
    if (v) offers.push({ "@type": "Offer", "name": "Venda", "price": v.v.toFixed(2), "priceCurrency": "BRL", "availability": "https://schema.org/InStock", "businessFunction": "http://purl.org/goodrelations/v1#Sell" });
    ["mensal"].forEach(function (c) {
      var r = valor(prodId, modId, "aluguel", c);
      if (r) offers.push({ "@type": "Offer", "name": "Aluguel " + c, "price": r.v.toFixed(2), "priceCurrency": "BRL", "availability": "https://schema.org/InStock", "businessFunction": "http://purl.org/goodrelations/v1#LeaseOut" });
    });
    if (offers.length) { data.offers = offers; node.textContent = JSON.stringify(data); }
  }
})();
