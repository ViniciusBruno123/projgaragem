# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
- **Dono de garagem** (revenda pequena de carros e motos em Catanduva-SP e região): decide se assina a plataforma. Hoje divulga estoque por WhatsApp/Instagram; quer uma vitrine própria e propostas chegando organizadas, sem depender de técnico.
- **Cliente final da garagem** (comprador): acessa a vitrine `/g/<slug>/` pelo celular, geralmente vindo de um link de WhatsApp.
- **Sócios da plataforma** (Vinícius e João Gabriel): apresentam a plataforma pessoalmente ao dono de garagem e atendem os contatos.

## Product Purpose
Plataforma de vitrines de veículos para garagens pequenas. Cada garagem ganha sua vitrine pública, um painel próprio e paga uma mensalidade (Mercado Pago). O site não vende veículos: conecta o cliente final à garagem por WhatsApp e e-mail. Sucesso hoje: conseguir o primeiro cliente pagante (garagem interessada).

## Positioning
Feita para a garagem pequena da região: vitrine própria com identidade da garagem (logo, cores, banners, fonte), simulador de financiamento com taxa média do Banco Central e propostas que caem direto no WhatsApp da garagem — sem montar site, sem taxa por venda, atendimento local.

## Operating Context
Onboarding manual: os sócios cadastram garagem e dono pelo Django admin (sem cadastro público). A landing da raiz `/` é usada em apresentação presencial (sábado, local) e depois para captar contatos de interessados.

## Capabilities and Constraints
- Vitrine pública em `/g/<slug>/` com logo, cores, fonte e vários banners personalizáveis; ícones flutuantes de WhatsApp, Instagram e "Como chegar" (Google Maps).
- Simulador de financiamento (Tabela Price) com taxa própria da garagem ou média de mercado do Banco Central.
- Proposta por veículo e pedido de avaliação de veículo do cliente (troca/venda), que chegam ao painel e ao WhatsApp.
- Painel: cadastro de veículos com fotos, marcar como vendido (o veículo some da vitrine), acompanhar propostas e avaliações; endereço definido em mapa (OpenStreetMap).
- Planos por limite de estoque: Básico 50, Intermediário 100, Avançado 300 veículos.
- Preço **não** aparece na landing (decisão do usuário): valor é conversado no contato.
- Contato da landing: botão de WhatsApp dos sócios com mensagem pronta e formulário de interesse que grava no sistema. Número do WhatsApp ainda não informado (configurável via `.env`).
- Deploy/domínio adiados até existir um cliente pagante.

## Brand Commitments
A plataforma é vendida pela **SPI Tech** ("Soluções digitais"), cuja identidade é obrigatória na landing page (raiz `/`): Asfalto #0A0D11 (fundo, ~60%), Azul Profundo #1A45B8 (marca, ~25%), Âmbar #D8920E (detalhes pontuais, até 5%), Névoa #E3E7EC (fundo claro), Grafite #3B4450 (texto secundário); títulos em Space Grotesk 600, texto em IBM Plex Sans 400; monograma "S" reto com bloco âmbar (cursor de terminal), logotipo horizontal "SPI | TECH" (arquivo em `static/img/spi-monograma.svg`); barra âmbar curta acima do título; slogan "Mais visto. Mais procurado. Mais vendido.". Instagram @spi.tech; WhatsApp em `.env` (`PLATAFORMA_WHATSAPP`, `PLATAFORMA_WHATSAPP_2`).

O produto em si (vitrines das garagens e painel) mantém a identidade própria já existente (paper/ink + verde, Big Shoulders / Public Sans / IBM Plex Mono); cada garagem tem a sua cor. Nome técnico `projgaragem` (setting `PLATAFORMA_NOME`, usado nos textos legais); nome comercial do produto ainda não definido.

## Evidence on Hand
Sem clientes, depoimentos, números ou casos reais — **não fabricar**. Existem vitrines de demonstração (Motos do João e Central Motors) com logos e banners em `design_assets_demo/` e dados no banco local.

## Product Principles
- Falar a língua do dono de garagem: estoque, proposta, WhatsApp — sem jargão de software.
- Mostrar o produto real (a vitrine de demonstração) em vez de prometer.
- Nunca afirmar o que o sistema não faz nem inventar prova social.
- Celular primeiro: o dono e o cliente final chegam pelo WhatsApp.
- Contato em um toque: WhatsApp sempre à mão.
