from django.db import models

from tenants.models import Garagem
from vehicles.models import Veiculo


class Proposta(models.Model):
    class Canal(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        EMAIL = 'email', 'E-mail'

    class Status(models.TextChoices):
        NOVA = 'nova', 'Nova'
        EM_CONTATO = 'em_contato', 'Em contato'
        CONVERTIDA = 'convertida', 'Vendido para esse cliente'
        PERDIDA = 'perdida', 'Sem retorno / Perdida'

    garagem = models.ForeignKey(Garagem, on_delete=models.CASCADE, related_name='propostas')
    veiculo = models.ForeignKey(
        Veiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='propostas'
    )
    nome = models.CharField(max_length=120)
    telefone = models.CharField(max_length=20)
    email = models.EmailField('E-mail (opcional)', blank=True)
    mensagem = models.TextField('Mensagem', blank=True)
    canal = models.CharField(max_length=10, choices=Canal.choices, default=Canal.WHATSAPP)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NOVA)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proposta'
        verbose_name_plural = 'Propostas'
        ordering = ['-criado_em']

    def __str__(self):
        alvo = self.veiculo.titulo if self.veiculo else 'Contato geral'
        return f"{self.nome} - {alvo}"


class Avaliacao(models.Model):
    """Pedido de avaliação de um veículo QUE O VISITANTE quer vender ou trocar — o inverso
    da Proposta (que é sobre um veículo do catálogo da garagem). Sem preço: quem avalia é
    a garagem, pelo WhatsApp, depois do envio."""

    class Status(models.TextChoices):
        NOVA = 'nova', 'Nova'
        EM_CONTATO = 'em_contato', 'Em contato'
        AVALIADA = 'avaliada', 'Avaliada'
        COMPRADA = 'comprada', 'Comprada'
        RECUSADA = 'recusada', 'Recusada'

    garagem = models.ForeignKey(Garagem, on_delete=models.CASCADE, related_name='avaliacoes')
    veiculo_interesse = models.ForeignKey(
        Veiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='avaliacoes',
        help_text="Veículo do catálogo que a pessoa quer levar na troca, quando o pedido veio da página dele.",
    )
    nome = models.CharField(max_length=120)
    telefone = models.CharField(max_length=20)
    email = models.EmailField('E-mail (opcional)', blank=True)
    tipo = models.CharField(max_length=5, choices=Veiculo.Tipo.choices, default=Veiculo.Tipo.CARRO)
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    ano = models.PositiveSmallIntegerField('Ano')
    quilometragem = models.PositiveIntegerField('Quilometragem (km)')
    observacoes = models.TextField(
        'Observações', blank=True,
        help_text="Estado de conservação, opcionais, motivo da venda — o que ajudar na avaliação.",
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NOVA)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avaliação de veículo'
        verbose_name_plural = 'Avaliações de veículo'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome} - {self.marca} {self.modelo} {self.ano}"


class FotoAvaliacao(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='fotos')
    imagem = models.ImageField(upload_to='avaliacoes/%Y/%m/')

    class Meta:
        verbose_name = 'Foto da avaliação'
        verbose_name_plural = 'Fotos da avaliação'
