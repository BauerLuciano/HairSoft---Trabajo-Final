from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
import logging
import time

from .models import (
    Turno, 
    ConfiguracionReoferta, 
    Producto, 
    SolicitudPresupuesto, 
    Cotizacion,
    InteresTurnoLiberado
)

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
        return
    
    if instance.estado == 'CANCELADO' and not instance.oferta_activa:
        if ConfiguracionReoferta.get_configuracion().activo:
            try:
                hay_interesados = InteresTurnoLiberado.objects.filter(
                    fecha_deseada=instance.fecha,
                    hora_deseada=instance.hora,
                    peluquero=instance.peluquero,
                    estado_oferta='pendiente'
                ).exists()

                if hay_interesados:
                    logger.info(f"🚨 Turno {instance.id} CANCELADO - Hay interesados. Iniciando reoferta.")
                    Turno.objects.filter(pk=instance.pk).update(oferta_activa=True)
                    transaction.on_commit(lambda: procesar_reoferta_masiva.delay(instance.id))
                else:
                    logger.info(f"ℹ️ Turno {instance.id} cancelado, sin interesados.")
                    
            except Exception as e:
                logger.error(f"❌ Error en señal de cancelación: {str(e)}")

# ==============================================================================
# 2. WHATSAPP AUTOMÁTICO CUANDO MODIFICÁS TURNO VIEJO
# ==============================================================================

@receiver(post_save, sender=Turno)
def enviar_whatsapp_reactivacion(sender, instance, created, **kwargs):
    """
    Cuando modificás un turno en Django Admin y ponés fecha vieja,
    manda WhatsApp AUTOMÁTICO al cliente inactivo.
    """
    # Solo ejecutar cuando se EDITA un turno existente (no nuevo)
    if created:
        return
    
    from django.utils import timezone
    from datetime import timedelta
    
    # Verificar si la fecha es vieja (más de 60 días)
    fecha_limite = timezone.now().date() - timedelta(days=60)
    
    if instance.fecha < fecha_limite:
        print("="*60)
        print("🔥 WHATSAPP AUTOMÁTICO ACTIVADO")
        print(f"📅 Turno editado: ID {instance.id}, Fecha: {instance.fecha}")
        print(f"👤 Cliente: {instance.cliente.nombre} ({instance.cliente.telefono})")
        print("="*60)
        
        # Importar y ejecutar la tarea DIRECTAMENTE
        from .tasks import procesar_reactivacion_clientes_inactivos
        
        try:
            # Ejecutar sincrónicamente para ver resultado inmediato
            resultado = procesar_reactivacion_clientes_inactivos()
            print(f"✅ Tarea ejecutada: {resultado}")
            print("📱 WhatsApp debería llegar en segundos...")
        except Exception as e:
            print(f"❌ Error ejecutando reactivación: {e}")

# ==============================================================================
# 3. AUTOMATIZACIÓN DE PROVEEDORES
# ==============================================================================

@receiver(post_save, sender=Producto)
def verificar_stock_minimo(sender, instance, **kwargs):
    stock_minimo = getattr(instance, 'stock_minimo', 0)
    
    if instance.stock_actual <= stock_minimo:
        ya_existe_solicitud = SolicitudPresupuesto.objects.filter(
            producto=instance, 
            estado='PENDIENTE'
        ).exists()

        if not ya_existe_solicitud:
            print(f"📉 ALERTA STOCK BAJO: {instance.nombre} ({instance.stock_actual}/{stock_minimo}). Iniciando licitación...")
            transaction.on_commit(lambda: _iniciar_proceso_compra(instance.id))

def _iniciar_proceso_compra(producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        cantidad_solicitada = getattr(producto, 'cantidad_a_pedir', 20)
        if cantidad_solicitada <= 0: cantidad_solicitada = 10

        solicitud = SolicitudPresupuesto.objects.create(
            producto=producto,
            cantidad_requerida=cantidad_solicitada 
        )

        proveedores = producto.proveedores.all() 
        print(f"🔎 Producto: {producto.nombre} - Proveedores encontrados: {proveedores.count()}")

        if not proveedores.exists():
            print(f"⚠️ El producto {producto.nombre} no tiene proveedores asignados.")
            return

        enviados = 0
        errores = 0

        for prov in proveedores:
            print(f"   👉 Procesando proveedor: {prov.nombre} (Email: {prov.email})")
            
            if prov.email: 
                try:
                    cotizacion = Cotizacion.objects.create(
                        solicitud=solicitud,
                        proveedor=prov
                    )
                    
                    enviar_email_cotizacion_proveedor.delay(cotizacion.id)
                    enviados += 1
                    print(f"      ✅ Tarea de email encolada para {prov.nombre}")
                    
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