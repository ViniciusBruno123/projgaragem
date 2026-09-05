from django.contrib import admin

from .models import Assinatura, EventoWebhookMercadoPago


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ('garagem', 'status', 'valor_mensal', 'proxima_cobranca_prevista', 'atualizada_em')
    list_filter = ('status',)
    search_fields = ('garagem__nome', 'mp_preapproval_id')
    autocomplete_fields = ('garagem',)


@admin.register(EventoWebhookMercadoPago)
class EventoWebhookMercadoPagoAdmin(admin.ModelAdmin):
    list_display = ('topico', 'recurso_id', 'processado_com_sucesso', 'recebido_em')
    list_filter = ('topico', 'processado_com_sucesso')
    readonly_fields = ('topico', 'recurso_id', 'payload_bruto', 'processado_com_sucesso', 'erro', 'recebido_em')

    def has_add_permission(self, request):
        return False
