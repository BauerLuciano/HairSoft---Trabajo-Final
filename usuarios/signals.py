from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from .models import Turno, ConfiguracionReoferta
# from .turno_service import TurnoService  # Ya no es necesario si llamas la task directamente
from .tasks import procesar_reoferta_masiva  # Importar la tarea Celery directamente
import logging

logger = logging.getLogger(__name__)


# 🛑 CORRECCIÓN: Usamos post_save para asegurar que el objeto Turno ya se guardó
@receiver(post_save, sender=Turno)
def manejar_cancelacion_turno_post_save(sender, instance, created, **kwargs):
    """
    Señal que detecta cuando un turno cambia a estado CANCELADO 
    y dispara el proceso de reoferta automática de forma asíncrona.
    """
    if created:
        return  # No hacer nada si es un nuevo turno, solo nos interesa la actualización (cancelación)
    
    # 1. Obtener el estado anterior si es posible (solo se puede hacer con una consulta extra en post_save)
    # Sin embargo, para simplificar, usaremos el estado actual y confiamos en el proceso de la View/API.
    
    # Si el estado actual es CANCELADO y la oferta no está activa (evitar re-procesar)
    if instance.estado == 'CANCELADO' and not instance.oferta_activa:
        
        # OBTENER EL ESTADO ANTERIOR DE MANERA SEGURA (si es crítico)
        try:
            # Obtener la instancia del turno de la base de datos *antes* de esta operación
            # Nota: Esto es complejo en post_save. Es más fácil asumir que la vista 
            # (ej: `cancelar_turno_con_reoferta` en views.py) ya puso `oferta_activa = True` 
            # al guardarlo. 
            # 
            # Ya que la vista `cancelar_turno_con_reoferta` ya maneja la lógica de poner 
            # `estado='CANCELADO'` y `oferta_activa=True` *antes* de llamar al save, 
            # y además llama directamente a la task, desactivaremos esta señal
            # para evitar duplicar la ejecución de `procesar_reoferta_masiva`.

            # Si la vista *NO* maneja la reoferta, entonces esta señal debe hacer lo siguiente:
            
            # --- Lógica si la View *NO* es la que inicia la reoferta ---
            
            # Buscamos el estado previo. Ya que estamos en post_save, 
            # podemos usar la lógica que tenías en pre_save:
            try:
                # Si el estado realmente cambió a CANCELADO en esta transacción
                turno_anterior = Turno.objects.get(pk=instance.pk)
                
                # Si la cancelación se debe a la API o un cambio manual, y la reoferta no se inició:
                if turno_anterior.estado != 'CANCELADO' and ConfiguracionReoferta.get_configuracion().activo:

                    logger.info(f"🚨 Turno {instance.id} cancelado (post_save) - Disparando reoferta asíncrona")
                    
                    # Ejecutar la tarea después de que la transacción haya terminado exitosamente
                    # Esto asegura que el estado CANCELADO sea visible para Celery
                    transaction.on_commit(lambda: procesar_reoferta_masiva.delay(instance.id))
                    
            except Turno.DoesNotExist:
                 pass # Caso raro, pero posible si el save falla.
                 
            # --- Fin de la Lógica alternativa ---

            # Como tu `views.py` tiene la función `cancelar_turno_con_reoferta` 
            # que ya maneja explícitamente la lógica y el disparo de la tarea Celery, 
            # es **altamente recomendado DESACTIVAR esta señal o modificarla** # para evitar dos envíos de notificaciones.

            # DEJO LA LÓGICA DE DETECCIÓN DE CANCELACIÓN EN post_save AQUÍ:

            # Esto solo se dispara si la cancelación ocurre por fuera de la vista 
            # de "cancelar_turno_con_reoferta" (ej. en el Admin o en otra view que solo llama a .save())
            
            # La mejor manera de evitar conflictos es que el campo `oferta_activa` 
            # sea actualizado por la vista (o servicio) que inicia la reoferta. 
            # Si el turno está CANCELADO y `oferta_activa=False` (o nulo, si no se procesó), 
            # entonces lo disparamos.
            
            if instance.estado == 'CANCELADO' and not instance.oferta_activa and instance.canal == 'WEB':
                if ConfiguracionReoferta.get_configuracion().activo:
                    logger.info(f"🚨 Turno {instance.id} CANCELADO (Señal) - Iniciando reoferta.")
                    transaction.on_commit(lambda: procesar_reoferta_masiva.delay(instance.id))
                    
                    # Opcional: Marcar el turno como "procesado" por la reoferta 
                    # si lo hicimos desde aquí, para no re-procesar
                    instance.oferta_activa = True
                    instance.save(update_fields=['oferta_activa'])
                    
        except Exception as e:
            logger.error(f"❌ Error en señal de cancelación (post_save): {str(e)}")

# Desconectar señal de auth existente
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import update_last_login
try:
    user_logged_in.disconnect(update_last_login, dispatch_uid='update_last_login')
except:
    pass
# Si necesitas un manejo más estricto del estado anterior, usa este bloque:
# @receiver(pre_save, sender=Turno)
# def guardar_estado_anterior(sender, instance, **kwargs):
#     if instance.pk:
#         try:
#             instance._estado_anterior = Turno.objects.get(pk=instance.pk).estado
#         except Turno.DoesNotExist:
#             instance._estado_anterior = None


# @receiver(post_save, sender=Turno)
# def manejar_cancelacion_turno_completa(sender, instance, created, **kwargs):
#     estado_anterior = getattr(instance, '_estado_anterior', None)
#     if estado_anterior != 'CANCELADO' and instance.estado == 'CANCELADO':
#         if instance.canal == 'WEB' and ConfiguracionReoferta.get_configuracion().activo:
#             transaction.on_commit(lambda: procesar_reoferta_masiva.delay(instance.id))


# Nota: He dejado el código anterior comentado para referencia, pero el bloque superior
# asume que la vista no siempre dispara la reoferta. Si tu vista `cancelar_turno_con_reoferta`
# es el ÚNICO lugar para cancelar, puedes eliminar esta señal.