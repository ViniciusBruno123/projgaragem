from django.shortcuts import get_object_or_404, render

from financing.forms import SimulacaoFinanciamentoForm
from financing.services import calcular_parcela_price, taxa_para
from tenants.legal import contexto_plataforma
from tenants.services import get_garagem_ativa_ou_404

from .forms import FiltroVeiculosForm

# Agrupa por tipo (motos antes de carros) para que cada linha da vitrine tenha fotos
# na mesma proporção; dentro do grupo, os mais recentes primeiro.
ORDEM_VITRINE = ('-tipo', '-criado_em')


def politica_privacidade(request, garagem_slug):
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    return render(request, 'storefront/politica_privacidade.html', {
        'garagem': garagem,
        **contexto_plataforma(),
    })


def frontpage(request, garagem_slug):
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    filtro = FiltroVeiculosForm(request.GET or None, garagem=garagem)
    # prefetch_related evita 1 consulta por card (foto principal + prévia do hover, ver
    # Veiculo.fotos_extra_urls) numa garagem com dezenas de veículos.
    veiculos_disponiveis = filtro.aplicar(garagem.veiculos.filter(disponivel=True).prefetch_related('fotos'))

    return render(request, 'storefront/frontpage.html', {
        'garagem': garagem,
        'filtro': filtro,
        'filtro_ativo': any(request.GET.values()),
        'veiculos_destaque': veiculos_disponiveis.filter(destaque=True).order_by(*ORDEM_VITRINE),
        'demais_veiculos': veiculos_disponiveis.filter(destaque=False).order_by(*ORDEM_VITRINE),
    })


def _contexto_simulacao(request, garagem, veiculo):
    """Compartilhado entre a página do veículo e o fragmento AJAX do simulador
    (storefront:simular_financiamento) — mesma conta dos dois lados."""
    taxa = taxa_para(garagem)
    form = SimulacaoFinanciamentoForm(request.GET or None, initial={'numero_parcelas': 24})
    parcela = None
    valor_financiado = None
    if form.is_valid():
        valor_financiado = veiculo.preco - form.cleaned_data['valor_entrada']
        if valor_financiado > 0:
            parcela = calcular_parcela_price(valor_financiado, taxa.valor, form.cleaned_data['numero_parcelas'])
    return {
        'garagem': garagem,
        'veiculo': veiculo,
        'form': form,
        'parcela': parcela,
        'taxa': taxa,
        'valor_financiado': valor_financiado,
    }


def detalhe_veiculo(request, garagem_slug, veiculo_slug):
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    veiculo = get_object_or_404(garagem.veiculos, slug=veiculo_slug, disponivel=True)
    return render(request, 'storefront/detalhe_veiculo.html', _contexto_simulacao(request, garagem, veiculo))


def simular_financiamento(request, garagem_slug, veiculo_slug):
    """Só o miolo do simulador (sem o resto da página) — usado pelo fetch de
    static/js/simulador_financiamento.js, pra "Calcular" não recarregar a página
    inteira nem jogar a rolagem pro topo. Sem JavaScript, o formulário continua
    funcionando normalmente: ele aponta pra a própria página do veículo, não pra cá."""
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    veiculo = get_object_or_404(garagem.veiculos, slug=veiculo_slug, disponivel=True)
    return render(request, 'storefront/_simulador_financiamento.html', _contexto_simulacao(request, garagem, veiculo))
