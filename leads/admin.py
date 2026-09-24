from django.contrib import admin

from .models import Avaliacao, FotoAvaliacao, Proposta


@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'garagem', 'veiculo', 'canal', 'status', 'criado_em')
    list_filter = ('garagem', 'canal', 'status')
    search_fields = ('nome', 'telefone', 'email')


class FotoAvaliacaoInline(admin.TabularInline):
    model = FotoAvaliacao
    extra = 0


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'garagem', 'marca', 'modelo', 'ano', 'status', 'criado_em')
    list_filter = ('garagem', 'tipo', 'status')
    search_fields = ('nome', 'telefone', 'email', 'marca', 'modelo')
    inlines = [FotoAvaliacaoInline]
