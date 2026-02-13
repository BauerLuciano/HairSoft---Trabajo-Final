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

@shared_task(bind=True, max_retries=3)
def enviar_whatsapp_oferta(self, numero, mensaje):
    """
    Envía WhatsApp vía Twilio con mejor manejo de errores y logging
    """
    try:
        from twilio.rest import Client
        
        if not numero.startswith('+'):
            numero = f"+54{numero.lstrip('0')}"  # +5491134567890
        
        if len(numero) < 12:
            logger.error(f"❌ Número inválido: {numero}")
            return False
        
        account_sid = settings.TWILIO_ACCOUNT_SID 
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER 
        to_whatsapp_number = f'whatsapp:{numero}'
        
        logger.info(f"📲 Intentando enviar WhatsApp a {numero}")
        logger.info(f"   FROM: {from_whatsapp_number}")
        logger.info(f"   TO: {to_whatsapp_number}")
        logger.info(f"   MSG: {mensaje[:50]}...")
        
        if not account_sid or not auth_token:
            logger.error("❌ Credenciales Twilio no configuradas")
            return False
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=mensaje, 
            from_=from_whatsapp_number, 
            to=to_whatsapp_number
        )
        
        logger.info(f"✅ WhatsApp ENVIADO - SID: {message.sid}")
        logger.info(f"   Estado: {message.status}")
        
        return {
            'success': True,
            'message_sid': message.sid,
            'status': message.status,
            'to': numero
        }
        
    except Exception as e:
        logger.error(f"❌ Error Twilio: {str(e)}", exc_info=True)
        
        if any(err in str(e).lower() for err in ['timeout', 'connection', 'network']):
            try:
                self.retry(exc=e, countdown=60)
            except Exception as retry_error:
                logger.error(f"❌ Falló reintento: {retry_error}")
        
        return {
            'success': False,
            'error': str(e),
            'to': numero
        }
    
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
    """VERSIÓN NGROK - Linkeable 100%"""
    logger.info("🎯 [FIDELIZACIÓN] Iniciando proceso con Ngrok...")
    
    try:
        DIAS_INACTIVIDAD = 60
        DIAS_COOLDOWN = 90
        hoy = timezone.now()
        
        # 1. Buscamos clientes
        from django.db.models import Exists, OuterRef
        
        clientes_con_turnos = Usuario.objects.filter(
            rol__nombre__iexact='Cliente',
            telefono__isnull=False,
        ).exclude(telefono='').annotate(
            tiene_turnos=Exists(
                Turno.objects.filter(
                    cliente=OuterRef('pk'),
                    fecha__lt=hoy.date()
                )
            )
        ).filter(tiene_turnos=True)
        
        if clientes_con_turnos.count() == 0:
            logger.info("ℹ️ No hay clientes para procesar.")
            return "0 mensajes enviados"
        
        # 2. Filtrado de inactivos
        clientes_inactivos = []
        for cliente in clientes_con_turnos:
            ultimo_turno = Turno.objects.filter(
                cliente=cliente,
                estado__in=['COMPLETADO', 'RESERVADO']
            ).order_by('-fecha', '-hora').first()
            
            if not ultimo_turno: continue
            
            fecha_turno_naive = datetime.combine(ultimo_turno.fecha, ultimo_turno.hora)
            fecha_ultimo_turno = timezone.make_aware(fecha_turno_naive)
            dias_inactivo = (hoy - fecha_ultimo_turno).days
            
            if dias_inactivo <= DIAS_INACTIVIDAD: continue
            
            fecha_cooldown = hoy - timedelta(days=DIAS_COOLDOWN)
            if PromocionReactivacion.objects.filter(cliente=cliente, fecha_creacion__gte=fecha_cooldown).exists():
                continue
            
            clientes_inactivos.append({
                'cliente': cliente,
                'dias_inactivo': dias_inactivo,
                'ultima_visita': ultimo_turno.fecha
            })
        
        # 3. Preparar Envíos
        limite_diario = 15
        clientes_a_enviar = clientes_inactivos[:limite_diario]
        enviados = 0
        
        # 🔥🔥🔥 ACÁ ESTÁ LA SOLUCIÓN 🔥🔥🔥
        # Ponemos tu dirección de Ngrok explícitamente
        base_url = 'https://brandi-palmar-pickily.ngrok-free.dev'
        
        for info_cliente in clientes_a_enviar:
            cliente = info_cliente['cliente']
            dias_inactivo = info_cliente['dias_inactivo']
            
            try:
                codigo = f"VOLVE{secrets.token_hex(3).upper()}"
                
                # Formatear teléfono
                telefono = str(cliente.telefono).strip()
                if not telefono.startswith('+'):
                    if telefono.startswith('0'): telefono = telefono[1:]
                    telefono = f"+54{telefono}"
                
                # Link con Ngrok
                link = f"{base_url}/turnos/crear-web?cup={codigo}"
                
                # Mensaje
                mensaje = (
                    f"✂️ *¡TE EXTRAÑAMOS!* 💈\n\n"
                    f"Hola {cliente.nombre}, hace *{dias_inactivo} días* que no te vemos.\n\n"
                    f"🎁 *TENÉS UN 15% OFF DE REGALO*\n"
                    f"Reservá tu próximo turno tocando acá:\n\n"
                    f"{link}\n\n" 
                    f"🎫 Código: *{codigo}*\n"
                    f"⏳ Vence en 7 días"
                )
                
                # Enviar Twilio
                from twilio.rest import Client
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                
                message = client.messages.create(
                    body=mensaje,
                    from_=settings.TWILIO_WHATSAPP_NUMBER,
                    to=f'whatsapp:{telefono}'
                )
                
                # Guardar Promo
                PromocionReactivacion.objects.create(
                    cliente=cliente,
                    codigo=codigo,
                    descuento_porcentaje=15,
                    fecha_vencimiento=hoy + timedelta(days=7),
                    mensaje_sid=message.sid,
                    canal_envio='WHATSAPP'
                )
                
                enviados += 1
                logger.info(f"✅ Enviado a {cliente.nombre} con link Ngrok")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error enviando a {cliente.nombre}: {e}")
                continue
        
        return f"{enviados} mensajes enviados"
        
    except Exception as e:
        logger.error(f"🚨 Error General: {e}")
        return str(e)
    
#PROBANDO
@shared_task
def simular_reactivacion_clientes_inactivos():
    """VERSIÓN SIMULACIÓN - Muestra en terminal sin enviar mensajes reales"""
    logger.info("🎭 [SIMULACIÓN] Iniciando proceso SIN envíos reales")
    
    try:
        DIAS_INACTIVIDAD = 60
        DIAS_COOLDOWN = 90
        hoy = timezone.now()
        
        from django.db.models import Exists, OuterRef
        
        # Clientes con turnos en el pasado
        clientes_con_turnos = Usuario.objects.filter(
            rol__nombre__iexact='Cliente',
            telefono__isnull=False,
        ).exclude(telefono='').annotate(
            tiene_turnos=Exists(
                Turno.objects.filter(
                    cliente=OuterRef('pk'),
                    fecha__lt=hoy.date()
                )
            )
        ).filter(tiene_turnos=True)
        
        print(f"🎭 SIMULACIÓN - Clientes con turnos en el pasado: {clientes_con_turnos.count()}")
        
        if clientes_con_turnos.count() == 0:
            print("❌ No hay clientes con turnos en el pasado")
            return "0 clientes identificados"
        
        # Identificar inactivos
        clientes_inactivos = []
        
        for cliente in clientes_con_turnos:
            ultimo_turno = Turno.objects.filter(
                cliente=cliente,
                estado__in=['COMPLETADO', 'RESERVADO']
            ).order_by('-fecha', '-hora').first()
            
            if not ultimo_turno:
                continue
            
            fecha_turno_naive = datetime.combine(ultimo_turno.fecha, ultimo_turno.hora)
            fecha_ultimo_turno = timezone.make_aware(fecha_turno_naive)
            dias_inactivo = (hoy - fecha_ultimo_turno).days
            
            if dias_inactivo <= DIAS_INACTIVIDAD:
                continue
            
            fecha_cooldown = hoy - timedelta(days=DIAS_COOLDOWN)
            if PromocionReactivacion.objects.filter(
                cliente=cliente,
                fecha_creacion__gte=fecha_cooldown
            ).exists():
                print(f"   ⏳ {cliente.nombre}: Ya recibió promoción reciente")
                continue
            
            clientes_inactivos.append({
                'cliente': cliente,
                'dias_inactivo': dias_inactivo,
                'ultima_visita': ultimo_turno.fecha
            })
        
        print(f"🎭 SIMULACIÓN - Clientes INACTIVOS identificados: {len(clientes_inactivos)}")
        print("=" * 70)
        
        if len(clientes_inactivos) == 0:
            print("✅ No hay clientes que cumplan criterios")
            return "0 clientes identificados"
        
        # Mostrar detalles
        for idx, info in enumerate(clientes_inactivos, 1):
            cliente = info['cliente']
            print(f"\n{idx}. 👤 {cliente.nombre} {cliente.apellido}")
            print(f"   📱 Teléfono: {cliente.telefono}")
            print(f"   📅 Última visita: {info['ultima_visita']}")
            print(f"   ⏳ Días inactivo: {info['dias_inactivo']} días")
            
            # Generar código (solo para mostrar)
            codigo = f"VOLVE{secrets.token_hex(3).upper()}"
            print(f"   🎟️  Código generado: {codigo}")
            
            # Mostrar mensaje que se enviaría
            mensaje = (
                f"*¡TE EXTRAÑAMOS EN LA PELUQUERÍA!* ✂️💈\n\n"
                f"Hola {cliente.nombre},\n\n"
                f"Notamos que hace *{info['dias_inactivo']} días* que no nos visitás.\n\n"
                f"*🎁 TE REGALAMOS UN 15% DE DESCUENTO* en tu próximo turno.\n\n"
                f"👉 *CLICK PARA RESERVAR:*\n"
                f"https://tupeluqueria.com/turnos/crear-web?cup={codigo}\n\n"
                f"📱 *Código:* {codigo}\n\n"
                f"⏰ *Válido por 7 días*\n"
                f"📍 *Peluquería: Los Últimos Serán Los Primeros*"
            )
            
            print(f"   📤 MENSAJE QUE SE ENVIARÍA:")
            print(f"   {'─' * 50}")
            print(f"   {mensaje[:150]}...")
            print(f"   {'─' * 50}")
        
        print(f"\n🎭 RESUMEN SIMULACIÓN:")
        print(f"   • Total clientes con turnos: {clientes_con_turnos.count()}")
        print(f"   • Clientes inactivos (60+ días): {len(clientes_inactivos)}")
        print(f"   • Mensajes que se enviarían: {len(clientes_inactivos)}")
        print(f"\n⚠️  NOTA: Esto es una SIMULACIÓN. No se enviaron mensajes reales.")
        print(f"   Para enviar realmente, usa la función real mañana.")
        
        return f"SIMULACIÓN: {len(clientes_inactivos)} clientes inactivos identificados"
        
    except Exception as e:
        print(f"🚨 ERROR en simulación: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

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

@shared_task
def procesar_alertas_stock_proveedores(producto_id):
    from .models import Producto, SolicitudPresupuesto, Cotizacion
    from django.core.mail import send_mail
    from django.utils import timezone
    from django.conf import settings
    import secrets
    import time

    try:
        producto = Producto.objects.get(id=producto_id)
        logger.info(f"📦 [CELERY] Iniciando envío de emails para: {producto.nombre}")
        
        fecha_hoy = timezone.now().strftime("%d/%m/%Y")
        
        # Se crea UNA sola solicitud para agrupar las cotizaciones
        solicitud = SolicitudPresupuesto.objects.create(
            producto=producto,
            cantidad_requerida=producto.lote_reposicion,
            estado='PENDIENTE'
        )

        # Usamos tu link de Ngrok para que sea clickeable fuera de tu red
        base_url = 'https://brandi-palmar-pickily.ngrok-free.dev'

        for proveedor in producto.proveedores.all():
            if not proveedor.email:
                continue

            cotizacion = Cotizacion.objects.create(
                solicitud=solicitud,
                proveedor=proveedor,
                token=secrets.token_urlsafe(32)
            )

            link = f"{base_url}/proveedor/cotizar/{cotizacion.token}"
            asunto = f"📦 Nueva Solicitud de Compra #{solicitud.id}"
            
            # --- TU HTML ORIGINAL (Con doble {{ }} en CSS para que Python no se confunda) ---
            mensaje_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .btn-hover:hover {{ background-color: #218838 !important; }}
                </style>
            </head>
            <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 40px 0;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                    <div style="background: linear-gradient(135deg, #007bff 0%, #6610f2 100%); padding: 40px 30px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 0.5px;">SOLICITUD DE COMPRA</h1>
                        <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0; font-size: 14px; font-weight: 500;">
                            Los Últimos Serán Los Primeros • {fecha_hoy}
                        </p>
                    </div>
                    <div style="padding: 40px 30px;">
                        <p style="font-size: 16px; color: #4a4a4a; line-height: 1.6; margin-bottom: 30px;">
                            Hola!☺️ <strong>{proveedor.nombre}</strong>,<br>
                            Estamos sin stock de este producto y necesitamos reponerlo con urgencia.
                        </p>
                        <div style="background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; padding: 25px; margin-bottom: 30px; position: relative;">
                            <div style="position: absolute; top: -10px; right: 20px; background-color: #dc3545; color: white; font-size: 10px; font-weight: bold; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px;">
                                Stock Bajo
                            </div>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td>
                                        <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">PRODUCTO</p>
                                        <p style="margin: 5px 0 15px; color: #2d3436; font-size: 18px; font-weight: 700;">{producto.nombre}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <p style="margin: 0; color: #888; font-size: 12px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">CANTIDAD A COTIZAR</p>
                                        <p style="margin: 5px 0 0; color: #2d3436; font-size: 22px; font-weight: 700; color: #007bff;">{solicitud.cantidad_requerida} u.</p>
                                    </td>
                                </tr>
                            </table>
                        </div>
                        <div style="text-align: center; margin-bottom: 30px;">
                            <a href="{link}" style="background-color: #28a745; color: #ffffff; padding: 18px 40px; text-decoration: none; border-radius: 50px; font-weight: 700; font-size: 16px; display: inline-block;">
                                Enviar Presupuesto
                            </a>
                        </div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 25px; text-align: center; border-top: 1px solid #e9ecef;">
                        <p style="margin: 0; color: #adb5bd; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Los Últimos Serán Los Primeros</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mensaje_texto = f"Hola {proveedor.nombre}, necesitamos {solicitud.cantidad_requerida} de {producto.nombre}. Link: {link}"

            try:
                send_mail(
                    subject=asunto,
                    message=mensaje_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[proveedor.email],
                    html_message=mensaje_html,
                    fail_silently=False
                )
                logger.info(f"✅ Email enviado a {proveedor.email}")
                time.sleep(10) # Pausa para Mailtrap
            except Exception as e:
                logger.error(f"❌ Error enviando mail a {proveedor.email}: {e}")

    except Producto.DoesNotExist:
        logger.error("❌ Producto no encontrado")