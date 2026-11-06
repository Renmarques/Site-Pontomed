# -*- coding: utf-8 -*-
import json, os, re, sys, shutil, datetime
from html import escape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "dados")
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "site")

def _ler(nome):
    with open(os.path.join(DADOS, nome), encoding="utf8") as f:
        return json.load(f)

INFO = _ler("site.json")
LOJAS_JSON = _ler("lojas.json")
CATEGORIAS = _ler("categorias.json")
PRODUTOS_JSON = _ler("produtos.json")

# categorias com seus modelos (a ordem do produtos.json define a ordem na pagina)
PRODUTOS = {}
for _slug, _cat in CATEGORIAS.items():
    _p = dict(_cat)
    _p["faq"] = [tuple(x) for x in _p.get("faq", [])]
    _p["modelos"] = PRODUTOS_JSON.get(_slug, [])
    for _x in _p["modelos"]:
        _x.setdefault("aba", "Todos"); _x.setdefault("peso", None); _x.setdefault("descricao", "")
        _x.setdefault("aluguel", None); _x.setdefault("venda", None); _x.setdefault("contain", False)
    PRODUTOS[_slug] = _p
LOJAS = {l["id"]: {"prep_titulo": l["prep_titulo"], "texto": l["texto"]} for l in LOJAS_JSON}
LOJA_NOMES = {l["id"]: l["nome"] for l in LOJAS_JSON}
CATALOG = {k: v["modelos"] for k, v in PRODUTOS.items()}

DOM = INFO["dominio"].rstrip("/")
HOJE = datetime.date.today().isoformat()
SEM = "Consulte o valor pelo WhatsApp"
CTA = '<a class="cta" href="#" data-wa data-tipo="duvida">Falar no WhatsApp</a>'
GTM_HEAD = """<!-- Google Tag Manager: troque GTM-XXXXXXX pelo seu ID -->
<script>window.dataLayer=window.dataLayer||[];(function(w,d,s,l,i){w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-XXXXXXX');</script>"""
GTM_BODY = '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXXX" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
SCRIPTS = '<script src="/assets/js/data.js" defer></script>\n<script src="/assets/js/whatsapp.js" defer></script>\n<script src="/assets/js/main.js" defer></script>'
SITEMAP = []
GTM_ID = INFO.get("gtmId") or "GTM-XXXXXXX"
GTM_HEAD = GTM_HEAD.replace("GTM-XXXXXXX", GTM_ID)
GTM_BODY = GTM_BODY.replace("GTM-XXXXXXX", GTM_ID)
INDEXAR = INFO.get("indexar", True)   # false = pede ao Google para NAO indexar (use na previa do cliente)

def jl(obj, attrs=""):
    return f'<script type="application/ld+json"{attrs}>\n{json.dumps(obj, ensure_ascii=False)}\n</script>'

def head(title, desc, path, og_type="website", schema="", noindex=False, canon_path=None):
    canon = DOM + (canon_path if canon_path is not None else path)
    robots = '<meta name="robots" content="noindex,follow">\n' if (noindex or not INDEXAR) else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
{GTM_HEAD}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOM}/assets/img/og.jpg">
<meta property="og:locale" content="pt_BR">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/css/style.css">
{schema}
</head>
"""

def header(full=True):
    if not full:
        return """<header class="lp-topo"><div class="wrap" style="display:flex;justify-content:space-between;align-items:center;gap:12px">
<span class="logo"><img src="/assets/img/logo.png" alt="Ponto Med" width="258" height="64" onerror="this.onerror=null;this.src='https://cdn.awsli.com.br/400x300/2495/2495914/logo/logo-bs7p6wmto9.jpg'"></span>
<a class="btn btn--ghost" href="tel:+552120426767" data-track="telefone" style="min-height:44px;padding:8px 16px">(21) 2042-6767</a>
</div></header>"""
    return f"""<header class="topo">
  <div class="wrap">
    <a class="logo" href="/"><img src="/assets/img/logo.png" alt="Ponto Med" width="258" height="64" onerror="this.onerror=null;this.src='https://cdn.awsli.com.br/400x300/2495/2495914/logo/logo-bs7p6wmto9.jpg'"></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="menu">Menu</button>
    <nav id="menu" aria-label="Principal">
      <div class="menu-item"><a href="/produtos">Produtos</a>
        <div class="submenu"><a href="/cadeira-de-rodas">Cadeira de rodas</a><a href="/muletas">Muletas</a><a href="/andadores">Andadores</a><a href="/cadeira-de-banho">Cadeira de banho</a><a href="/botas-ortopedicas-e-imobilizadores">Botas e imobilizadores</a></div></div>
      <a href="/lojas">Lojas</a>
      <a href="/#como-funciona">Como alugar</a>
      <a href="/perguntas-frequentes">Dúvidas</a>
      {CTA}
    </nav>
  </div>
</header>"""

FOOTER = """<footer class="rodape">
  <div class="wrap cols">
    <div><h3>Ponto Med</h3><p>Aluguel e venda de materiais hospitalares no Rio de Janeiro.</p><p>Tel.: <a href="tel:+552120426767" data-track="telefone">(21) 2042-6767</a></p></div>
    <div><h3>Produtos</h3><ul><li><a href="/cadeira-de-rodas">Cadeira de rodas</a></li><li><a href="/muletas">Muletas</a></li><li><a href="/andadores">Andadores</a></li><li><a href="/cadeira-de-banho">Cadeira de banho</a></li><li><a href="/botas-ortopedicas-e-imobilizadores">Botas e imobilizadores</a></li></ul></div>
    <div><h3>Lojas</h3><ul><li><a href="/loja-leblon">Leblon</a></li><li><a href="/loja-gavea">Gávea</a></li><li><a href="/loja-copacabana">Copacabana</a></li><li><a href="/loja-laranjeiras">Laranjeiras</a></li></ul></div>
    <div><h3>Institucional</h3><ul><li><a href="/perguntas-frequentes">Perguntas frequentes</a></li></ul></div>
  </div>
  <div class="wrap"><p>© <span data-ano></span> Ponto Med. Todos os direitos reservados. <span data-site="razaoSocial"></span> · CNPJ <span data-site="cnpj"></span></p></div>
</footer>"""

def crumbs(items):
    lis = "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in items[:-1]) + f'<li aria-current="page">{items[-1][0]}</li>'
    return f'<div class="crumbs-bar"><div class="wrap"><nav class="crumbs" aria-label="Você está em"><ol>{lis}</ol></nav></div></div>'

def bc_schema(items):
    return jl({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":DOM+u} for i,(n,u) in enumerate(items)]})

def faq_schema(faq):
    return jl({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]})

def faq_html(faq):
    return "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q,a in faq)

def page(path, title, desc, body, schema="", full=True, noindex=False, canon_path=None, body_attr="", og_type="website", sitemap=True, priority="0.7"):
    html = head(title, desc, path, og_type, schema, noindex, canon_path) + f"<body{(' '+body_attr) if body_attr else ''}>\n{GTM_BODY}\n"
    html += '<a class="skip" href="#conteudo">Ir para o conteúdo</a>\n' + header(full) + f'\n<main id="conteudo">\n{body}\n</main>\n'
    html += (FOOTER if full else '<footer class="rodape"><div class="wrap"><p>© <span data-ano></span> Ponto Med</p></div></footer>') + f"\n{SCRIPTS}\n</body>\n</html>\n"
    out = os.path.join(SITE, path.strip("/"), "index.html") if path != "/" else os.path.join(SITE, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(html)
    if sitemap and not noindex:
        SITEMAP.append((path, priority))

def preco(slug, tipo, campo=None, modelo=None, apartir=True):
    a = f' data-modelo="{modelo}"' if modelo else ""
    c = f' data-campo="{campo}"' if campo else ""
    p = " data-a-partir" if (apartir and not modelo and (tipo == "venda" or campo)) else ""
    return f'<span data-preco="{slug}"{a} data-tipo="{tipo}"{c}{p}>{SEM}</span>'

def preco_c(slug, tipo, campo=None, modelo=None):
    return preco(slug, tipo, campo, modelo, apartir=False).replace("<span ", '<span data-curto ', 1)

def pcard_resumo(slug, p):
    """Cartao de categoria (Home e /produtos): foto, nome e quantidade de modelos. Sem preco."""
    n = len(p["modelos"])
    return f"""      <a class="tile" href="/{slug}">
        <div class="tile__img{' img-contain' if p['modelos'][0].get('contain') else ''}"><img src="{p['modelos'][0]['img']}" alt="{p['nome']}: aluguel e venda" width="400" height="400" loading="lazy"></div>
        <h3>{p['nome']}</h3>
        <span class="tile__go">{n} modelo{'s' if n > 1 else ''} <b>&rarr;</b></span>
      </a>"""

def mcard(slug, x):
    """Cartao de modelo: foto, nome e precos em destaque. O cartao inteiro e um link."""
    al = preco_c(slug,'aluguel','mensal',x['id'])
    return f"""      <a class="mcard" href="/{slug}/{x['id']}" data-aba="{x['aba']}">
        <span class="mcard__img{' img-contain' if x.get('contain') else ''}"><img src="{x['img']}" alt="{x['nome']}" width="400" height="400" loading="lazy"></span>
        <h3>{x['nome']}</h3>
        <span class="mcard__precos">
          <span class="mcard__preco mcard__preco--a"><small>Aluguel/mês</small>{al}</span>
          <span class="mcard__preco"><small>Venda</small>{preco_c(slug,'venda',None,x['id'])}</span>
        </span>
      </a>"""

def _num(v):
    return "null" if v is None else json.dumps(v)

def escrever_data_js():
    """Gera assets/js/data.js a partir de dados/*.json (nao edite o data.js a mao)."""
    site = {k: v for k, v in INFO.items() if k != "depoimentos"}
    lojas = [{k: l.get(k) for k in ("id", "nome", "prep", "endereco", "whatsapp", "horario", "horarioSchema", "nota", "avaliacoes")} for l in LOJAS_JSON]
    produtos = {}
    for slug, p in PRODUTOS.items():
        produtos[slug] = {"nome": p["nome"], "modelos": [
            {"id": x["id"], "nome": x["nome"], "aluguel": {"mensal": x["aluguel"]}, "venda": {"preco": x["venda"]}} for x in p["modelos"]]}
    corpo = "window.PONTOMED = " + json.dumps({"site": site, "depoimentos": INFO.get("depoimentos", []), "lojas": lojas, "produtos": produtos}, ensure_ascii=False, indent=2) + ";\n"
    cab = "/* ARQUIVO GERADO por ferramentas/gerar_site.py a partir de dados/*.json. NAO EDITE AQUI: edite os arquivos da pasta dados/ e rode: python build.py */\n"
    os.makedirs(os.path.join(SITE, "assets", "js"), exist_ok=True)
    with open(os.path.join(SITE, "assets", "js", "data.js"), "w", encoding="utf8", newline="\n") as f:
        f.write(cab + corpo)

escrever_data_js()

def lojas_grid():
    return '<div class="grid" data-lojas-lista></div>'


def catbar(atual):
    itens = ""
    for s, p in sorted(PRODUTOS.items(), key=lambda kv: kv[1]["ordem"]):
        on = ' class="is-on" aria-current="page"' if s == atual else ""
        x0 = p["modelos"][0]
        itens += f'<a href="/{s}"{on}><img src="{x0["img"]}" alt="" width="36" height="36" loading="lazy"><span>{p["nome"].replace("Botas ortopédicas e imobilizadores","Botas e imobilizadores")}</span></a>'
    return f'<nav class="catbar" aria-label="Categorias de produtos"><div class="wrap">{itens}</div></nav>'

def produto_page(slug, p):
    path = "/" + slug
    crumb = [("Início","/"),("Produtos","/produtos"),(p["nome"],path)]
    nome_l = p["nome"].lower()
    schema = jl({"@context":"https://schema.org","@type":"Product","name":p["nome"],"description":p["desc"],"brand":{"@type":"Organization","name":"Ponto Med"},"url":DOM+path}, ' id="schema-produto"') \
             + "\n" + bc_schema(crumb) + "\n" + faq_schema(p["faq"])
    modelos = chr(10).join(mcard(slug, x) for x in p["modelos"])
    _abas = []
    for _x in p["modelos"]:
        if _x["aba"] not in _abas: _abas.append(_x["aba"])
    if len(_abas) > 1:
        abas = '    <div class="abas" role="group" aria-label="Filtrar modelos"><button type="button" class="aba is-on" data-filtro="">Todos</button>' + "".join(f'<button type="button" class="aba" data-filtro="{a}">{a}</button>' for a in _abas) + '</div>'
    else:
        abas = ""
    body = f"""{crumbs(crumb)}
{catbar(slug)}
<section id="modelos" class="primeira">
  <div class="wrap">
    <div class="sec-head"><h1>{p['modelos_h2']}</h1><p class="lead">{p['modelos_p']}</p></div>
{abas}
    <div class="grid grid--modelos">
{modelos}
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="sec-head"><h2>Aluguel e venda de {nome_l} perto de você</h2>
      <p class="lead">Você pode alugar ou comprar em qualquer uma das nossas lojas.</p></div>
    {lojas_grid()}
  </div>
</section>

<section>
  <div class="wrap" style="max-width:820px">
    <div class="sec-head"><h2>Perguntas frequentes sobre {nome_l}</h2></div>
    {faq_html(p['faq'])}
  </div>
</section>"""
    page(path, p["title"], p["desc"], body, schema, body_attr=f'data-produto="{slug}"', og_type="product", priority="0.9")

def lp_page(slug, p):
    lp = p["lp"]; path = f"/lp/{slug}"
    nome_l = p["nome"].lower()
    ben = "".join(f"<li>{b}</li>" for b in lp["beneficios"])
    faq = p["faq"][:3]
    body = f"""<section class="hero">
  <div class="wrap">
    <h1>{lp['h1']}</h1>
    <p>{lp['sub']}</p>
    <ul class="selos">{''.join(f'<li>{b}</li>' for b in lp['beneficios'])}</ul>
    <div class="hero-cta">
      <button class="btn btn--branco" data-wa data-tipo="aluguel">Alugar pelo WhatsApp</button>
      <button class="btn btn--branco" data-wa data-tipo="venda">Comprar pelo WhatsApp</button>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="duo">
      <article class="bloco bloco--aluguel">
        <header>Aluguel</header>
        <div class="corpo">
          <h2>{p['h2a']}</h2>
          <ul class="precos">
            <li>Mensal {preco(slug,'aluguel','mensal')}</li>
          </ul>
          <button class="btn btn--aluguel btn--block" data-wa data-tipo="aluguel">Alugar pelo WhatsApp</button>
        </div>
      </article>
      <article class="bloco bloco--venda">
        <header>Venda</header>
        <div class="corpo">
          <h2>{p['h2v']}</h2>
          <p class="preco-grande">{preco(slug,'venda')}</p>
          <button class="btn btn--venda btn--block" data-wa data-tipo="venda">Comprar pelo WhatsApp</button>
        </div>
      </article>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Como funciona</h2>
    <ol class="passos">
      <li><h3>Chame no WhatsApp</h3><p>Escolha a loja mais próxima e a mensagem já vai pronta.</p></li>
      <li><h3>Confirme o modelo</h3><p>Nossa equipe indica o modelo certo e passa os valores.</p></li>
      <li><h3>Retire ou receba</h3><p>Combine a retirada na loja ou a entrega.</p></li>
    </ol>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <h2>Dúvidas rápidas</h2>
    {faq_html(faq)}
  </div>
</section>

<section class="cta-final">
  <div class="wrap">
    <h2>Fale agora com a loja mais próxima</h2>
    <p>Leblon, Gávea, Copacabana e Laranjeiras.</p>
    <div class="hero-cta" style="justify-content:center">
      <button class="btn btn--branco" data-wa data-tipo="aluguel">Alugar pelo WhatsApp</button>
      <button class="btn btn--branco" data-wa data-tipo="venda">Comprar pelo WhatsApp</button>
    </div>
  </div>
</section>"""
    title = f"{lp['h1']} | Ponto Med"
    page(path, title, lp["sub"], body, full=False, noindex=True, canon_path="/"+slug, body_attr=f'data-produto="{slug}"')

def loja_page(lid, info):
    nome = LOJA_NOMES[lid]; path = f"/loja-{lid}"
    _L = next(l for l in LOJAS_JSON if l["id"] == lid)
    _tel = re.sub(r"^55(\d{2})(\d{5})(\d{4})$", r"(\1) \2-\3", str(_L["whatsapp"]))
    crumb = [("Início","/"),("Lojas","/lojas"),(f"Loja {nome}",path)]
    title = f"Materiais Hospitalares {info['prep_titulo']}: Aluguel e Venda | Ponto Med"
    desc = f"Loja Ponto Med {info['prep_titulo']}: aluguel e venda de cadeira de rodas, muletas, andadores e mais. Endereço, horário, mapa e WhatsApp da loja."
    prods = ""
    for slug, p in sorted(PRODUTOS.items(), key=lambda kv: kv[1]["ordem"]):
        prods += f"""      <article class="pcard"><div class="info">
        <h3><a href="/{slug}">{p['nome']}</a></h3>
        <p>{p['card_desc']}</p>
        <div class="acoes">
          <button class="btn btn--aluguel btn--block" data-wa-loja="{lid}" data-produto="{slug}" data-tipo="aluguel">Alugar na loja {nome}</button>
          <button class="btn btn--venda btn--block" data-wa-loja="{lid}" data-produto="{slug}" data-tipo="venda">Comprar na loja {nome}</button>
        </div></div></article>
"""
    outras = " · ".join(f'<a href="/loja-{k}">{v}</a>' for k, v in LOJA_NOMES.items() if k != lid)
    body = f"""{crumbs(crumb)}
<section class="hero-soft">
  <div class="wrap loja-topo">
    <div>
      <h1>Materiais hospitalares {info['prep_titulo']}: aluguel e venda</h1>
      <p>{info['texto']}</p>
    </div>
    <div class="card" style="border:3px solid var(--marca);border-radius:16px;padding:24px">
      <h2 style="font-size:1.4rem">Loja {nome}</h2>
      <p><strong>Endereço:</strong> <span data-loja-campo="endereco">{_L["endereco"]}</span></p>
      <p><strong>Horário:</strong> <span data-loja-campo="horario">{_L["horario"]}</span></p>
      <p><strong>WhatsApp da loja:</strong> <span data-loja-campo="whatsapp">{_tel}</span></p>
      <p><strong>Telefone:</strong> <a href="tel:+552120426767" data-track="telefone" data-loja="{lid}">(21) 2042-6767</a></p>
      <div style="display:grid;gap:10px;margin-top:14px">
        <button class="btn btn--block" data-wa-loja="{lid}" data-tipo="duvida">Falar com a loja {nome} no WhatsApp</button>
        <a class="btn btn--ghost btn--block" data-como-chegar href="https://www.google.com/maps/search/?api=1&query=Ponto+Med+{nome}+Rio+de+Janeiro" target="_blank" rel="noopener" data-track="como-chegar" data-loja="{lid}">Como chegar</a>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <h2>Mapa da loja {nome}</h2>
    <div data-mapa class="ph" style="aspect-ratio:16/9">[MAPA DO GOOGLE: aparece quando o endereço for preenchido em data.js]</div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>Alugar ou comprar na loja {nome}</h2>
    <p>Escolha o produto e fale direto com a loja {nome}. A mensagem já vai pronta.</p>
    <div class="grid">
{prods}    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <h2>Outras lojas</h2>
    <p>{outras}</p>
    <p><a href="/lojas">Ver todas as lojas</a></p>
  </div>
</section>"""
    page(path, title, desc, body, bc_schema(crumb), body_attr=f'data-loja="{lid}"', priority="0.8")

def institucionais():
    # produtos hub
    cards = "\n".join(pcard_resumo(s, p) for s, p in sorted(PRODUTOS.items(), key=lambda kv: kv[1]["ordem"]))
    crumb = [("Início","/"),("Produtos","/produtos")]
    body = f"""{crumbs(crumb)}
<section class="hero-soft"><div class="wrap">
<h1>Produtos de mobilidade: aluguel e venda no Rio de Janeiro</h1>
<p class="lead">Cadeira de rodas, muletas, andadores, cadeira de banho e botas ortopédicas. Em cada página você compara aluguel e venda e chama a loja mais próxima no WhatsApp.</p>
<div class="tiles" style="margin-top:24px">
{cards}
</div></div></section>"""
    page("/produtos","Produtos de Mobilidade: Aluguel e Venda no RJ | Ponto Med","Cadeira de rodas, muletas, andadores, cadeira de banho e botas ortopédicas para alugar ou comprar no Rio de Janeiro. Veja e fale pelo WhatsApp.",body,bc_schema(crumb),priority="0.9")

    # lojas hub
    crumb = [("Início","/"),("Lojas","/lojas")]
    body = f"""{crumbs(crumb)}
<section class="hero-soft"><div class="wrap">
<h1>Lojas Ponto Med no Rio de Janeiro</h1>
<p class="lead">São 4 lojas: Leblon, Gávea, Copacabana e Laranjeiras. Escolha a mais próxima de você, veja endereço, horário e fale direto no WhatsApp da loja.</p>
{lojas_grid()}
</div></section>"""
    page("/lojas","4 Lojas de Materiais Hospitalares no Rio de Janeiro | Ponto Med","Lojas Ponto Med no Leblon, Gávea, Copacabana e Laranjeiras. Aluguel e venda de cadeira de rodas, muletas e andadores. Escolha a mais próxima.",body,bc_schema(crumb),priority="0.9")

    # faq geral
    faq = [
     ("Vale mais a pena alugar ou comprar?","Alugar costuma compensar quando o uso é temporário, como em recuperação de cirurgia ou fratura. Comprar compensa quando o uso é de longo prazo ou permanente."),
     ("O aluguel é por quanto tempo?","O aluguel é mensal. Consulte valores e condições no WhatsApp da loja."),
     ("Preciso de documentos para alugar?","A loja informa os documentos necessários pelo WhatsApp."),
     ("Como escolho a loja?","Escolha a mais próxima de você. Ao clicar em qualquer botão de WhatsApp, você vê as 4 lojas e seleciona a que preferir."),
     ("O site vende ou aluga direto?","Não. O site mostra produtos e valores, e o pedido é feito pelo WhatsApp da loja escolhida."),
     ("Vocês entregam?","Informamos as condições de entrega pelo WhatsApp da loja escolhida."),
     ("Posso comprar depois de alugar?","Consulte as condições no WhatsApp da loja."),
     ("Quais produtos vocês oferecem?","Cadeira de rodas, muletas, andadores, cadeira de banho e botas ortopédicas e imobilizadores, para aluguel e venda."),
     ("Quais lojas vocês têm?","Leblon, Gávea, Copacabana e Laranjeiras, no Rio de Janeiro."),
     ("Como peço valores?","Os valores aparecem nas páginas dos produtos. Quando houver dúvida, chame a loja pelo WhatsApp.")]
    crumb = [("Início","/"),("Perguntas frequentes","/perguntas-frequentes")]
    body = f"""{crumbs(crumb)}
<section class="hero-soft"><div class="wrap">
<h1>Perguntas frequentes sobre aluguel e venda</h1>
{faq_html(faq)}
<p style="margin-top:20px"><button class="btn" data-wa data-tipo="duvida">Tirar dúvidas no WhatsApp</button></p>
</div></section>"""
    page("/perguntas-frequentes","Dúvidas sobre Aluguel e Compra de Equipamentos | Ponto Med","Respostas rápidas sobre aluguel e compra de cadeira de rodas, muletas e andadores no Rio de Janeiro: prazos, lojas, entrega e valores.",body,bc_schema(crumb)+"\n"+faq_schema(faq),priority="0.7")

    # 404
    body = """<section><div class="wrap centro">
<h1>Página não encontrada</h1>
<p class="lead">Não encontramos o endereço que você digitou. Veja os produtos ou fale com a loja mais próxima.</p>
<div class="hero-cta" style="justify-content:center">
<a class="btn btn--ghost" href="/produtos">Ver produtos</a>
<button class="btn" data-wa data-tipo="duvida">Falar pelo WhatsApp</button>
</div></div></section>"""
    page("/404","Página não encontrada | Ponto Med","Página não encontrada.",body,noindex=True,sitemap=False)


def home_page():
    cards = chr(10).join(pcard_resumo(s, p) for s, p in sorted(PRODUTOS.items(), key=lambda kv: kv[1]["ordem"]))
    area = [{"@type":"City","name":"Rio de Janeiro"}]
    schema = jl({"@context":"https://schema.org","@graph":[
        {"@type":"Organization","@id":DOM+"/#org","name":"Ponto Med","url":DOM+"/","logo":DOM+"/assets/img/logo.png","telephone":"+552120426767","areaServed":area},
        {"@type":"WebSite","url":DOM+"/","name":"Ponto Med"}]})
    body = f"""<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <h1>Aluguel e venda de equipamentos de mobilidade no Rio de Janeiro</h1>
      <p class="lead">Cadeira de rodas, muletas, andadores e muito mais. Escolha entre alugar ou comprar e fale direto no WhatsApp com a loja mais perto de você.</p>
      <div class="hero-cta">
        <button class="btn" data-wa data-tipo="duvida">Falar pelo WhatsApp</button>
        <a class="btn btn--ghost" href="#produtos">Ver produtos</a>
      </div>
      <div class="hero-lojas">
        <span class="hero-lojas__titulo">Atendemos perto de você:</span>
        <div class="hero-lojas__lista" data-lojas-pills>
          <noscript><a href="/loja-copacabana">Copacabana</a><a href="/loja-gavea">Gávea</a><a href="/loja-laranjeiras">Laranjeiras</a><a href="/loja-leblon">Leblon</a></noscript>
        </div>
      </div>
    </div>
    <div class="hero-art"><img data-hero-foto src="/assets/img/hero-ilustracao.svg" alt="Atendente da Ponto Med entregando uma caixa a uma senhora em cadeira de rodas" width="560" height="460"></div>
  </div>
</section>

<section id="produtos">
  <div class="wrap">
    <div class="sec-head"><span class="tag">Nossos produtos</span>
      <h2>O que você procura?</h2>
      <p class="lead">Escolha uma categoria para ver todos os modelos disponíveis para aluguel e venda.</p></div>
    <div class="tiles">
{cards}
    </div>
  </div>
</section>

<section id="lojas" class="alt">
  <div class="wrap">
    <div class="sec-head"><span class="tag">Nossas lojas</span><h2>Onde estamos</h2>
      <p class="lead">Escolha a loja mais perto de você e fale direto no WhatsApp dela.</p></div>
    {lojas_grid()}
  </div>
</section>

<section id="como-funciona">
  <div class="wrap">
    <div class="sec-head"><span class="tag">Passo a passo</span><h2>Como funciona</h2></div>
    <ol class="passos">
      <li><h3>Escolha o produto</h3><p>Veja modelos e valores de aluguel e de venda.</p></li>
      <li><h3>Chame no WhatsApp</h3><p>Selecione a loja mais próxima e a mensagem já vai pronta.</p></li>
      <li><h3>Retire ou receba</h3><p>Combine a retirada na loja ou a entrega com a equipe.</p></li>
      <li><h3>Use e devolva</h3><p>No aluguel, a devolução é combinada com a loja.</p></li>
    </ol>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="sec-head"><h2>Quem confia na Ponto Med</h2>
      <div class="nota-card"><strong class="nota-card__num" data-site="avaliacaoGoogle"></strong><div class="nota-card__info"><span class="stars" data-stars aria-hidden="true">★★★★★</span><span class="nota-card__txt">Mais de <b>100</b> avaliações no Google</span></div></div></div>
    <div class="depos" data-depoimentos></div>
  </div>
</section>

<section>
  <div class="wrap" style="max-width:820px">
    <div class="sec-head"><h2>Dúvidas rápidas</h2></div>
    <details><summary>O aluguel é por quanto tempo?</summary><p>O aluguel é mensal. Fale com a loja pelo WhatsApp para combinar o período e a renovação.</p></details>
    <details><summary>Vocês entregam o equipamento em casa?</summary><p>Informamos as condições de entrega pelo WhatsApp, de acordo com o seu endereço e com a loja mais próxima.</p></details>
    <details><summary>Preciso de documentos para alugar?</summary><p>A loja informa pelo WhatsApp quais documentos são necessários para fazer o aluguel.</p></details>
    <details><summary>Como escolho o modelo certo para mim?</summary><p>Nossa equipe orienta você pelo WhatsApp, considerando o uso, o peso e o espaço onde o equipamento vai ficar.</p></details>
    <p class="centro"><a href="/perguntas-frequentes">Ver todas as perguntas &rarr;</a></p>
  </div>
</section>

<section class="cta-final">
  <div class="wrap">
    <h2>Fale agora com a loja mais próxima</h2>
    <p>Atendimento rápido pelo WhatsApp.</p>
    <button class="btn btn--branco" data-wa data-tipo="duvida">Falar pelo WhatsApp</button>
  </div>
</section>"""
    page("/", "Aluguel e Venda de Materiais Hospitalares no RJ | Ponto Med",
         "Alugue ou compre cadeira de rodas, muletas, andadores, cadeira de banho e botas ortopédicas no Rio de Janeiro. 4 lojas: Leblon, Gávea, Copacabana e Laranjeiras. Chame no WhatsApp.",
         body, schema, sitemap=False)


def modelo_page(slug, p, x):
    mid = x["id"]; path = f"/{slug}/{mid}"
    crumb = [("Início","/"),("Produtos","/produtos"),(p["nome"],"/"+slug),(x["nome"],path)]
    nome = x["nome"]; nome_l = nome
    checks = "".join(f"<li>{d}</li>" for d in x["destaques"])
    peso = f'<p><strong>Peso suportado:</strong> {x["peso"]}</p>' if x.get("peso") else ""
    _res = [o for o in p["modelos"] if o["id"] != mid]
    outros = sorted(_res, key=lambda o: 0 if o["aba"] == x["aba"] else 1)[:4]
    outros_html = chr(10).join(mcard(slug, o) for o in outros)
    faq = [
      (f"Posso alugar {nome_l}?", f"Sim. O aluguel é mensal. Consulte o valor e as condições no WhatsApp da loja mais próxima."),
      (f"Posso comprar {nome_l}?", "Sim. Escolha a loja mais próxima e fale direto no WhatsApp para confirmar a disponibilidade e o valor."),
      ("Como escolho a loja?", "Ao clicar em Alugar ou Comprar, você vê as lojas e escolhe a mais próxima. A mensagem já vai pronta.")]
    desc = f"{nome}: alugar ou comprar no Rio de Janeiro. {x['destaques'][0]}. Aluguel mensal e venda pelo WhatsApp. Leblon, Gávea, Copacabana e Laranjeiras."
    title = f"{nome}: Aluguel e Venda no RJ | Ponto Med"
    schema = jl({"@context":"https://schema.org","@type":"Product","name":nome,"description":f"{nome}. "+" ".join(x["destaques"]),"image":x["img"].replace("/400x400/","/800x800/"),"brand":{"@type":"Organization","name":"Ponto Med"},"category":p["nome"],"url":DOM+path}, ' id="schema-produto"') + chr(10) + bc_schema(crumb) + chr(10) + faq_schema(faq)
    desc_sec = f'''<section>
  <div class="wrap" style="max-width:860px">
    <h2>Descrição do produto</h2>
    <p>{x["descricao"]}</p>
  </div>
</section>''' if x.get("descricao") else ""
    sim_sec = f'''<section class="alt">
  <div class="wrap">
    <div class="sec-head"><h2>Produtos parecidos</h2></div>
    <div class="grid grid--modelos">
{outros_html}
    </div>
  </div>
</section>''' if outros else ""
    body = f"""{crumbs(crumb)}
<section class="hero-soft">
  <div class="wrap">
    <article class="mpage">
      <div class="mhero__img{' img-contain' if x.get('contain') else ''}"><img src="{x['img'].replace('/400x400/','/800x800/')}" alt="{nome}" width="800" height="800"></div>
      <div class="mpage__info">
        <h1>{nome}</h1>
        <ul class="checks checks--grande">{checks}</ul>
        {peso}
        <div class="mprecos">
          <div class="mprecos__a"><small>Aluguel por mês</small>{preco(slug,'aluguel','mensal',mid)}</div>
          <div><small>Venda</small>{preco(slug,'venda',None,mid)}</div>
        </div>
        <button class="btn btn--block" data-wa data-tipo="duvida">Entrar em contato pelo WhatsApp</button>
      </div>
    </article>
  </div>
</section>

{desc_sec}
{sim_sec}
<section>
  <div class="wrap">
    <h2 class="h-pequeno">Nossas lojas</h2>
    <div class="grid lojas-mini" data-lojas-lista></div>
  </div>
</section>

<section class="alt">
  <div class="wrap" style="max-width:820px">
    <h2>Perguntas frequentes</h2>
    {faq_html(faq)}
  </div>
</section>"""
    page(path, title, desc, body, schema, body_attr=f'data-produto="{slug}" data-modelo="{mid}" data-modelo-nome="{nome}"', og_type="product", priority="0.7")

for s, p in PRODUTOS.items():
    produto_page(s, p)
    for _x in p['modelos']:
        modelo_page(s, p, _x)
    if p["lp"]: lp_page(s, p)
for l, i in LOJAS.items():
    loja_page(l, i)
institucionais()
home_page()

# remove paginas de modelos que nao existem mais
import shutil
for _s, _p in PRODUTOS.items():
    _keep = {x["id"] for x in _p["modelos"]}
    _d = os.path.join(SITE, _s)
    for _n in os.listdir(_d):
        if os.path.isdir(os.path.join(_d, _n)) and _n not in _keep:
            shutil.rmtree(os.path.join(_d, _n))

# sitemap
urls = [("/","1.0")] + SITEMAP
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u, pr in urls:
    sm += f"  <url><loc>{DOM}{u}</loc><lastmod>{HOJE}</lastmod><priority>{pr}</priority></url>\n"
sm += "</urlset>\n"
open(os.path.join(SITE, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(sm)
# robots.txt
if INDEXAR:
    rb = "User-agent: *\nAllow: /\nDisallow: /lp/\n\nSitemap: " + DOM + "/sitemap.xml\n"
else:
    rb = "User-agent: *\nDisallow: /\n"
open(os.path.join(SITE, "robots.txt"), "w", encoding="utf-8", newline="\n").write(rb)
print(len(urls), "urls no sitemap")
