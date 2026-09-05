from django.shortcuts import get_object_or_404, render

from financing.forms import SimulacaoFinanciamentoForm
from financing.services import calcular_parcela_price
from tenants.services import get_garagem_ativa_ou_404


def frontpage(request, garagem_slug):
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    veiculos_destaque = garagem.veiculos.filter(disponivel=True, destaque=True)
    demais_veiculos = garagem.veiculos.filter(disponivel=True, destaque=False)
    return render(request, 'storefront/frontpage.html', {
        'garagem': garagem,
        'veiculos_destaque': veiculos_destaque,
        'demais_veiculos': demais_veiculos,
    })


def detalhe_veiculo(request, garagem_slug, veiculo_slug):
    garagem = get_garagem_ativa_ou_404(garagem_slug)
    veiculo = get_object_or_404(garagem.veiculos, slug=veiculo_slug, disponivel=True)

    form = SimulacaoFinanciamentoForm(request.GET or None, initial={'numero_parcelas': 24})
    parcela = None
    valor_financiado = None
    if form.is_valid():
        valor_financiado = veiculo.preco - form.cleaned_data['valor_entrada']
        if valor_financiado > 0:
            parcela = calcular_parcela_price(
                valor_financiado, garagem.taxa_juros_mensal_padrao, form.cleaned_data['numero_parcelas']
            )

    return render(request, 'storefront/detalhe_veiculo.html', {
        'garagem': garagem,
        'veiculo': veiculo,
        'form': form,
        'parcela': parcela,
        'valor_financiado': valor_financiado,
    })
