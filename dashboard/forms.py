from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from django.utils.formats import localize

from financing.services import taxa_media_de_mercado

from tenants.models import Garagem
from vehicles.forms import ImagemOtimizadaMixin
from vehicles.forms import FotoVeiculoForm as BaseFotoVeiculoForm
from vehicles.models import FotoVeiculo, Veiculo


class EstiloLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


ORDENACOES_VEICULO = [
    ('-criado_em', 'Mais recentes'),
    ('criado_em', 'Mais antigos'),
    ('preco', 'Preço: menor primeiro'),
    ('-preco', 'Preço: maior primeiro'),
    ('-ano_modelo', 'Ano: mais novo primeiro'),
    ('ano_modelo', 'Ano: mais antigo primeiro'),
    ('quilometragem', 'Km: menor primeiro'),
    ('-quilometragem', 'Km: maior primeiro'),
    ('titulo', 'Título (A-Z)'),
]

SIM_NAO = [('', 'Todos'), ('sim', 'Sim'), ('nao', 'Não')]


class VeiculoPainelFiltroForm(forms.Form):
    """Filtro e ordenação da lista "Meus veículos". Ao contrário do filtro da
    vitrine, considera todo o estoque do dono (inclusive indisponível), já que
    aqui ele está gerenciando, não comprando."""

    tipo = forms.ChoiceField(required=False, label="Tipo")
    marca = forms.ChoiceField(required=False, label="Marca")
    disponivel = forms.ChoiceField(required=False, label="Disponível", choices=SIM_NAO)
    destaque = forms.ChoiceField(required=False, label="Destaque", choices=SIM_NAO)
    ordenar = forms.ChoiceField(required=False, label="Ordenar por", choices=ORDENACOES_VEICULO)

    def __init__(self, *args, garagem=None, **kwargs):
        super().__init__(*args, **kwargs)
        veiculos = garagem.veiculos.all() if garagem else Veiculo.objects.none()

        self.fields['tipo'].choices = [('', 'Todos')] + list(Veiculo.Tipo.choices)

        marcas = veiculos.order_by('marca').values_list('marca', flat=True).distinct()
        self.fields['marca'].choices = [('', 'Todas')] + [(m, m) for m in marcas]

        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-select form-select-sm')

    def aplicar(self, queryset):
        if not self.is_valid():
            return queryset

        dados = self.cleaned_data
        if dados.get('tipo'):
            queryset = queryset.filter(tipo=dados['tipo'])
        if dados.get('marca'):
            queryset = queryset.filter(marca=dados['marca'])
        if dados.get('disponivel') == 'sim':
            queryset = queryset.filter(disponivel=True)
        elif dados.get('disponivel') == 'nao':
            queryset = queryset.filter(disponivel=False)
        if dados.get('destaque') == 'sim':
            queryset = queryset.filter(destaque=True)
        elif dados.get('destaque') == 'nao':
            queryset = queryset.filter(destaque=False)

        ordenar = dados.get('ordenar')
        return queryset.order_by(*([ordenar] if ordenar else ['-destaque', '-criado_em']))


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


class GaragemForm(ImagemOtimizadaMixin, forms.ModelForm):
    class Meta:
        model = Garagem
        fields = [
            'logo', 'capa', 'endereco', 'horario_funcionamento', 'instagram_url', 'facebook_url',
            'cor_destaque', 'taxa_juros_mensal_padrao',
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
            'cor_destaque': 'Cor dos botões e detalhes da sua vitrine e do seu painel.',
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
        self.fields['logo'].widget.attrs['accept'] = 'image/*'
        self.fields['capa'].widget.attrs['accept'] = 'image/*'

        media = taxa_media_de_mercado()
        if media:
            self.fields['taxa_juros_mensal_padrao'].help_text = (
                "Opcional. Em branco, o simulador usa a média de mercado do Banco Central: "
                f"{localize(media.taxa_mensal)}% ao mês (ref. {media.referencia:%m/%Y})."
            )

    def clean_logo(self):
        return self._limpar_imagem_otimizada('logo')

    def clean_capa(self):
        return self._limpar_imagem_otimizada('capa')
