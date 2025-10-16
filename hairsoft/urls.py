"""
URL configuration for hairsoft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Importar vistas desde la app usuarios
from usuarios import views as usuarios_views

urlpatterns = [
    path('', lambda request: redirect('/usuarios/api/usuarios/')),  # raíz redirige al listado de usuarios
    path('usuarios/', include('usuarios.urls')),
    path('admin/', admin.site.urls),

    # URLs de turnos
    #path('turnos/', usuarios_views.listado_turnos, name='listado_turnos'),
    #path('turnos/nuevo/', usuarios_views.crear_turno, name='crear_turno'),
    #path('turnos/editar/<int:pk>/', usuarios_views.editar_turno, name='editar_turno'),
    #path('turnos/eliminar/<int:pk>/', usuarios_views.eliminar_turno, name='eliminar_turno'),
]
