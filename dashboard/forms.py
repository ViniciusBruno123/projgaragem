from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from django.utils.formats import localize

from financing.services import taxa_media_de_mercado

from tenants.models import Garagem
from vehicles.forms import FotoVeiculoForm as BaseFotoVeiculoForm
from vehicles.models import FotoVeiculo, Veiculo


class EstiloLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


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


class FotoVeiculoForm(BaseFotoVeiculoForm):
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
        fields = [
            'endereco', 'horario_funcionamento', 'instagram_url', 'facebook_url', 'cor_destaque',
            'taxa_juros_mensal_padrao',
        ]
        labels = {
            'endereco': 'Endereço',
            'horario_funcionamento': 'Horário de funcionamento',
            'instagram_url': 'Link do Instagram',
            'facebook_url': 'Link do Facebook',
            'cor_destaque': 'Cor da vitrine',
        }
        help_texts = {
            'horario_funcionamento': 'Aparece no rodapé da vitrine.',
            'cor_destaque': 'Cor dos botões e detalhes da sua vitrine.',
        }
        widgets = {
            'horario_funcionamento': forms.TextInput(attrs={'placeholder': 'Ex: Seg a Sex, 8h às 18h'}),
            'cor_destaque': forms.TextInput(attrs={'type': 'color', 'style': 'height: 2.5rem; padding: 0.25rem;'}),
            'taxa_juros_mensal_padrao': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': 'Ex: 1,99'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

        media = taxa_media_de_mercado()
        if media:
            self.fields['taxa_juros_mensal_padrao'].help_text = (
                "Opcional. Em branco, o simulador usa a média de mercado do Banco Central: "
                f"{localize(media.taxa_mensal)}% ao mês (ref. {media.referencia:%m/%Y})."
            )
