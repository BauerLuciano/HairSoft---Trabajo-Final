from rest_framework import viewsets, filters, generics, permissions, status, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import HttpResponse
from .models import Auditoria, Servicio, Turno, Usuario, Producto, Liquidacion, PedidoWeb
from .serializers import AuditoriaSerializer, ServicioSerializer, TurnoSerializer, UsuarioSerializer, ProductoCatalogoSerializer, LiquidacionSerializer, PedidoWebSerializer
import io
import datetime
from reportlab.lib import colors
from reportlab.pdfgen import canvas

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
        # Esto soluciona el Error 400
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
        
        # 1. Detectar si viene del historial (parametro 'origen')
        es_historial = request.query_params.get('origen') == 'historial'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # --- FUNCIÓN BLINDADA DEL SELLO "PAGADO" ---
        def dibujar_sello(canvas, doc):
            canvas.saveState()
            canvas.translate(300, 400) 
            canvas.rotate(25) 
            
            # Color Rojo Transparente
            c_rojo = colors.Color(0.8, 0, 0, alpha=0.3)
            canvas.setStrokeColor(c_rojo)
            canvas.setFillColor(c_rojo)
            canvas.setLineWidth(5)
            
            # Recuadro
            canvas.roundRect(-100, -40, 200, 80, 10, stroke=1, fill=0)
            
            # Texto PAGADO
            canvas.setFont("Helvetica-Bold", 40)
            canvas.drawCentredString(0, -10, "PAGADO")
            
            # Fecha (Usamos datetime.datetime.now() para evitar el error de atributo)
            canvas.setFont("Helvetica-Bold", 10)
            fecha_hoy = datetime.datetime.now().strftime("%d/%m/%Y")
            canvas.drawCentredString(0, -30, f"LIQUIDADO: {fecha_hoy}")
            
            canvas.restoreState()
        # ---------------------------------------------

        # HEADER DEL PDF
        logo_path = "logo_barberia.jpg"
        try:
            logo = ImageRL(logo_path, width=25*mm, height=25*mm)
        except:
            logo = Paragraph("HS", styles['Heading1'])

        title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, fontName='Helvetica-Bold', spaceAfter=4)
        subtitle_style = ParagraphStyle('HeaderSub', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#555555'))
        
        # Título cambia si es Historial
        titulo_texto = "COMPROBANTE DE PAGO" if es_historial else "LIQUIDACIÓN DE SUELDOS (PRELIMINAR)"

        header_data = [[
            logo, 
            [
                Paragraph("LOS ÚLTIMOS SERÁN LOS PRIMEROS", title_style),
                Paragraph("Sistema de Gestión: <b>HairSoft</b>", subtitle_style),
                Spacer(1, 6),
                Paragraph(f"{titulo_texto}<br/>Período: {inicio} al {fin}", subtitle_style)
            ]
        ]]
        
        t_header = Table(header_data, colWidths=[30*mm, 130*mm])
        t_header.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("<hr width='100%' color='#0ea5e9' size='2'/>", styles['Normal']))
        elements.append(Spacer(1, 20))

        # OBTENCIÓN DE DATOS
        empleados = Usuario.objects.filter(is_active=True, rol__nombre='Peluquero')
        if peluquero_id and peluquero_id != 'null':
            empleados = empleados.filter(id=peluquero_id)

        grand_total = 0
        width_resumen = [80*mm, 80*mm]
        width_detalle = [20*mm, 40*mm, 75*mm, 25*mm]

        hay_datos = False

        for emp in empleados:
            filtros = {
                'peluquero': emp, 
                'estado': 'COMPLETADO', 
                'fecha__range': [inicio, fin]
            }
            
            # Lógica: Si es historial mostramos todo lo del rango. Si es preliminar, solo lo no pagado.
            if not es_historial:
                turnos = Turno.objects.filter(**filtros).exclude(liquidacion__isnull=False)
            else:
                turnos = Turno.objects.filter(**filtros)
            
            if not turnos.exists():
                continue

            hay_datos = True
            total_comision = sum(float(t.monto_comision) for t in turnos)
            sueldo_fijo = float(emp.sueldo_fijo or 0)
            total_a_pagar = total_comision + sueldo_fijo
            
            grand_total += total_a_pagar

            # SECCIÓN DEL EMPLEADO
            elements.append(Paragraph(f"<b>PROFESIONAL: {emp.nombre} {emp.apellido}</b>", styles['Heading3']))
            elements.append(Spacer(1, 3))

            # Tabla Resumen de Montos
            resumen_data = [
                ['CONCEPTO', 'MONTO'],
                ['Comisiones por Servicios', f"${total_comision:,.2f}"]
            ]
            if sueldo_fijo > 0:
                resumen_data.append(['Sueldo Fijo / Base', f"${sueldo_fijo:,.2f}"])
            
            # EL TOTAL A PAGAR (DESTACADO)
            resumen_data.append(['TOTAL A PERCIBIR', f"${total_a_pagar:,.2f}"])

            t_res = Table(resumen_data, colWidths=width_resumen)
            t_res.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')), 
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                ('BACKGROUND', (0,1), (-1,-2), colors.HexColor('#f1f5f9')), 
                ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
                # Estilo Fila Total
                ('TEXTCOLOR', (0,-1), (-1,-1), colors.HexColor('#16a34a')), 
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,-1), (-1,-1), 12),
                ('TOPPADDING', (0,-1), (-1,-1), 8),
                ('BOTTOMPADDING', (0,-1), (-1,-1), 8),
                ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            elements.append(t_res)
            elements.append(Spacer(1, 10))

            # Tabla Detalle de Turnos
            service_style = ParagraphStyle('ServiceList', parent=styles['Normal'], fontSize=8, leading=10)
            data = [[
                Paragraph('<b>Fecha</b>', styles['Normal']), 
                Paragraph('<b>Cliente</b>', styles['Normal']), 
                Paragraph('<b>Servicios</b>', styles['Normal']), 
                Paragraph('<b>Comisión</b>', styles['Normal'])
            ]]
            
            for t in turnos:
                s_items = []
                for s in t.servicios.all():
                    pct = getattr(s, 'porcentaje_comision', 0)
                    s_items.append(f"&bull; {s.nombre} <b>({int(pct)}%)</b>")
                servicios_vertical = "<br/>".join(s_items)

                data.append([
                    t.fecha.strftime("%d/%m"),
                    Paragraph(f"{t.cliente.nombre}<br/>{t.cliente.apellido}", styles['Normal']),
                    Paragraph(servicios_vertical, service_style),
                    f"${t.monto_comision}"
                ])
            
            t_det = Table(data, colWidths=width_detalle)
            t_det.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')), 
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
            ]))
            elements.append(t_det)
            elements.append(Spacer(1, 25))

        if not hay_datos:
            elements.append(Paragraph("No hay datos para mostrar.", styles['Normal']))
        else:
            elements.append(Spacer(1, 10))
            if not peluquero_id or peluquero_id == 'null':
                total_style = ParagraphStyle('TotalFinal', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#0f172a'), alignment=TA_RIGHT, rightIndent=12)
                elements.append(Paragraph(f"TOTAL GENERAL LIQUIDADO: ${grand_total:,.2f}", total_style))

        # GENERACIÓN DEL PDF
        try:
            if es_historial:
                # Aplicamos el sello si viene del historial
                doc.build(elements, onFirstPage=dibujar_sello, onLaterPages=dibujar_sello)
            else:
                doc.build(elements)
        except Exception as e:
            # Fallback por si reportlab falla al construir
            print(f"Error generando PDF: {e}")
            return Response({'error': str(e)}, status=500)
            
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf') 
    
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
        # 1. Validar datos
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            pedido = serializer.save(cliente=self.request.user, estado=PedidoWeb.ESTADO_PAGADO) 

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