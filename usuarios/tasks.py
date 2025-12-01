from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import time
import secrets
from django.db.models import Max, Q 
from django.conf import settings

from .models import (
    Turno, 
    InteresTurnoLiberado, 
    ConfiguracionReoferta, 
    Cotizacion, 
    PromocionReactivacion, 
    Usuario,
    Producto, 
    SolicitudPresupuesto
)

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. TAREAS DE ENVÍO (Auxiliares)
# ==============================================================================

@shared_task
def enviar_whatsapp_oferta(numero, mensaje):
    """Envía WhatsApp vía Twilio"""
    try:
        from twilio.rest import Client
        
        account_sid = settings.TWILIO_ACCOUNT_SID 
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER 
        to_whatsapp_number = f'whatsapp:{numero}'
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=mensaje, from_=from_whatsapp_number, to=to_whatsapp_number)
        print(f"✅ WhatsApp enviado a {numero}. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Error Twilio: {str(e)}")
        return False

@shared_task
def enviar_email_oferta(email, mensaje, fecha, hora):
    """Envía Email (usado en reoferta de turnos)"""
    try:
        from django.core.mail import send_mail
        subject = f"¡Turno disponible! {fecha} {hora} - HairSoft"
        send_mail(subject, mensaje, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False

@shared_task
def enviar_email_cotizacion_proveedor(cotizacion_id):
    """Envía solicitud de presupuesto a proveedores"""
    try:
        from django.core.mail import send_mail
        
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        if not cotizacion.proveedor.email: return False

        link = f"http://localhost:5173/proveedor/cotizar/{cotizacion.token}"
        mensaje = f"""
Estimado {cotizacion.proveedor.nombre},
Requerimos presupuesto para: {cotizacion.solicitud.producto.nombre} (Cant: {cotizacion.solicitud.cantidad_requerida}).
Ingrese su oferta aquí: {link}
        """
        send_mail(
            f"Solicitud de Cotización #{cotizacion.solicitud.id}", 
            mensaje, 
            settings.DEFAULT_FROM_EMAIL, 
            [cotizacion.proveedor.email], 
            fail_silently=False
        )
        print(f"📧 Email enviado a proveedor {cotizacion.proveedor.nombre}")
        return True
    except Exception as e:
        print(f"❌ Error email proveedor: {str(e)}")
        return False


# ==============================================================================
# 2. TAREAS DE NEGOCIO 
# ==============================================================================

@shared_task
def procesar_reoferta_masiva(turno_id):
    try:
        turno = Turno.objects.get(id=turno_id)
        if not turno.oferta_activa or turno.estado != 'CANCELADO': return False
        
        interesados = turno.obtener_interesados()
        if not interesados.exists():
            turno.estado = 'DISPONIBLE'; turno.oferta_activa = False; turno.save()
            return True
        
        for interes in interesados:
            interes.turno_liberado = turno; interes.save()
            link = f"http://localhost:5173/aceptar-oferta/{turno.id}/{interes.token_oferta}"
            msg = f"*¡TURNO DISPONIBLE!* 🎁\n{turno.fecha} {turno.hora}\nReservá acá: {link}"
            if interes.cliente.telefono: enviar_whatsapp_oferta.delay(interes.cliente.telefono, msg)
            interes.marcar_enviada()
        return True
    except Exception as e:
        print(f"❌ Error reoferta: {e}")
        return False

@shared_task
def notificar_turno_asignado(turno_id):
    try:
        turno = Turno.objects.get(id=turno_id)
        perdieron = InteresTurnoLiberado.objects.filter(turno_liberado=turno, estado_oferta='enviada').exclude(cliente=turno.cliente)
        msg = f"❌ El turno del {turno.fecha} ya fue tomado."
        for p in perdieron:
            p.rechazar_oferta()
            if p.cliente.telefono: enviar_whatsapp_oferta.delay(p.cliente.telefono, msg)
        return True
    except Exception: return False


# ==============================================================================
# 3. MÓDULO DE FIDELIZACIÓN: REACTIVACIÓN AUTOMÁTICA (VERSIÓN FINAL REAL)
# ==============================================================================

@shared_task
def procesar_reactivacion_clientes_inactivos():
    """
    Tarea DIARIA REAL:
    1. Busca clientes cuyo último turno fue hace más de 60 días.
    2. Respeta el cooldown de 90 días.
    3. Envía cupón de 15% OFF.
    """
    print("🕵️‍♂️ [FIDELIZACIÓN] Iniciando análisis diario de clientes inactivos...")
    
    DIAS_INACTIVIDAD = 60
    DIAS_VALIDEZ = 7
    DIAS_COOLDOWN = 90
    
    hoy = timezone.now()
    # Fecha límite: Todo turno ANTERIOR a esto es "viejo"
    fecha_limite = hoy - timedelta(days=DIAS_INACTIVIDAD)
    fecha_limite_cooldown = hoy - timedelta(days=DIAS_COOLDOWN)
    
    # Traemos clientes y la fecha de su último turno
    clientes = Usuario.objects.filter(rol__nombre__iexact='Cliente').annotate(
        ultimo_turno=Max('turnos_cliente__fecha')
    )
    
    enviados = 0
    
    for cliente in clientes:
        # 1. Si nunca vino, no es reactivación
        if not cliente.ultimo_turno: 
            continue 

        # 2. FILTRO DE FECHA REAL
        # Si su último turno fue DESPUÉS de la fecha límite (ej: vino ayer), es ACTIVO -> Ignorar
        ultimo_turno_dt = timezone.make_aware(datetime.combine(cliente.ultimo_turno, datetime.min.time()))
        
        if ultimo_turno_dt >= fecha_limite:
            # Vino hace poco, no molestar
            continue 

        # 3. Filtro Anti-Spam (Ya tiene promo activa o reciente?)
        promo_reciente = PromocionReactivacion.objects.filter(
            cliente=cliente,
            fecha_creacion__gte=fecha_limite_cooldown
        ).exists()

        if promo_reciente:
            continue

        try:
            if not cliente.telefono: continue

            codigo = f"VOLVE-{secrets.token_hex(2).upper()}"
            vencimiento = hoy + timedelta(days=DIAS_VALIDEZ)
            
            PromocionReactivacion.objects.create(
                cliente=cliente, codigo=codigo, fecha_vencimiento=vencimiento
            )
            
            link = f"http://localhost:5173/turnos/crear-web?cup={codigo}"
            
            mensaje = (
                f"👋 ¡Hola {cliente.nombre}!\n\n"
                f"Te extrañamos en Los Ultimos Serán Los Primeros ✂️.\n\n"
                f"🎁 *15% OFF en tu próximo servicio*\n"
                f"Válido por 7 días.\n\n"
                f"Reservá acá con el descuento ya aplicado:\n"
                f"{link}\n\n"
                f"¡Te esperamos!"
            )
            
            enviar_whatsapp_oferta.delay(cliente.telefono, mensaje)
            print(f"   🚀 Cupón enviado a {cliente.nombre} (Inactivo desde {cliente.ultimo_turno})")
            enviados += 1
            time.sleep(2)

        except Exception as e:
            print(f"Error con cliente {cliente.nombre}: {e}")

    return f"Proceso real finalizado. {enviados} enviados."