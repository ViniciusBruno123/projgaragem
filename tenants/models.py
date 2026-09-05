from decimal import Decimal

from django.conf import settings
from django.db import models


class Garagem(models.Model):
    class Status(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        ATRASADO = 'atrasado', 'Atrasado'
        SUSPENSO = 'suspenso', 'Suspenso'

    dono = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='garagem'
    )
    nome = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, db_index=True)
    telefone_whatsapp = models.CharField(
        max_length=20,
        help_text="Somente dígitos, com DDI e DDD. Ex: 5517999999999",
    )
    email_contato = models.EmailField()
    cidade = models.CharField(max_length=100, default='Catanduva')
    taxa_juros_mensal_padrao = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('2.5'),
        help_text="Taxa mensal (%) usada no simulador de financiamento.",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ATIVO)
    suspensa_manualmente_em = models.DateTimeField(null=True, blank=True)
    ultimo_aviso_atraso_enviado_em = models.DateTimeField(null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Garagem'
        verbose_name_plural = 'Garagens'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.telefone_whatsapp and not self.telefone_whatsapp.isdigit():
            raise ValidationError({
                'telefone_whatsapp': 'Use apenas dígitos (DDI + DDD + número), sem espaços ou símbolos.'
            })
