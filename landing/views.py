import time
from urllib.parse import quote

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from tenants.models import Garagem

from .forms import InteresseGaragemForm

MENSAGEM_WHATSAPP = "Olá! Vi o {nome} e quero saber como colocar a minha garagem no ar."


def _link_whatsapp():
    """Sem número configurado (PLATAFORMA_WHATSAPP), o botão vira âncora pro formulário —
    nunca um número inventado."""
    numero = settings.PLATAFORMA_WHATSAPP
    if not numero:
        return ''
    texto = MENSAGEM_WHATSAPP.format(nome=settings.PLATAFORMA_NOME)
    return f'https://wa.me/{numero}?text={quote(texto)}'


def _vitrine_demo(slug):
    """Garagem de demonstração exibida nos celulares da landing (iframe da vitrine real).
    Some sozinha se a garagem não existir ou estiver suspensa — a landing não quebra."""
    return Garagem.objects.filter(slug=slug).exclude(status=Garagem.Status.SUSPENSO).first()


# Clientes fictícios do painel de demonstração (rotulado como tal na página) — os veículos
# são os do estoque da própria garagem de demonstração, pra tela do cliente e a do dono
# contarem a mesma história.
CLIENTES_DEMO = [
    ('Rafael M.', 'agora mesmo', 'nova'),
    ('Camila T.', 'há 1 hora', 'contato'),
    ('Bianca R.', 'ontem', 'nova'),
    ('Diego S.', 'saiu da vitrine', 'vendido'),
]
SELOS_DEMO = {'nova': 'Nova', 'contato': 'Em contato', 'vendido': 'Vendido'}


def _propostas_demo(veiculos):
    """Linhas do painel de demonstração. Com pouco estoque na garagem de demonstração,
    completa com veículos genéricos em vez de esconder o painel."""
    titulos = [f'{v.titulo.title()} · {v.ano_modelo}' for v in veiculos]
    genericos = ['Honda CG 160 · 2022', 'Fiat Argo 1.0 · 2021', 'VW Gol 1.6 · 2018', 'Yamaha Fazer 250 · 2020']
    titulos += genericos[len(titulos):]
    return [
        {'cliente': cliente, 'veiculo': titulo, 'quando': quando, 'status': status, 'selo': SELOS_DEMO[status]}
        for (cliente, quando, status), titulo in zip(CLIENTES_DEMO, titulos)
    ]


def home(request):
    if request.method == 'POST':
        form = InteresseGaragemForm(request.POST)
        if form.is_valid():
            interesse = form.save()
            send_mail(
                subject=f'Novo interesse na plataforma — {interesse.nome_garagem}',
                message=(
                    f'Nome: {interesse.nome}\n'
                    f'Garagem: {interesse.nome_garagem}\n'
                    f'WhatsApp: {interesse.telefone}\n\n'
                    f'Mensagem:\n{interesse.mensagem}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.PLATFORM_ADMIN_EMAIL],
                fail_silently=True,
            )
            return redirect(f"{reverse('landing:home')}?enviado=1#contato")
    else:
        form = InteresseGaragemForm(initial={'iniciado_em': time.time()})

    demo = _vitrine_demo(settings.LANDING_DEMO_SLUG)
    demo2 = _vitrine_demo(settings.LANDING_DEMO_SLUG_2)
    veiculos_demo = list(demo.veiculos.filter(disponivel=True)[:4]) if demo else []
    veiculo_simulacao = veiculos_demo[0] if veiculos_demo else None
    return render(request, 'landing/home.html', {
        'form': form,
        'enviado': request.GET.get('enviado') == '1',
        'link_whatsapp': _link_whatsapp(),
        'demo': demo,
        'demo_url': reverse('storefront:frontpage', kwargs={'garagem_slug': demo.slug}) if demo else '',
        'simulacao_url': (
            reverse('storefront:detalhe_veiculo', kwargs={'garagem_slug': demo.slug, 'veiculo_slug': veiculo_simulacao.slug})
            + '#simulador-financiamento'
        ) if veiculo_simulacao else '',
        'demo2': demo2,
        'demo2_url': reverse('storefront:frontpage', kwargs={'garagem_slug': demo2.slug}) if demo2 else '',
        'propostas_demo': _propostas_demo(veiculos_demo),
        'plataforma_nome': settings.PLATAFORMA_NOME,
    })
