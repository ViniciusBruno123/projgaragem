import urllib.parse


def gerar_link_whatsapp(garagem, veiculo=None, nome=""):
    numero = garagem.telefone_whatsapp
    if veiculo:
        texto = (
            f"Olá! Tenho interesse no veículo {veiculo.titulo} ({veiculo.ano_modelo}) "
            "anunciado no site."
        )
    else:
        texto = "Olá! Gostaria de mais informações sobre os veículos disponíveis."
    if nome:
        texto = f"Meu nome é {nome}. {texto}"
    return f"https://wa.me/{numero}?text={urllib.parse.quote(texto)}"
