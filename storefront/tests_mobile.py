"""Teste de responsividade no celular, com Chromium de verdade (Playwright).

Não roda na suíte normal (é lento e precisa de internet, pois o site carrega o
Bootstrap e as fontes por CDN). Para rodar: scripts/testar_mobile.sh
"""
import os
import unittest
import urllib.request
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from leads.models import Proposta
from tenants.models import Garagem
from vehicles.models import Veiculo

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

# O Playwright síncrono roda um event loop na thread; sem isso o Django recusa usar o ORM no teardown.
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

LARGURAS = (320, 360, 390, 430, 768)
LARGURA_MAXIMA_CELULAR = 430
CDN_DO_BOOTSTRAP = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css'

MEDE_PAGINA = """() => {
    const vw = document.documentElement.clientWidth;
    const fora = [...document.querySelectorAll('body *')].filter(e => {
        const r = e.getBoundingClientRect();
        return r.width > 0 && getComputedStyle(e).position !== 'fixed'
            && r.right > vw + 1 && !e.closest('.carrossel-trilho');
    }).slice(0, 3).map(e => e.tagName.toLowerCase() + '.' + String(e.className).split(' ')[0]);
    const camposPequenos = [...document.querySelectorAll(
        'input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=color]), select, textarea'
    )].filter(e => e.getBoundingClientRect().width > 0 && parseFloat(getComputedStyle(e).fontSize) < 16).length;
    return {larguraDoc: document.documentElement.scrollWidth, vw, fora, camposPequenos};
}"""


@unittest.skipUnless(os.environ.get('TESTE_MOBILE') == '1', 'Defina TESTE_MOBILE=1 (ou rode scripts/testar_mobile.sh).')
@unittest.skipIf(sync_playwright is None, 'Rode: pip install -r requirements-dev.txt')
class ResponsividadeMobileTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        try:
            urllib.request.urlopen(CDN_DO_BOOTSTRAP, timeout=5).close()
        except OSError as exc:
            raise unittest.SkipTest(f'Sem internet para o CDN do Bootstrap: {exc}')
        try:
            cls.playwright = sync_playwright().start()
            cls.addClassCleanup(cls.playwright.stop)
            cls.browser = cls.playwright.chromium.launch()
            cls.addClassCleanup(cls.browser.close)
        except Exception as exc:
            raise unittest.SkipTest(f'Chromium indisponível ({exc}). Rode: playwright install chromium')

    def setUp(self):
        dono = User.objects.create_user('dono_mobile', 'dono_mobile@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Mobile', slug='garagem-mobile',
            telefone_whatsapp='5517999999999', email_contato='contato@example.com',
            endereco='Avenida com um nome bem comprido, 1234 - Centro',
            horario_funcionamento='Seg a Sex, 8h às 18h | Sáb, 8h às 12h',
            instagram_url='https://instagram.com/garagemmobile',
        )
        base = dict(
            garagem=self.garagem, marca='Honda', modelo='CG', ano_fabricacao=2011, ano_modelo=2012,
            quilometragem=121212, combustivel='gasolina', preco='11900.00',
        )
        self.moto = Veiculo.objects.create(
            titulo='Honda CG 160 Titan Start com um título bem comprido para testar a quebra de linha',
            tipo='moto', cilindrada=160, destaque=True, aceita_troca=True, **base,
        )
        Veiculo.objects.create(titulo='Yamaha Fazer 250', tipo='moto', cilindrada=250, destaque=True, **base)
        Veiculo.objects.create(titulo='VW Gol 1.6', tipo='carro', potencia_motor='1.6', destaque=True, **base)
        for i in range(3):
            Veiculo.objects.create(titulo=f'Moto extra {i}', tipo='moto', cilindrada=125, **base)
        Proposta.objects.create(
            garagem=self.garagem, veiculo=self.moto, nome='Cliente com um nome muito comprido da Silva Sauro',
            telefone='17999999999', mensagem='Mensagem bem longa, ' * 12,
        )

    def _paginas(self):
        g, v = self.garagem.slug, self.moto
        return [
            ('vitrine', f'/g/{g}/'),
            ('vitrine-filtrada', f'/g/{g}/?tipo=moto'),
            ('veiculo', f'/g/{g}/veiculos/{v.slug}/'),
            ('proposta', f'/g/{g}/veiculos/{v.slug}/proposta/'),
            ('contato', f'/g/{g}/contato/'),
            ('privacidade', f'/g/{g}/privacidade/'),
            ('termos', '/termos/'),
            ('login', '/painel/login/'),
            ('painel-home', '/painel/'),
            ('painel-veiculos', '/painel/veiculos/'),
            ('painel-veiculo-novo', '/painel/veiculos/novo/'),
            ('painel-veiculo-editar', f'/painel/veiculos/{v.pk}/editar/'),
            ('painel-propostas', '/painel/propostas/'),
            ('painel-assinatura', '/painel/assinatura/'),
            ('painel-dados', '/painel/dados/'),
        ]

    def _entrar_no_painel(self, pagina):
        pagina.goto(self.live_server_url + '/painel/login/')
        pagina.fill('#id_username', 'dono_mobile')
        pagina.fill('#id_password', 'senha12345')
        pagina.click('button[type=submit]')
        pagina.wait_for_url('**/painel/')

    def test_nenhuma_tela_estoura_a_largura_nem_tem_campo_pequeno_no_celular(self):
        pasta_prints = Path(settings.BASE_DIR) / 'test-artifacts' / 'mobile'
        tirar_prints = os.environ.get('MOBILE_SCREENSHOTS') == '1'
        problemas = []

        for largura in LARGURAS:
            contexto = self.browser.new_context(
                viewport={'width': largura, 'height': 800}, has_touch=True, is_mobile=True,
            )
            pagina = contexto.new_page()
            self._entrar_no_painel(pagina)
            for nome, caminho in self._paginas():
                pagina.goto(self.live_server_url + caminho, wait_until='networkidle')
                pagina.evaluate('document.fonts.ready')
                medidas = pagina.evaluate(MEDE_PAGINA)

                if medidas['larguraDoc'] > medidas['vw'] + 1:
                    problemas.append(
                        f"{largura}px {nome}: página com {medidas['larguraDoc']}px de largura "
                        f"(tela de {medidas['vw']}px). Elementos: {medidas['fora']}"
                    )
                if largura <= LARGURA_MAXIMA_CELULAR and medidas['camposPequenos']:
                    problemas.append(f"{largura}px {nome}: {medidas['camposPequenos']} campo(s) com fonte menor que 16px")

                if tirar_prints:
                    destino = pasta_prints / str(largura)
                    destino.mkdir(parents=True, exist_ok=True)
                    pagina.screenshot(path=str(destino / f'{nome}.png'), full_page=True)
            contexto.close()

        self.assertEqual(problemas, [], '\n' + '\n'.join(problemas))
