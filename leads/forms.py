from django import forms

from .models import Proposta


class PropostaForm(forms.ModelForm):
    class Meta:
        model = Proposta
        fields = ['nome', 'telefone', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(17) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
