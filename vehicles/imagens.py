import io
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps


class FotoInvalida(Exception):
    pass


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
