import io

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image

from tenants.models import Garagem

from .forms import FotoVeiculoForm
from .imagens import FotoInvalida, otimizar_foto
from .models import Veiculo
from .services import veiculos_semelhantes


def gerar_foto(tamanho=(3000, 2000), formato='JPEG', modo='RGB', exif=None, nome=None):
    """Foto de teste com ruído (não comprime demais), como um arquivo enviado."""
    imagem = Image.effect_noise(tamanho, 60).convert(modo)
    saida = io.BytesIO()
    extras = {'exif': exif} if exif is not None else {}
    imagem.save(saida, formato, **extras)
    nome = nome or f'foto.{formato.lower()}'
    return SimpleUploadedFile(nome, saida.getvalue(), content_type=f'image/{formato.lower()}')


def abrir(resultado):
    return Image.open(io.BytesIO(resultado.read()))


class VeiculoTipoValidationTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_veiculo', 'dono_veiculo@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Teste', slug='garagem-teste-veiculo',
            telefone_whatsapp='5517999999999', email_contato='dono_veiculo@example.com',
        )

    def _veiculo(self, **kwargs):
        base = dict(
            garagem=self.garagem, titulo='Veículo', slug='veiculo-teste', marca='Marca',
            modelo='Modelo', ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, preco='10000.00',
        )
        base.update(kwargs)
        return Veiculo(**base)

    def test_moto_com_potencia_motor_e_invalida(self):
        veiculo = self._veiculo(tipo=Veiculo.Tipo.MOTO, potencia_motor='1.6')
        with self.assertRaises(ValidationError):
            veiculo.full_clean()

    def test_carro_com_cilindrada_e_invalido(self):
        veiculo = self._veiculo(tipo=Veiculo.Tipo.CARRO, cilindrada=160)
        with self.assertRaises(ValidationError):
            veiculo.full_clean()

    def test_moto_com_cilindrada_e_valida(self):
        veiculo = self._veiculo(tipo=Veiculo.Tipo.MOTO, cilindrada=160)
        veiculo.full_clean()  # não deve levantar

    def test_carro_com_potencia_motor_e_valido(self):
        veiculo = self._veiculo(tipo=Veiculo.Tipo.CARRO, potencia_motor='2.0')
        veiculo.full_clean()  # não deve levantar


class VeiculoSlugAutomaticoTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_slug', 'dono_slug@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Slug', slug='garagem-slug',
            telefone_whatsapp='5517999999999', email_contato='dono_slug@example.com',
        )

    def _criar(self, titulo):
        return Veiculo.objects.create(
            garagem=self.garagem, titulo=titulo, marca='Honda', modelo='CG',
            ano_fabricacao=2022, ano_modelo=2022, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, preco='10000.00',
        )

    def test_slug_gerado_a_partir_do_titulo(self):
        veiculo = self._criar('Honda CG 160 2022')
        self.assertEqual(veiculo.slug, 'honda-cg-160-2022')

    def test_slugs_duplicados_recebem_sufixo(self):
        v1 = self._criar('Honda CG 160')
        v2 = self._criar('Honda CG 160')
        self.assertEqual(v1.slug, 'honda-cg-160')
        self.assertEqual(v2.slug, 'honda-cg-160-2')

    def test_slug_nao_muda_ao_editar_titulo(self):
        veiculo = self._criar('Honda CG 160')
        slug_original = veiculo.slug
        veiculo.titulo = 'Honda CG 160 Revisada'
        veiculo.save()
        self.assertEqual(veiculo.slug, slug_original)


class OtimizarFotoTests(SimpleTestCase):
    def test_reduz_para_o_lado_maximo_mantendo_proporcao(self):
        original = gerar_foto((3000, 2000))
        resultado = otimizar_foto(original)
        imagem = abrir(resultado)
        self.assertEqual(imagem.format, 'JPEG')
        self.assertEqual(max(imagem.size), 1280)
        self.assertEqual(imagem.size, (1280, 853))
        self.assertLess(resultado.size, original.size)

    def test_nao_amplia_foto_pequena(self):
        imagem = abrir(otimizar_foto(gerar_foto((400, 300))))
        self.assertEqual(imagem.size, (400, 300))

    def test_respeita_a_orientacao_do_celular(self):
        exif = Image.Exif()
        exif[0x0112] = 6  # girar 90 graus
        imagem = abrir(otimizar_foto(gerar_foto((300, 200), exif=exif)))
        self.assertEqual(imagem.size, (200, 300))

    def test_remove_metadados(self):
        exif = Image.Exif()
        exif[0x010F] = 'Marca do celular'
        imagem = abrir(otimizar_foto(gerar_foto((300, 200), exif=exif)))
        self.assertEqual(len(imagem.getexif()), 0)

    def test_png_transparente_vira_jpeg_com_fundo_branco(self):
        saida = io.BytesIO()
        Image.new('RGBA', (100, 100), (0, 0, 0, 0)).save(saida, 'PNG')
        arquivo = SimpleUploadedFile('logo.png', saida.getvalue(), content_type='image/png')
        resultado = otimizar_foto(arquivo)
        imagem = abrir(resultado)
        self.assertEqual(imagem.format, 'JPEG')
        self.assertTrue(resultado.name.endswith('.jpg'))
        self.assertGreater(min(imagem.getpixel((50, 50))), 250)

    def test_arquivo_que_nao_e_imagem(self):
        arquivo = SimpleUploadedFile('foto.jpg', b'isto nao e uma imagem')
        with self.assertRaises(FotoInvalida):
            otimizar_foto(arquivo)

    @override_settings(FOTO_MAX_PIXELS=1000)
    def test_resolucao_alta_demais(self):
        with self.assertRaises(FotoInvalida):
            otimizar_foto(gerar_foto((100, 100)))


class FotoVeiculoFormTests(TestCase):
    def test_foto_grande_e_reduzida_ao_validar(self):
        form = FotoVeiculoForm(data={'ordem': 0}, files={'imagem': gerar_foto((3000, 2000))})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(max(abrir(form.cleaned_data['imagem']).size), 1280)

    @override_settings(FOTO_UPLOAD_MAX_BYTES=1000)
    def test_foto_acima_do_limite_e_recusada_com_mensagem_clara(self):
        form = FotoVeiculoForm(data={'ordem': 0}, files={'imagem': gerar_foto((200, 200), formato='PNG')})
        self.assertFalse(form.is_valid())
        self.assertIn('limite', form.errors['imagem'][0])

    def test_arquivo_que_nao_e_imagem_e_recusado(self):
        arquivo = SimpleUploadedFile('foto.jpg', b'isto nao e uma imagem', content_type='image/jpeg')
        form = FotoVeiculoForm(data={'ordem': 0}, files={'imagem': arquivo})
        self.assertFalse(form.is_valid())
        self.assertIn('imagem', form.errors)

    def test_so_ordem_diferente_do_inicial_nao_conta_como_alteracao(self):
        # Um slot vazio do formset (extra=6 no painel) só com "ordem" diferente do
        # pré-preenchido — por exemplo, um scroll acidental sobre o campo numérico focado
        # (ver static/js/numero_sem_scroll.js) — não pode virar "campo obrigatório" pra foto.
        form = FotoVeiculoForm(data={'ordem': 99}, initial={'ordem': 4}, files={})
        self.assertFalse(form.has_changed())

    def test_imagem_ou_principal_diferentes_continuam_contando_como_alteracao(self):
        form = FotoVeiculoForm(data={'ordem': 4, 'principal': 'on'}, initial={'ordem': 4}, files={})
        self.assertTrue(form.has_changed())

        form = FotoVeiculoForm(data={'ordem': 4}, initial={'ordem': 4}, files={'imagem': gerar_foto((100, 100))})
        self.assertTrue(form.has_changed())


class ExibicaoDoVeiculoTests(SimpleTestCase):
    def test_ano_curto_usa_os_dois_ultimos_digitos(self):
        self.assertEqual(Veiculo(ano_fabricacao=1999, ano_modelo=2000).ano_curto, '99/00')
        self.assertEqual(Veiculo(ano_fabricacao=2021, ano_modelo=2022).ano_curto, '21/22')

    def test_ano_curto_aparece_uma_vez_quando_fabricacao_e_modelo_coincidem(self):
        self.assertEqual(Veiculo(ano_fabricacao=2023, ano_modelo=2023).ano_curto, '23')
        self.assertEqual(Veiculo(ano_fabricacao=2005, ano_modelo=2005).ano_curto, '05')

    def test_etanol_e_exibido_como_alcool(self):
        self.assertEqual(Veiculo(combustivel='etanol').get_combustivel_display(), 'Álcool')


class VeiculosSemelhantesTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_semelhantes', 'dono_semelhantes@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Semelhantes', slug='garagem-semelhantes',
            telefone_whatsapp='5517999999999', email_contato='dono_semelhantes@example.com',
        )
        self.base = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.MOTO, titulo='Base', marca='Honda', modelo='CG',
            ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, cilindrada=150, preco='10000.00',
        )
        # sem isso self.base.preco fica como a string passada acima, não como Decimal
        # (Model.objects.create não recarrega do banco) — na view de verdade isso nunca
        # acontece, porque o veículo sempre vem de uma consulta (get_object_or_404).
        self.base.refresh_from_db()

    def _moto(self, titulo, **extra):
        base = dict(
            garagem=self.garagem, tipo=Veiculo.Tipo.MOTO, marca='Honda', modelo='CG',
            ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, cilindrada=150, preco='10000.00',
        )
        base.update(extra)
        return Veiculo.objects.create(titulo=titulo, **base)

    def test_ordena_por_tipo_depois_preco_depois_marca_depois_ano_depois_motor(self):
        preco_identico_marca_diferente = self._moto('Preço idêntico, marca diferente', marca='Yamaha')
        preco_perto = self._moto(
            'Preço perto', preco='10100.00', marca='Suzuki', ano_fabricacao=2015, ano_modelo=2015, cilindrada=125,
        )
        preco_longe = self._moto('Preço longe', preco='50000.00')
        tipo_diferente = Veiculo.objects.create(
            garagem=self.garagem, tipo=Veiculo.Tipo.CARRO, titulo='Tipo diferente', marca='Honda', modelo='Civic',
            ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, potencia_motor='1.6', preco='10000.00',
        )

        resultado = veiculos_semelhantes(self.base)
        self.assertEqual(resultado, [preco_identico_marca_diferente, preco_perto, preco_longe, tipo_diferente])

    def test_exclui_o_proprio_veiculo_e_indisponiveis_e_de_outra_garagem(self):
        self._moto('Indisponível', disponivel=False)
        outro_dono = User.objects.create_user('dono_semelhantes_b', 'b@example.com', 'senha12345')
        outra_garagem = Garagem.objects.create(
            dono=outro_dono, nome='Outra Garagem', slug='outra-garagem-semelhantes',
            telefone_whatsapp='5517999999998', email_contato='b@example.com',
        )
        Veiculo.objects.create(
            garagem=outra_garagem, tipo=Veiculo.Tipo.MOTO, titulo='De outra garagem', marca='Honda', modelo='CG',
            ano_fabricacao=2020, ano_modelo=2020, quilometragem=1000,
            combustivel=Veiculo.Combustivel.FLEX, cilindrada=150, preco='10000.00',
        )
        self.assertEqual(veiculos_semelhantes(self.base), [])

    def test_no_maximo_5_mas_menos_se_a_garagem_nao_tiver(self):
        self.assertEqual(veiculos_semelhantes(self.base), [])  # só a base existe

        for i in range(7):
            self._moto(f'Moto {i}')
        self.assertEqual(len(veiculos_semelhantes(self.base)), 5)
