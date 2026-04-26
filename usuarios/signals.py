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
    Liquidacion
)
from .middleware import get_current_request_data
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
MODELOS_A_AUDITAR = [
    Usuario, Producto, Turno, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago,
    SesionCaja, MovimientoCaja, Liquidacion
]

def serializar(valor):
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
            req_data = get_current_request_data()
            usuario_db = req_data.get('user')
            if usuario_db and not getattr(usuario_db, 'is_authenticated', False): 
                usuario_db = None
            
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
                # Revisamos si el movimiento tiene origen automático (Venta o Turno)
                # Usamos getattr con _id para no disparar consultas extra a la DB
                es_venta = getattr(instance, 'venta_relacionada_id', None)
                es_turno = getattr(instance, 'turno_relacionado_id', None)
                concepto = getattr(instance, 'concepto', '').upper()

                if es_venta or concepto == 'VENTA':
                    accion = 'INGRESO_VENTA'
                elif es_turno or concepto == 'TURNO':
                    accion = 'INGRESO_TURNO'
                else:
                    # Si no tiene relación, entonces sí es un movimiento manual de caja
                    tipo_mov = getattr(instance, 'tipo', '').upper()
                    if tipo_mov == 'INGRESO':
                        accion = 'INGRESO_MANUAL'
                    elif tipo_mov == 'EGRESO':
                        accion = 'EGRESO_MANUAL'
            # =========================================================

            reporte = {}
            hay_cambios = False
            
            if created:
                for k, v in datos_nuevos.items(): 
                    reporte[k] = {'tipo': 'VALOR', 'valor': v}
                hay_cambios = True
            elif hasattr(instance, '_estado_anterior'):
                datos_viejos = instance._estado_anterior
                for k, v_nuevo in datos_nuevos.items():
                    v_viejo = datos_viejos.get(k)
                    if serializar(v_viejo) != serializar(v_nuevo):
                        hay_cambios = True
                        reporte[k] = {
                            'tipo': 'CAMBIO', 
                            'anterior': serializar(v_viejo), 
                            'nuevo': serializar(v_nuevo)
                        }
            
            if hay_cambios:
                # Agregamos la información técnica para el frontend
                reporte['__meta__'] = {
                    'navegador': req_data.get('navegador', 'Desconocido'),
                    'ip': req_data.get('ip', '127.0.0.1')
                }

                Auditoria.objects.create(
                    usuario=usuario_db, 
                    modelo_afectado=nombre_modelo, 
                    objeto_id=str(instance.pk),
                    accion=accion, 
                    details=reporte, # Nota: Asegúrate si tu modelo usa 'detalles' o 'details'
                    ip_address=req_data.get('ip')
                )
        except Exception as e:
            logger.error(f"❌ Error Auditoría: {e}")

@receiver(post_delete)
def auditar_borrado(sender, instance, **kwargs):
    if sender in MODELOS_A_AUDITAR:
        try:
            req_data = get_current_request_data()
            usuario_db = req_data.get('user')
            if usuario_db and not getattr(usuario_db, 'is_authenticated', False): 
                usuario_db = None
            datos = obtener_datos(instance)
            Auditoria.objects.create(
                usuario=usuario_db, 
                modelo_afectado=sender.__name__, 
                objeto_id=str(instance.pk),
                accion='ELIMINAR', 
                detalles={k: {'tipo': 'VALOR', 'valor': v} for k, v in datos.items()},
                ip_address=req_data.get('ip')
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
        
        # Formateamos los detalles para que tu parser de Vue los entienda perfecto
        detalles = {
            '__meta__': {
                'navegador': navegador,
                'ip': ip
            },
            'Mensaje del Sistema': {
                'tipo': 'VALOR', 
                'valor': f'El usuario {getattr(user, "username", getattr(user, "correo", "Desconocido"))} inició sesión exitosamente.'
            }
        }
        
        Auditoria.objects.create(
            usuario=user,
            modelo_afectado='SesionDeUsuario',  # Tu vue lo clasificará como AUTENTICACION
            objeto_id=str(user.pk),
            accion='LOGIN',
            detalles=detalles,
            ip_address=ip
        )
    except Exception as e:
        logger.error(f"❌ Error al auditar LOGIN: {e}")

@receiver(user_logged_out)
def auditar_cierre_sesion(sender, request, user, **kwargs):
    try:
        req_data = get_current_request_data()
        ip = req_data.get('ip', 'Desconocida')
        navegador = req_data.get('navegador', 'Desconocido')
        
        identificador = "Desconocido"
        if user:
            identificador = getattr(user, "username", getattr(user, "correo", "Desconocido"))

        detalles = {
            '__meta__': {
                'navegador': navegador,
                'ip': ip
            },
            'Mensaje del Sistema': {
                'tipo': 'VALOR', 
                'valor': f'El usuario {identificador} cerró sesión.'
            }
        }
        
        Auditoria.objects.create(
            usuario=user,
            modelo_afectado='SesionDeUsuario', 
            objeto_id=str(user.pk) if user else '0',
            accion='LOGOUT',
            detalles=detalles,
            ip_address=ip
        )
    except Exception as e:
        logger.error(f"❌ Error al auditar LOGOUT: {e}")