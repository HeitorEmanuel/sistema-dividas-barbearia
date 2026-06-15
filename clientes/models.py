from django.conf import settings
from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    nome = models.CharField('nome', max_length=100)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    observacao = models.TextField('observação', blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True, null=True, blank=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def dividas_pendentes(self):
        return self.dividas.filter(status=Divida.Status.PENDENTE)


class Divida(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        PAGA = 'paga', 'Paga'

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='dividas',
        verbose_name='cliente'
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dividas_criadas',
        verbose_name='funcionário que criou',
    )
    pago_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dividas_pagas',
        verbose_name='funcionário que recebeu',
    )
    valor = models.DecimalField('valor', max_digits=10, decimal_places=2)
    descricao = models.CharField('descrição', max_length=200)
    data_criacao = models.DateTimeField('data de criação', auto_now_add=True)
    data_pagamento = models.DateTimeField('data de pagamento', null=True, blank=True)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )

    class Meta:
        verbose_name = 'Dívida'
        verbose_name_plural = 'Dívidas'
        ordering = ['status', '-data_criacao']

    def __str__(self):
        return f'{self.cliente.nome} - R$ {self.valor}'

    def marcar_como_paga(self, usuario=None):
        self.status = self.Status.PAGA
        self.data_pagamento = timezone.now()
        if usuario and usuario.is_authenticated:
            self.pago_por = usuario
            self.save(update_fields=['status', 'data_pagamento', 'pago_por'])
        else:
            self.save(update_fields=['status', 'data_pagamento'])


class Historico(models.Model):
    usuario = models.CharField('usuário', max_length=100)
    acao = models.CharField('ação', max_length=255)
    data = models.DateTimeField('data', auto_now_add=True)

    class Meta:
        verbose_name = 'Histórico'
        verbose_name_plural = 'Histórico'
        ordering = ['-data']

    def __str__(self):
        return f'{self.usuario} - {self.acao}'
