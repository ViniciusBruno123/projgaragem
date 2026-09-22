"""Limite de tentativas de login do painel — sem dependência externa.

Guarda as falhas em banco (TentativaLoginFalha) em vez de cache em memória, para
funcionar mesmo com vários processos gunicorn e sobreviver a um restart do servidor.
"""
from datetime import timedelta

from django.utils import timezone

from .models import TentativaLoginFalha

JANELA = timedelta(minutes=15)
LIMITE_POR_USUARIO = 5  # mesmo usuário errando a senha
LIMITE_POR_IP = 15      # o mesmo IP tentando vários usuários


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
