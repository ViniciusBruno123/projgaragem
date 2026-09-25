---
name: projgaragem
description: Dois sistemas irmaos. O produto (vitrines e painel) em papel, tinta e verde por garagem; a landing da SPI Tech em Asfalto, Azul Profundo e Ambar pontual.
colors:
  spi-asfalto: "#0a0d11"
  spi-asfalto-2: "#11151c"
  spi-azul: "#1a45b8"
  spi-ambar: "#d8920e"
  spi-nevoa: "#e3e7ec"
  spi-grafite: "#3b4450"
  spi-linha: "#252c38"
  spi-nevoa-suave: "rgba(227, 231, 236, 0.78)"
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
  lp-display:
    fontFamily: "Space Grotesk, Public Sans, sans-serif"
    fontSize: "clamp(2.6rem, 6vw, 5rem)"
    fontWeight: 700
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  lp-headline:
    fontFamily: "Space Grotesk, Public Sans, sans-serif"
    fontSize: "clamp(2rem, 4.2vw, 3.1rem)"
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: "-0.01em"
  lp-title:
    fontFamily: "Space Grotesk, Public Sans, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  lp-body:
    fontFamily: "IBM Plex Sans, Public Sans, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  lp-button:
    fontFamily: "IBM Plex Sans, Public Sans, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 600
    lineHeight: 1.2
  produto-display:
    fontFamily: "Big Shoulders, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "0.01em"
  produto-body:
    fontFamily: "Public Sans, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  produto-label:
    fontFamily: "IBM Plex Mono, monospace"
    fontSize: "0.75rem"
    fontWeight: 600
    letterSpacing: "0.04em"
rounded:
  lp-sm: "4px"
  lp-tile: "8px"
  produto: "2px"
  phone: "40px"
  phone-mini: "24px"
spacing:
  sm: "0.5rem"
  md: "1.25rem"
  lg: "2.5rem"
  section: "5.5rem"
  section-mobile: "3.75rem"
components:
  lp-button:
    backgroundColor: "{colors.spi-azul}"
    textColor: "#ffffff"
    typography: "{typography.lp-button}"
    rounded: "{rounded.lp-sm}"
    padding: "0.9rem 1.5rem"
  lp-button-claro:
    backgroundColor: "{colors.spi-nevoa}"
    textColor: "{colors.spi-asfalto}"
    rounded: "{rounded.lp-sm}"
    padding: "0.9rem 1.5rem"
  lp-seletor-ativo:
    backgroundColor: "{colors.spi-azul}"
    textColor: "#ffffff"
    rounded: "2px"
    padding: "0.65rem 1rem"
  lp-logo-tile:
    backgroundColor: "{colors.spi-asfalto-2}"
    rounded: "{rounded.lp-tile}"
    size: "3.1rem"
  lp-secao-nevoa:
    backgroundColor: "{colors.spi-nevoa}"
    textColor: "{colors.spi-asfalto}"
    padding: "5.5rem 0"
  lp-secao-azul:
    backgroundColor: "{colors.spi-azul}"
    textColor: "#ffffff"
    padding: "5.5rem 0"
  lp-contato:
    backgroundColor: "{colors.spi-asfalto}"
    textColor: "{colors.spi-nevoa}"
    padding: "5.5rem 0"
  lp-campo:
    backgroundColor: "{colors.spi-asfalto-2}"
    textColor: "#ffffff"
    rounded: "{rounded.lp-sm}"
    padding: "0.75rem 0.9rem"
  phone-frame:
    backgroundColor: "#05070a"
    rounded: "{rounded.phone}"
    width: "360px"
  button-accent:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    rounded: "{rounded.produto}"
  button-outline-ink:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.produto}"
  selo:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.accent-ink}"
    typography: "{typography.produto-label}"
    rounded: "{rounded.produto}"
---

# Design System: projgaragem

## Overview

**Creative North Star: "O Asfalto e a Vitrine"**

Ha dois sistemas no repositorio e eles nao se misturam. O produto (vitrines das garagens e painel do dono, `static/css/site.css`) segue a identidade propria: papel frio, tinta quase preta, um verde por garagem, Big Shoulders em caixa alta, cantos de 2px, estrutura por regua. A landing da plataforma (rota `/`, `static/css/landing.css`, tudo prefixado `lp-`) veste a identidade obrigatoria da SPI Tech, vendedora do produto: Asfalto como campo, Azul Profundo em botoes e em uma faixa inteira, Ambar so em pontos, Nevoa para a unica secao clara.

A landing e uma pagina escura com um objeto claro dentro: o celular preto mostra a vitrine real do produto (iframe) e, ao trocar para "Voce recebe", o painel do dono desliza por cima. Essa tela interna e o unico lugar onde os dois sistemas se encontram, e la vale o sistema do produto, nao o da SPI. Estrutura por linhas finas, faixas de cor inteira e cantos de 4px; nada de grade de cartoes com icone.

**Key Characteristics:**
- Landing: Asfalto domina (heroi, contato, rodape), uma faixa Nevoa, uma faixa Azul, Ambar em barra, uma frase, numerais, foco e cursor.
- Space Grotesk nos titulos (700 no h1, 600 nos demais), IBM Plex Sans no texto; Plex Mono so em trechos tecnicos (endereco `/g/...`).
- Azul e sempre preenchimento, nunca cor de texto.
- Produto: Big Shoulders / Public Sans / Plex Mono, verde sobrescrevivel por garagem, 2px de raio.
- Celular como moldura: unico objeto com raio grande e sombra longa.

## Colors

Landing: neutro azulado escuro com um azul de marca e um ambar de tempero. Produto: dois neutros quentes-frios com um verde e dois sinais.

### Primary
- **Azul Profundo** (`spi-azul`, #1a45b8): botao primario, aba ativa do seletor, faixa "Como comecar", caixa marcada do formulario. Somente como fundo; texto azul sobre Asfalto da cerca de 2,4:1 e nao passa.
- **Verde Garagem** (`accent`, #0f5c4d): cor do produto, por garagem (`--accent`). Dentro da landing aparece so no painel de demonstracao (borda da barra, selo "nova").

### Secondary
- **Ambar** (`spi-ambar`, #d8920e): barra de 4rem x 6px acima do titulo, a ultima linha do h1 ("Mais vendido."), numerais dos passos, anel de foco, selecao de texto, cursor do campo, hover das linhas de contato, regua da confirmacao. Ate 5% da tela.

### Neutral
- **Asfalto** (`spi-asfalto`, #0a0d11): campo do heroi, contato, rodape e texto da secao Nevoa. **Asfalto 2** (`spi-asfalto-2`, #11151c): fim do degrade do heroi, fundo do tile do logo e dos campos.
- **Nevoa** (`spi-nevoa`, #e3e7ec): texto sobre Asfalto e fundo da secao clara. **Nevoa suave** (`spi-nevoa-suave`, 78%): todo texto pequeno ou de apoio sobre escuro (lead, legenda, itens de lista, rodape).
- **Grafite** (`spi-grafite`, #3b4450): texto secundario sobre Nevoa. **Linha** (`spi-linha`, #252c38): reguas e bordas sobre Asfalto.
- **Tinta** (`ink`), **Tinta suave** (`ink-soft`), **Papel** (`paper`), **Papel 2** (`paper-2`), **Linha** (`line`): produto e painel de demonstracao.

### Semantic
- **Ambar do produto** (`warn`, #b8842b) para "em contato" e **Tijolo** (`danger`, #a23b2e) para erro, ambos no produto. Na landing, erros de formulario usam um coral claro (#ff9d8f) para contraste sobre Asfalto.

### Named Rules
**The Blue-As-Fill Rule.** Azul so preenche (botao, aba ativa, faixa). Nunca escreva texto ou icone em azul sobre Asfalto. Desvio conhecido e aceito: e a razao de links e rotulos irem em Nevoa.

**The Amber-Spice Rule.** Ambar e tempero: barra, uma frase, numerais, foco. Nunca fundo de botao nem faixa.

**The Muted-Mist Rule.** Texto pequeno sobre escuro usa Nevoa a 78%, nao branco puro nem cinza mais escuro; titulos e botoes usam branco.

**The Two-Systems Rule.** Tokens `--spi-*` valem fora do celular; `--ink/--paper/--accent` valem dentro dele e em todo o produto. Nao cruze.

**The Borrowed Accent Rule.** No produto, componentes usam `var(--accent)`/`var(--accent-ink)`, nunca o hex, para a cor da garagem se propagar.

## Typography

**Landing display:** Space Grotesk (com Public Sans)
**Landing body:** IBM Plex Sans (com Public Sans)
**Produto:** Big Shoulders (titulos), Public Sans (texto), IBM Plex Mono (numeros, selos, metadados)

**Character:** geometrica e tecnica na landing, com a frase de marca em caixa alta; sinalizadora e condensada no produto.

### Hierarchy
- **Display** (700, clamp(2.6rem, 6vw, 5rem), 1.02, -0.02em, caixa alta, branco): so o h1 do heroi. Desvio conhecido: o manual da marca pede 600; 700 foi escolhido para igualar os posts do Instagram.
- **Headline** (600, clamp(2rem, 4.2vw, 3.1rem), 1.05): titulos de secao; o contato usa 700 em clamp(2.1rem, 4.6vw, 3.4rem).
- **Title** (600, 1.3 a 1.5rem): termos da lista com regua, h3 dos passos; numerais dos passos em 700 / 3.75rem, Ambar.
- **Body** (400 a 500, 1rem a 1.2rem, 1.55 a 1.6): IBM Plex Sans; lead limitado a 34rem, descricoes a 34rem, passos a 24rem.
- **Button** (600, 1.05rem; 0.95rem no pequeno): IBM Plex Sans.
- **Logo** (Space Grotesk 600, 1.6rem, "SPI"; "TECH" em 0.8rem com tracking 0.22em).
- **Produto:** titulos h1 a h5 em Big Shoulders 700 caixa alta 0.01em; selos e metadados em Plex Mono 0.68 a 0.8rem caixa alta; valores com `.num`.

### Named Rules
**The Slogan-Caps Rule.** Na landing so o h1 e caixa alta; os demais titulos ficam em caixa mista (`text-transform: none` sobrescreve o `site.css`).

**The Mono-For-Data Rule.** Plex Mono e para dados: enderecos, numeros, selos de estado. Nao decora titulos.

## Layout

Contêiner do Bootstrap. Heroi em duas colunas (7/5): texto e lista do lado ativo a esquerda, celular a direita, alinhados ao topo; abaixo de 992px empilha, a lista do lado ativo some e o celular fica em `min(640px, 80vh)`. Secao Nevoa em 6/6 (lista e dois mini-celulares) ou coluna unica sem a segunda demo. Passos em tres colunas com vao de 3rem, uma coluna abaixo de 768px. Contato em 5/7 (texto e canais, formulario). Ritmo vertical de 5.5rem por secao (3.75rem abaixo de 768px), heroi com 4.5rem embaixo. Botoes de acao ocupam largura total no celular e o rotulo "Falar com a gente" encurta para "WhatsApp". Mobile first: o comprador e o dono chegam por link de WhatsApp.

## Elevation & Depth

Plano por padrao. Profundidade na landing vem de troca de faixa (Asfalto, Nevoa, Azul, Asfalto), do degrade sutil Asfalto para Asfalto 2 no heroi e de reguas de 1px. Sombra existe em objetos: o botao (`0 8px 20px -10px rgba(0,0,0,0.7)`, difusa), o celular (`0 40px 60px -30px rgba(0,0,0,0.9)` mais aro 1px #2a3240) e os mini-celulares (`0 24px 40px -24px`). No produto, so os botoes flutuantes (`0 1px 3px rgba(0,0,0,0.2)`).

### Named Rules
**The Object-Shadow Rule.** Sombra so em coisa que flutua ou imita aparelho. Secoes, listas, campos e faixas ficam sem sombra.

## Shapes

Landing: 4px em botoes, seletor e campos; 2px nos botoes internos do seletor; tile do logo 8px (6px no rodape). Produto e painel de demonstracao: 2px. Excecao justificada: o celular (moldura preta de 10px, raio 40px; tela 30px; mini-celulares 6px e 24px). Estrutura por regua: 1px #b9c0ca acima de cada termo da lista Nevoa, 2px branco a 55% acima dos passos, 1px Linha entre itens sobre Asfalto. Logo: monograma "S" reto em blocos azuis com bloco Ambar (cursor), em quadrado Asfalto 2 com borda Linha, seguido de "SPI | TECH".

## Components

### Buttons
- **Primario (`lp-btn`):** Azul Profundo, texto branco, borda #3a63d0, 4px, padding 0.9rem 1.5rem; hover clareia para #2452cc e sobe 2px em 160ms (`cubic-bezier(0.16, 1, 0.3, 1)`), active volta. Icone SVG inline (traco 1.8) quando ha WhatsApp.
- **Claro (`lp-btn--claro`):** Nevoa com texto Asfalto, para usar sobre a faixa azul; hover branco.
- **Link (`lp-link`):** Nevoa 500, sublinhado; hover branco e sublinhado 2px.
- **Produto:** `btn-accent` (verde, hover opacidade 0.85) e `btn-outline-ink` (borda Linha, hover tinta), 2px.

### Seletor Cliente | Ele simula | Voce recebe
Tablist com borda #3a4352, 4px, padding 3px; botoes de 7.5rem minimo, Plex Sans 600; hover #1b222d; aba ativa em Azul com texto branco. Legenda abaixo em Nevoa suave rotula o que e sintetico. Em telas estreitas ocupa a largura toda.

### Celular com dois lados (assinatura)
Moldura #05070a com a vitrine real em iframe; o painel entra por cima em cortina (`clip-path` da direita para a esquerda, 650ms) e a proposta nova chega com destaque verde que se dissolve (900ms, atraso 500ms); a lista do lado ativo entra com 8px de subida em 500ms. Painel de demonstracao: barra de tinta com borda verde de 3px, abas, lista com regua, selos Plex Mono, rotulo "Demonstracao". Movimento desligado em `prefers-reduced-motion`.

### Lista com regua
`dl` com regua de 1px acima de cada item, termo em Space Grotesk 600 1.3rem, descricao em Grafite. Substitui cartoes.

### Faixa de passos
Azul inteiro, tres passos com regua branca de 2px, numeral Ambar, titulo branco, texto #e6ecfb, botao claro abaixo.

### Formulario de contato
Sobre Asfalto: campos Asfalto 2, texto branco, borda #6b7686 (contraste de componente), 4px; foco troca a borda para Ambar com anel Ambar a 35% de 3px; caixa marcada em Azul; erros em coral; confirmacao com regua Ambar de 4px. Canais (WhatsApp, Instagram) em linhas com regua Linha, hover com regua Ambar.

### Cabecalho e menu da vitrine (produto)
Papel com borda inferior de 3px tinta, marca em Big Shoulders 1.5rem, altura da linha 5.625rem com ou sem logo; capa com banners em fade de 700ms; menu lateral offcanvas na cor da garagem; botoes flutuantes de WhatsApp e Instagram em tinta.

## Do's and Don'ts

### Do:
- **Do** usar Asfalto como campo, Azul em preenchimentos, Ambar em ate 5% da tela, Nevoa nas secoes claras.
- **Do** manter a barra Ambar curta (4rem x 6px) acima do titulo e a ultima linha do slogan em Ambar.
- **Do** usar Nevoa a 78% para texto pequeno sobre escuro e branco para titulos e botoes.
- **Do** dar foco visivel de 3px em Ambar sobre escuro (Azul sobre Nevoa) e respeitar `prefers-reduced-motion`.
- **Do** separar conteudo por reguas e troca de faixa, com o easing `cubic-bezier(0.16, 1, 0.3, 1)` em toda transicao.
- **Do** mostrar o produto real e rotular o que e sintetico ("Demonstracao").
- **Do** manter dentro do celular o vocabulario do produto (tinta, papel, verde, Big Shoulders, 2px).

### Don't:
- **Don't** escrever texto ou icone em azul sobre Asfalto.
- **Don't** usar Ambar como fundo de botao ou faixa.
- **Don't** usar grade de cartoes com icone para listar recursos.
- **Don't** afirmar prova social, numeros, depoimentos ou preco que nao existem.
- **Don't** aplicar tokens `--spi-*` no produto nem `--accent` verde nas superficies da SPI.
- **Don't** usar Big Shoulders na landing nem Space Grotesk no produto.

### Not canonized (defeitos ou valores pontuais que a build carrega)
- Hex soltos fora dos tokens (#3a63d0, #2452cc, #aab2bf, #4a5464, #6b7686, #8a94a3, #e6ecfb, #ff9d8f): ajustes de contraste pontuais, nao escala; nao herdar em novas superficies, criar token antes.
- Selos e rotulos mono caixa alta do painel de demonstracao sao rotulos de estado, nao sobretitulos; nao criar kickers ou eyebrows acima de titulos a partir deles. A barra Ambar e marca da SPI, nao um kicker, e nao carrega texto.
- O h1 em 700 (manual: 600) e desvio registrado da marca, nao regra para os demais titulos.
