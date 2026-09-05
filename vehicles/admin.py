from django.contrib import admin

from .models import FotoVeiculo, Veiculo


class FotoVeiculoInline(admin.TabularInline):
    model = FotoVeiculo
    extra = 1


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'garagem', 'marca', 'modelo', 'ano_modelo',
        'quilometragem', 'combustivel', 'preco', 'destaque', 'disponivel',
    )
    list_filter = ('garagem', 'combustivel', 'destaque', 'disponivel')
    search_fields = ('titulo', 'marca', 'modelo', 'garagem__nome')
    prepopulated_fields = {'slug': ('titulo',)}
    autocomplete_fields = ('garagem',)
    inlines = [FotoVeiculoInline]
