from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from tenants.services import get_garagem_ativa_ou_404

from .forms import PropostaForm
from .services import gerar_link_whatsapp


def enviar_proposta(request, garagem_slug, veiculo_slug=None):
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    veiculo = None
    if veiculo_slug:
        veiculo = get_object_or_404(garagem.veiculos, slug=veiculo_slug, disponivel=True)

    if request.method == 'POST':
        form = PropostaForm(request.POST)
        if form.is_valid():
            proposta = form.save(commit=False)
            proposta.garagem = garagem
            proposta.veiculo = veiculo
            proposta.save()

            if garagem.email_contato:
                send_mail(
                    subject=f"Nova proposta - {veiculo.titulo if veiculo else 'Contato geral'}",
                    message=(
                        f"Nome: {proposta.nome}\n"
                        f"Telefone: {proposta.telefone}\n"
                        f"E-mail: {proposta.email}\n\n"
                        f"Mensagem:\n{proposta.mensagem}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[garagem.email_contato],
                    fail_silently=True,
                )

            return redirect(gerar_link_whatsapp(garagem, veiculo, proposta.nome))
    else:
        form = PropostaForm()

    return render(request, 'leads/proposta_form.html', {
        'garagem': garagem,
        'veiculo': veiculo,
        'form': form,
    })
