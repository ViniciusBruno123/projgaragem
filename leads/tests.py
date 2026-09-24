import shutil
import tempfile
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from tenants.models import Garagem
from vehicles.models import Veiculo
from vehicles.tests import gerar_foto

from .models import Avaliacao, Proposta


class ConsentimentoPropostaTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_lgpd', 'dono_lgpd@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem LGPD', slug='garagem-lgpd',
            telefone_whatsapp='5517999999999', email_contato='dono_lgpd@example.com',
        )
        self.url = reverse('storefront:contato', kwargs={'garagem_slug': self.garagem.slug})
        self.dados = {'nome': 'Cliente Teste', 'telefone': '17988887777', 'email': '', 'mensagem': 'Oi'}

    def test_formulario_mostra_link_da_politica_de_privacidade(self):
        resp = self.client.get(self.url)
        privacidade = reverse('storefront:privacidade', kwargs={'garagem_slug': self.garagem.slug})
        self.assertContains(resp, privacidade)

    def test_sem_consentimento_nao_cria_proposta(self):
        resp = self.client.post(self.url, self.dados)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'política de privacidade')
        self.assertEqual(Proposta.objects.count(), 0)

    def test_com_consentimento_cria_proposta_e_redireciona_para_whatsapp(self):
        resp = self.client.post(self.url, {**self.dados, 'aceito_privacidade': 'on'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp['Location'].startswith('https://wa.me/5517999999999'))
        self.assertEqual(Proposta.objects.count(), 1)


class AntiSpamPropostaTests(TestCase):
    """O formulário público de proposta/contato é o alvo mais exposto do site a robôs."""

    def setUp(self):
        dono = User.objects.create_user('dono_antispam', 'dono_antispam@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Antispam', slug='garagem-antispam',
            telefone_whatsapp='5517999999999', email_contato='dono_antispam@example.com',
        )
        self.url = reverse('storefront:contato', kwargs={'garagem_slug': self.garagem.slug})
        self.dados = {
            'nome': 'Cliente Teste', 'telefone': '17988887777', 'email': '', 'mensagem': 'Oi',
            'aceito_privacidade': 'on',
        }

    def test_pagina_inclui_o_carimbo_de_hora_e_o_campo_armadilha(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'name="iniciado_em"')
        self.assertContains(resp, 'name="site"')

    def test_preencher_o_campo_armadilha_bloqueia_o_envio(self):
        resp = self.client.post(self.url, {**self.dados, 'site': 'http://spam.example.com', 'iniciado_em': time.time()})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Não foi possível enviar')
        self.assertEqual(Proposta.objects.count(), 0)

    def test_enviar_rapido_demais_apos_carregar_a_pagina_bloqueia_o_envio(self):
        resp = self.client.post(self.url, {**self.dados, 'iniciado_em': time.time()})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Não foi possível enviar')
        self.assertEqual(Proposta.objects.count(), 0)

    def test_pessoa_de_verdade_consegue_enviar(self):
        resp = self.client.post(self.url, {**self.dados, 'iniciado_em': time.time() - 10})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Proposta.objects.count(), 1)


class ConsentimentoAvaliacaoTests(TestCase):
    """Formulário público de "quero vender/trocar meu veículo" — o inverso da proposta."""

    def setUp(self):
        dono = User.objects.create_user('dono_avaliacao', 'dono_avaliacao@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Avaliação', slug='garagem-avaliacao',
            telefone_whatsapp='5517999999999', email_contato='dono_avaliacao@example.com',
        )
        self.url = reverse('storefront:enviar_avaliacao', kwargs={'garagem_slug': self.garagem.slug})
        self.dados = {
            'nome': 'Vendedor Teste', 'telefone': '17988887777', 'email': '',
            'tipo': Veiculo.Tipo.CARRO, 'marca': 'Fiat', 'modelo': 'Uno', 'ano': 2015,
            'quilometragem': 80000, 'observacoes': 'Único dono',
        }

    def test_formulario_mostra_link_da_politica_de_privacidade(self):
        resp = self.client.get(self.url)
        privacidade = reverse('storefront:privacidade', kwargs={'garagem_slug': self.garagem.slug})
        self.assertContains(resp, privacidade)

    def test_sem_consentimento_nao_cria_avaliacao(self):
        resp = self.client.post(self.url, self.dados)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'política de privacidade')
        self.assertEqual(Avaliacao.objects.count(), 0)

    def test_com_consentimento_cria_avaliacao_e_redireciona_para_whatsapp(self):
        resp = self.client.post(self.url, {**self.dados, 'aceito_privacidade': 'on'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp['Location'].startswith('https://wa.me/5517999999999'))
        avaliacao = Avaliacao.objects.get()
        self.assertEqual(avaliacao.garagem, self.garagem)
        self.assertEqual(avaliacao.marca, 'Fiat')
        self.assertIsNone(avaliacao.veiculo_interesse)

    def test_vindo_da_pagina_de_um_veiculo_que_aceita_troca_grava_o_interesse(self):
        veiculo = Veiculo.objects.create(
            garagem=self.garagem, titulo='Honda Civic', slug='honda-civic', marca='Honda', modelo='Civic',
            ano_fabricacao=2020, ano_modelo=2020, quilometragem=30000, combustivel='flex',
            preco='90000.00', aceita_troca=True,
        )
        url = reverse(
            'storefront:enviar_avaliacao_veiculo',
            kwargs={'garagem_slug': self.garagem.slug, 'veiculo_slug': veiculo.slug},
        )
        resp = self.client.post(url, {**self.dados, 'aceito_privacidade': 'on'})
        self.assertEqual(resp.status_code, 302)
        avaliacao = Avaliacao.objects.get()
        self.assertEqual(avaliacao.veiculo_interesse, veiculo)
        self.assertIn('Honda%20Civic', resp['Location'])


class AntiSpamAvaliacaoTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_avaliacao_spam', 'dono_avaliacao_spam@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Avaliação Spam', slug='garagem-avaliacao-spam',
            telefone_whatsapp='5517999999999', email_contato='dono_avaliacao_spam@example.com',
        )
        self.url = reverse('storefront:enviar_avaliacao', kwargs={'garagem_slug': self.garagem.slug})
        self.dados = {
            'nome': 'Vendedor Teste', 'telefone': '17988887777', 'email': '',
            'tipo': Veiculo.Tipo.CARRO, 'marca': 'Fiat', 'modelo': 'Uno', 'ano': 2015,
            'quilometragem': 80000, 'observacoes': '', 'aceito_privacidade': 'on',
        }

    def test_preencher_o_campo_armadilha_bloqueia_o_envio(self):
        resp = self.client.post(self.url, {**self.dados, 'site': 'http://spam.example.com', 'iniciado_em': time.time()})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Não foi possível enviar')
        self.assertEqual(Avaliacao.objects.count(), 0)

    def test_pessoa_de_verdade_consegue_enviar(self):
        resp = self.client.post(self.url, {**self.dados, 'iniciado_em': time.time() - 10})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Avaliacao.objects.count(), 1)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class FotosAvaliacaoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.addClassCleanup(shutil.rmtree, settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        dono = User.objects.create_user('dono_fotos_avaliacao', 'dono_fotos_avaliacao@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Fotos Avaliação', slug='garagem-fotos-avaliacao',
            telefone_whatsapp='5517999999999', email_contato='dono_fotos_avaliacao@example.com',
        )
        self.url = reverse('storefront:enviar_avaliacao', kwargs={'garagem_slug': self.garagem.slug})
        self.dados = {
            'nome': 'Vendedor Teste', 'telefone': '17988887777', 'email': '',
            'tipo': Veiculo.Tipo.CARRO, 'marca': 'Fiat', 'modelo': 'Uno', 'ano': 2015,
            'quilometragem': 80000, 'observacoes': '', 'aceito_privacidade': 'on',
            'iniciado_em': time.time() - 10,
        }

    def test_envia_fotos_opcionais_junto_com_o_pedido(self):
        resp = self.client.post(self.url, {
            **self.dados,
            'fotos': [gerar_foto(nome='foto1.jpg'), gerar_foto(nome='foto2.jpg')],
        })
        self.assertEqual(resp.status_code, 302)
        avaliacao = Avaliacao.objects.get()
        self.assertEqual(avaliacao.fotos.count(), 2)

    def test_foto_invalida_bloqueia_o_envio_sem_criar_avaliacao(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        resp = self.client.post(self.url, {
            **self.dados,
            'fotos': [SimpleUploadedFile('foto.jpg', b'isto nao e uma imagem', content_type='image/jpeg')],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Avaliacao.objects.count(), 0)
