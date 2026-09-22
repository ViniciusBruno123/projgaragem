from django.db import models

from tenants.models import Garagem


class Veiculo(models.Model):
    class Tipo(models.TextChoices):
        MOTO = 'moto', 'Moto'
        CARRO = 'carro', 'Carro'

    class Combustivel(models.TextChoices):
        GASOLINA = 'gasolina', 'Gasolina'
        ETANOL = 'etanol', 'Álcool'
        FLEX = 'flex', 'Flex'
        DIESEL = 'diesel', 'Diesel'
        ELETRICO = 'eletrico', 'Elétrico'

    garagem = models.ForeignKey(Garagem, on_delete=models.CASCADE, related_name='veiculos')
    tipo = models.CharField(max_length=5, choices=Tipo.choices, default=Tipo.MOTO)
    titulo = models.CharField('Título', max_length=150)
    slug = models.SlugField(max_length=170, blank=True, help_text="Gerado automaticamente a partir do título.")
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    ano_fabricacao = models.PositiveSmallIntegerField('Ano de fabricação')
    ano_modelo = models.PositiveSmallIntegerField('Ano do modelo')
    quilometragem = models.PositiveIntegerField('Quilometragem (km)')
    combustivel = models.CharField('Combustível', max_length=10, choices=Combustivel.choices)
    cilindrada = models.PositiveSmallIntegerField(
        'Cilindrada (cc)', null=True, blank=True, help_text="Cilindradas (cc) — apenas para motos. Ex: 160"
    )
    potencia_motor = models.DecimalField(
        'Potência do motor (litros)', max_digits=2, decimal_places=1, null=True, blank=True,
        help_text="Potência do motor em litros — apenas para carros. Ex: 1.0, 1.6, 2.0",
    )
    preco = models.DecimalField('Preço (R$)', max_digits=10, decimal_places=2)
    descricao = models.TextField('Descrição', blank=True)
    destaque = models.BooleanField(default=False, help_text="Aparece no carrossel de destaques da vitrine.")
    disponivel = models.BooleanField('Disponível', default=True, help_text="Desmarque para ocultar da vitrine (vendido/reservado).")
    aceita_troca = models.BooleanField(default=False, help_text="Exibe o selo \"Aceita troca\" no anúncio.")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        unique_together = ('garagem', 'slug')
        ordering = ['-destaque', '-criado_em']

    def __str__(self):
        return f"{self.titulo} ({self.garagem.nome})"

    @property
    def ano_curto(self):
        """Ano só com os dois últimos dígitos: 1999/2000 -> 99/00; iguais aparecem uma vez."""
        fabricacao = f'{self.ano_fabricacao % 100:02d}'
        if self.ano_fabricacao == self.ano_modelo:
            return fabricacao
        return f'{fabricacao}/{self.ano_modelo % 100:02d}'

    @property
    def fotos_extra_urls(self):
        """URLs das próximas fotos (depois da principal), separadas por "|", para o card da
        vitrine mostrar uma prévia ao passar o mouse (ver static/js/vitrine.js). Só o texto
        da URL entra na página — a imagem em si só é baixada se o visitante passar o mouse,
        então isso não pesa a página numa garagem com dezenas de veículos. Usa self.fotos.all()
        (não um novo .filter()) para reaproveitar o prefetch_related da view, sem consulta extra.
        """
        fotos = list(self.fotos.all())[1:4]
        return '|'.join(foto.imagem.url for foto in fotos)

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.tipo == self.Tipo.MOTO and self.potencia_motor:
            errors['potencia_motor'] = 'Potência do motor é um campo exclusivo para carros.'
        if self.tipo == self.Tipo.CARRO and self.cilindrada:
            errors['cilindrada'] = 'Cilindrada é um campo exclusivo para motos.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._gerar_slug_unico()
        super().save(*args, **kwargs)

    def _gerar_slug_unico(self):
        from django.utils.text import slugify

        base = slugify(self.titulo)
        slug = base
        contador = 2
        while Veiculo.objects.filter(garagem=self.garagem, slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{contador}"
            contador += 1
        return slug


class FotoVeiculo(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField('Foto', upload_to='veiculos/%Y/%m/')
    principal = models.BooleanField('Foto principal', default=False)
    ordem = models.PositiveSmallIntegerField('Ordem de exibição', default=0)

    class Meta:
        verbose_name = 'Foto do veículo'
        verbose_name_plural = 'Fotos do veículo'
        ordering = ['-principal', 'ordem']

    def __str__(self):
        return f"Foto de {self.veiculo.titulo}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.principal:
            FotoVeiculo.objects.filter(veiculo=self.veiculo).exclude(pk=self.pk).update(principal=False)
