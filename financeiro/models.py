from django.db import models

from django.db import models
from core.models import ModeloSaaS
from cadastros.models import Cadastro

class Categoria(ModeloSaaS):
    TIPO_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        ordering = ['nome']


class Lancamento(ModeloSaaS):
    TIPO_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago / Recebido'),
        ('CANCELADO', 'Cancelado'),
    ]

    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    
    # Relacionamentos
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Categoria")
    cadastro = models.ForeignKey(Cadastro, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cliente/Fornecedor")
    
    # Valores e Datas
    valor_previsto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Original")
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor Pago/Recebido")
    
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data do Pagamento/Baixa")
    
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, verbose_name="Tipo")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor_previsto}"

    class Meta:
        verbose_name = "Lançamento"
        verbose_name_plural = "Lançamentos"
        ordering = ['data_vencimento']