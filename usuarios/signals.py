# usuarios/signals.py (VERSIÓN CORREGIDA - CON CELERY FIDELIZACIÓN + LOGINS)
from django.db.models.signals import pre_save, post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, time
import logging, uuid

# 🔥 FIX: Agregamos Liquidacion a los imports
from .models import (
    Turno, Producto, Auditoria, Usuario, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago,
    InteresTurnoLiberado, PromocionReactivacion, SesionCaja, MovimientoCaja,
    Liquidacion, PedidoWeb, DetallePedidoWeb, ConfiguracionLocal,
    ConfiguracionSistema, Envio, HorarioAtencion,
    Permiso, Silla, DetalleVenta, DetallePedido, NotaCredito,
    SolicitudReabastecimiento, SolicitudPresupuesto, CotizacionProveedor,
    Cotizacion, ConfiguracionReoferta,
    PasswordResetToken, Caja, PagoTemporal, ListaPrecioProveedor,
)
from .middleware import get_current_request_data
from .auditoria_service import AuditoriaService
from .tasks import procesar_reactivacion_clientes_inactivos

logger = logging.getLogger(__name__)

# =========================================================
# LÓGICA DE NEGOCIO: FIDELIZACIÓN AUTOMÁTICA
# =========================================================
@receiver(post_save, sender=Turno)
def disparar_analisis_fidelizacion(sender, instance, **kwargs):
    """
    ✅ VERSIÓN ASÍNCRONA (RAPIDÍSIMA):
    Como tienes Celery + Redis configurado, esto NO traba la pantalla.
    
    Lógica: Si se guarda/modifica un turno con fecha pasada (histórico),
    le avisamos al Worker que revise si hay clientes para reactivar.
    """
    try:
        if instance.fecha and instance.fecha <= timezone.now().date():
            logger.info(f"🔄 Turno histórico {instance.id} ({instance.fecha}) guardado. Disparando Worker...")
            procesar_reactivacion_clientes_inactivos.delay()
            
    except Exception as e:
        logger.error(f"❌ Error signal fidelización: {e}")
        
# =========================================================
# AUDITORÍA DE DATOS (NO TOCAR)
# =========================================================

# 🔥 FIX: Agregamos Liquidacion a la lista de vigilancia
# Modelos cuya creación / edición / borrado se audita automáticamente.
MODELOS_A_AUDITAR = [
    Usuario, Permiso, Rol, PasswordResetToken,
    Producto, Marca, Proveedor, CategoriaProducto, ListaPrecioProveedor,
    Servicio, CategoriaServicio,
    Turno, Silla, InteresTurnoLiberado, PromocionReactivacion, ConfiguracionReoferta,
    Venta, DetalleVenta, NotaCredito,
    Pedido, DetallePedido,
    PedidoWeb, DetallePedidoWeb, Envio,
    MetodoPago, PagoTemporal,
    SesionCaja, MovimientoCaja, Caja, Liquidacion,
    ConfiguracionLocal, ConfiguracionSistema, HorarioAtencion,
    SolicitudReabastecimiento, SolicitudPresupuesto, CotizacionProveedor, Cotizacion,
]

def serializar(valor):
    from django.db.models.fields.files import FieldFile
    if isinstance(valor, FieldFile):
        return valor.name if valor else None
    if isinstance(valor, (Decimal, float)): 
        return float(valor)
    if isinstance(valor, (date, datetime)): 
        return valor.isoformat()
    if isinstance(valor, time): 
        return valor.strftime("%H:%M:%S") 
    if isinstance(valor, uuid.UUID): 
        return str(valor)
    if hasattr(valor, 'pk'): 
        return str(valor)
    return valor

def obtener_datos(instance):
    try:
        data = {}
        for field in instance._meta.fields:
            if field.name in ['password', 'imagen', 'groups', 'user_permissions', 'last_login']: 
                continue
            val = getattr(instance, field.name)
            if hasattr(instance, f'get_{field.name}_display'):
                val = getattr(instance, f'get_{field.name}_display')()
            data[field.name] = serializar(val)
        return data
    except Exception as e:
        logger.error(f"Error obteniendo datos para auditoría: {e}")
        return {}

@receiver(pre_save)
def capturar_estado_previo(sender, instance, **kwargs):
    if sender in MODELOS_A_AUDITAR and instance.pk:
        try:
            viejo = sender.objects.get(pk=instance.pk)
            instance._estado_anterior = obtener_datos(viejo)
        except sender.DoesNotExist:
            instance._estado_anterior = {}

@receiver(post_save)
def auditar_cambios(sender, instance, created, **kwargs):
    # Fix para evitar bucles infinitos en auditoría
    if getattr(instance, '_disable_audit', False): 
        return

    if sender in MODELOS_A_AUDITAR and sender != Auditoria:
        try:
            nombre_modelo = sender.__name__
            datos_nuevos = obtener_datos(instance)
            
            # Acción por defecto
            accion = 'CREAR' if created else 'EDITAR'
            
            # =========================================================
            # 🔥 LÓGICA PERSONALIZADA PARA CAJA (CORREGIDA)
            # =========================================================
            if nombre_modelo == 'SesionCaja':
                if created:
                    accion = 'APERTURA_CAJA'
                elif hasattr(instance, '_estado_anterior'):
                    datos_viejos = instance._estado_anterior
                    if not datos_viejos.get('fecha_cierre') and datos_nuevos.get('fecha_cierre'):
                        accion = 'CIERRE_CAJA'
                        
            elif nombre_modelo == 'MovimientoCaja' and created:
                tipo_mov = getattr(instance, 'tipo', '').upper()
                es_venta = getattr(instance, 'venta_relacionada_id', None)
                es_turno = getattr(instance, 'turno_relacionado_id', None)
                concepto = getattr(instance, 'concepto', '').upper()

                if tipo_mov == 'EGRESO':
                    accion = 'EGRESO_MANUAL'
                elif concepto == 'COBRO_RESTANTE':
                    accion = 'COBRO_RESTANTE'
                elif es_venta or concepto == 'VENTA':
                    accion = 'INGRESO_VENTA'
                elif es_turno or concepto == 'TURNO':
                    accion = 'INGRESO_TURNO'
                else:
                    accion = 'INGRESO_MANUAL'
            # =========================================================

            reporte = {}
            hay_cambios = False
            
            if created:
                for k, v in datos_nuevos.items(): 
                    reporte[k] = {'tipo': 'VALOR', 'valor': v}
                hay_cambios = True
            elif hasattr(instance, '_estado_anterior'):
                datos_viejos = instance._estado_anterior
                # Los campos auto_now (fecha_actualizacion, fecha_modificacion, ...)
                # cambian en CADA save() aunque no haya un cambio funcional real,
                # generando eventos EDITAR "vacíos" (p. ej. PedidoWeb #167 donde el
                # único cambio era fecha_actualizacion). Se excluyen del diff para
                # que un save() sin cambios funcionales no cree auditoría de ruido.
                # NO afecta eventos históricos ni el CREAR (que conserva sus VALOR).
                campos_auto_now = {
                    f.name for f in instance._meta.fields
                    if getattr(f, 'auto_now', False)
                }
                for k, v_nuevo in datos_nuevos.items():
                    if k in campos_auto_now:
                        continue
                    v_viejo = datos_viejos.get(k)
                    if serializar(v_viejo) != serializar(v_nuevo):
                        hay_cambios = True
                        reporte[k] = {
                            'tipo': 'CAMBIO', 
                            'anterior': serializar(v_viejo), 
                            'nuevo': serializar(v_nuevo)
                        }
            
            # Solo añadir dia_semana como referencia si ya hay otros cambios reales
            if nombre_modelo == 'HorarioAtencion' and hay_cambios and 'dia_semana' not in reporte:
                dia_ref = datos_nuevos.get('dia_semana') or (datos_viejos.get('dia_semana') if not created else '')
                if dia_ref:
                    reporte['dia_semana'] = {'tipo': 'VALOR', 'valor': dia_ref}

            if hay_cambios:
                AuditoriaService.registrar(
                    accion=accion,
                    modelo_afectado=nombre_modelo,
                    objeto_id=instance.pk,
                    detalles=reporte,
                )
        except Exception as e:
            logger.error(f"❌ Error Auditoría: {e}")

@receiver(post_delete)
def auditar_borrado(sender, instance, **kwargs):
    if sender in MODELOS_A_AUDITAR:
        try:
            datos = obtener_datos(instance)
            AuditoriaService.registrar(
                accion='ELIMINAR',
                modelo_afectado=sender.__name__,
                objeto_id=instance.pk,
                detalles={k: {'tipo': 'VALOR', 'valor': v} for k, v in datos.items()},
            )
        except Exception as e:
            logger.error(f"Error en auditoría de borrado: {e}")

# =========================================================
# 🔥 NUEVO: AUDITORÍA DE INICIO Y CIERRE DE SESIÓN 🔥
# =========================================================

@receiver(user_logged_in)
def auditar_inicio_sesion(sender, request, user, **kwargs):
    try:
        req_data = get_current_request_data()
        ip = req_data.get('ip', 'Desconocida')
        navegador = req_data.get('navegador', 'Desconocido')
        
        detalles = {
            'Mensaje del Sistema': {
                'tipo': 'VALOR', 
                'valor': f'El usuario {getattr(user, "username", getattr(user, "correo", "Desconocido"))} inició sesión exitosamente.'
            }
        }
        
        AuditoriaService.registrar(
            accion='LOGIN',
            modelo_afectado='SesionDeUsuario',
            objeto_id=user.pk,
            detalles=detalles,
            usuario=user,
        )
    except Exception as e:
        logger.error(f"❌ Error al auditar LOGIN: {e}")

@receiver(user_logged_out)
def auditar_cierre_sesion(sender, request, user, **kwargs):
    try:
        identificador = "Desconocido"
        if user:
            identificador = getattr(user, "username", getattr(user, "correo", "Desconocido"))

        detalles = {
            'Mensaje del Sistema': {
                'tipo': 'VALOR', 
                'valor': f'El usuario {identificador} cerró sesión.'
            }
        }
        
        AuditoriaService.registrar(
            accion='LOGOUT',
            modelo_afectado='SesionDeUsuario',
            objeto_id=user.pk if user else None,
            detalles=detalles,
            usuario=user,
        )
    except Exception as e:
        logger.error(f"❌ Error al auditar LOGOUT: {e}")