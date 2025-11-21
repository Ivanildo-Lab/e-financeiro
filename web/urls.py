from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # Raiz do site
    path('dashboard/', views.dashboard, name='dashboard'),
]