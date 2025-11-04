# usuarios/urls.py

from django.urls import path

# ✅ 1. Importación para funciones: Renombrar 'views' a 'func_views'
from . import views as func_views 

# ✅ 2. Importación para CLASES: Importar todas las clases que usan .as_view()
from .views import (
    VentaViewSet, 
    ProductoListCreateAPIView, 
    ProveedorListCreateView, 
    ProveedorRetrieveUpdateDestroyView,
    CategoriaProductoListAPIView,
    MetodoPagoListAPIView,
    generar_comprobante_pdf,
    PedidoListCreateAPIView, 
    PedidoRetrieveUpdateDestroyAPIView,
    buscar_pedidos,
    cancelar_pedido,
    recibir_pedido,
    pedidos_pendientes_recepcion,
    pedidos_para_cancelar,
    datos_crear_pedido,
    debug_crear_pedido,
)


# ================================
# Configuración de ViewSet para Ventas
# ================================
venta_list = VentaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

venta_detail = VentaViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    # ==============================
    # Autenticación y Perfil (USAN FUNCIONES)
    # ==============================
    path('api/auth/login/', func_views.login_auth, name='api_login'), 
    path('api/me/', func_views.me_api_view, name='me_api_view'), 
    path('api/usuario_actual/', func_views.me_api_view, name='usuario_actual'),
    path('usuarios/api/me/', func_views.me_api_view, name='me_api_view_alias'),

    # ================================
    # Usuarios (USAN FUNCIONES)
    # ================================
    path('api/usuarios/', func_views.listado_usuarios, name='listado_usuarios'),
    path('api/usuarios/crear/', func_views.crear_usuario, name='crear_usuario'),
    path('api/usuarios/editar/<int:pk>/', func_views.editar_usuario, name='editar_usuario'),
    path('api/usuarios/eliminar/<int:pk>/', func_views.eliminar_usuario, name='eliminar_usuario'),

    # ================================
    # Clientes Autocomplete (USA FUNCIÓN)
    # ================================
    path('api/clientes/', func_views.ClienteAutocomplete, name='cliente-autocomplete'),

    # ================================
    # Peluqueros (USA FUNCIÓN)
    # ================================
    path('api/peluqueros/', func_views.listado_peluqueros, name='listado_peluqueros'),

    # ================================
    # Servicios (USAN FUNCIONES)
    # ================================
    path('api/categorias/servicios/', func_views.listado_categorias_servicios, name='listado_categorias_servicios'),
    path('api/servicios/', func_views.listado_servicios, name='listado_servicios'),
    path('api/servicios/crear/', func_views.crear_servicio, name='crear_servicio'),
    path('api/servicios/editar/<int:pk>/', func_views.editar_servicio, name='editar_servicio'),
    path('api/servicios/eliminar/<int:pk>/', func_views.eliminar_servicio, name='eliminar_servicio'),

    # ================================
    # Productos (CLASE Y FUNCIÓN)
    # ================================
    path('api/categorias/productos/', CategoriaProductoListAPIView.as_view(), name='listado_categorias_productos'), 
    path('api/productos/', ProductoListCreateAPIView.as_view(), name='productos_api'),
    
    # ✅ NUEVA RUTA: MÉTODOS DE PAGO
    path('api/metodos-pago/', MetodoPagoListAPIView.as_view(), name='listado_metodos_pago'),

    # ================================
    # Turnos (USAN FUNCIONES)
    # ================================
    path('api/turnos/', func_views.listado_turnos, name='listado_turnos'),
    path('api/turnos/crear/', func_views.crear_turno, name='crear_turno'),
    path('api/turnos/<int:turno_id>/cancelar/', func_views.cancelar_turno, name='cancelar_turno'),
    path('api/turnos/<int:turno_id>/completar/', func_views.completar_turno, name='completar_turno'),
    path('api/turnos/<int:turno_id>/modificar/', func_views.modificar_turno, name='modificar_turno'),
    path('api/turnos/verificar-disponibilidad/', func_views.verificar_disponibilidad, name='verificar_disponibilidad'),

    # ================================
    # Categorías Servicios (USAN FUNCIONES)
    # ================================
    path('api/categorias/servicios/crear/', func_views.crear_categoria_servicio, name='crear_categoria_servicio'),
    path('api/categorias/servicios/editar/<int:pk>/', func_views.editar_categoria_servicio, name='editar_categoria_servicio'),
    path('api/categorias/servicios/eliminar/<int:pk>/', func_views.eliminar_categoria_servicio, name='eliminar_categoria_servicio'),

    # ================================
    # Categorías Productos (USAN FUNCIONES)
    # ================================
    path('api/categorias/productos/crear/', func_views.crear_categoria_producto, name='crear_categoria_producto'),
    path('api/categorias/productos/editar/<int:pk>/', func_views.editar_categoria_producto, name='editar_categoria_producto'),
    path('api/categorias/productos/eliminar/<int:pk>/', func_views.eliminar_categoria_producto, name='eliminar_categoria_producto'),

    # ==============================
    # Roles y Permisos (USAN FUNCIONES)
    # ==============================
    path('api/roles/', func_views.listado_roles, name='listado_roles'),
    path('api/roles/crear/', func_views.crear_rol, name='crear_rol'),
    path('api/roles/editar/<int:pk>/', func_views.editar_rol, name='editar_rol'),
    path('api/roles/eliminar/<int:pk>/', func_views.eliminar_rol, name='eliminar_rol'),
    path('api/permisos/', func_views.listado_permisos, name='listado_permisos'),

    # ==============================
    # API MERCADOPAGO (USAN FUNCIONES)
    # ==============================
    path('api/mercadopago/crear-preferencia-sena/', func_views.crear_preferencia_pago_seña, name='crear_preferencia_pago_seña'),
    path('api/mercadopago/pago-exitoso/', func_views.pago_exitoso, name='mp_pago_exitoso'),
    path('api/mercadopago/pago-error/', func_views.pago_error, name='mp_pago_error'),
    path('api/mercadopago/pago-pendiente/', func_views.pago_pendiente, name='mp_pago_pendiente'),

    # ================================
    # Proveedores (CLASES)
    # ================================
    path('api/proveedores/', ProveedorListCreateView.as_view(), name='proveedores-list'),
    path('api/proveedores/<int:pk>/', ProveedorRetrieveUpdateDestroyView.as_view(), name='proveedores-detail'),

    # ================================
    # Para ver el usuario logueado (USA FUNCIÓN)
    # ================================
    path('api/usuarios/<int:user_id>/', func_views.obtener_usuario_por_id, name='obtener_usuario_por_id'),

    # ================================
    # VENTAS (USA VentaViewSet Y FUNCIONES PARA MODIFICAR)
    # ================================
    path('api/ventas/', venta_list, name='ventas-list'), 
    path('api/ventas/<int:pk>/', venta_detail, name='ventas-detail'),

    # ✅ RUTAS CORREGIDAS - SIN DUPLICADOS
    path('api/ventas/<int:venta_id>/editar/', func_views.obtener_venta_para_edicion, name='venta-detalle'),
    path('api/ventas/<int:venta_id>/actualizar/', func_views.actualizar_venta, name='venta-actualizar'),
    
    # ✅ SOLO UNA RUTA PARA ANULAR
    path('api/ventas/<int:venta_id>/anular/', func_views.anular_venta, name='anular_venta'),

    #-----
    path('api/debug-ventas/', func_views.debug_ventas, name='debug_ventas'),

    #----PDF
    path('api/ventas/<int:venta_id>/comprobante-pdf/', generar_comprobante_pdf, name='generar_comprobante_pdf'),


    # ================================
    # PEDIDOS - Nuevas rutas
    # ================================
    path('api/pedidos/', PedidoListCreateAPIView.as_view(), name='pedidos-list-create'),
    path('api/pedidos/<int:pk>/', PedidoRetrieveUpdateDestroyAPIView.as_view(), name='pedidos-detail'),
    
    # Búsqueda y Filtros
    path('api/pedidos/buscar/', buscar_pedidos, name='buscar-pedidos'),
    
    # Operaciones de Estado
    path('api/pedidos/<int:pedido_id>/cancelar/', cancelar_pedido, name='cancelar-pedido'),
    path('api/pedidos/<int:pedido_id>/recibir/', recibir_pedido, name='recibir-pedido'),
    
    # Listados Especializados
    path('api/pedidos/pendientes-recepcion/', pedidos_pendientes_recepcion, name='pedidos-pendientes-recepcion'),
    path('api/pedidos/para-cancelar/', pedidos_para_cancelar, name='pedidos-para-cancelar'),
    
    # Datos para formularios
    path('api/pedidos/datos-crear/', datos_crear_pedido, name='datos-crear-pedido'),

    path('api/pedidos/debug/', debug_crear_pedido, name='debug_crear_pedido'),

]