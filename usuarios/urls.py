# usuarios/urls.py
from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Usuarios
    path('', views.listado_usuarios, name='listado_usuarios'),
    path('nuevo/', views.crear_usuario, name='crear_usuario'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # Turnos
    path('turnos/', views.listado_turnos, name='listado_turnos'),
    path('turnos/nuevo/', views.crear_turno, name='registrar_turno'),
    path('turnos/editar/<int:pk>/', views.editar_turno, name='editar_turno'),
    path('turnos/eliminar/<int:pk>/', views.eliminar_turno, name='eliminar_turno'),
    path('turnos/cliente-autocomplete/', views.ClienteAutocomplete.as_view(), name='cliente-autocomplete'),

    # API
    path('api/servicios/', api_views.ServicioListAPIView.as_view(), name='api-servicios'),
    path('api/turnos/', api_views.TurnoListAPIView.as_view(), name='api-turnos'),
    path('api/peluqueros/', api_views.PeluqueroListAPIView.as_view(), name='api-peluqueros'),
    path('api/clientes/', api_views.ClienteListAPIView.as_view(), name='api-clientes'),
]
