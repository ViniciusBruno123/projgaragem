import json

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import EventoWebhookMercadoPago
from .services import processar_evento, validar_assinatura_mp


@csrf_exempt
@require_POST
def webhook_mercadopago(request):
    if not validar_assinatura_mp(request):
        return HttpResponseForbidden()

    topico = request.GET.get('type', '')
    recurso_id = request.GET.get('data.id', '')
    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        payload = {}

    evento = EventoWebhookMercadoPago.objects.create(
        topico=topico, recurso_id=recurso_id, payload_bruto=payload,
    )

    try:
        processar_evento(evento)
    except Exception as exc:
        evento.erro = str(exc)
        evento.save(update_fields=['erro'])

    # Sempre 200: erro de processamento fica registrado no evento para
    # investigação manual, mas não deve gerar retry-loop do Mercado Pago.
    return HttpResponse(status=200)
