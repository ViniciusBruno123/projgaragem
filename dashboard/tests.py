from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from leads.models import Proposta
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
            'cor_destaque': '#123456',
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


class AtualizarStatusPropostaViewTests(TestCase):
    def setUp(self):
        self.dono_a = User.objects.create_user('dono_a_prop', 'a@example.com', 'senha12345')
        self.garagem_a = Garagem.objects.create(
            dono=self.dono_a, nome='Garagem A', slug='garagem-a-prop',
            telefone_whatsapp='5517999999999', email_contato='a@example.com',
        )
        self.proposta_a = Proposta.objects.create(
            garagem=self.garagem_a, nome='Cliente A', telefone='17988887777',
        )

        dono_b = User.objects.create_user('dono_b_prop', 'b@example.com', 'senha12345')
        self.garagem_b = Garagem.objects.create(
            dono=dono_b, nome='Garagem B', slug='garagem-b-prop',
            telefone_whatsapp='5517999999998', email_contato='b@example.com',
        )
        self.proposta_b = Proposta.objects.create(
            garagem=self.garagem_b, nome='Cliente B', telefone='17988886666',
        )

        self.client.login(username='dono_a_prop', password='senha12345')

    def test_dono_atualiza_status_da_propria_proposta(self):
        url = reverse('dashboard:proposta_status', kwargs={'pk': self.proposta_a.pk})
        resp = self.client.post(url, {'status': Proposta.Status.CONVERTIDA})
        self.assertRedirects(resp, reverse('dashboard:proposta_list'))

        self.proposta_a.refresh_from_db()
        self.assertEqual(self.proposta_a.status, Proposta.Status.CONVERTIDA)

    def test_dono_nao_atualiza_proposta_de_outra_garagem(self):
        url = reverse('dashboard:proposta_status', kwargs={'pk': self.proposta_b.pk})
        resp = self.client.post(url, {'status': Proposta.Status.CONVERTIDA})
        self.assertEqual(resp.status_code, 404)

        self.proposta_b.refresh_from_db()
        self.assertEqual(self.proposta_b.status, Proposta.Status.NOVA)

    def test_status_invalido_e_ignorado(self):
        url = reverse('dashboard:proposta_status', kwargs={'pk': self.proposta_a.pk})
        self.client.post(url, {'status': 'nao-existe'})

        self.proposta_a.refresh_from_db()
        self.assertEqual(self.proposta_a.status, Proposta.Status.NOVA)
