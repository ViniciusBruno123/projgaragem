from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Garagem


def get_garagem_ativa_ou_404(garagem_slug):
    """Vitrine pública fica indisponível somente quando a garagem está suspensa.
    Atraso de pagamento não tira a vitrine do ar — só trava a edição no painel.
    """
    garagem = get_object_or_404(Garagem, slug=garagem_slug)
    if garagem.status == Garagem.Status.SUSPENSO:
        raise Http404()
    return garagem


def formatar_telefone(digitos):
    """5517992078701 -> (17) 99207-8701, para exibir. Fora do padrão brasileiro, devolve como veio."""
    digitos = str(digitos or '')
    numero = digitos[2:] if digitos.startswith('55') and len(digitos) in (12, 13) else digitos
    if len(numero) == 11:
        return f'({numero[:2]}) {numero[2:7]}-{numero[7:]}'
    if len(numero) == 10:
        return f'({numero[:2]}) {numero[2:6]}-{numero[6:]}'
    return digitos
