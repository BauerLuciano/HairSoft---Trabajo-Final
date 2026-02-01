from rest_framework import viewsets, filters, generics, permissions, status, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import HttpResponse
from .models import Auditoria, Servicio, Turno, Usuario, Producto, Liquidacion, PedidoWeb, ConfiguracionSistema
from .serializers import AuditoriaSerializer, ServicioSerializer, TurnoSerializer, UsuarioSerializer, ProductoCatalogoSerializer, LiquidacionSerializer, PedidoWebSerializer
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
# 💰 4. MÓDULO DE LIQUIDACIÓN
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
            # CORRECCIÓN: 'COMPLETADO' (Mayúsculas)
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
        data = request.data
        empleado_id = data.get('empleado_id')
        inicio = data.get('fecha_inicio')
        fin = data.get('fecha_fin')
        
        try:
            empleado = Usuario.objects.get(id=empleado_id)
        except Usuario.DoesNotExist:
            return Response({"error": "Empleado no encontrado"}, status=404)

        # CORRECCIÓN: 'COMPLETADO' (Mayúsculas)
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

        return Response({"status": "ok", "id": liquidacion.id, "mensaje": "Pago registrado correctamente"})

class ReporteLiquidacionPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inicio = request.query_params.get('fecha_inicio')
        fin = request.query_params.get('fecha_fin')
        peluquero_id = request.query_params.get('peluquero_id')
        
        # 1. CAPTURAR EL USUARIO QUE IMPRIME (NOMBRE REAL)
        usuario_impresor = f"{request.user.nombre} {request.user.apellido}"

        es_historial = request.query_params.get('origen') == 'historial'

        empleados = Usuario.objects.filter(is_active=True, rol__nombre='Peluquero')
        if peluquero_id and peluquero_id != 'null':
            empleados = empleados.filter(id=peluquero_id)

        data_empleados = []

        for emp in empleados:
            filtros = {
                'peluquero': emp, 
                'estado': 'COMPLETADO', 
                'fecha__range': [inicio, fin]
            }
            
            if not es_historial:
                turnos = Turno.objects.filter(**filtros).exclude(liquidacion__isnull=False)
            else:
                turnos = Turno.objects.filter(**filtros)
            
            sueldo_fijo = float(emp.sueldo_fijo or 0)
            if not turnos.exists() and sueldo_fijo == 0:
                continue

            total_comision = sum(float(t.monto_comision) for t in turnos)
            
            lista_turnos = []
            for t in turnos:
                servicios_str = "<br/>".join([f"• {s.nombre} ({int(getattr(s, 'porcentaje_comision', 0))}%)" for s in t.servicios.all()])
                lista_turnos.append({
                    'fecha': t.fecha.strftime("%d/%m"),
                    'cliente': f"{t.cliente.nombre} {t.cliente.apellido}",
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

        # 2. PASAR 'usuario_impresor' A LA FUNCIÓN DEL PDF
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
        # Si es Admin o Recepcionista ve todo
        if user.rol and user.rol.nombre in ['Administrador', 'Recepcionista']:
            return PedidoWeb.objects.all().order_by('-fecha_creacion')
        # Si es cliente normal, solo ve sus pedidos
        return PedidoWeb.objects.filter(cliente=user).order_by('-fecha_creacion')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ✅ CAMBIO: Nace como PENDIENTE de pago, no PAGADO
            pedido = serializer.save(cliente=self.request.user, estado='PENDIENTE_PAGO') 

            # 3. Generar link MP
            mp_service = MercadoPagoService()
            detalles = pedido.detalles.all()
            resultado_mp = mp_service.crear_preferencia_compra_web(pedido, detalles)
            
            headers = self.get_success_headers(serializer.data)
            return Response({
                'mensaje': 'Pedido creado. Redirigiendo...',
                'pedido_id': pedido.id,
                'url_pago': resultado_mp['url_pago']
            }, status=status.HTTP_201_CREATED, headers=headers)

        except serializers.ValidationError as e:
            print(f"❌ ERROR DE VALIDACIÓN (STOCK): {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"❌ ERROR GENERAL: {e}")
            return Response(
                {'error': f'Ocurrió un error en el servidor: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        user = request.user
        if not (user.rol and user.rol.nombre in ['Administrador', 'Recepcionista']):
             return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)

        if nuevo_estado == PedidoWeb.ESTADO_CANCELADO and pedido.estado != PedidoWeb.ESTADO_CANCELADO:
            with transaction.atomic():
                for detalle in pedido.detalles.all():
                    detalle.producto.stock_actual += detalle.cantidad
                    detalle.producto.save()
        
        pedido.estado = nuevo_estado
        pedido.save()
        
        return Response({'status': 'Estado actualizado', 'nuevo_estado': pedido.get_estado_display()})