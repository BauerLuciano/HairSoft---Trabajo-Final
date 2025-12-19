from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from datetime import date, datetime
import logging

from .models import (
    Turno, Producto, Auditoria, Usuario, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago
)
from .middleware import get_current_request_data

logger = logging.getLogger(__name__)

# Modelos a vigilar (CRUD)
MODELOS_A_AUDITAR = [
    Usuario, Producto, Turno, Venta, Pedido, Rol,
    Servicio, Marca, Proveedor, CategoriaProducto, CategoriaServicio, MetodoPago
]

def serializar(valor):
    if isinstance(valor, (Decimal, float)):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
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

# ---------------------------------------------------------
# AUDITORÍA DE DATOS (SOLO CRUD)
# ---------------------------------------------------------

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
    if sender in MODELOS_A_AUDITAR:
        if sender == Auditoria: return

        try:
            req_data = get_current_request_data()
            usuario_db = req_data.get('user')
            navegador = req_data.get('navegador', 'Desconocido')
            
            if usuario_db and not getattr(usuario_db, 'is_authenticated', False):
                usuario_db = None

            nombre_modelo = sender.__name__
            datos_nuevos = obtener_datos(instance)
            reporte = {}
            reporte['__meta__'] = {'navegador': navegador, 'timestamp': datetime.now().isoformat()}
            accion = ''

            if created:
                accion = 'CREAR'
                for k, v in datos_nuevos.items():
                    reporte[k] = {'tipo': 'VALOR', 'valor': v}
            
            elif hasattr(instance, '_estado_anterior'):
                accion = 'EDITAR'
                datos_viejos = instance._estado_anterior
                hay_cambios = False

                for key, val_nuevo in datos_nuevos.items():
                    val_viejo = datos_viejos.get(key)
                    v1 = serializar(val_viejo)
                    v2 = serializar(val_nuevo)

                    if v1 != v2:
                        hay_cambios = True
                        reporte[key] = {'tipo': 'CAMBIO', 'anterior': v1, 'nuevo': v2}
                    else:
                        reporte[key] = {'tipo': 'VALOR', 'valor': v2}
                
                if not hay_cambios: return

            else:
                return

            Auditoria.objects.create(
                usuario=usuario_db,
                modelo_afectado=nombre_modelo,
                objeto_id=str(instance.pk),
                accion=accion,
                detalles=reporte, 
                ip_address=req_data.get('ip')
            )
            # print(f"✅ Auditoría CRUD: {accion} {nombre_modelo}")

        except Exception as e:
            print(f"❌ Error Auditoría CRUD: {e}")

@receiver(post_delete)
def auditar_borrado(sender, instance, **kwargs):
    if sender in MODELOS_A_AUDITAR:
        try:
            req_data = get_current_request_data()
            usuario_db = req_data.get('user')
            if usuario_db and not getattr(usuario_db, 'is_authenticated', False):
                usuario_db = None
            
            navegador = req_data.get('navegador', 'Desconocido')
            datos = obtener_datos(instance)
            reporte = {k: {'tipo': 'VALOR', 'valor': v} for k, v in datos.items()}
            reporte['__meta__'] = {'navegador': navegador}

            Auditoria.objects.create(
                usuario=usuario_db,
                modelo_afectado=sender.__name__,
                objeto_id=str(instance.pk),
                accion='ELIMINAR',
                detalles=reporte,
                ip_address=req_data.get('ip')
            )
        except Exception as e:
            print(f"❌ Error Auditoría Delete: {e}")