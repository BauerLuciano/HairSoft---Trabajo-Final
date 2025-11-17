from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.views.static import serve
from django.conf import settings
from django.shortcuts import redirect
import os

urlpatterns = [
    # Redirige raíz al listado de usuarios
    path('', lambda request: redirect('/usuarios/', permanent=False)),

    # Incluye todas las rutas de la app usuarios
    path('usuarios/', include('usuarios.urls')),

    # Admin
    path('admin/', admin.site.urls),
]

# Sirve el index.html del frontend cuando entrás a /usuarios/ o refrescás
frontend_index = os.path.join(settings.BASE_DIR, 'hairsoft-frontend', 'index.html')

if os.path.exists(frontend_index):
    urlpatterns += [
        re_path(r'^usuarios/?$', serve, {'path': 'index.html', 'document_root': os.path.join(settings.BASE_DIR, 'hairsoft-frontend')}),
    ]
