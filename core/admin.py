from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empresa, Usuario, ParametroSistema

# 3. Configuração para gerenciar Parâmetros do Sistema
@admin.register(ParametroSistema)
class ParametroSistemaAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'empresa')
    list_filter = ('empresa', 'chave')
    search_fields = ('chave', 'valor')

# 1. Configuração para gerenciar Empresas
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'ativo', 'created_at')
    search_fields = ('nome', 'cnpj')
    list_filter = ('ativo',)

# 2. Configuração para gerenciar Usuários
# Precisamos customizar para mostrar o campo 'empresa' dentro do cadastro do usuário
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Colunas que aparecem na lista de usuários
    list_display = ('username', 'email', 'first_name', 'empresa', 'is_staff')
    
    # Filtros laterais
    list_filter = ('empresa', 'is_staff', 'is_superuser')

    # Adiciona o campo 'empresa' no formulário de edição do usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Informações SaaS', {'fields': ('empresa', 'cargo')}),
    )
    
    # Adiciona o campo 'empresa' também na tela de criar usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações SaaS', {'fields': ('empresa', 'email')}),
    )