from django.db import migrations


def copiar_capa_para_banner(apps, schema_editor):
    """Cada Garagem podia ter uma única capa; agora pode ter várias (Banner, em transição na
    vitrine). Copia a capa existente, se houver, como o primeiro banner — sem duplicar o
    arquivo em disco, só aponta o novo registro para o mesmo caminho já salvo."""
    Garagem = apps.get_model('tenants', 'Garagem')
    Banner = apps.get_model('tenants', 'Banner')
    for garagem in Garagem.objects.exclude(capa=''):
        Banner.objects.create(garagem=garagem, imagem=garagem.capa.name, ordem=0)


def reverter(apps, schema_editor):
    """Não recria o campo capa (isso é feito pela migração seguinte) — só limpa os banners
    criados por esta migração, caso ela seja desfeita antes daquela."""
    Banner = apps.get_model('tenants', 'Banner')
    Banner.objects.filter(ordem=0).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0009_adiciona_banner_e_ocultar_identidade'),
    ]

    operations = [
        migrations.RunPython(copiar_capa_para_banner, reverter),
    ]
