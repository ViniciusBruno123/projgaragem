from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tenants.models import Garagem
from vehicles.models import Veiculo


class RobotsTxtTests(TestCase):
    def test_libera_vitrine_e_bloqueia_areas_internas(self):
        resp = self.client.get('/robots.txt')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/plain')

        conteudo = resp.content.decode()
        self.assertIn('Allow: /g/', conteudo)
        self.assertIn('Disallow: /painel/', conteudo)
        self.assertIn('Disallow: /admin/', conteudo)
        self.assertIn('Disallow: /billing/', conteudo)
        self.assertIn('Sitemap: ', conteudo)
        self.assertIn('/sitemap.xml', conteudo)


class SitemapTests(TestCase):
    def setUp(self):
        dono_ativo = User.objects.create_user('dono_sitemap_ativo', 'a_sm@example.com', 'senha12345')
        self.garagem_ativa = Garagem.objects.create(
            dono=dono_ativo, nome='Garagem Ativa', slug='garagem-ativa-sitemap',
            telefone_whatsapp='5517999999999', email_contato='a_sm@example.com',
        )
        Veiculo.objects.create(
            garagem=self.garagem_ativa, tipo=Veiculo.Tipo.MOTO, titulo='Moto Disponível Sitemap',
            marca='Honda', modelo='CG', ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, preco='10000.00', disponivel=True,
        )
        Veiculo.objects.create(
            garagem=self.garagem_ativa, tipo=Veiculo.Tipo.MOTO, titulo='Moto Vendida Sitemap',
            marca='Honda', modelo='CG', ano_fabricacao=2019, ano_modelo=2019, quilometragem=2000,
            combustivel=Veiculo.Combustivel.FLEX, preco='9000.00', disponivel=False,
        )

        dono_suspenso = User.objects.create_user('dono_sitemap_suspenso', 'b_sm@example.com', 'senha12345')
        self.garagem_suspensa = Garagem.objects.create(
            dono=dono_suspenso, nome='Garagem Suspensa', slug='garagem-suspensa-sitemap',
            telefone_whatsapp='5517999999998', email_contato='b_sm@example.com',
            status=Garagem.Status.SUSPENSO,
        )
        Veiculo.objects.create(
            garagem=self.garagem_suspensa, tipo=Veiculo.Tipo.CARRO, titulo='Carro Suspenso Sitemap',
            marca='Fiat', modelo='Uno', ano_fabricacao=2018, ano_modelo=2018, quilometragem=3000,
            combustivel=Veiculo.Combustivel.FLEX, preco='15000.00', disponivel=True,
        )

    def test_lista_garagem_ativa_mas_nao_suspensa(self):
        resp = self.client.get(reverse('sitemap'))
        self.assertEqual(resp.status_code, 200)
        conteudo = resp.content.decode()
        self.assertIn('/g/garagem-ativa-sitemap/', conteudo)
        self.assertNotIn('/g/garagem-suspensa-sitemap/', conteudo)

    def test_lista_veiculo_disponivel_mas_nao_indisponivel_nem_de_garagem_suspensa(self):
        conteudo = self.client.get(reverse('sitemap')).content.decode()
        self.assertIn('moto-disponivel-sitemap', conteudo)
        self.assertNotIn('moto-vendida-sitemap', conteudo)
        self.assertNotIn('carro-suspenso-sitemap', conteudo)

    def test_garagem_atrasada_continua_no_sitemap(self):
        self.garagem_ativa.status = Garagem.Status.ATRASADO
        self.garagem_ativa.save()
        conteudo = self.client.get(reverse('sitemap')).content.decode()
        self.assertIn('/g/garagem-ativa-sitemap/', conteudo)
