from decimal import Decimal

from django import forms
from django.utils.formats import number_format

from vehicles.models import Veiculo


# Ordenação da lista. Vazio = a ordem padrão da vitrine (motos antes de carros, mais recentes
# primeiro); qualquer outra ordem mistura os tipos, então a página deixa de agrupar por tipo.
ORDENACOES_VITRINE = [
    ('', 'Padrão'),
    ('preco', 'Menor preço'),
    ('-preco', 'Maior preço'),
    ('-ano_modelo', 'Mais novos'),
    ('quilometragem', 'Menor km'),
]


class FiltroVeiculosForm(forms.Form):
    tipo = forms.ChoiceField(required=False, label="Tipo")
    marca = forms.ChoiceField(required=False, label="Marca")
    cambio = forms.ChoiceField(required=False, label="Câmbio")
    cilindrada = forms.ChoiceField(required=False, label="CC (motos)")
    potencia_motor = forms.ChoiceField(required=False, label="Motor (carros)")
    ano_min = forms.ChoiceField(required=False, label="Ano mínimo")
    ano_max = forms.ChoiceField(required=False, label="Ano máximo")
    preco_min = forms.DecimalField(required=False, min_value=Decimal('0'), label="Preço mínimo")
    preco_max = forms.DecimalField(required=False, min_value=Decimal('0'), label="Preço máximo")
    ordenar = forms.ChoiceField(required=False, label="Ordenar por", choices=ORDENACOES_VITRINE)

    def __init__(self, *args, garagem=None, **kwargs):
        super().__init__(*args, **kwargs)
        disponiveis = garagem.veiculos.filter(disponivel=True) if garagem else Veiculo.objects.none()

        self.fields['tipo'].choices = [('', 'Todos')] + list(Veiculo.Tipo.choices)

        marcas = disponiveis.order_by('marca').values_list('marca', flat=True).distinct()
        self.fields['marca'].choices = [('', 'Todas')] + [(m, m) for m in marcas]

        cambios_em_estoque = set(disponiveis.exclude(cambio='').values_list('cambio', flat=True))
        self.fields['cambio'].choices = [('', 'Todos')] + [
            (valor, rotulo) for valor, rotulo in Veiculo.Cambio.choices if valor in cambios_em_estoque
        ]

        cilindradas = (
            disponiveis.filter(cilindrada__isnull=False)
            .order_by('cilindrada').values_list('cilindrada', flat=True).distinct()
        )
        self.fields['cilindrada'].choices = [('', 'Todas')] + [(cc, f"{cc}cc") for cc in cilindradas]

        potencias = (
            disponiveis.filter(potencia_motor__isnull=False)
            .order_by('potencia_motor').values_list('potencia_motor', flat=True).distinct()
        )
        self.fields['potencia_motor'].choices = [('', 'Todas')] + [(p, str(p)) for p in potencias]

        anos = disponiveis.order_by('ano_modelo').values_list('ano_modelo', flat=True).distinct()
        anos_choices = [(a, str(a)) for a in anos]
        self.fields['ano_min'].choices = [('', 'Todos')] + anos_choices
        self.fields['ano_max'].choices = [('', 'Todos')] + anos_choices

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select form-select-sm')
            else:
                field.widget.attrs.setdefault('class', 'form-control form-control-sm')

    def aplicar(self, queryset):
        if not self.is_valid():
            return queryset

        dados = self.cleaned_data
        if dados.get('tipo'):
            queryset = queryset.filter(tipo=dados['tipo'])
        if dados.get('marca'):
            queryset = queryset.filter(marca=dados['marca'])
        if dados.get('cambio'):
            queryset = queryset.filter(cambio=dados['cambio'])
        if dados.get('cilindrada'):
            queryset = queryset.filter(cilindrada=dados['cilindrada'])
        if dados.get('potencia_motor'):
            queryset = queryset.filter(potencia_motor=dados['potencia_motor'])
        if dados.get('ano_min'):
            queryset = queryset.filter(ano_modelo__gte=dados['ano_min'])
        if dados.get('ano_max'):
            queryset = queryset.filter(ano_modelo__lte=dados['ano_max'])
        if dados.get('preco_min') is not None:
            queryset = queryset.filter(preco__gte=dados['preco_min'])
        if dados.get('preco_max') is not None:
            queryset = queryset.filter(preco__lte=dados['preco_max'])
        return queryset

    def ordem(self):
        """Campo(s) do order_by pedidos pelo visitante, ou None para a ordem padrão da vitrine."""
        if not self.is_valid() or not self.cleaned_data.get('ordenar'):
            return None
        return (self.cleaned_data['ordenar'], '-criado_em')

    def ativos(self, parametros):
        """Filtros em uso, um por chip na página; cada um traz o link que remove só ele
        (parametros = request.GET). A ordenação não conta: não restringe o resultado."""
        if not self.is_valid():
            return []
        chips = []
        for nome, campo in self.fields.items():
            valor = self.cleaned_data.get(nome)
            if nome == 'ordenar' or valor in (None, ''):
                continue
            if isinstance(campo, forms.ChoiceField):
                texto = {str(k): v for k, v in campo.choices}.get(str(valor), valor)
            else:
                texto = f"R$ {number_format(valor, 0, use_l10n=True, force_grouping=True)}"
            restantes = parametros.copy()
            restantes.pop(nome, None)
            chips.append({'rotulo': campo.label, 'valor': texto, 'remover': '?' + restantes.urlencode()})
        return chips
