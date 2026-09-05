from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from billing.models import Assinatura
from billing.services import enviar_email_aviso_admin
from tenants.models import Garagem


class Command(BaseCommand):
    help = (
        "Verifica assinaturas pausadas/canceladas no Mercado Pago, marca a garagem "
        "como atrasada e avisa o administrador da plataforma por e-mail após N dias "
        "de atraso. Nunca suspende a vitrine — isso é sempre uma ação manual."
    )

    def handle(self, *args, **options):
        limite = settings.DIAS_ATRASO_PARA_AVISO_ADMIN
        hoje = timezone.now().date()

        assinaturas_em_falha = Assinatura.objects.filter(
            status__in=[Assinatura.Status.PAUSED, Assinatura.Status.CANCELLED]
        ).select_related('garagem')

        avisos_enviados = 0
        for assinatura in assinaturas_em_falha:
            garagem = assinatura.garagem

            if garagem.status == Garagem.Status.ATIVO:
                garagem.status = Garagem.Status.ATRASADO
                garagem.save(update_fields=['status'])

            dias_atraso = (hoje - assinatura.atualizada_em.date()).days
            if dias_atraso >= limite and garagem.ultimo_aviso_atraso_enviado_em is None:
                enviar_email_aviso_admin(garagem, dias_atraso)
                garagem.ultimo_aviso_atraso_enviado_em = timezone.now()
                garagem.save(update_fields=['ultimo_aviso_atraso_enviado_em'])
                avisos_enviados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Verificação concluída: {assinaturas_em_falha.count()} assinatura(s) em falha, "
            f"{avisos_enviados} aviso(s) enviado(s) ao administrador."
        ))
