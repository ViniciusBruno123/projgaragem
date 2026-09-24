import time

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from tenants.services import get_garagem_ativa_ou_404
from vehicles.imagens import FotoInvalida, otimizar_foto_com_limite

from .forms import AvaliacaoForm, PropostaForm
from .models import FotoAvaliacao
from .services import gerar_link_whatsapp, gerar_link_whatsapp_avaliacao

# Quantas fotos o formulário público de avaliação aceita — só o suficiente pra dar uma
# ideia do estado do veículo antes da conversa no WhatsApp, sem virar um upload pesado.
MAX_FOTOS_AVALIACAO = 4


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
        form = PropostaForm(initial={'iniciado_em': time.time()})

    return render(request, 'leads/proposta_form.html', {
        'garagem': garagem,
        'veiculo': veiculo,
        'form': form,
    })


def enviar_avaliacao(request, garagem_slug, veiculo_slug=None):
    """Formulário público de "quero vender/trocar meu veículo" — o inverso da proposta:
    aqui é o visitante que descreve UM VEÍCULO DELE (fora do catálogo) para a garagem
    avaliar. veiculo_slug, quando presente, é o veículo do catálogo que a pessoa viu o
    selo "Aceita troca" e quer levar na troca (ver Avaliacao.veiculo_interesse)."""
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    veiculo_interesse = None
    if veiculo_slug:
        veiculo_interesse = get_object_or_404(garagem.veiculos, slug=veiculo_slug, disponivel=True)

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        fotos_otimizadas = []
        erro_foto = None
        for arquivo in request.FILES.getlist('fotos')[:MAX_FOTOS_AVALIACAO]:
            try:
                fotos_otimizadas.append(otimizar_foto_com_limite(arquivo))
            except FotoInvalida as exc:
                erro_foto = str(exc)
                break

        if erro_foto:
            form.add_error(None, erro_foto)
        elif form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.garagem = garagem
            avaliacao.veiculo_interesse = veiculo_interesse
            avaliacao.save()
            for imagem in fotos_otimizadas:
                FotoAvaliacao.objects.create(avaliacao=avaliacao, imagem=imagem)

            if garagem.email_contato:
                send_mail(
                    subject=f"Novo pedido de avaliação - {avaliacao.marca} {avaliacao.modelo}",
                    message=(
                        f"Nome: {avaliacao.nome}\n"
                        f"Telefone: {avaliacao.telefone}\n"
                        f"E-mail: {avaliacao.email}\n\n"
                        f"Veículo: {avaliacao.marca} {avaliacao.modelo} {avaliacao.ano} "
                        f"({avaliacao.get_tipo_display()}) - {avaliacao.quilometragem} km\n\n"
                        f"Observações:\n{avaliacao.observacoes}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[garagem.email_contato],
                    fail_silently=True,
                )

            return redirect(gerar_link_whatsapp_avaliacao(garagem, avaliacao))
    else:
        form = AvaliacaoForm(initial={'iniciado_em': time.time()})

    return render(request, 'leads/avaliacao_form.html', {
        'garagem': garagem,
        'veiculo_interesse': veiculo_interesse,
        'form': form,
        'max_fotos': MAX_FOTOS_AVALIACAO,
    })
