from decimal import Decimal

from django.db import migrations


def limpar_taxa_padrao_antiga(apps, schema_editor):
    """2,50 era o valor padrão antigo, que o dono nem podia editar: passa a valer a média de mercado."""
    Garagem = apps.get_model('tenants', 'Garagem')
    Garagem.objects.filter(taxa_juros_mensal_padrao=Decimal('2.50')).update(taxa_juros_mensal_padrao=None)


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0004_alter_garagem_taxa_juros_mensal_padrao'),
    ]

    operations = [
        migrations.RunPython(limpar_taxa_padrao_antiga, migrations.RunPython.noop),
    ]
