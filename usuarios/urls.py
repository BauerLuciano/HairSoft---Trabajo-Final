from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importamos tus vistas basadas en funciones (donde escribimos el código nuevo)
from . import views as func_views

# Importamos las vistas basadas en clases (para lo que no hemos tocado)
from .api_views import (
    AuditoriaViewSet,
    PedidoWebViewSet,
    # ServicioListAPIView,  <-- YA NO USAMOS ESTAS PARA SERVICIOS
    # ServicioCreateAPIView, <-- YA NO USAMOS ESTAS PARA SERVICIOS
    # ServicioUpdateAPIView, <-- YA NO USAMOS ESTAS PARA SERVICIOS
    # ServicioToggleEstadoView, <-- YA NO USAMOS ESTAS PARA SERVICIOS
    ProductoCatalogoView,
    ReporteLiquidacionView,
    ReporteLiquidacionPDFView,
    RegistrarPagoLiquidacionView,
    HistorialLiquidacionesView
)

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
    enviar_pedido_proveedor,
    pedidos_pendientes_recepcion,
    pedidos_para_cancelar,
    datos_crear_pedido,
    debug_crear_pedido,
    ListaPrecioProveedorViewSet,
    HistorialPreciosViewSet,
    turnos_ocupados,
    gestionar_cotizacion_externa,
    SolicitudPresupuestoViewSet,
    contar_interesados,
    validar_cupon
)

# ================================
# ✅ Router
# ================================
router = DefaultRouter()
router.register(r'auditoria', AuditoriaViewSet, basename='auditoria')
router.register(r'web/pedidos', PedidoWebViewSet, basename='pedidos-web')

venta_list = VentaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

venta_detail = VentaViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    # ==============================
    # ✅ ÚNICA INCLUSIÓN DEL ROUTER
    # ==============================
    path('api/', include(router.urls)),

    path('api/debug/auditoria/', func_views.debug_auditoria, name='debug_auditoria'),

    # ==============================
    # Autenticación y Perfil
    # ==============================
    path('api/auth/login/', func_views.login_auth, name='api_login'),
    path('api/auth/logout/', func_views.logout_view, name='api_logout'),
    path('api/me/', func_views.me_api_view, name='me_api_view'),
    path('api/usuario_actual/', func_views.me_api_view, name='usuario_actual'),
    path('usuarios/api/me/', func_views.me_api_view, name='me_api_view_alias'),

    # ================================
    # Marcas
    # ================================
    path('api/marcas/', func_views.listar_marcas, name='listar_marcas'),
    path('api/marcas/crear/', func_views.crear_marca, name='crear_marca'),
    path('api/marcas/<int:pk>/cambiar_estado/', func_views.cambiar_estado_marca, name='cambiar_estado_marca'),
    path('api/marcas/<int:pk>/', func_views.actualizar_marca, name='actualizar_marca'),
    path('api/marcas/<int:pk>/eliminar/', func_views.eliminar_marca, name='eliminar_marca'),

    # ================================
    # Usuarios
    # ================================
    path('api/usuarios/', func_views.listado_usuarios, name='listado_usuarios'),
    path('api/usuarios/crear/', func_views.crear_usuario, name='crear_usuario'),
    path('api/usuarios/editar/<int:pk>/', func_views.editar_usuario, name='editar_usuario'),
    path('api/usuarios/eliminar/<int:pk>/', func_views.eliminar_usuario, name='eliminar_usuario'),
    path('api/usuarios/activar/<int:pk>/', func_views.activar_usuario, name='activar_usuario'),

    # ================================
    # Clientes / Peluqueros
    # ================================
    path('api/clientes/', func_views.ClienteAutocomplete, name='cliente-autocomplete'),
    path('api/peluqueros/', func_views.listado_peluqueros, name='listado_peluqueros'),

    # ================================
    # ✂️ SERVICIOS (✅ CORREGIDO - AHORA USA func_views)
    # ================================
    # 1. Listado de Categorías (Para el select)
    path('api/categorias/servicios/', func_views.listado_categorias_servicios, name='listado_categorias_servicios'),
    
    # 2. Servicios CRUD (Usamos tus funciones def, NO las clases viejas)
    path('api/servicios/', func_views.listado_servicios, name='listado_servicios'),
    path('api/servicios/crear/', func_views.crear_servicio, name='crear_servicio'),
    path('api/servicios/editar/<int:pk>/', func_views.editar_servicio, name='editar_servicio'),
    path('api/servicios/<int:pk>/', func_views.obtener_servicio, name='obtener_servicio'),
    path('api/servicios/<int:pk>/cambiar-estado/', func_views.cambiar_estado_servicio, name='cambiar_estado_servicio'),

    # 3. Categorías CRUD
    path('api/categorias/servicios/crear/', func_views.crear_categoria_servicio, name='crear_categoria_servicio'),
    path('api/categorias/servicios/editar/<int:pk>/', func_views.editar_categoria_servicio, name='editar_categoria_servicio'),
    path('api/categorias/servicios/eliminar/<int:pk>/', func_views.eliminar_categoria_servicio, name='eliminar_categoria_servicio'),

    # ================================
    # Productos
    # ================================
    path('api/categorias/productos/', CategoriaProductoListAPIView.as_view(), name='listado_categorias_productos'),
    path('api/productos/', ProductoListCreateAPIView.as_view(), name='productos_api'),
    path('api/productos/<int:pk>/', ProductoRetrieveUpdateDestroyAPIView.as_view(), name='productos-detail'),
    path('api/metodos-pago/', MetodoPagoListAPIView.as_view(), name='listado_metodos_pago'),
    path('api/catalogo/', ProductoCatalogoView.as_view(), name='catalogo-publico'),

    # ================================
    # 📅 TURNOS
    # ================================
    path('api/turnos/', func_views.listar_turnos_general, name='listado_turnos'),
    path('api/turnos/crear/', func_views.crear_turno, name='crear_turno'),
    path('api/turnos/<int:turno_id>/modificar/', func_views.modificar_turno, name='modificar_turno'),
    path('api/turnos/<int:turno_id>/', func_views.obtener_turno_por_id, name='obtener_turno_por_id'),
    path('api/turnos/<int:turno_id>/completar/', func_views.completar_turno, name='completar_turno'),
    path('api/turnos/<int:turno_id>/procesar-sena/', func_views.procesar_sena_turno, name='procesar_sena_turno'),
    path('api/turnos/verificar-horarios/', func_views.obtener_horarios_disponibles, name='verificar_horarios'),
    path('api/turnos/verificar-disponibilidad/', func_views.verificar_disponibilidad, name='verificar_disponibilidad'),
    path('api/turnos/mis-turnos/', func_views.mis_turnos, name='mis_turnos'),
    
    path('api/turnos/cancelar-propio/<int:turno_id>/', func_views.cancelar_turno_unificado, name='cancelar_mi_turno'),
    path('api/turnos/<int:turno_id>/cancelar/', func_views.cancelar_turno_unificado, name='cancelar-turno'),
    path('api/turnos/<int:turno_id>/cancelar-con-reoferta/', func_views.cancelar_turno_unificado, name='cancelar_turno_con_reoferta'),
    
    path('api/turnos/<int:turno_id>/actualizar-pago/', func_views.actualizar_pago_presencial, name='actualizar_pago_turno'),
    path('api/turnos/<int:turno_id>/completar-reembolso-manual/', func_views.completar_reembolso_manual, name='completar_reembolso_manual'),
    path('api/turnos/<int:turno_id>/cambiar-estado/<str:nuevo_estado>/', func_views.cambiar_estado_turno, name='cambiar_estado_turno'),
    path('api/turnos/<int:turno_id>/completar-pago/', func_views.completar_pago_turno, name='completar_pago_turno'),
    path('api/turnos/registrar-interes/', func_views.registrar_interes_turno, name='registrar_interes_turno'),
    path('api/turnos/<int:turno_id>/interesados/', contar_interesados, name='contar_interesados'),
    path('api/turnos/ocupados/', turnos_ocupados, name='turnos_ocupados'),

    # ================================
    # Categorías Productos (Funciones)
    # ================================
    path('api/categorias/productos/crear/', func_views.crear_categoria_producto, name='crear_categoria_producto'),
    path('api/categorias/productos/editar/<int:pk>/', func_views.editar_categoria_producto, name='editar_categoria_producto'),
    path('api/categorias/productos/eliminar/<int:pk>/', func_views.eliminar_categoria_producto, name='eliminar_categoria_producto'),

    # ==============================
    # Roles y Permisos
    # ==============================
    path('api/roles/', func_views.listado_roles, name='listado_roles'),
    path('api/roles/crear/', func_views.crear_rol, name='crear_rol'),
    path('api/roles/<int:pk>/', func_views.editar_rol, name='detalle_rol'),
    path('api/roles/eliminar/<int:pk>/', func_views.eliminar_rol, name='eliminar_rol'),
    path('api/permisos/', func_views.listado_permisos, name='listado_permisos'),

    # ==============================
    # API MercadoPago
    # ==============================
    path('api/mercadopago/crear-preferencia-sena/', func_views.crear_preferencia_pago_seña, name='crear_preferencia_pago_seña'),
    path('api/mercadopago/pago-exitoso/', func_views.pago_exitoso, name='mp_pago_exitoso'),
    path('api/mercadopago/pago-error/', func_views.pago_error, name='mp_pago_error'),
    path('api/mercadopago/pago-pendiente/', func_views.pago_pendiente, name='mp_pago_pendiente'),
    path('mercadopago/webhook/', func_views.mercadopago_webhook, name='mercadopago_webhook'),

    # ================================
    # Proveedores
    # ================================
    path('api/proveedores/', ProveedorListCreateView.as_view(), name='proveedores-list'),
    path('api/proveedores/<int:pk>/', ProveedorRetrieveUpdateDestroyView.as_view(), name='proveedores-detail'),

    # ================================
    # Usuario Logueado
    # ================================
    path('api/usuarios/<int:user_id>/', func_views.obtener_usuario_por_id, name='obtener_usuario_por_id'),

    # ================================
    # Ventas
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
    # Pedidos (Proveedores)
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
    path('api/pedidos/<int:pedido_id>/enviar/', enviar_pedido_proveedor, name='enviar-pedido'),
    path('api/externo/pedido/<str:token>/', func_views.obtener_pedido_externo, name='pedido-externo-get'),
    path('api/externo/pedido/<str:token>/confirmar/', func_views.confirmar_pedido_externo, name='pedido-externo-post'),
    path('api/pedidos/<int:pedido_id>/proponer-precios/', func_views.proponer_precios, name='proponer-precios'),
    path('api/pedidos/<int:pedido_id>/confirmar-precios/', func_views.confirmar_precios, name='confirmar_precios'),

    # ================================
    # Listas de Precios
    # ================================
    path('api/listas-precios/', ListaPrecioProveedorViewSet.as_view({'get': 'list', 'post': 'create'}), name='listas-precios-list'),
    path('api/listas-precios/<int:pk>/', ListaPrecioProveedorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='listas-precios-detail'),
    path('api/listas-precios/por-proveedor/', func_views.listas_por_proveedor, name='listas-por-proveedor'),
    path('api/listas-precios/<int:pk>/desactivar/', func_views.desactivar_lista_precio, name='desactivar-lista-precio'),
    path('api/listas-precios/actualizar-masivo/', func_views.actualizar_listas_masivo, name='actualizar-listas-masivo'),
    path('api/historial-precios/', HistorialPreciosViewSet.as_view({'get': 'list'}), name='historial-precios-list'),
    path('api/historial-precios/<int:pk>/', HistorialPreciosViewSet.as_view({'get': 'retrieve'}), name='historial-precios-detail'),
    path('api/calcular-precios-pedido/', func_views.calcular_precios_pedido, name='calcular-precios-pedido'),
    path('api/calcular-precio-sugerido/', func_views.calcular_precio_sugerido, name='calcular-precio-sugerido'),

    # ================================
    # Reoferta / WhatsApp
    # ================================
    path('api/turnos/<int:turno_id>/aceptar-oferta/<str:token>/', func_views.aceptar_oferta_turno, name='aceptar_oferta_turno'),
    path('api/turnos/mis-intereses/', func_views.listar_intereses_usuario, name='listar_intereses_usuario'),
    path('api/turnos/eliminar-interes/<int:interes_id>/', func_views.eliminar_interes_turno, name='eliminar_interes_turno'),
    path('api/reoferta/configuracion/', func_views.obtener_configuracion_reoferta, name='configuracion-reoferta'),
    path('api/reoferta/configuracion/actualizar/', func_views.actualizar_configuracion_reoferta, name='actualizar-configuracion-reoferta'),
    path('api/reoferta/estadisticas/', func_views.estadisticas_reoferta, name='estadisticas-reoferta'),
    path('api/reoferta/forzar/<int:turno_id>/', func_views.forzar_reoferta, name='forzar-reoferta'),
    path('api/intereses-turnos/cliente/<int:cliente_id>/', func_views.listar_intereses_cliente, name='listar-intereses-cliente'),
    path('api/reoferta/respuesta/<int:interes_id>/', func_views.procesar_respuesta_oferta, name='procesar-respuesta-oferta'),
    path('api/turnos/<int:turno_id>/oferta-info/<str:token>/', func_views.oferta_info_api, name='oferta_info_api'),

    # Cotizaciones y Dashboard
    path('api/cotizacion-externa/<str:token>/', gestionar_cotizacion_externa, name='cotizacion_externa'),
    path('api/dashboard/', func_views.dashboard_data, name='dashboard_data'),

    # Solicitudes Presupuesto
    path('api/solicitudes-presupuesto/', SolicitudPresupuestoViewSet.as_view({'get': 'list'}), name='solicitudes-list'),
    path('api/solicitudes-presupuesto/<int:pk>/', SolicitudPresupuestoViewSet.as_view({'get': 'retrieve'}), name='solicitudes-detail'),
    path('api/solicitudes-presupuesto/<int:pk>/generar-orden/', SolicitudPresupuestoViewSet.as_view({'post': 'generar_orden_compra'}), name='solicitudes-generar-orden'),

    path('api/turnos/reembolsos-pendientes/', 
         func_views.obtener_turnos_con_reembolso_pendiente, 
         name='reembolsos_pendientes'),
    
    path('api/turnos/<int:turno_id>/cancelar-unificado/', 
         func_views.cancelar_turno_unificado, 
         name='cancelar-turno-unificado'),

    # Validar cupón
    path('api/promociones/validar/<str:codigo>/', validar_cupon, name='validar_cupon'),

    # Password Reset
    path('api/password-reset/solicitar/', func_views.solicitar_reset_password, name='solicitar-reset'),
    path('api/password-reset/confirmar/', func_views.confirmar_reset_password, name='confirmar-reset'),

    # 💰 LIQUIDACIÓN DE SUELDOS
    path('api/reporte-liquidacion/', ReporteLiquidacionView.as_view(), name='reporte_liquidacion'),
    path('api/reporte-liquidacion/pdf/', ReporteLiquidacionPDFView.as_view(), name='reporte_liquidacion_pdf'),
    path('api/liquidaciones/registrar/', RegistrarPagoLiquidacionView.as_view(), name='registrar_pago'),
    path('api/liquidaciones/historial/', HistorialLiquidacionesView.as_view(), name='historial_pagos'),

    # Parametrizar la política de seña
    path('api/configuracion/', func_views.gestionar_configuracion, name='configuracion_sistema'),
]