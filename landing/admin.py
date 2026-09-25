from django.contrib import admin

from .models import InteresseGaragem


@admin.register(InteresseGaragem)
class InteresseGaragemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nome_garagem', 'telefone', 'atendido', 'criado_em')
    list_filter = ('atendido',)
    search_fields = ('nome', 'nome_garagem', 'telefone')
    list_editable = ('atendido',)
