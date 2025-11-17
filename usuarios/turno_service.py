# usuarios/turno_service.py
from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction
import logging
from .models import Turno
from .mercadopago_service import MercadoPagoService

logger = logging.getLogger(__name__)

class TurnoService:
    
    @staticmethod
    def procesar_cancelacion_automatica(turno_id, usuario_cancelacion=None):
        """
        Proceso completo de cancelación automática según las reglas de negocio
        """
        try:
            with transaction.atomic():
                turno = Turno.objects.select_related('cliente', 'peluquero').get(id=turno_id)
                
                # Verificar si el turno puede ser cancelado
                if turno.estado == 'CANCELADO':
                    return False, "El turno ya está cancelado"
                
                # Calcular tiempo restante
                ahora = timezone.now()
                fecha_turno = timezone.make_aware(
                    datetime.combine(turno.fecha, turno.hora)
                )
                tiempo_restante = fecha_turno - ahora
                
                # Verificar que no sea un turno pasado
                if tiempo_restante.total_seconds() <= 0:
                    return False, "No se puede cancelar un turno que ya pasó"
                
                # Determinar si corresponde devolución (más de 3 horas)
                corresponde_devolucion = tiempo_restante >= timedelta(hours=3)
                
                # Procesar devolución si corresponde
                devolucion_procesada = False
                mensaje_devolucion = ""
                
                if corresponde_devolucion and turno.monto_seña > 0:
                    devolucion_procesada, mensaje_devolucion = TurnoService._procesar_devolucion_senia(turno)
                
                # Actualizar estado del turno
                turno.estado = 'CANCELADO'
                turno.fecha_modificacion = timezone.now()
                turno.reembolsado = devolucion_procesada
                turno.save()
                
                # Mensaje de resultado
                mensaje = 'Turno cancelado exitosamente'
                if corresponde_devolucion:
                    if devolucion_procesada:
                        mensaje += f'. {mensaje_devolucion}'
                    else:
                        mensaje += '. No se pudo procesar la devolución automáticamente.'
                else:
                    mensaje += '. No corresponde reembolso por cancelación con menos de 3 horas de anticipación.'
                
                logger.info(f"Turno {turno_id} cancelado. Reembolso: {devolucion_procesada}")
                return True, mensaje
                
        except Turno.DoesNotExist:
            return False, "Turno no encontrado"
        except Exception as e:
            logger.error(f"Error al cancelar turno {turno_id}: {str(e)}")
            return False, f"Error al cancelar turno: {str(e)}"
    
    @staticmethod
    def _procesar_devolucion_senia(turno):
        """
        Procesar devolución de la seña según el canal y medio de pago
        """
        try:
            # Para pagos web con Mercado Pago
            if turno.canal == 'WEB' and turno.medio_pago == 'MERCADO_PAGO':
                # En un entorno real, aquí llamarías a la API de Mercado Pago para hacer el reembolso
                # mp_service = MercadoPagoService()
                # resultado = mp_service.devolver_pago(turno.id_pago_mercadopago, turno.monto_seña)
                
                # Por ahora, simulamos el proceso exitoso
                logger.info(f"Simulando reembolso MP para turno {turno.id}, monto: {turno.monto_seña}")
                return True, "Seña reembolsada via Mercado Pago"
            
            # Para pagos presenciales
            elif turno.canal == 'PRESENCIAL':
                # Solo marcamos que corresponde devolución física
                return True, "Cliente debe pasar a buscar el reembolso en efectivo"
            
            # Para otros casos
            else:
                return False, "No se pudo determinar el método de devolución"
                
        except Exception as e:
            logger.error(f"Error en devolución de seña para turno {turno.id}: {str(e)}")
            return False, f"Error en proceso de devolución: {str(e)}"
    
    @staticmethod
    def verificar_anticipacion_cancelacion(turno):
        """
        Verificar si un turno puede ser cancelado con reembolso
        Retorna: (puede_cancelar, hay_reembolso, tiempo_restante)
        """
        try:
            ahora = timezone.now()
            fecha_turno = timezone.make_aware(
                datetime.combine(turno.fecha, turno.hora)
            )
            tiempo_restante = fecha_turno - ahora
            
            # No puede cancelar turnos pasados
            puede_cancelar = tiempo_restante.total_seconds() > 0
            hay_reembolso = tiempo_restante >= timedelta(hours=3)
            
            return puede_cancelar, hay_reembolso, tiempo_restante
            
        except Exception as e:
            logger.error(f"Error verificando anticipación para turno {turno.id}: {str(e)}")
            return False, False, timedelta(0)
# En usuarios/turno_service.py - agregar estos métodos a la clase TurnoService

@staticmethod
def _notificar_interesados(turno_cancelado):
    """
    Notificar a clientes interesados en el horario liberado (FIFO)
    """
    try:
        from .models import InteresTurnoLiberado
        from django.core.mail import send_mail
        from django.conf import settings
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Buscar interesados para el mismo peluquero, fecha, hora y servicios similares
        interesados = InteresTurnoLiberado.objects.filter(
            peluquero=turno_cancelado.peluquero,
            fecha_deseada=turno_cancelado.fecha,
            hora_deseada=turno_cancelado.hora,
            notificado=False
        ).order_by('fecha_registro')[:5]  # FIFO - primeros 5
        
        notificados = 0
        for interesado in interesados:
            # Calcular descuento del 15%
            precio_original = interesado.servicio.precio
            precio_con_descuento = precio_original * 0.85
            
            # Enviar notificación (por ahora solo log)
            logger.info(f"📧 NOTIFICACIÓN: Turno disponible para {interesado.cliente.nombre}")
            logger.info(f"   📅 Fecha: {turno_cancelado.fecha} {turno_cancelado.hora}")
            logger.info(f"   💇 Peluquero: {turno_cancelado.peluquero.nombre}")
            logger.info(f"   💰 Precio original: ${precio_original}")
            logger.info(f"   🔥 Precio con 15% descuento: ${precio_con_descuento}")
            logger.info(f"   ⏰ Tiempo límite: 1 hora para confirmar")
            
            # Marcar como notificado
            interesado.notificado = True
            interesado.fecha_notificacion = timezone.now()
            interesado.save()
            
            notificados += 1
            
            # Aquí podrías integrar:
            # - Envío de email (send_mail)
            # - WhatsApp (con APIs como Twilio)
            # - Notificación push
            
        logger.info(f"✅ Notificados {notificados} interesados para turno {turno_cancelado.id}")
        return notificados > 0
        
    except Exception as e:
        logger.error(f"❌ Error notificando interesados para turno {turno_cancelado.id}: {str(e)}")
        return False

@staticmethod
def registrar_interes_turno(cliente_id, servicio_id, peluquero_id, fecha_deseada, hora_deseada):
    """
    Registrar interés de un cliente en un turno específico
    """
    try:
        from .models import InteresTurnoLiberado, Usuario, Servicio
        
        # Verificar que no exista ya el mismo interés
        interes_existente = InteresTurnoLiberado.objects.filter(
            cliente_id=cliente_id,
            servicio_id=servicio_id,
            peluquero_id=peluquero_id,
            fecha_deseada=fecha_deseada,
            hora_deseada=hora_deseada,
            notificado=False
        ).exists()
        
        if interes_existente:
            return False, "Ya estás registrado en la lista de espera para este horario"
        
        # Crear nuevo interés
        interes = InteresTurnoLiberado.objects.create(
            cliente_id=cliente_id,
            servicio_id=servicio_id,
            peluquero_id=peluquero_id,
            fecha_deseada=fecha_deseada,
            hora_deseada=hora_deseada
        )
        
        logger.info(f"✅ Interés registrado: {cliente_id} para {fecha_deseada} {hora_deseada}")
        return True, "Te avisaremos si se libera este turno"
        
    except Exception as e:
        logger.error(f"❌ Error registrando interés: {str(e)}")
        return False, f"Error al registrar interés: {str(e)}"