from django.db import models

from tenants.models import Garagem
from vehicles.models import Veiculo


class Proposta(models.Model):
    class Canal(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        EMAIL = 'email', 'E-mail'

    class Status(models.TextChoices):
        NOVA = 'nova', 'Nova'
        EM_CONTATO = 'em_contato', 'Em contato'
        CONVERTIDA = 'convertida', 'Vendido para esse cliente'
        PERDIDA = 'perdida', 'Sem retorno / Perdida'

    garagem = models.ForeignKey(Garagem, on_delete=models.CASCADE, related_name='propostas')
    veiculo = models.ForeignKey(
        Veiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='propostas'
    )
    nome = models.CharField(max_length=120)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    mensagem = models.TextField(blank=True)
    canal = models.CharField(max_length=10, choices=Canal.choices, default=Canal.WHATSAPP)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NOVA)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proposta'
        verbose_name_plural = 'Propostas'
        ordering = ['-criado_em']

    def __str__(self):
        alvo = self.veiculo.titulo if self.veiculo else 'Contato geral'
        return f"{self.nome} - {alvo}"
