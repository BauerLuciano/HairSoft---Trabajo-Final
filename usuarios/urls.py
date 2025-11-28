from django.urls import path
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter

# ✅ 1. Importación para funciones: Renombrar 'views' a 'func_views'
from . import views as func_views 

# ✅ 2. Importación para CLASES: Importar todas las clases que usan .as_view()
from .views import (
    VentaViewSet, 
    ProductoListCreateAPIView, 
    ProductoRetrieveUpdateDestroyAPIView,
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
    ListaPrecioProveedorViewSet,
    HistorialPreciosViewSet,
    turnos_ocupados,
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
    path('api/productos/<int:pk>/', ProductoRetrieveUpdateDestroyAPIView.as_view(), name='productos-detail'),
    
    # ✅ MÉTODOS DE PAGO
    path('api/metodos-pago/', MetodoPagoListAPIView.as_view(), name='listado_metodos_pago'),

    # ================================
    # Turnos (USAN FUNCIONES)
    # ================================
    path('api/turnos/', func_views.listado_turnos, name='listado_turnos'),
    path('api/turnos/crear/', func_views.crear_turno, name='crear_turno'),
    path('api/turnos/<int:turno_id>/completar/', func_views.completar_turno, name='completar_turno'),
    path('api/turnos/<int:turno_id>/modificar/', func_views.modificar_turno, name='modificar_turno'),
    path('api/turnos/<int:turno_id>/procesar-sena/', func_views.procesar_sena_turno, name='procesar_sena_turno'),
    path('api/turnos/verificar-disponibilidad/', func_views.verificar_disponibilidad, name='verificar_disponibilidad'),
    path('api/turnos/cancelar-propio/<int:turno_id>/', func_views.cancelar_mi_turno, name='cancelar_mi_turno'),

    # ================================
    # ✅✅✅ RUTA CRÍTICA FALTANTE - REGISTRAR INTERÉS
    # ================================
    path('api/turnos/registrar-interes/', func_views.registrar_interes_turno, name='registrar_interes_turno'),

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
    path('api/ventas/registrar/', func_views.registrar_venta, name='registrar_venta_custom'),
    path('api/ventas/', venta_list, name='ventas-list'), 
    path('api/ventas/<int:pk>/', venta_detail, name='ventas-detail'),
    path('api/ventas/<int:venta_id>/editar/', func_views.obtener_venta_para_edicion, name='venta-detalle'),
    path('api/ventas/<int:venta_id>/actualizar/', func_views.actualizar_venta, name='venta-actualizar'),
    path('api/ventas/<int:venta_id>/anular/', func_views.anular_venta, name='anular_venta'),
    path('api/debug-ventas/', func_views.debug_ventas, name='debug_ventas'),
    path('api/ventas/<int:venta_id>/comprobante-pdf/', generar_comprobante_pdf, name='generar_comprobante_pdf'),

    # ================================
    # PEDIDOS
    # ================================
    path('api/pedidos/', PedidoListCreateAPIView.as_view(), name='pedidos-list-create'),
    path('api/pedidos/<int:pk>/', PedidoRetrieveUpdateDestroyAPIView.as_view(), name='pedidos-detail'),
    path('api/pedidos/buscar/', buscar_pedidos, name='buscar-pedidos'),
    path('api/pedidos/<int:pedido_id>/cancelar/', cancelar_pedido, name='cancelar-pedido'),
    path('api/pedidos/<int:pedido_id>/recibir/', recibir_pedido, name='recibir-pedido'),
    path('api/pedidos/pendientes-recepcion/', pedidos_pendientes_recepcion, name='pedidos-pendientes-recepcion'),
    path('api/pedidos/para-cancelar/', pedidos_para_cancelar, name='pedidos-para-cancelar'),
    path('api/pedidos/datos-crear/', datos_crear_pedido, name='datos-crear-pedido'),
    path('api/pedidos/debug/', debug_crear_pedido, name='debug_crear_pedido'),

    # Propuesta y confirmación de precios
    path('api/pedidos/<int:pedido_id>/proponer-precios/', func_views.proponer_precios, name='proponer-precios'),
    path('api/pedidos/<int:pedido_id>/confirmar-precios/', func_views.confirmar_precios, name='confirmar-precios'),

    # ================================
    # LISTAS DE PRECIOS DE PROVEEDORES
    # ================================
    path('api/listas-precios/', ListaPrecioProveedorViewSet.as_view({
        'get': 'list', 
        'post': 'create'
    }), name='listas-precios-list'),
    
    path('api/listas-precios/<int:pk>/', ListaPrecioProveedorViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='listas-precios-detail'),
    
    path('api/listas-precios/por-proveedor/', func_views.listas_por_proveedor, name='listas-por-proveedor'),
    path('api/listas-precios/<int:pk>/desactivar/', func_views.desactivar_lista_precio, name='desactivar-lista-precio'),
    path('api/listas-precios/actualizar-masivo/', func_views.actualizar_listas_masivo, name='actualizar-listas-masivo'),
    
    # Historial de Precios
    path('api/historial-precios/', HistorialPreciosViewSet.as_view({
        'get': 'list'
    }), name='historial-precios-list'),
    
    path('api/historial-precios/<int:pk>/', HistorialPreciosViewSet.as_view({
        'get': 'retrieve'
    }), name='historial-precios-detail'),
    
    # Cálculo de precios
    path('api/calcular-precios-pedido/', func_views.calcular_precios_pedido, name='calcular-precios-pedido'),
    path('api/calcular-precio-sugerido/', func_views.calcular_precio_sugerido, name='calcular-precio-sugerido'),

    path('api/turnos/<int:turno_id>/procesar-sena/', func_views.procesar_sena_turno, name='procesar_sena_turno'),
    path('api/turnos/<int:turno_id>/completar-pago/', func_views.completar_pago_turno, name='completar_pago_turno'),

    # ================================
    # REOFERTA MASIVA - ✅ RUTAS CORREGIDAS
    # ================================
    path('api/turnos/<int:turno_id>/cancelar-con-reoferta/', func_views.cancelar_turno_con_reoferta, name='cancelar_turno_con_reoferta'),
    path('api/turnos/<int:turno_id>/aceptar-oferta/<str:token>/', func_views.aceptar_oferta_turno, name='aceptar_oferta_turno'),
    path('api/turnos/mis-intereses/', func_views.listar_intereses_usuario, name='listar_intereses_usuario'),
    path('api/turnos/eliminar-interes/<int:interes_id>/', func_views.eliminar_interes_turno, name='eliminar_interes_turno'),

    # ================================
    # REOFERTA AUTOMÁTICA
    # ================================
    path('api/reoferta/configuracion/', func_views.obtener_configuracion_reoferta, name='configuracion-reoferta'),
    path('api/reoferta/configuracion/actualizar/', func_views.actualizar_configuracion_reoferta, name='actualizar-configuracion-reoferta'),
    path('api/reoferta/estadisticas/', func_views.estadisticas_reoferta, name='estadisticas-reoferta'),
    path('api/reoferta/forzar/<int:turno_id>/', func_views.forzar_reoferta, name='forzar-reoferta'),
    path('api/intereses-turnos/cliente/<int:cliente_id>/', func_views.listar_intereses_cliente, name='listar-intereses-cliente'),
    path('api/reoferta/respuesta/<int:interes_id>/', func_views.procesar_respuesta_oferta, name='procesar-respuesta-oferta'),
    path('api/turnos/<int:turno_id>/oferta-info/<str:token>/', func_views.obtener_info_oferta, name='oferta_info'),
    
    # ================================
    # OTRAS RUTAS
    # ================================
    path('turnos/api/ocupados/', turnos_ocupados, name='turnos_ocupados'),
    path('api/dashboard/', func_views.dashboard_data, name='dashboard_data'),
    path('api/marcas/', func_views.listar_marcas, name='listar_marcas'),
    path('api/marcas/crear/', func_views.crear_marca, name='crear_marca'),
]