import shutil
import tempfile
from datetime import date

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from financing.models import TaxaReferencia
from leads.models import Proposta
from tenants.models import Garagem
from vehicles.models import FotoVeiculo, Veiculo
from vehicles.tests import gerar_foto

from .models import TentativaLoginFalha
from .security import LIMITE_POR_USUARIO


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


class TaxaDeJurosNoPainelTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_juros', 'dono_juros@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Juros', slug='garagem-juros',
            telefone_whatsapp='5517999999999', email_contato='dono_juros@example.com',
        )
        self.client.login(username='dono_juros', password='senha12345')
        self.url = reverse('dashboard:dados_garagem')

    def _salvar(self, taxa):
        return self.client.post(self.url, {
            'endereco': '', 'horario_funcionamento': '', 'instagram_url': '', 'facebook_url': '',
            'cor_destaque': '#0F5C4D', 'taxa_juros_mensal_padrao': taxa,
        })

    def test_dono_informa_a_propria_taxa(self):
        self.assertRedirects(self._salvar('1.99'), self.url)
        self.garagem.refresh_from_db()
        self.assertEqual(str(self.garagem.taxa_juros_mensal_padrao), '1.99')

    def test_em_branco_volta_a_usar_a_media_de_mercado(self):
        self.garagem.taxa_juros_mensal_padrao = '1.99'
        self.garagem.save()
        self.assertRedirects(self._salvar(''), self.url)
        self.garagem.refresh_from_db()
        self.assertIsNone(self.garagem.taxa_juros_mensal_padrao)

    def test_taxa_absurda_ou_negativa_e_recusada(self):
        for invalida in ('25', '-1'):
            resp = self._salvar(invalida)
            self.assertEqual(resp.status_code, 200)
            self.garagem.refresh_from_db()
            self.assertIsNone(self.garagem.taxa_juros_mensal_padrao)

    def test_pagina_mostra_a_media_de_mercado_vigente(self):
        TaxaReferencia.objects.create(fonte='bcb-sgs-25471', referencia=date(2026, 7, 1), taxa_mensal='1.98')
        resp = self.client.get(self.url)
        self.assertContains(resp, '1,98% ao mês (ref. 07/2026)')


class LogoECapaDaGaragemTests(TestCase):
    def setUp(self):
        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, ignore_errors=True)
        self.enterContext(override_settings(MEDIA_ROOT=media))

        dono = User.objects.create_user('dono_logo', 'dono_logo@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Logo', slug='garagem-logo',
            telefone_whatsapp='5517999999999', email_contato='dono_logo@example.com',
        )
        self.client.login(username='dono_logo', password='senha12345')
        self.url = reverse('dashboard:dados_garagem')

    def test_dono_envia_logo_e_capa_que_sao_reduzidas(self):
        resp = self.client.post(self.url, {
            'endereco': '', 'horario_funcionamento': '', 'instagram_url': '', 'facebook_url': '',
            'cor_destaque': '#0F5C4D',
            'logo': gerar_foto((2000, 2000), nome='logo.png', formato='PNG', modo='RGBA'),
            'capa': gerar_foto((3000, 900), nome='capa.jpg'),
        })
        self.assertRedirects(resp, self.url)

        self.garagem.refresh_from_db()
        self.assertTrue(self.garagem.logo.name.endswith('.jpg'))  # sempre reencodada em JPEG
        self.assertTrue(self.garagem.capa.name.endswith('.jpg'))
        with Image.open(self.garagem.capa.path) as imagem:
            self.assertEqual(max(imagem.size), 1280)

    def test_vitrine_publica_mostra_logo_e_capa_quando_cadastrados(self):
        self.garagem.logo = gerar_foto((400, 400), nome='logo.jpg')
        self.garagem.capa = gerar_foto((1600, 500), nome='capa.jpg')
        self.garagem.save()

        resp = self.client.get(reverse('storefront:frontpage', kwargs={'garagem_slug': self.garagem.slug}))
        self.assertContains(resp, 'brand-logo')
        self.assertContains(resp, 'site-header--capa')


class LimiteDeTentativasDeLoginTests(TestCase):
    def setUp(self):
        User.objects.create_user('dono_seguro', 'dono_seguro@example.com', 'senha-correta-123')
        self.url = reverse('dashboard:login')

    def test_login_com_senha_certa_funciona(self):
        resp = self.client.post(self.url, {'username': 'dono_seguro', 'password': 'senha-correta-123'})
        self.assertEqual(resp.status_code, 302)

    def test_bloqueia_apos_varias_senhas_erradas_para_o_mesmo_usuario(self):
        for _ in range(LIMITE_POR_USUARIO):
            resp = self.client.post(self.url, {'username': 'dono_seguro', 'password': 'errada'})
            self.assertEqual(resp.status_code, 200)

        # A senha certa não passa mais: o usuário está bloqueado, não só a senha errada.
        resp = self.client.post(self.url, {'username': 'dono_seguro', 'password': 'senha-correta-123'})
        self.assertContains(resp, 'Muitas tentativas de login')

    def test_login_com_sucesso_limpa_as_falhas_anteriores(self):
        for _ in range(LIMITE_POR_USUARIO - 1):
            self.client.post(self.url, {'username': 'dono_seguro', 'password': 'errada'})

        resp = self.client.post(self.url, {'username': 'dono_seguro', 'password': 'senha-correta-123'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(TentativaLoginFalha.objects.filter(usuario='dono_seguro').count(), 0)


class RecuperarSenhaTests(TestCase):
    def setUp(self):
        self.dono = User.objects.create_user('dono_recupera', 'dono_recupera@example.com', 'senha-antiga-123')
        Garagem.objects.create(
            dono=self.dono, nome='Garagem Recupera', slug='garagem-recupera',
            telefone_whatsapp='5517999999999', email_contato='dono_recupera@example.com',
        )

    def test_pedido_com_email_cadastrado_envia_link_por_email(self):
        resp = self.client.post(reverse('dashboard:senha_recuperar'), {'email': 'dono_recupera@example.com'})
        self.assertRedirects(resp, reverse('dashboard:senha_recuperar_enviado'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('senha/redefinir/', mail.outbox[0].body)

    def test_pedido_com_email_desconhecido_nao_revela_isso_e_nao_envia_email(self):
        resp = self.client.post(reverse('dashboard:senha_recuperar'), {'email': 'ninguem@example.com'})
        self.assertRedirects(resp, reverse('dashboard:senha_recuperar_enviado'))
        self.assertEqual(len(mail.outbox), 0)

    def test_link_do_email_permite_trocar_a_senha_e_logar_com_a_nova(self):
        self.client.post(reverse('dashboard:senha_recuperar'), {'email': 'dono_recupera@example.com'})
        link = [linha for linha in mail.outbox[0].body.splitlines() if 'senha/redefinir/' in linha][0].strip()
        caminho = '/' + link.split('/', 3)[-1]  # tira o esquema e o domínio, mantém só o path

        # Primeiro acesso: a view troca o token da URL por um marcador de sessão e redireciona.
        resp = self.client.get(caminho, follow=True)
        form_url = resp.request['PATH_INFO']

        resp = self.client.post(form_url, {'new_password1': 'senha-nova-456', 'new_password2': 'senha-nova-456'})
        self.assertRedirects(resp, reverse('dashboard:senha_redefinir_concluido'))

        self.client.logout()
        resp = self.client.post(
            reverse('dashboard:login'), {'username': 'dono_recupera', 'password': 'senha-nova-456'}
        )
        self.assertEqual(resp.status_code, 302)

    def test_link_invalido_nao_permite_trocar_a_senha(self):
        resp = self.client.get(reverse('dashboard:senha_redefinir', kwargs={'uidb64': 'invalido', 'token': 'x'}))
        self.assertContains(resp, 'inválido')


class AlternarCampoVeiculoViewTests(TestCase):
    def setUp(self):
        dono_a = User.objects.create_user('dono_a_alt', 'a_alt@example.com', 'senha12345')
        self.garagem_a = Garagem.objects.create(
            dono=dono_a, nome='Garagem A Alternar', slug='garagem-a-alternar',
            telefone_whatsapp='5517999999999', email_contato='a_alt@example.com',
        )
        self.veiculo_a = Veiculo.objects.create(
            garagem=self.garagem_a, tipo=Veiculo.Tipo.MOTO, titulo='Moto A', marca='Honda', modelo='CG',
            ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, preco='10000.00',
        )

        dono_b = User.objects.create_user('dono_b_alt', 'b_alt@example.com', 'senha12345')
        garagem_b = Garagem.objects.create(
            dono=dono_b, nome='Garagem B Alternar', slug='garagem-b-alternar',
            telefone_whatsapp='5517999999998', email_contato='b_alt@example.com',
        )
        self.veiculo_b = Veiculo.objects.create(
            garagem=garagem_b, tipo=Veiculo.Tipo.CARRO, titulo='Carro B', marca='Fiat', modelo='Uno',
            ano_fabricacao=2018, ano_modelo=2018, quilometragem=50000,
            combustivel=Veiculo.Combustivel.FLEX, preco='20000.00',
        )

        self.client.login(username='dono_a_alt', password='senha12345')

    def _url(self, veiculo, campo):
        return reverse('dashboard:veiculo_alternar', kwargs={'pk': veiculo.pk, 'campo': campo})

    def test_alterna_destaque_do_proprio_veiculo(self):
        self.assertFalse(self.veiculo_a.destaque)
        resp = self.client.post(self._url(self.veiculo_a, 'destaque'))
        self.assertRedirects(resp, reverse('dashboard:veiculo_list'))
        self.veiculo_a.refresh_from_db()
        self.assertTrue(self.veiculo_a.destaque)

        # Clicar de novo desliga.
        self.client.post(self._url(self.veiculo_a, 'destaque'))
        self.veiculo_a.refresh_from_db()
        self.assertFalse(self.veiculo_a.destaque)

    def test_alterna_disponivel_do_proprio_veiculo(self):
        self.assertTrue(self.veiculo_a.disponivel)
        self.client.post(self._url(self.veiculo_a, 'disponivel'))
        self.veiculo_a.refresh_from_db()
        self.assertFalse(self.veiculo_a.disponivel)

    def test_nao_alterna_veiculo_de_outra_garagem(self):
        resp = self.client.post(self._url(self.veiculo_b, 'destaque'))
        self.assertEqual(resp.status_code, 404)
        self.veiculo_b.refresh_from_db()
        self.assertFalse(self.veiculo_b.destaque)

    def test_campo_fora_da_lista_permitida_e_recusado(self):
        resp = self.client.post(self._url(self.veiculo_a, 'preco'))
        self.assertEqual(resp.status_code, 404)
        self.veiculo_a.refresh_from_db()
        self.assertEqual(str(self.veiculo_a.preco), '10000.00')

    def test_mantem_filtro_da_lista_ao_voltar(self):
        resp = self.client.post(self._url(self.veiculo_a, 'destaque'), {'proximo': '/painel/veiculos/?tipo=moto'})
        self.assertRedirects(resp, '/painel/veiculos/?tipo=moto')

    def test_url_externa_em_proximo_e_ignorada(self):
        resp = self.client.post(self._url(self.veiculo_a, 'destaque'), {'proximo': 'https://outrosite.com/roubo'})
        self.assertRedirects(resp, reverse('dashboard:veiculo_list'))

    def test_bloqueado_quando_garagem_esta_atrasada(self):
        self.garagem_a.status = Garagem.Status.ATRASADO
        self.garagem_a.save()
        resp = self.client.post(self._url(self.veiculo_a, 'destaque'))
        self.assertRedirects(resp, reverse('dashboard:assinatura'))
        self.veiculo_a.refresh_from_db()
        self.assertFalse(self.veiculo_a.destaque)


class FiltroEOrdenacaoDeVeiculosTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_filtro', 'dono_filtro@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Filtro', slug='garagem-filtro',
            telefone_whatsapp='5517999999999', email_contato='dono_filtro@example.com',
        )
        self.moto_barata = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.MOTO, titulo='Moto Barata', marca='Honda', modelo='CG',
            ano_fabricacao=2015, ano_modelo=2015, quilometragem=60000,
            combustivel=Veiculo.Combustivel.FLEX, preco='8000.00', disponivel=True,
        )
        self.carro_caro = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.CARRO, titulo='Carro Caro', marca='Toyota', modelo='Corolla',
            ano_fabricacao=2023, ano_modelo=2023, quilometragem=5000,
            combustivel=Veiculo.Combustivel.FLEX, preco='120000.00', disponivel=False,
        )
        self.client.login(username='dono_filtro', password='senha12345')
        self.url = reverse('dashboard:veiculo_list')

    def test_sem_filtro_mostra_todos_do_mais_recente_para_o_mais_antigo(self):
        resp = self.client.get(self.url)
        self.assertEqual(list(resp.context['veiculos']), [self.carro_caro, self.moto_barata])

    def test_filtro_por_tipo(self):
        resp = self.client.get(self.url, {'tipo': 'moto'})
        self.assertEqual(list(resp.context['veiculos']), [self.moto_barata])

    def test_filtro_por_disponibilidade(self):
        resp = self.client.get(self.url, {'disponivel': 'nao'})
        self.assertEqual(list(resp.context['veiculos']), [self.carro_caro])

    def test_ordena_por_preco_crescente(self):
        resp = self.client.get(self.url, {'ordenar': 'preco'})
        self.assertEqual(list(resp.context['veiculos']), [self.moto_barata, self.carro_caro])

    def test_ordena_por_preco_decrescente(self):
        resp = self.client.get(self.url, {'ordenar': '-preco'})
        self.assertEqual(list(resp.context['veiculos']), [self.carro_caro, self.moto_barata])

    def test_filtro_so_considera_veiculos_da_propria_garagem(self):
        outro_dono = User.objects.create_user('dono_filtro_b', 'b@example.com', 'senha12345')
        outra_garagem = Garagem.objects.create(
            dono=outro_dono, nome='Outra Garagem', slug='outra-garagem-filtro',
            telefone_whatsapp='5517999999998', email_contato='b@example.com',
        )
        Veiculo.objects.create(
            garagem=outra_garagem, tipo=Veiculo.Tipo.MOTO, titulo='Moto de Outra Garagem', marca='Yamaha',
            modelo='Factor', ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, preco='9000.00',
        )
        resp = self.client.get(self.url)
        self.assertEqual(list(resp.context['veiculos']), [self.carro_caro, self.moto_barata])
