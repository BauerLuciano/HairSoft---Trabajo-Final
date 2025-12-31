from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from datetime import date, datetime, time
import logging
import uuid

from .models import (
    Turno, Producto, Auditoria, Usuario, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago,
    InteresTurnoLiberado # Importado arriba para evitar lios
)
from .middleware import get_current_request_data

logger = logging.getLogger(__name__)

# =========================================================
# LÓGICA DE NEGOCIO: REOFERTA AUTOMÁTICA (Whatsapp)
# =========================================================

@receiver(post_save, sender=Turno)
def disparar_reoferta_por_cancelacion(sender, instance, created, **kwargs):
    """
    Detecta si un turno se CANCELÓ.
    Si hay interesados, dispara la tarea de Celery.
    """
    if created:
        return

    # Solo actuamos si el estado es CANCELADO
    if instance.estado == 'CANCELADO':
        print(f"\n⚡ [SIGNAL DEBUG] ---------------------------------------------------")
        print(f"⚡ [SIGNAL DEBUG] Turno {instance.id} pasó a CANCELADO.")
        print(f"⚡ [SIGNAL DEBUG] Datos del Turno -> Fecha: {instance.fecha} | Hora: {instance.hora} | Peluquero ID: {instance.peluquero.id}")
        
        # 1. Buscamos interesados que coincidan en FECHA y PELUQUERO (Filtro grueso)
        candidatos_brutos = InteresTurnoLiberado.objects.filter(
            fecha_deseada=instance.fecha,
            peluquero=instance.peluquero,
            estado_oferta='pendiente'
        )
        
        print(f"⚡ [SIGNAL DEBUG] Interesados encontrados (coincidencia fecha/peluquero): {candidatos_brutos.count()}")

        candidatos_reales = []
        
        # 2. Filtramos la HORA manualmente (Filtro fino)
        for interes in candidatos_brutos:
            # Convertimos ambos a string HH:MM para asegurar comparación perfecta
            hora_turno_str = instance.hora.strftime('%H:%M')
            hora_interes_str = interes.hora_deseada.strftime('%H:%M')
            
            print(f"   👉 Comparando: Turno({hora_turno_str}) vs Interés({hora_interes_str}) - Cliente: {interes.cliente.nombre}")
            
            if hora_turno_str == hora_interes_str:
                print("      ✅ ¡MATCH CONFIRMADO!")
                candidatos_reales.append(interes)
            else:
                print("      ❌ No coincide la hora.")

        # 3. Si hay match, disparamos
        if len(candidatos_reales) > 0:
            print(f"🚀 [SIGNAL] Disparando reoferta a {len(candidatos_reales)} personas.")
            
            # Marcamos oferta activa usando update para evitar recursión
            Turno.objects.filter(pk=instance.pk).update(oferta_activa=True)
            
            from .tasks import procesar_reoferta_masiva
            transaction.on_commit(lambda: procesar_reoferta_masiva.delay(instance.id))
        else:
            print("ℹ️ [SIGNAL] Turno cancelado, pero la hora exacta no tuvo interesados.")
        
        print(f"⚡ [SIGNAL DEBUG] ---------------------------------------------------\n")


# =========================================================
# AUDITORÍA DE DATOS (NO TOCAR - Ya funcionaba bien)
# =========================================================

MODELOS_A_AUDITAR = [
    Usuario, Producto, Turno, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago
]

def serializar(valor):
    if isinstance(valor, (Decimal, float)): return float(valor)
    if isinstance(valor, (date, datetime)): return valor.isoformat()
    if isinstance(valor, time): return valor.strftime("%H:%M:%S") # Fix time error
    if isinstance(valor, uuid.UUID): return str(valor)
    if hasattr(valor, 'pk'): return str(valor)
    return valor

def obtener_datos(instance):
    try:
        data = {}
        for field in instance._meta.fields:
            if field.name in ['password', 'imagen', 'groups', 'user_permissions', 'last_login']: continue
            val = getattr(instance, field.name)
            if hasattr(instance, f'get_{field.name}_display'):
                val = getattr(instance, f'get_{field.name}_display')()
            data[field.name] = serializar(val)
        return data
    except:
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
    if sender in MODELOS_A_AUDITAR and sender != Auditoria:
        try:
            req_data = get_current_request_data()
            usuario_db = req_data.get('user')
            if usuario_db and not getattr(usuario_db, 'is_authenticated', False): usuario_db = None
            
            nombre_modelo = sender.__name__
            datos_nuevos = obtener_datos(instance)
            accion = 'CREAR' if created else 'EDITAR'
            
            reporte = {}
            hay_cambios = False
            
            if created:
                for k, v in datos_nuevos.items(): reporte[k] = {'tipo': 'VALOR', 'valor': v}
                hay_cambios = True
            elif hasattr(instance, '_estado_anterior'):
                datos_viejos = instance._estado_anterior
                for k, v_nuevo in datos_nuevos.items():
                    v_viejo = datos_viejos.get(k)
                    if serializar(v_viejo) != serializar(v_nuevo):
                        hay_cambios = True
                        reporte[k] = {'tipo': 'CAMBIO', 'anterior': serializar(v_viejo), 'nuevo': serializar(v_nuevo)}
            
            if hay_cambios:
                Auditoria.objects.create(
                    usuario=usuario_db, modelo_afectado=nombre_modelo, objeto_id=str(instance.pk),
                    accion=accion, detalles=reporte, ip_address=req_data.get('ip')
                )
        except Exception as e:
            print(f"❌ Error Auditoría: {e}")

@receiver(post_delete)
def auditar_borrado(sender, instance, **kwargs):
    if sender in MODELOS_A_AUDITAR:
        try:
            req_data = get_current_request_data()
            usuario_db = req_data.get('user')
            if usuario_db and not getattr(usuario_db, 'is_authenticated', False): usuario_db = None
            datos = obtener_datos(instance)
            Auditoria.objects.create(
                usuario=usuario_db, modelo_afectado=sender.__name__, objeto_id=str(instance.pk),
                accion='ELIMINAR', detalles={k: {'tipo': 'VALOR', 'valor': v} for k, v in datos.items()},
                ip_address=req_data.get('ip')
            )
        except Exception: pass