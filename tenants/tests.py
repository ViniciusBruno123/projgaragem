from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Garagem


class TermosDeUsoTests(TestCase):
    def test_pagina_de_termos_e_publica(self):
        resp = self.client.get(reverse('termos_uso'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Termos de uso e privacidade')

    def test_login_do_painel_linka_os_termos(self):
        resp = self.client.get(reverse('dashboard:login'))
        self.assertContains(resp, reverse('termos_uso'))

    def test_painel_linka_os_termos_no_rodape(self):
        dono = User.objects.create_user('dono_termos', 'dono_termos@example.com', 'senha12345')
        Garagem.objects.create(
            dono=dono, nome='Garagem Termos', slug='garagem-termos',
            telefone_whatsapp='5517999999999', email_contato='dono_termos@example.com',
        )
        self.client.login(username='dono_termos', password='senha12345')
        resp = self.client.get(reverse('dashboard:home'))
        self.assertContains(resp, reverse('termos_uso'))


class LimiteDeVeiculosPorPlanoTests(TestCase):
    def _garagem(self, **extra):
        dono = User.objects.create_user(
            f'dono_plano_{Garagem.objects.count()}', f'p{Garagem.objects.count()}@example.com', 'senha12345',
        )
        return Garagem.objects.create(
            dono=dono, nome='Garagem Plano', slug=f'garagem-plano-{Garagem.objects.count()}',
            telefone_whatsapp='5517999999999', email_contato=dono.email, **extra,
        )

    def test_plano_padrao_e_basico_com_limite_de_50(self):
        garagem = self._garagem()
        self.assertEqual(garagem.plano, Garagem.Plano.BASICO)
        self.assertEqual(garagem.limite_veiculos, 50)

    def test_limites_dos_outros_planos(self):
        self.assertEqual(self._garagem(plano=Garagem.Plano.INTERMEDIARIO).limite_veiculos, 100)
        self.assertEqual(self._garagem(plano=Garagem.Plano.AVANCADO).limite_veiculos, 300)
