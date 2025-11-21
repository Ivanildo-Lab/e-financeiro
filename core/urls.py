from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas dos Apps
    path('cadastros/', include('cadastros.urls')),
    
    # O App WEB assume a raiz do site (deixe por último ou explicitamente na raiz)
    path('', include('web.urls')),
]

# Configuração para servir Imagens (Banners/Logos) em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)