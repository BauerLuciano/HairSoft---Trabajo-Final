from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
import os

SERVE_FRONTEND = os.environ.get('SERVE_FRONTEND', 'True' if settings.DEBUG else 'False').lower() in ('true', '1', 'yes')

def serve_frontend(request, path=''):
    frontend_path = os.path.join(settings.BASE_DIR, 'hairsoft-frontend', 'index.html')
    if os.path.exists(frontend_path):
        return serve(request, 'index.html', os.path.dirname(frontend_path))
    return serve(request, path, document_root=settings.STATIC_ROOT)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),

]

if settings.DEBUG and not os.environ.get('CLOUDINARY_CLOUD_NAME'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if SERVE_FRONTEND:
    urlpatterns += [
        re_path(r'^.*$', serve_frontend),
    ]