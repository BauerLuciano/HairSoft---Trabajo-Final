# ARCHIVO: usuarios/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging
from .models import Turno, InteresTurnoLiberado, ConfiguracionReoferta, Cotizacion
import requests
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. TAREAS DE ENVÍO
# ==============================================================================
@shared_task
def enviar_whatsapp_oferta(numero, mensaje):
    """
    Envía el mensaje de WhatsApp usando las credenciales de settings.py
    """
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID 
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER # Usamos el de settings
        
        # Formateo básico para asegurar compatibilidad
        to_whatsapp_number = f'whatsapp:{numero}'
        
        print("=" * 60)
        print(f"🚀 ENVIANDO WHATSAPP...")
        print(f"➡️ De: {from_whatsapp_number}")
        print(f"➡️ A: {to_whatsapp_number}")
        print("=" * 60)
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=mensaje,
            from_=from_whatsapp_number,
            to=to_whatsapp_number
        )
        
        print(f"✅ MENSAJE ENVIADO. SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR TWILIO: {str(e)}")
        return False

@shared_task
def enviar_email_oferta(email, mensaje, fecha, hora):
    try:
        subject = f"¡Turno disponible! {fecha} {hora} - HairSoft"
        send_mail(
            subject=subject,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False

@shared_task
def enviar_oferta_individual(interes_id, turno_id):
    """
    Construye el link y manda la oferta a un interesado específico.
    """
    try:
        config = ConfiguracionReoferta.get_configuracion()
        interes = InteresTurnoLiberado.objects.get(id=interes_id)
        turno = Turno.objects.get(id=turno_id)
        
        # Vincular el interés al turno actual
        interes.turno_liberado = turno
        interes.save()
        
        # ✅✅✅ AQUÍ ESTÁ LA MAGIA: TU IP REAL Y PUERTO VITE (5173)
        # Esto hace que el celular abra tu página de Vue
        base_url = "http://localhost:5173" 
        
        # Construimos el link limpio
        link = f"{base_url}/aceptar-oferta/{turno.id}/{interes.token_oferta}"
        
        mensaje = f"""
*¡HOLA! TENEMOS UNA OFERTA PARA VOS* 🎁

Se liberó un turno para el *{turno.fecha.strftime('%d/%m')}* a las *{turno.hora.strftime('%H:%M')} hs*.
💈 *Profesional:* {turno.peluquero.nombre} {turno.peluquero.apellido}

👇 *TOCÁ EL LINK PARA ACEPTAR:*
{link}

⚠️ _Si el link no funciona, respondé "HOLA" a este mensaje y probá de nuevo._
"""
        
        # Enviar WhatsApp
        if config.notificar_whatsapp and interes.cliente.telefono:
            enviar_whatsapp_oferta(interes.cliente.telefono, mensaje)
        
        # Enviar Email
        if config.notificar_email and interes.cliente.correo: 
            enviar_email_oferta(
                interes.cliente.correo, 
                mensaje, 
                turno.fecha.strftime('%d/%m'),
                turno.hora.strftime('%H:%M')
            )
        
        # Marcar como enviada en la BD
        interes.marcar_enviada()
        return True
        
    except Exception as e:
        print(f"❌ ERROR en enviar_oferta_individual: {str(e)}")
        return False

# ==============================================================================
# 2. LOGICA DE REOFERTA MASIVA
# ==============================================================================
@shared_task
def procesar_reoferta_masiva(turno_id):
    try:
        turno = Turno.objects.get(id=turno_id)
        
        if not turno.oferta_activa or turno.estado != 'CANCELADO':
            return False
        
        interesados = turno.obtener_interesados()
        
        if not interesados.exists():
            print(f"ℹ️ No hay interesados para el turno {turno_id}")
            # Si no hay nadie, lo dejamos disponible para cualquiera
            turno.estado = 'DISPONIBLE' 
            turno.oferta_activa = False
            turno.save()
            return True
        
        print(f"🚀 Iniciando reoferta para {interesados.count()} personas...")
        
        for interes in interesados:
            enviar_oferta_individual(interes.id, turno_id)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en reoferta masiva: {str(e)}")
        return False

# ==============================================================================
# 3. OTRAS TAREAS DE MANTENIMIENTO
# ==============================================================================
@shared_task
def notificar_turno_asignado(turno_id):
    """Avisa a los que llegaron tarde que el turno ya fue tomado"""
    try:
        turno = Turno.objects.get(id=turno_id)
        
        # Buscar a los que se les envió oferta pero NO son el cliente que ganó
        perdieron = InteresTurnoLiberado.objects.filter(
            turno_liberado=turno,
            estado_oferta='enviada'
        ).exclude(cliente=turno.cliente)
        
        mensaje_triste = f"❌ El turno del {turno.fecha.strftime('%d/%m')} ya fue tomado por otra persona. ¡La próxima será!"
        
        for p in perdieron:
            p.rechazar_oferta()
            if p.cliente.telefono:
                enviar_whatsapp_oferta.delay(p.cliente.telefono, mensaje_triste)
                
        return True
    except Exception:
        return False

@shared_task
def expirar_reoferta(turno_id):
    pass # Simplificado para que no de error si se llama


#PROVEEDORES Y COTIZACIONES

@shared_task
def enviar_email_cotizacion_proveedor(cotizacion_id):
    try:
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        if not cotizacion.proveedor.email:
            return False

        # Link al frontend público (ajusta tu URL base)
        link = f"http://localhost:5173/proveedor/cotizar/{cotizacion.token}"
        
        mensaje = f"""
        Estimado {cotizacion.proveedor.nombre},
        
        Desde HairSoft requerimos presupuesto para reponer stock:
        
        Producto: {cotizacion.solicitud.producto.nombre}
        Cantidad: {cotizacion.solicitud.cantidad_requerida} unidades.
        
        Por favor, ingrese su precio y tiempo de entrega aquí:
        {link}
        """
        
        send_mail(
            subject=f"Solicitud de Cotización #{cotizacion.solicitud.id}",
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cotizacion.proveedor.email]
        )
        return True
    except Exception as e:
        print(f"Error email proveedor: {e}")
        return False