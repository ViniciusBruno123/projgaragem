import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from tenants.models import Garagem
from vehicles.models import FotoVeiculo, Veiculo
from vehicles.tests import gerar_foto


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


class PoliticaPrivacidadeTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_priv', 'dono_priv@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Privacidade', slug='garagem-privacidade',
            telefone_whatsapp='5517999999999', email_contato='contato_priv@example.com',
        )
        self.url = reverse('storefront:privacidade', kwargs={'garagem_slug': self.garagem.slug})

    def test_pagina_mostra_garagem_como_controladora_e_seu_contato(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Garagem Privacidade')
        self.assertContains(resp, 'contato_priv@example.com')

    def test_rodape_da_vitrine_linka_a_politica(self):
        resp = self.client.get(reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug}))
        self.assertContains(resp, self.url)

    def test_garagem_suspensa_retorna_404(self):
        self.garagem.status = Garagem.Status.SUSPENSO
        self.garagem.save()
        self.assertEqual(self.client.get(self.url).status_code, 404)


class ProporcaoFotoPorTipoTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_prop', 'dono_prop@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Proporção', slug='garagem-proporcao',
            telefone_whatsapp='5517999999999', email_contato='dono_prop@example.com',
        )
        base = dict(
            garagem=self.garagem, marca='Marca', modelo='Modelo', ano_fabricacao=2020,
            ano_modelo=2020, quilometragem=1000, combustivel=Veiculo.Combustivel.FLEX, preco='10000.00',
        )
        # o carro é criado por último: sem o agrupamento, apareceria antes (mais recente)
        self.moto = Veiculo.objects.create(tipo=Veiculo.Tipo.MOTO, titulo='Moto Alfa', slug='moto-alfa', **base)
        self.carro = Veiculo.objects.create(tipo=Veiculo.Tipo.CARRO, titulo='Carro Beta', slug='carro-beta', **base)

    def test_cards_usam_a_proporcao_do_tipo(self):
        resp = self.client.get(reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug}))
        self.assertContains(resp, 'foto-moto')
        self.assertContains(resp, 'foto-carro')

    def test_motos_vem_antes_de_carros_em_linhas_separadas(self):
        resp = self.client.get(reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug}))
        html = resp.content.decode()
        self.assertLess(html.index('Moto Alfa'), html.index('Carro Beta'))
        self.assertEqual(html.count('<div class="row">'), 2)

    def test_pagina_do_veiculo_usa_a_proporcao_do_tipo(self):
        url = reverse('storefront:detalhe_veiculo', kwargs={
            'garagem_slug': self.garagem.slug, 'veiculo_slug': self.carro.slug,
        })
        self.assertContains(self.client.get(url), 'foto-carro')


class FotoClicavelEPreviaNoHoverTests(TestCase):
    """A foto do card abre o detalhe do veículo, e traz as próximas fotos prontas
    para a prévia no hover (só o texto da URL — a imagem só baixa se alguém passar
    o mouse de verdade, ver static/js/vitrine.js)."""

    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        self.enterContext(override_settings(MEDIA_ROOT=media))

        dono = User.objects.create_user('dono_hover', 'dono_hover@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Hover', slug='garagem-hover',
            telefone_whatsapp='5517999999999', email_contato='dono_hover@example.com',
        )
        self.veiculo = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.MOTO, titulo='Moto Hover', marca='Honda',
            modelo='CG', ano_fabricacao=2021, ano_modelo=2021, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, preco='12000.00',
        )
        self.url = reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug})
        self.url_detalhe = reverse('storefront:detalhe_veiculo', kwargs={
            'garagem_slug': self.garagem.slug, 'veiculo_slug': self.veiculo.slug,
        })

    def test_foto_e_um_link_para_o_detalhe(self):
        FotoVeiculo.objects.create(veiculo=self.veiculo, imagem=gerar_foto((1200, 900), nome='foto1.jpg'))
        resp = self.client.get(self.url)
        self.assertContains(resp, f'<a href="{self.url_detalhe}" class="photo-link"')

    def test_com_varias_fotos_traz_as_extras_para_o_hover_sem_a_principal(self):
        principal = FotoVeiculo.objects.create(
            veiculo=self.veiculo, imagem=gerar_foto((1200, 900), nome='principal.jpg'), principal=True,
        )
        extra1 = FotoVeiculo.objects.create(veiculo=self.veiculo, imagem=gerar_foto((1200, 900), nome='extra1.jpg'))
        extra2 = FotoVeiculo.objects.create(veiculo=self.veiculo, imagem=gerar_foto((1200, 900), nome='extra2.jpg'))

        resp = self.client.get(self.url)
        html = resp.content.decode()
        atributo = f'data-fotos-extra="{extra1.imagem.url}|{extra2.imagem.url}"'
        self.assertIn(atributo, html)
        self.assertNotIn(principal.imagem.url + '|', html)  # a principal não repete nas extras

    def test_com_uma_foto_so_nao_ha_extra_para_o_hover(self):
        FotoVeiculo.objects.create(veiculo=self.veiculo, imagem=gerar_foto((1200, 900), nome='unica.jpg'))
        resp = self.client.get(self.url)
        self.assertContains(resp, 'data-fotos-extra=""')

    def test_sem_foto_nenhuma_o_card_continua_levando_ao_detalhe(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, f'<a href="{self.url_detalhe}" class="photo-link"')
        self.assertContains(resp, 'sem foto')


class IconesECarrosselTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_icones', 'dono_icones@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Ícones', slug='garagem-icones',
            telefone_whatsapp='5517999999999', email_contato='dono_icones@example.com',
        )
        self.moto = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.MOTO, titulo='Moto Destaque', slug='moto-destaque',
            marca='Honda', modelo='CG', ano_fabricacao=2011, ano_modelo=2011, quilometragem=49800,
            combustivel=Veiculo.Combustivel.GASOLINA, cilindrada=125, preco='11900.00', destaque=True,
        )
        self.url = reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug})

    def test_card_mostra_dados_com_icones_e_numeros_formatados(self):
        resp = self.client.get(self.url)
        for icone in ('#i-calendario', '#i-odometro', '#i-motor', '#i-combustivel'):
            self.assertContains(resp, icone)
        self.assertContains(resp, '49.800')
        self.assertContains(resp, 'R$ 11.900,00')
        self.assertContains(resp, 'Gasolina')

    def test_ano_aparece_com_dois_digitos_e_so_duplicado_quando_diferem(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, '<span class="visually-hidden">Ano:</span>11')
        self.assertNotContains(resp, '11/11')
        self.assertNotContains(resp, '2011')
        self.moto.ano_modelo = 2012
        self.moto.save()
        self.assertContains(self.client.get(self.url), '11/12')

    def test_selo_de_troca_fica_sobre_a_foto_e_nao_no_corpo_do_card(self):
        self.moto.aceita_troca = True
        self.moto.save()
        html = self.client.get(self.url).content.decode()
        self.assertIn('tag--foto', html)
        self.assertLess(html.index('tag--foto'), html.index('class="body"'))

    def test_destaques_ficam_no_carrossel_com_avanco_de_10_segundos(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'data-carrossel')
        self.assertContains(resp, 'data-intervalo="10000"')
        self.assertContains(resp, 'js/vitrine.js')

    def test_sem_destaques_nao_ha_carrossel(self):
        self.moto.destaque = False
        self.moto.save()
        self.assertNotContains(self.client.get(self.url), 'data-carrossel')

    def test_pagina_do_veiculo_mostra_unidades(self):
        url = reverse('storefront:detalhe_veiculo', kwargs={
            'garagem_slug': self.garagem.slug, 'veiculo_slug': self.moto.slug,
        })
        resp = self.client.get(url)
        self.assertContains(resp, '49.800 km')
        self.assertContains(resp, '125 cc')
        self.assertContains(resp, '#i-odometro')


class OpenGraphTests(TestCase):
    """O link da vitrine é colado no WhatsApp — o preview (título, texto e foto) é parte do produto."""

    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        self.enterContext(override_settings(MEDIA_ROOT=media))

        dono = User.objects.create_user('dono_og', 'dono_og@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Vitrine OG', slug='garagem-vitrine-og',
            telefone_whatsapp='5517999999999', email_contato='dono_og@example.com',
        )
        self.veiculo = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.MOTO, titulo='Honda CG 160 OG',
            marca='Honda', modelo='CG 160', ano_fabricacao=2022, ano_modelo=2022,
            quilometragem=5000, combustivel=Veiculo.Combustivel.FLEX, cilindrada=160, preco='15000.00',
        )

    def test_frontpage_sem_logo_nem_capa_nao_mostra_og_image(self):
        resp = self.client.get(reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug}))
        self.assertContains(resp, f'property="og:title" content="{self.garagem.nome}"')
        self.assertContains(resp, 'property="og:url"')
        self.assertNotContains(resp, 'property="og:image"')

    def test_frontpage_com_capa_usa_capa_como_og_image_absoluta(self):
        self.garagem.capa = gerar_foto((1600, 500), nome='capa.jpg')
        self.garagem.save()

        resp = self.client.get(reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug}))
        self.assertContains(resp, 'property="og:image" content="http://testserver/media/garagens/capas/capa')

    def test_pagina_do_veiculo_usa_titulo_e_foto_do_veiculo(self):
        FotoVeiculo.objects.create(veiculo=self.veiculo, imagem=gerar_foto((1200, 900), nome='moto.jpg'))

        url = reverse('storefront:detalhe_veiculo', kwargs={
            'garagem_slug': self.garagem.slug, 'veiculo_slug': self.veiculo.slug,
        })
        resp = self.client.get(url)
        self.assertContains(resp, f'property="og:title" content="{self.veiculo.titulo} — {self.garagem.nome}"')
        self.assertContains(resp, 'property="og:image" content="http://testserver/media/veiculos/')
        self.assertContains(resp, 'R$ 15.000,00')

    def test_pagina_do_veiculo_sem_foto_usa_capa_da_garagem(self):
        self.garagem.capa = gerar_foto((1600, 500), nome='capa.jpg')
        self.garagem.save()

        url = reverse('storefront:detalhe_veiculo', kwargs={
            'garagem_slug': self.garagem.slug, 'veiculo_slug': self.veiculo.slug,
        })
        resp = self.client.get(url)
        self.assertContains(resp, 'property="og:image" content="http://testserver/media/garagens/capas/capa')
