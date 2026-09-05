from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from tenants.models import Garagem

from .models import Veiculo


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
