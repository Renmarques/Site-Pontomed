# Site Ponto Med

Site de aluguel e venda de equipamentos de mobilidade no Rio de Janeiro. Ninguém compra pelo site: todo botão leva ao WhatsApp da loja escolhida.

O site é estático (HTML, CSS e JavaScript puros). As páginas são **geradas** a partir de arquivos simples na pasta `dados/`. Você edita os dados e roda um comando.

## Como o projeto está organizado

```
dados/                  ← AQUI você edita (produtos, preços, lojas, textos)
  produtos.json         ← todos os produtos, com preço, foto e descrição
  lojas.json            ← as 4 lojas: endereço, WhatsApp, horário
  site.json             ← telefone, razão social, avaliações, depoimentos, GTM, domínio
  categorias.json       ← textos de cada categoria (título, descrição, perguntas frequentes)
ferramentas/
  gerar_site.py         ← o gerador (normalmente não precisa mexer)
build.py                ← comando que gera o site
site/                   ← o site pronto. É o que vai ao ar
  assets/css, js, img   ← estilo, scripts, logo e foto do topo
```

> **Não edite as páginas dentro de `site/` nem o `site/assets/js/data.js` à mão.** Eles são gerados e seriam sobrescritos na próxima geração.

## Gerar o site

Precisa só do Python 3 instalado. Na pasta do projeto:

```bash
python build.py
```

Isso recria todas as páginas em `site/`. Para ver no computador:

```bash
python -m http.server 8765 --directory site
```

e abra http://localhost:8765.

## Mexer em produtos (`dados/produtos.json`)

Cada categoria é uma lista de produtos. Exemplo de um produto:

```json
{
  "id": "start-c1",
  "nome": "Cadeira de Rodas Dobrável Start C1 Ottobock",
  "aba": "Dobráveis",
  "img": "https://.../foto.png",
  "destaques": ["Estrutura leve em alumínio aeronáutico", "Dobramento rápido em duplo X"],
  "peso": "até 125 kg",
  "aluguel": 600,
  "venda": 12100,
  "descricao": "Texto que aparece em 'Descrição do produto'.",
  "contain": false
}
```

| Campo | O que é |
|---|---|
| `id` | Nome curto e único, sem acento nem espaço (vira o endereço: `/cadeira-de-rodas/start-c1`). |
| `nome` | Nome que aparece no site e na mensagem do WhatsApp. |
| `aba` | Aba de filtro na lista da categoria. Escreva igual em produtos do mesmo tipo (ex.: `Dobráveis`). Se todos tiverem a mesma aba, as abas não aparecem. |
| `img` | Endereço da foto. Ideal: baixar a foto, converter para WebP e salvar em `site/assets/img/produtos/`, usando `/assets/img/produtos/nome.webp`. |
| `destaques` | Até 3 frases curtas, aparecem no card do produto. |
| `peso` | Peso suportado (ex.: `"até 125 kg"`). Use `null` se não souber: a linha some. |
| `aluguel` | Preço do aluguel **por mês**, só o número (`600`). Use `null` se ainda não tem: aparece "Consulte". |
| `venda` | Preço de venda, só o número (`12100`). Use `null` para "Consulte". |
| `descricao` | Parágrafo da página do produto. |
| `contain` | `true` só para fotos sem fundo azul (PNG transparente ou fundo branco). |

- **Adicionar produto:** copie um bloco, mude os campos e cole na lista da categoria certa. Ao gerar, a página do produto, o card, o sitemap e os preços são criados sozinhos.
- **Remover produto:** apague o bloco. A página dele é apagada na próxima geração.
- **Mudar preço:** troque o número em `aluguel` ou `venda`.
- **Ordem:** a ordem da lista é a ordem na página.
- Os preços aparecem no site assim: aluguel por mês e venda. Não existe aluguel por dia ou semana.

## Lojas, telefone, avaliações e depoimentos

- **Lojas** (`dados/lojas.json`): endereço, WhatsApp (só números, com 55 e DDD), horário e o texto de apresentação de cada loja.
- **Telefone, razão social, CNPJ, nota e quantidade de avaliações** (`dados/site.json`).
- **Depoimentos** (`dados/site.json`, lista `depoimentos`): hoje são **genéricos e temporários**. Troque por avaliações reais do Google (nome e texto). Para esconder a seção, deixe a lista vazia `[]`.
- **Anos de mercado:** preencha `anosDeMercado` em `site.json` (ex.: `"12"`). Enquanto estiver vazio, não aparece.

## Antes de divulgar (lançamento)

1. **Domínio:** em `site.json`, troque `dominio` pelo endereço final. Também troque `seudominio.com.br` no arquivo `site/.htaccess` (só vale na Hostinger).
2. **GTM:** em `site.json`, troque `gtmId` pelo seu ID do Google Tag Manager.
3. **Indexação:** `indexar: true` deixa o Google listar o site. Para uma **prévia que o cliente vê** sem aparecer no Google, use `indexar: false`, e volte para `true` no lançamento.
4. **Imagem de compartilhamento:** salve uma imagem 1200×630 em `site/assets/img/og.jpg`.
5. **Política de privacidade:** a página foi retirada. O Google Ads exige uma, então crie `politica-de-privacidade` antes de anunciar.
6. **Fotos dos produtos:** vêm dos sites antigos (pontomed.com e loja da cama). Baixe e hospede no próprio site antes de tirar os sites antigos do ar.

## Publicar para o cliente ver

O site usa caminhos a partir da raiz (`/assets/...`). Então publique na **raiz** de um endereço:

- **Netlify, Vercel ou Cloudflare Pages** (ligados a este repositório): funcionam direto. O arquivo `netlify.toml` já diz para o Netlify rodar `python3 build.py` e publicar a pasta `site`. Assim, ao editar um `.json` no próprio site do Git, o site é gerado de novo sozinho.
- **GitHub Pages:** só funciona se o repositório se chamar `seu-usuario.github.io` ou se usar domínio próprio. Num endereço de repositório comum (`usuario.github.io/nome-do-repo`) o estilo e as imagens quebram.
- **Hostinger:** envie o conteúdo da pasta `site/` para `public_html`. O `.htaccess` cuida de HTTPS, endereços sem `.html` e página 404.

## Como o WhatsApp e o rastreamento funcionam

- Todo botão abre uma janela com as 4 lojas (ordem aleatória). Cada loja leva ao WhatsApp dela.
- A mensagem é curta e não cita a loja: "Olá! Vim pelo site e gostaria de mais informações sobre a Cadeira Higiênica." (ou só "…mais informações." quando a pessoa não veio de um produto).
- Cada clique envia um evento `whatsapp_click` para o `dataLayer` (loja, produto, modelo, tipo, página de origem, UTM e gclid), além de `telefone_click` e `como_chegar_click`.
