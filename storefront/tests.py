from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tenants.models import Garagem
from vehicles.models import Veiculo


class FiltroVeiculosFrontpageTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_filtro', 'dono_filtro@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Filtro', slug='garagem-filtro',
            telefone_whatsapp='5517999999999', email_contato='dono_filtro@example.com',
        )
        self.moto = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.MOTO, titulo='Honda CG 160',
            slug='honda-cg-160', marca='Honda', modelo='CG 160', ano_fabricacao=2022,
            ano_modelo=2022, quilometragem=5000, combustivel=Veiculo.Combustivel.FLEX,
            cilindrada=160, preco='15000.00',
        )
        self.carro = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.CARRO, titulo='VW Gol',
            slug='vw-gol', marca='Volkswagen', modelo='Gol', ano_fabricacao=2019,
            ano_modelo=2019, quilometragem=40000, combustivel=Veiculo.Combustivel.FLEX,
            potencia_motor='1.6', preco='45000.00',
        )

    def _get(self, **params):
        url = reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug})
        return self.client.get(url, params)

    def test_sem_filtro_mostra_ambos(self):
        resp = self._get()
        self.assertContains(resp, 'Honda CG 160')
        self.assertContains(resp, 'VW Gol')

    def test_filtro_por_tipo_moto(self):
        resp = self._get(tipo='moto')
        self.assertContains(resp, 'Honda CG 160')
        self.assertNotContains(resp, 'VW Gol')

    def test_filtro_por_tipo_carro(self):
        resp = self._get(tipo='carro')
        self.assertContains(resp, 'VW Gol')
        self.assertNotContains(resp, 'Honda CG 160')

    def test_filtro_por_marca(self):
        resp = self._get(marca='Honda')
        self.assertContains(resp, 'Honda CG 160')
        self.assertNotContains(resp, 'VW Gol')

    def test_filtro_por_preco_maximo(self):
        resp = self._get(preco_max='20000')
        self.assertContains(resp, 'Honda CG 160')
        self.assertNotContains(resp, 'VW Gol')

    def test_filtro_por_cilindrada(self):
        resp = self._get(cilindrada='160')
        self.assertContains(resp, 'Honda CG 160')
        self.assertNotContains(resp, 'VW Gol')

    def test_filtro_por_potencia_motor(self):
        resp = self._get(potencia_motor='1.6')
        self.assertContains(resp, 'VW Gol')
        self.assertNotContains(resp, 'Honda CG 160')
