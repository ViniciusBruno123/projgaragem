import hashlib
import hmac

import mercadopago
from django.conf import settings
from django.core.mail import send_mail

from tenants.models import Garagem

from .models import Assinatura


def get_sdk():
    return mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)


def criar_assinatura_mercadopago(garagem, valor_mensal):
    """Cria (ou recria) a assinatura recorrente no Mercado Pago para a garagem.

    Retorna a URL (init_point) que o dono da garagem deve acessar para
    autorizar a cobrança recorrente no cartão.
    """
    sdk = get_sdk()
    preapproval_data = {
        "reason": f"Mensalidade plataforma - {garagem.nome}",
        "external_reference": str(garagem.id),
        "payer_email": garagem.dono.email,
        "back_url": f"{settings.SITE_URL}/painel/assinatura/",
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": float(valor_mensal),
            "currency_id": "BRL",
        },
        "status": "pending",
    }
    result = sdk.preapproval().create(preapproval_data)
    response = result["response"]

    Assinatura.objects.update_or_create(
        garagem=garagem,
        defaults={
            "mp_preapproval_id": response["id"],
            "status": response.get("status", Assinatura.Status.PENDING),
            "valor_mensal": valor_mensal,
        },
    )
    return response["init_point"]


def validar_assinatura_mp(request):
    """Valida a assinatura HMAC do webhook do Mercado Pago.

    Ver: https://www.mercadopago.com.br/developers/pt/docs/checkout-api-orders/notifications
    """
    x_signature = request.headers.get('x-signature', '')
    x_request_id = request.headers.get('x-request-id', '')
    data_id = request.GET.get('data.id', '')
    if not x_signature or not settings.MERCADOPAGO_WEBHOOK_SECRET:
        return False

    try:
        parts = dict(p.strip().split('=', 1) for p in x_signature.split(',') if '=' in p)
    except ValueError:
        return False

    ts, v1 = parts.get('ts'), parts.get('v1')
    if not ts or not v1:
        return False

    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    esperado = hmac.new(
        settings.MERCADOPAGO_WEBHOOK_SECRET.encode(), manifest.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(esperado, v1)


def processar_evento(evento):
    """Busca o recurso atualizado no Mercado Pago e sincroniza Assinatura/Garagem.

    Nunca confia no status vindo do payload do webhook — sempre busca o
    recurso atual via API antes de decidir o que fazer.
    """
    if evento.topico not in ('preapproval', 'subscription_preapproval'):
        return

    sdk = get_sdk()
    result = sdk.preapproval().get(evento.recurso_id)
    response = result['response']

    try:
        assinatura = Assinatura.objects.select_related('garagem').get(mp_preapproval_id=response['id'])
    except Assinatura.DoesNotExist:
        return

    novo_status = response['status']
    assinatura.status = novo_status
    assinatura.save(update_fields=['status', 'atualizada_em'])

    garagem = assinatura.garagem
    if novo_status == Assinatura.Status.AUTHORIZED:
        # Suspensão é sempre manual — um pagamento em dia nunca reativa
        # sozinho uma garagem que o administrador suspendeu de propósito.
        if garagem.status != Garagem.Status.SUSPENSO:
            garagem.status = Garagem.Status.ATIVO
        garagem.ultimo_aviso_atraso_enviado_em = None
        garagem.save(update_fields=['status', 'ultimo_aviso_atraso_enviado_em'])
    elif novo_status in (Assinatura.Status.PAUSED, Assinatura.Status.CANCELLED):
        if garagem.status == Garagem.Status.ATIVO:
            garagem.status = Garagem.Status.ATRASADO
            garagem.save(update_fields=['status'])

    evento.processado_com_sucesso = True
    evento.save(update_fields=['processado_com_sucesso'])


def enviar_email_aviso_admin(garagem, dias_atraso):
    send_mail(
        subject=f"[projgaragem] {garagem.nome} está com {dias_atraso} dia(s) de atraso",
        message=(
            f"A garagem '{garagem.nome}' (slug: {garagem.slug}) está com pagamento "
            f"atrasado há {dias_atraso} dia(s).\n\n"
            "O painel de edição dela já está bloqueado automaticamente. A vitrine "
            "pública continua no ar — suspenda manualmente pelo Django admin "
            "(ação 'Suspender vitrine pública') se decidir cortar o acesso."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.PLATFORM_ADMIN_EMAIL],
        fail_silently=True,
    )
