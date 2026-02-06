# usuarios/signals.py (VERSIÓN CORREGIDA - SIN CELERY)
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from datetime import date, datetime, time
import logging
import uuid

from .models import (
    Turno, Producto, Auditoria, Usuario, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago,
    InteresTurnoLiberado 
)
from .middleware import get_current_request_data

logger = logging.getLogger(__name__)

# =========================================================
# LÓGICA DE NEGOCIO: REOFERTA AUTOMÁTICA (Whatsapp) - DESACTIVADA
# =========================================================

@receiver(post_save, sender=Turno)
def disparar_reoferta_por_cancelacion(sender, instance, created, **kwargs):
    """
    🔥 VERSIÓN DESACTIVADA - Ya no usa Celery
    Ahora el Service maneja TODO sincrónicamente
    """
    # COMPLETAMENTE DESACTIVADO - El Service maneja todo
    pass

# =========================================================
# AUDITORÍA DE DATOS (NO TOCAR)
# =========================================================

MODELOS_A_AUDITAR = [
    Usuario, Producto, Turno, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago
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
            accion = 'CREAR' if created else 'EDITAR'
            
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
                Auditoria.objects.create(
                    usuario=usuario_db, 
                    modelo_afectado=nombre_modelo, 
                    objeto_id=str(instance.pk),
                    accion=accion, 
                    detalles=reporte, 
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