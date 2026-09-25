import re
import time

from django import forms

from leads.forms import SEGUNDOS_MINIMOS_PARA_ENVIO

from .models import InteresseGaragem


class InteresseGaragemForm(forms.ModelForm):
    # Mesma proteção dos formulários públicos das vitrines (leads.forms.AntiSpamFormMixin):
    # honeypot invisível + tempo mínimo de preenchimento. Não herda dela porque o texto do
    # consentimento aqui é outro (contato da plataforma, não política de privacidade da garagem).
    site = forms.CharField(required=False, widget=forms.HiddenInput)
    iniciado_em = forms.FloatField(required=False, widget=forms.HiddenInput)
    aceito_contato = forms.BooleanField(
        required=True,
        error_messages={'required': 'Para enviar, é preciso concordar em ser contatado.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = InteresseGaragem
        fields = ['nome', 'nome_garagem', 'telefone', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'name'}),
            'nome_garagem': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'organization'}),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '(17) 99999-9999',
                'type': 'tel', 'inputmode': 'tel', 'autocomplete': 'tel',
            }),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {'telefone': 'Seu WhatsApp', 'mensagem': 'Quer contar algo? (opcional)'}

    def clean_telefone(self):
        digitos = re.sub(r'\D', '', self.cleaned_data.get('telefone', ''))
        if not 10 <= len(digitos) <= 13:
            raise forms.ValidationError('Informe o DDD e o número, ex: (17) 99999-9999.')
        return digitos

    def clean(self):
        cleaned_data = super().clean()
        iniciado_em = cleaned_data.get('iniciado_em')
        rapido_demais = iniciado_em and time.time() - iniciado_em < SEGUNDOS_MINIMOS_PARA_ENVIO
        if cleaned_data.get('site') or rapido_demais:
            self.add_error(None, 'Não foi possível enviar. Atualize a página e tente novamente.')
        return cleaned_data
