from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

from .imagens import FotoInvalida, otimizar_foto
from .models import FotoVeiculo

MB = 1024 * 1024


class FotoVeiculoForm(forms.ModelForm):
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
        arquivo = self.cleaned_data['imagem']
        if not isinstance(arquivo, UploadedFile):
            return arquivo  # foto já salva, sem novo envio

        if arquivo.size > settings.FOTO_UPLOAD_MAX_BYTES:
            tamanho = f'{arquivo.size / MB:.1f}'.replace('.', ',')
            raise forms.ValidationError(
                f'A foto tem {tamanho} MB e o limite é {settings.FOTO_UPLOAD_MAX_BYTES // MB} MB. '
                'Tire a foto em resolução menor ou reduza-a antes de enviar.'
            )
        try:
            return otimizar_foto(arquivo)
        except FotoInvalida as exc:
            raise forms.ValidationError(str(exc)) from exc
