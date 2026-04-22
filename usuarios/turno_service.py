from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction
from decimal import Decimal
import logging
import uuid
from django.core.exceptions import ValidationError # <--- IMPORTANTE PARA VALIDAR
from .models import Turno, Silla, InteresTurnoLiberado, ConfiguracionSistema # <--- AGREGADA IMPORTACIÓN DE SILLA Y OTROS
from .tasks import procesar_reoferta_masiva  # Importar la tarea de Celery

logger = logging.getLogger(__name__)

class TurnoService:

    # =========================================================================
    # 🆕 NUEVA LÓGICA DE SILLAS (REGISTRAR TURNO)
    # =========================================================================

    @staticmethod
    def _asignar_silla_disponible(fecha, hora):
        """
        Busca una silla activa que no esté ocupada en ese horario.
        Prioriza por el campo 'orden'.
        """
        sillas_activas = Silla.objects.filter(activa=True).order_by('orden')
        
        if not sillas_activas.exists():
            return None # No hay sillas configuradas en el sistema

        ids_ocupadas = Turno.objects.filter(
            fecha=fecha,
            hora=hora,
            estado__in=['RESERVADO', 'CONFIRMADO', 'PENDIENTE', 'PAGADO', 'SENADO']
        ).exclude(silla__isnull=True).values_list('silla_id', flat=True)

        for silla in sillas_activas:
            if silla.id not in ids_ocupadas:
                return silla # Encontré lugar
        
        return None # Todo lleno

    @staticmethod
    def registrar_turno(datos):
        from rest_framework.exceptions import ValidationError

        cliente_id = datos.get('cliente_id') or datos.get('cliente')
        
        if hasattr(cliente_id, 'id'):
            cliente_id = cliente_id.id
            
        if cliente_id:
            ya_tiene_turno = Turno.objects.filter(
                fecha=datos['fecha'],
                hora=datos['hora'],
                cliente_id=cliente_id,
                estado__in=['RESERVADO', 'CONFIRMADO', 'PENDIENTE', 'PAGADO', 'SENADO']
            ).exists()
            
            if ya_tiene_turno:
                raise ValidationError({"error": "No puedes reservar. Ya tienes un turno para esta misma fecha y hora con otro profesional."})

        silla_asignada = None

        if 'silla' in datos and datos['silla']:
            silla_id = datos['silla']
            try:
                silla_elegida = Silla.objects.get(id=silla_id)
                
                if not silla_elegida.activa:
                    raise ValidationError({"error": f"La {silla_elegida.nombre} está fuera de servicio."})

                esta_ocupada = Turno.objects.filter(
                    fecha=datos['fecha'],
                    hora=datos['hora'],
                    silla=silla_elegida,
                    estado__in=['RESERVADO', 'CONFIRMADO', 'PENDIENTE', 'PAGADO', 'SENADO']
                ).exists()

                if esta_ocupada:
                    raise ValidationError({"error": f"La {silla_elegida.nombre} ya está ocupada en ese horario."})
                
                silla_asignada = silla_elegida

            except Silla.DoesNotExist:
                raise ValidationError({"error": "La silla seleccionada no existe."})

        else:
            silla_asignada = TurnoService._asignar_silla_disponible(datos['fecha'], datos['hora'])
            
            if not silla_asignada:
                raise ValidationError({"error": "No hay puestos de trabajo disponibles en este horario (Local lleno)."})

        try:
            cliente_instancia = datos.get('cliente')
            if not cliente_instancia and cliente_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                cliente_instancia = User.objects.get(id=cliente_id)

            # 🔥 ACÁ ESTABA EL ERROR: Le sacamos el servicio=datos.get('servicio')
            turno = Turno.objects.create(
                fecha=datos['fecha'],
                hora=datos['hora'],
                cliente=cliente_instancia,
                peluquero=datos['peluquero'],
                silla=silla_asignada, 
                estado='RESERVADO', 
                canal=datos.get('canal', 'PRESENCIAL'),
                monto_total=datos.get('monto_total', 0),
                monto_seña=datos.get('monto_seña', 0),
                tipo_pago=datos.get('tipo_pago', 'TOTAL'),
                medio_pago=datos.get('medio_pago', 'EFECTIVO')
            )
            
            if 'servicios' in datos and datos['servicios']:
                turno.servicios.set(datos['servicios'])

            return turno

        except Exception as e:
            logger.error(f"Error creando turno: {e}")
            raise e

    # =========================================================================
    # 🔥 UNIFICACIÓN DE MODIFICACIONES
    # =========================================================================
    @staticmethod
    @transaction.atomic
    def modificar_turno(turno_viejo_id, nuevos_datos, usuario_ejecutor):
        """
        Lógica unificada para modificar turno. 
        Maneja reglas de penalidad económica y roles.
        """
        turno_viejo = Turno.objects.select_for_update().get(id=turno_viejo_id)
        
        # 1. Determinar Rol (El staff esquiva la penalidad)
        grupos_usuario = usuario_ejecutor.groups.values_list('name', flat=True)
        es_staff = usuario_ejecutor.is_superuser or 'Administrador' in grupos_usuario or 'Recepcionista' in grupos_usuario

        # 2. Evaluar Penalidad del sistema
        puede_mod, tiene_penalidad, msg_evaluacion = turno_viejo.puede_ser_modificado()
        
        if not puede_mod:
            raise ValidationError({"error": msg_evaluacion})

        aplica_penalidad = tiene_penalidad and not es_staff

        if aplica_penalidad:
            TurnoService.procesar_cancelacion_automatica(
                turno_id=turno_viejo.id,
                motivo="Modificación tardía",
                observacion="El cliente modificó fuera de término. Se retiene el pago."
            )

            nuevos_datos['monto_seña'] = 0 
            nuevos_datos['mp_payment_id'] = None
            
            nuevo_turno = TurnoService.registrar_turno(nuevos_datos)
            return True, "Fuera de término: Se retiene el pago anterior. Deberás abonar el nuevo turno.", nuevo_turno
        
        else:
            nuevos_datos['monto_seña'] = turno_viejo.monto_seña
            nuevos_datos['monto_total'] = turno_viejo.monto_total
            nuevos_datos['tipo_pago'] = turno_viejo.tipo_pago
            nuevos_datos['medio_pago'] = turno_viejo.medio_pago
            nuevos_datos['mp_payment_id'] = turno_viejo.mp_payment_id
            
            nuevo_turno = TurnoService.registrar_turno(nuevos_datos)
            
            # Matamos el turno viejo pasando es_modificacion_gratis para NO generar reembolsos locos
            TurnoService.procesar_cancelacion_automatica(
                turno_id=turno_viejo.id,
                motivo="Reprogramación",
                observacion="Modificación gratuita de horario.",
                es_modificacion_gratis=True
            )
            
            return True, "Turno reprogramado exitosamente sin cargos extra.", nuevo_turno

    # =========================================================================
    # 🛑 FIN LÓGICA DE SILLAS - A CONTINUACIÓN TU CÓDIGO ORIGINAL
    # =========================================================================
    
    @staticmethod
    def procesar_cancelacion_automatica(turno_id, usuario_cancelacion=None, motivo="", observacion="", es_modificacion_gratis=False):
        """
        🔥 VERSIÓN FINAL CORREGIDA - Integrada con Tetris del tiempo y flag de modificación
        """
        print(f"🔄 CANCELANDO TURNO {turno_id} - REEMBOLSO SEGÚN MARGEN")
        
        try:
            from django.db.models import Q
            from .models import InteresTurnoLiberado, ConfiguracionSistema
            
            print(f"\n🔥 INICIANDO CANCELACIÓN TURNO {turno_id}")
            print(f"   Motivo: {motivo}")
            print(f"   Observación: {observacion}")
            
            with transaction.atomic():
                # 1. OBTENER Y CANCELAR TURNO
                turno = Turno.objects.select_for_update().get(id=turno_id)
                
                if turno.estado == 'CANCELADO':
                    return False, "El turno ya está cancelado"
                
                # Verificar que no haya pasado
                ahora = timezone.now()
                fecha_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
                tiempo_restante = fecha_turno - ahora
                
                if tiempo_restante.total_seconds() <= 0:
                    return False, "No se puede cancelar un turno que ya pasó"
                
                # 2. DETERMINAR SI ES CANCELACIÓN DEL CLIENTE (no reoferta)
                es_cancelacion_cliente = True  # Asumir que es el cliente
                
                # 3. GENERAR TOKEN SIEMPRE
                turno.token_reoferta = str(uuid.uuid4())
                print(f"🔑 TOKEN GENERADO EN SERVICE: {turno.token_reoferta}")
                
                # 4. CANCELAR TURNO (sin tocar reembolso aún)
                turno.estado = 'CANCELADO'
                turno.fecha_modificacion = ahora
                turno.motivo_cancelacion = motivo or "Cancelado por el sistema"
                turno.obs_cancelacion = observacion
                turno.reembolsado = False  # nunca se marca automáticamente
                turno.save()
                
                # 5. LLAMAR A LA FUNCIÓN DE REEMBOLSO PARA QUE DETERMINE EL ESTADO
                if es_cancelacion_cliente and not es_modificacion_gratis:
                    config = ConfiguracionSistema.get_solo()
                    margen = config.margen_horas_cancelacion
                    horas_restantes = tiempo_restante.total_seconds() / 3600

                    # Verificar si pagó algo
                    puso_plata = (turno.monto_seña > 0 or turno.tipo_pago == 'TOTAL')

                    if horas_restantes >= margen and puso_plata:
                        turno.reembolso_estado = 'PENDIENTE'
                        mensaje_reembolso = "Reembolso pendiente de procesar manualmente."
                    else:
                        turno.reembolso_estado = 'NO_APLICA'
                        mensaje_reembolso = "No corresponde reembolso (cancelación tardía o sin pago)."
                    
                    turno.reembolsado = False
                    turno.save()
                else:
                    # Cancelación por reoferta o por modificación gratis transferida
                    turno.reembolso_estado = 'NO_APLICA'
                    turno.save()
                    mensaje_reembolso = "Cancelación administrativa/reoferta - no aplica reembolso."
                
                print(f"💾 Turno {turno_id} guardado. Reembolso: {turno.reembolso_estado}, Reembolsado: {turno.reembolsado}")
            
            # 6. 🔥 BUSCAR INTERESADOS (TETRIS DEL TIEMPO REFINADO Y AGRUPADO)
            print(f"🔍 Buscando interesados (excluyendo cliente que canceló y aplicando Tetris)...")
            
            duracion_hueco = turno.duracion_total or turno.calcular_duracion_total()
            if duracion_hueco == 0: duracion_hueco = 30
            fecha_base = datetime.combine(turno.fecha, turno.hora)
            fecha_fin_hueco = fecha_base + timedelta(minutes=duracion_hueco)
            hora_fin_hueco = fecha_fin_hueco.time()
            
            # Traemos todos los intereses en ese rango (excluyendo al que canceló)
            interesados_potenciales = InteresTurnoLiberado.objects.filter(
                peluquero=turno.peluquero,
                fecha_deseada=turno.fecha,
                hora_deseada__gte=turno.hora,
                hora_deseada__lt=hora_fin_hueco
            ).exclude(
                Q(estado_oferta='aceptada') | 
                Q(cliente=turno.cliente)  # ✅ EXCLUIR AL CLIENTE QUE CANCELÓ
            ).select_related('servicio', 'cliente').order_by('fecha_registro')
            
            # AGRUPAR POR CLIENTE PARA SUMAR TIEMPOS DE SERVICIOS
            from collections import defaultdict
            intereses_agrupados = defaultdict(list)
            for interes in interesados_potenciales:
                intereses_agrupados[interes.cliente_id].append(interes)

            interesados_validos_ids = []

            # Filtrado Tetris: Validar que LA SUMA de los servicios entre en el tiempo libre
            for cliente_id, lista_intereses in intereses_agrupados.items():
                hora_solicitada = lista_intereses[0].hora_deseada
                inicio_bloque = datetime.combine(turno.fecha, hora_solicitada)
                
                # Sumamos la duración de TODOS los servicios que quiere este cliente
                duracion_total_cliente = sum(i.servicio.duracion for i in lista_intereses)
                fin_bloque_cliente = inicio_bloque + timedelta(minutes=duracion_total_cliente)
                
                # Si TODO el bloque del cliente termina ANTES de que se acabe el hueco, califica
                if fin_bloque_cliente <= fecha_fin_hueco:
                    for i in lista_intereses:
                        interesados_validos_ids.append(i.id)

            interesados = InteresTurnoLiberado.objects.filter(id__in=interesados_validos_ids).order_by('fecha_registro')
            
            print(f"👥 Interesados encontrados (Tetris Match Completo): {interesados.count()}")
            
            # 7. 🔥 ENVIAR WHATSAPP A TODOS LOS INTERESADOS
            whatsapp_enviados = 0
            if interesados.exists():
                print(f"📡 Enviando WhatsApps a nuevos interesados (agrupados por cliente)...")
                
                # Importar función de WhatsApp
                from .tasks import enviar_whatsapp_oferta
                base_url = "https://brandi-palmar-pickily.ngrok-free.dev"
                
                # 🔥 OBTENER DESCUENTO DE CONFIGURACIÓN
                config = ConfiguracionSistema.get_solo()
                descuento = config.porcentaje_descuento_reoferta  # Valor por defecto 15
                
                # Re-agrupar para mandar 1 solo whatsapp por cliente
                intereses_por_cliente_envio = defaultdict(list)
                for interesado in interesados:
                    intereses_por_cliente_envio[interesado.cliente_id].append(interesado)
                
                for cliente_id, lista_int in intereses_por_cliente_envio.items():
                    interes_ejemplo = lista_int[0]
                    cliente = interes_ejemplo.cliente
                    print(f"  → Procesando cliente: {cliente.nombre} (ID: {cliente_id}, Tel: {cliente.telefono}) - {len(lista_int)} interés(es) calificados")
                    
                    # Generar link único con token
                    link = f"{base_url}/aceptar-oferta/{turno.id}/{turno.token_reoferta}"
                    mensaje = (
                        f"¡TURNO DISPONIBLE! 🎁\n"
                        f"Hola {cliente.nombre}, se liberó un lugar:\n\n"
                        f"📅 {turno.fecha}\n"
                        f"⏰ {turno.hora}\n\n"
                        f"👇 Tocá el link para reservar con un {descuento}% de descuento!:\n"  # <-- USAMOS VARIABLE
                        f"{link}\n\n"
                        f"Los Últimos Serán Los Primeros"
                    )
                    
                    # Enviar WhatsApp si tiene teléfono (UNA SOLA VEZ por cliente)
                    if cliente.telefono:
                        print(f"    📱 Enviando WhatsApp a {cliente.telefono}")
                        resultado = enviar_whatsapp_oferta(cliente.telefono, mensaje)
                        
                        if resultado:
                            print(f"    ✅ WhatsApp ENVIADO correctamente")
                            whatsapp_enviados += 1
                        else:
                            print(f"    ❌ Error enviando WhatsApp")
                    
                    # Actualizar TODOS los intereses de este cliente a 'enviada'
                    for interesado in lista_int:
                        interesado.estado_oferta = 'enviada'
                        interesado.turno_liberado = turno
                        interesado.save(update_fields=['estado_oferta', 'turno_liberado'])
                        print(f"    ✅ Interés ID {interesado.id} actualizado a 'enviada'")
                
                print(f"✅ {whatsapp_enviados} WhatsApps enviados exitosamente")
            
            # 8. ✅ MENSAJE FINAL - INCLUYE INFORMACIÓN DEL REEMBOLSO
            mensaje = 'Turno cancelado exitosamente.'
            
            if es_cancelacion_cliente and not es_modificacion_gratis:
                if turno.reembolso_estado == 'PENDIENTE':
                    mensaje += ' Reembolso pendiente de procesar manualmente.'
                elif turno.reembolso_estado == 'NO_APLICA':
                    mensaje += ' No corresponde reembolso (cancelación tardía).'
                else:
                    mensaje += f' Estado reembolso: {turno.reembolso_estado}'
            else:
                mensaje += ' Cancelación interna/modificación - no aplica reembolso acá.'
            
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
        try:
            from .models import InteresTurnoLiberado
            
            interesados = InteresTurnoLiberado.objects.filter(
                peluquero=turno_cancelado.peluquero,
                fecha_deseada=turno_cancelado.fecha,
                hora_deseada=turno_cancelado.hora,
                estado_oferta='pendiente'
            ).order_by('fecha_registro')[:5]
            
            for interesado in interesados:
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
        try:
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
    print("🚀 Clase ReofertaAutomaticaService cargada correctamente")

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
    def obtener_datos_oferta_previa(turno_liberado_id, token):
        from .models import Turno, InteresTurnoLiberado, ConfiguracionSistema
        from decimal import Decimal
        try:
            turno_liberado = Turno.objects.get(id=turno_liberado_id)
            
            if str(turno_liberado.token_reoferta) != str(token):
                logger.error(f"❌ Mismatch Token. DB: {turno_liberado.token_reoferta}, URL: {token}")
                return None, "Token inválido o enlace expirado"

            interes_principal = InteresTurnoLiberado.objects.filter(
                turno_liberado_id=turno_liberado_id,
                token_oferta=token
            ).first()

            if not interes_principal:
                interes_principal = InteresTurnoLiberado.objects.filter(
                    turno_liberado_id=turno_liberado_id,
                    estado_oferta__in=['enviada', 'preparando']
                ).first()
            
            if not interes_principal: 
                return None, "Oferta no disponible"

            intereses_cliente = InteresTurnoLiberado.objects.filter(
                turno_liberado_id=turno_liberado_id,
                cliente=interes_principal.cliente
            )

            total_bruto = sum(Decimal(str(i.servicio.precio)) for i in intereses_cliente)
            nombres_servicios = ", ".join([i.servicio.nombre for i in intereses_cliente])
            
            config = ConfiguracionSistema.get_solo()
            descuento = config.porcentaje_descuento_reoferta
            
            precio_oferta = total_bruto * (Decimal('100') - Decimal(descuento)) / Decimal('100')
            
            turno_anterior = Turno.objects.filter(
                cliente=interes_principal.cliente, 
                estado__in=['RESERVADO', 'CONFIRMADO']
            ).exclude(id=turno_liberado_id).order_by('-fecha_creacion').first()
            
            pagado_anterior = Decimal('0.00')
            if turno_anterior:
                pagado_anterior = turno_anterior.monto_total if turno_anterior.tipo_pago == 'TOTAL' else turno_anterior.monto_seña
            
            saldo = max(Decimal('0.00'), pagado_anterior - precio_oferta)
            monto_final = max(Decimal('0.00'), precio_oferta - pagado_anterior)

            return {
                "precio_original": float(total_bruto),
                "precio_final": float(precio_oferta),
                "pagado_anterior": float(pagado_anterior),
                "saldo_a_favor": float(saldo),
                "monto_final_a_pagar": float(monto_final),
                "servicio": nombres_servicios,
                "profesional": f"{turno_liberado.peluquero.nombre} {turno_liberado.peluquero.apellido}",
                "fecha": turno_liberado.fecha.strftime("%d/%m/%Y"),
                "hora": turno_liberado.hora.strftime("%H:%M"),
                "cliente_id": interes_principal.cliente.id,
                "turno_liberado_id": turno_liberado_id,
                "token": token,
                "descuento_porcentaje": descuento, 
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def ejecutar_canje(intereses_o_unico, turno_liberado):
        print("🔥 EJECUTANDO ejecutar_canje - Método alcanzado")
        from .models import Turno, InteresTurnoLiberado
        from django.db import transaction
        from decimal import Decimal
        try:
            with transaction.atomic():
                if hasattr(intereses_o_unico, '__iter__'):
                    lista_original = list(intereses_o_unico)
                    interes_base = lista_original[0]
                else:
                    interes_base = intereses_o_unico
                    lista_original = [interes_base]

                turno_target = Turno.objects.select_for_update().get(id=turno_liberado.id)
                if turno_target.estado != 'CANCELADO':
                    return False, "El turno ya fue tomado por otra persona."

                cliente = interes_base.cliente

                intereses_completos = InteresTurnoLiberado.objects.filter(
                    turno_liberado=turno_target,
                    cliente=cliente,
                    estado_oferta='enviada'
                )
                if intereses_completos.exists():
                    lista_intereses = list(intereses_completos)
                else:
                    lista_intereses = lista_original

                turno_anterior = Turno.objects.filter(
                    cliente=cliente, estado__in=['RESERVADO', 'CONFIRMADO']
                ).exclude(id=turno_target.id).order_by('-fecha_creacion').first()

                pagado_previo = Decimal('0.00')
                canal_clonado = 'WEB'
                mp_id = None
                cod_trans = None
                entidad = None

                if turno_anterior:
                    pagado_previo = turno_anterior.monto_total if turno_anterior.tipo_pago == 'TOTAL' else turno_anterior.monto_seña
                    canal_clonado = turno_anterior.canal
                    mp_id = turno_anterior.mp_payment_id
                    cod_trans = turno_anterior.codigo_transaccion
                    entidad = turno_anterior.entidad_pago

                    turno_anterior.estado = 'CANCELADO'
                    turno_anterior.motivo_cancelacion = "Turno por canje"
                    turno_anterior.reembolso_estado = 'NO_APLICA'
                    turno_anterior.save()

                total_bruto = sum(Decimal(str(i.servicio.precio)) for i in lista_intereses)
                precio_con_desc = total_bruto * Decimal('0.85')

                if pagado_previo < precio_con_desc:
                    tipo_pago = 'SENA_50'
                else:
                    tipo_pago = 'TOTAL'

                monto_seña = pagado_previo

                nuevo = Turno.objects.create(
                    fecha=turno_target.fecha,
                    hora=turno_target.hora,
                    peluquero=interes_base.peluquero,
                    cliente=cliente,
                    estado='RESERVADO',
                    canal=canal_clonado,
                    tipo_pago=tipo_pago,
                    medio_pago='MERCADO_PAGO',
                    mp_payment_id=mp_id,
                    codigo_transaccion=cod_trans,
                    entidad_pago=entidad,
                    monto_total=precio_con_desc,
                    monto_seña=monto_seña,
                    oferta_activa=True,
                    motivo_cancelacion="",
                    obs_cancelacion="Turno obtenido por canje"
                )

                for item in lista_intereses:
                    nuevo.servicios.add(item.servicio)
                    item.estado_oferta = 'aceptada'
                    item.fecha_respuesta = timezone.now()
                    item.save()

                InteresTurnoLiberado.objects.filter(
                    turno_liberado=turno_target, estado_oferta='enviada'
                ).exclude(cliente=cliente).update(estado_oferta='expirada')

                return True, "¡Turno confirmado con éxito!"
        except Exception as e:
            return False, f"Error en canje: {str(e)}"