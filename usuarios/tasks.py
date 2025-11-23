from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from .models import Turno, InteresTurnoLiberado, ConfiguracionReoferta
import requests
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. TAREAS DE ENVÍO (Definidas primero)
# ==============================================================================
@shared_task
def enviar_whatsapp_oferta(numero, mensaje):
    """
    Envío de WhatsApp con Twilio. 
    AHORA ENVÍA EL MENSAJE DINÁMICO (REAL).
    """
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID 
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        # MANTENEMOS ESTO HARCODEADO PORQUE FUNCIONÓ
        from_whatsapp_number = 'whatsapp:+14155238886' 
        
        # MANTENEMOS EL FORMATO +54 9
        to_whatsapp_number = f'whatsapp:{numero}'
        
        print("=" * 60)
        print(f"🚀 ENVIANDO DESDE: {from_whatsapp_number}")
        print(f"🚀 ENVIANDO HACIA: {to_whatsapp_number}")
        print(f"📝 CONTENIDO: {mensaje[:50]}...") # Imprimimos el inicio del mensaje para chequear
        print("=============================================================")
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=mensaje,  # <--- 🚨 ACÁ ESTÁ EL CAMBIO (Usamos la variable real)
            from_=from_whatsapp_number,
            to=to_whatsapp_number
        )
        
        print("✅ TWILIO ACEPTÓ LA SOLICITUD.")
        print(f"📨 MESSAGE SID: {message.sid}")
        print("-------------------------------------------------------------")
        return True
        
    except Exception as e:
        error_msg = f"❌ ERROR CRÍTICO TWILIO EN CONEXIÓN: {str(e)}"
        print(error_msg)
        return False

@shared_task
def enviar_email_oferta(email, mensaje, fecha, hora):
    """
    Envía oferta por email
    """
    try:
        subject = f"¡Turno disponible! {fecha} {hora} - HairSoft"
        
        send_mail(
            subject=subject,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Email enviado a {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email: {str(e)}")
        return False

@shared_task
def enviar_oferta_individual(interes_id, turno_id):
    """
    Coordina el envío individual.
    """
    try:
        config = ConfiguracionReoferta.get_configuracion()
        
        print(f"🚀 EJECUTANDO enviar_oferta_individual para interes {interes_id}, turno {turno_id}")
        
        interes = InteresTurnoLiberado.objects.get(id=interes_id)
        turno = Turno.objects.get(id=turno_id)
        
        # Asignar turno
        interes.turno_liberado = turno
        interes.save()
        
        enlace_aceptacion = f"http://localhost:8000/usuarios/api/turnos/{turno.id}/aceptar-oferta/{interes.token_oferta}/"
        
        mensaje = f"""
¡TURNO DISPONIBLE! 🎉

📅 Fecha: {turno.fecha.strftime('%d/%m')}
⏰ Hora: {turno.hora.strftime('%H:%M')} hs
💈 Profesional: {turno.peluquero.nombre} {turno.peluquero.apellido}
✂️ Servicio: {interes.servicio.nombre}

💰 Precio especial: ${interes.servicio.precio * (1 - interes.descuento_aplicado/100):.2f}
🎁 Descuento: {interes.descuento_aplicado}% OFF

⏳ Tenés hasta las {turno.fecha_expiracion_oferta.strftime('%H:%M')} para aceptarlo.
🚨 Primer cliente que confirme → se lo queda.

✅ Confirmar: {enlace_aceptacion}

No respondas a este mensaje.
"""
        
        print(f"📱 Preparando WhatsApp para {interes.cliente.nombre} - Tel: {interes.cliente.telefono}")
        
        # LOGICA DE ENVÍO WHATSAPP
        if config.notificar_whatsapp and interes.cliente.telefono:
            # Llamada directa
            enviar_whatsapp_oferta(interes.cliente.telefono, mensaje) 
        else:
            print(f"❌ WhatsApp no enviado - Config: {config.notificar_whatsapp}, Tel: {interes.cliente.telefono}")
        
        # LOGICA DE ENVÍO EMAIL
        if config.notificar_email and interes.cliente.correo: 
            enviar_email_oferta(
                interes.cliente.correo, 
                mensaje, 
                turno.fecha.strftime('%d/%m'),
                turno.hora.strftime('%H:%M')
            )
        
        # Marcar enviado
        interes.marcar_enviada()
        
        logger.info(f"Oferta enviada a {interes.cliente.nombre}")
        print(f"✅ OFERTA COMPLETADA para {interes.cliente.nombre}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando oferta individual: {str(e)}")
        print(f"❌ ERROR en enviar_oferta_individual: {str(e)}")
        return False

# ==============================================================================
# 2. TAREA PRINCIPAL
# ==============================================================================

@shared_task
def procesar_reoferta_masiva(turno_id):
    """
    Tarea principal
    """
    interesados = [] 
    try:
        turno = Turno.objects.get(id=turno_id)
        
        if not turno.oferta_activa or turno.estado != 'CANCELADO':
            logger.warning(f" {turno_id} no está listo para reoferta")
            return False
        
        interesados = turno.obtener_interesados()
        
        if not interesados.exists():
            logger.info(f"No hay interesados para turno {turno_id}")
            return True
        
        logger.info(f"Enviando ofertas a {interesados.count()} interesados para turno {turno_id}")
        
        for interes in interesados:
            enviar_oferta_individual(interes.id, turno_id)
        
        return True
        
    except Exception as e:
        logger.error(f"Error en procesar_reoferta_masiva: {str(e)}")
        print(f"❌ ERROR CRÍTICO EN PROCESAR REOFERTA: {str(e)}") 
        return False

# ==============================================================================
# 3. OTRAS TAREAS
# ==============================================================================

@shared_task
def expirar_reoferta(turno_id):
    try:
        turno = Turno.objects.get(id=turno_id)
        
        if turno.estado == 'CANCELADO' and turno.oferta_activa:
            turno.estado = 'DISPONIBLE'
            turno.oferta_activa = False
            turno.save()
            
            InteresTurnoLiberado.objects.filter(
                turno_liberado=turno,
                estado_oferta='enviada'
            ).update(estado_oferta='expirada')
            
            logger.info(f"Reoferta expirada para turno {turno_id}")
            notificar_expiracion_reoferta.delay(turno_id)
            
        return True
            
    except Exception as e:
        logger.error(f"Error expirando reoferta: {str(e)}")
        return False

@shared_task
def expirar_reoferta_sin_interesados(turno_id):
    try:
        turno = Turno.objects.get(id=turno_id)
        turno.estado = 'DISPONIBLE'
        turno.oferta_activa = False
        turno.save()
        logger.info(f"Turno {turno_id} marcado como disponible (sin interesados)")
        return True
    except Exception as e:
        logger.error(f"Error expirando reoferta sin interesados: {str(e)}")
        return False

@shared_task
def notificar_expiracion_reoferta(turno_id):
    logger.info(f"Notificando expiración de reoferta para turno {turno_id}")
    return True

@shared_task
def notificar_turno_asignado(turno_id):
    try:
        turno = Turno.objects.get(id=turno_id)
        
        interesados = InteresTurnoLiberado.objects.filter(
            turno_liberado=turno,
            estado_oferta='enviada'
        ).exclude(cliente=turno.cliente)
        
        mensaje_rechazo = f"""
ℹ️ El turno del {turno.fecha.strftime('%d/%m')} ya fue tomado.
"""
        
        for interes in interesados:
            interes.rechazar_oferta()
            if interes.cliente.telefono:
                enviar_whatsapp_oferta.delay(interes.cliente.telefono, mensaje_rechazo)
            
        logger.info(f"Notificaciones de rechazo enviadas para turno {turno_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error notificando turno asignado: {str(e)}")
        return False