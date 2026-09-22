from django import template

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
