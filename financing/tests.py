import io
import json
from datetime import date
from decimal import Decimal
from unittest.mock import patch
from urllib.error import URLError

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils.formats import number_format

from tenants.models import Garagem
from vehicles.models import Veiculo

from .models import TaxaReferencia
from .services import (
    FONTE_BCB, TaxaIndisponivel, buscar_taxa_bcb, calcular_parcela_price, taxa_para,
)

URLOPEN = 'financing.services.urllib.request.urlopen'


def resposta_bcb(data='01/07/2026', valor='1.98'):
    return io.BytesIO(json.dumps([{'data': data, 'valor': valor}]).encode())


class CalcularParcelaPriceTests(SimpleTestCase):
    def test_taxa_zero_divide_igualmente(self):
        parcela = calcular_parcela_price(Decimal('12000'), Decimal('0'), 12)
        self.assertEqual(parcela, Decimal('1000.00'))

    def test_taxa_conhecida_bate_com_calculo_manual(self):
        # PV=10000, i=2%, n=12 -> PMT = 10000 * (0.02*1.02^12)/(1.02^12-1) = 945.60
        parcela = calcular_parcela_price(Decimal('10000'), Decimal('2'), 12)
        self.assertEqual(parcela, Decimal('945.60'))

    def test_uma_parcela_igual_ao_valor_financiado_mais_juros(self):
        parcela = calcular_parcela_price(Decimal('1000'), Decimal('5'), 1)
        self.assertEqual(parcela, Decimal('1050.00'))


class BuscarTaxaBcbTests(SimpleTestCase):
    @patch(URLOPEN)
    def test_le_o_ultimo_valor_publicado(self, urlopen):
        urlopen.return_value = resposta_bcb('01/07/2026', '1.98')
        self.assertEqual(buscar_taxa_bcb(), (date(2026, 7, 1), Decimal('1.98')))

    @patch(URLOPEN, side_effect=URLError('sem rede'))
    def test_falha_de_rede(self, urlopen):
        with self.assertRaises(TaxaIndisponivel):
            buscar_taxa_bcb()

    @patch(URLOPEN)
    def test_resposta_que_nao_e_json(self, urlopen):
        urlopen.return_value = io.BytesIO(b'<html>manutencao</html>')
        with self.assertRaises(TaxaIndisponivel):
            buscar_taxa_bcb()

    @patch(URLOPEN)
    def test_resposta_vazia(self, urlopen):
        urlopen.return_value = io.BytesIO(b'[]')
        with self.assertRaises(TaxaIndisponivel):
            buscar_taxa_bcb()


class GaragemDeTeste:
    def criar_garagem(self, **extra):
        dono = User.objects.create_user('dono_taxa', 'dono_taxa@example.com', 'senha12345')
        return Garagem.objects.create(
            dono=dono, nome='Garagem Taxa', slug='garagem-taxa',
            telefone_whatsapp='5517999999999', email_contato='dono_taxa@example.com', **extra,
        )


class TaxaParaTests(GaragemDeTeste, TestCase):
    def test_sem_taxa_propria_nem_media_usa_a_estimada(self):
        taxa = taxa_para(self.criar_garagem())
        self.assertEqual((taxa.origem, taxa.valor), ('estimada', Decimal('2.00')))

    def test_sem_taxa_propria_usa_a_media_de_mercado_mais_recente(self):
        TaxaReferencia.objects.create(fonte=FONTE_BCB, referencia=date(2026, 6, 1), taxa_mensal='1.97')
        TaxaReferencia.objects.create(fonte=FONTE_BCB, referencia=date(2026, 7, 1), taxa_mensal='1.98')
        taxa = taxa_para(self.criar_garagem())
        self.assertEqual((taxa.origem, taxa.valor, taxa.referencia), ('mercado', Decimal('1.98'), date(2026, 7, 1)))

    def test_taxa_da_garagem_tem_prioridade_sobre_a_media(self):
        TaxaReferencia.objects.create(fonte=FONTE_BCB, referencia=date(2026, 7, 1), taxa_mensal='1.98')
        taxa = taxa_para(self.criar_garagem(taxa_juros_mensal_padrao=Decimal('1.50')))
        self.assertEqual((taxa.origem, taxa.valor), ('garagem', Decimal('1.50')))

    def test_taxa_zero_da_garagem_e_respeitada(self):
        TaxaReferencia.objects.create(fonte=FONTE_BCB, referencia=date(2026, 7, 1), taxa_mensal='1.98')
        taxa = taxa_para(self.criar_garagem(taxa_juros_mensal_padrao=Decimal('0')))
        self.assertEqual((taxa.origem, taxa.valor), ('garagem', Decimal('0')))


class AtualizarTaxaMediaCommandTests(TestCase):
    @patch(URLOPEN)
    def test_salva_a_taxa_e_e_idempotente(self, urlopen):
        urlopen.side_effect = lambda *a, **k: resposta_bcb()
        call_command('atualizar_taxa_media')
        call_command('atualizar_taxa_media')
        taxa = TaxaReferencia.objects.get()
        self.assertEqual((taxa.referencia, taxa.taxa_mensal), (date(2026, 7, 1), Decimal('1.98')))

    @patch(URLOPEN)
    def test_corrige_o_valor_do_mesmo_mes(self, urlopen):
        urlopen.side_effect = [resposta_bcb(valor='1.98'), resposta_bcb(valor='2.05')]
        call_command('atualizar_taxa_media')
        call_command('atualizar_taxa_media')
        self.assertEqual(TaxaReferencia.objects.get().taxa_mensal, Decimal('2.05'))

    @patch(URLOPEN, side_effect=URLError('sem rede'))
    def test_falha_de_rede_da_erro_e_preserva_a_taxa_anterior(self, urlopen):
        TaxaReferencia.objects.create(fonte=FONTE_BCB, referencia=date(2026, 6, 1), taxa_mensal='1.97')
        with self.assertRaises(CommandError):
            call_command('atualizar_taxa_media')
        self.assertEqual(TaxaReferencia.objects.get().taxa_mensal, Decimal('1.97'))


class SimuladorUsaATaxaTests(GaragemDeTeste, TestCase):
    def _pagina_do_veiculo(self, garagem):
        veiculo = Veiculo.objects.create(
            garagem=garagem, titulo='Moto Simulada', marca='Honda', modelo='CG', ano_fabricacao=2022,
            ano_modelo=2022, quilometragem=1000, combustivel='flex', preco='10000.00',
        )
        url = reverse('storefront:detalhe_veiculo', kwargs={'garagem_slug': garagem.slug, 'veiculo_slug': veiculo.slug})
        return self.client.get(url, {'valor_entrada': '0', 'numero_parcelas': '12'})

    def _parcela(self, taxa):
        return number_format(calcular_parcela_price(Decimal('10000'), Decimal(taxa), 12), decimal_pos=2, force_grouping=True)

    def test_mostra_a_media_de_mercado_e_calcula_com_ela(self):
        TaxaReferencia.objects.create(fonte=FONTE_BCB, referencia=date(2026, 7, 1), taxa_mensal='1.98')
        resp = self._pagina_do_veiculo(self.criar_garagem())
        self.assertContains(resp, 'média de mercado do Banco Central (ref. 07/2026)')
        self.assertContains(resp, '1,98% ao mês')
        self.assertContains(resp, f"12x de R$ {self._parcela('1.98')}")

    def test_mostra_a_taxa_da_garagem_e_calcula_com_ela(self):
        TaxaReferencia.objects.create(fonte=FONTE_BCB, referencia=date(2026, 7, 1), taxa_mensal='1.98')
        resp = self._pagina_do_veiculo(self.criar_garagem(taxa_juros_mensal_padrao=Decimal('1.50')))
        self.assertContains(resp, 'taxa informada pela garagem')
        self.assertContains(resp, f"12x de R$ {self._parcela('1.50')}")
        self.assertNotContains(resp, 'Banco Central')

    def test_sem_nenhuma_referencia_avisa_que_e_estimada(self):
        resp = self._pagina_do_veiculo(self.criar_garagem())
        self.assertContains(resp, 'taxa estimada')
