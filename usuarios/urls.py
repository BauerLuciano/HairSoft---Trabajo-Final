# usuarios/urls.py
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

    # ================================
    # Clientes Autocomplete
    # ================================
    path('api/clientes/', views.ClienteAutocomplete.as_view(), name='cliente-autocomplete'),

    # ================================
    # Peluqueros
    # ================================
    path('api/peluqueros/', views.listado_peluqueros, name='listado_peluqueros'),

    # ================================
    # Servicios
    # ================================
    path('api/categorias/servicios/', views.listado_categorias_servicios, name='listado_categorias_servicios'),
    path('api/servicios/', views.listado_servicios, name='listado_servicios'),
    path('api/servicios/crear/', views.crear_servicio, name='crear_servicio'),
    path('api/servicios/editar/<int:pk>/', views.editar_servicio, name='editar_servicio'),
    path('api/servicios/eliminar/<int:pk>/', views.eliminar_servicio, name='eliminar_servicio'),

    # ================================
    # Productos
    # ================================
    path('api/categorias/productos/', views.listado_categorias_productos, name='listado_categorias_productos'),
    path('api/productos/', views.listado_productos, name='listado_productos'),
    # Estas vistas aún no están implementadas en views.py
    # path('api/productos/crear/', views.crear_producto, name='crear_producto'),
    # path('api/productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    # path('api/productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # ================================
    # Turnos
    # ================================
    path('api/turnos/', views.listado_turnos, name='listado_turnos'),  # para obtener turnos
    path('api/turnos/crear/', views.crear_turno, name='crear_turno'),
    # Estas vistas aún no están implementadas en views.py
    # path('api/turnos/editar/<int:pk>/', views.editar_turno, name='editar_turno'),
    # path('api/turnos/eliminar/<int:pk>/', views.eliminar_turno, name='eliminar_turno'),

# ================================
# Categorías Servicios
# ================================
path('api/categorias/servicios/crear/', views.crear_categoria_servicio, name='crear_categoria_servicio'),
path('api/categorias/servicios/editar/<int:pk>/', views.editar_categoria_servicio, name='editar_categoria_servicio'),
path('api/categorias/servicios/eliminar/<int:pk>/', views.eliminar_categoria_servicio, name='eliminar_categoria_servicio'),

# ================================
# Categorías Productos
# ================================
path('api/categorias/productos/crear/', views.crear_categoria_producto, name='crear_categoria_producto'),
path('api/categorias/productos/editar/<int:pk>/', views.editar_categoria_producto, name='editar_categoria_producto'),
path('api/categorias/productos/eliminar/<int:pk>/', views.eliminar_categoria_producto, name='eliminar_categoria_producto'),

# ==============================
# Rutas para Roles
# ==============================
path('api/roles/', views.listado_roles, name='listado_roles'),
path('api/roles/crear/', views.crear_rol, name='crear_rol'),
path('api/roles/editar/<int:pk>/', views.editar_rol, name='editar_rol'),
path('api/roles/eliminar/<int:pk>/', views.eliminar_rol, name='eliminar_rol'),


]
