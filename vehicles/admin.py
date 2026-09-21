from django.contrib import admin

from .forms import FotoVeiculoForm
from .models import FotoVeiculo, Veiculo


class FotoVeiculoInline(admin.TabularInline):
    model = FotoVeiculo
    form = FotoVeiculoForm
    extra = 1


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'garagem', 'tipo', 'marca', 'modelo', 'ano_modelo', 'cilindrada', 'potencia_motor',
        'quilometragem', 'combustivel', 'preco', 'destaque', 'disponivel', 'aceita_troca',
    )
    list_filter = ('garagem', 'tipo', 'combustivel', 'destaque', 'disponivel', 'aceita_troca')
    search_fields = ('titulo', 'marca', 'modelo', 'garagem__nome')
    prepopulated_fields = {'slug': ('titulo',)}
    autocomplete_fields = ('garagem',)
    inlines = [FotoVeiculoInline]
