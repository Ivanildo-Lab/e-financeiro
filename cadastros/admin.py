from django.contrib import admin

from django.contrib import admin
from .models import Cadastro

@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    # Colunas que aparecem na lista
    list_display = ('num_registro', 'nome', 'cpf', 'situacao', 'cidade', 'empresa')
    
    # Filtros laterais
    list_filter = ('situacao', 'estado', 'empresa')
    
    # Campo de busca
    search_fields = ('nome', 'cpf', 'num_registro', 'email')
    
    # Organização do formulário no admin (agrupando campos)
    fieldsets = (
        ('Vínculo', {
            'fields': ('empresa', 'num_registro', 'num_contrato', 'situacao', 'data_admissao')
        }),
        ('Dados Pessoais', {
            'fields': ('nome', 'apelido', 'cpf', 'rg', 'data_nascimento', 'estado_civil', 'nacionalidade', 'naturalidade', 'profissao')
        }),
        ('Filiação', {
            'fields': ('nome_pai', 'nome_mae')
        }),
        ('Contato', {
            'fields': ('email', 'celular', 'tel_residencial', 'tel_trabalho')
        }),
        ('Endereço', {
            'fields': ('cep', 'endereco', 'bairro', 'cidade', 'estado')
        }),
        ('Outros', {
            'fields': ('foto', 'observacoes')
        }),
    )