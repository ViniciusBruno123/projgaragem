from datetime import date

from django.conf import settings

# Atualizar sempre que o texto dos termos ou da política de privacidade mudar.
ATUALIZADO_EM = date(2026, 9, 21)


def contexto_plataforma():
    return {
        'plataforma_nome': settings.PLATAFORMA_NOME,
        'plataforma_cnpj': settings.PLATAFORMA_CNPJ,
        'plataforma_email': settings.PLATFORM_ADMIN_EMAIL,
        'atualizado_em': ATUALIZADO_EM,
    }
