import re

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.formats import localize

from financing.services import taxa_media_de_mercado

from tenants.models import Banner, Garagem
from vehicles.forms import ImagemOtimizadaMixin
from vehicles.forms import FotoVeiculoForm as BaseFotoVeiculoForm
from vehicles.models import FotoVeiculo, Veiculo


class EstiloLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class SelectComPreviaDeFonte(forms.Select):
    """<select> de fonte com uma amostra "Aa" em cada opção, já na fonte que ela representa.

    O valor de cada escolha é o próprio nome da família (ver Garagem.FonteTitulo), então dá
    para usá-lo direto como font-family do <option> — sem precisar de uma tabela à parte.
    Funciona nos navegadores baseados em Chromium e no Firefox; no Safari a "Aa" aparece sem
    estilo (degrada bem: o texto continua lá, só não fica na fonte de amostra).

    O navegador só aplica esse estilo na LISTA aberta — a caixa fechada do <select> sempre usa
    a fonte do próprio elemento, não a da opção escolhida (limitação do <select> nativo). O
    atributo data-previa-fonte abaixo é lido por static/js/previa_fonte.js, que copia a fonte
    da opção selecionada para o próprio <select>, também na caixa fechada.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['data-previa-fonte'] = 'true'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option['attrs']['style'] = f"font-family: '{value}', sans-serif;"
            option['label'] = f"{label} — Aa"
        return option


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
        # FileInput simples em vez do ClearableFileInput padrão do Django: o painel já tem
        # sua própria prévia da foto atual (template) e um "Excluir" pra linha inteira
        # (can_delete do formset) — o "Atualmente / Modificar / Limpar" do widget padrão
        # só duplicava essa informação.
        self.fields['imagem'].widget = forms.FileInput(attrs={'accept': 'image/*', 'data-cortar': 'veiculo'})
        self.fields['imagem'].widget.attrs.setdefault('class', 'form-control')
        self.fields['ordem'].widget.attrs.setdefault('class', 'form-control form-control-sm input-ordem')
        self.fields['principal'].widget.attrs.setdefault('class', 'form-check-input')


class FotoVeiculoBaseFormSet(BaseInlineFormSet):
    """Só estiliza o checkbox de excluir (can_delete não passa pelo __init__ do form)."""

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if 'DELETE' in form.fields:
            form.fields['DELETE'].widget.attrs['class'] = 'form-check-input'


# extra=6: várias fotos de uma vez, sem precisar salvar e reabrir a cada uma.
FotoVeiculoFormSet = inlineformset_factory(
    Veiculo, FotoVeiculo,
    form=FotoVeiculoForm, formset=FotoVeiculoBaseFormSet,
    extra=6, can_delete=True,
)


class GaragemForm(ImagemOtimizadaMixin, forms.ModelForm):
    class Meta:
        model = Garagem
        fields = [
            'logo', 'ocultar_logo_capa', 'ocultar_nome_capa', 'telefone_whatsapp',
            'endereco', 'latitude', 'longitude', 'google_place_id', 'horario_funcionamento',
            'instagram_url', 'facebook_url', 'cor_destaque', 'cor_titulo', 'fonte_titulo',
            'taxa_juros_mensal_padrao',
        ]
        labels = {
            'telefone_whatsapp': 'Telefone do WhatsApp',
            'endereco': 'Endereço',
            'horario_funcionamento': 'Horário de funcionamento',
            'instagram_url': 'Link do Instagram',
            'facebook_url': 'Link do Facebook',
            'cor_destaque': 'Cor da vitrine',
        }
        help_texts = {
            'telefone_whatsapp': 'Para onde vão as propostas dos clientes. Pode digitar com parênteses e traço.',
            'horario_funcionamento': 'Aparece no rodapé da vitrine.',
            'cor_destaque': 'Cor dos botões e detalhes da sua vitrine e do seu painel.',
        }
        widgets = {
            'telefone_whatsapp': forms.TextInput(attrs={'placeholder': '(17) 99999-9999'}),
            'horario_funcionamento': forms.TextInput(attrs={'placeholder': 'Ex: Seg a Sex, 8h às 18h'}),
            'cor_destaque': forms.TextInput(attrs={'type': 'color', 'style': 'height: 2.5rem; padding: 0.25rem;'}),
            'cor_titulo': forms.TextInput(attrs={'type': 'color', 'style': 'height: 2.5rem; padding: 0.25rem;'}),
            'fonte_titulo': SelectComPreviaDeFonte,
            'taxa_juros_mensal_padrao': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'placeholder': 'Ex: 1,99'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'google_place_id': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            elif not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.setdefault('class', 'form-control')
        self.fields['logo'].widget.attrs['accept'] = 'image/*'
        # Corte no upload (ver static/js/cortar_foto.js): a logo aparece inteira (object-fit:
        # contain), então o corte é livre.
        self.fields['logo'].widget.attrs['data-cortar'] = 'livre'

        # Com a chave do Maps configurada, "endereco" some da lista e vira campo oculto —
        # quem digita ele é o widget de busca do Google Maps (ver dados_garagem.html/
        # endereco_autocomplete.js), não mais texto livre.
        if settings.GOOGLE_MAPS_API_KEY:
            self.fields['endereco'].widget = forms.HiddenInput()

        media = taxa_media_de_mercado()
        if media:
            self.fields['taxa_juros_mensal_padrao'].help_text = (
                "Opcional. Em branco, o simulador usa a média de mercado do Banco Central: "
                f"{localize(media.taxa_mensal)}% ao mês (ref. {media.referencia:%m/%Y})."
            )

    def clean_telefone_whatsapp(self):
        # O dono digita como quiser (com DDD entre parênteses, traço etc.); guardamos só
        # dígitos. Sem DDI, assume Brasil — é o público desta plataforma.
        numero = re.sub(r'\D', '', self.cleaned_data.get('telefone_whatsapp', ''))
        if len(numero) in (10, 11):
            numero = '55' + numero
        return numero

    def clean_logo(self):
        return self._limpar_imagem_otimizada('logo')


class BannerForm(ImagemOtimizadaMixin, forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['imagem', 'ordem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sempre cortada (cover) numa faixa larga — a altura real do cabeçalho varia com a
        # largura da tela (não é uma proporção fixa), então 5:1 é uma aproximação: fica perto
        # do formato de um notebook comum sem obrigar o cabeçalho a virar uma faixa enorme; o
        # "cover" ainda ajusta um pouco em cada tela (ver static/css/site.css, .site-header--capa).
        self.fields['imagem'].widget = forms.FileInput(attrs={'accept': 'image/*', 'data-cortar': '5/1'})
        self.fields['imagem'].widget.attrs.setdefault('class', 'form-control')
        self.fields['ordem'].widget.attrs.setdefault('class', 'form-control form-control-sm input-ordem')

    def clean_imagem(self):
        return self._limpar_imagem_otimizada('imagem')

    def has_changed(self):
        """Mesma proteção do FotoVeiculoForm (vehicles/forms.py): "ordem" sozinho não pode
        obrigar a enviar uma imagem num slot extra vazio do formset."""
        return bool(set(self.changed_data) - {'ordem'})


class BannerBaseFormSet(BaseInlineFormSet):
    """Só estiliza o checkbox de excluir (can_delete não passa pelo __init__ do form)."""

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if 'DELETE' in form.fields:
            form.fields['DELETE'].widget.attrs['class'] = 'form-check-input'


# extra=3: banners são de campanha, não um catálogo grande como as fotos de veículo — 3 de
# uma vez cobre bem "um banner base + um ou dois de campanha".
BannerFormSet = inlineformset_factory(
    Garagem, Banner,
    form=BannerForm, formset=BannerBaseFormSet,
    extra=3, can_delete=True,
)
