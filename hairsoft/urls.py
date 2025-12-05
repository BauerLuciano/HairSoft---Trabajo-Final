from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
import os

# Función para servir el frontend
def serve_frontend(request, path=''):
    frontend_path = os.path.join(settings.BASE_DIR, 'hairsoft-frontend', 'index.html')
    if os.path.exists(frontend_path):
        return serve(request, 'index.html', os.path.dirname(frontend_path))
    else:
        return serve(request, path, document_root=settings.STATIC_ROOT)

urlpatterns = [
    # 1. Admin
    path('admin/', admin.site.urls),

    # 2. LA CLAVE: Conectar tu archivo usuarios/urls.py bajo el prefijo 'usuarios/'
    # Esto hace que funcionen las rutas tipo: /usuarios/api/turnos/
    path('usuarios/', include('usuarios.urls')),

    # 3. Soporte extra por si alguna ruta llama directo a /api/
    path('', include('usuarios.urls')),

    # 4. Archivos estáticos y media
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 5. Todo lo demás -> Frontend (Vue)
urlpatterns += [
    re_path(r'^.*$', serve_frontend),
]