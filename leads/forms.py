from django import forms

from .models import Proposta


class PropostaForm(forms.ModelForm):
    aceito_privacidade = forms.BooleanField(
        required=True,
        error_messages={'required': 'Para enviar, é preciso concordar com a política de privacidade.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = Proposta
        fields = ['nome', 'telefone', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(17) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
