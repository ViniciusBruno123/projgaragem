from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from tenants.models import Garagem
from vehicles.models import Veiculo

# A vitrine de uma garagem suspensa dá 404 (ver tenants.services.get_garagem_ativa_ou_404);
# atrasada continua no ar. Os dois sitemaps abaixo seguem a mesma regra.
STATUS_COM_VITRINE_NO_AR = [Garagem.Status.ATIVO, Garagem.Status.ATRASADO]


class GaragemSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Garagem.objects.filter(status__in=STATUS_COM_VITRINE_NO_AR)

    def location(self, garagem):
        return reverse('storefront:frontpage', kwargs={'garagem_slug': garagem.slug})


class VeiculoSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return (
            Veiculo.objects.filter(disponivel=True, garagem__status__in=STATUS_COM_VITRINE_NO_AR)
            .select_related('garagem')
        )

    def location(self, veiculo):
        return reverse(
            'storefront:detalhe_veiculo',
            kwargs={'garagem_slug': veiculo.garagem.slug, 'veiculo_slug': veiculo.slug},
        )

    def lastmod(self, veiculo):
        return veiculo.atualizado_em
