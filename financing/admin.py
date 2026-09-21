from django.contrib import admin

from .models import TaxaReferencia


@admin.register(TaxaReferencia)
class TaxaReferenciaAdmin(admin.ModelAdmin):
    list_display = ('referencia', 'taxa_mensal', 'fonte', 'obtida_em')
    readonly_fields = ('obtida_em',)
