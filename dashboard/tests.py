import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from leads.models import Proposta
from tenants.models import Garagem
from vehicles.models import FotoVeiculo, Veiculo
from vehicles.tests import gerar_foto


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


class UploadDeFotoViewTests(TestCase):
    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        self.enterContext(override_settings(MEDIA_ROOT=media))

        dono = User.objects.create_user('dono_foto', 'dono_foto@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Foto', slug='garagem-foto',
            telefone_whatsapp='5517999999999', email_contato='dono_foto@example.com',
        )
        self.client.login(username='dono_foto', password='senha12345')

    def _dados_veiculo(self, **extra):
        return {
            'tipo': 'moto', 'titulo': 'Moto Teste', 'marca': 'Honda', 'modelo': 'CG',
            'ano_fabricacao': 2022, 'ano_modelo': 2022, 'quilometragem': 1000,
            'combustivel': 'flex', 'preco': '10000.00', 'disponivel': 'on',
            'fotos-TOTAL_FORMS': 1, 'fotos-INITIAL_FORMS': 0,
            'fotos-MIN_NUM_FORMS': 0, 'fotos-MAX_NUM_FORMS': 1000,
            **extra,
        }

    def _criar_com_foto(self):
        return self.client.post(reverse('dashboard:veiculo_create'), self._dados_veiculo(**{
            'fotos-0-imagem': gerar_foto((3000, 2000), nome='IMG_0001.JPG'),
            'fotos-0-principal': 'on', 'fotos-0-ordem': 0,
        }))

    def test_foto_grande_e_salva_reduzida_em_jpeg(self):
        resp = self._criar_com_foto()
        self.assertRedirects(resp, reverse('dashboard:veiculo_list'))

        foto = FotoVeiculo.objects.get()
        self.assertTrue(foto.imagem.name.endswith('.jpg'))
        with Image.open(foto.imagem.path) as imagem:
            self.assertEqual(imagem.format, 'JPEG')
            self.assertEqual(max(imagem.size), 1280)

    @override_settings(FOTO_UPLOAD_MAX_BYTES=1000)
    def test_foto_acima_do_limite_mostra_erro_e_nao_salva_o_veiculo(self):
        resp = self._criar_com_foto()
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'o limite é')
        self.assertEqual(Veiculo.objects.count(), 0)
        self.assertEqual(FotoVeiculo.objects.count(), 0)

    def test_editar_veiculo_sem_reenviar_foto_nao_reprocessa_o_arquivo(self):
        self._criar_com_foto()
        foto = FotoVeiculo.objects.get()
        nome_original = foto.imagem.name

        resp = self.client.post(
            reverse('dashboard:veiculo_update', kwargs={'pk': foto.veiculo.pk}),
            self._dados_veiculo(**{
                'titulo': 'Moto Teste Revisada',
                'fotos-TOTAL_FORMS': 2, 'fotos-INITIAL_FORMS': 1,
                'fotos-0-id': foto.pk, 'fotos-0-veiculo': foto.veiculo.pk,
                'fotos-0-principal': 'on', 'fotos-0-ordem': 0,
                'fotos-1-ordem': 0,
            }),
        )
        self.assertRedirects(resp, reverse('dashboard:veiculo_list'))

        foto.refresh_from_db()
        self.assertEqual(foto.imagem.name, nome_original)
        self.assertEqual(foto.veiculo.titulo, 'Moto Teste Revisada')
