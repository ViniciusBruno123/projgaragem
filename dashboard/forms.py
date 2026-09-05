from django import forms
from django.forms import inlineformset_factory

from tenants.models import Garagem
from vehicles.models import FotoVeiculo, Veiculo


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            'tipo', 'titulo', 'marca', 'modelo', 'ano_fabricacao', 'ano_modelo',
            'quilometragem', 'combustivel', 'cilindrada', 'potencia_motor', 'preco', 'descricao',
            'destaque', 'disponivel', 'aceita_troca',
        ]
        widgets = {'descricao': forms.Textarea(attrs={'rows': 4})}
        help_texts = {
            'cilindrada': 'Preencha apenas se o tipo for Moto.',
            'potencia_motor': 'Preencha apenas se o tipo for Carro.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.CheckboxInput,)):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class FotoVeiculoForm(forms.ModelForm):
    class Meta:
        model = FotoVeiculo
        fields = ['imagem', 'principal', 'ordem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagem'].widget.attrs.setdefault('class', 'form-control')
        self.fields['ordem'].widget.attrs.setdefault('class', 'form-control')
        self.fields['principal'].widget.attrs.setdefault('class', 'form-check-input')


FotoVeiculoFormSet = inlineformset_factory(
    Veiculo, FotoVeiculo,
    form=FotoVeiculoForm,
    extra=1, can_delete=True,
)


class GaragemForm(forms.ModelForm):
    class Meta:
        model = Garagem
        fields = ['endereco', 'horario_funcionamento', 'instagram_url', 'facebook_url']
        widgets = {
            'horario_funcionamento': forms.TextInput(attrs={'placeholder': 'Ex: Seg a Sex, 8h às 18h'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
