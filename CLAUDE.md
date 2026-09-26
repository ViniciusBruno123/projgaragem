# projgaragem (Farol, por SPI Tech)

Plataforma Django multi-tenant de vitrines de veículos para garagens de Catanduva-SP. Apps: `tenants`, `vehicles`,
`storefront` (vitrine pública `/g/<slug>/`), `dashboard` (painel `/painel/`), `leads`, `financing`, `billing`,
`landing` (página de venda na raiz `/`).

## Comandos

- Rodar: `python manage.py runserver 0.0.0.0:8000` (o `.env` só é relido ao reiniciar o processo).
- Testar: `python manage.py test` (suíte inteira, cerca de 70 s) ou `python manage.py test landing` (um app).
- Migrações: `python manage.py makemigrations && python manage.py migrate`. Troca de campo com dados usa
  AddField, depois RunPython (copia os dados) e por fim RemoveField, com função reversa.

## Convenções do código

- Comentários e textos de interface em português.
- Isolamento entre garagens: buscar sempre a partir de `self.garagem.<relação>`, nunca `Model.objects.get(pk=...)` solto.
- Templates Django: comentário de várias linhas é `{% comment %}...{% endcomment %}`; `{# #}` só funciona em uma linha.
- Formulários públicos usam honeypot e tempo mínimo de envio (`leads.forms.AntiSpamFormMixin`).
- Segredos e contatos ficam no `.env` (modelo em `.env.example`), nunca no repositório.

## Ferramentas de apoio (plugins do Claude Code)

- **Graphify** (grafo de conhecimento, só código, extração local sem enviar nada para fora): para perguntas de
  arquitetura ("o que depende de X", "como A chega em B"), consulte o grafo antes de vasculhar arquivos:
  `graphify query "..."`, `graphify explain "Nome"`, `graphify affected "Nome"`, `graphify path "A" "B"`.
  O grafo fica em `graphify-out/` (ignorado pelo git). Gerar: `graphify extract . --code-only` e depois
  `graphify cluster-only . --no-label --no-viz`; atualizar após mudanças grandes: `graphify update .`.
  O que fica fora do grafo está em `.graphifyignore`.
- **Ponytail** (código mínimo, ativo por padrão no nível `full`): vale para lógica e backend. Em trabalho de design
  e interface (fluxo Impeccable) mandam o `PRODUCT.md`, o `DESIGN.md` e o brief da superfície: ponytail pede menos código,
  não menos design. Se atrapalhar, `/ponytail lite` ou `/ponytail off`.
- **Agent Skills** (fluxo de engenharia): para mudanças maiores, `/agent-skills:spec`, `:plan`, `:build`, `:test`,
  `:review`, `:ship`. Use `security-and-hardening` antes de qualquer publicação em produção. Para UI, prefira o
  Impeccable e as skills do próprio projeto a `frontend-ui-engineering`.
