# projgaragem

Plataforma de vitrines de veículos para garagens pequenas de Catanduva e região. Cada garagem tem sua vitrine
pública (`/g/<slug>/`), um painel próprio (`/painel/`) e paga uma mensalidade via Mercado Pago. O site não vende
veículos: conecta o cliente à garagem por WhatsApp e e-mail.

## Rodar localmente

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements-dev.txt
cp .env.example .env            # e ajuste os valores
./venv/bin/python manage.py migrate
./venv/bin/python manage.py createsuperuser
./venv/bin/python manage.py runserver
```

O cadastro de garagens e donos é feito pelo Django admin (`/admin/`).

## Testes

```bash
./venv/bin/python manage.py test          # suíte normal, rápida
```

## Testar no celular

**No celular de verdade** (computador e celular no mesmo Wi-Fi):

```bash
./scripts/dev_celular.sh
```

O script imprime os endereços (`http://192.168.x.x:8000/...`) para abrir no celular. Se não abrir, libere a porta 8000
no firewall do computador.

**Automatizado**, com um Chromium que emula telas de 320 a 768 px:

```bash
./venv/bin/playwright install chromium     # só na primeira vez
./scripts/testar_mobile.sh
```

Percorre a vitrine, o painel e as páginas legais, e falha se alguma tela estourar a largura ou tiver campo com fonte
menor que 16 px (o iPhone dá zoom nesses campos). Salva um print de cada tela em `test-artifacts/mobile/<largura>/`.
Precisa de internet (o site carrega o Bootstrap e as fontes por CDN) e leva cerca de um minuto, por isso não roda na
suíte normal.

## Rotinas agendadas (cron)

```bash
# todo dia: marca garagens atrasadas e avisa o administrador
./venv/bin/python manage.py verificar_inadimplencia

# todo mês: atualiza a taxa média de juros de financiamento de veículos (Banco Central, SGS 25471)
./venv/bin/python manage.py atualizar_taxa_media
```

O simulador usa a taxa que a garagem informar em "Dados da garagem"; em branco, usa essa média de mercado. Se o
Banco Central estiver fora do ar, o comando falha com erro (o cron avisa) e a última taxa salva continua valendo.
