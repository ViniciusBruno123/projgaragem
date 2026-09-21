#!/usr/bin/env bash
# Sobe o servidor de desenvolvimento acessível pelo celular, na mesma rede Wi-Fi.
set -euo pipefail
cd "$(dirname "$0")/.."

PORTA="${1:-8000}"
echo "Abra no celular (conectado ao mesmo Wi-Fi):"
for ip in $(hostname -I | tr ' ' '\n' | grep -E '^[0-9]+\.'); do
    echo "  http://$ip:$PORTA/g/<slug-da-garagem>/"
done
echo
echo "Se não abrir, libere a porta $PORTA no firewall do computador."
echo

# ALLOWED_HOSTS=* vale só para este processo; o .env não é alterado.
ALLOWED_HOSTS='*' exec ./venv/bin/python manage.py runserver "0.0.0.0:$PORTA"
