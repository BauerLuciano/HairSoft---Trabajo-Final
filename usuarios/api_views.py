from rest_framework import viewsets, filters, generics, permissions, status, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from django.db.models import Sum, Count, F, Value, DecimalField, ExpressionWrapper, FloatField, Q, Avg
from django.db import transaction
from django.http import HttpResponse
from django.db.models.functions import TruncDate, Coalesce
from django.utils.dateparse import parse_date
from django.utils import timezone
from .models import Auditoria, Servicio, Turno, Usuario, Producto, Liquidacion, PedidoWeb, ConfiguracionSistema, Silla, SesionCaja, Venta, DetalleVenta, Pedido
from .serializers import AuditoriaSerializer, ServicioSerializer, TurnoSerializer, UsuarioSerializer, ProductoCatalogoSerializer, LiquidacionSerializer, PedidoWebSerializer, SillaSerializer
import io
import datetime
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from .pdf_utils import generar_liquidacion_pdf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus import Image as ImageRL 
from reportlab.lib.units import inch, mm
from .mercadopago_service import MercadoPagoService
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# ============================================
# 1. API DE AUDITORÍA
# ============================================
class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.select_related('usuario', 'usuario__rol').all().order_by('-fecha')
    serializer_class = AuditoriaSerializer
    permission_classes = [AllowAny] 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['accion', 'modelo_afectado']
    search_fields = ['modelo_afectado', 'usuario__nombre', 'usuario__apellido', 'usuario__correo', 'objeto_id']

# ============================================
# 2. APIs DE GESTIÓN DE SERVICIOS
# ============================================

class ServicioListAPIView(generics.ListAPIView):
    queryset = Servicio.objects.all().order_by('nombre')
    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]

class ServicioCreateAPIView(generics.CreateAPIView):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        porcentaje = self.request.data.get('porcentaje_comision', 0)
        serializer.save(porcentaje_comision=porcentaje)

class ServicioUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

class ServicioToggleEstadoView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, id):
        try:
            servicio = Servicio.objects.get(id=id)
            servicio.activo = not servicio.activo
            servicio.save()
            return Response({'status': 'ok', 'activo': servicio.activo})
        except Servicio.DoesNotExist:
            return Response({'error': 'Servicio no encontrado'}, status=404)

# ============================================
# 3. OTRAS APIs
# ============================================

class TurnoListAPIView(generics.ListCreateAPIView):
    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer
    permission_classes = [AllowAny]

class PeluqueroListAPIView(generics.ListAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        return Usuario.objects.filter(rol__nombre__icontains='Peluquero')

class UsuarioListAPIView(generics.ListAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]
    def get_queryset(self):
        queryset = Usuario.objects.all()
        q = self.request.GET.get('q')
        rol = self.request.GET.get('rol')
        if rol: queryset = queryset.filter(rol__nombre__icontains=rol)
        if q: queryset = queryset.filter(nombre__icontains=q) | queryset.filter(apellido__icontains=q)
        return queryset

class ProductoCatalogoView(generics.ListAPIView):
    queryset = Producto.objects.filter(estado='ACTIVO', stock_actual__gt=0)
    serializer_class = ProductoCatalogoSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion', 'marca__nombre']


# ============================================
#  4. MÓDULO DE LIQUIDACIÓN
# ============================================

class ReporteLiquidacionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inicio = request.query_params.get('fecha_inicio')
        fin = request.query_params.get('fecha_fin')
        peluquero_id = request.query_params.get('peluquero_id')

        if not inicio or not fin:
            return Response({"error": "Faltan fechas"}, status=400)

        empleados = Usuario.objects.filter(is_active=True, rol__nombre='Peluquero')
        
        if peluquero_id and peluquero_id != 'null':
            empleados = empleados.filter(id=peluquero_id)

        reporte = []

        for emp in empleados:
            turnos = Turno.objects.filter(
                peluquero=emp,
                estado='COMPLETADO', 
                fecha__range=[inicio, fin]
            ).select_related('cliente').prefetch_related('servicios')

            detalles_turnos = []
            total_comision = 0

            turnos_pagados_ids = Liquidacion.turnos_pagados.through.objects.filter(
                turno_id__in=turnos.values_list('id', flat=True)
            ).values_list('turno_id', flat=True)

            for t in turnos:
                if t.id in turnos_pagados_ids:
                    continue

                servicios_display = []
                for s in t.servicios.all():
                    pct = getattr(s, 'porcentaje_comision', 0)
                    servicios_display.append(f"{s.nombre} ({int(pct)}%)")
                
                str_servicios = " + ".join(servicios_display)
                monto_comision = float(t.monto_comision)
                total_comision += monto_comision

                detalles_turnos.append({
                    "id": t.id,
                    "fecha": t.fecha,
                    "hora": t.hora,
                    "cliente": f"{t.cliente.nombre} {t.cliente.apellido}",
                    "servicios": str_servicios, 
                    "total_cobrado": float(t.monto_total or 0),
                    "comision": monto_comision
                })

            sueldo_base = float(emp.sueldo_fijo or 0)
            total_a_pagar = total_comision + sueldo_base

            reporte.append({
                "id": emp.id,
                "nombre": f"{emp.nombre} {emp.apellido}",
                "rol": emp.rol.nombre if emp.rol else "N/A",
                "cantidad_turnos": len(detalles_turnos),
                "comision_ganada": round(total_comision, 2),
                "sueldo_fijo": sueldo_base,
                "total_a_pagar": round(total_a_pagar, 2),
                "detalles": detalles_turnos
            })

        return Response(reporte)


class RegistrarPagoLiquidacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .models import SesionCaja, MovimientoCaja, Usuario, Turno, Liquidacion

        sesion_abierta = SesionCaja.objects.filter(fecha_cierre__isnull=True).first()
        if not sesion_abierta:
            return Response(
                {"error": "Debe abrir una caja antes de pagar liquidaciones."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        empleado_id = data.get('empleado_id')
        inicio = data.get('fecha_inicio')
        fin = data.get('fecha_fin')
        
        try:
            empleado = Usuario.objects.get(id=empleado_id)
        except Usuario.DoesNotExist:
            return Response({"error": "Empleado no encontrado"}, status=404)

        turnos = Turno.objects.filter(
            peluquero_id=empleado_id, 
            estado='COMPLETADO', 
            fecha__range=[inicio, fin]
        ).exclude(liquidacion__isnull=False)
        
        total_comision = sum(float(t.monto_comision) for t in turnos)
        sueldo_fijo = float(empleado.sueldo_fijo or 0)
        total = total_comision + sueldo_fijo

        if total == 0:
             return Response({"error": "No hay monto pendiente para liquidar."}, status=400)

        try:
            with transaction.atomic():
                liquidacion = Liquidacion.objects.create(
                    empleado=empleado,
                    fecha_inicio_periodo=inicio,
                    fecha_fin_periodo=fin,
                    monto_comisiones=total_comision,
                    monto_sueldo_fijo=sueldo_fijo,
                    total_pagado=total,
                    observaciones=data.get('observaciones', '')
                )
                
                liquidacion.turnos_pagados.set(turnos)

                MovimientoCaja.objects.create(
                    sesion_caja=sesion_abierta,
                    tipo='EGRESO',
                    metodo_pago='EFECTIVO',
                    concepto='LIQUIDACION_SUELDO',
                    monto=total,
                    descripcion=f"Liquidación a {empleado.nombre} {empleado.apellido} (Periodo: {inicio} al {fin})"
                )

            return Response({"status": "ok", "id": liquidacion.id, "mensaje": "Pago registrado correctamente y descontado de la caja."})
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Error interno al guardar: {str(e)}"}, status=500)

class ReporteLiquidacionPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inicio = request.query_params.get('fecha_inicio')
        fin = request.query_params.get('fecha_fin')
        peluquero_id = request.query_params.get('peluquero_id')
        
        usuario_impresor = f"{request.user.nombre} {request.user.apellido}"
        es_historial = request.query_params.get('origen') == 'historial'

        empleados = Usuario.objects.filter(is_active=True, rol__nombre='Peluquero')
        if peluquero_id and peluquero_id != 'null':
            empleados = empleados.filter(id=peluquero_id)

        data_empleados = []

        for emp in empleados:
            # 🔥 CORRECCIÓN: Separamos la lógica si es historial o si es en vivo
            if es_historial:
                from .models import Liquidacion
                # Buscamos la liquidación exacta guardada en el historial
                liq = Liquidacion.objects.filter(empleado=emp, fecha_inicio_periodo=inicio, fecha_fin_periodo=fin).first()
                if not liq:
                    continue
                turnos = liq.turnos_pagados.all()
                sueldo_fijo = float(liq.monto_sueldo_fijo)
                total_comision = float(liq.monto_comisiones)
            else:
                turnos = Turno.objects.filter(
                    peluquero=emp, 
                    estado='COMPLETADO', 
                    fecha__range=[inicio, fin]
                ).exclude(liquidacion__isnull=False)
                
                sueldo_fijo = float(emp.sueldo_fijo or 0)
                if not turnos.exists() and sueldo_fijo == 0:
                    continue
                total_comision = sum(float(t.monto_comision) for t in turnos)
            
            lista_turnos = []
            for t in turnos:
                # Armamos el string con los servicios y porcentajes
                servicios_str = "<br/>".join([f"• {s.nombre} ({int(getattr(s, 'porcentaje_comision', 0))}%)" for s in t.servicios.all()])
                cliente_nombre = f"{t.cliente.nombre} {t.cliente.apellido}" if t.cliente else "Consumidor Final"
                
                lista_turnos.append({
                    'fecha': t.fecha.strftime("%d/%m"),
                    'cliente': cliente_nombre,
                    'servicios': servicios_str,
                    'monto': float(t.monto_comision)
                })

            data_empleados.append({
                'nombre': f"{emp.nombre} {emp.apellido}",
                'comisiones': total_comision,
                'sueldo_fijo': sueldo_fijo,
                'total': total_comision + sueldo_fijo,
                'turnos': lista_turnos 
            })

        pdf_bytes = generar_liquidacion_pdf(data_empleados, inicio, fin, usuario_impresor, es_pagado=es_historial)

        return HttpResponse(pdf_bytes, content_type='application/pdf')
    
class HistorialLiquidacionesView(generics.ListAPIView):
    serializer_class = LiquidacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        empleado_id = self.request.query_params.get('empleado_id')
        queryset = Liquidacion.objects.all().select_related('empleado').order_by('-fecha_pago')
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        return queryset

class PedidoWebViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoWebSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.rol and user.rol.nombre in ['Administrador', 'Recepcionista']:
            return PedidoWeb.objects.all().order_by('-fecha_creacion')
        return PedidoWeb.objects.filter(cliente=user).order_by('-fecha_creacion')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                pedido = serializer.save(cliente=self.request.user, estado='PENDIENTE_PAGO') 
                
                mp_service = MercadoPagoService()
                detalles = pedido.detalles.all()
                resultado_mp = mp_service.crear_preferencia_compra_web(pedido, detalles)
                
                return Response({
                    'mensaje': 'Pedido creado. Redirigiendo...',
                    'pedido_id': pedido.id,
                    'url_pago': resultado_mp['url_pago']
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"❌ ERROR EN CREATE PEDIDO: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        repartidor = request.data.get('repartidor')
        
        motivo = request.data.get('motivo_cancelacion')
        observacion = request.data.get('obs_cancelacion')
        
        if not (request.user.rol and request.user.rol.nombre in ['Administrador', 'Recepcionista']):
             return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)

        if nuevo_estado == 'CANCELADO' and pedido.estado != 'CANCELADO':
            with transaction.atomic():
                for detalle in pedido.detalles.all():
                    detalle.producto.stock_actual += detalle.cantidad
                    detalle.producto.save()
                
                pedido.motivo_cancelacion = motivo
                pedido.obs_cancelacion = observacion
                print(f"🚫 Pedido #{pedido.id} cancelado por: {motivo}")

        if repartidor:
            pedido.datos_entrega_interna = repartidor
            print(f"📦 Asignando repartidor: {repartidor} al pedido {pedido.id}")

        pedido.estado = nuevo_estado
        pedido.save()
        
        return Response({
            'status': 'Estado actualizado', 
            'nuevo_estado': pedido.get_estado_display(),
            'repartidor': pedido.datos_entrega_interna,
            'motivo': motivo
        })

class SillaViewSet(viewsets.ModelViewSet):
    queryset = Silla.objects.all().order_by('orden')
    serializer_class = SillaSerializer
    permission_classes = [IsAuthenticated]

class ConfigWebView(APIView):
    permission_classes = [AllowAny] # Público, para que lo lea el Home y Checkout

    def get(self, request):
        config = ConfiguracionSistema.objects.first()
        if config:
            return Response({
                'costo_moto': float(config.costo_envio_moto),
                'razon_social': config.razon_social,
                'direccion': config.direccion,
                'telefono': config.telefono,
                'email': config.email,
            })
        else:
            return Response({
                'costo_moto': 1500.00,
                'razon_social': 'Los Últimos Serán Los Primeros',
                'direccion': 'Avenida Libertador 600, San Vicente - Misiones',
                'telefono': '3755-72716',
                'email': 'contacto@hairsoft.com'
            })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verificar_estado_caja(request):
    """
    Verifica si existe al menos una SesionCaja abierta (fecha_cierre es null).
    """
    try:
        caja_abierta = SesionCaja.objects.filter(fecha_cierre__isnull=True).exists()
        return Response({'abierta': caja_abierta}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

class EstadisticasDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            inicio_str = request.query_params.get('fecha_inicio')
            fin_str = request.query_params.get('fecha_fin')

            if not inicio_str or not fin_str:
                return Response({'error': 'Debes proporcionar fecha_inicio y fecha_fin'}, status=400)

            f_inicio = parse_date(inicio_str)
            f_fin = parse_date(fin_str)

            # Convertir a datetime aware para campos DateTimeField (Venta, PedidoWeb)
            f_inicio_dt = timezone.make_aware(datetime.datetime.combine(f_inicio, datetime.time.min))
            f_fin_dt = timezone.make_aware(datetime.datetime.combine(f_fin, datetime.time.max))

            # =========================================================
            # 1. INGRESOS TOTALES
            # =========================================================
            ventas_qs = Venta.objects.filter(
                fecha__range=[f_inicio_dt, f_fin_dt],
                anulada=False
            )
            # Turno.fecha es DateField -> usamos __range con objetos date
            turnos_qs = Turno.objects.filter(fecha__range=[f_inicio, f_fin])
            pedidos_web_qs = PedidoWeb.objects.filter(
                fecha_creacion__range=[f_inicio_dt, f_fin_dt],
                estado__in=['PAGADO', 'EN_PREPARACION', 'LISTO_RETIRO', 'EN_CAMINO', 'ENTREGADO']
            )

            # A. Ventas de mostrador
            stats_ventas = ventas_qs.aggregate(ingreso=Sum('total'), cantidad=Count('id'))
            ingreso_ventas = float(stats_ventas['ingreso'] or 0)
            cantidad_ventas = stats_ventas['cantidad'] or 0

            # B. Turnos Completados
            turnos_completados_qs = turnos_qs.filter(estado='COMPLETADO')
            ingreso_turnos_completados = float(turnos_completados_qs.aggregate(total=Sum('monto_total'))['total'] or 0)
            cantidad_turnos_completados = turnos_completados_qs.count()

            # C. Señas Retenidas
            penalizaciones_qs = turnos_qs.filter(
                estado='CANCELADO',
                reembolsado=False,
                reembolso_estado='NO_APLICA'
            ).filter(Q(monto_seña__gt=0) | Q(monto_total__gt=0)).select_related('cliente').prefetch_related('servicios').order_by('-fecha')

            ingresos_penalizaciones_lista = []
            ingreso_penalizaciones = 0
            for p in penalizaciones_qs:
                monto_retenido = float(p.monto_total) if p.tipo_pago == 'TOTAL' else float(p.monto_seña)
                if monto_retenido > 0:
                    ingreso_penalizaciones += monto_retenido
                    ingresos_penalizaciones_lista.append({
                        'cliente': f"{p.cliente.nombre} {p.cliente.apellido}" if p.cliente else 'Consumidor Final',
                        'fecha': p.fecha.strftime('%Y-%m-%d'),
                        'servicio': ", ".join([s.nombre for s in p.servicios.all()]),
                        'motivo': p.motivo_cancelacion or 'Cancelación tardía',
                        'monto_retenido': monto_retenido
                    })

            # D. Pedidos Web
            stats_pedidos = pedidos_web_qs.aggregate(ingreso=Sum('total'), cantidad=Count('id'))
            ingreso_pedidos_web = float(stats_pedidos['ingreso'] or 0)
            cantidad_pedidos_web = stats_pedidos['cantidad'] or 0

            # Totales
            ingreso_total_bruto = ingreso_ventas + ingreso_turnos_completados + ingreso_penalizaciones + ingreso_pedidos_web
            total_operaciones = cantidad_ventas + cantidad_turnos_completados + len(ingresos_penalizaciones_lista) + cantidad_pedidos_web
            ticket_promedio = (ingreso_total_bruto / total_operaciones) if total_operaciones > 0 else 0

            # =========================================================
            # 2. MEDIOS DE PAGO UNIFICADOS
            # =========================================================
            medios_dict = {}
            # Ventas
            for v in ventas_qs.values('medio_pago__nombre').annotate(total=Sum('total')):
                mp = (v['medio_pago__nombre'] or 'OTRO').upper().replace('_', ' ')
                medios_dict[mp] = medios_dict.get(mp, 0) + float(v['total'] or 0)
            # Turnos
            for t in turnos_completados_qs.values('medio_pago').annotate(total=Sum('monto_total')):
                mp = (t['medio_pago'] or 'OTRO').upper().replace('_', ' ')
                medios_dict[mp] = medios_dict.get(mp, 0) + float(t['total'] or 0)
            # Penalizaciones
            for p in penalizaciones_qs:
                mp = (p.medio_pago or 'OTRO').upper().replace('_', ' ')
                monto = float(p.monto_total) if p.tipo_pago == 'TOTAL' else float(p.monto_seña)
                medios_dict[mp] = medios_dict.get(mp, 0) + monto
            # Pedidos Web
            if ingreso_pedidos_web > 0:
                medios_dict['MERCADO PAGO'] = medios_dict.get('MERCADO PAGO', 0) + ingreso_pedidos_web

            grafico_medios = [{'medio': k, 'total': v} for k, v in sorted(medios_dict.items(), key=lambda item: item[1], reverse=True)]

            # =========================================================
            # 3. SERVICIO ESTRELLA (ventas mostrador + turnos completados)
            # =========================================================
            from decimal import Decimal
            servicio_stats = {}

            # 3a. Ventas de mostrador
            ventas_servicios = DetalleVenta.objects.filter(
                venta__fecha__range=[f_inicio_dt, f_fin_dt],
                venta__anulada=False,
                servicio__isnull=False
            ).values('servicio__id', 'servicio__nombre').annotate(
                cantidad=Sum('cantidad'),
                ingreso=Sum('subtotal')
            )
            for vs in ventas_servicios:
                sid = vs['servicio__id']
                nombre = vs['servicio__nombre']
                if sid not in servicio_stats:
                    servicio_stats[sid] = {'nombre': nombre, 'cantidad': 0, 'ingreso': Decimal('0.00')}
                servicio_stats[sid]['cantidad'] += vs['cantidad']
                servicio_stats[sid]['ingreso'] += Decimal(str(vs['ingreso'] or 0))

            # 3b. Turnos completados
            turnos_con_servicios = turnos_completados_qs.prefetch_related('servicios')
            for turno in turnos_con_servicios:
                servicios_turno = list(turno.servicios.all())
                if not servicios_turno:
                    continue
                precio_total_lista = sum((s.precio for s in servicios_turno), Decimal('0.00'))
                if precio_total_lista > 0:
                    factor = Decimal(str(turno.monto_total or 0)) / precio_total_lista
                else:
                    factor = Decimal('0.00')
                for s in servicios_turno:
                    sid = s.id
                    if sid not in servicio_stats:
                        servicio_stats[sid] = {'nombre': s.nombre, 'cantidad': 0, 'ingreso': Decimal('0.00')}
                    servicio_stats[sid]['cantidad'] += 1
                    servicio_stats[sid]['ingreso'] += s.precio * factor

            if servicio_stats:
                mejor = max(servicio_stats.values(), key=lambda x: x['cantidad'])
                servicio_top = {
                    'nombre': mejor['nombre'],
                    'cantidad': mejor['cantidad'],
                    'ingreso': float(mejor['ingreso'])
                }
            else:
                servicio_top = {'nombre': 'Ninguno', 'cantidad': 0, 'ingreso': 0.0}

            # =========================================================
            # 4. PRODUCTO ESTRELLA
            # =========================================================
            producto_top = DetalleVenta.objects.filter(
                venta__fecha__range=[f_inicio_dt, f_fin_dt],
                venta__anulada=False,
                producto__isnull=False
            ).values('producto__nombre').annotate(
                cantidad=Sum('cantidad'),
                ingreso=Sum('subtotal')
            ).order_by('-cantidad').first()

            # =========================================================
            # 5. STOCK ESTANCADO
            # =========================================================
            productos_vendidos_ids = DetalleVenta.objects.filter(
                venta__fecha__range=[f_inicio_dt, f_fin_dt],
                venta__anulada=False,
                producto__isnull=False
            ).values_list('producto_id', flat=True)

            stock_estancado_qs = Producto.objects.exclude(id__in=productos_vendidos_ids).filter(
                estado='ACTIVO', stock_actual__gt=0
            ).annotate(
                capital_parado=ExpressionWrapper(F('stock_actual') * F('precio'), output_field=DecimalField())
            ).values('nombre', 'marca__nombre', 'stock_actual', 'capital_parado').order_by('-capital_parado')[:5]

            # =========================================================
            # 6. FIDELIZACIÓN (clientes únicos: nuevos vs recurrentes)
            # =========================================================
            clientes_ids_unicos = set(
                turnos_completados_qs.exclude(cliente__isnull=True)
                .values_list('cliente_id', flat=True)
            )
            recurrentes = 0
            nuevos = 0
            print("=== DEBUG FIDELIDAD ===")
            print(f"Período: {f_inicio} a {f_fin}")
            print(f"Clientes únicos en período: {len(clientes_ids_unicos)}")
            for cid in clientes_ids_unicos:
                # Contar total de turnos COMPLETADOS en TODA la historia para este cliente
                total_turnos_historia = Turno.objects.filter(
                    cliente_id=cid,
                    estado='COMPLETADO'
                ).count()
                print(f"Cliente ID {cid} -> total histórico de turnos: {total_turnos_historia}")
                if total_turnos_historia > 1:
                    recurrentes += 1
                else:
                    nuevos += 1
            print(f"Nuevos: {nuevos} | Recurrentes: {recurrentes}")
            print("=========================")
            
            total_clientes = nuevos + recurrentes
            tasa_fidelidad = (recurrentes / total_clientes * 100) if total_clientes > 0 else 0
            # =========================================================
            # 7. USUARIO EMISOR (DEBE ESTAR DEFINIDO ANTES DEL RESPONSE)
            # =========================================================
            if request.user.is_authenticated:
                usuario_emisor = f"{getattr(request.user, 'nombre', '')} {getattr(request.user, 'apellido', '')}".strip() or request.user.username
            else:
                usuario_emisor = "Administrador"

            # =========================================================
            # RESPUESTA FINAL
            # =========================================================
            return Response({
                'usuario_emisor': usuario_emisor,
                'kpis': {
                    'ingreso_total': ingreso_total_bruto,
                    'ingreso_operaciones': ingreso_ventas + ingreso_turnos_completados + ingreso_pedidos_web,
                    'ingreso_penalizaciones': ingreso_penalizaciones,
                    'ticket_promedio': ticket_promedio,
                    'fidelidad': { 'tasa': round(tasa_fidelidad, 1), 'nuevos': nuevos, 'recurrentes': recurrentes },
                    'servicio_estrella': servicio_top,
                    'producto_estrella': {
                        'nombre': producto_top['producto__nombre'] if producto_top else 'Ninguno',
                        'cantidad': producto_top['cantidad'] if producto_top else 0,
                        'ingreso': float(producto_top['ingreso'] or 0) if producto_top else 0
                    },
                },
                'graficos': {
                    'medios_pago': grafico_medios,
                    'turnos_ingresos': [
                        {'label': 'Turnos Completados', 'total': ingreso_turnos_completados, 'color': '#10b981'},
                        {'label': 'Señas Retenidas', 'total': ingreso_penalizaciones, 'color': '#f59e0b'}
                    ]
                },
                'tablas': {
                    'stock_estancado': [
                        {
                            'producto': p['nombre'],
                            'marca': p['marca__nombre'] or 'Sin Marca',
                            'stock': p['stock_actual'],
                            'capital': float(p['capital_parado'] or 0)
                        } for p in stock_estancado_qs
                    ],
                    'penalizaciones': ingresos_penalizaciones_lista
                }
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': 'Error interno del servidor. Revisá la consola.'}, status=500)