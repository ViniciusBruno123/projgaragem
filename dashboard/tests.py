from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from tenants.models import Garagem


class DadosGaragemViewTests(TestCase):
    def setUp(self):
        self.dono = User.objects.create_user('dono_dados', 'dono_dados@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=self.dono, nome='Garagem Dados', slug='garagem-dados',
            telefone_whatsapp='5517999999999', email_contato='dono_dados@example.com',
        )
        self.client.login(username='dono_dados', password='senha12345')

    def test_dono_atualiza_dados_institucionais(self):
        url = reverse('dashboard:dados_garagem')
        resp = self.client.post(url, {
            'endereco': 'Rua Nova, 100',
            'horario_funcionamento': 'Seg a Sex, 9h às 17h',
            'instagram_url': 'https://instagram.com/garagemteste',
            'facebook_url': '',
        })
        self.assertRedirects(resp, url)

        self.garagem.refresh_from_db()
        self.assertEqual(self.garagem.endereco, 'Rua Nova, 100')
        self.assertEqual(self.garagem.horario_funcionamento, 'Seg a Sex, 9h às 17h')
        self.assertEqual(self.garagem.instagram_url, 'https://instagram.com/garagemteste')

    def test_requer_login(self):
        self.client.logout()
        resp = self.client.get(reverse('dashboard:dados_garagem'))
        self.assertEqual(resp.status_code, 302)
