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

class ReofertaAutomaticaService:
    """
    Servicio para manejar el proceso completo de reoferta automática
    """
    
    @staticmethod
    @transaction.atomic
    def procesar_reoferta(turno_cancelado):
        """
        Proceso principal de reoferta automática
        """
        try:
            from .models import InteresTurnoLiberado, ConfiguracionReoferta
            
            logger.info(f"🔄 Iniciando reoferta para turno {turno_cancelado.id}")
            
            # Verificar configuración
            config = ConfiguracionReoferta.get_configuracion()
            if not config.activo:
                logger.info("⏸️ Módulo de reoferta desactivado")
                return False
            
            # Buscar interesados (FIFO)
            interesados = ReofertaAutomaticaService._obtener_interesados_fifo(turno_cancelado)
            
            if not interesados:
                logger.info("ℹ️ No hay interesados para notificar")
                return False
            
            logger.info(f"📋 {len(interesados)} interesados encontrados para turno {turno_cancelado.id}")
            
            # Procesar notificaciones en orden FIFO
            for interesado in interesados:
                resultado = ReofertaAutomaticaService._notificar_cliente(
                    interesado, turno_cancelado, config
                )
                
                if resultado:
                    logger.info(f"✅ Cliente {interesado.cliente.nombre} aceptó la oferta")
                    return True
                else:
                    logger.info(f"⏭️ Cliente {interesado.cliente.nombre} no respondió, siguiente...")
            
            logger.info("❌ Ningún cliente aceptó la oferta")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error en procesar_reoferta: {str(e)}")
            return False
    
    @staticmethod
    def _obtener_interesados_fifo(turno_cancelado):
        """
        Obtiene clientes interesados en orden FIFO para el turno cancelado
        """
        from .models import InteresTurnoLiberado
        
        # Buscar interesados que coincidan con el peluquero, fecha y hora
        interesados = InteresTurnoLiberado.objects.filter(
            peluquero=turno_cancelado.peluquero,
            fecha_deseada=turno_cancelado.fecha,
            hora_deseada=turno_cancelado.hora,
            oferta_enviada=False,  # No notificados previamente
            oferta_aceptada=False  # No han aceptado previamente
        ).order_by('fecha_registro', 'prioridad')[:5]  # FIFO - primeros 5
        
        return list(interesados)
    
    @staticmethod
    def _notificar_cliente(interesado, turno_cancelado, config):
        """
        Notifica a un cliente específico y maneja su respuesta
        """
        from django.utils import timezone
        from .models import InteresTurnoLiberado, Turno
        
        try:
            # Calcular precio con descuento
            precio_original = interesado.servicio.precio
            descuento = config.descuento_por_defecto
            precio_con_descuento = precio_original * (1 - descuento / 100)
            
            # Marcar como notificado
            interesado.oferta_enviada = True
            interesado.fecha_oferta_enviada = timezone.now()
            interesado.descuento_aplicado = descuento
            interesado.tiempo_limite_respuesta = config.tiempo_limite_respuesta
            interesado.save()
            
            # Enviar notificación
            notificacion_enviada = ReofertaAutomaticaService._enviar_notificacion(
                interesado, turno_cancelado, precio_original, precio_con_descuento, config
            )
            
            if notificacion_enviada:
                # Simular espera de respuesta (en producción sería asíncrono)
                # Por ahora, simulamos que el primer cliente siempre acepta
                return ReofertaAutomaticaService._simular_respuesta_cliente(
                    interesado, turno_cancelado
                )
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error notificando cliente {interesado.id}: {str(e)}")
            return False
    
    @staticmethod
    def _enviar_notificacion(interesado, turno_cancelado, precio_original, precio_con_descuento, config):
        """
        Envía la notificación al cliente (email, WhatsApp, etc.)
        """
        try:
            cliente = interesado.cliente
            peluquero = turno_cancelado.peluquero
            
            # Información para la notificación
            info_turno = {
                'fecha': turno_cancelado.fecha.strftime("%d/%m/%Y"),
                'hora': turno_cancelado.hora.strftime("%H:%M"),
                'peluquero': f"{peluquero.nombre} {peluquero.apellido}",
                'servicio': interesado.servicio.nombre,
                'precio_original': float(precio_original),
                'precio_descuento': float(precio_con_descuento),
                'descuento': float(interesado.descuento_aplicado),
                'tiempo_limite': interesado.tiempo_limite_respuesta
            }
            
            # Log de la notificación (en producción enviarías email/WhatsApp real)
            logger.info(f"📧 NOTIFICACIÓN ENVIADA A: {cliente.nombre} ({cliente.correo})")
            logger.info(f"   📅 Turno: {info_turno['fecha']} {info_turno['hora']}")
            logger.info(f"   💇 Peluquero: {info_turno['peluquero']}")
            logger.info(f"   ✂️ Servicio: {info_turno['servicio']}")
            logger.info(f"   💰 Precio original: ${info_turno['precio_original']}")
            logger.info(f"   🔥 Precio con {info_turno['descuento']}% descuento: ${info_turno['precio_descuento']}")
            logger.info(f"   ⏰ Tiempo límite: {info_turno['tiempo_limite']} minutos")
            
            # Aquí integrarías:
            if config.notificar_email:
                ReofertaAutomaticaService._enviar_email(cliente, info_turno)
            
            if config.notificar_whatsapp:
                ReofertaAutomaticaService._enviar_whatsapp(cliente, info_turno)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando notificación: {str(e)}")
            return False
    
    @staticmethod
    def _enviar_email(cliente, info_turno):
        """Integración con envío de email"""
        try:
            # Usar Django send_mail o tu servicio de email
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"¡Oferta especial! Turno disponible para {info_turno['fecha']} {info_turno['hora']}"
            message = f"""
            Hola {cliente.nombre},
            
            Tenemos una oferta especial para ti. Se ha liberado un turno:
            
            📅 Fecha: {info_turno['fecha']}
            ⏰ Hora: {info_turno['hora']}
            💇 Peluquero: {info_turno['peluquero']}
            ✂️ Servicio: {info_turno['servicio']}
            
            💰 Precio regular: ${info_turno['precio_original']}
            🔥 Precio con descuento: ${info_turno['precio_descuento']} ({info_turno['descuento']}% OFF)
            
            ⏰ Tienes {info_turno['tiempo_limite']} minutos para confirmar este turno.
            
            ¡No pierdas esta oportunidad!
            
            Saludos,
            El equipo de HairSoft
            """
            
            # Descomentar cuando configures email
            # send_mail(
            #     subject,
            #     message,
            #     settings.DEFAULT_FROM_EMAIL,
            #     [cliente.correo],
            #     fail_silently=False,
            # )
            
            logger.info(f"📧 Email simulado para {cliente.correo}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {str(e)}")
            return False
    
    @staticmethod
    def _enviar_whatsapp(cliente, info_turno):
        """Integración con WhatsApp (usando Twilio u otro servicio)"""
        try:
            # Ejemplo con Twilio (descomentar cuando configures)
            # from twilio.rest import Client
            
            mensaje = f"""
¡Oferta especial! 🎉

Se liberó un turno para {info_turno['fecha']} a las {info_turno['hora']} con {info_turno['peluquero']}.

Servicio: {info_turno['servicio']}
Precio regular: ${info_turno['precio_original']}
🔥 OFERTA: ${info_turno['precio_descuento']} ({info_turno['descuento']}% OFF)

Tienes {info_turno['tiempo_limite']} minutos para confirmar.

Responde SI para aceptar.
            """
            
            logger.info(f"📱 WhatsApp simulado para {cliente.telefono}")
            logger.info(f"   Mensaje: {mensaje}")
            
            # Código real para Twilio:
            # account_sid = 'your_account_sid'
            # auth_token = 'your_auth_token'
            # client = Client(account_sid, auth_token)
            # 
            # message = client.messages.create(
            #     body=mensaje,
            #     from_='whatsapp:+14155238886',
            #     to=f'whatsapp:{cliente.telefono}'
            # )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando WhatsApp: {str(e)}")
            return False
    
    @staticmethod
    def _simular_respuesta_cliente(interesado, turno_cancelado):
        """
        Simula la respuesta del cliente (en producción esto vendría de webhooks)
        Por ahora, el primer cliente siempre acepta
        """
        from django.utils import timezone
        from .models import Turno
        
        try:
            # Simular aceptación (en producción esto sería por webhook)
            interesado.oferta_aceptada = True
            interesado.fecha_respuesta = timezone.now()
            interesado.save()
            
            # Crear nuevo turno para el cliente
            nuevo_turno = Turno.objects.create(
                fecha=turno_cancelado.fecha,
                hora=turno_cancelado.hora,
                estado='RESERVADO',
                canal='WEB',
                tipo_pago='PENDIENTE',
                medio_pago='PENDIENTE',
                monto_seña=0,
                monto_total=turno_cancelado.monto_total * (1 - interesado.descuento_aplicado / 100),
                cliente=interesado.cliente,
                peluquero=turno_cancelado.peluquero
            )
            
            # Copiar servicios del turno cancelado
            nuevo_turno.servicios.set(turno_cancelado.servicios.all())
            
            logger.info(f"✅ Nuevo turno {nuevo_turno.id} creado para {interesado.cliente.nombre}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando nuevo turno: {str(e)}")
            return False

# Integrar con el TurnoService existente
class TurnoService:
    # ... métodos existentes ...
    
    @staticmethod
    def procesar_reoferta_automatica(turno_id):
        """
        Método público para procesar reoferta automática
        """
        try:
            turno = Turno.objects.get(id=turno_id)
            
            # Solo procesar turnos web cancelados
            if turno.estado == 'CANCELADO' and turno.canal == 'WEB':
                return ReofertaAutomaticaService.procesar_reoferta(turno)
            
            return False
            
        except Turno.DoesNotExist:
            logger.error(f"❌ Turno {turno_id} no encontrado para reoferta")
            return False