# usuarios/urls.py

from django.urls import path
from . import views # 🛑 CORRECCIÓN: 'vie' cambiado a 'views'

urlpatterns = [

    # ==============================
    # Autenticación y Perfil
    # ==============================
    # NUEVA RUTA DE LOGIN (CRÍTICA)
    path('api/auth/login/', views.login_auth, name='api_login'), 
    
    # Perfil del usuario logueado (CRÍTICA para Vue)
    path('api/me/', views.me_api_view, name='me_api_view'), 
    
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
    path('api/clientes/', views.ClienteAutocomplete, name='cliente-autocomplete'),

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

    # ================================
    # Turnos
    # ================================
    path('api/turnos/', views.listado_turnos, name='listado_turnos'),
    path('api/turnos/crear/', views.crear_turno, name='crear_turno'),
    path('api/turnos/<int:turno_id>/cancelar/', views.cancelar_turno, name='cancelar_turno'),
    path('api/turnos/<int:turno_id>/completar/', views.completar_turno, name='completar_turno'),
    path('api/turnos/<int:turno_id>/modificar/', views.modificar_turno, name='modificar_turno'),
    path('api/turnos/verificar-disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),

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

    # ==============================
    # Permisos
    # ==============================
    path('api/permisos/', views.listado_permisos, name='listado_permisos'),

    # ==============================
    # API MERCADOPAGO
    # ==============================
    path('api/mercadopago/crear-preferencia-sena/', views.crear_preferencia_pago_seña, name='crear_preferencia_pago_seña'),
    
    # ✅ URLs para Mercado Pago - VISTAS REALES
    path('api/mercadopago/pago-exitoso/', views.pago_exitoso, name='mp_pago_exitoso'),
    path('api/mercadopago/pago-error/', views.pago_error, name='mp_pago_error'),
    path('api/mercadopago/pago-pendiente/', views.pago_pendiente, name='mp_pago_pendiente'),

    # ================================
    # Proveedores
    # ================================
    path('api/proveedores/', views.ProveedorListCreateView.as_view(), name='proveedores-list'),
    path('api/proveedores/<int:pk>/', views.ProveedorRetrieveUpdateDestroyView.as_view(), name='proveedores-detail'),
]