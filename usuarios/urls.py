from django.urls import path
from . import views

urlpatterns = [
    # ================================
    # Usuarios
    # ================================
    path('api/usuarios/', views.listado_usuarios, name='listado_usuarios'),
    path('api/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('api/usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('api/usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
]

    # ================================
    # Turnos (placeholders)
    # ================================
    #path('turnos/', views.listado_turnos, name='listado_turnos'),
    #path('turnos/nuevo/', views.crear_turno, name='registrar_turno'),
    #path('turnos/editar/<int:pk>/', views.editar_turno, name='editar_turno'),
    #path('turnos/eliminar/<int:pk>/', views.eliminar_turno, name='eliminar_turno'),
    #path('turnos/cliente-autocomplete/', views.ClienteAutocomplete.as_view(), name='cliente-autocomplete'),

