from django.urls import path
from django.contrib.auth import views as auth_views # <--- ESSA LINHA É OBRIGATÓRIA
from . import views
from .forms import CustomLoginForm

urlpatterns = [
    # Landing Page e Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- SISTEMA DE LOGIN PERSONALIZADO ---
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=CustomLoginForm,
        redirect_authenticated_user=True
    ), name='login'),
    
    # Rota de Logout (Redireciona para o login após sair)
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]