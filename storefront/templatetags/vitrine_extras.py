from django import template
from django.urls import reverse

from leads.services import gerar_link_whatsapp
from tenants.services import formatar_telefone

register = template.Library()


@register.simple_tag(takes_context=True)
def absolute_url(context, caminho):
    """Transforma uma URL relativa (o campo de uma foto, por exemplo) em absoluta,
    com esquema e domínio — o Open Graph exige isso, o WhatsApp não busca imagem
    a partir de um caminho relativo."""
    request = context.get('request')
    if not request or not caminho:
        return ''
    return request.build_absolute_uri(caminho)


@register.filter
def telefone_br(digitos):
    return formatar_telefone(digitos)


@register.simple_tag(takes_context=True)
def whatsapp_veiculo(context, veiculo):
    """Link do WhatsApp da garagem com a mensagem pronta sobre este veículo (título, preço e o
    link do anúncio), para o botão do card e da página do veículo."""
    request = context.get('request')
    garagem = context['garagem']
    url = ''
    if request:
        url = request.build_absolute_uri(
            reverse('storefront:detalhe_veiculo', kwargs={'garagem_slug': garagem.slug, 'veiculo_slug': veiculo.slug})
        )
    return gerar_link_whatsapp(garagem, veiculo, url_anuncio=url)
