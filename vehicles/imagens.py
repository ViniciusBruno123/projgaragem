import io
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps


MB = 1024 * 1024


class FotoInvalida(Exception):
    pass


def otimizar_foto_com_limite(arquivo):
    """otimizar_foto, mas barra antes arquivos maiores que o limite configurado, com a
    mesma mensagem amigável usada em toda a plataforma — fotos de veículo, logo/capa da
    garagem e fotos do formulário público de avaliação de usados (leads.views.enviar_avaliacao)
    compartilham essa checagem em vez de cada um duplicá-la.
    """
    if arquivo.size > settings.FOTO_UPLOAD_MAX_BYTES:
        tamanho = f'{arquivo.size / MB:.1f}'.replace('.', ',')
        raise FotoInvalida(
            f'O arquivo tem {tamanho} MB e o limite é {settings.FOTO_UPLOAD_MAX_BYTES // MB} MB. '
            'Envie uma imagem menor.'
        )
    return otimizar_foto(arquivo)


def otimizar_foto(arquivo):
    """Reduz a foto, corrige a orientação e remove os metadados (inclusive o GPS).

    Devolve um ContentFile JPEG. Levanta FotoInvalida, com mensagem pronta para
    o usuário, se a imagem não puder ser lida ou for grande demais.
    """
    lado = settings.FOTO_LADO_MAXIMO
    try:
        arquivo.seek(0)
        with Image.open(arquivo) as original:
            if original.width * original.height > settings.FOTO_MAX_PIXELS:
                raise FotoInvalida('A foto tem resolução alta demais. Tire outra em resolução menor.')

            perfil_de_cor = original.info.get('icc_profile')
            original.draft('RGB', (lado, lado))
            imagem = ImageOps.exif_transpose(original)

            if imagem.mode in ('RGBA', 'LA') or 'transparency' in imagem.info:
                imagem = imagem.convert('RGBA')
                fundo = Image.new('RGB', imagem.size, (255, 255, 255))
                fundo.paste(imagem, mask=imagem.getchannel('A'))
                imagem = fundo
            else:
                imagem = imagem.convert('RGB')

            imagem.thumbnail((lado, lado), Image.Resampling.LANCZOS)

            saida = io.BytesIO()
            imagem.save(
                saida, 'JPEG', quality=settings.FOTO_QUALIDADE_JPEG,
                optimize=True, progressive=True, icc_profile=perfil_de_cor,
            )
    except FotoInvalida:
        raise
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise FotoInvalida('Não foi possível ler a foto. Envie um arquivo JPG ou PNG válido.') from exc

    return ContentFile(saida.getvalue(), name=f'{Path(arquivo.name).stem}.jpg')
