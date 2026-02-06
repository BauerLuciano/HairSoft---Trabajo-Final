from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction
from decimal import Decimal
import logging
import uuid
from .models import Turno
from .tasks import procesar_reoferta_masiva  # Importar la tarea de Celery

logger = logging.getLogger(__name__)

class TurnoService:
    
    @staticmethod
    def procesar_cancelacion_automatica(turno_id, usuario_cancelacion=None, motivo="", observacion=""):
        """
        🔥 VERSIÓN FINAL CORREGIDA - Reembolso SIEMPRE PENDIENTE (nunca automático)
        """
        print(f"🔄 CANCELANDO TURNO {turno_id} - REEMBOLSO SIEMPRE PENDIENTE")
        
        try:
            from django.db.models import Q
            from .models import InteresTurnoLiberado
            
            print(f"\n🔥 INICIANDO CANCELACIÓN TURNO {turno_id}")
            print(f"   Motivo: {motivo}")
            print(f"   Observación: {observacion}")
            
            with transaction.atomic():
                # 1. OBTENER Y CANCELAR TURNO
                turno = Turno.objects.select_for_update().get(id=turno_id)
                
                if turno.estado == 'CANCELADO':
                    return False, "El turno ya está cancelado"
                
                # 2. ✅ USAR LA LÓGICA DE REEMBOLSO QUE YA TENÉS EN VIEWS.PY
                # Pero primero verificar el tiempo
                ahora = timezone.now()
                fecha_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
                tiempo_restante = fecha_turno - ahora
                
                if tiempo_restante.total_seconds() <= 0:
                    return False, "No se puede cancelar un turno que ya pasó"
                
                # 3. ✅ DETERMINAR SI ES CANCELACIÓN DEL CLIENTE (no reoferta)
                es_cancelacion_cliente = True  # Asumir que es el cliente
                
                # 4. ✅ GENERAR TOKEN SIEMPRE
                turno.token_reoferta = str(uuid.uuid4())
                print(f"🔑 TOKEN GENERADO EN SERVICE: {turno.token_reoferta}")
                
                # 5. ✅ CANCELAR TURNO PERO DEJAR REEMBOLSO PENDIENTE
                turno.estado = 'CANCELADO'
                turno.fecha_modificacion = ahora
                turno.motivo_cancelacion = motivo or "Cancelado por el sistema"
                turno.obs_cancelacion = observacion
                
                # ✅ CORRECCIÓN CRÍTICA: INICIALIZAR REEMBOLSO COMO "PENDIENTE" 
                # La función procesar_reembolso_si_corresponde lo ajustará después
                if es_cancelacion_cliente:
                    # ✅ SIEMPRE empezar como PENDIENTE si el cliente pagó algo
                    if turno.monto_seña > 0 or turno.tipo_pago == 'TOTAL':
                        turno.reembolso_estado = 'PENDIENTE'
                    else:
                        turno.reembolso_estado = 'NO_APLICA'
                else:
                    # Si es por reoferta/aceptación de oferta, NO APLICA reembolso
                    turno.reembolso_estado = 'NO_APLICA'
                
                # ✅ NO marcar como reembolsado automáticamente NUNCA
                turno.reembolsado = False
                
                # 6. ✅ AHORA SÍ LLAMAR A TU FUNCIÓN DE REEMBOLSO
                # Pero primero guardamos el turno para tener ID
                turno.save()
                
                # Importar tu función desde views.py
                from usuarios.views import procesar_reembolso_si_corresponde
                
                # Determinar si corresponde devolución usando la lógica del modelo
                puede_cancelar, hay_reembolso, msg_tiempo = turno.puede_ser_cancelado()
                
                if hay_reembolso and es_cancelacion_cliente:
                    # ✅ Llamar a tu función para que determine el estado del reembolso
                    # PERO IMPORTANTE: Esta función NO debe marcar automáticamente como COMPLETADO
                    procesado, mensaje_reembolso = procesar_reembolso_si_corresponde(turno)
                    
                    # ✅ CORRECCIÓN: Si la función lo marca como COMPLETADO, forzar a PENDIENTE
                    if turno.reembolso_estado == 'COMPLETADO':
                        print(f"⚠️  ATENCIÓN: La función marcó reembolso como COMPLETADO, forzando a PENDIENTE")
                        turno.reembolso_estado = 'PENDIENTE'
                        turno.reembolsado = False
                        mensaje_reembolso = "Reembolso pendiente de procesar manualmente"
                    
                    # Guardar cambios del reembolso
                    turno.save()
                    print(f"💰 Estado reembolso después de procesar: {turno.reembolso_estado}")
                else:
                    mensaje_reembolso = "No corresponde reembolso"
                
                print(f"💾 Turno {turno_id} guardado. Reembolso: {turno.reembolso_estado}, Reembolsado: {turno.reembolsado}")
            
            # 7. 🔥 BUSCAR INTERESADOS (EXCLUIR AL CLIENTE QUE CANCELÓ)
            print(f"🔍 Buscando interesados (excluyendo cliente que canceló)...")
            
            interesados = InteresTurnoLiberado.objects.filter(
                peluquero=turno.peluquero,
                fecha_deseada=turno.fecha,
                hora_deseada=turno.hora
            ).exclude(
                Q(estado_oferta='aceptada') | 
                Q(cliente=turno.cliente)  # ✅ EXCLUIR AL CLIENTE QUE CANCELÓ
            ).order_by('fecha_registro')
            
            print(f"👥 Interesados encontrados (sin cliente que canceló): {interesados.count()}")
            
            # 8. 🔥 ENVIAR WHATSAPP A TODOS LOS INTERESADOS (excepto el que canceló)
            whatsapp_enviados = 0
            if interesados.exists():
                print(f"📡 Enviando WhatsApps a nuevos interesados...")
                
                # Importar función de WhatsApp
                from .tasks import enviar_whatsapp_oferta
                base_url = "https://brandi-palmar-pickily.ngrok-free.dev"
                
                for interesado in interesados:
                    try:
                        print(f"  → Procesando: {interesado.cliente.nombre} (Tel: {interesado.cliente.telefono})")
                        
                        # Generar link único con token
                        link = f"{base_url}/aceptar-oferta/{turno.id}/{turno.token_reoferta}"
                        mensaje = (
                            f"¡TURNO DISPONIBLE! 🎁\n"
                            f"Hola {interesado.cliente.nombre}, se liberó un lugar:\n\n"
                            f"📅 {turno.fecha}\n"
                            f"⏰ {turno.hora}\n\n"
                            f"👇 Tocá el link para reservar con un 15% de descuento!:\n"
                            f"{link}\n\n"
                            f"Los Últimos Serán Los Primeros"
                        )
                        
                        # Enviar WhatsApp si tiene teléfono
                        if interesado.cliente.telefono:
                            print(f"    📱 Enviando WhatsApp a {interesado.cliente.telefono}")
                            resultado = enviar_whatsapp_oferta(interesado.cliente.telefono, mensaje)
                            
                            if resultado:
                                print(f"    ✅ WhatsApp ENVIADO correctamente")
                                whatsapp_enviados += 1
                            else:
                                print(f"    ❌ Error enviando WhatsApp")
                        
                        # Actualizar estado del interesado
                        interesado.estado_oferta = 'enviada'
                        interesado.turno_liberado = turno
                        interesado.save(update_fields=['estado_oferta', 'turno_liberado'])
                        
                        print(f"    ✅ Estado actualizado a 'enviada'")
                        
                    except Exception as e:
                        print(f"    ❌ Error con {interesado.cliente.nombre}: {e}")
                        continue
                
                print(f"✅ {whatsapp_enviados} WhatsApps enviados exitosamente")
            
            # 9. ✅ MENSAJE FINAL - REEMBOLSO SIEMPRE PENDIENTE
            mensaje = 'Turno cancelado exitosamente'
            
            if es_cancelacion_cliente:
                if turno.reembolso_estado == 'PENDIENTE':
                    mensaje += '. Reembolso pendiente de procesar manualmente.'
                elif turno.reembolso_estado == 'NO_APLICA':
                    mensaje += '. No corresponde reembolso.'
                else:
                    mensaje += f'. Estado reembolso: {turno.reembolso_estado}'
            else:
                mensaje += '. Cancelación por aceptación de oferta - no aplica reembolso.'
            
            if whatsapp_enviados > 0:
                mensaje += f' Se notificó a {whatsapp_enviados} interesados.'
            elif interesados.exists():
                mensaje += ' Se encontraron interesados pero no se pudo enviar notificaciones.'
            
            return True, mensaje
            
        except Turno.DoesNotExist:
            return False, "Turno no encontrado"
        except Exception as e:
            import traceback
            print(f"❌ ERROR FATAL: {e}")
            print(traceback.format_exc())
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def _notificar_interesados_sincrono(turno_cancelado):
        """
        Notificación SÍNCRONA inmediata después del commit.
        Actualiza estado de interesados sin enviar WhatsApp.
        """
        try:
            from .models import InteresTurnoLiberado
            
            # Usar 'estado_oferta' en lugar de 'notificado'
            interesados = InteresTurnoLiberado.objects.filter(
                peluquero=turno_cancelado.peluquero,
                fecha_deseada=turno_cancelado.fecha,
                hora_deseada=turno_cancelado.hora,
                estado_oferta='pendiente'
            ).order_by('fecha_registro')[:5]
            
            for interesado in interesados:
                # Solo actualizar estado, no enviar mensajes aquí
                interesado.estado_oferta = 'preparando'
                interesado.turno_liberado = turno_cancelado
                interesado.save(update_fields=['estado_oferta', 'turno_liberado'])
                
            logger.info(f"📋 {len(interesados)} interesados marcados como 'preparando'")
            return len(interesados)
            
        except Exception as e:
            logger.error(f"❌ Error en notificación síncrona: {str(e)}")
            return 0

    @staticmethod
    def _procesar_devolucion_senia(turno):
        """
        ✅ VERSIÓN CORREGIDA: SOLO determina si corresponde reembolso, NO lo procesa automáticamente
        """
        try:
            # ✅ CORRECCIÓN: NUNCA procesamos automáticamente, solo determinamos el tipo
            if turno.canal == 'WEB' and turno.medio_pago == 'MERCADO_PAGO':
                logger.info(f"💰 Reembolso MP PENDIENTE para turno {turno.id}, monto: {turno.monto_seña}")
                return False, "Reembolso pendiente de procesar via Mercado Pago"
            elif turno.canal == 'PRESENCIAL':
                logger.info(f"💰 Reembolso en efectivo PENDIENTE para turno {turno.id}, monto: {turno.monto_seña}")
                return False, "Cliente debe pasar a buscar el reembolso en efectivo (pendiente)"
            else:
                return False, "No se pudo determinar el método de devolución"
        except Exception as e:
            logger.error(f"❌ Error en devolución de seña para turno {turno.id}: {str(e)}")
            return False, f"Error en proceso de devolución: {str(e)}"
    
    @staticmethod
    def verificar_anticipacion_cancelacion(turno):
        try:
            ahora = timezone.now()
            fecha_turno = timezone.make_aware(
                datetime.combine(turno.fecha, turno.hora)
            )
            tiempo_restante = fecha_turno - ahora
            
            puede_cancelar = tiempo_restante.total_seconds() > 0
            hay_reembolso = tiempo_restante >= timedelta(hours=3)
            
            return puede_cancelar, hay_reembolso, tiempo_restante
        except Exception as e:
            logger.error(f"❌ Error verificando anticipación para turno {turno.id}: {str(e)}")
            return False, False, timedelta(0)

    @staticmethod
    def registrar_interes_turno(cliente_id, servicio_id, peluquero_id, fecha_deseada, hora_deseada):
        try:
            from .models import InteresTurnoLiberado
            
            interes_existente = InteresTurnoLiberado.objects.filter(
                cliente_id=cliente_id,
                servicio_id=servicio_id,
                peluquero_id=peluquero_id,
                fecha_deseada=fecha_deseada,
                hora_deseada=hora_deseada,
                estado_oferta='pendiente',
                oferta_aceptada=False
            ).exists()
            
            if interes_existente:
                return False, "Ya estás registrado en la lista de espera para este horario"
            
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

    @staticmethod
    def procesar_reoferta_automatica(turno_id):
        try:
            turno = Turno.objects.get(id=turno_id)
            if turno.estado == 'CANCELADO': 
                return ReofertaAutomaticaService.procesar_reoferta(turno)
            return False
        except Turno.DoesNotExist:
            logger.error(f"❌ Turno {turno_id} no encontrado para reoferta")
            return False


class ReofertaAutomaticaService:
    
    @staticmethod
    def procesar_reoferta(turno_cancelado):
        try:
            from .models import InteresTurnoLiberado
            
            logger.info(f"🔄 Iniciando reoferta para turno {turno_cancelado.id}")
            
            # Asegurar token (backup por si se llama manual)
            if not turno_cancelado.token_reoferta:
                turno_cancelado.token_reoferta = str(uuid.uuid4())
                turno_cancelado.save(update_fields=['token_reoferta'])
            
            interesados = InteresTurnoLiberado.objects.filter(
                peluquero=turno_cancelado.peluquero,
                fecha_deseada=turno_cancelado.fecha,
                hora_deseada=turno_cancelado.hora,
                estado_oferta='enviada' 
            ).order_by('fecha_registro')[:1]
            
            if not interesados:
                return False
            
            interesado = interesados[0]
            
            # GENERAR LINK PARA EL FRONTEND
            base_url = "https://brandi-palmar-pickily.ngrok-free.dev"
            link_oferta = f"{base_url}/aceptar-oferta/{turno_cancelado.id}/{turno_cancelado.token_reoferta}"
            
            logger.info(f"🔗 LINK GENERADO PARA {interesado.cliente.nombre}: {link_oferta}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en procesar_reoferta: {str(e)}")
            return False

    @staticmethod
    @transaction.atomic
    def ejecutar_canje(interesado, turno_liberado):
        """
        🔥 LÓGICA DE CANJE BLINDADA (3 REGISTROS + PAGO CLONADO)
        """
        from .models import Turno
        
        try:
            logger.info(f"🔄 EJECUTANDO CANJE PARA: {interesado.cliente.nombre}")
            
            # 1. BUSCAR TURNO VIEJO (B)
            turno_viejo = Turno.objects.filter(
                cliente=interesado.cliente,
                estado__in=['RESERVADO', 'CONFIRMADO'],
                fecha__gte=timezone.now().date()
            ).order_by('-fecha_creacion').first()

            if not turno_viejo:
                return False, "El cliente no tiene un turno activo para canjear."

            # 2. CAPTURAR DATOS FINANCIEROS (CLONACIÓN)
            mp_id_origen = turno_viejo.mp_payment_id
            transaccion_origen = turno_viejo.nro_transaccion
            medio_pago_origen = turno_viejo.medio_pago
            
            # Plata pagada
            plata_pagada = turno_viejo.monto_seña or Decimal('0.00')
            if turno_viejo.tipo_pago == 'TOTAL':
                plata_pagada = turno_viejo.monto_total or Decimal('0.00')

            logger.info(f"💰 Plata pagada en turno viejo: {plata_pagada}. Medio: {medio_pago_origen}")

            # 3. CANCELAR TURNO VIEJO (B) - SIN DEVOLUCIÓN
            # Usamos update() directo para evitar que signals interfieran aquí
            Turno.objects.filter(id=turno_viejo.id).update(
                estado='CANCELADO',
                motivo_cancelacion='CANJE_AUTOMATICO',
                obs_cancelacion=f"Canjeado por turno ID {turno_liberado.id}.",
                reembolsado=True,
                reembolso_estado='NO_APLICA', # CLAVE
                fecha_modificacion=timezone.now()
            )
            logger.info(f"🚫 Turno Viejo ID {turno_viejo.id} CANCELADO (Registro 2 de 3)")

            # 4. PRECIO NUEVO
            precio_base = interesado.servicio.precio
            descuento = Decimal('0.85')
            precio_con_descuento = precio_base * descuento
            
            # 5. SALDO A FAVOR
            saldo_a_favor = Decimal('0.00')
            if plata_pagada > precio_con_descuento:
                saldo_a_favor = plata_pagada - precio_con_descuento

            # 6. TIPO DE PAGO NUEVO
            if plata_pagada >= precio_con_descuento:
                tipo_pago_nuevo = 'TOTAL'
                monto_seña_nuevo = precio_con_descuento 
                estado_nuevo = 'CONFIRMADO' 
            else:
                tipo_pago_nuevo = 'SENA_50'
                monto_seña_nuevo = plata_pagada
                estado_nuevo = 'RESERVADO'

            # 7. CREAR TURNO NUEVO (C)
            nuevo_turno = Turno.objects.create(
                cliente=interesado.cliente,
                peluquero=turno_liberado.peluquero,
                fecha=turno_liberado.fecha,
                hora=turno_liberado.hora,
                canal='WEB',
                estado=estado_nuevo,
                
                # CLONACIÓN EXPLÍCITA
                mp_payment_id=mp_id_origen,
                nro_transaccion=transaccion_origen,
                medio_pago=medio_pago_origen,
                
                tipo_pago=tipo_pago_nuevo,
                monto_seña=monto_seña_nuevo,
                monto_total=precio_con_descuento,
                
                obs_cancelacion=f"Generado por Reoferta. Origen Turno {turno_viejo.id}. Saldo favor: ${saldo_a_favor}",
                reembolso_estado='NO_APLICA',
                reembolsado=False,
            )
            
            nuevo_turno.servicios.add(interesado.servicio)
            interesado.oferta_aceptada = True
            interesado.fecha_aceptacion = timezone.now()
            interesado.save()

            logger.info(f"✅ Turno Nuevo ID {nuevo_turno.id} CREADO. MP Clonado: {mp_id_origen}")
            return True, "Canje exitoso"

        except Exception as e:
            logger.error(f"❌ Error en canje: {str(e)}")
            return False, str(e)

    @staticmethod
    def obtener_datos_oferta_previa(turno_liberado_id, token):
        from .models import Turno, InteresTurnoLiberado
        try:
            turno_liberado = Turno.objects.get(id=turno_liberado_id)
            
            # Validar token
            if str(turno_liberado.token_reoferta) != str(token):
                logger.error(f"❌ Mismatch Token. DB: {turno_liberado.token_reoferta}, URL: {token}")
                return None, "Token inválido"

            # CORREGIDO: Filtro por estado_oferta
            interesado = InteresTurnoLiberado.objects.filter(
                peluquero=turno_liberado.peluquero, 
                fecha_deseada=turno_liberado.fecha,
                hora_deseada=turno_liberado.hora, 
                estado_oferta='enviada'
            ).first()
            
            if not interesado:
                # Intento con preparando por si acaso
                interesado = InteresTurnoLiberado.objects.filter(
                    peluquero=turno_liberado.peluquero, 
                    fecha_deseada=turno_liberado.fecha,
                    hora_deseada=turno_liberado.hora, 
                    estado_oferta='preparando'
                ).first()
            
            if not interesado: 
                return None, "Oferta no disponible"

            precio_base = interesado.servicio.precio
            precio_oferta = precio_base * Decimal('0.85')
            
            turno_anterior = Turno.objects.filter(
                cliente=interesado.cliente, 
                estado__in=['RESERVADO', 'CONFIRMADO']
            ).order_by('-fecha_creacion').first()
            
            pagado_anterior = Decimal('0.00')
            if turno_anterior:
                 pagado_anterior = turno_anterior.monto_total if turno_anterior.tipo_pago == 'TOTAL' else turno_anterior.monto_seña
            
            saldo = max(Decimal('0.00'), pagado_anterior - precio_oferta)
            monto_final = max(Decimal('0.00'), precio_oferta - pagado_anterior)

            return {
                "precio_original": float(precio_base),
                "precio_final": float(precio_oferta),
                "pagado_anterior": float(pagado_anterior),
                "saldo_a_favor": float(saldo),
                "monto_final_a_pagar": float(monto_final),
                "servicio": interesado.servicio.nombre,
                "profesional": f"{turno_liberado.peluquero.nombre} {turno_liberado.peluquero.apellido}",
                "fecha": str(turno_liberado.fecha),
                "hora": str(turno_liberado.hora),
                "cliente_id": interesado.cliente.id,
                "turno_liberado_id": turno_liberado_id,
                "token": token
            }, None
        except Exception as e:
            return None, str(e)