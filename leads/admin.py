from django.contrib import admin

from .models import Proposta


@admin.register(Proposta)
class PropostaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'garagem', 'veiculo', 'canal', 'status', 'criado_em')
    list_filter = ('garagem', 'canal', 'status')
    search_fields = ('nome', 'telefone', 'email')
