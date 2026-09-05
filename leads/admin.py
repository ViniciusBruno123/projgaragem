from django.contrib import admin

from .models import Proposta


@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'garagem', 'veiculo', 'canal', 'criado_em', 'lida')
    list_filter = ('garagem', 'canal', 'lida')
    search_fields = ('nome', 'telefone', 'email')
