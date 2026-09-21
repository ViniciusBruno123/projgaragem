from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tenants.models import Garagem

from .models import Proposta


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
