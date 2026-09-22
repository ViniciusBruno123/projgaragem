import re
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

HEX_COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')


class Garagem(models.Model):
    class Status(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        ATRASADO = 'atrasado', 'Atrasado'
        SUSPENSO = 'suspenso', 'Suspenso'

    class Plano(models.TextChoices):
        BASICO = 'basico', 'Básico'
        INTERMEDIARIO = 'intermediario', 'Intermediário'
        AVANCADO = 'avancado', 'Avançado'

    # Quantos veículos cada plano permite cadastrar (ver Garagem.limite_veiculos). Mudar o
    # plano é feito pelo administrador no /admin/, junto com o valor da mensalidade cobrada
    # — não há hoje uma tabela de preço por plano, só o limite de estoque.
    LIMITE_VEICULOS_POR_PLANO = {
        Plano.BASICO: 50,
        Plano.INTERMEDIARIO: 100,
        Plano.AVANCADO: 300,
    }

    class FonteTitulo(models.TextChoices):
        """Cada opção é o nome exato da família no Google Fonts (ver templates/base.html,
        onde todas são carregadas) — o valor salvo já é o font-family usado no CSS."""
        BIG_SHOULDERS = 'Big Shoulders', 'Moderna (padrão)'
        OSWALD = 'Oswald', 'Condensada'
        BEBAS_NEUE = 'Bebas Neue', 'Impacto'
        ANTON = 'Anton', 'Extra bold'
        PLAYFAIR_DISPLAY = 'Playfair Display', 'Clássica'
        ARCHIVO_BLACK = 'Archivo Black', 'Robusta'
        POPPINS = 'Poppins', 'Geométrica'
        TEKO = 'Teko', 'Alta e fina'
        BARLOW_CONDENSED = 'Barlow Condensed', 'Condensada e limpa'
        RAJDHANI = 'Rajdhani', 'Tecnológica'

    dono = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='garagem'
    )
    nome = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, db_index=True)
    telefone_whatsapp = models.CharField(
        max_length=20,
        help_text="Somente dígitos, com DDI e DDD. Ex: 5517999999999",
    )
    email_contato = models.EmailField()
    cidade = models.CharField(max_length=100, default='Catanduva')
    endereco = models.CharField(max_length=200, blank=True)
    horario_funcionamento = models.CharField(
        max_length=150, blank=True, help_text="Ex: Seg a Sex, 8h às 18h"
    )
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    logo = models.ImageField(
        'Logo', upload_to='garagens/logos/', null=True, blank=True,
        help_text="Aparece ao lado do nome da garagem, na vitrine e no painel.",
    )
    capa = models.ImageField(
        'Faixa superior (capa)', upload_to='garagens/capas/', null=True, blank=True,
        help_text="Imagem larga que aparece atrás do cabeçalho da sua vitrine. Opcional.",
    )
    cor_destaque = models.CharField(
        max_length=7, default='#0F5C4D',
        help_text="Cor de destaque da sua vitrine, em hexadecimal (ex: #0F5C4D).",
    )
    cor_titulo = models.CharField(
        'Cor do nome da garagem', max_length=7, default='#1A1A18',
        help_text=(
            "Cor do nome da garagem, da cidade e do botão \"Fale conosco\" no topo da vitrine — os três mudam "
            "juntos, para não sumir um deles se o fundo mudar de cor. Padrão: escuro."
        ),
    )
    fonte_titulo = models.CharField(
        'Fonte do nome da garagem', max_length=30,
        choices=FonteTitulo.choices, default=FonteTitulo.BIG_SHOULDERS,
        help_text="Fonte do nome da garagem no topo da vitrine.",
    )
    taxa_juros_mensal_padrao = models.DecimalField(
        'Taxa de juros própria (% ao mês)', max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('20'))],
        help_text="Opcional. Em branco, o simulador usa a taxa média de mercado do Banco Central.",
    )
    plano = models.CharField(
        max_length=20, choices=Plano.choices, default=Plano.BASICO,
        help_text="Define quantos veículos a garagem pode cadastrar (ver LIMITE_VEICULOS_POR_PLANO).",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ATIVO)
    suspensa_manualmente_em = models.DateTimeField(null=True, blank=True)
    ultimo_aviso_atraso_enviado_em = models.DateTimeField(null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Garagem'
        verbose_name_plural = 'Garagens'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def limite_veiculos(self):
        return self.LIMITE_VEICULOS_POR_PLANO[self.plano]

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.telefone_whatsapp:
            if not self.telefone_whatsapp.isdigit():
                errors['telefone_whatsapp'] = 'Use apenas dígitos (DDI + DDD + número), sem espaços ou símbolos.'
            elif not (10 <= len(self.telefone_whatsapp) <= 15):
                errors['telefone_whatsapp'] = 'Informe o DDI + DDD + número (ex: 5517999999999).'
        if self.cor_destaque and not HEX_COLOR_RE.match(self.cor_destaque):
            errors['cor_destaque'] = 'Use o formato hexadecimal, ex: #0F5C4D.'
        if self.cor_titulo and not HEX_COLOR_RE.match(self.cor_titulo):
            errors['cor_titulo'] = 'Use o formato hexadecimal, ex: #1A1A18.'
        if errors:
            raise ValidationError(errors)
