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
    """VERSIÓN CORREGIDA - Solo clientes con turnos previos y 60+ días sin visitar"""
    logger.info("🎯 [FIDELIZACIÓN] Iniciando proceso optimizado...")
    
    try:
        DIAS_INACTIVIDAD = 60
        DIAS_COOLDOWN = 90
        hoy = timezone.now()
        
        # 🔥 CONSULTA OPTIMIZADA: Solo clientes con al menos UN turno en el pasado
        from django.db.models import Exists, OuterRef
        
        # Primero, clientes que tienen al menos un turno
        clientes_con_turnos = Usuario.objects.filter(
            rol__nombre__iexact='Cliente',
            telefono__isnull=False,
        ).exclude(telefono='').annotate(
            tiene_turnos=Exists(
                Turno.objects.filter(
                    cliente=OuterRef('pk'),
                    fecha__lt=hoy.date()  # Solo turnos pasados
                )
            )
        ).filter(tiene_turnos=True)
        
        logger.info(f"📊 Clientes con al menos un turno en el pasado: {clientes_con_turnos.count()}")
        
        if clientes_con_turnos.count() == 0:
            logger.info("ℹ️ No hay clientes con turnos en el pasado. Terminando.")
            return "0 mensajes enviados"
        
        # Identificar clientes inactivos
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
                logger.info(f"   ⏳ {cliente.nombre}: Ya recibió promoción reciente")
                continue
            
            clientes_inactivos.append({
                'cliente': cliente,
                'dias_inactivo': dias_inactivo,
                'ultima_visita': ultimo_turno.fecha
            })
        
        logger.info(f"🎯 Clientes inactivos (60+ días): {len(clientes_inactivos)}")
        
        if len(clientes_inactivos) == 0:
            logger.info("✅ No hay clientes que cumplan criterios")
            return "0 mensajes enviados"
        
        # 🔥 LIMITAR ENVÍOS
        limite_diario = 15
        clientes_a_enviar = clientes_inactivos[:limite_diario]
        
        if len(clientes_inactivos) > limite_diario:
            logger.warning(f"⚠️  {len(clientes_inactivos)} inactivos, solo se enviará a {limite_diario}")
        
        # 🔥 PROCESAR ENVÍO
        enviados = 0
        
        for info_cliente in clientes_a_enviar:
            cliente = info_cliente['cliente']
            dias_inactivo = info_cliente['dias_inactivo']
            
            logger.info(f"\n📨 Procesando: {cliente.nombre}")
            logger.info(f"   📅 Última visita: {info_cliente['ultima_visita']} (hace {dias_inactivo} días)")
            
            try:
                # Generar código
                codigo = f"VOLVE{secrets.token_hex(3).upper()}"
                
                # Formatear teléfono
                telefono = str(cliente.telefono).strip()
                if not telefono.startswith('+'):
                    if telefono.startswith('0'):
                        telefono = telefono[1:]
                    telefono = f"+54{telefono}"
                
                # Construir link
                frontend_url = settings.FRONTEND_URL
                if not frontend_url.startswith('http'):
                    frontend_url = f"https://{frontend_url}"
                
                link = f"{frontend_url}/turnos/crear-web?cup={codigo}"
                
                # Mensaje
                mensaje = (
                    f"*¡TE EXTRAÑAMOS EN LA PELUQUERÍA!* ✂️💈\n\n"
                    f"Hola {cliente.nombre},\n\n"
                    f"Notamos que hace *{dias_inactivo} días* que no nos visitás.\n\n"
                    f"*🎁 TE REGALAMOS UN 15% DE DESCUENTO* en tu próximo turno.\n\n"
                    f"👉 *CLICK PARA RESERVAR:*\n"
                    f"{link}\n\n"
                    f"📱 *Código:* {codigo}\n\n"
                    f"⏰ *Válido por 7 días*\n"
                    f"📍 *Peluquería: Los Últimos Serán Los Primeros*"
                )
                
                # 🔥 ENVIAR MENSAJE
                try:
                    from twilio.rest import Client
                    account_sid = settings.TWILIO_ACCOUNT_SID
                    auth_token = settings.TWILIO_AUTH_TOKEN
                    
                    client = Client(account_sid, auth_token)
                    
                    message = client.messages.create(
                        body=mensaje,
                        from_=settings.TWILIO_WHATSAPP_NUMBER,
                        to=f'whatsapp:{telefono}'
                    )
                    
                    logger.info(f"   ✅ Enviado! SID: {message.sid}")
                    
                    # 🔥 CREAR PROMOCIÓN CON LOS CAMPOS CORRECTOS
                    PromocionReactivacion.objects.create(
                        cliente=cliente,
                        codigo=codigo,
                        descuento_porcentaje=15,
                        fecha_vencimiento=hoy + timedelta(days=7),
                        # 🔥 Si agregaste los campos al modelo:
                        mensaje_sid=message.sid,  # ID del mensaje Twilio
                        canal_envio='WHATSAPP'
                    )
                    
                    enviados += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    if "exceeded the 50 daily messages limit" in error_msg:
                        logger.error(f"   🚨 LÍMITE DIARIO DE TWILIO ALCANZADO. Deteniendo.")
                        break
                    else:
                        logger.error(f"   ❌ Error Twilio: {error_msg}")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error general con {cliente.nombre}: {str(e)}")
                continue
        
        logger.info(f"\n✅ Proceso completado: {enviados} mensajes enviados")
        return f"{enviados} mensajes enviados"
        
    except Exception as e:
        logger.error(f"🚨 ERROR CRÍTICO: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"
    
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