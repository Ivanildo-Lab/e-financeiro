from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cadastros, name='lista_cadastros'),
    path('novo/', views.novo_cadastro, name='novo_cadastro'),
    path('editar/<int:id>/', views.editar_cadastro, name='editar_cadastro'),
]