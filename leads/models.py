from django.db import models

from tenants.models import Garagem
from vehicles.models import Veiculo


class Proposta(models.Model):
    class Canal(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        EMAIL = 'email', 'E-mail'

    garagem = models.ForeignKey(Garagem, on_delete=models.CASCADE, related_name='propostas')
    veiculo = models.ForeignKey(
        Veiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='propostas'
    )
    nome = models.CharField(max_length=120)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    mensagem = models.TextField(blank=True)
    canal = models.CharField(max_length=10, choices=Canal.choices, default=Canal.WHATSAPP)
    criado_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Proposta'
        verbose_name_plural = 'Propostas'
        ordering = ['-criado_em']

    def __str__(self):
        alvo = self.veiculo.titulo if self.veiculo else 'Contato geral'
        return f"{self.nome} - {alvo}"
