"""
Servicio centralizado de auditoría.

Todos los eventos (signals automáticos, acciones manuales de las vistas,
procesos automáticos como webhooks MP o tareas Celery) pasan por
`AuditoriaService.registrar(...)`. Así se:

  1. Centraliza la generación de eventos (una sola fuente de verdad).
  2. Evita duplicados entre signals y auditoría manual.
  3. Estandariza módulo, resultado, snapshot de usuario, IP, navegador,
     endpoint, método HTTP e ID de operación (multi-modelo).
  4. Etiqueta los procesos automáticos como usuario SISTEMA con contexto.

Reutiliza el modelo `Auditoria` existente (compatibilidad histórica).
"""
import logging
import uuid
from contextlib import contextmanager

from .middleware import get_current_request_data, _thread_locals

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeo modelo -> módulo (para clasificar módulo del sistema)
# ---------------------------------------------------------------------------
MODULO_MODELO = {
    'Usuario': 'USUARIOS', 'Permiso': 'USUARIOS', 'Rol': 'USUARIOS',
    'PasswordResetToken': 'USUARIOS',
    'Servicio': 'SERVICIOS', 'CategoriaServicio': 'SERVICIOS',
    'Producto': 'INVENTARIO', 'CategoriaProducto': 'INVENTARIO',
    'Marca': 'INVENTARIO', 'HistorialStock': 'INVENTARIO',
    'Proveedor': 'PROVEEDORES', 'Pedido': 'PROVEEDORES', 'DetallePedido': 'PROVEEDORES',
    'SolicitudReabastecimiento': 'PROVEEDORES', 'SolicitudPresupuesto': 'PROVEEDORES',
    'Cotizacion': 'PROVEEDORES', 'CotizacionProveedor': 'PROVEEDORES',
    'ListaPrecioProveedor': 'PRECIOS', 'HistorialPrecios': 'PRECIOS',
    'Turno': 'TURNOS', 'Silla': 'TURNOS', 'InteresTurnoLiberado': 'TURNOS',
    'PromocionReactivacion': 'TURNOS',
    'Venta': 'VENTAS', 'DetalleVenta': 'VENTAS', 'NotaCredito': 'VENTAS',
    'PedidoWeb': 'PEDIDOS_WEB', 'DetallePedidoWeb': 'PEDIDOS_WEB', 'Envio': 'PEDIDOS_WEB',
    'MetodoPago': 'PAGOS', 'PagoTemporal': 'PAGOS',
    'SesionCaja': 'CAJA', 'MovimientoCaja': 'CAJA', 'Caja': 'CAJA', 'Liquidacion': 'CAJA',
    'ConfiguracionLocal': 'CONFIGURACION', 'ConfiguracionSistema': 'CONFIGURACION',
    'ConfiguracionReoferta': 'CONFIGURACION', 'HorarioAtencion': 'CONFIGURACION',
    'Notificacion': 'SISTEMA',
    'SesionDeUsuario': 'AUTENTICACION',
}

MODULO_ACCION = {
    'LOGIN': 'AUTENTICACION', 'LOGOUT': 'AUTENTICACION',
    'LOGIN_GOOGLE': 'AUTENTICACION', 'LOGIN_FALLIDO': 'AUTENTICACION',
    'CAMBIO_PASSWORD': 'AUTENTICACION',
    'ANULAR_VENTA': 'VENTAS', 'CANCELAR': 'TURNOS',
    'INGRESO_VENTA': 'CAJA', 'INGRESO_TURNO': 'CAJA',
    'INGRESO_MANUAL': 'CAJA', 'EGRESO_MANUAL': 'CAJA',
    'APERTURA_CAJA': 'CAJA', 'CIERRE_CAJA': 'CAJA',
    'COBRO_RESTANTE': 'TURNOS',
    'AJUSTE_STOCK': 'INVENTARIO',
    'CONSULTAR': 'SEGURIDAD', 'EXPORTAR': 'SEGURIDAD', 'RESTAURAR': 'SEGURIDAD',
}


def modulo_de(modelo_afectado, accion=''):
    """Determina el módulo del sistema al que pertenece un evento."""
    accion_upper = (accion or '').upper()
    if accion_upper in MODULO_ACCION:
        return MODULO_ACCION[accion_upper]
    modelo = (modelo_afectado or '')
    if modelo in MODULO_MODELO:
        return MODULO_MODELO[modelo]
    return 'SISTEMA'


def _nombre_completo(usuario):
    if usuario is None:
        return ''
    nombre = f"{getattr(usuario, 'nombre', '')} {getattr(usuario, 'apellido', '')}".strip()
    return nombre or getattr(usuario, 'correo', '') or str(usuario)


class AuditoriaService:
    """Punto único de registro de eventos de auditoría."""

    @staticmethod
    def registrar(accion, modelo_afectado, objeto_id=None, detalles=None,
                  mensaje='', resultado=None, usuario=None, contexto=None,
                  proceso=None):
        """
        Crea un registro de auditoría de forma centralizada.

        Parámetros:
            accion:        código de acción (CREAR, EDITAR, LOGIN, ANULAR_VENTA, ...)
            modelo_afectado: nombre del modelo o entidad afectada
            objeto_id:     id del registro afectado
            detalles:      dict con los valores ANTES/DESPUÉS ({campo: {tipo, anterior, nuevo}})
            mensaje:       motivo / mensaje legible
            resultado:     EXITO / ERROR / SISTEMA (default automático)
            usuario:       usuario que ejecutó (default: el de la request)
            contexto:      dict extra de contexto (ej. proceso automático, montos)
            proceso:       nombre del proceso automático (ej. 'mercadopago_webhook')
        """
        from .models import Auditoria

        req_data = get_current_request_data() or {}
        request_user = req_data.get('user')
        if request_user and not getattr(request_user, 'is_authenticated', False):
            request_user = None

        if usuario is None:
            usuario = request_user

        thread_proceso = getattr(_thread_locals, 'proceso_actual', None)
        thread_es_sistema = getattr(_thread_locals, 'es_sistema', False)
        proceso = proceso or req_data.get('proceso_actual') or thread_proceso
        es_sistema = bool(req_data.get('es_sistema') or thread_es_sistema or proceso)

        # Resultado por defecto
        if resultado is None:
            resultado = 'SISTEMA' if (es_sistema and not usuario) else 'EXITO'

        # Snapshot del usuario (para no depender del estado actual del registro)
        es_usuario_autenticado = bool(
            usuario is not None and getattr(usuario, 'is_authenticated', False)
        )
        if es_usuario_autenticado:
            nombre_completo = _nombre_completo(usuario)
            correo = getattr(usuario, 'correo', '') or ''
        elif usuario is not None:
            nombre_completo = getattr(usuario, 'nombre', '') or 'Anónimo'
            correo = getattr(usuario, 'correo', '') or ''
        elif es_sistema:
            nombre_completo = 'SISTEMA'
            correo = ''
        else:
            # Evento sin usuario identificado (ej. cliente web anónimo)
            nombre_completo = 'Anónimo'
            correo = ''

        contexto_final = dict(contexto or {})
        if es_sistema:
            contexto_final.setdefault('es_sistema', True)
        if proceso:
            contexto_final['proceso'] = proceso
        if req_data.get('id_operacion'):
            contexto_final.setdefault('id_operacion', str(req_data['id_operacion']))

        id_operacion = req_data.get('id_operacion') or uuid.uuid4()

        try:
            auditoria = Auditoria.objects.create(
                usuario=usuario,
                usuario_nombre=nombre_completo,
                usuario_email=correo,
                modelo_afectado=modelo_afectado,
                objeto_id=str(objeto_id) if objeto_id is not None else None,
                accion=accion,
                detalles=detalles or {},
                ip_address=req_data.get('ip'),
                modulo=modulo_de(modelo_afectado, accion),
                resultado=resultado,
                mensaje=mensaje,
                endpoint=req_data.get('endpoint', ''),
                metodo_http=req_data.get('metodo_http', ''),
                user_agent=(req_data.get('navegador') or '')[:500],
                id_operacion=id_operacion,
                contexto=contexto_final,
            )
            # El middleware usa estos ids para marcar EXITO/ERROR según el HTTP status
            ids = req_data.get('auditoria_ids')
            if isinstance(ids, list):
                ids.append(auditoria.id)
            return auditoria
        except Exception as e:
            logger.error(f"❌ Error al registrar auditoría ({accion} {modelo_afectado}): {e}")
            return None

    @staticmethod
    @contextmanager
    def contexto_sistema(proceso):
        """
        Context manager para procesos automáticos (Celery, webhooks, etc.).
        Todo evento auditado dentro quedará identificado como usuario SISTEMA
        y con el proceso en el contexto.
        """
        old_proceso = getattr(_thread_locals, 'proceso_actual', None)
        old_es_sistema = getattr(_thread_locals, 'es_sistema', False)
        _thread_locals.proceso_actual = proceso
        _thread_locals.es_sistema = True
        try:
            yield
        finally:
            _thread_locals.proceso_actual = old_proceso
            _thread_locals.es_sistema = old_es_sistema