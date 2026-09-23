from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from .imagens import FotoInvalida, otimizar_foto
from .models import FotoVeiculo

MB = 1024 * 1024


class ImagemOtimizadaMixin:
    """Valida o tamanho e otimiza (redimensiona, remove metadados) uma imagem enviada.

    Reutilizado por qualquer form com campo de imagem — fotos de veículo, logo e
    capa da garagem — para não duplicar a checagem de limite nem a chamada a
    vehicles.imagens.otimizar_foto.
    """

    def _limpar_imagem_otimizada(self, nome_campo):
        arquivo = self.cleaned_data.get(nome_campo)
        if not isinstance(arquivo, UploadedFile):
            return arquivo  # arquivo já salvo, sem novo envio

        if arquivo.size > settings.FOTO_UPLOAD_MAX_BYTES:
            tamanho = f'{arquivo.size / MB:.1f}'.replace('.', ',')
            raise forms.ValidationError(
                f'O arquivo tem {tamanho} MB e o limite é {settings.FOTO_UPLOAD_MAX_BYTES // MB} MB. '
                'Envie uma imagem menor.'
            )
        try:
            return otimizar_foto(arquivo)
        except FotoInvalida as exc:
            raise forms.ValidationError(str(exc)) from exc


class FotoVeiculoForm(ImagemOtimizadaMixin, forms.ModelForm):
    """Formulário de foto compartilhado pelo painel do dono e pelo Django admin."""

    class Meta:
        model = FotoVeiculo
        fields = ['imagem', 'principal', 'ordem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        limite_mb = settings.FOTO_UPLOAD_MAX_BYTES // MB
        self.fields['imagem'].help_text = f'JPG ou PNG, até {limite_mb} MB. A foto é reduzida automaticamente.'
        self.fields['imagem'].widget.attrs['accept'] = 'image/*'

    def clean_imagem(self):
        return self._limpar_imagem_otimizada('imagem')

    def has_changed(self):
        """"Ordem" sozinho não conta como "o dono mexeu nesse slot" — só isso não pode
        obrigar a enviar uma foto. Sem isso, um slot vazio do formset (extra=6 no painel)
        que só teve o número de "ordem" alterado por engano — por exemplo, rolar a página
        com o mouse em cima de um campo numérico focado muda o valor dele em vez de rolar
        (ver static/js/numero_sem_scroll.js) — passava a exigir a foto, mesmo sem o dono
        ter escolhido nada ali."""
        return bool(set(self.changed_data) - {'ordem'})
