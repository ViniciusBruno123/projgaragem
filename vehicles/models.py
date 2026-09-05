from django.db import models

from tenants.models import Garagem


class Veiculo(models.Model):
    class Combustivel(models.TextChoices):
        GASOLINA = 'gasolina', 'Gasolina'
        ETANOL = 'etanol', 'Etanol'
        FLEX = 'flex', 'Flex'
        DIESEL = 'diesel', 'Diesel'
        ELETRICO = 'eletrico', 'Elétrico'

    garagem = models.ForeignKey(Garagem, on_delete=models.CASCADE, related_name='veiculos')
    titulo = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170)
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    ano_fabricacao = models.PositiveSmallIntegerField()
    ano_modelo = models.PositiveSmallIntegerField()
    quilometragem = models.PositiveIntegerField()
    combustivel = models.CharField(max_length=10, choices=Combustivel.choices)
    cilindrada = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Cilindradas (cc), quando aplicável. Ex: 160"
    )
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)
    destaque = models.BooleanField(default=False, help_text="Aparece na frontpage da garagem.")
    disponivel = models.BooleanField(default=True, help_text="Desmarque para ocultar da vitrine (vendido/reservado).")
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


class FotoVeiculo(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='veiculos/%Y/%m/')
    principal = models.BooleanField(default=False)
    ordem = models.PositiveSmallIntegerField(default=0)

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
