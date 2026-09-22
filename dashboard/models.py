from django.db import models


class TentativaLoginFalha(models.Model):
    """Registro de uma tentativa de login que falhou, para o limite de tentativas.

    Guardamos o nome de usuário digitado (mesmo que não exista) e o IP de origem,
    porque bloqueamos tanto por usuário quanto por IP — ver dashboard/security.py.
    Linhas antigas são apagadas automaticamente quando saem da janela de contagem.
    """

    usuario = models.CharField(max_length=150, blank=True, db_index=True)
    ip = models.GenericIPAddressField(db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tentativa de login falha'
        verbose_name_plural = 'Tentativas de login falhas'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.usuario or '(sem usuário)'} — {self.ip} em {self.criado_em:%d/%m/%Y %H:%M}"
