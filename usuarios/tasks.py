# usuarios/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import time
import secrets
import uuid
from django.db.models import Max, Q, F 
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
    """Envía WhatsApp vía Twilio - Versión SÍNCRONA"""
    try:
        from twilio.rest import Client
        
        account_sid = settings.TWILIO_ACCOUNT_SID 
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER 
        to_whatsapp_number = f'whatsapp:{numero}'
        
        print(f"    📲 Conectando a Twilio...")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=mensaje, 
            from_=from_whatsapp_number, 
            to=to_whatsapp_number
        )
        print(f"    ✅ Twilio OK - SID: {message.sid[:20]}...")
        return True
    except Exception as e:
        print(f"    ❌ Error Twilio: {str(e)}")
        return False  # ¡IMPORTANTE! Retorna False, NO lanza excepción
    
@shared_task
def enviar_email_oferta(email, mensaje, fecha, hora):
    try:
        from django.core.mail import send_mail
        subject = f"¡Turno disponible! {fecha} {hora} - HairSoft"
        send_mail(subject, mensaje, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"❌ Error enviando email: {str(e)}")
        return False

@shared_task
def enviar_email_cotizacion_proveedor(cotizacion_id):
    try:
        from django.core.mail import send_mail
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        if not cotizacion.proveedor.email: 
            return False

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
        logger.info(f"📧 Email enviado a proveedor {cotizacion.proveedor.nombre}")
        return True
    except Exception as e:
        logger.error(f"❌ Error email proveedor: {str(e)}")
        return False

# ==============================================================================
# 2. TAREAS DE NEGOCIO - VERSIÓN CORREGIDA
# ==============================================================================

@shared_task
def procesar_reoferta_masiva(turno_id):
    """
    🔥 VERSIÓN COMPLETAMENTE CORREGIDA: 
    - Eliminado raw SQL (causaba error "no existe la relación «usuarios_turno»")
    - Usa ORM normal de Django
    - Verifica token y envía WhatsApps
    """
    try:
        # 🔥 CORRECCIÓN CRÍTICA: Usar ORM normal, NO raw SQL
        # Error original: turno = Turno.objects.raw('SELECT * FROM usuarios_turno WHERE id = %s', [turno_id])[0]
        turno = Turno.objects.get(id=turno_id)
        
        # Validaciones de estado
        if turno.estado != 'CANCELADO': 
            logger.warning(f"⚠️ Turno {turno_id} no está cancelado. Estado: {turno.estado}")
            return False
        
        # 🔥 VERIFICACIÓN CRÍTICA: Token DEBE existir
        if not turno.token_reoferta:
            logger.error(f"🚨 ERROR CRÍTICO: Turno {turno_id} NO tiene token en DB")
            # Generar token de emergencia
            turno.token_reoferta = str(uuid.uuid4())
            # Guardar SOLO el token sin afectar otros campos
            Turno.objects.filter(id=turno.id).update(token_reoferta=turno.token_reoferta)
            logger.warning(f"⚠️ Token de emergencia generado: {turno.token_reoferta}")
        
        # Obtener interesados que están en estado 'preparando' (marcados por el Service)
        interesados = InteresTurnoLiberado.objects.filter(
            turno_liberado=turno,
            estado_oferta='preparando'
        ).order_by('fecha_registro')
        
        if not interesados.exists():
            logger.info(f"📭 No hay interesados en estado 'preparando' para turno {turno_id}")
            # Intentar con 'pendiente' como fallback
            interesados = InteresTurnoLiberado.objects.filter(
                peluquero=turno.peluquero,
                fecha_deseada=turno.fecha,
                hora_deseada=turno.hora,
                estado_oferta='pendiente'
            ).order_by('fecha_registro')
        
        if not interesados.exists():
            logger.info(f"📭 No hay interesados para turno {turno_id}")
            return True
        
        logger.info(f"📨 Enviando ofertas a {interesados.count()} interesados para turno {turno_id}")
        
        # 🔥 BASE_URL para los links (usa FRONTEND_URL de settings o fallback)
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        
        # Enviar mensajes a los interesados
        for interes in interesados:
            try:
                # Actualizar a 'enviada' ANTES de enviar
                interes.estado_oferta = 'enviada'
                interes.turno_liberado = turno
                interes.save(update_fields=['estado_oferta', 'turno_liberado'])
                
                # 🔥 Generar link con el token (que DEBERÍA existir)
                link = f"{base_url}/aceptar-oferta/{turno.id}/{turno.token_reoferta}"

                msg = (
                    f"¡TURNO DISPONIBLE! 🎁\n"
                    f"Hola {interes.cliente.nombre}, se liberó un lugar:\n\n"
                    f"📅 {turno.fecha}\n"
                    f"⏰ {turno.hora}\n\n"
                    f"👇 Tocá el link para reservar con un 15% de descuento!:\n"
                    f"{link}\n\n"
                    f"Los Últimos Serán Los Primeros"
                )
                
                # 🔥 ENVIAR WHATSAPP REALMENTE (antes solo se programaba)
                if interes.cliente.telefono: 
                    # Llamar DIRECTAMENTE a la función (no .delay()) para asegurar envío
                    # O usar .apply_async() con retry
                    try:
                        result = enviar_whatsapp_oferta.apply_async(
                            args=[interes.cliente.telefono, msg],
                            retry=True,
                            retry_policy={
                                'max_retries': 3,
                                'interval_start': 2,
                                'interval_step': 2,
                                'interval_max': 10,
                            }
                        )
                        logger.info(f"📱 WhatsApp ENVIADO para {interes.cliente.nombre} - Tel: {interes.cliente.telefono}")
                    except Exception as e:
                        logger.error(f"❌ Error programando WhatsApp: {str(e)}")
                        # Intento directo como fallback
                        enviar_whatsapp_oferta(interes.cliente.telefono, msg)
                
                # Pequeña pausa para no saturar Twilio
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error con interesado {interes.id}: {str(e)}")
                continue
        
        logger.info(f"✅ Reoferta masiva COMPLETADA para turno {turno_id}")
        return True

    except Turno.DoesNotExist:
        logger.error(f"❌ Turno {turno_id} no encontrado en tarea de reoferta")
        return False
    except Exception as e:
        logger.error(f"❌ Error crítico en reoferta masiva: {e}", exc_info=True)
        return False

@shared_task
def notificar_turno_asignado(turno_id):
    try:
        turno = Turno.objects.get(id=turno_id)
        # Ajustado filtro para usar estado_oferta si existe, sino lo que tenías
        perdieron = InteresTurnoLiberado.objects.filter(turno_liberado=turno).exclude(cliente=turno.cliente)
        msg = f"❌ El turno del {turno.fecha} ya fue tomado."
        for p in perdieron:
            # Asumiendo métodos, si no existen los comentamos o ajustamos
            if hasattr(p, 'rechazar_oferta'): 
                p.rechazar_oferta()
            if p.cliente.telefono: 
                enviar_whatsapp_oferta.delay(p.cliente.telefono, msg)
        return True
    except Exception as e:
        logger.error(f"❌ Error notificando turno asignado: {e}")
        return False

# ==============================================================================
# 3. MÓDULO DE FIDELIZACIÓN
# ==============================================================================

@shared_task
def procesar_reactivacion_clientes_inactivos():
    logger.info("🕵️‍♂️ [FIDELIZACIÓN] Iniciando análisis diario de clientes inactivos...")
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
        if not cliente.ultimo_turno: 
            continue 
        
        ultimo_turno_dt = timezone.make_aware(datetime.combine(cliente.ultimo_turno, datetime.min.time()))
        if ultimo_turno_dt >= fecha_limite: 
            continue 

        if PromocionReactivacion.objects.filter(cliente=cliente, fecha_creacion__gte=fecha_limite_cooldown).exists():
            continue

        try:
            if not cliente.telefono: 
                continue
            
            codigo = f"VOLVE-{secrets.token_hex(2).upper()}"
            PromocionReactivacion.objects.create(
                cliente=cliente, 
                codigo=codigo, 
                fecha_vencimiento=hoy + timedelta(days=7)
            )
            
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
            logger.error(f"❌ Error con cliente {cliente.nombre}: {e}")
    
    logger.info(f"✅ Fidelización: {enviados} enviados.")
    return f"Fidelización: {enviados} enviados."

# ==============================================================================
# 4. MÓDULO DE INVENTARIO: REPOSICIÓN AUTOMÁTICA (DINÁMICO)
# ==============================================================================
@shared_task
def chequear_stock_y_generar_solicitudes():
    logger.info("📦 [INVENTARIO] Iniciando chequeo dinámico...")
    
    productos_bajo_stock = Producto.objects.filter(
        stock_actual__lte=F('stock_minimo'),
        estado='ACTIVO'
    )
    
    creadas = 0
    for producto in productos_bajo_stock:
        try:
            # Importación local para evitar ciclos
            from .models import SolicitudReabastecimiento, CotizacionProveedor
            
            if SolicitudReabastecimiento.objects.filter(producto=producto, estado='PENDIENTE').exists():
                continue
            
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
                
            logger.info(f"✅ Solicitud #{solicitud.id} para {producto.nombre} generada por {cantidad_a_pedir} u.")
            creadas += 1
        except Exception as e:
            logger.error(f"❌ Error en reposición {producto.nombre}: {e}")

    logger.info(f"✅ Proceso finalizado. {creadas} reabastecimientos iniciados.")
    return f"Proceso finalizado. {creadas} reabastecimientos iniciados."

# ==============================================================================
# 5. TAREAS PERIÓDICAS DE MANTENIMIENTO
# ==============================================================================
@shared_task
def limpiar_tokens_expirados():
    """Limpia tokens de reoferta con más de 48 horas"""
    try:
        from django.utils import timezone
        from datetime import timedelta
        from .models import Turno
        
        limite = timezone.now() - timedelta(hours=48)
        expirados = Turno.objects.filter(
            estado='CANCELADO',
            token_reoferta__isnull=False,
            fecha_modificacion__lt=limite
        )
        
        count = expirados.count()
        expirados.update(token_reoferta=None)
        
        logger.info(f"🧹 Limpiados {count} tokens expirados")
        return f"Tokens limpiados: {count}"
    except Exception as e:
        logger.error(f"❌ Error limpiando tokens: {e}")
        return "Error"