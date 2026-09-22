from decimal import Decimal

from django import forms

from vehicles.models import Veiculo


class FiltroVeiculosForm(forms.Form):
    tipo = forms.ChoiceField(required=False, label="Tipo")
    marca = forms.ChoiceField(required=False, label="Marca")
    cilindrada = forms.ChoiceField(required=False, label="Cilindrada (motos)")
    potencia_motor = forms.ChoiceField(required=False, label="Motor (carros)")
    preco_min = forms.DecimalField(required=False, min_value=Decimal('0'), label="Preço mínimo")
    preco_max = forms.DecimalField(required=False, min_value=Decimal('0'), label="Preço máximo")

    def __init__(self, *args, garagem=None, **kwargs):
        super().__init__(*args, **kwargs)
        disponiveis = garagem.veiculos.filter(disponivel=True) if garagem else Veiculo.objects.none()

        self.fields['tipo'].choices = [('', 'Todos')] + list(Veiculo.Tipo.choices)

        marcas = disponiveis.order_by('marca').values_list('marca', flat=True).distinct()
        self.fields['marca'].choices = [('', 'Todas')] + [(m, m) for m in marcas]

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
        if dados.get('cilindrada'):
            queryset = queryset.filter(cilindrada=dados['cilindrada'])
        if dados.get('potencia_motor'):
            queryset = queryset.filter(potencia_motor=dados['potencia_motor'])
        if dados.get('preco_min') is not None:
            queryset = queryset.filter(preco__gte=dados['preco_min'])
        if dados.get('preco_max') is not None:
            queryset = queryset.filter(preco__lte=dados['preco_max'])
        return queryset
