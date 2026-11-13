from django.urls import path
from . import views

urlpatterns = [
    # --- CLIENTES (Sócios/Alunos) ---
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/novo/', views.novo_cliente, name='novo_cliente'),

    # --- FORNECEDORES ---
    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/novo/', views.novo_fornecedor, name='novo_fornecedor'),

    # --- GERAL ---
    # A edição é a mesma para os dois, pois a view sabe redirecionar de volta
    path('editar/<int:id>/', views.editar_cadastro, name='editar_cadastro'),
    path('excluir/<int:id>/', views.excluir_cadastro, name='excluir_cadastro'),
    path('ficha/<int:id>/', views.imprimir_ficha, name='imprimir_ficha'),
    
    # Rota padrão: se acessar /cadastros/, vai para clientes
    path('', views.lista_clientes, name='lista_cadastros_padrao'),

    # --- EVENTOS / VENCIMENTOS ---
    path('eventos/adicionar/<int:id>/', views.adicionar_evento, name='adicionar_evento'),
    path('eventos/editar/<int:id>/', views.editar_evento, name='editar_evento'),
    path('eventos/excluir/<int:id>/', views.excluir_evento, name='excluir_evento'),
]