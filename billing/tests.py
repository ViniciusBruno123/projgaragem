import hashlib
import hmac
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from tenants.models import Garagem

from .models import Assinatura, EventoWebhookMercadoPago
from .services import processar_evento, validar_assinatura_mp

SECRET = 'testsecret'


def _assinar(data_id, request_id, ts, secret=SECRET):
    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    return hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()


@override_settings(MERCADOPAGO_WEBHOOK_SECRET=SECRET)
class ValidarAssinaturaMpTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _request(self, data_id='123', request_id='req-1', ts='1700000000', v1=None):
        v1 = v1 if v1 is not None else _assinar(data_id, request_id, ts)
        return self.factory.post(
            f'/billing/webhook/mercadopago/?type=preapproval&data.id={data_id}',
            HTTP_X_SIGNATURE=f'ts={ts},v1={v1}',
            HTTP_X_REQUEST_ID=request_id,
        )

    def test_assinatura_valida(self):
        self.assertTrue(validar_assinatura_mp(self._request()))

    def test_assinatura_adulterada_e_rejeitada(self):
        request = self._request(v1='0' * 64)
        self.assertFalse(validar_assinatura_mp(request))

    def test_sem_header_e_rejeitada(self):
        request = self.factory.post('/billing/webhook/mercadopago/?type=preapproval&data.id=123')
        self.assertFalse(validar_assinatura_mp(request))


class ProcessarEventoTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_teste', 'dono@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Teste', slug='garagem-teste',
            telefone_whatsapp='5517999999999', email_contato='dono@example.com',
            status=Garagem.Status.ATIVO,
        )
        self.assinatura = Assinatura.objects.create(
            garagem=self.garagem, mp_preapproval_id='mp-123',
            status=Assinatura.Status.AUTHORIZED, valor_mensal='99.90',
        )

    def _mock_sdk(self, status):
        sdk = MagicMock()
        sdk.preapproval.return_value.get.return_value = {
            'response': {'id': 'mp-123', 'status': status}
        }
        return sdk

    @patch('billing.services.get_sdk')
    def test_pausada_marca_garagem_como_atrasada(self, mock_get_sdk):
        mock_get_sdk.return_value = self._mock_sdk('paused')
        evento = EventoWebhookMercadoPago.objects.create(
            topico='preapproval', recurso_id='mp-123', payload_bruto={},
        )
        processar_evento(evento)

        self.assinatura.refresh_from_db()
        self.garagem.refresh_from_db()
        evento.refresh_from_db()
        self.assertEqual(self.assinatura.status, Assinatura.Status.PAUSED)
        self.assertEqual(self.garagem.status, Garagem.Status.ATRASADO)
        self.assertTrue(evento.processado_com_sucesso)

    @patch('billing.services.get_sdk')
    def test_autorizada_nao_reativa_garagem_suspensa_manualmente(self, mock_get_sdk):
        self.garagem.status = Garagem.Status.SUSPENSO
        self.garagem.save()
        mock_get_sdk.return_value = self._mock_sdk('authorized')

        evento = EventoWebhookMercadoPago.objects.create(
            topico='preapproval', recurso_id='mp-123', payload_bruto={},
        )
        processar_evento(evento)

        self.garagem.refresh_from_db()
        self.assertEqual(self.garagem.status, Garagem.Status.SUSPENSO)

    @patch('billing.services.get_sdk')
    def test_autorizada_reativa_garagem_atrasada(self, mock_get_sdk):
        self.garagem.status = Garagem.Status.ATRASADO
        self.garagem.save()
        mock_get_sdk.return_value = self._mock_sdk('authorized')

        evento = EventoWebhookMercadoPago.objects.create(
            topico='preapproval', recurso_id='mp-123', payload_bruto={},
        )
        processar_evento(evento)

        self.garagem.refresh_from_db()
        self.assertEqual(self.garagem.status, Garagem.Status.ATIVO)


@override_settings(DIAS_ATRASO_PARA_AVISO_ADMIN=5, PLATFORM_ADMIN_EMAIL='admin@example.com')
class VerificarInadimplenciaCommandTests(TestCase):
    def setUp(self):
        dono = User.objects.create_user('dono_cmd', 'dono_cmd@example.com', 'senha12345')
        self.garagem = Garagem.objects.create(
            dono=dono, nome='Garagem Atrasada', slug='garagem-atrasada',
            telefone_whatsapp='5517999999999', email_contato='dono_cmd@example.com',
            status=Garagem.Status.ATIVO,
        )
        self.assinatura = Assinatura.objects.create(
            garagem=self.garagem, mp_preapproval_id='mp-atraso',
            status=Assinatura.Status.PAUSED, valor_mensal='99.90',
        )
        # auto_now sobrescreveria na criação — força a data via update() direto no banco.
        seis_dias_atras = timezone.now() - timedelta(days=6)
        Assinatura.objects.filter(pk=self.assinatura.pk).update(atualizada_em=seis_dias_atras)

    def test_marca_garagem_como_atrasada_e_avisa_admin_uma_vez(self):
        call_command('verificar_inadimplencia')

        self.garagem.refresh_from_db()
        self.assertEqual(self.garagem.status, Garagem.Status.ATRASADO)
        self.assertIsNotNone(self.garagem.ultimo_aviso_atraso_enviado_em)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Garagem Atrasada', mail.outbox[0].subject)

        call_command('verificar_inadimplencia')
        self.assertEqual(len(mail.outbox), 1, "não deve reenviar aviso enquanto não voltar a autorizada")

    def test_nao_avisa_antes_do_limite_de_dias(self):
        Assinatura.objects.filter(pk=self.assinatura.pk).update(atualizada_em=timezone.now() - timedelta(days=2))
        call_command('verificar_inadimplencia')

        self.garagem.refresh_from_db()
        self.assertEqual(self.garagem.status, Garagem.Status.ATRASADO)
        self.assertIsNone(self.garagem.ultimo_aviso_atraso_enviado_em)
        self.assertEqual(len(mail.outbox), 0)
