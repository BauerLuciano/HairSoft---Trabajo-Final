from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
import logging
import time # ✅ IMPORT NECESARIO PARA EL FRENO DE MAILTRAP

# ✅ Importamos los modelos nuevos (Asegurate de haberlos creado en models.py primero)
from .models import (
    Turno, 
    ConfiguracionReoferta, 
    Producto, 
    SolicitudPresupuesto, 
    Cotizacion
)

# ✅ Importamos la nueva tarea
from .tasks import procesar_reoferta_masiva, enviar_email_cotizacion_proveedor

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. LÓGICA EXISTENTE: REOFERTA DE TURNOS (NO TOCAR)
# ==============================================================================

@receiver(post_save, sender=Turno)
def manejar_cancelacion_turno_post_save(sender, instance, created, **kwargs):
    """
    Señal que detecta cuando un turno cambia a estado CANCELADO 
    y dispara el proceso de reoferta automática de forma asíncrona.
    """
    if created:
        return  # No hacer nada si es un nuevo turno
    
    # Si el estado actual es CANCELADO y la oferta no está activa
    if instance.estado == 'CANCELADO' and not instance.oferta_activa and instance.canal == 'WEB':
        # Verificamos si la configuración está activa
        if ConfiguracionReoferta.get_configuracion().activo:
            try:
                logger.info(f"🚨 Turno {instance.id} CANCELADO (Señal) - Iniciando reoferta.")
                
                # Ejecutar tarea después del commit para evitar Race Conditions
                transaction.on_commit(lambda: procesar_reoferta_masiva.delay(instance.id))
                
                # Marcar oferta como activa para no re-procesar
                # Nota: Usamos update() directo para no disparar señales recursivas
                Turno.objects.filter(pk=instance.pk).update(oferta_activa=True)
                    
            except Exception as e:
                logger.error(f"❌ Error en señal de cancelación (post_save): {str(e)}")

# Desconectar señal de auth existente (Legacy)
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login
try:
    user_logged_in.disconnect(update_last_login, dispatch_uid='update_last_login')
except:
    pass


# ==============================================================================
# 2. NUEVA LÓGICA: AUTOMATIZACIÓN DE PROVEEDORES 🚀
# ==============================================================================

@receiver(post_save, sender=Producto)
def verificar_stock_minimo(sender, instance, **kwargs):
    """
    Dispara la solicitud de presupuesto a proveedores si el stock cae 
    por debajo del mínimo.
    """
    # Verificamos que el producto tenga configurado un stock mínimo
    # (Usamos getattr por si todavía no corriste la migración del campo nuevo)
    stock_minimo = getattr(instance, 'stock_minimo', 0)
    
    if instance.stock_actual <= stock_minimo:
        
        # 1. Evitar Spam: Verificar si ya hay una solicitud PENDIENTE para este producto
        ya_existe_solicitud = SolicitudPresupuesto.objects.filter(
            producto=instance, 
            estado='PENDIENTE'
        ).exists()

        if not ya_existe_solicitud:
            print(f"📉 ALERTA STOCK BAJO: {instance.nombre} ({instance.stock_actual}/{stock_minimo}). Iniciando licitación...")
            
            # Usamos on_commit para asegurar que el Producto esté guardado antes de que Celery lo lea
            transaction.on_commit(lambda: _iniciar_proceso_compra(instance.id))

def _iniciar_proceso_compra(producto_id):
    """Función auxiliar para crear la solicitud y disparar tareas"""
    try:
        producto = Producto.objects.get(id=producto_id)
        
        # Cantidad dinámica o default
        cantidad_solicitada = getattr(producto, 'cantidad_a_pedir', 20)
        if cantidad_solicitada <= 0: cantidad_solicitada = 10

        # 1. Crear la Solicitud Madre
        solicitud = SolicitudPresupuesto.objects.create(
            producto=producto,
            cantidad_requerida=cantidad_solicitada 
        )

        # 2. Buscar proveedores
        proveedores = producto.proveedores.all() 
        print(f"🔎 Producto: {producto.nombre} - Proveedores encontrados: {proveedores.count()}")

        if not proveedores.exists():
            print(f"⚠️ El producto {producto.nombre} no tiene proveedores asignados.")
            return

        # 3. Crear cotizaciones y notificar
        enviados = 0
        errores = 0

        # Bucle con freno para Mailtrap
        for prov in proveedores:
            print(f"   👉 Procesando proveedor: {prov.nombre} (Email: {prov.email})")
            
            if prov.email: 
                try:
                    # Crear cotización
                    cotizacion = Cotizacion.objects.create(
                        solicitud=solicitud,
                        proveedor=prov
                    )
                    
                    # Disparar tarea
                    enviar_email_cotizacion_proveedor.delay(cotizacion.id)
                    enviados += 1
                    print(f"      ✅ Tarea de email encolada para {prov.nombre}")
                    
                    # 🛑 FRENO DE EMERGENCIA: 10 SEGUNDOS
                    print("      ⏳ Esperando 10 segundos para no saturar Mailtrap...")
                    time.sleep(10) 

                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    errores += 1
            else:
                print(f"      ⚠️ SALTADO: {prov.nombre} no tiene email registrado.")

        print(f"🏁 Proceso finalizado. Enviados: {enviados}, Errores: {errores}")

    except Exception as e:
        print(f"❌ Error CRÍTICO iniciando proceso de compra: {str(e)}")