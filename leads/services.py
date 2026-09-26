import urllib.parse

from django.utils.formats import number_format


def gerar_link_whatsapp(garagem, veiculo=None, nome="", url_anuncio=""):
    """url_anuncio (absoluta) vai na mensagem para a garagem abrir o mesmo anúncio que o cliente viu."""
    numero = garagem.telefone_whatsapp
    if veiculo:
        preco = number_format(veiculo.preco, 2, use_l10n=True, force_grouping=True)
        texto = (
            f"Olá! Tenho interesse no veículo {veiculo.titulo} ({veiculo.ano_modelo}), "
            f"R$ {preco}, anunciado no site."
        )
        if url_anuncio:
            texto += f" {url_anuncio}"
    else:
        texto = "Olá! Gostaria de mais informações sobre os veículos disponíveis."
    if nome:
        texto = f"Meu nome é {nome}. {texto}"
    return f"https://wa.me/{numero}?text={urllib.parse.quote(texto)}"


def gerar_link_whatsapp_avaliacao(garagem, avaliacao):
    texto = (
        f"Olá! Meu nome é {avaliacao.nome} e quero vender ou trocar meu veículo: "
        f"{avaliacao.marca} {avaliacao.modelo} {avaliacao.ano}, {avaliacao.quilometragem} km."
    )
    if avaliacao.veiculo_interesse:
        texto += f" Tenho interesse em trocar pelo {avaliacao.veiculo_interesse.titulo} anunciado no site."
    return f"https://wa.me/{garagem.telefone_whatsapp}?text={urllib.parse.quote(texto)}"
