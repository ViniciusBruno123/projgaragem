from django.conf import settings
from django.contrib import admin, messages
from django.utils import timezone

from .models import Banner, Garagem


class BannerInline(admin.TabularInline):
    model = Banner
    extra = 1


@admin.action(description="Suspender vitrine pública das garagens selecionadas")
def suspender_vitrine(modeladmin, request, queryset):
    queryset.update(status=Garagem.Status.SUSPENSO, suspensa_manualmente_em=timezone.now())


@admin.action(description="Reativar garagem (voltar para ativo)")
def reativar_garagem(modeladmin, request, queryset):
    queryset.update(status=Garagem.Status.ATIVO, suspensa_manualmente_em=None)


@admin.action(description="Gerar link de assinatura Mercado Pago")
def gerar_link_assinatura(modeladmin, request, queryset):
    from billing.services import criar_assinatura_mercadopago

    for garagem in queryset:
        try:
            init_point = criar_assinatura_mercadopago(garagem, settings.PLANO_MENSALIDADE_PADRAO)
            modeladmin.message_user(request, f"{garagem.nome}: {init_point}", level=messages.SUCCESS)
        except Exception as exc:
            modeladmin.message_user(
                request, f"{garagem.nome}: erro ao gerar assinatura — {exc}", level=messages.ERROR
            )


@admin.register(Garagem)
class GaragemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'cidade', 'plano', 'total_de_veiculos', 'status', 'dono', 'criada_em')
    list_filter = ('status', 'plano', 'cidade')
    list_editable = ('plano',)
    search_fields = ('nome', 'slug', 'dono__username', 'dono__email')
    prepopulated_fields = {'slug': ('nome',)}
    autocomplete_fields = ('dono',)
    actions = [suspender_vitrine, reativar_garagem, gerar_link_assinatura]
    inlines = [BannerInline]

    @admin.display(description='Veículos')
    def total_de_veiculos(self, garagem):
        return f'{garagem.veiculos.count()}/{garagem.limite_veiculos}'
