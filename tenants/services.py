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
