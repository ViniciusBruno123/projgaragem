from django.core.management.base import BaseCommand, CommandError

from financing.services import TaxaIndisponivel, atualizar_taxa_bcb


class Command(BaseCommand):
    help = (
        "Atualiza a taxa média de juros do financiamento de veículos (Banco Central, série SGS 25471). "
        "Pensado para rodar uma vez por mês, via cron."
    )

    def handle(self, *args, **options):
        try:
            taxa, criada = atualizar_taxa_bcb()
        except TaxaIndisponivel as exc:
            raise CommandError(str(exc))

        situacao = 'salva' if criada else 'já estava atualizada'
        self.stdout.write(self.style.SUCCESS(
            f"Taxa média de mercado: {taxa.taxa_mensal}% ao mês (ref. {taxa.referencia:%m/%Y}), {situacao}."
        ))
