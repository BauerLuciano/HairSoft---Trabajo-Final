from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import time
import secrets
import uuid
from django.db.models import Max, Q, F # <--- F es vital para comparar stock_actual vs stock_minimo
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
    try:
        from django.core.mail import send_mail
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        if not cotizacion.proveedor.email: return False

        # ✅ USANDO FRONTEND_URL
        link = f"{settings.FRONTEND_URL}/proveedor/cotizar/{cotizacion.token}"
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
        
        # Validaciones de estado
        if not turno.oferta_activa or turno.estado != 'CANCELADO': 
            return False
        
        interesados = turno.obtener_interesados()
        
        # Si no hay nadie esperando, liberamos el turno normal
        if not interesados.exists():
            turno.estado = 'CANCELADO' 
            turno.oferta_activa = False
            turno.save()
            return True
        
        # Enviar mensajes a los interesados
        for interes in interesados:
            interes.turno_liberado = turno
            interes.save()
            
            # ✅ USANDO FRONTEND_URL
            link = f"{settings.FRONTEND_URL}/aceptar-oferta/{turno.id}/{interes.token_oferta}"

            # ✅ LIMPIEZA DE FORMATO PARA WHATSAPP
            msg = (
                f"¡TURNO DISPONIBLE! 🎁\n"
                f"Hola {interes.cliente.nombre}, se liberó un lugar:\n\n"
                f"📅 {turno.fecha}\n"
                f"⏰ {turno.hora}\n\n"
                f"👇 Tocá el link para reservar con un 15% de descuento!:\n"
                f"{link}\n\n"
                f"Los Últimos Serán Los Primeros"
            )
            
            # Envío
            if interes.cliente.telefono: 
                enviar_whatsapp_oferta.delay(interes.cliente.telefono, msg)
            
            interes.marcar_enviada()
            
        return True

    except Exception as e:
        print(f"❌ Error reoferta masiva: {e}")
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
# 3. MÓDULO DE FIDELIZACIÓN
# ==============================================================================

@shared_task
def procesar_reactivacion_clientes_inactivos():
    print("🕵️‍♂️ [FIDELIZACIÓN] Iniciando análisis diario de clientes inactivos...")
    DIAS_INACTIVIDAD = 60
    DIAS_COOLDOWN = 90
    hoy = timezone.now()
    fecha_limite = hoy - timedelta(days=DIAS_INACTIVIDAD)
    fecha_limite_cooldown = hoy - timedelta(days=DIAS_COOLDOWN)
    
    clientes = Usuario.objects.filter(rol__nombre__iexact='Cliente').annotate(
        ultimo_turno=Max('turnos_cliente__fecha')
    )
    
    enviados = 0
    for cliente in clientes:
        if not cliente.ultimo_turno: continue 
        ultimo_turno_dt = timezone.make_aware(datetime.combine(cliente.ultimo_turno, datetime.min.time()))
        if ultimo_turno_dt >= fecha_limite: continue 

        if PromocionReactivacion.objects.filter(cliente=cliente, fecha_creacion__gte=fecha_limite_cooldown).exists():
            continue

        try:
            if not cliente.telefono: continue
            codigo = f"VOLVE-{secrets.token_hex(2).upper()}"
            PromocionReactivacion.objects.create(cliente=cliente, codigo=codigo, fecha_vencimiento=hoy + timedelta(days=7))
            
            # ✅ USANDO FRONTEND_URL
            mensaje = (
                f"👋 ¡Hola {cliente.nombre}!\n"
                f"Somos de la peluquería Los Ultimos Serán Los Primeros.\n"
                f"Te extrañamos ✂️. Reservá con 15% OFF acá:\n"
                f"{settings.FRONTEND_URL}/turnos/crear-web?cup={codigo}"
            )
            
            enviar_whatsapp_oferta.delay(cliente.telefono, mensaje)
            enviados += 1
            time.sleep(2)
        except Exception as e:
            print(f"Error con cliente {cliente.nombre}: {e}")
    return f"Fidelización: {enviados} enviados."

# ==============================================================================
# 4. MÓDULO DE INVENTARIO: REPOSICIÓN AUTOMÁTICA (DINÁMICO)
# ==============================================================================
@shared_task
def chequear_stock_y_generar_solicitudes():
    """
    Tarea Automática corregida para usar los modelos Reales:
    SolicitudReabastecimiento y CotizacionProveedor
    """
    print("📦 [INVENTARIO] Iniciando chequeo dinámico...")
    
    # Buscamos productos que necesiten reponer
    productos_bajo_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        estado='ACTIVO'
    )
    
    creadas = 0
    for producto in productos_bajo_stock:
        # Nota: Ajusté el nombre de los modelos según tu comentario de corrección
        # ✅ Supongo que existen SolicitudReabastecimiento y CotizacionProveedor
        from .models import SolicitudReabastecimiento, CotizacionProveedor
        
        if SolicitudReabastecimiento.objects.filter(producto=producto, estado='PENDIENTE').exists():
            continue
            
        try:
            cantidad_a_pedir = producto.lote_reposicion if producto.lote_reposicion >= 1 else 1
            
            solicitud = SolicitudReabastecimiento.objects.create(
                producto=producto,
                cantidad_solicitada=cantidad_a_pedir,
                estado='PENDIENTE'
            )
            
            proveedores = producto.proveedores.all()
            for proveedor in proveedores:
                CotizacionProveedor.objects.create(
                    solicitud=solicitud,
                    proveedor=proveedor,
                    token_acceso=uuid.uuid4()
                )
                
            print(f"   ✅ Solicitud #{solicitud.id} para {producto.nombre} generada por {cantidad_a_pedir} u.")
            creadas += 1
        except Exception as e:
            print(f"❌ Error en reposición {producto.nombre}: {e}")

    return f"Proceso finalizado. {creadas} reabastecimientos iniciados."