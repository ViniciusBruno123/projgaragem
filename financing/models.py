from django.db import models


class TaxaReferencia(models.Model):
    """Taxa média de mercado do financiamento de veículos, obtida do Banco Central."""

    fonte = models.CharField(max_length=40, default='bcb-sgs-25471')
    referencia = models.DateField(help_text="Mês a que a taxa se refere.")
    taxa_mensal = models.DecimalField(max_digits=5, decimal_places=2, help_text="Em % ao mês.")
    obtida_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Taxa de referência'
        verbose_name_plural = 'Taxas de referência'
        ordering = ['-referencia']
        unique_together = ('fonte', 'referencia')

    def __str__(self):
        return f"{self.taxa_mensal}% a.m. ({self.referencia:%m/%Y})"
