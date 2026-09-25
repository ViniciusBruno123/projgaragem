from django.db import models


class InteresseGaragem(models.Model):
    """Contato deixado no formulário da landing page (raiz do site) por um dono de garagem
    interessado na plataforma — o "lead" da própria plataforma, diferente do lead de
    cada garagem (leads.Proposta)."""

    nome = models.CharField('Nome', max_length=120)
    nome_garagem = models.CharField('Nome da garagem', max_length=120)
    telefone = models.CharField('WhatsApp', max_length=20)
    mensagem = models.TextField('Mensagem', blank=True)
    atendido = models.BooleanField('Já atendido', default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Interesse de garagem'
        verbose_name_plural = 'Interesses de garagens'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} — {self.nome_garagem}'
