#!/usr/bin/env bash
# Abre as telas do site em tamanhos de celular num Chromium headless e falha se
# alguma estourar a largura ou tiver campo pequeno demais (o iPhone dá zoom).
# Salva um print de cada tela em test-artifacts/mobile/<largura>/.
#
# Primeira vez: ./venv/bin/pip install -r requirements-dev.txt
#               ./venv/bin/playwright install chromium
set -euo pipefail
cd "$(dirname "$0")/.."

TESTE_MOBILE=1 MOBILE_SCREENSHOTS="${MOBILE_SCREENSHOTS:-1}" \
    ./venv/bin/python manage.py test storefront.tests_mobile -v 2
