from django.urls import path
from . import views

urlpatterns = [
    path('listado/', views.listado_usuarios, name='listado_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
]
