import time

from django import forms

from .models import Avaliacao, Proposta

# Tempo mínimo entre a página carregar e o formulário ser enviado. Um robô que
# preenche e envia na hora cai nesse limite; uma pessoa lendo o formulário não.
SEGUNDOS_MINIMOS_PARA_ENVIO = 3


class AntiSpamFormMixin(forms.Form):
    """Honeypot + carimbo de tempo, compartilhados por todo formulário público desta
    plataforma (proposta/contato e avaliação de usados) — os dois são o alvo mais exposto
    do site a robôs, por não exigirem login.

    Herda de forms.Form (não é um mixin "puro") de propósito: o metaclasse do Django só
    registra como campo de verdade (form.fields, validação, render) o que está declarado
    numa classe que passou por DeclarativeFieldsMetaclass. Um mixin comum (sem essa base)
    deixa esses campos como atributos Python invisíveis pro form — inclusive o checkbox de
    consentimento, que passaria a validar sempre como Ok sem aparecer na página."""

    # Honeypot: campo invisível para quem enxerga a página, que só um robô preenche.
    # O nome não avisa que é uma armadilha.
    site = forms.CharField(required=False, widget=forms.HiddenInput)
    # Carimbo de hora enviado junto com a página (ver initial na view). Serve só
    # para medir o tempo de preenchimento, não é lido nem gravado.
    iniciado_em = forms.FloatField(required=False, widget=forms.HiddenInput)

    aceito_privacidade = forms.BooleanField(
        required=True,
        error_messages={'required': 'Para enviar, é preciso concordar com a política de privacidade.'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        iniciado_em = cleaned_data.get('iniciado_em')
        preenchido_rapido_demais = iniciado_em and time.time() - iniciado_em < SEGUNDOS_MINIMOS_PARA_ENVIO
        if cleaned_data.get('site') or preenchido_rapido_demais:
            # Erro genérico de propósito: não ajuda um robô a descobrir qual campo é a armadilha.
            self.add_error(None, 'Não foi possível enviar sua mensagem. Atualize a página e tente novamente.')
        return cleaned_data


class PropostaForm(AntiSpamFormMixin, forms.ModelForm):
    class Meta:
        model = Proposta
        fields = ['nome', 'telefone', 'email', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(17) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AvaliacaoForm(AntiSpamFormMixin, forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nome', 'telefone', 'email', 'tipo', 'marca', 'modelo', 'ano', 'quilometragem', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(17) 99999-9999'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'quilometragem': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
