---
name: projgaragem
description: Vitrines de veículos para garagens pequenas, em papel, tinta e um verde profundo, com tipografia de placa e linhas finas no lugar de cartões.
colors:
  ink: "#1a1a18"
  ink-soft: "#5b5d56"
  paper: "#f2f3f1"
  paper-2: "#e7e8e3"
  line: "#d3d5ce"
  accent: "#0f5c4d"
  accent-ink: "#f2f3f1"
  warn: "#b8842b"
  danger: "#a23b2e"
typography:
  display:
    fontFamily: "Big Shoulders, sans-serif"
    fontSize: "clamp(3rem, 7.4vw, 6rem)"
    fontWeight: 800
    lineHeight: 0.95
    letterSpacing: "0"
  headline:
    fontFamily: "Big Shoulders, sans-serif"
    fontSize: "clamp(2rem, 4.5vw, 3.25rem)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.01em"
  title:
    fontFamily: "Big Shoulders, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "0.01em"
  body:
    fontFamily: "Public Sans, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "IBM Plex Mono, monospace"
    fontSize: "0.75rem"
    fontWeight: 600
    letterSpacing: "0.04em"
rounded:
  sm: "2px"
  phone: "40px"
  phone-mini: "24px"
spacing:
  sm: "0.5rem"
  md: "1.25rem"
  lg: "2.5rem"
  section: "5rem"
components:
  button-accent:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.sm}"
  button-outline-ink:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
  button-landing:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0.85rem 1.4rem"
  button-landing-ink:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    padding: "0.85rem 1.4rem"
  stamp:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.sm}"
    typography: "{typography.label}"
  phone-frame:
    backgroundColor: "{colors.ink}"
    rounded: "{rounded.phone}"
    width: "360px"
  contact-band:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    padding: "5rem 0"
---

# Design System: projgaragem

## Overview

**Creative North Star: "A Placa da Garagem"**

O sistema fala como a sinalizacao de uma garagem de bairro: letra condensada em caixa alta, tinta quase preta sobre papel frio, um unico verde profundo como cor de marca. Nada de cartoes flutuantes ou gradientes; a estrutura vem de linhas finas, faixas de cor inteira e cantos de 2px. O Bootstrap fornece grid, formularios e carrossel, mas toda aparencia (cor, tipo, raio, sombra) e redefinida em `site.css`.

O verde (`accent`) e por garagem: cada vitrine pode sobrescrever `--accent`, e o resto do sistema (menu lateral, cabecalho com capa, hover) le a variavel. A plataforma, na landing, usa o verde padrao. Tudo que carrega `accent` precisa funcionar com outra cor escolhida pelo dono.

A landing (rota `/`) e a unica superficie feita pelo fluxo Impeccable e usa o mesmo mundo com mais volume: heroi drenched em verde, celular com moldura de tinta que alterna cliente e dono, listas com regua, faixa de contato inteira em tinta.

**Key Characteristics:**
- Papel e tinta em superficies grandes; verde em faixas inteiras ou em pontos pequenos, nunca diluido.
- Big Shoulders em caixa alta para titulos; Public Sans para leitura; IBM Plex Mono para numeros, selos e metadados.
- Cantos de 2px em tudo, exceto a moldura do celular.
- Estrutura por regua (1px linha, 1px tinta, 3px tinta), nao por cartao.
- Mostra o produto real (vitrine de demonstracao em iframe) em vez de ilustracao.

## Colors

Paleta restrita: dois neutros quentes-frios (papel, tinta), um verde de marca, dois sinais.

### Primary
- **Verde Garagem** (`accent`, #0f5c4d): cor de marca e de acao. Herói da landing (fundo inteiro), botao `btn-accent`, selo "nova", numerais dos passos, foco, selecao de texto, menu lateral da vitrine. Sobrescrevivel por garagem.

### Neutral
- **Tinta** (`ink`, #1a1a18): texto, cabecalho da vitrine (borda de 3px), faixa de contato, moldura do celular, botoes flutuantes.
- **Tinta suave** (`ink-soft`, #5b5d56): texto secundario, descricoes de lista.
- **Papel** (`paper`, #f2f3f1): fundo da pagina e texto sobre verde/tinta (`accent-ink` e o mesmo valor).
- **Papel 2** (`paper-2`, #e7e8e3): secoes alternadas da landing.
- **Linha** (`line`, #d3d5ce): divisorias e bordas de campos.

### Semantic
- **Ambar** (`warn`, #b8842b): selo de "contato" no painel demonstrativo (texto do selo em #7a5614, valor pontual).
- **Tijolo** (`danger`, #a23b2e): estados de erro do produto.

### Named Rules
**The Whole-Band Rule.** O verde e a tinta aparecem como faixa de largura total (heroi, contato) ou como ponto pequeno (selo, numeral). Nunca como cartao colorido no meio de uma secao de papel.

**The Borrowed Accent Rule.** Componentes usam `var(--accent)` e `var(--accent-ink)`, nunca o hex, para que a cor da garagem se propague.

## Typography

**Display Font:** Big Shoulders (sans-serif)
**Body Font:** Public Sans (sans-serif)
**Label/Mono Font:** IBM Plex Mono (monospace)

**Character:** condensada e sinalizadora nos titulos, neutra e legivel no texto corrido, tecnica nos numeros. Titulos h1 a h5 ja vem em caixa alta, peso 700, tracking 0.01em, com `text-wrap: balance`.

### Hierarchy
- **Display** (800, clamp(3rem, 7.4vw, 6rem), 0.95): h1 do heroi da landing, largura maxima 11ch.
- **Headline** (700, clamp(2rem, 4.5vw, 3.25rem), 1): titulos de secao; a faixa de contato usa clamp(2.25rem, 5vw, 3.75rem) e lh 0.98.
- **Title** (700, 1.5rem, caixa alta): termos das listas com regua; h3 dos passos em 1.6rem; numerais dos passos em 800 / 4rem em verde.
- **Body** (400, 1rem a 1.2rem, 1.5 a 1.55): Public Sans; texto de apoio limitado a 34rem (lead) ou 24rem (passos).
- **Label** (600, 0.68 a 0.8rem, 0.04em, caixa alta, Plex Mono): selos de status, metadados da vitrine (cidade), marcador "demonstracao". Valores e precos usam `.num` (Plex Mono, numeros tabulares).

### Named Rules
**The Sign-Painter Rule.** Big Shoulders so em titulos e marca, sempre em caixa alta; qualquer texto corrido ou de interface vai em Public Sans.

**The Mono-For-Data Rule.** Plex Mono e reservado a numeros, selos de estado e metadados; nao para decorar titulos.

## Layout

Contêiner do Bootstrap. A landing usa ritmo vertical de 5rem por secao (3.5rem abaixo de 768px), heroi em duas colunas (texto e lista do lado ativo a esquerda, celular a direita) que empilha abaixo de 992px, onde a lista do lado ativo some e o celular fica em `min(640px, 80vh)`. Listas de recursos em duas colunas com 4rem de vao, uma coluna no celular; passos em tres colunas, uma no celular. Espacamento em passos de 0.5, 0.75, 1.25, 2.5 e 5rem; botoes de acao viram largura total no celular. O produto e mobile first: o comprador chega por link de WhatsApp.

## Elevation & Depth

Sistema plano. Profundidade vem de troca de faixa (papel, papel-2, verde, tinta) e de reguas. Sombras existem so em objetos fisicos: botoes flutuantes da vitrine (`0 1px 3px rgba(0,0,0,0.2)`) e o celular da landing (sombra longa e difusa `0 40px 60px -30px rgba(0,0,0,0.6)`, mini-celulares `0 24px 40px -24px`).

### Named Rules
**The Flat-Surface Rule.** Secoes, listas e campos nao levam sombra. Sombra difusa so em objetos que imitam um aparelho ou que flutuam sobre a pagina.

## Shapes

Cantos de 2px em botoes, selos, campos, banners e botoes flutuantes (`--bs-border-radius*` forcados a 2px). A unica excecao e o celular da landing (moldura 10px de tinta, raio 40px; tela interna 30px; miniaturas 6px de moldura e raio 24px), justificada por representar um aparelho. Estrutura por regua: 1px `line` entre itens, 1px `ink` acima de cada termo de lista, 3px `ink` acima dos passos, borda de 3px sob o cabecalho da vitrine (tinta) e sob a capa (verde).

## Components

### Buttons
- **Shape:** 2px, sem contorno arredondado.
- **Acao da vitrine (`btn-accent`):** fundo verde, texto papel, hover reduz opacidade para 0.85.
- **Secundario (`btn-outline-ink`):** transparente, borda `line`, hover troca a borda para tinta.
- **Landing:** botao papel sobre verde (padding 0.85rem 1.4rem, Public Sans 700), variante tinta sobre papel; hover sobe 2px em 160ms com easing `cubic-bezier(0.16, 1, 0.3, 1)`. Icone SVG inline em traco 1.8.

### Selos
Plex Mono 0.68rem caixa alta, borda 1px tinta, raio 2px. Variantes: "nova" (verde cheio), "vendido" (tinta cheia), "contato" (transparente, borda ambar).

### Cabecalho e menu da vitrine
Barra utilitaria, nao navbar: papel com borda inferior de 3px tinta, marca em Big Shoulders 1.5rem, altura minima da linha 5.625rem independente de haver logo. Com capa: banners empilhados em fade de 700ms, veu de tinta em gradiente, nome sobre fundo tinta 45% com blur. Menu lateral offcanvas em verde da garagem, aberto por botao fixo de tinta (2.6rem) no canto superior direito; botoes flutuantes de WhatsApp e Instagram em tinta 2.75rem, hover vira verde.

### Banner de venda
Faixa de tinta com texto papel e titulo em Big Shoulders: a acao oposta (vender) contrasta de proposito com os cartoes claros de veiculo.

### Celular com dois lados (assinatura da landing)
Moldura de tinta com a vitrine real em iframe; o painel do dono entra por cima com uma transicao de cortina (`clip-path` da direita para a esquerda, 650ms), e a proposta nova chega na lista com um destaque verde que se dissolve (900ms, atraso 500ms). O painel demonstrativo repete o vocabulario do real: barra de tinta com borda inferior verde de 3px, abas, lista com regua, rotulo mono "demonstracao". Seletor Cliente | Dono: par de botoes com contorno papel a 70%, o ativo preenche em papel. Movimento desligado em `prefers-reduced-motion`.

### Listas com regua
`dl` em grade: termo em Big Shoulders 1.5rem caixa alta, descricao em tinta suave, cada item com regua de 1px tinta acima. Substitui cartoes.

### Faixa de contato
Tinta inteira, campos em papel com borda papel, foco com anel papel 45%, caixa marcada em verde, erros em #ffb4a8, confirmacao com regua de 3px papel. Rodape continua em tinta.

## Do's and Don'ts

### Do:
- **Do** usar `var(--accent)`/`var(--accent-ink)` para tudo que e marca, para respeitar a cor por garagem.
- **Do** separar conteudo por reguas (1px `line`, 1px `ink`, 3px `ink`) e por troca de faixa de fundo.
- **Do** manter 2px de raio; so aparelhos (celular) fogem disso.
- **Do** mostrar a vitrine de demonstracao real e rotular o que e sintetico (painel "demonstracao").
- **Do** usar foco visivel de 3px em `accent` (papel sobre verde e tinta), e respeitar `prefers-reduced-motion`.
- **Do** carregar o easing `cubic-bezier(0.16, 1, 0.3, 1)` em toda transicao da landing.

### Don't:
- **Don't** montar grade de cartoes com icone e titulo para listar recursos; use lista com regua.
- **Don't** usar gradientes decorativos ou verde diluido; o verde e cor chapada.
- **Don't** aplicar Big Shoulders em texto corrido nem Plex Mono em titulos.
- **Don't** afirmar prova social, numeros ou depoimentos que nao existem, nem preco na landing.
- **Don't** aplicar arredondamento largo do Bootstrap; as variaveis `--bs-border-radius*` ja estao em 2px.

### Not canonized (defeitos que a build carrega)
- Sombra em degrau duro do botao da landing (`0 2px 0 rgba(0,0,0,0.35)` sobreposta a uma difusa): deslocamento duro fora de um mundo neobrutalista; nao herdar em novas superficies.
- Selos e rotulos em mono caixa alta sao rotulos de estado, nao sobretitulos; nao criar kickers ou eyebrows acima de titulos a partir deles.
