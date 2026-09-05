from decimal import Decimal

from django.test import SimpleTestCase

from .services import calcular_parcela_price


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
