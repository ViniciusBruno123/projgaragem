"""Limite de tentativas de login do painel e do /admin/ — sem dependência externa.

Guarda as falhas em banco (TentativaLoginFalha) em vez de cache em memória, para
funcionar mesmo com vários processos gunicorn e sobreviver a um restart do servidor.
"""
import random
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.mail import send_mail
from django.utils import timezone

from .models import CodigoAcessoAdmin, TentativaLoginFalha

JANELA = timedelta(minutes=15)
LIMITE_POR_USUARIO = 5  # mesmo usuário errando a senha
LIMITE_POR_IP = 15      # o mesmo IP tentando vários usuários
VALIDADE_CODIGO = timedelta(minutes=15)


def ip_do_request(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _limpar_antigas():
    TentativaLoginFalha.objects.filter(criado_em__lt=timezone.now() - JANELA).delete()


def bloqueado(request, usuario):
    """True se o usuário ou o IP já erraram demais nos últimos minutos."""
    _limpar_antigas()
    ip = ip_do_request(request)
    if usuario and TentativaLoginFalha.objects.filter(usuario__iexact=usuario).count() >= LIMITE_POR_USUARIO:
        return True
    return TentativaLoginFalha.objects.filter(ip=ip).count() >= LIMITE_POR_IP


def registrar_falha(request, usuario):
    TentativaLoginFalha.objects.create(usuario=(usuario or '')[:150], ip=ip_do_request(request))


def limpar_falhas(usuario):
    """Chamado no login com sucesso, para não penalizar o dono por erros antigos."""
    TentativaLoginFalha.objects.filter(usuario__iexact=usuario).delete()


def _limpar_codigos_expirados():
    CodigoAcessoAdmin.objects.filter(criado_em__lt=timezone.now() - VALIDADE_CODIGO).delete()


def codigo_valido(usuario, codigo):
    _limpar_codigos_expirados()
    return bool(codigo) and CodigoAcessoAdmin.objects.filter(usuario__iexact=usuario, codigo=codigo).exists()


def consumir_codigo(usuario, codigo):
    CodigoAcessoAdmin.objects.filter(usuario__iexact=usuario, codigo=codigo).delete()


def enviar_codigo_se_necessario(usuario):
    """Manda um código novo por e-mail — a não ser que já exista um válido, para não reenviar
    a cada tentativa enquanto o código anterior ainda vale."""
    _limpar_codigos_expirados()
    if CodigoAcessoAdmin.objects.filter(usuario__iexact=usuario).exists():
        return
    codigo = f"{random.randint(0, 999999):06d}"
    CodigoAcessoAdmin.objects.create(usuario=(usuario or '')[:150], codigo=codigo)
    minutos = int(VALIDADE_CODIGO.total_seconds() // 60)
    send_mail(
        subject=f"[{settings.PLATAFORMA_NOME}] Código de acesso — login do /admin/",
        message=(
            f"Alguém tentou entrar como \"{usuario}\" no /admin/ e errou a senha "
            f"{LIMITE_POR_USUARIO} vezes seguidas.\n\n"
            f"Se foi você, o código para continuar tentando é: {codigo}\n"
            f"Vale por {minutos} minutos.\n\n"
            "Se não foi você, não faça nada — sem esse código, ninguém consegue entrar."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_CODIGO_ACESSO_ADMIN],
        fail_silently=True,
    )


class AdminLoginComCodigoForm(AdminAuthenticationForm):
    """Login do /admin/ (Django admin da plataforma) com uma trava extra: depois de
    LIMITE_POR_USUARIO tentativas erradas, só entra quem também souber o código mandado
    por e-mail (ver enviar_codigo_se_necessario) — nem com a senha certa passa sem ele."""

    codigo_acesso = forms.CharField(
        required=False, label='Código de acesso',
        help_text='Só pedido depois de várias tentativas erradas — chega por e-mail.',
    )

    def clean(self):
        usuario = (self.cleaned_data.get('username') or '').strip()

        if usuario and bloqueado(self.request, usuario):
            codigo = (self.cleaned_data.get('codigo_acesso') or '').strip()
            if not codigo_valido(usuario, codigo):
                enviar_codigo_se_necessario(usuario)
                raise forms.ValidationError(
                    'Muitas tentativas erradas. Mandamos um código de acesso por e-mail — '
                    'digite usuário, senha e esse código para continuar.'
                )
            consumir_codigo(usuario, codigo)

        try:
            cleaned_data = super().clean()
        except forms.ValidationError:
            if usuario:
                registrar_falha(self.request, usuario)
            raise
        if usuario:
            limpar_falhas(usuario)
        return cleaned_data
