import logging
from rest_framework import viewsets, filters, generics, permissions, status, serializers
from django.conf import settings
from django.core.cache import cache
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
import django_filters
# Lazy imports: google.oauth2 se importa dentro de google_login()
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, F, Value, DecimalField, ExpressionWrapper, FloatField, Q, Avg, OuterRef, Subquery, IntegerField
from django.db import transaction
from django.http import HttpResponse, FileResponse
from django.db.models.functions import TruncDate, Coalesce
from .backup_service import (
    listar_backups,
    resumen_backups,
    generar_backup,
    verificar_backup,
    leer_log,
    resolver_ruta_backup,
    TIPOS_VALIDOS,
)
from django.utils.dateparse import parse_date
from django.utils import timezone
from .models import Auditoria, Servicio, Turno, Usuario, Producto, Liquidacion, PedidoWeb, ConfiguracionSistema, ConfiguracionLocal, Envio, Silla, SesionCaja, Venta, DetalleVenta, Pedido, HorarioAtencion
from .serializers import (AuditoriaSerializer, ServicioSerializer, TurnoSerializer, UsuarioSerializer,
                          ProductoCatalogoSerializer, LiquidacionSerializer, PedidoWebSerializer,
                          SillaSerializer, ConfiguracionLocalSerializer, EnvioSerializer, CrearEnvioSerializer,
                          HorarioAtencionSerializer)
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
class AuditoriaPaginacion(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 200


class EsAuditorPermiso(BasePermission):
    """
    Solo personal autorizado puede leer el historial de auditoría.
    Autorizados: superusuarios, staff, roles de gestión (Administrador,
    Recepcionista) o roles con el permiso VER_AUDITORIA.
    """
    ROLES_AUTORIZADOS = ('ADMINISTRADOR', 'RECEPCIONISTA', 'ADMIN')

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            return False
        if user.is_superuser or user.is_staff:
            return True
        rol = getattr(user, 'rol', None)
        if rol and rol.nombre.upper() in self.ROLES_AUTORIZADOS:
            return True
        try:
            return rol is not None and rol.permisos.filter(codigo__iexact='VER_AUDITORIA').exists()
        except Exception:
            return False


class AuditoriaFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateTimeFilter(field_name='fecha', lookup_expr='gte')
    fecha_hasta = django_filters.DateTimeFilter(field_name='fecha', lookup_expr='lte')
    usuario_nombre = django_filters.CharFilter(method='filtrar_usuario')
    objeto_id = django_filters.CharFilter(lookup_expr='icontains')
    id_operacion = django_filters.UUIDFilter(field_name='id_operacion', lookup_expr='exact')

    def filtrar_usuario(self, queryset, name, value):
        return queryset.filter(
            Q(usuario_nombre__icontains=value)
            | Q(usuario__nombre__icontains=value)
            | Q(usuario__apellido__icontains=value)
            | Q(usuario__correo__icontains=value)
        )

    class Meta:
        model = Auditoria
        fields = ['accion', 'resultado', 'modelo_afectado', 'usuario']


# Procesos automáticos internos y repetitivos que se excluyen del historial visible
# de Auditoría (siguen registrándose en la DB). Se identifican por su `contexto.proceso`
# y NO por `resultado=SISTEMA`: otros procesos automáticos sí son relevantes para el
# administrador (reposición de stock, reoferta, webhook de pagos) y permanecen visibles.
# Caso: el barrido de fidelización crea N PromocionReactivacion por ejecución (una por
# cliente inactivo) — ruido sin valor en el listado principal.
PROCESOS_AUTOMATICOS_OCULTOS = [
    'celery:procesar_reactivacion_clientes_inactivos',
]


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Auditoria.objects.select_related('usuario', 'usuario__rol').all()
    serializer_class = AuditoriaSerializer
    permission_classes = [EsAuditorPermiso]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuditoriaFilter
    search_fields = [
        'usuario__nombre', 'usuario__apellido', 'usuario__correo',
        'usuario_nombre', 'usuario_email', 'modelo_afectado', 'objeto_id',
        'accion', 'modulo', 'ip_address', 'endpoint', 'mensaje',
    ]
    ordering_fields = ['fecha', 'id']
    ordering = ['-fecha']
    pagination_class = AuditoriaPaginacion

    def get_queryset(self):
        qs = super().get_queryset()
        # Módulos: multi-selección (OR). Acepta `modulo=VENTAS&modulo=PAGOS`
        # (getlist) y mantiene compatibilidad con `modulo=VENTAS` (un solo valor).
        # Sin param de módulo = Todos. Mantiene el fallback legacy: eventos con
        # `modulo=''` pero cuyo modelo_afectado pertenece al módulo seleccionado.
        from .auditoria_service import MODULO_MODELO
        modulos = self.request.query_params.getlist('modulo')
        if modulos:
            q_modulos = Q()
            for mod in modulos:
                if not mod:
                    continue
                modelos_del_modulo = [m for m, _mod in MODULO_MODELO.items() if _mod == mod]
                q_modulos |= Q(modulo=mod) | (Q(modulo='') & Q(modelo_afectado__in=modelos_del_modulo))
            qs = qs.filter(q_modulos)
        # Autor histórico sin FK (usuario eliminado / SET_NULL): se filtra por el
        # snapshot exacto (nombre + email) y solo eventos sin usuario FK, para no
        # mezclar cuentas que compartan nombre (p. ej. dos "Luciano Bauer").
        nombre_snapshot = self.request.query_params.get('usuario_nombre_snapshot')
        if nombre_snapshot:
            _q_snapshot = Q(usuario__isnull=True) & Q(usuario_nombre__iexact=nombre_snapshot)
            email_snapshot = self.request.query_params.get('usuario_email_snapshot', '')
            if email_snapshot:
                _q_snapshot &= Q(usuario_email__iexact=email_snapshot)
            qs = qs.filter(_q_snapshot)
        # Excluye los procesos automáticos internos y repetitivos (ver
        # PROCESOS_AUTOMATICOS_OCULTOS): no ensucian el listado principal.
        # Se filtra por pk con subquery (no `exclude(contexto__proceso__in=...)`
        # directo: la mayoría de las filas no tiene clave `proceso` y el lookup
        # devuelve NULL, que un NOT IN descartaría; la subquery las preserva).
        qs = qs.exclude(
            pk__in=Auditoria.objects
            .filter(contexto__proceso__in=PROCESOS_AUTOMATICOS_OCULTOS)
            .values('pk')
        )
        # Cantidad de eventos que comparten el mismo id_operacion. Se expone como
        # `total_eventos_operacion` para que el frontend solo ofrezca "ver operación"
        # cuando realmente existe un grupo (total > 1). Subquery correlacionado
        # indexado por id_operacion: evita N+1 en listado y detalle.
        qs = qs.annotate(
            total_eventos_operacion=Coalesce(
                Subquery(
                    Auditoria.objects
                    .filter(id_operacion=OuterRef('id_operacion'))
                    .values('id_operacion')
                    .annotate(total=Count('id'))
                    .values('total'),
                    output_field=IntegerField()
                ),
                0
            )
        )
        return qs

    @action(detail=False, methods=['get'])
    def autores(self, request):
        """
        Autores reales de eventos de auditoría, para el selector "Usuario".
        Solo devuelve quienes realmente aparecen como autores de eventos
        (NO Usuario.objects.all()): un cliente que nunca generó eventos no
        figura. Cuando existe FK se identifica por el id del usuario (estable:
        distingue cuentas con el mismo nombre); los autores históricos cuyo
        usuario fue eliminado (SET_NULL) se identifican por su snapshot
        histórico (usuario_nombre + usuario_email).
        """
        base = Auditoria.objects.exclude(usuario__isnull=True)
        fk_rows = (base
                   .values('usuario')
                   .annotate(eventos=Count('id'))
                   .order_by('-eventos'))
        snap_rows = (Auditoria.objects
                     .filter(usuario__isnull=True)
                     .exclude(usuario_nombre__in=['', 'SISTEMA', 'Anónimo'])
                     .values('usuario_nombre', 'usuario_email')
                     .annotate(eventos=Count('id'))
                     .order_by('-eventos'))

        autores = []
        for r in fk_rows:
            u = Usuario.objects.filter(id=r['usuario']).first()
            if u is None:
                continue
            rol = u.rol.nombre if u.rol else 'Sin rol'
            nombre = f"{u.nombre} {u.apellido}".strip() or u.correo
            autores.append({
                'id': u.id,
                'nombre': nombre,
                'email': u.correo or '',
                'rol': rol,
                'eventos': r['eventos'],
                'origen': 'usuario',
            })
        for r in snap_rows:
            autores.append({
                'id': None,
                'nombre': r['usuario_nombre'],
                'email': r['usuario_email'] or '',
                'rol': 'Sin rol',
                'eventos': r['eventos'],
                'origen': 'snapshot',
            })
        return Response({'autores': autores})

    # NOTA — CONSULTAR RECURSIVO ELIMINADO:
    # list() y retrieve() de la propia Auditoría ya NO generan eventos CONSULTAR.
    # Antes, cada apertura del listado o de un detalle creaba un registro CONSULTAR
    # sobre el modelo Auditoria con un id_operacion propio (siempre singleton, se
    # verificó: 0 de 35 comparten UUID con otro evento), contaminando el historial
    # que se está leyendo y confundiendo la trazabilidad ("ver operación" generaba
    # más ruido). La auditoría de consultas del resto del sistema no se ve afectada:
    # el único lugar que producía CONSULTAR era este ViewSet y solo para Auditoria.
    # (Este ViewSet hereda de ReadOnlyModelViewSet: list/retrieve siguen intactos.)

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
        
        # 💳 MEDIO DE PAGO del egreso (fallback a EFECTIVO para compatibilidad con llamadas antiguas)
        metodo_pago = (data.get('metodo_pago') or 'EFECTIVO').upper()
        if metodo_pago not in ('EFECTIVO', 'MERCADO_PAGO'):
            return Response(
                {"error": f"Medio de pago inválido: {metodo_pago}. Use EFECTIVO o MERCADO_PAGO."},
                status=400
            )
        
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

        # 🔥 Validar que la liquidación no deje el saldo del método seleccionado en negativo
        from decimal import Decimal
        from .views import validar_egreso_saldo
        nombre_metodo = 'Mercado Pago' if metodo_pago == 'MERCADO_PAGO' else 'Efectivo'
        ok, disponible, faltante = validar_egreso_saldo(sesion_abierta, metodo_pago, Decimal(str(total)))
        if not ok:
            return Response({
                "error": (
                    f"Saldo insuficiente de {nombre_metodo}. Disponible: ${float(disponible):,.2f}. "
                    f"Egreso: ${float(total):,.2f}. Faltan: ${float(faltante):,.2f}. "
                    f"Registrá primero un ingreso (ej. Aporte del dueño) y volvé a liquidar."
                )
            }, status=400)

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
                    metodo_pago=metodo_pago,
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
                frontend_origen = request.META.get('HTTP_ORIGIN') or request.META.get('HTTP_REFERER') or settings.FRONTEND_URL
                pedido = serializer.save(cliente=self.request.user, estado='PENDIENTE_PAGO', frontend_origen=frontend_origen) 
                
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
        # Nota: Este perform_create es redundante porque ya pasas el cliente en el save() 
        # dentro de create(), pero no molesta dejarlo.
        serializer.save(cliente=self.request.user)

    # ✅ NUEVO ENDPOINT: Para que el cliente solicite la cancelación
    @action(detail=True, methods=['post'])
    def solicitar_cancelacion(self, request, pk=None):
        pedido = self.get_object() # Seguro porque get_queryset ya filtra por cliente
        motivo = request.data.get('motivo', 'Sin motivo especificado')

        estados_validos = [
            PedidoWeb.ESTADO_PENDIENTE_PAGO, 
            PedidoWeb.ESTADO_PAGADO, 
            PedidoWeb.ESTADO_PREPARACION
        ]
        
        if pedido.estado not in estados_validos:
            return Response(
                {"error": "El pedido ya está procesado y no se puede solicitar su cancelación."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        pedido.estado = PedidoWeb.ESTADO_SOLICITA_CANCELACION
        pedido.obs_cancelacion = f"SOLICITUD DE CLIENTE: {motivo}"
        pedido.save()

        print(f"⚠️ El cliente ID {request.user.id} solicitó cancelar el pedido #{pedido.id}")
        return Response({"mensaje": "Solicitud de cancelación enviada correctamente."})

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        repartidor = request.data.get('repartidor')
        motivo_cancelacion = request.data.get('motivo_cancelacion')
        obs_cancelacion = request.data.get('obs_cancelacion')

        if not nuevo_estado:
            return Response({"error": "Estado no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔥 LÓGICA DE CANCELACIÓN Y REEMBOLSO 🔥
        if nuevo_estado == 'CANCELADO':
            if pedido.estado == 'CANCELADO':
                return Response({"error": "El pedido ya está cancelado."}, status=status.HTTP_400_BAD_REQUEST)

            from .models import SesionCaja, MovimientoCaja
            sesion_abierta = SesionCaja.objects.filter(fecha_cierre__isnull=True).first()
            if not sesion_abierta:
                return Response(
                    {"error": "Debe abrir una caja antes de procesar una cancelación y un reembolso."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            reembolso_exitoso = False
            mensaje_obs_final = obs_cancelacion or 'Cancelación aprobada por administrador'

            # 1. Intentar hacer el reembolso en Mercado Pago
            if pedido.mp_payment_id:
                try:
                    from .mercadopago_service import MercadoPagoService
                    mp_service = MercadoPagoService()
                    respuesta_mp = mp_service.reembolsar_pago(pedido.mp_payment_id)
                    
                    if respuesta_mp.get("status") in ["approved", "refunded", "pending"]:
                        mensaje_obs_final = "Reembolso automático realizado con éxito en Mercado Pago."
                        reembolso_exitoso = True
                    else:
                        mensaje_obs_final = f"Reembolso automático omitido (Sandbox/Credenciales). Se requiere devolución manual."
                        
                except Exception as e:
                    mensaje_obs_final = f"Entorno de Prueba: Reembolso omitido. Se requiere devolución manual."

            # 2. Cancelamos, devolvemos stock y egresamos de caja
            with transaction.atomic():
                for detalle in pedido.detalles.all():
                    producto = detalle.producto
                    if producto:
                        from .models import HistorialStock
                        stock_anterior = producto.stock_actual
                        producto.stock_actual += detalle.cantidad
                        producto.save()

                        HistorialStock.objects.create(
                            producto=producto,
                            cantidad_anterior=stock_anterior,
                            cantidad_nueva=producto.stock_actual,
                            motivo=f"Reingreso por Pedido Web Cancelado (#{pedido.id})",
                            usuario=request.user,
                            tipo_ajuste='DEVOLUCION'
                        )

                # 💵 REGISTRAR EGRESO DE CAJA
                # 🔥 CORREGIDO: pedido.cliente.nombre en lugar de pedido.cliente_nombre
                nombre_cliente = pedido.cliente.nombre if pedido.cliente else "Cliente Web"
                
                MovimientoCaja.objects.create(
                    sesion_caja=sesion_abierta,
                    tipo='EGRESO',
                    metodo_pago='MERCADO_PAGO' if pedido.mp_payment_id else 'EFECTIVO',
                    concepto='DEVOLUCION',
                    monto=pedido.total,
                    descripcion=f"Devolución Pedido Web #{pedido.id} ({nombre_cliente})"
                )

                pedido.estado = 'CANCELADO'
                pedido.motivo_cancelacion = motivo_cancelacion or 'Solicitud de Cliente'
                pedido.obs_cancelacion = mensaje_obs_final
                pedido.save()

            return Response({
                "message": "Pedido cancelado.", 
                "reembolso_exitoso": reembolso_exitoso
            })

        # --- Lógica para el resto de los estados ---
        whatsapp_enviado = False
        if nuevo_estado == 'EN_CAMINO':
            pedido.datos_entrega_interna = repartidor

            # WhatsApp al cliente + tiempo estimado por OSRM
            if pedido.tipo_entrega == 'MOTO' and pedido.latitud_entrega and pedido.longitud_entrega:
                try:
                    from .envio_service import distancia_por_ruta
                    from .models import ConfiguracionLocal
                    config_local = ConfiguracionLocal.get_solo()
                    _km, _ruta_coords, duracion_segundos = distancia_por_ruta(
                        float(config_local.latitud_local),
                        float(config_local.longitud_local),
                        float(pedido.latitud_entrega),
                        float(pedido.longitud_entrega),
                    )
                    tiempo_estimado = round(duracion_segundos / 60) if duracion_segundos > 0 else 0
                    if tiempo_estimado > 0:
                        pedido.datos_entrega_interna = repartidor
                        pedido.tiempo_estimado_minutos = tiempo_estimado
                        from .tasks import enviar_whatsapp_pedido_en_camino
                        enviar_whatsapp_pedido_en_camino.delay(pedido.id, repartidor, tiempo_estimado)
                        whatsapp_enviado = True
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"❌ Error al calcular OSRM/encolar WhatsApp EN_CAMINO #{pedido.id}: {e}")

        pedido.estado = nuevo_estado
        pedido.save()

        return Response({
            "message": f"Estado actualizado a {nuevo_estado}",
            "whatsapp_enviado": whatsapp_enviado,
        })
    
class SillaViewSet(viewsets.ModelViewSet):
    queryset = Silla.objects.all().order_by('orden')
    serializer_class = SillaSerializer
    permission_classes = [IsAuthenticated]

class EsAdminODescartar(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and getattr(request.user, 'rol', None) and request.user.rol.nombre.upper() == 'ADMINISTRADOR'

class HorarioAtencionViewSet(viewsets.ModelViewSet):
    queryset = HorarioAtencion.objects.all()
    serializer_class = HorarioAtencionSerializer
    permission_classes = [EsAdminODescartar]

    def perform_update(self, serializer):
        serializer.save()
        cache.delete('horarios_atencion')
        cache.delete('horarios_atencion_values')

    def perform_create(self, serializer):
        serializer.save()
        cache.delete('horarios_atencion')
        cache.delete('horarios_atencion_values')

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete('horarios_atencion')
        cache.delete('horarios_atencion_values')

class ConfigWebView(APIView):
    permission_classes = [AllowAny] # Público, para que lo lea el Home y Checkout

    def _url_or_none(self, request, file_field):
        if not file_field:
            return None
        return request.build_absolute_uri(file_field.url)

    def get(self, request):
        config = ConfiguracionSistema.objects.first()

        # Horarios cacheados (la cache se invalida al editar en HorarioAtencionViewSet)
        horarios = cache.get('horarios_atencion')
        if horarios is None:
            horarios = HorarioAtencionSerializer(HorarioAtencion.objects.all(), many=True).data
            cache.set('horarios_atencion', horarios, timeout=3600)

        if config:
            return Response({
                'costo_moto': float(config.costo_envio_moto),
                'razon_social': config.razon_social,
                'direccion': config.direccion,
                'telefono': config.telefono,
                'email': config.email,
                'logo': self._url_or_none(request, config.logo),
                'imagen_portada': self._url_or_none(request, config.imagen_portada),
                'imagen_login': self._url_or_none(request, config.imagen_login),
                'mostrar_imagen_login': config.mostrar_imagen_login,
                'horarios': horarios,
            })
        else:
            return Response({
                'costo_moto': 1500.00,
                'razon_social': 'Los Últimos Serán Los Primeros',
                'direccion': 'Avenida Libertador 600, San Vicente - Misiones',
                'telefono': '3755-72716',
                'email': 'contacto@hairsoft.com',
                'logo': None,
                'imagen_portada': None,
                'horarios': horarios,
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
            # 🔥 CORREGIDO (doble conteo): SOLO ventas de mostrador (PRODUCTO) no anuladas.
            # Las ventas tipo 'TURNO' (automáticas duplicadas + legacy fantasma) son registros
            # documentales que NO representan facturación real: quedan EXCLUIDAS de este módulo.
            # No se modifican ni eliminan en BD, simplemente no participan del cálculo.
            ventas_qs = Venta.objects.filter(
                fecha__range=[f_inicio_dt, f_fin_dt],
                anulada=False,
                tipo='PRODUCTO'
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

            # Totales: la facturación bruta NO incluye señas retenidas (indicador separado).
            ingreso_total_bruto = ingreso_ventas + ingreso_turnos_completados + ingreso_pedidos_web
            # 🔥 CORREGIDO: el denominador usa EXACTAMENTE las mismas operaciones del
            # numerador (facturación). Las señas retenidas NO son operaciones de venta
            # y las ventas tipo TURNO quedaron excluidas de `ventas_qs`.
            total_operaciones = cantidad_ventas + cantidad_turnos_completados + cantidad_pedidos_web
            ticket_promedio = (ingreso_total_bruto / total_operaciones) if total_operaciones > 0 else 0

            # =========================================================
            # 2. MEDIOS DE PAGO UNIFICADOS
            # =========================================================
            medios_dict = {}
            # 🔥 CORREGIDO: fuentes = facturación (ventas PRODUCTO + turnos COMPLETADOS + web).
            # Las ventas tipo TURNO quedan excluidas (ventas_qs ya filtra PRODUCTO) y las
            # señas retenidas NO se mezclan acá (son dinero retenido por cancelación, no una
            # venta; viven en el bloque "Ingresos por Turnos").
            # Ventas
            for v in ventas_qs.values('medio_pago__nombre').annotate(total=Sum('total')):
                mp = (v['medio_pago__nombre'] or 'OTRO').upper().replace('_', ' ')
                medios_dict[mp] = medios_dict.get(mp, 0) + float(v['total'] or 0)
            # Turnos
            for t in turnos_completados_qs.values('medio_pago').annotate(total=Sum('monto_total')):
                mp = (t['medio_pago'] or 'OTRO').upper().replace('_', ' ')
                medios_dict[mp] = medios_dict.get(mp, 0) + float(t['total'] or 0)
            # Pedidos Web: el único flujo de pago es Mercado Pago
            # (checkout crear_preferencia_compra_web + pago_exitoso/webhook con mp_payment_id)
            if ingreso_pedidos_web > 0:
                medios_dict['MERCADO PAGO'] = medios_dict.get('MERCADO PAGO', 0) + ingreso_pedidos_web

            grafico_medios = [{'medio': k, 'total': v} for k, v in sorted(medios_dict.items(), key=lambda item: item[1], reverse=True)]

            # =========================================================
            # 3. SERVICIO ESTRELLA + RANKING (SOLO turnos completados)
            #    🔥 CORREGIDO (doble conteo): se eliminó la fuente duplicada
            #    DetalleVenta/ventas (las ventas tipo TURNO ya no se cuentan).
            #    El POS no vende servicios, así que los turnos completados
            #    son la única fuente legítima de servicios realizados.
            # =========================================================
            from decimal import Decimal
            servicio_stats = {}

            # Turnos completados
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

            servicios_mas_elegidos = sorted(
                [
                    {'nombre': v['nombre'], 'cantidad': v['cantidad'], 'ingreso': float(v['ingreso'])}
                    for v in servicio_stats.values()
                ],
                key=lambda x: (x['cantidad'], x['ingreso']),
                reverse=True
            )[:5]

            if servicios_mas_elegidos:
                mejor = servicios_mas_elegidos[0]
                servicio_top = {
                    'nombre': mejor['nombre'],
                    'cantidad': mejor['cantidad'],
                    'ingreso': mejor['ingreso']
                }
            else:
                servicio_top = {'nombre': 'Ninguno', 'cantidad': 0, 'ingreso': 0.0}

            # =========================================================
            # 4. PRODUCTO ESTRELLA + RANKING (solo ventas PRODUCTO)
            # =========================================================
            productos_vendidos_qs = DetalleVenta.objects.filter(
                venta__fecha__range=[f_inicio_dt, f_fin_dt],
                venta__anulada=False,
                venta__tipo='PRODUCTO',
                producto__isnull=False
            ).values('producto__nombre').annotate(
                cantidad=Sum('cantidad'),
                ingreso=Sum('subtotal')
            ).order_by('-cantidad')

            productos_mas_vendidos = [
                {
                    'nombre': p['producto__nombre'],
                    'cantidad': p['cantidad'],
                    'ingreso': float(p['ingreso'] or 0)
                }
                for p in productos_vendidos_qs[:5]
            ]

            producto_top = productos_vendidos_qs.first()

            # =========================================================
            # 5. STOCK ESTANCADO
            # =========================================================
            productos_vendidos_ids = DetalleVenta.objects.filter(
                venta__fecha__range=[f_inicio_dt, f_fin_dt],
                venta__anulada=False,
                venta__tipo='PRODUCTO',
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
            for cid in clientes_ids_unicos:
                # Contar total de turnos COMPLETADOS en TODA la historia para este cliente
                total_turnos_historia = Turno.objects.filter(
                    cliente_id=cid,
                    estado='COMPLETADO'
                ).count()
                if total_turnos_historia > 1:
                    recurrentes += 1
                else:
                    nuevos += 1

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
                    ],
                    'servicios_mas_elegidos': servicios_mas_elegidos,
                    'productos_mas_vendidos': productos_mas_vendidos,
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

#google login
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    token = request.data.get('token')
    
    if not token:
        return Response({'error': 'Token no proporcionado'}, status=400)

    try:
        # 1. Validamos contra Google (import lazy para no romper tests)
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
        
        correo = idinfo.get('email')
        nombre = idinfo.get('given_name', '')
        apellido = idinfo.get('family_name', '')

        usuario = Usuario.objects.filter(correo=correo).first()
        
        if usuario:
            # ✅ ESCENARIO A: YA EXISTE
            token_obj, created = Token.objects.get_or_create(user=usuario)
            
            # 🔥 REGISTRO BLINDADO DE AUDITORÍA (LOGIN GOOGLE) 🔥
            try:
                from .auditoria_service import AuditoriaService
                
                nombre_completo = f"{getattr(usuario, 'nombre', '')} {getattr(usuario, 'apellido', '')}".strip()
                if not nombre_completo:
                    nombre_completo = getattr(usuario, 'correo', str(usuario))
                    
                detalles_login = {
                    'Mensaje del Sistema': {'tipo': 'VALOR', 'valor': f'El usuario {nombre_completo} inició sesión mediante Google.'}
                }
                
                AuditoriaService.registrar(
                    accion='LOGIN_GOOGLE',
                    modelo_afectado='SesionDeUsuario',
                    objeto_id=usuario.pk,
                    detalles=detalles_login,
                    usuario=usuario,
                )
            except Exception as e:
                print("❌ ERROR EN AUDITORIA DE LOGIN GOOGLE:")
                import traceback
                traceback.print_exc()

            # Respondemos EXACTAMENTE igual que el login tradicional
            return Response({
                'status': 'ok',
                'message': 'Login exitoso con Google',
                'token': token_obj.key,
                'user_id': usuario.id,
                'nombre': getattr(usuario, 'nombre', ''),
                'apellido': getattr(usuario, 'apellido', ''),
                'rol': usuario.rol.nombre.upper() if getattr(usuario, 'rol', None) else 'SIN_ROL',
            })
        else:
            # 🟡 ESCENARIO B: ES NUEVO -> 202
            return Response({
                'requiere_completar_perfil': True,
                'datos_google': {
                    'correo': correo,
                    'nombre': nombre,
                    'apellido': apellido
                }
            }, status=202) 

    except ValueError:
        return Response({'error': 'Token de Google inválido o expirado'}, status=401)

# ============================================
# ENVÍOS (Motomandados)
# ============================================

class ConfiguracionLocalView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        config = ConfiguracionLocal.get_solo()
        serializer = ConfiguracionLocalSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        config = ConfiguracionLocal.get_solo()
        serializer = ConfiguracionLocalSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class CalcularEnvioView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        lat = request.data.get('latitud')
        lng = request.data.get('longitud')
        if lat is None or lng is None:
            return Response({'error': 'latitud y longitud son requeridos'}, status=400)
        from .envio_service import calcular_costo_envio
        costo, distancia, dentro_cobertura, ruta_coords, tiempo_estimado_minutos = calcular_costo_envio(float(lat), float(lng))
        return Response({
            'costo_envio': costo,
            'distancia_km': distancia,
            'dentro_cobertura': dentro_cobertura,
            'ruta_coords': ruta_coords,
            'tiempo_estimado_minutos': tiempo_estimado_minutos,
        })

class EnvioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Envio.objects.all().select_related('venta').order_by('-fecha_creacion')

    def get_serializer_class(self):
        if self.action == 'create':
            return CrearEnvioSerializer
        return EnvioSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        envio = self.get_object()
        nuevo_estado = request.data.get('estado')
        if nuevo_estado not in dict(Envio.ESTADO_CHOICES):
            return Response({'error': 'Estado inválido'}, status=400)
        envio.estado = nuevo_estado
        envio.save()
        return Response(EnvioSerializer(envio).data)


# ============================================
# Copias de seguridad (solo ADMINISTRADOR)
# ============================================
def _es_administrador(user):
    return getattr(user, 'rol', None) and user.rol.nombre.upper() == 'ADMINISTRADOR'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listado_backups(request):
    if not _es_administrador(request.user):
        return Response({'error': 'No autorizado'}, status=403)
    backups = listar_backups()
    return Response({'backups': backups, **resumen_backups(backups)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generar_un_backup(request):
    if not _es_administrador(request.user):
        return Response({'error': 'No autorizado'}, status=403)
    tipo = request.data.get('tipo')
    if tipo not in TIPOS_VALIDOS:
        return Response({'error': 'Tipo inválido. Use Diario, Semanal o Mensual.'}, status=400)
    try:
        resultado = generar_backup(tipo)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    return Response(resultado, status=200 if resultado.get('ok') else 500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verificar_un_backup(request, ruta):
    if not _es_administrador(request.user):
        return Response({'error': 'No autorizado'}, status=403)
    try:
        resultado = verificar_backup(ruta)
    except ValueError as e:
        return Response({'error': str(e)}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    return Response(resultado, status=200 if resultado.get('ok') else 500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def descargar_un_backup(request, ruta):
    if not _es_administrador(request.user):
        return Response({'error': 'No autorizado'}, status=403)
    try:
        archivo = resolver_ruta_backup(ruta)
    except ValueError as e:
        return Response({'error': str(e)}, status=404)
    return FileResponse(open(str(archivo), 'rb'), as_attachment=True, filename=archivo.name)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ultimos_registros_backup(request):
    if not _es_administrador(request.user):
        return Response({'error': 'No autorizado'}, status=403)
    return Response({'registros': leer_log()})