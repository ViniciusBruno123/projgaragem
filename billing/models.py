from django.db import models

from tenants.models import Garagem


class Assinatura(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        AUTHORIZED = 'authorized', 'Autorizada'
        PAUSED = 'paused', 'Pausada'
        CANCELLED = 'cancelled', 'Cancelada'

    garagem = models.OneToOneField(Garagem, on_delete=models.CASCADE, related_name='assinatura')
    mp_preapproval_id = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    valor_mensal = models.DecimalField(max_digits=8, decimal_places=2)
    proxima_cobranca_prevista = models.DateField(null=True, blank=True)
    ultimo_pagamento_em = models.DateTimeField(null=True, blank=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'

    def __str__(self):
        return f"Assinatura de {self.garagem.nome} ({self.get_status_display()})"


class EventoWebhookMercadoPago(models.Model):
    """Log bruto de todo webhook recebido — auditoria e reprocessamento manual."""

    topico = models.CharField(max_length=60)
    recurso_id = models.CharField(max_length=64)
    payload_bruto = models.JSONField()
    processado_com_sucesso = models.BooleanField(default=False)
    erro = models.TextField(blank=True)
    recebido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evento de webhook (Mercado Pago)'
        verbose_name_plural = 'Eventos de webhook (Mercado Pago)'
        ordering = ['-recebido_em']

    def __str__(self):
        return f"{self.topico} - {self.recurso_id}"
