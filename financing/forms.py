from decimal import Decimal

from django import forms


class SimulacaoFinanciamentoForm(forms.Form):
    valor_entrada = forms.DecimalField(
        min_value=Decimal('0'), max_digits=10, decimal_places=2, initial=Decimal('0'),
        required=False, label="Valor de entrada",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    )
    numero_parcelas = forms.IntegerField(
        min_value=1, max_value=60, initial=24, label="Número de parcelas",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )

    def clean_valor_entrada(self):
        return self.cleaned_data.get('valor_entrada') or Decimal('0')
