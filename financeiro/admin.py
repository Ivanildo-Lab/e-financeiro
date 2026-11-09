from django.contrib import admin
from .models import PlanoDeContas, Caixa, Conta, Lancamento


@admin.register(PlanoDeContas)
class PlanoDeContasAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'codigo', 'nome', 'tipo', 'aceita_lancamentos']
    list_filter = ['tipo', 'aceita_lancamentos', 'empresa']
    search_fields = ['codigo', 'nome', 'empresa__nome']
    list_editable = ['aceita_lancamentos']
    ordering = ['empresa', 'codigo', 'nome']


@admin.register(Caixa)
class CaixaAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'nome', 'saldo_inicial']
    list_filter = ['empresa']
    search_fields = ['nome', 'empresa__nome']


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'descricao', 'plano_de_contas', 'valor',
                    'data_vencimento', 'status', 'documento']
    list_filter = ['status', 'plano_de_contas__tipo', 'empresa']
    search_fields = ['descricao', 'documento', 'plano_de_contas__nome', 'empresa__nome']
    date_hierarchy = 'data_vencimento'
    raw_id_fields = ['cadastro']


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'data_lancamento', 'descricao', 'valor',
                    'tipo', 'caixa', 'plano_de_contas']
    list_filter = ['tipo', 'caixa', 'plano_de_contas__tipo', 'empresa']
    search_fields = ['descricao', 'caixa__nome', 'plano_de_contas__nome', 'empresa__nome']
    date_hierarchy = 'data_lancamento'
