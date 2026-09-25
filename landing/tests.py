import time

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from tenants.models import Garagem
from vehicles.models import Veiculo

from .models import InteresseGaragem


def _dados(**extra):
    dados = {
        'nome': 'Carlos', 'nome_garagem': 'Auto Carlos', 'telefone': '(17) 99999-1234',
        'mensagem': '', 'aceito_contato': 'on', 'site': '',
        'iniciado_em': str(time.time() - 60),
    }
    dados.update(extra)
    return dados


class LandingPageTests(TestCase):
    def test_raiz_abre_a_landing(self):
        resposta = self.client.get('/')
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'landing/home.html')

    @override_settings(PLATAFORMA_WHATSAPP='5517999998888')
    def test_botao_de_whatsapp_usa_o_numero_configurado(self):
        resposta = self.client.get('/')
        self.assertContains(resposta, 'https://wa.me/5517999998888?text=')

    @override_settings(PLATAFORMA_WHATSAPP='')
    def test_sem_numero_o_botao_leva_ao_formulario(self):
        resposta = self.client.get('/')
        self.assertNotContains(resposta, 'wa.me')
        self.assertContains(resposta, 'href="#contato"')

    @override_settings(LANDING_DEMO_SLUG='nao-existe')
    def test_sem_garagem_de_demonstracao_a_pagina_continua_no_ar(self):
        resposta = self.client.get('/')
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, '<iframe')

    def test_vitrine_de_demonstracao_entra_por_iframe_e_pode_ser_emoldurada(self):
        from django.contrib.auth.models import User
        dono = User.objects.create_user('dono_demo', password='x')
        garagem = Garagem.objects.create(dono=dono, nome='Demo', slug='demo', telefone_whatsapp='5517999999999',
                                         email_contato='d@x.com')
        veiculo = Veiculo.objects.create(
            garagem=garagem, titulo='Honda CG 160', slug='cg-160', marca='Honda', modelo='CG 160',
            ano_fabricacao=2022, ano_modelo=2022, quilometragem=1000, combustivel='flex', preco='15000',
        )
        with override_settings(LANDING_DEMO_SLUG='demo'):
            resposta = self.client.get('/')
            self.assertContains(resposta, 'data-src-cliente="/g/demo/"')
            self.assertContains(resposta, f'data-src-simula="/g/demo/veiculos/{veiculo.slug}/#simulador-financiamento"')
            # o painel de demonstração conta a história dos veículos da própria vitrine
            self.assertContains(resposta, 'Honda Cg 160 · 2022')
        vitrine = self.client.get('/g/demo/')
        self.assertEqual(vitrine.headers['X-Frame-Options'], 'SAMEORIGIN')


class InteresseGaragemFormTests(TestCase):
    def test_envio_valido_grava_e_avisa_o_administrador(self):
        resposta = self.client.post('/', _dados())
        self.assertRedirects(resposta, '/?enviado=1#contato', fetch_redirect_response=False)
        interesse = InteresseGaragem.objects.get()
        self.assertEqual(interesse.telefone, '17999991234')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Auto Carlos', mail.outbox[0].subject)

    def test_pagina_de_sucesso_mostra_confirmacao(self):
        resposta = self.client.get('/?enviado=1')
        self.assertContains(resposta, 'Recebemos o seu contato')

    def test_sem_consentimento_nao_grava(self):
        dados = _dados()
        del dados['aceito_contato']
        resposta = self.client.post('/', dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(InteresseGaragem.objects.count(), 0)

    def test_telefone_curto_demais_nao_grava(self):
        resposta = self.client.post('/', _dados(telefone='123'))
        self.assertContains(resposta, 'Informe o DDD e o número')
        self.assertEqual(InteresseGaragem.objects.count(), 0)

    def test_honeypot_preenchido_nao_grava(self):
        self.client.post('/', _dados(site='http://spam.example'))
        self.assertEqual(InteresseGaragem.objects.count(), 0)

    def test_envio_rapido_demais_nao_grava(self):
        self.client.post('/', _dados(iniciado_em=str(time.time())))
        self.assertEqual(InteresseGaragem.objects.count(), 0)
