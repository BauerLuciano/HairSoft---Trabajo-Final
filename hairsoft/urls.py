from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
import os

def serve_frontend(request, path=''):
    frontend_path = os.path.join(settings.BASE_DIR, 'hairsoft-frontend', 'index.html')
    if os.path.exists(frontend_path):
        return serve(request, 'index.html', os.path.dirname(frontend_path))
    else:
        return serve(request, path, document_root=settings.STATIC_ROOT)

urlpatterns = [
    # 1. El Admin se queda ACÁ, es su único lugar.
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 3. Frontend (Siempre al final)
urlpatterns += [
    re_path(r'^.*$', serve_frontend),
]