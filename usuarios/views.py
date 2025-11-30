from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.db.models import Count, Sum, F, Q
from django.contrib.auth.hashers import make_password
# 🛑 CORRECCIÓN APLICADA: Importar authenticate y login
from django.contrib.auth import authenticate, login 
from rest_framework import viewsets, status, generics 
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response 
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Rol, Permiso, Usuario, Servicio, CategoriaProducto, CategoriaServicio, Producto, Turno, Proveedor, Venta, DetalleVenta, MetodoPago, Pedido, DetallePedido, ListaPrecioProveedor, HistorialPrecios, Marca, InteresTurnoLiberado, Cotizacion, SolicitudPresupuesto
from .mercadopago_service import MercadoPagoService
import json, re, requests
from .serializers import LoginSerializer, ProveedorSerializer, ProductoSerializer, VentaSerializer, DetalleVentaSerializer, CategoriaProductoSerializer, MetodoPagoSerializer, VentaUpdateSerializer, CategoriaServicioSerializer, PedidoSerializer, DetallePedidoSerializer, PedidoRecepcionSerializer, PedidoBusquedaSerializer, ListaPrecioProveedorSerializer, HistorialPreciosSerializer, PrecioSugeridoSerializer, ActualizarListaPreciosSerializer, CotizacionExternaSerializer, SolicitudPresupuestoSerializer
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .pdf_utils import generar_comprobante_venta
from decimal import Decimal
import secrets, logging

# Configuración del logger
logger = logging.getLogger(__name__)

# Modelos y formularios
from .models import (
    Usuario,
    Servicio,
    Turno,
    Producto,
    CategoriaProducto,
    CategoriaServicio
)
from .forms import UsuarioForm

# ================================
# Funciones Auxiliares
# ================================

def get_rol_abreviado(rol_largo):
    """Mapea los roles largos del modelo a los códigos cortos esperados por el frontend."""
    if not rol_largo:
        return 'CLI'
    rol = rol_largo.upper()
    if rol == 'ADMINISTRADOR':
        return 'ADMIN'
    elif rol == 'RECEPCIONISTA':
        return 'REC'
    elif rol == 'PELUQUERO':
        return 'PEL'
    elif rol == 'CLIENTE':
        return 'CLI'
    return 'CLI'


# ================================
# Usuarios
# ================================
@csrf_exempt
def listado_usuarios(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    q = request.GET.get('q', '').strip()
    rol_id = request.GET.get('rol_id')  # 🔹 nuevo parámetro para filtrar por rol
    usuarios = Usuario.objects.select_related('rol').all()
    
    if q:
        usuarios = usuarios.filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(dni__icontains=q)
        )
    if rol_id:
        usuarios = usuarios.filter(rol_id=rol_id)

    data = [
        {
            'id': u.id,
            'nombre': u.nombre or '',
            'apellido': u.apellido or '',
            'dni': u.dni or '',
            'telefono': u.telefono or '',
            'rol_id': u.rol.id if u.rol else None,
            'rol_nombre': u.rol.nombre if u.rol else None,
            'correo': u.correo or '',
            'estado': (u.estado or 'ACTIVO').upper(),
            'fecha_creacion': u.fecha_creacion.isoformat() if u.fecha_creacion else ''
        } for u in usuarios
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def crear_usuario(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        print("📦 DATOS RECIBIDOS:", data)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

    # =========================
    # 🔹 CAMPOS OBLIGATORIOS
    # =========================
    required_fields = ['nombre', 'apellido', 'dni', 'correo', 'contrasena']
    for field in required_fields:
        if not data.get(field):
            return JsonResponse({
                'status': 'error',
                'message': f'El campo {field} es obligatorio'
            }, status=400)

    # =========================
    # 🔹 VALIDACIONES
    # =========================

    # Nombre y apellido → solo letras
    if not re.match(r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}$', data['nombre']):
        return JsonResponse({'status': 'error', 'message': 'El nombre solo debe contener letras y espacios (2-50 caracteres)'}, status=400)

    if not re.match(r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}$', data['apellido']):
        return JsonResponse({'status': 'error', 'message': 'El apellido solo debe contener letras y espacios (2-50 caracteres)'}, status=400)

    # DNI → solo dígitos, 7 a 9 números
    if not re.match(r'^\d{7,9}$', data['dni']):
        return JsonResponse({'status': 'error', 'message': 'El DNI debe contener solo números (7-9 dígitos)'}, status=400)

    # Teléfono → opcional, pero formato válido
    telefono = data.get('telefono', '')
    if telefono and not re.match(r'^\+?\d{6,15}$', telefono):
        return JsonResponse({'status': 'error', 'message': 'El teléfono solo puede contener números y opcional "+" (6-15 dígitos)'}, status=400)

    # Correo → validación real
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['correo']):
        return JsonResponse({'status': 'error', 'message': 'Correo electrónico inválido'}, status=400)

    # Contraseña → mínimo 6 caracteres
    if len(data['contrasena']) < 6:
        return JsonResponse({'status': 'error', 'message': 'La contraseña debe tener al menos 6 caracteres'}, status=400)

    # =========================
    # 🔹 EVITAR DUPLICADOS
    # =========================
    if Usuario.objects.filter(correo=data['correo']).exists():
        return JsonResponse({'status': 'error', 'message': 'Ya existe un usuario con ese correo'}, status=400)

    if Usuario.objects.filter(dni=data['dni']).exists():
        return JsonResponse({'status': 'error', 'message': 'Ya existe un usuario con ese DNI'}, status=400)

    # =========================
    # 🔹 REGLA: UN SOLO ADMINISTRADOR ACTIVO
    # =========================
    rol_id = data.get('rol') or data.get('rol_id')
    data['rol'] = rol_id if rol_id else None

    if rol_id:
        rol = Rol.objects.filter(pk=rol_id).first()
        if rol and rol.nombre.upper() == 'ADMINISTRADOR':
            if Usuario.objects.filter(rol__nombre__iexact='ADMINISTRADOR', estado='ACTIVO').exists():
                return JsonResponse({'status': 'error', 'message': 'Ya existe un administrador activo'}, status=400)

    # =========================
    # 🔹 HASH DE CONTRASEÑA
    # =========================
    data['contrasena'] = make_password(data['contrasena'])

    # =========================
    # 🔹 CREAR USUARIO
    # =========================
    try:
        usuario = Usuario.objects.create(
            nombre=data['nombre'],
            apellido=data['apellido'],
            dni=data['dni'],
            telefono=telefono,
            correo=data['correo'],
            contrasena=data['contrasena'],
            rol_id=rol_id,
            estado=data.get('estado', 'ACTIVO')
        )

        return JsonResponse({'status': 'ok', 'id': usuario.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error al crear el usuario: {str(e)}'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_auth(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    correo = validated_data.get('username')
    contrasena = validated_data.get('password')

    user = authenticate(username=correo, password=contrasena) # Django usa 'username' interno

    if user:
        # ✅ Generar o recuperar token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'status': 'ok',
            'message': 'Login exitoso',
            'token': token.key,  # <--- ¡AQUÍ ESTÁ LA CLAVE! 🔑
            'user_id': user.id,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'rol': user.rol.nombre.upper() if user.rol else 'SIN_ROL',
        })
    else:
        return Response({'error': 'Credenciales inválidas'}, status=401)
    
@csrf_exempt
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        print(" DATOS EDITAR USUARIO:", data)  # Debug
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

    # ✅ USAR EL NUEVO FORMULARIO MEJORADO
    form = UsuarioForm(data, instance=usuario)
    
    if form.is_valid():
        try:
            usuario_actualizado = form.save()
            return JsonResponse({'status': 'ok', 'id': usuario_actualizado.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al guardar el usuario: {str(e)}'}, status=500)

    errores = {k: v for k, v in form.errors.items()}
    print(" ERRORES DEL FORM:", errores)  # Debug
    return JsonResponse({'status': 'error', 'errors': errores}, status=400)


@csrf_exempt
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        usuario.estado = 'INACTIVO'
        usuario.save()
        return JsonResponse({'status': 'ok', 'message': 'Usuario desactivado correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ================================
# Clientes Autocomplete
# ================================
def ClienteAutocomplete(request):
    term = request.GET.get('q', '').strip()

    if not term:
        return JsonResponse({'results': []})

    # Roles que pueden reservar turnos (clientes + empleados)
    roles_permitidos = ['cliente', 'peluquero', 'recepcionista', 'admin']

    # Buscar usuarios activos cuyo nombre, apellido o dni coincida
    usuarios = Usuario.objects.filter(
        estado='ACTIVO'
    ).filter(
        Q(nombre__icontains=term) |
        Q(apellido__icontains=term) |
        Q(dni__icontains=term)
    ).filter(
        Q(rol__nombre__iexact='cliente') |
        Q(rol__nombre__iexact='peluquero') |
        Q(rol__nombre__iexact='recepcionista') |
        Q(rol__nombre__iexact='admin')
    )

    # Preparar datos para JSON
    data = [
        {
            'id': u.id,
            'nombre': f"{u.nombre} {u.apellido}",
            'dni': u.dni,
            'rol': u.rol.nombre if u.rol else 'Sin rol'
        }
        for u in usuarios
    ]

    return JsonResponse({'results': data})

# ================================
# Servicios
# ================================
@csrf_exempt
def listado_servicios(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    servicios = Servicio.objects.all().order_by('nombre')
    data = [
        {
            'id': s.id,
            'nombre': s.nombre,
            'precio': float(s.precio),
            'duracion': getattr(s, 'duracion', 0),
            'categoria': s.categoria.nombre if getattr(s, 'categoria', None) else None
        } for s in servicios
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def crear_servicio(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        precio = data.get('precio')
        duracion = data.get('duracion', 20)
        categoria_id = data.get('categoria')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Datos inválidos: {str(e)}'}, status=400)

    if not nombre or precio is None:
        return JsonResponse({'status': 'error', 'message': 'Faltan campos obligatorios'}, status=400)

    if Servicio.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'status': 'error', 'message': 'El servicio ya existe'}, status=400)

    categoria = CategoriaServicio.objects.filter(pk=categoria_id).first() if categoria_id else None

    servicio = Servicio.objects.create(
        nombre=nombre,
        precio=precio,
        duracion=duracion,
        categoria=categoria
    )

    return JsonResponse({'status': 'ok', 'id': servicio.id})


@csrf_exempt
def editar_servicio(request, pk):
    servicio = Servicio.objects.filter(pk=pk).first()
    if not servicio:
        return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        precio = data.get('precio')
        duracion = data.get('duracion', 20)
        categoria_id = data.get('categoria')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Datos inválidos: {str(e)}'}, status=400)

    if nombre:
        if Servicio.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': 'Otro servicio con ese nombre ya existe'}, status=400)
        servicio.nombre = nombre

    if precio is not None:
        servicio.precio = precio

    servicio.duracion = duracion
    servicio.categoria = CategoriaServicio.objects.filter(pk=categoria_id).first() if categoria_id else None
    servicio.save()

    return JsonResponse({'status': 'ok', 'id': servicio.id})


@csrf_exempt
def eliminar_servicio(request, pk):
    servicio = Servicio.objects.filter(pk=pk).first()
    if not servicio:
        return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        servicio.delete()
        return JsonResponse({'status': 'ok', 'message': 'Servicio eliminado correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ================================
# Productos
# ================================
@csrf_exempt
def listado_productos(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    productos = Producto.objects.select_related('categoria').all()
    data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'stock_actual': p.stock_actual,  # ✅ CORREGIR: usar stock_actual
            'categoria': p.categoria.nombre if p.categoria else None,
            'categoria_id': p.categoria.id if p.categoria else None  # ✅ AGREGAR
        } for p in productos
    ]
    return JsonResponse(data, safe=False)

class ProductoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Producto.objects.select_related('categoria', 'marca').prefetch_related('proveedores').all()
    serializer_class = ProductoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        nombre = self.request.query_params.get('nombre')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            try:
                categoria_id = int(categoria_id)
                queryset = queryset.filter(categoria_id=categoria_id)
            except ValueError:
                pass

        return queryset

class ProductoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Para ver, editar y eliminar productos individuales"""
    queryset = Producto.objects.select_related('categoria', 'marca').prefetch_related('proveedores').all()
    serializer_class = ProductoSerializer
    permission_classes = [AllowAny]  # Temporal para testing
    
# ================================
# Peluqueros
# ================================
@csrf_exempt
def listado_peluqueros(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        rol_peluquero = Rol.objects.get(nombre__iexact='Peluquero')
    except Rol.DoesNotExist:
        return JsonResponse([], safe=False)  # Si no hay peluquero definido

    peluqueros = Usuario.objects.filter(rol=rol_peluquero, estado='ACTIVO')
    data = [{'id': p.id, 'nombre': f'{p.nombre} {p.apellido}'} for p in peluqueros]
    return JsonResponse(data, safe=False)


# ================================
# Turnos
# ================================
@csrf_exempt
def listado_turnos(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        # ===== Parámetros GET =====
        peluquero_id = request.GET.get('peluquero')
        estado = request.GET.get('estado')
        canal = request.GET.get('canal')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        fecha_exacta = request.GET.get('fecha') # <--- NUEVO: Para filtrar por día exacto

        # ===== Query base =====
        turnos = Turno.objects.all().select_related('cliente', 'peluquero').prefetch_related('servicios').order_by('fecha', 'hora')

        # ===== Filtros =====
        if peluquero_id:
            turnos = turnos.filter(peluquero__id=peluquero_id)

        if estado:
            # Mapeo de estados
            estado_map = {
                'RESERVADO': 'RESERVADO', 'CONFIRMADO': 'CONFIRMADO', 
                'CANCELADO': 'CANCELADO', 'COMPLETADO': 'COMPLETADO',
                'PENDIENTE': 'RESERVADO'
            }
            # Soporte para filtrar múltiples estados (ej: RESERVADO,CONFIRMADO)
            if ',' in estado:
                estados_lista = [estado_map.get(e.strip().upper(), e.strip().upper()) for e in estado.split(',')]
                turnos = turnos.filter(estado__in=estados_lista)
            else:
                estado_bd = estado_map.get(estado.upper(), estado.upper())
                turnos = turnos.filter(estado=estado_bd)

        if canal:
            turnos = turnos.filter(canal=canal.upper())

        # Filtro de fecha exacta (Optimización)
        if fecha_exacta:
            try:
                fecha_e = datetime.strptime(fecha_exacta, "%Y-%m-%d").date()
                turnos = turnos.filter(fecha=fecha_e)
            except ValueError:
                pass

        if fecha_desde:
            try:
                fecha_d = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
                turnos = turnos.filter(fecha__gte=fecha_d)
            except ValueError:
                pass
        if fecha_hasta:
            try:
                fecha_h = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
                turnos = turnos.filter(fecha__lte=fecha_h)
            except ValueError:
                pass

        # ===== Lógica de Permisos =====
        es_admin_o_recep = False
        if request.user.is_authenticated:
            rol_nombre = request.user.rol.nombre.upper() if request.user.rol else ''
            if request.user.is_staff or rol_nombre in ['ADMINISTRADOR', 'ADMIN', 'RECEPCIONISTA', 'REC']:
                es_admin_o_recep = True

        # ===== Construcción del resultado =====
        data = []
        ahora = timezone.now()

        for t in turnos:
            servicios_list = []
            duracion_total = 0
            
            for servicio in t.servicios.all():
                servicios_list.append({
                    'id': servicio.id,
                    'nombre': servicio.nombre,
                    'precio': float(servicio.precio),
                    'duracion': servicio.duracion,
                    'categoria': servicio.categoria.id if servicio.categoria else None
                })
                duracion_total += servicio.duracion

            # Reglas de negocio
            try:
                fecha_turno_naive = datetime.combine(t.fecha, t.hora)
                fecha_turno = timezone.make_aware(fecha_turno_naive)
                tres_horas_antes = fecha_turno - timedelta(hours=3)
                
                cumple_tiempo = ahora < tres_horas_antes
                puede_modificar = (t.estado in ['RESERVADO', 'CONFIRMADO'] and (cumple_tiempo or es_admin_o_recep))
                puede_cancelar = puede_modificar
                puede_completar = (t.estado == 'CONFIRMADO' and es_admin_o_recep)

            except Exception as e:
                # Fallback seguro
                puede_modificar = es_admin_o_recep
                puede_cancelar = es_admin_o_recep
                puede_completar = False

            data.append({
                'id': t.id,
                'fecha': t.fecha.strftime("%Y-%m-%d"),
                'fecha_turno': t.fecha.strftime("%Y-%m-%d"),
                'hora': t.hora.strftime("%H:%M"),
                'hora_turno': t.hora.strftime("%H:%M"),
                'estado': t.estado,
                
                # ✅ AQUÍ ESTÁ EL ARREGLO: AGREGAMOS LOS IDs
                'peluquero_id': t.peluquero.id,       # <--- ¡FALTABA ESTO!
                'cliente_id': t.cliente.id,           # <--- Útil también
                
                'canal': getattr(t, 'canal', 'PRESENCIAL'),
                'tipo_pago': getattr(t, 'tipo_pago', 'PENDIENTE'),
                'monto_seña': float(getattr(t, 'monto_seña', 0)),
                'monto_total': float(getattr(t, 'monto_total', 0)),
                'cliente_nombre': t.cliente.nombre,
                'cliente_apellido': t.cliente.apellido,
                'peluquero_nombre': t.peluquero.nombre,
                'peluquero_apellido': t.peluquero.apellido,
                'servicios': servicios_list,
                'duracion_total': duracion_total,
                'puede_modificar': puede_modificar,
                'puede_cancelar': puede_cancelar,
                'puede_completar': puede_completar,
                'oferta_activa': getattr(t, 'oferta_activa', False),
                'fecha_expiracion_oferta': t.fecha_expiracion_oferta.isoformat() if getattr(t, 'fecha_expiracion_oferta', None) else None
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Error crítico en listado_turnos: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    

@api_view(['POST'])
@permission_classes([AllowAny]) 
def crear_turno(request):
    try:
        print(f"🚀 CREAR TURNO: Iniciando proceso...")
        data = request.data
        
        # 1. IDENTIFICAR USUARIO (LÓGICA CORREGIDA)
        cliente = None
        canal = data.get('canal', 'WEB')

        # 🟢 CAMBIO IMPORTANTE: Preguntamos PRIMERO por el canal
        if canal == 'PRESENCIAL':
            # Si es presencial, mandan el ID explícitamente (aunque yo sea Admin)
            cliente_id = data.get('cliente_id')
            if cliente_id:
                try:
                    cliente = Usuario.objects.get(pk=cliente_id)
                    print(f"✅ Cliente asignado manualmente (Presencial): {cliente.nombre}")
                except Usuario.DoesNotExist:
                    return Response({'status': 'error', 'message': "Cliente no encontrado"}, status=400)
            else:
                return Response({'status': 'error', 'message': "Falta seleccionar un cliente."}, status=400)

        elif request.user.is_authenticated:
            # Si es WEB y hay token, el cliente es el usuario logueado
            cliente = request.user
            print(f"✅ Usuario Token (Web): {cliente.nombre} (ID: {cliente.id})")
        
        # Si llegamos aquí sin cliente...
        if not cliente:
            return Response({'status': 'error', 'message': "Debes iniciar sesión."}, status=401)

        # 2. DATOS
        try:
            peluquero_id = int(data.get('peluquero_id'))
            servicios_ids = data.get('servicios_ids', [])
            fecha_str = data.get('fecha')
            hora_str = data.get('hora')
            
            if len(hora_str) > 5: 
                hora_str = hora_str[:5]
            
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
            
        except (ValueError, TypeError) as e:
            return Response({'status': 'error', 'message': "Datos inválidos"}, status=400)

        # 3. VALIDAR DISPONIBILIDAD
        ocupado = Turno.objects.filter(
            fecha=fecha_obj, 
            hora=hora_obj, 
            peluquero_id=peluquero_id, 
            estado__in=['RESERVADO', 'CONFIRMADO']
        ).exists()

        if ocupado:
            return Response({'status': 'error', 'message': 'Horario ya ocupado.'}, status=400)

        # 4. LIMPIEZA DE ZOMBIES
        zombies = Turno.objects.filter(
            fecha=fecha_obj,
            hora=hora_obj,
            peluquero_id=peluquero_id,
            oferta_activa=True
        )
        if zombies.exists():
            zombies.update(oferta_activa=False, estado='CANCELADO')
            from .models import InteresTurnoLiberado
            InteresTurnoLiberado.objects.filter(turno_liberado__in=zombies).update(estado_oferta='rechazada')

        # 5. CREAR TURNO
        peluquero = Usuario.objects.get(pk=peluquero_id)
        servicios = Servicio.objects.filter(pk__in=servicios_ids)
        monto_total = sum(float(s.precio) for s in servicios)
        
        tipo_pago = data.get('tipo_pago')
        monto_seña = monto_total * 0.5 if tipo_pago == 'SENA_50' else monto_total

        turno = Turno.objects.create(
            cliente=cliente,
            peluquero=peluquero,
            fecha=fecha_obj,
            hora=hora_obj,
            canal=canal, # <--- AHORA SÍ TOMA EL CORRECTO
            tipo_pago=tipo_pago,
            medio_pago=data.get('medio_pago', 'EFECTIVO'),
            monto_seña=monto_seña,
            monto_total=monto_total,
            estado='RESERVADO'
        )
        turno.servicios.set(servicios)
        
        # 6. MERCADO PAGO
        mp_data = None
        procesar_pago = False
        
        if data.get('medio_pago') == 'MERCADO_PAGO':
            try:
                from .mercadopago_service import MercadoPagoService
                mp_service = MercadoPagoService()
                preference_data = {
                    'turno_id': turno.id,
                    'monto_pago': float(monto_seña),
                    'cliente_nombre': f"{cliente.nombre} {cliente.apellido}",
                    'cliente_correo': cliente.correo or "cliente@test.com",
                    'peluquero_nombre': f"{peluquero.nombre} {peluquero.apellido}",
                    'es_pago_total': (tipo_pago == 'TOTAL')
                }
                
                resultado_mp = mp_service.crear_preferencia_seña(preference_data)
                if resultado_mp['success']:
                    procesar_pago = True
                    mp_data = {
                        'init_point': resultado_mp.get('init_point'), 
                        'preference_id': resultado_mp['preference_id']
                    }
            except Exception as e:
                print(f"❌ Error MP: {e}")

        return Response({
            'status': 'ok',
            'turno_id': turno.id,
            'message': 'Turno reservado correctamente',
            'procesar_pago': procesar_pago,
            'mp_data': mp_data
        })

    except Exception as e:
        print(f"💥 EXCEPCIÓN: {str(e)}")
        return Response({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt
def verificar_disponibilidad(request):
    """Verifica disponibilidad de un peluquero en fecha y hora específica"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        peluquero_id = request.GET.get('peluquero_id')
        fecha = request.GET.get('fecha')
        hora = request.GET.get('hora')

        if not all([peluquero_id, fecha, hora]):
            return JsonResponse({
                'status': 'error', 
                'message': "Faltan parámetros: peluquero_id, fecha, hora"
            }, status=400)

        # Convertir parámetros
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora, "%H:%M").time()

        # Verificar disponibilidad
        disponible = not Turno.objects.filter(
            fecha=fecha_obj, 
            hora=hora_obj, 
            peluquero_id=peluquero_id,
            estado__in=['RESERVADO', 'CONFIRMADO']
        ).exists()

        return JsonResponse({
            'status': 'ok',
            'disponible': disponible,
            'fecha': fecha,
            'hora': hora,
            'peluquero_id': peluquero_id
        })

    except Exception as e:
        print(f"Error en verificar_disponibilidad: {str(e)}")
        return JsonResponse({
            'status': 'error', 
            'message': f"Error interno: {str(e)}"
        }, status=500)

@csrf_exempt
def completar_turno(request, turno_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        turno = Turno.objects.get(pk=turno_id)
        
        # Solo se puede completar turnos confirmados
        if turno.estado != 'CONFIRMADO':
            return JsonResponse({
                'status': 'error',
                'message': 'Solo se pueden completar turnos en estado CONFIRMADO'
            }, status=400)

        turno.estado = 'COMPLETADO'
        turno.save()

        return JsonResponse({
            'status': 'ok',
            'message': 'Turno marcado como completado'
        })

    except Turno.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Turno no encontrado'
        }, status=404)
    except Exception as e:
        print("Error al completar turno:", e)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
def modificar_turno(request, turno_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        turno = Turno.objects.get(pk=turno_id)
        
        # 1. VERIFICACIÓN DE PERMISOS
        # Asumo que el método `puede_ser_modificado()` existe en tu modelo Turno.
        if not turno.puede_ser_modificado():
            return JsonResponse({
                'status': 'error',
                'message': 'No se puede modificar el turno. Debe modificarse con al menos 3 horas de anticipación.'
            }, status=400)

        # 2. PREPARACIÓN DE DATOS CANDIDATOS
        
        # Usamos los datos actuales como base y los actualizamos con los recibidos
        nueva_fecha = data.get('fecha', turno.fecha)
        nueva_hora = data.get('hora', turno.hora)
        nuevo_peluquero_id = data.get('peluquero_id', turno.peluquero_id)
        nuevos_servicios_ids = data.get('servicios_ids')
        nuevo_tipo_pago = data.get('tipo_pago', turno.tipo_pago)

        # Convertir fecha y hora si son strings (vienen del frontend)
        if isinstance(nueva_fecha, str):
            nueva_fecha = datetime.strptime(nueva_fecha, "%Y-%m-%d").date()
        if isinstance(nueva_hora, str):
            nueva_hora = datetime.strptime(nueva_hora, "%H:%M").time()
            
        # Obtener el objeto del nuevo peluquero
        nuevo_peluquero = Usuario.objects.get(pk=nuevo_peluquero_id)

        # 3. VALIDACIÓN DE DISPONIBILIDAD (EL PUNTO CRÍTICO CORREGIDO)
        
        # Validar que la nueva combinación de Fecha/Hora/Peluquero esté disponible
        # 🚨 CORRECCIÓN CLAVE: Excluir el turno actual (turno_id) del chequeo.
        if Turno.objects.filter(
            fecha=nueva_fecha, 
            hora=nueva_hora, 
            peluquero=nuevo_peluquero,
            estado__in=['RESERVADO', 'CONFIRMADO'] # Solo chequeamos contra turnos activos
        ).exclude(pk=turno_id).exists(): 
            return JsonResponse({
                'status': 'error',
                'message': 'El peluquero no está disponible en la nueva fecha y hora solicitada.'
            }, status=400)
            
        # 4. APLICAR MODIFICACIONES EN EL OBJETO TURNO

        # Actualizar campos básicos
        turno.fecha = nueva_fecha
        turno.hora = nueva_hora
        turno.tipo_pago = nuevo_tipo_pago
        turno.peluquero = nuevo_peluquero
        
        # Actualizar servicios y recalcular montos si se proporcionaron nuevos IDs
        if nuevos_servicios_ids is not None:
            servicios = Servicio.objects.filter(pk__in=nuevos_servicios_ids)
            if servicios.exists():
                turno.servicios.set(servicios)
                
                # Recalcular montos
                monto_total = sum(float(servicio.precio) for servicio in servicios)
                turno.monto_total = monto_total
                
                # Recalcular seña
                if turno.tipo_pago == 'SENA_50':
                    turno.monto_seña = monto_total * 0.5
                else:
                    # Si cambia el tipo de pago, la seña puede ajustarse a 0
                    turno.monto_seña = 0 
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No se encontraron los nuevos servicios especificados.'
                }, status=400)
        
        # Si se cambia el tipo_pago pero no los servicios, recalcula la seña
        elif 'tipo_pago' in data and data['tipo_pago'] == 'SENA_50':
             turno.monto_seña = turno.monto_total * 0.5


        # Guardar todos los cambios
        turno.save()

        # 5. RESPUESTA
        return JsonResponse({
            'status': 'ok',
            'message': 'Turno modificado exitosamente',
            'turno_id': turno.id,
            'nuevo_monto_total': float(turno.monto_total),
            'nuevo_monto_seña': float(turno.monto_seña)
        })

    except Turno.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Turno no encontrado'
        }, status=404)
    except Usuario.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Peluquero o Cliente no encontrado'
        }, status=400)
    except Exception as e:
        print("Error al modificar turno:", e)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny]) 
def registrar_interes_turno(request):
    print("-------------------------------------------------------")
    print("🔥 DEBUG: Intentando registrar interés (Ignorando Sesión)")
    print("Datos crudos recibidos:", request.data)
    print("-------------------------------------------------------")
    
    try:
        data = request.data
        
        # 1. PRUEBA DE IDENTIFICACIÓN CRÍTICA
        cliente_id_candidato = data.get('cliente_id')
        
        if not cliente_id_candidato:
            print("❌ DEBUG FALLO: El campo 'cliente_id' NO se encontró en el cuerpo del POST.")
            return Response({
                'error': '❌❌ Error: El campo "cliente_id" es OBLIGATORIO en el cuerpo del request. El frontend NO lo está enviando.'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        # 2. PRUEBA DE FORMATO NUMÉRICO
        try:
            cliente_id = int(cliente_id_candidato)
        except (TypeError, ValueError):
            print(f"❌ DEBUG FALLO: El valor '{cliente_id_candidato}' NO es un número válido.")
            return Response({
                'error': f'Error: El ID de cliente ({cliente_id_candidato}) no es un número válido.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. PRUEBA DE EXISTENCIA EN BD (LA MAYOR CAUSA DE FALLO)
        from .models import Usuario, Servicio, Turno, InteresTurnoLiberado
        from datetime import datetime
        
        try:
            # 💡 Verificamos si existe el usuario
            cliente = Usuario.objects.get(id=cliente_id) 
        except Usuario.DoesNotExist:
            print(f"❌ DEBUG FALLO: El cliente con ID {cliente_id} NO EXISTE en la tabla de usuarios.")
            return Response({'error': f'Error: El cliente con ID {cliente_id} NO EXISTE. Verifica tu base de datos.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 4. SI LLEGA HASTA AQUÍ, EL ID ES CORRECTO. Continuamos con la lógica.
        
        servicio_id = data.get('servicio_id')
        peluquero_id = data.get('peluquero_id')
        fecha_deseada_str = data.get('fecha_deseada') 
        hora_deseada_str = data.get('hora_deseada') 

        # Más chequeos de existencia de objetos
        try:
            servicio = Servicio.objects.get(id=servicio_id)
            peluquero = Usuario.objects.get(id=peluquero_id)
            fecha_deseada = datetime.strptime(fecha_deseada_str, "%Y-%m-%d").date()
            hora_deseada = datetime.strptime(hora_deseada_str, "%H:%M").time()
        except Exception as e:
            return Response({'error': f'Error en datos de turno (Servicio/Peluquero/Fecha Inválida): {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 5. CREAR INTERÉS
        interes_existente = InteresTurnoLiberado.objects.filter(
            cliente=cliente, peluquero=peluquero, fecha_deseada=fecha_deseada, hora_deseada=hora_deseada
        ).exists()
        
        if interes_existente:
            return Response({'error': 'Ya estás registrado como interesado en este horario'}, status=status.HTTP_400_BAD_REQUEST)
        
        interes = InteresTurnoLiberado.objects.create(
            cliente=cliente, servicio=servicio, peluquero=peluquero,
            fecha_deseada=fecha_deseada, hora_deseada=hora_deseada
        )
        
        return Response({
            'success': True,
            'message': '✅ ¡Interés registrado! Procede a la cancelación para que Celery envíe el WhatsApp.',
            'interes_id': interes.id
        })
        
    except Exception as e:
        import traceback
        return Response({'error': f'Error interno inesperado: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
def listar_intereses_cliente(request, cliente_id=None):
    """
    Listar intereses de un cliente (para ver en su perfil)
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        from .models import InteresTurnoLiberado
        
        # Si no se especifica cliente_id, usar el usuario autenticado
        if not cliente_id and request.user.is_authenticated:
            cliente_id = request.user.id
        
        if not cliente_id:
            return JsonResponse({'error': 'Se requiere cliente_id'}, status=400)

        intereses = InteresTurnoLiberado.objects.filter(
            cliente_id=cliente_id
        ).select_related('servicio', 'peluquero').order_by('-fecha_registro')

        data = []
        for interes in intereses:
            data.append({
                'id': interes.id,
                'servicio_nombre': interes.servicio.nombre,
                'peluquero_nombre': f"{interes.peluquero.nombre} {interes.peluquero.apellido}",
                'fecha_deseada': interes.fecha_deseada.isoformat(),
                'hora_deseada': interes.hora_deseada.strftime("%H:%M"),
                'fecha_registro': interes.fecha_registro.isoformat(),
                'notificado': (interes.estado_oferta == 'enviada'),
                'fecha_notificacion': interes.fecha_notificacion.isoformat() if interes.fecha_notificacion else None
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en listar_intereses_cliente: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def procesar_sena_turno(request, turno_id):
    """Procesar seña de un turno"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        turno = Turno.objects.get(id=turno_id)
        
        if turno.estado != 'RESERVADO':
            return JsonResponse({
                'status': 'error',
                'message': 'Solo se puede señar turnos en estado RESERVADO'
            }, status=400)

        # Calcular monto de seña
        monto_sena = turno.monto_total * 0.5

        # Actualizar turno
        turno.tipo_pago = 'SENA_50'
        turno.monto_seña = monto_sena
        turno.estado = 'CONFIRMADO'
        turno.save()

        return JsonResponse({
            'status': 'ok',
            'message': f'Seña procesada exitosamente. Monto: ${monto_sena}',
            'monto_sena': float(monto_sena)
        })

    except Turno.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Turno no encontrado'
        }, status=404)
    except Exception as e:
        print(f"Error procesando seña: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }, status=500)

@csrf_exempt
def completar_pago_turno(request, turno_id):
    """Completar pago de un turno (pagar resto de seña)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        turno = Turno.objects.get(id=turno_id)
        
        if turno.estado != 'CONFIRMADO' or turno.tipo_pago != 'SENA_50':
            return JsonResponse({
                'status': 'error',
                'message': 'Solo se puede completar pago de turnos confirmados con seña'
            }, status=400)

        # Cambiar a pago total
        turno.tipo_pago = 'TOTAL'
        turno.monto_seña = turno.monto_total
        turno.save()

        return JsonResponse({
            'status': 'ok',
            'message': f'Pago completado exitosamente. Monto total: ${turno.monto_total}',
            'monto_total': float(turno.monto_total)
        })

    except Turno.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Turno no encontrado'
        }, status=404)
    except Exception as e:
        print(f"Error completando pago: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }, status=500)

def turnos_ocupados(request):
    fecha = request.GET.get("fecha")
    peluquero_id = request.GET.get("peluquero")

    if not fecha or not peluquero_id:
        return JsonResponse({"error": "Faltan parámetros"}, status=400)

    ocupados = Turno.objects.filter(
        fecha=fecha,
        peluquero_id=peluquero_id,
    ).values_list("hora", flat=True)

    return JsonResponse({
        "fecha": fecha,
        "peluquero": peluquero_id,
        "ocupados": list(ocupados)
    })
# ================================
# Listado  de  Categorías
# ================================
@csrf_exempt
def listado_categorias_servicios(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    categorias = CategoriaServicio.objects.all().order_by('nombre')
    data = [{'id': c.id, 'nombre': c.nombre, 'descripcion': c.descripcion} for c in categorias]
    return JsonResponse(data, safe=False)


class CategoriaProductoListAPIView(generics.ListAPIView):
    # 1. Fuente de datos: Todas las categorías de productos
    queryset = CategoriaProducto.objects.all().order_by('nombre')
    
    # 2. Traductor: Usa el Serializer (que ya revisamos)
    # Asegúrate de que CategoriaProductoSerializer esté importado en views.py
    # from .serializers import ..., CategoriaProductoSerializer
    serializer_class = CategoriaProductoSerializer



# ================================
# Categorías CRUD
# ================================
@csrf_exempt
def crear_categoria_servicio(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        if not nombre:
            return JsonResponse({'status': 'error', 'message': 'Nombre obligatorio'}, status=400)
        if CategoriaServicio.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({'status': 'error', 'message': 'La categoría ya existe'}, status=400)
        cat = CategoriaServicio.objects.create(nombre=nombre, descripcion=descripcion)
        return JsonResponse({'status': 'ok', 'id': cat.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def editar_categoria_servicio(request, pk):
    cat = get_object_or_404(CategoriaServicio, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        if nombre:
            if CategoriaServicio.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                return JsonResponse({'status': 'error', 'message': 'Otra categoría con ese nombre ya existe'}, status=400)
            cat.nombre = nombre
        if descripcion:
            cat.descripcion = descripcion
        cat.save()
        return JsonResponse({'status': 'ok', 'id': cat.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def eliminar_categoria_servicio(request, pk):
    cat = get_object_or_404(CategoriaServicio, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    try:
        cat.delete()
        return JsonResponse({'status': 'ok', 'message': 'Categoría eliminada'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def crear_categoria_producto(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        if not nombre:
            return JsonResponse({'status': 'error', 'message': 'Nombre obligatorio'}, status=400)
        if CategoriaProducto.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({'status': 'error', 'message': 'La categoría ya existe'}, status=400)
        cat = CategoriaProducto.objects.create(nombre=nombre, descripcion=descripcion)
        return JsonResponse({'status': 'ok', 'id': cat.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def editar_categoria_producto(request, pk):
    cat = get_object_or_404(CategoriaProducto, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        if nombre:
            if CategoriaProducto.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                return JsonResponse({'status': 'error', 'message': 'Otra categoría con ese nombre ya existe'}, status=400)
            cat.nombre = nombre
        if descripcion:
            cat.descripcion = descripcion
        cat.save()
        return JsonResponse({'status': 'ok', 'id': cat.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def eliminar_categoria_producto(request, pk):
    cat = get_object_or_404(CategoriaProducto, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    try:
        cat.delete()
        return JsonResponse({'status': 'ok', 'message': 'Categoría eliminada'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ================================
# Roles
# ================================
@csrf_exempt
def listado_roles(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    roles = Rol.objects.prefetch_related('permisos').all().order_by('nombre')
    data = [
        {
            'id': r.id,
            'nombre': r.nombre,
            'descripcion': r.descripcion or '',
            'activo': r.activo,
            'permisos': [{'id': p.id, 'nombre': p.nombre} for p in r.permisos.all()]
        } for r in roles
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def crear_rol(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()

        if not nombre:
            return JsonResponse({'status': 'error', 'message': 'El nombre del rol es obligatorio'}, status=400)

        if Rol.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({'status': 'error', 'message': 'Ya existe un rol con ese nombre'}, status=400)

        rol = Rol.objects.create(nombre=nombre, descripcion=descripcion)
        return JsonResponse({'status': 'ok', 'id': rol.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def editar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        activo = data.get('activo', True)

        if nombre:
            if Rol.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                return JsonResponse({'status': 'error', 'message': 'Otro rol con ese nombre ya existe'}, status=400)
            rol.nombre = nombre

        rol.descripcion = descripcion
        rol.activo = activo
        rol.save()

        return JsonResponse({'status': 'ok', 'id': rol.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
def eliminar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        rol.delete()
        return JsonResponse({'status': 'ok', 'message': 'Rol eliminado correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# ✅ Crear rol con permisos
@csrf_exempt
def crear_rol(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        permisos_ids = data.get('permisos', [])

        if not nombre:
            return JsonResponse({'status': 'error', 'message': 'El nombre del rol es obligatorio'}, status=400)

        if Rol.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({'status': 'error', 'message': 'Ya existe un rol con ese nombre'}, status=400)

        rol = Rol.objects.create(nombre=nombre, descripcion=descripcion)
        if permisos_ids:
            rol.permisos.set(permisos_ids)  # <-- Asignar permisos seleccionados
        rol.save()

        return JsonResponse({'status': 'ok', 'id': rol.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ✅ Editar rol con permisos
@csrf_exempt
def editar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)

        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        permisos_ids = data.get('permisos', [])  # 🟢 lista de IDs
        activo = data.get('activo', True)

        if not nombre:
            return JsonResponse({'status': 'error', 'message': 'El nombre del rol es obligatorio'}, status=400)

        if Rol.objects.exclude(pk=pk).filter(nombre__iexact=nombre).exists():
            return JsonResponse({'status': 'error', 'message': 'Ya existe otro rol con ese nombre'}, status=400)

        rol.nombre = nombre
        rol.descripcion = descripcion
        rol.activo = activo
        rol.save()

        # 🔗 Actualizar los permisos del rol
        if permisos_ids is not None:
            permisos = Permiso.objects.filter(id__in=permisos_ids)
            rol.permisos.set(permisos)

        return JsonResponse({'status': 'ok', 'id': rol.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# ================================
# Permisos
# ================================
@csrf_exempt
def listado_permisos(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    permisos = Permiso.objects.filter(activo=True).order_by('nombre')
    data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'codigo': p.codigo,
            'descripcion': p.descripcion or '',
        } for p in permisos
    ]
    return JsonResponse(data, safe=False)

# ================================
# API Mercado Pago
# ================================

@csrf_exempt
def crear_preferencia_pago_seña(request):
    """Crea una preferencia de pago para la seña de un turno"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        turno_id = data.get('turno_id')
        monto_sena = data.get('monto_sena')
        cliente_nombre = data.get('cliente_nombre')
        peluquero_nombre = data.get('peluquero_nombre')
        es_pago_total = data.get('es_pago_total', False)
        
        print(f"🔄 Creando preferencia MP - Turno: {turno_id}, Monto: {monto_sena}")
        
        if not all([turno_id, monto_sena]):
            return JsonResponse({
                'success': False, 
                'error': 'Faltan datos requeridos: turno_id y monto_sena'
            })

        # Crear servicio MP
        mp_service = MercadoPagoService()
        
        # Datos para la preferencia
        turno_data = {
            'turno_id': turno_id,
            'monto_seña': monto_sena,
            'cliente_nombre': cliente_nombre,
            'peluquero_nombre': peluquero_nombre,
            'es_pago_total': es_pago_total
        }
        
        # Crear preferencia
        resultado = mp_service.crear_preferencia_seña(turno_data)
        
        if resultado['success']:
            # ✅ Usar sandbox_init_point si está disponible (para testing)
            init_point = resultado.get('sandbox_init_point') or resultado['init_point']
            
            return JsonResponse({
                'success': True,
                'init_point': init_point,
                'preference_id': resultado['preference_id'],
                'modo_test': True
            })
        else:
            return JsonResponse({
                'success': False,
                'error': resultado['error']
            })
            
    except Exception as e:
        print(f"Error en crear_preferencia_pago_seña: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        })

@csrf_exempt
def pago_exitoso(request):
    """Maneja la redirección y GUARDA EL ID DE PAGO"""
    try:
        payment_id = request.GET.get('payment_id') # <--- ESTE ES EL DATO DE ORO
        status = request.GET.get('status')
        external_reference = request.GET.get('external_reference')  # turno_id
        
        print(f"✅ Pago exitoso - Turno: {external_reference}, Payment ID: {payment_id}")
        
        if external_reference:
            try:
                turno = Turno.objects.get(id=external_reference)
                turno.estado = 'CONFIRMADO'
                
                # ✅ GUARDAMOS LA LLAVE DEL REEMBOLSO
                if payment_id and payment_id != 'null':
                    turno.mp_payment_id = payment_id
                
                turno.save()
            except Turno.DoesNotExist:
                print(f"⚠️ Turno {external_reference} no encontrado")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Pago procesado. Turno confirmado.',
            'turno_id': external_reference
        })
        
    except Exception as e:
        print(f"❌ Error en pago_exitoso: {e}")
        return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def pago_error(request):
    """Maneja la redirección cuando el pago falla"""
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    external_reference = request.GET.get('external_reference')
    
    print(f"❌ Pago fallido - Turno: {external_reference}, Payment: {payment_id}, Status: {status}")
    
    return JsonResponse({
        'status': 'error',
        'message': 'El pago no pudo ser procesado. Por favor, intenta nuevamente.',
        'turno_id': external_reference
    })

@csrf_exempt
def pago_pendiente(request):
    """Maneja la redirección cuando el pago está pendiente"""
    payment_id = request.GET.get('payment_id')
    status = request.GET.get('status')
    external_reference = request.GET.get('external_reference')
    
    print(f"⏳ Pago pendiente - Turno: {external_reference}, Payment: {payment_id}, Status: {status}")
    
    return JsonResponse({
        'status': 'pending', 
        'message': 'El pago está pendiente de confirmación. Te notificaremos cuando sea procesado.',
        'turno_id': external_reference
    })

# EN: usuarios/views.py

# 1. FUNCIÓN AUXILIAR ACTUALIZADA (Lógica Universal)
def procesar_reembolso_si_corresponde(turno):
    """
    Intenta reembolso automático SIEMPRE que haya un ID de pago (Web o Presencial).
    """
    # A. Verificar regla de 3 horas
    ahora = timezone.now()
    fecha_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
    tiempo_restante = fecha_turno - ahora
    
    if tiempo_restante < timedelta(hours=3):
        return False, f"Faltan {str(tiempo_restante).split('.')[0]}. Menos de 3 horas: No corresponde reembolso."

    # B. SI TIENE ID DE PAGO (Sea Web o cargado Manualmente en Presencial)
    if turno.mp_payment_id:
        try:
            print(f"💳 Intentando reembolso automático para ID: {turno.mp_payment_id}")
            mp = MercadoPagoService()
            resultado = mp.devolver_pago(turno.mp_payment_id)
            
            if resultado['success']:
                turno.reembolsado = True
                turno.save()
                return True, f"✅ Reembolso de ${turno.monto_seña} procesado exitosamente en Mercado Pago."
            else:
                return False, f"❌ Falló Mercado Pago: {resultado.get('error')}. Devolver manualmente."
        except Exception as e:
            return False, f"❌ Error técnico MP: {str(e)}"

    # C. SI NO TIENE ID (Efectivo puro o sin comprobante)
    else:
        return True, f"⚠️ ATENCIÓN: Devolución MANUAL requerida (${turno.monto_seña}). No hay ID de transacción digital."

# 2. CREAR TURNO ACTUALIZADO (Para guardar el ID manual)
@api_view(['POST'])
@permission_classes([AllowAny]) 
def crear_turno(request):
    try:
        print(f"🚀 CREAR TURNO: Iniciando proceso...")
        data = request.data
        
        # ... (LÓGICA DE CLIENTE/USUARIO IGUAL QUE ANTES) ...
        # 1. IDENTIFICAR USUARIO
        cliente = None
        canal = data.get('canal', 'WEB')

        if canal == 'PRESENCIAL':
            cliente_id = data.get('cliente_id')
            if cliente_id:
                try:
                    cliente = Usuario.objects.get(pk=cliente_id)
                except Usuario.DoesNotExist:
                    return Response({'status': 'error', 'message': "Cliente no encontrado"}, status=400)
            else:
                return Response({'status': 'error', 'message': "Falta seleccionar un cliente."}, status=400)
        elif request.user.is_authenticated:
            cliente = request.user
        
        if not cliente:
            return Response({'status': 'error', 'message': "Debes iniciar sesión."}, status=401)

        # ... (LÓGICA DE DATOS Y VALIDACIÓN IGUAL QUE ANTES) ...
        # 2. DATOS
        try:
            peluquero_id = int(data.get('peluquero_id'))
            servicios_ids = data.get('servicios_ids', [])
            fecha_str = data.get('fecha')
            hora_str = data.get('hora')
            if len(hora_str) > 5: hora_str = hora_str[:5]
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
        except (ValueError, TypeError):
            return Response({'status': 'error', 'message': "Datos inválidos"}, status=400)

        # 3. VALIDAR DISPONIBILIDAD
        if Turno.objects.filter(fecha=fecha_obj, hora=hora_obj, peluquero_id=peluquero_id, estado__in=['RESERVADO', 'CONFIRMADO']).exists():
            return Response({'status': 'error', 'message': 'Horario ya ocupado.'}, status=400)

        # 4. LIMPIEZA DE ZOMBIES
        zombies = Turno.objects.filter(fecha=fecha_obj, hora=hora_obj, peluquero_id=peluquero_id, oferta_activa=True)
        if zombies.exists():
            zombies.update(oferta_activa=False, estado='CANCELADO')
            from .models import InteresTurnoLiberado
            InteresTurnoLiberado.objects.filter(turno_liberado__in=zombies).update(estado_oferta='rechazada')

        # 5. CREAR TURNO (AQUÍ ESTÁ EL CAMBIO)
        peluquero = Usuario.objects.get(pk=peluquero_id)
        servicios = Servicio.objects.filter(pk__in=servicios_ids)
        monto_total = sum(float(s.precio) for s in servicios)
        
        tipo_pago = data.get('tipo_pago')
        monto_seña = monto_total * 0.5 if tipo_pago == 'SENA_50' else monto_total

        # ✅ CAPTURAMOS EL ID MANUAL SI VIENE DEL FRONTEND
        mp_payment_id_manual = data.get('mp_payment_id', None)

        turno = Turno.objects.create(
            cliente=cliente,
            peluquero=peluquero,
            fecha=fecha_obj,
            hora=hora_obj,
            canal=canal,
            tipo_pago=tipo_pago,
            medio_pago=data.get('medio_pago', 'EFECTIVO'),
            monto_seña=monto_seña,
            monto_total=monto_total,
            estado='RESERVADO',
            mp_payment_id=mp_payment_id_manual # <--- GUARDAMOS EL ID MANUAL
        )
        turno.servicios.set(servicios)
        
        # 6. MERCADO PAGO (WEB)
        mp_data = None
        procesar_pago = False
        
        if data.get('medio_pago') == 'MERCADO_PAGO' and canal == 'WEB':
            # ... (Tu lógica de generación de link existente) ...
            try:
                from .mercadopago_service import MercadoPagoService
                mp_service = MercadoPagoService()
                preference_data = {
                    'turno_id': turno.id,
                    'monto_pago': float(monto_seña),
                    'cliente_nombre': f"{cliente.nombre} {cliente.apellido}",
                    'cliente_correo': cliente.correo or "cliente@test.com",
                    'peluquero_nombre': f"{peluquero.nombre}",
                    'es_pago_total': (tipo_pago == 'TOTAL')
                }
                res_mp = mp_service.crear_preferencia_seña(preference_data)
                if res_mp['success']:
                    procesar_pago = True
                    mp_data = {'init_point': res_mp.get('init_point'), 'preference_id': res_mp['preference_id']}
            except Exception:
                pass

        return Response({
            'status': 'ok',
            'turno_id': turno.id,
            'message': 'Turno registrado.',
            'procesar_pago': procesar_pago,
            'mp_data': mp_data
        })

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
@api_view(['GET'])
@permission_classes([AllowAny])
def me_api_view(request):
    from .models import Usuario
    
    # 🆕 OBTENER USUARIO DEL localStorage VIA HEADERS
    user_id = request.headers.get('User-Id')
    user_rol = request.headers.get('User-Rol')
    
    print(f"🔍 Headers recibidos - User-ID: {user_id}, User-Rol: {user_rol}")
    
    if user_id:
        try:
            user = Usuario.objects.get(id=int(user_id))
            print(f"✅ Usuario encontrado: {user.nombre} {user.apellido}")
            
            return Response({
                'nombre': user.nombre,
                'apellido': user.apellido,
                'rol': user_rol or (user.rol.nombre if user.rol else 'Usuario')
            })
        except Usuario.DoesNotExist:
            print("❌ Usuario no encontrado en BD")
    
    print("❌ No hay usuario autenticado")
    return Response({
        'nombre': 'Invitado',
        'apellido': '',
        'rol': 'Invitado'
    })

# D:\Facultad\Trabajo final\HairSoft\usuarios\views.py

class ProveedorListCreateView(generics.ListCreateAPIView):
    # Esto mantiene tu regla de listar TODOS (activos e inactivos) para la trazabilidad
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

    # ✅ CORRECCIÓN: Sobreescribimos perform_create para forzar el estado ACTIVO
    def perform_create(self, serializer):
        """
        Asegura que el proveedor se cree siempre con el estado 'ACTIVO',
        ya que no tiene lógica que nazca inactivo.
        """
        # Guardamos el objeto, estableciendo explícitamente el campo 'estado'
        serializer.save(estado='ACTIVO')


class ProveedorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    
    # Esta lógica para el "borrado suave" (trazabilidad) está PERFECTA
    def perform_destroy(self, instance):
        """
        Cambia el estado a 'INACTIVO' en lugar de eliminar el registro 
        físicamente de la base de datos.
        """
        instance.estado = 'INACTIVO'
        instance.save()


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_usuario_por_id(request, user_id):
    """Obtiene un usuario específico por ID"""
    try:
        user = Usuario.objects.get(id=user_id)
        return Response({
            'id': user.id,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'correo': user.correo,
            'rol': user.rol.nombre if user.rol else 'Sin rol'
        })
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
    
# =================================
# VENTAS
# =================================

# En usuarios/views.py (Pégalo al final del archivo o cerca de VentaViewSet)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_venta(request):
    """
    Registra una venta, descuenta stock y valida datos.
    Reemplaza la lógica del Serializer para mayor control.
    """
    print("💰 Iniciando registro de venta (Función Personalizada)...")
    data = request.data
    
    try:
        with transaction.atomic(): # 🔐 Bloque atómico
            
            # 1. Validar datos básicos
            usuario_vendedor = request.user
            # En Vue mandas 'usuario', pero lo tomamos del request.user por seguridad
            
            cliente_id = data.get('cliente') or data.get('cliente_id')
            # Vue manda 'medio_pago' (que es el ID)
            medio_pago_id = data.get('medio_pago') 
            items = data.get('detalles', [])

            if not items:
                return Response({"error": "La venta debe tener al menos un detalle."}, status=400)

            if not medio_pago_id:
                return Response({"error": "El medio de pago es obligatorio."}, status=400)

            # 2. Obtener Método de Pago
            try:
                medio_pago = MetodoPago.objects.get(id=medio_pago_id, activo=True)
            except MetodoPago.DoesNotExist:
                return Response({"error": "Método de pago inválido o inactivo."}, status=400)

            # 3. Crear Cabecera de Venta
            venta = Venta.objects.create(
                cliente_id=cliente_id if cliente_id else None,
                usuario=usuario_vendedor,
                tipo='PRODUCTO',
                medio_pago=medio_pago,
                total=0 
            )

            total_acumulado = 0

            # 4. Procesar items
            for item in items:
                # Vue manda 'producto' (ID) dentro de cada detalle
                producto_id = item.get('producto')
                cantidad = int(item.get('cantidad', 1))
                precio_enviado = float(item.get('precio_unitario', 0))

                if cantidad <= 0:
                    raise Exception(f"La cantidad debe ser mayor a 0.")

                # Bloqueamos el producto para evitar condición de carrera
                try:
                    producto = Producto.objects.select_for_update().get(id=producto_id)
                except Producto.DoesNotExist:
                    raise Exception(f"El producto con ID {producto_id} no existe.")

                # 📦 Validación de Stock
                if producto.stock_actual < cantidad:
                    raise Exception(f"Stock insuficiente para '{producto.nombre}'. Disponibles: {producto.stock_actual}, Solicitados: {cantidad}")
                
                # 📉 Descontar Stock
                producto.stock_actual -= cantidad
                producto.save()

                # Usamos el precio del producto en BD por seguridad, o el enviado si hay descuento manual
                precio_unitario = producto.precio 
                subtotal = precio_unitario * cantidad

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )

                total_acumulado += subtotal

            # 5. Guardar Total Final
            venta.total = total_acumulado
            venta.save()

            print(f"✅ Venta #{venta.id} registrada con éxito. Total: ${venta.total}")
            
            return Response({
                "success": True,
                "message": "Venta registrada correctamente",
                "id": venta.id, # Vue espera 'id'
                "total": float(venta.total)
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"❌ Error al registrar venta: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VentaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    queryset = Venta.objects.all()\
        .select_related('cliente', 'usuario', 'medio_pago')\
        .prefetch_related('detalles__producto', 'detalles__servicio')\
        .order_by('-fecha')
        
    serializer_class = VentaSerializer

    def list(self, request, *args, **kwargs):
        print("🔍 VentaViewSet.list - INICIO")
        
        # Debug: ver qué hay en la base de datos
        ventas_db = Venta.objects.all()
        print(f"📊 Ventas en BD: {ventas_db.count()}")
        for v in ventas_db:
            print(f"  - Venta {v.id}: {v.fecha} - ${v.total} - {v.tipo}")
        
        queryset = self.filter_queryset(self.get_queryset())
        print(f"🔍 QuerySet después de filtros: {queryset.count()}")
        
        try:
            serializer = self.get_serializer(queryset, many=True)
            print(f"✅ Serialización exitosa - {len(serializer.data)} ventas")
            print(f"📦 Datos serializados: {serializer.data}")
            return Response(serializer.data)
        except Exception as e:
            print(f"❌ ERROR en serialización: {str(e)}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()}")
            return Response({"error": f"Error en serialización: {str(e)}"}, status=500)


# En usuarios/views.py - Agregar después del VentaViewSet existente
@csrf_exempt
def obtener_venta_para_edicion(request, venta_id):
    """Obtiene una venta específica con todos los datos para edición"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        venta = Venta.objects\
            .select_related('cliente', 'usuario', 'medio_pago')\
            .prefetch_related('detalles__producto', 'detalles__servicio')\
            .get(id=venta_id)
        
        # Serializar la venta
        serializer = VentaSerializer(venta)
        venta_data = serializer.data
        
        # ✅ CORRECCIÓN: Cargar TODOS los productos (no solo disponibles)
        productos_todos = Producto.objects.all()
        venta_data['productos_disponibles'] = ProductoSerializer(
            productos_todos, 
            many=True
        ).data
        
        # ✅ CORRECCIÓN: Cargar métodos de pago
        metodos_pago = MetodoPago.objects.filter(activo=True)
        venta_data['metodos_pago'] = MetodoPagoSerializer(
            metodos_pago, 
            many=True
        ).data
        
        # ✅ CORRECCIÓN: Cargar categorías
        categorias = CategoriaProducto.objects.all()
        venta_data['categorias'] = CategoriaProductoSerializer(
            categorias,
            many=True
        ).data
        
        print(f"✅ Datos cargados - Productos: {len(productos_todos)}, Métodos pago: {len(metodos_pago)}, Categorías: {len(categorias)}")
        
        return JsonResponse(venta_data)
        
    except Venta.DoesNotExist:
        return JsonResponse({'error': 'Venta no encontrada'}, status=404)
    except Exception as e:
        print(f"Error al obtener venta: {str(e)}")
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
    
@csrf_exempt
def actualizar_venta(request, venta_id):
    """Actualiza una venta existente con manejo correcto de stock"""
    if request.method not in ['PUT', 'PATCH']:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        venta = Venta.objects.get(id=venta_id)
        data = json.loads(request.body)
        
        print(f"🔄 Actualizando venta {venta_id} con datos:", data)
        
        with transaction.atomic():
            # 1. RESTAURAR STOCK de todos los productos de la venta anterior
            detalles_anteriores = venta.detalles.all()
            for detalle in detalles_anteriores:
                if detalle.producto:
                    detalle.producto.stock_actual += detalle.cantidad
                    detalle.producto.save()
                    print(f"✅ Stock restaurado: {detalle.producto.nombre} +{detalle.cantidad} (Stock actual: {detalle.producto.stock_actual})")
            
            # 2. ELIMINAR detalles antiguos
            detalles_anteriores.delete()
            print("🗑️ Detalles antiguos eliminados")
            
            # 3. VALIDAR STOCK para los nuevos productos
            detalles_data = data.get('detalles', [])
            for detalle_data in detalles_data:
                producto_id = detalle_data.get('producto')
                cantidad = detalle_data.get('cantidad', 0)
                
                if producto_id and cantidad > 0:
                    producto = Producto.objects.get(id=producto_id)
                    if producto.stock_actual < cantidad:
                        return JsonResponse({
                            'error': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}, Solicitado: {cantidad}'
                        }, status=400)
            
            # 4. CREAR NUEVOS DETALLES y actualizar stock
            total_venta = 0
            nuevos_detalles = []
            
            for detalle_data in detalles_data:
                producto_id = detalle_data.get('producto')
                cantidad = detalle_data.get('cantidad', 0)
                precio_unitario = detalle_data.get('precio_unitario', 0)
                subtotal = cantidad * precio_unitario
                total_venta += subtotal
                
                if producto_id and cantidad > 0:
                    producto = Producto.objects.get(id=producto_id)
                    # ACTUALIZAR STOCK - RESTAR la cantidad
                    producto.stock_actual -= cantidad
                    producto.save()
                    print(f"📦 Stock actualizado: {producto.nombre} -{cantidad} (Nuevo stock: {producto.stock_actual})")
                
                # Crear detalle
                detalle = DetalleVenta(
                    venta=venta,
                    producto_id=producto_id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
                nuevos_detalles.append(detalle)
            
            # Guardar todos los detalles nuevos
            DetalleVenta.objects.bulk_create(nuevos_detalles)
            
            # 5. ACTUALIZAR VENTA
            venta.total = total_venta
            venta.medio_pago_id = data.get('medio_pago')
            venta.save()
            
            print(f"✅ Venta {venta_id} actualizada exitosamente. Total: ${total_venta}")
            print(f"💰 Medio de pago: {venta.medio_pago}")
        
        return JsonResponse({
            'status': 'ok',
            'message': '✅ Venta actualizada correctamente',
            'venta_id': venta.id,
            'total': float(venta.total)
        })
            
    except Venta.DoesNotExist:
        return JsonResponse({'error': 'Venta no encontrada'}, status=404)
    except Producto.DoesNotExist as e:
        return JsonResponse({'error': f'Producto no encontrado: {str(e)}'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"❌ Error al actualizar venta: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

@csrf_exempt
def anular_venta(request, venta_id):
    """Anula una venta (borrado lógico)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        venta = Venta.objects.get(id=venta_id)
        
        # Restaurar stock de productos
        for detalle in venta.detalles.all():
            if detalle.producto:
                detalle.producto.stock_actual += detalle.cantidad
                detalle.producto.save()
        
        # Marcar como anulada
        venta.anulada = True
        venta.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': 'Venta anulada correctamente'
        })
        
    except Venta.DoesNotExist:
        return JsonResponse({'error': 'Venta no encontrada'}, status=404)
    except Exception as e:
        print(f"Error al anular venta: {str(e)}")
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)
# ================================
# MÉTODOS DE PAGO (NUEVA VISTA)
# ================================
class MetodoPagoListAPIView(generics.ListAPIView):
    queryset = MetodoPago.objects.filter(activo=True).order_by('nombre')
    serializer_class = MetodoPagoSerializer



#--------------
@api_view(['GET'])
@permission_classes([AllowAny])
def debug_ventas(request):
    """Endpoint para debug de ventas"""
    print("🔍 DEBUG VENTAS - Verificando base de datos")
    
    # 1. Contar ventas en la base de datos
    total_ventas = Venta.objects.count()
    print(f"📊 Total de ventas en BD: {total_ventas}")
    
    # 2. Obtener todas las ventas simples
    ventas_simple = Venta.objects.all().order_by('-id')
    print(f"📋 Ventas encontradas: {ventas_simple.count()}")
    
    ventas_data = []
    for v in ventas_simple:
        print(f"  - Venta {v.id}: {v.fecha} - ${v.total} - {v.tipo} - Anulada: {v.anulada}")
        ventas_data.append({
            'id': v.id,
            'fecha': v.fecha.isoformat() if v.fecha else None,
            'total': float(v.total) if v.total else 0,
            'tipo': v.tipo,
            'anulada': v.anulada,
            'cliente_id': v.cliente_id,
            'usuario_id': v.usuario_id,
            'medio_pago_id': v.medio_pago_id
        })
    
    # 3. Probar el serializer del ViewSet
    from .serializers import VentaSerializer
    try:
        ventas_complejas = Venta.objects.all()\
            .select_related('cliente', 'usuario', 'medio_pago')\
            .prefetch_related('detalles__producto', 'detalles__servicio')\
            .order_by('-fecha')
        
        serializer = VentaSerializer(ventas_complejas, many=True)
        print(f"✅ Serializer funciona - {len(serializer.data)} ventas serializadas")
    except Exception as e:
        print(f"❌ Error en serializer: {e}")
    
    return Response({
        'total_ventas': total_ventas,
        'ventas_simple': ventas_data,
        'mensaje': f'Hay {total_ventas} ventas en la base de datos'
    })

# En usuarios/views.py

@api_view(['GET'])
@permission_classes([AllowAny])
def generar_comprobante_pdf(request, venta_id):
    """
    Vista para generar y descargar el comprobante PDF de una venta
    """
    try:
        print(f"🔍 VISTA: Iniciando generación PDF para venta {venta_id}")
        
        # 1. Obtener el objeto Venta y sus detalles
        venta = get_object_or_404(Venta, id=venta_id)
        detalles = DetalleVenta.objects.filter(venta=venta)
        
        print(f"✅ VISTA: Venta {venta.id} encontrada, {detalles.count()} detalles")
        
        # 2. 🚨 SERIALIZAR LA VENTA (Convertir Objeto -> Diccionario)
        # Esto es necesario porque pdf_utils espera un diccionario con .get()
        # y además el serializer ya nos trae los nombres (cliente_nombre, medio_pago_nombre)
        from .serializers import VentaSerializer
        venta_data = VentaSerializer(venta).data
        
        # 3. Generar el PDF pasando el DICCIONARIO (venta_data) y los detalles
        from .pdf_utils import generar_comprobante_venta
        pdf_content = generar_comprobante_venta(venta_data, detalles)
        
        if pdf_content:
            print("✅ VISTA: PDF generado, enviando respuesta")
            response = HttpResponse(pdf_content, content_type='application/pdf')
            # Nombre del archivo para descarga
            filename = f"Comprobante_HairSoft_Venta_{venta.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            print("❌ VISTA: pdf_content es None")
            return HttpResponse("Error al generar el PDF", status=500)
            
    except Exception as e:
        print(f"❌ VISTA: Error: {str(e)}")
        import traceback
        print(f"❌ VISTA: Traceback: {traceback.format_exc()}")
        return HttpResponse(f"Error: {str(e)}", status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def generar_comprobante_pdf(request, venta_id):
    """
    Vista para generar y descargar el comprobante PDF de una venta
    """
    try:
        print(f"🔍 VISTA: Iniciando generación PDF para venta {venta_id}")
        
        # 1. Obtener el objeto de base de datos
        venta = get_object_or_404(Venta, id=venta_id)
        detalles = DetalleVenta.objects.filter(venta=venta)
        
        print(f"✅ VISTA: Venta {venta.id} encontrada")
        
        # 2. 🚨 EL PASO QUE FALTABA: SERIALIZAR (Convertir Objeto a Diccionario)
        # Importamos el serializador aquí mismo para asegurar que lo encuentre
        from .serializers import VentaSerializer
        serializer = VentaSerializer(venta)
        venta_data = serializer.data  # <--- ESTO CONVIERTE EL OBJETO EN DICCIONARIO
        
        # 3. Generar el PDF pasando el DICCIONARIO
        from .pdf_utils import generar_comprobante_venta
        
        # Ahora le pasamos 'venta_data' (el diccionario) en vez de 'venta' (el objeto)
        pdf_content = generar_comprobante_venta(venta_data, detalles)
        
        if pdf_content:
            print("✅ VISTA: PDF generado, enviando respuesta")
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Comprobante_Venta_{venta.id}.pdf"'
            return response
        else:
            return HttpResponse("Error al generar el PDF", status=500)
            
    except Exception as e:
        print(f"❌ VISTA Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {str(e)}", status=500)

@api_view(['POST'])
def anular_venta(request, venta_id):
    """
    Anula una venta y devuelve el stock de los productos
    """
    try:
        with transaction.atomic():
            # Obtener la venta
            venta = get_object_or_404(Venta, id=venta_id)
            
            # Verificar que no esté ya anulada
            if venta.anulada:
                return Response(
                    {'error': 'Esta venta ya está anulada'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener los detalles de la venta
            detalles = DetalleVenta.objects.filter(venta=venta)
            
            # Devolver el stock de los productos
            for detalle in detalles:
                if detalle.producto:
                    producto = detalle.producto
                    producto.stock_actual += detalle.cantidad
                    producto.save()
            
            # Marcar la venta como anulada
            venta.anulada = True
            venta.save()
            
            # Registrar en logs
            print(f"✅ Venta #{venta_id} anulada. Stock devuelto.")
            
            return Response(
                {'message': f'Venta #{venta_id} anulada exitosamente. Stock actualizado.'},
                status=status.HTTP_200_OK
            )
            
    except Exception as e:
        print(f"❌ Error anulando venta: {str(e)}")
        return Response(
            {'error': 'Error interno al anular la venta'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ================================
# PEDIDOS
# ================================

class PedidoListCreateAPIView(generics.ListCreateAPIView):
    """Listar y crear pedidos - VERSIÓN DEBUG"""
    queryset = Pedido.objects.all()\
        .select_related('proveedor', 'usuario_creador')\
        .prefetch_related('detalles__producto')\
        .order_by('-fecha_pedido')
    serializer_class = PedidoSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """DEBUG: Permitir que el serializer maneje el usuario_creador"""
        try:
            # Dejar que el serializer se encargue del usuario_creador
            serializer.save()
        except Exception as e:
            print(f"❌ Error en perform_create: {e}")
            # Forzar guardado sin usuario_creador
            serializer.save()

class PedidoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Detalle, actualizar y eliminar pedidos"""
    queryset = Pedido.objects.all()\
        .select_related('proveedor', 'usuario_creador')\
        .prefetch_related('detalles__producto')
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_pedidos(request):
    """Buscar pedidos por diferentes criterios - VERSIÓN MEJORADA"""
    try:
        pedido_id = request.GET.get('id')
        proveedor_id = request.GET.get('proveedor_id')
        estado = request.GET.get('estado')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')

        # ✅ MEJORA: Cargar más eficientemente los detalles
        pedidos = Pedido.objects.all()\
            .select_related('proveedor', 'usuario_creador')\
            .prefetch_related('detalles__producto')\
            .order_by('-fecha_pedido')

        # Aplicar filtros
        if pedido_id:
            try:
                pedidos = pedidos.filter(id=int(pedido_id))
            except ValueError:
                return Response({'error': 'ID de pedido inválido'}, status=400)
                
        if proveedor_id:
            try:
                pedidos = pedidos.filter(proveedor_id=int(proveedor_id))
            except ValueError:
                return Response({'error': 'ID de proveedor inválido'}, status=400)
                
        if estado:
            # Validar que el estado sea uno de los permitidos
            estados_permitidos = ['PENDIENTE', 'CONFIRMADO', 'ENTREGADO', 'CANCELADO', 'PARCIAL']
            if estado.upper() in estados_permitidos:
                pedidos = pedidos.filter(estado=estado.upper())
            else:
                return Response({'error': f'Estado inválido. Estados permitidos: {", ".join(estados_permitidos)}'}, status=400)
                
        if fecha_desde:
            try:
                fecha_d = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
                pedidos = pedidos.filter(fecha_pedido__date__gte=fecha_d)
            except ValueError:
                return Response({'error': 'Formato de fecha desde inválido. Use YYYY-MM-DD'}, status=400)
                
        if fecha_hasta:
            try:
                fecha_h = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
                pedidos = pedidos.filter(fecha_pedido__date__lte=fecha_h)
            except ValueError:
                return Response({'error': 'Formato de fecha hasta inválido. Use YYYY-MM-DD'}, status=400)

        print(f"🔍 Filtros aplicados - ID: {pedido_id}, Proveedor: {proveedor_id}, Estado: {estado}")
        print(f"📅 Fechas - Desde: {fecha_desde}, Hasta: {fecha_hasta}")
        print(f"📊 Resultados: {pedidos.count()} pedidos encontrados")

        # ✅ DEBUG: Verificar que los detalles se carguen
        if pedidos.exists():
            primer_pedido = pedidos.first()
            print(f"🔍 Primer pedido - ID: {primer_pedido.id}, Detalles count: {primer_pedido.detalles.count()}")
            if primer_pedido.detalles.exists():
                primer_detalle = primer_pedido.detalles.first()
                print(f"🔍 Primer detalle - Producto: {primer_detalle.producto.nombre}, Cantidad: {primer_detalle.cantidad}")

        serializer = PedidoBusquedaSerializer(pedidos, many=True)
        
        # ✅ DEBUG: Verificar datos serializados
        if serializer.data and len(serializer.data) > 0:
            print(f"✅ Datos serializados - Primer pedido detalles: {serializer.data[0].get('detalles', [])}")
        
        return Response(serializer.data)

    except Exception as e:
        print(f"❌ Error en buscar_pedidos: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def cancelar_pedido(request, pedido_id):
    """Cancelar un pedido pendiente"""
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        if not pedido.puede_ser_cancelado():
            return Response({
                'error': 'No se puede cancelar el pedido. Solo se pueden cancelar pedidos en estado PENDIENTE.'
            }, status=status.HTTP_400_BAD_REQUEST)

        pedido.cancelar_pedido()
        
        return Response({
            'message': 'Pedido cancelado exitosamente.',
            'pedido_id': pedido.id,
            'estado': pedido.estado
        })

    except Pedido.DoesNotExist:
        return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def recibir_pedido(request, pedido_id):
    """Registrar recepción de un pedido - VERSIÓN SIMPLIFICADA"""
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        # Validación simple
        if pedido.estado not in ['PENDIENTE', 'CONFIRMADO']:
            return Response({
                'error': f'No se puede recibir el pedido. Estado actual: {pedido.estado}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Procesar recepción directamente
        with transaction.atomic():
            # Actualizar stock con cantidades ORIGINALES
            for detalle in pedido.detalles.all():
                if detalle.producto:
                    detalle.producto.stock_actual += detalle.cantidad
                    detalle.producto.save()
            
            # ✅ CORRECTO: Marcar pedido como ENTREGADO
            pedido.estado = 'ENTREGADO'
            pedido.fecha_recepcion = timezone.now()
            pedido.save()

        return Response({
            'message': 'Pedido recibido exitosamente.',
            'pedido_id': pedido.id,
            'estado': pedido.estado,
            'fecha_recepcion': pedido.fecha_recepcion
        })

    except Pedido.DoesNotExist:
        return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def pedidos_pendientes_recepcion(request):
    """Obtener lista de pedidos pendientes de recepción"""
    try:
        pedidos = Pedido.objects.filter(estado__in=['PENDIENTE', 'PARCIAL'])\
            .select_related('proveedor', 'usuario_creador')\
            .prefetch_related('detalles__producto')\
            .order_by('fecha_pedido')

        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def pedidos_para_cancelar(request):
    """Obtener lista de pedidos que pueden ser cancelados"""
    try:
        pedidos = Pedido.objects.filter(estado='PENDIENTE')\
            .select_related('proveedor', 'usuario_creador')\
            .prefetch_related('detalles__producto')\
            .order_by('fecha_pedido')

        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def datos_crear_pedido(request):
    """Obtener proveedores activos, productos y categorías para crear pedidos"""
    try:
        proveedores_activos = Proveedor.objects.filter(estado='ACTIVO')
        productos = Producto.objects.all().select_related('categoria').prefetch_related('proveedores')
        categorias = CategoriaProducto.objects.all().order_by('nombre')
        
        proveedores_data = ProveedorSerializer(proveedores_activos, many=True).data
        productos_data = ProductoSerializer(productos, many=True).data
        categorias_data = CategoriaProductoSerializer(categorias, many=True).data
        
        return Response({
            'proveedores': proveedores_data,
            'productos': productos_data,
            'categorias': categorias_data  # ✅ NUEVO: Incluir categorías
        })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#-----TEMPORAAAAAAAALLLLLL

@api_view(['POST'])
@permission_classes([AllowAny])
def debug_crear_pedido(request):
    """Endpoint temporal para debug de creación de pedidos"""
    try:
        print("🔍 DEBUG: Datos recibidos:", request.data)
        
        # Verificar que hay un usuario disponible
        usuario = Usuario.objects.filter(estado='ACTIVO').first()
        if not usuario:
            # Crear usuario temporal
            rol = Rol.objects.filter(nombre__iexact='administrador').first()
            if not rol:
                rol = Rol.objects.create(nombre='Administrador', descripcion='Rol debug')
            
            usuario = Usuario.objects.create(
                nombre='Debug', 
                apellido='User',
                dni='88888888',
                correo='debug@temp.com',
                contrasena='temp',
                rol=rol,
                estado='ACTIVO'
            )
        
        # Crear pedido manualmente
        from django.db import transaction
        
        with transaction.atomic():
            pedido = Pedido.objects.create(
                proveedor_id=request.data.get('proveedor'),
                observaciones=request.data.get('observaciones', ''),
                usuario_creador=usuario
            )
            
            # Crear detalles
            total = 0
            for detalle in request.data.get('detalles', []):
                detalle_obj = DetallePedido.objects.create(
                    pedido=pedido,
                    producto_id=detalle.get('producto'),
                    cantidad=detalle.get('cantidad', 1),
                    precio_unitario=detalle.get('precio_unitario', 0),
                    subtotal=detalle.get('cantidad', 1) * detalle.get('precio_unitario', 0)
                )
                total += detalle_obj.subtotal
            
            pedido.total = total
            pedido.save()
        
        return Response({
            'status': 'ok',
            'message': 'Pedido creado en modo debug',
            'pedido_id': pedido.id
        })
        
    except Exception as e:
        print(f"❌ Error en debug_crear_pedido: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return Response({'error': str(e)}, status=500)


# ===========================================
# PROPUESTA Y CONFIRMACIÓN DE PRECIOS
# ===========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def proponer_precios(request, pedido_id):
    """
    El proveedor propone precios para cada detalle del pedido.
    """
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        detalles_data = request.data.get('detalles', [])

        if not detalles_data:
            return Response({'error': 'Debe enviar los detalles con precios.'}, status=400)

        for d in detalles_data:
            detalle = pedido.detalles.get(id=d['id'])
            precio_propuesto = d.get('precio_propuesto')

            if precio_propuesto is None:
                return Response({'error': f'Falta precio_propuesto para el detalle {d["id"]}'}, status=400)

            detalle.precio_propuesto = precio_propuesto
            detalle.subtotal = detalle.cantidad * precio_propuesto
            detalle.save()

        return Response({'mensaje': 'Precios propuestos guardados correctamente.'})

    except DetallePedido.DoesNotExist:
        return Response({'error': 'Uno de los detalles no existe.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def confirmar_precios(request, pedido_id):
    """
    El comercio confirma los precios propuestos y actualiza totales.
    """
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        total = 0

        for detalle in pedido.detalles.all():
            if detalle.precio_propuesto is not None:
                detalle.precio_unitario = detalle.precio_propuesto
                detalle.subtotal = detalle.cantidad * detalle.precio_unitario
                detalle.save()
            total += detalle.subtotal

        pedido.total = total
        pedido.estado = 'CONFIRMADO'
        pedido.save()

        return Response({
            'mensaje': 'Precios confirmados correctamente.',
            'pedido_id': pedido.id,
            'total': pedido.total
        })

    except Exception as e:
        return Response({'error': str(e)}, status=400)


####proveedores
class ListaPrecioProveedorViewSet(viewsets.ModelViewSet):
    queryset = ListaPrecioProveedor.objects.all()
    serializer_class = ListaPrecioProveedorSerializer
    # QUITAmos TEMPORALMENTE LA AUTENTICACIÓN
    permission_classes = []

    def get_queryset(self):
        """Filtra por proveedor y producto si se especifican"""
        queryset = super().get_queryset()
        
        proveedor_id = self.request.query_params.get('proveedor_id')
        if proveedor_id:
            queryset = queryset.filter(proveedor_id=proveedor_id)
            
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
            
        solo_activos = self.request.query_params.get('activos', 'true').lower() == 'true'
        if solo_activos:
            queryset = queryset.filter(activo=True)
            
        return queryset

    @action(detail=False, methods=['get'])
    def por_proveedor(self, request):
        """Obtiene todas las listas de precios de un proveedor específico"""
        proveedor_id = request.query_params.get('proveedor_id')
        if not proveedor_id:
            return Response(
                {'error': 'Se requiere el parámetro proveedor_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        proveedor = get_object_or_404(Proveedor, id=proveedor_id)
        listas = self.get_queryset().filter(proveedor=proveedor, activo=True)
        serializer = self.get_serializer(listas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactiva una lista de precios"""
        lista_precio = self.get_object()
        lista_precio.activo = False
        lista_precio.save()
        
        return Response({
            'message': 'Lista de precios desactivada correctamente',
            'lista_id': lista_precio.id
        })

    @action(detail=False, methods=['post'])
    def actualizar_masivo(self, request):
        """Actualización masiva de listas de precios"""
        serializer = ActualizarListaPreciosSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        proveedor_id = serializer.validated_data['proveedor_id']
        precios_data = serializer.validated_data['precios']
        
        try:
            with transaction.atomic():
                proveedor = Proveedor.objects.get(id=proveedor_id)
                actualizados = 0
                creados = 0
                
                for precio_item in precios_data:
                    producto_id = precio_item.get('producto_id')
                    precio_base = precio_item.get('precio_base')
                    margen_ganancia = precio_item.get('margen_ganancia', 30.0)
                    
                    producto = Producto.objects.get(id=producto_id)
                    
                    # Buscar si ya existe una lista activa
                    lista_existente = ListaPrecioProveedor.objects.filter(
                        proveedor=proveedor,
                        producto=producto,
                        activo=True
                    ).first()
                    
                    if lista_existente:
                        # Crear registro en historial antes de actualizar
                        HistorialPrecios.objects.create(
                            lista_precio=lista_existente,
                            precio_anterior=lista_existente.precio_base,
                            precio_nuevo=precio_base,
                            margen_anterior=lista_existente.margen_ganancia,
                            margen_nuevo=margen_ganancia,
                            usuario=request.user,
                            motivo=precio_item.get('motivo', 'Actualización masiva')
                        )
                        
                        # Actualizar lista existente
                        lista_existente.precio_base = precio_base
                        lista_existente.margen_ganancia = margen_ganancia
                        lista_existente.save()
                        actualizados += 1
                    else:
                        # Crear nueva lista
                        ListaPrecioProveedor.objects.create(
                            proveedor=proveedor,
                            producto=producto,
                            precio_base=precio_base,
                            margen_ganancia=margen_ganancia
                        )
                        creados += 1
                
                return Response({
                    'message': f'Listas de precios actualizadas: {actualizados} actualizadas, {creados} nuevas',
                    'actualizados': actualizados,
                    'creados': creados
                })
                
        except Exception as e:
            return Response(
                {'error': f'Error en actualización masiva: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class HistorialPreciosViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialPrecios.objects.all().select_related(
        'lista_precio', 'lista_precio__proveedor', 'lista_precio__producto', 'usuario'
    ).order_by('-fecha_cambio')
    
    serializer_class = HistorialPreciosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtra por lista de precios o proveedor"""
        queryset = super().get_queryset()
        
        lista_precio_id = self.request.query_params.get('lista_precio_id')
        if lista_precio_id:
            queryset = queryset.filter(lista_precio_id=lista_precio_id)
            
        proveedor_id = self.request.query_params.get('proveedor_id')
        if proveedor_id:
            queryset = queryset.filter(lista_precio__proveedor_id=proveedor_id)
            
        producto_id = self.request.query_params.get('producto_id')
        if producto_id:
            queryset = queryset.filter(lista_precio__producto_id=producto_id)
            
        return queryset


# Servicio para cálculo de precios por volumen
class PreciosService:
    @staticmethod
    def calcular_precio_sugerido(proveedor_id, producto_id, cantidad):
        """Calcula precio sugerido basado en volumen"""
        try:
            lista_precio = ListaPrecioProveedor.objects.get(
                proveedor_id=proveedor_id,
                producto_id=producto_id,
                activo=True
            )
            
            precio_base = lista_precio.precio_base
            margen_base = lista_precio.margen_ganancia
            
            # Aplicar descuento por volumen
            descuento_volumen = PreciosService._calcular_descuento_volumen(cantidad)
            margen_final = margen_base * (1 - descuento_volumen / 100)
            
            precio_sugerido = precio_base * (1 + (margen_final / 100))
            
            return {
                'precio_base': float(precio_base),
                'precio_sugerido': float(precio_sugerido),
                'margen_aplicado': float(margen_final),
                'descuento_volumen': float(descuento_volumen),
                'lista_precio_id': lista_precio.id
            }
            
        except ListaPrecioProveedor.DoesNotExist:
            return None

    @staticmethod
    def _calcular_descuento_volumen(cantidad):
        """Calcula el descuento aplicable por volumen de compra"""
        if cantidad >= 100:
            return 15.0  # 15% de descuento
        elif cantidad >= 50:
            return 10.0  # 10% de descuento
        elif cantidad >= 25:
            return 5.0   # 5% de descuento
        else:
            return 0.0   # Sin descuento


# Vistas para cálculo de precios
@api_view(['POST'])
def calcular_precios_pedido(request):
    """Calcula precios sugeridos para un pedido"""
    items = request.data.get('items', [])
    resultados = []
    
    for item in items:
        producto_id = item.get('producto_id')
        proveedor_id = item.get('proveedor_id')
        cantidad = item.get('cantidad', 1)
        
        if not all([producto_id, proveedor_id]):
            continue
            
        calculo = PreciosService.calcular_precio_sugerido(
            proveedor_id, producto_id, cantidad
        )
        
        if calculo:
            resultados.append({
                'producto_id': producto_id,
                'proveedor_id': proveedor_id,
                'cantidad': cantidad,
                **calculo
            })
        else:
            resultados.append({
                'producto_id': producto_id,
                'proveedor_id': proveedor_id,
                'cantidad': cantidad,
                'error': 'No se encontró lista de precios activa'
            })
    
    return Response(resultados)

@api_view(['GET'])
def calcular_precio_sugerido(request):
    """Calcula precio sugerido para un producto específico"""
    producto_id = request.GET.get('producto_id')
    proveedor_id = request.GET.get('proveedor_id')
    cantidad = int(request.GET.get('cantidad', 1))
    
    if not all([producto_id, proveedor_id]):
        return Response(
            {'error': 'Se requieren producto_id y proveedor_id'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    calculo = PreciosService.calcular_precio_sugerido(
        proveedor_id, producto_id, cantidad
    )
    
    if calculo:
        return Response(calculo)
    else:
        return Response(
            {'error': 'No se encontró lista de precios activa'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def listas_por_proveedor(request):
    """Obtiene listas de precios por proveedor"""
    proveedor_id = request.GET.get('proveedor_id')
    if not proveedor_id:
        return Response(
            {'error': 'Se requiere proveedor_id'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    listas = ListaPrecioProveedor.objects.filter(
        proveedor_id=proveedor_id, 
        activo=True
    ).select_related('producto')
    
    serializer = ListaPrecioProveedorSerializer(listas, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def desactivar_lista_precio(request, pk):
    """Desactiva una lista de precios"""
    lista_precio = get_object_or_404(ListaPrecioProveedor, id=pk)
    lista_precio.activo = False
    lista_precio.save()
    
    return Response({
        'message': 'Lista de precios desactivada correctamente',
        'lista_id': lista_precio.id
    })

@api_view(['POST'])
def actualizar_listas_masivo(request):
    """Actualización masiva de listas de precios"""
    serializer = ActualizarListaPreciosSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    proveedor_id = serializer.validated_data['proveedor_id']
    precios_data = serializer.validated_data['precios']
    
    try:
        with transaction.atomic():
            proveedor = Proveedor.objects.get(id=proveedor_id)
            actualizados = 0
            creados = 0
            
            for precio_item in precios_data:
                producto_id = precio_item.get('producto_id')
                precio_base = precio_item.get('precio_base')
                margen_ganancia = precio_item.get('margen_ganancia', 30.0)
                
                producto = Producto.objects.get(id=producto_id)
                
                # Buscar si ya existe una lista activa
                lista_existente = ListaPrecioProveedor.objects.filter(
                    proveedor=proveedor,
                    producto=producto,
                    activo=True
                ).first()
                
                if lista_existente:
                    # Crear registro en historial antes de actualizar
                    HistorialPrecios.objects.create(
                        lista_precio=lista_existente,
                        precio_anterior=lista_existente.precio_base,
                        precio_nuevo=precio_base,
                        margen_anterior=lista_existente.margen_ganancia,
                        margen_nuevo=margen_ganancia,
                        usuario=request.user,
                        motivo=precio_item.get('motivo', 'Actualización masiva')
                    )
                    
                    # Actualizar lista existente
                    lista_existente.precio_base = precio_base
                    lista_existente.margen_ganancia = margen_ganancia
                    lista_existente.save()
                    actualizados += 1
                else:
                    # Crear nueva lista
                    ListaPrecioProveedor.objects.create(
                        proveedor=proveedor,
                        producto=producto,
                        precio_base=precio_base,
                        margen_ganancia=margen_ganancia
                    )
                    creados += 1
            
            return Response({
                'message': f'Listas de precios actualizadas: {actualizados} actualizadas, {creados} nuevas',
                'actualizados': actualizados,
                'creados': creados
            })
            
    except Exception as e:
        return Response(
            {'error': f'Error en actualización masiva: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# ================================
# DASHBOARD ENDPOINT - VERSIÓN SIMPLIFICADA TEMPORAL
# ================================

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_data(request):
    """Endpoint REAL para dashboard - consulta la base de datos"""
    try:
        print("✅ Dashboard endpoint llamado - consultando BD real")
        
        # Obtener el período del request
        period = request.GET.get('period', 'semana')
        
        # 🔥 CONSULTAS REALES A LA BASE DE DATOS
        
        # 1. INGRESOS TOTALES (último mes)
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        fecha_inicio = timezone.now() - timedelta(days=30)
        ingresos_totales = Venta.objects.filter(
            fecha__gte=fecha_inicio, 
            anulada=False
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # 2. SERVICIOS REALIZADOS (último mes)
        servicios_realizados = Turno.objects.filter(
            fecha__gte=fecha_inicio,
            estado='COMPLETADO'
        ).count()
        
        # 3. CLIENTES NUEVOS (último mes)
        clientes_nuevos = Usuario.objects.filter(
            fecha_creacion__gte=fecha_inicio,
            rol__nombre__iexact='cliente'
        ).count()
        
        # 4. PRODUCTOS VENDIDOS (último mes)
        productos_vendidos = DetalleVenta.objects.filter(
            venta__fecha__gte=fecha_inicio,
            venta__anulada=False,
            producto__isnull=False
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        # 5. TICKET PROMEDIO
        ticket_promedio = ingresos_totales / max(servicios_realizados, 1)
        
        # 6. STOCK BAJO (productos con stock por debajo del mínimo)
        # Asumiendo que tienes un campo stock_minimo en Producto
        stock_bajo = Producto.objects.filter(
            stock_actual__lte=5  # Ajusta según tu lógica de stock mínimo
        )[:5]  # Limitar a 5 productos
        
        stock_bajo_data = [
            {
                'nombre': producto.nombre,
                'stock_actual': producto.stock_actual,
                'stock_minimo': 5,  # Ajusta según tu modelo
                'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría'
            }
            for producto in stock_bajo
        ]
        
        # 7. SERVICIOS TOP (más vendidos)
        from django.db.models import Count
        servicios_top = Servicio.objects.annotate(
            ventas_count=Count('detalleventa')
        ).order_by('-ventas_count')[:3]
        
        servicios_top_data = [
            {
                'nombre': servicio.nombre,
                'cantidad': servicio.ventas_count,
                'ingresos': servicio.ventas_count * servicio.precio,
                'tendencia': 0  # Podrías calcular la tendencia vs período anterior
            }
            for servicio in servicios_top
        ]
        
        # 8. TOP PELUQUEROS (más servicios completados)
        top_peluqueros = Usuario.objects.filter(
            turnos_peluquero__estado='COMPLETADO',
            turnos_peluquero__fecha__gte=fecha_inicio
        ).annotate(
            servicios_count=Count('turnos_peluquero'),
            ingresos_total=Sum('turnos_peluquero__monto_total')
        ).order_by('-servicios_count')[:3]
        
        top_peluqueros_data = [
            {
                'nombre': f"{p.nombre} {p.apellido}",
                'servicios_completados': p.servicios_count,
                'ingresos_generados': p.ingresos_total or 0
            }
            for p in top_peluqueros
        ]
        
        # 9. VENTAS POR DÍA (últimos 7 días)
        ventas_por_dia = []
        labels_dias = []
        
        for i in range(6, -1, -1):
            fecha = timezone.now() - timedelta(days=i)
            total_dia = Venta.objects.filter(
                fecha__date=fecha.date(),
                anulada=False
            ).aggregate(total=Sum('total'))['total'] or 0
            
            ventas_por_dia.append(float(total_dia))
            labels_dias.append(fecha.strftime('%a'))
        
        # Datos REALES de tu base de datos
        data = {
            'ingresosTotales': float(ingresos_totales),
            'serviciosRealizados': servicios_realizados,
            'clientesNuevos': clientes_nuevos,
            'productosVendidos': productos_vendidos,
            'ticketPromedio': float(ticket_promedio),
            'ventasTrend': 0,  # Podrías calcular vs período anterior
            'metaMensual': 150000.0,
            'totalClientes': Usuario.objects.filter(rol__nombre__iexact='cliente').count(),
            'stockBajoCount': stock_bajo.count(),
            'stockBajo': stock_bajo_data,
            'serviciosTop': servicios_top_data,
            'topPeluqueros': top_peluqueros_data,
            'productosTop': [],  # Podrías implementar similar a servicios_top
            'ventasPorDia': ventas_por_dia,
            'serviciosDistribucion': [],  # Podrías implementar
            'labelsDias': labels_dias
        }
        
        print(f"✅ Datos REALES enviados - Ingresos: ${ingresos_totales}, Servicios: {servicios_realizados}")
        return Response(data)
        
    except Exception as e:
        print(f"❌ Error en dashboard REAL: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return Response({'error': str(e)}, status=500)

# ================================
# CONFIGURACIÓN REOFERTA AUTOMÁTICA
# ================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_configuracion_reoferta(request):
    """Obtiene la configuración actual del módulo de reoferta"""
    try:
        from .models import ConfiguracionReoferta
        config = ConfiguracionReoferta.get_configuracion()
        
        return Response({
            'id': config.id,
            'descuento_por_defecto': float(config.descuento_por_defecto),
            'tiempo_limite_respuesta': config.tiempo_limite_respuesta,
            'max_intentos_notificacion': config.max_intentos_notificacion,
            'activo': config.activo,
            'notificar_email': config.notificar_email,
            'notificar_whatsapp': config.notificar_whatsapp,
            'fecha_actualizacion': config.fecha_actualizacion
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def actualizar_configuracion_reoferta(request):
    """Actualiza la configuración del módulo de reoferta"""
    try:
        from .models import ConfiguracionReoferta
        
        config = ConfiguracionReoferta.get_configuracion()
        
        # Actualizar campos
        if 'descuento_por_defecto' in request.data:
            config.descuento_por_defecto = request.data['descuento_por_defecto']
        if 'tiempo_limite_respuesta' in request.data:
            config.tiempo_limite_respuesta = request.data['tiempo_limite_respuesta']
        if 'max_intentos_notificacion' in request.data:
            config.max_intentos_notificacion = request.data['max_intentos_notificacion']
        if 'activo' in request.data:
            config.activo = request.data['activo']
        if 'notificar_email' in request.data:
            config.notificar_email = request.data['notificar_email']
        if 'notificar_whatsapp' in request.data:
            config.notificar_whatsapp = request.data['notificar_whatsapp']
        
        config.save()
        
        return Response({
            'message': 'Configuración actualizada correctamente',
            'configuracion': {
                'id': config.id,
                'descuento_por_defecto': float(config.descuento_por_defecto),
                'tiempo_limite_respuesta': config.tiempo_limite_respuesta,
                'activo': config.activo
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_reoferta(request):
    """Obtiene estadísticas del módulo de reoferta"""
    try:
        from .models import InteresTurnoLiberado
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Estadísticas generales
        total_interesados = InteresTurnoLiberado.objects.count()
        total_ofertas_enviadas = InteresTurnoLiberado.objects.filter(oferta_enviada=True).count()
        total_ofertas_aceptadas = InteresTurnoLiberado.objects.filter(oferta_aceptada=True).count()
        
        # Tasa de conversión
        tasa_conversion = 0
        if total_ofertas_enviadas > 0:
            tasa_conversion = (total_ofertas_aceptadas / total_ofertas_enviadas) * 100
        
        # Estadísticas del último mes
        ultimo_mes = datetime.now() - timedelta(days=30)
        ofertas_ultimo_mes = InteresTurnoLiberado.objects.filter(
            fecha_oferta_enviada__gte=ultimo_mes
        ).count()
        
        aceptadas_ultimo_mes = InteresTurnoLiberado.objects.filter(
            fecha_respuesta__gte=ultimo_mes,
            oferta_aceptada=True
        ).count()
        
        return Response({
            'estadisticas_generales': {
                'total_interesados': total_interesados,
                'total_ofertas_enviadas': total_ofertas_enviadas,
                'total_ofertas_aceptadas': total_ofertas_aceptadas,
                'tasa_conversion': round(tasa_conversion, 2),
                'ofertas_ultimo_mes': ofertas_ultimo_mes,
                'aceptadas_ultimo_mes': aceptadas_ultimo_mes
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def forzar_reoferta(request, turno_id):
    """Fuerza el proceso de reoferta para un turno específico"""
    try:
        from .turno_service import TurnoService
        
        resultado = TurnoService.procesar_reoferta_automatica(turno_id)
        
        return Response({
            'success': resultado,
            'message': 'Proceso de reoferta ejecutado correctamente' if resultado else 'No se pudo ejecutar la reoferta'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def procesar_respuesta_oferta(request, interes_id):
    """Webhook para procesar respuestas de clientes a ofertas de reoferta"""
    try:
        from .models import InteresTurnoLiberado, Turno
        from django.utils import timezone
        
        interes = get_object_or_404(InteresTurnoLiberado, id=interes_id)
        accion = request.data.get('accion')  # 'aceptar' o 'rechazar'
        
        if accion == 'aceptar':
            # Marcar como aceptada
            interes.aceptar_oferta()
            
            # Buscar turno cancelado relacionado
            turno_cancelado = Turno.objects.filter(
                fecha=interes.fecha_deseada,
                hora=interes.hora_deseada,
                peluquero=interes.peluquero,
                estado='CANCELADO'
            ).first()
            
            if turno_cancelado:
                # Crear nuevo turno para el cliente
                nuevo_turno = Turno.objects.create(
                    fecha=interes.fecha_deseada,
                    hora=interes.hora_deseada,
                    estado='RESERVADO',
                    canal='WEB',
                    tipo_pago='PENDIENTE',
                    medio_pago='PENDIENTE',
                    monto_seña=0,
                    monto_total=interes.servicio.precio * (1 - interes.descuento_aplicado / 100),
                    cliente=interes.cliente,
                    peluquero=interes.peluquero
                )
                nuevo_turno.servicios.add(interes.servicio)
                
                return Response({
                    'success': True,
                    'message': 'Oferta aceptada. Turno reservado exitosamente.',
                    'turno_id': nuevo_turno.id
                })
            else:
                return Response({
                    'success': False,
                    'message': 'No se encontró el turno cancelado relacionado.'
                }, status=400)
                
        elif accion == 'rechazar':
            interes.rechazar_oferta()
            return Response({
                'success': True,
                'message': 'Oferta rechazada.'
            })
        else:
            return Response({
                'success': False,
                'message': 'Acción no válida. Use "aceptar" o "rechazar".'
            }, status=400)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error procesando respuesta: {str(e)}'
        }, status=500)

# Listar todas las marcas
def listar_marcas(request):
    if request.method != "GET":
        return JsonResponse({'message': 'Método no permitido'}, status=405)

    marcas = Marca.objects.all()

    data = []
    for marca in marcas:
        # Cantidad de productos asociados a esa marca
        cantidad_productos = Producto.objects.filter(marca=marca).count()

        # Cantidad de proveedores que venden productos de esa marca
        cantidad_proveedores = Proveedor.objects.filter(
            productos__marca=marca
        ).distinct().count()

        data.append({
            "id": marca.id,
            "nombre": marca.nombre,
            "cantidad_productos": cantidad_productos,
            "cantidad_proveedores": cantidad_proveedores
        })

    return JsonResponse(data, safe=False)

# Crear una nueva marca
@csrf_exempt
def crear_marca(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'JSON inválido'}, status=400)
        
        nombre = data.get('nombre')
        if not nombre:
            return JsonResponse({'message': 'El nombre es obligatorio'}, status=400)
        
        if Marca.objects.filter(nombre=nombre).exists():
            return JsonResponse({'message': 'La marca ya existe'}, status=400)
        
        marca = Marca.objects.create(nombre=nombre)
        return JsonResponse({'id': marca.id, 'nombre': marca.nombre})
    
    return JsonResponse({'message': 'Método no permitido'}, status=405)

# ================================
# REOFERTA MASIVA - NUEVAS VISTAS
# ================================
@csrf_exempt
def cancelar_turno_con_reoferta(request, turno_id):
    """
    Cancela un turno, procesa reembolso automático si corresponde e inicia reoferta.
    """
    print(f"🔥🔥🔥 CANCELACIÓN CON REOFERTA LLAMADA - Turno: {turno_id}")
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # 1. OBTENER EL TURNO
        turno = Turno.objects.get(id=turno_id)
        print(f"📅 Turno: {turno.fecha} {turno.hora} - Estado: {turno.estado}")

        # 2. PROCESAR REEMBOLSO AUTOMÁTICO (NUEVO) 💰
        print("💳 Verificando reembolso automático...")
        reembolso_ok, mensaje_reembolso = procesar_reembolso_si_corresponde(turno)
        print(f"💰 Resultado Reembolso: {mensaje_reembolso}")

        # 3. CAMBIAR ESTADO A CANCELADO
        turno.estado = 'CANCELADO'
        turno.oferta_activa = True
        
        # Configurar expiración de la oferta (1 hora desde ahora)
        turno.fecha_expiracion_oferta = timezone.now() + timedelta(hours=1)
        turno.save()
        
        print("✅ Turno marcado como CANCELADO")

        # 4. BUSCAR INTERESADOS
        print("🔎 Buscando interesados en lista de espera...")
        interesados = turno.obtener_interesados()
        cantidad_interesados = interesados.count()
        print(f"👥 Interesados encontrados: {cantidad_interesados}")

        # 5. INICIAR REOFERTA O LIBERAR
        if cantidad_interesados > 0:
            print(f"🚀 Iniciando reoferta masiva...")
            
            # Importamos aquí para evitar ciclos
            from .tasks import procesar_reoferta_masiva
            
            # Disparar tarea Celery en segundo plano
            procesar_reoferta_masiva.delay(turno_id) 
            
            return JsonResponse({
                'status': 'ok',
                'message': f'Turno cancelado. {mensaje_reembolso} Se notificará a {cantidad_interesados} interesados.',
                'reoferta_iniciada': True,
                'interesados': cantidad_interesados,  # ✅ CORREGIDO
                'reembolso_info': mensaje_reembolso
            })
        else:
            print("ℹ️ No hay interesados. El turno queda DISPONIBLE.")
            turno.estado = 'DISPONIBLE'
            turno.oferta_activa = False
            turno.save()
            
            return JsonResponse({
                'status': 'ok', 
                'message': f'Turno cancelado. {mensaje_reembolso} No hay interesados en lista de espera.',
                'reoferta_iniciada': False,
                'interesados': cantidad_interesados,  # ✅ CORREGIDO - usa la variable
                'reembolso_info': mensaje_reembolso
            })

    except Turno.DoesNotExist:
        return JsonResponse({'error': 'Turno no encontrado'}, status=404)
    except Exception as e:
        print(f"💥 ERROR FATAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_info_oferta(request, turno_id, token):
    try:
        turno = Turno.objects.get(id=turno_id)
        interes = InteresTurnoLiberado.objects.get(
            token_oferta=token,
            turno_liberado=turno,
            estado_oferta='enviada'
        )

        if interes.oferta_expirada():
            return Response({'error': 'La oferta ha expirado.'}, status=400)

        # ✅ CÁLCULOS CORREGIDOS (TODO A DECIMAL)
        # Convertimos los números fijos a Decimal para que Python no se queje
        precio_original = interes.servicio.precio
        descuento = interes.descuento_aplicado
        
        # Usamos Decimal('1') y Decimal('100') para mantener el tipo de dato
        factor_descuento = Decimal('1') - (descuento / Decimal('100'))
        precio_final = precio_original * factor_descuento
        
        # Aquí estaba el error: cambiamos 0.5 por Decimal('0.5')
        monto_sena = precio_final * Decimal('0.5') 

        return Response({
            'fecha': turno.fecha.strftime('%d/%m/%Y'),
            'hora': turno.hora.strftime('%H:%M'),
            'profesional': f"{turno.peluquero.nombre} {turno.peluquero.apellido}",
            'servicio': interes.servicio.nombre,
            'precio_original': float(precio_original),
            'descuento': float(descuento),
            'precio_final': float(precio_final),
            'monto_sena': float(monto_sena),
            'cliente': interes.cliente.nombre
        })

    except (Turno.DoesNotExist, InteresTurnoLiberado.DoesNotExist):
        return Response({'error': 'Oferta inválida o no encontrada.'}, status=404)
    except Exception as e:
        # Agregamos print para ver el error real si pasa otra cosa
        print(f"❌ Error en obtener_info_oferta: {e}") 
        return Response({'error': f'Error interno: {str(e)}'}, status=500)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_intereses_usuario(request):
    """
    Lista intereses del usuario autenticado
    """
    try:
        intereses = InteresTurnoLiberado.objects.filter(
            cliente=request.user
        ).select_related('servicio', 'peluquero').order_by('-fecha_registro')
        
        data = []
        for interes in intereses:
            data.append({
                'id': interes.id,
                'servicio_nombre': interes.servicio.nombre,
                'peluquero_nombre': f"{interes.peluquero.nombre} {interes.peluquero.apellido}",
                'fecha_deseada': interes.fecha_deseada.strftime('%d/%m/%Y'),
                'hora_deseada': interes.hora_deseada.strftime('%H:%M'),
                'fecha_registro': interes.fecha_registro.strftime('%d/%m/%Y %H:%M'),
                'estado_oferta': interes.estado_oferta,
                'descuento_aplicado': float(interes.descuento_aplicado)
            })
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Error listando intereses: {str(e)}")
        return Response({
            'error': 'Error al cargar los intereses'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_interes_turno(request, interes_id):
    """
    Elimina un interés en turnos
    """
    try:
        interes = InteresTurnoLiberado.objects.get(id=interes_id, cliente=request.user)
        interes.delete()
        
        return Response({
            'success': True,
            'message': 'Interés eliminado correctamente'
        })
        
    except InteresTurnoLiberado.DoesNotExist:
        return Response({
            'error': 'Interés no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error eliminando interés: {str(e)}")
        return Response({
            'error': 'Error al eliminar el interés'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelar_mi_turno(request, turno_id):
    """
    Permite al cliente cancelar SU turno y recibir reembolso automático si corresponde.
    """
    try:
        turno = Turno.objects.get(id=turno_id)

        # 1. Seguridad: Que el turno sea suyo
        if turno.cliente != request.user:
            return Response({'error': 'No tienes permiso para cancelar este turno.'}, status=403)

        # 2. Validar estado
        if turno.estado == 'CANCELADO':
             return Response({'error': 'El turno ya está cancelado.'}, status=400)

        # 3. Regla de las 3 horas (Bloqueo estricto para el cliente)
        # A diferencia del Admin, al cliente NO le dejamos cancelar si falta poco.
        ahora = timezone.now()
        fecha_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
        tiempo_restante = fecha_turno - ahora

        if tiempo_restante < timedelta(hours=3):
             return Response({
                 'error': 'Ya no puedes cancelar online (faltan menos de 3hs). Por favor llama al local.'
             }, status=400)

        # 4. PROCESAR REEMBOLSO (La Magia 💸)
        # Reutilizamos la lógica que ya armamos para el admin
        reembolso_ok, mensaje_reembolso = procesar_reembolso_si_corresponde(turno)
        
        print(f"💰 Cancelación Web - Reembolso: {mensaje_reembolso}")

        # 5. Cancelar y Activar Reoferta
        turno.estado = 'CANCELADO'
        turno.oferta_activa = True
        turno.fecha_expiracion_oferta = timezone.now() + timedelta(hours=1)
        turno.save()

        # 6. Disparar Reoferta (Si corresponde)
        interesados = turno.obtener_interesados()
        if interesados.exists():
            from .tasks import procesar_reoferta_masiva
            procesar_reoferta_masiva.delay(turno.id)

        return Response({
            'status': 'ok',
            'message': f'Turno cancelado. {mensaje_reembolso}'
        })

    except Turno.DoesNotExist:
        return Response({'error': 'Turno no encontrado'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def aceptar_oferta_turno(request, turno_id, token):
    """
    Acepta oferta, gestiona canje y GENERA PAGO MP.
    """
    try:
        turno_nuevo = Turno.objects.get(id=turno_id)
        tipo_pago = request.data.get('tipo_pago', 'SENA_50') 
        
        interes = InteresTurnoLiberado.objects.get(
            token_oferta=token,
            turno_liberado=turno_nuevo,
            estado_oferta='enviada'
        )
        
        if interes.oferta_expirada():
            return Response({'error': 'La oferta ha expirado.'}, status=400)
        
        if turno_nuevo.estado != 'CANCELADO' or not turno_nuevo.oferta_activa:
            return Response({'error': 'El turno ya no está disponible.'}, status=400)

        with transaction.atomic():
            # 1. CANJE
            turno_viejo = Turno.objects.filter(
                cliente=interes.cliente,
                fecha=turno_nuevo.fecha,
                estado__in=['RESERVADO', 'CONFIRMADO']
            ).exclude(id=turno_nuevo.id).first()

            if turno_viejo:
                turno_viejo.estado = 'CANCELADO'
                turno_viejo.save()

            # 2. CONFIGURAR NUEVO TURNO
            precio_original = interes.servicio.precio
            descuento = Decimal(interes.descuento_aplicado)
            factor = Decimal('1') - (descuento / Decimal('100'))
            precio_final = precio_original * factor
            
            turno_nuevo.cliente = interes.cliente
            turno_nuevo.canal = 'WEB'
            turno_nuevo.estado = 'RESERVADO'
            turno_nuevo.oferta_activa = False
            turno_nuevo.cliente_asignado_reoferta = interes.cliente
            turno_nuevo.monto_total = precio_final
            
            turno_nuevo.tipo_pago = tipo_pago
            turno_nuevo.medio_pago = 'MERCADO_PAGO'
            
            if tipo_pago == 'SENA_50':
                turno_nuevo.monto_seña = precio_final * Decimal('0.5')
            else:
                turno_nuevo.monto_seña = precio_final
            
            turno_nuevo.save()
            turno_nuevo.servicios.clear()
            turno_nuevo.servicios.add(interes.servicio)
            
            interes.aceptar_oferta(ip_address=get_client_ip(request))
            
            InteresTurnoLiberado.objects.filter(
                turno_liberado=turno_nuevo,
                estado_oferta='enviada'
            ).exclude(id=interes.id).update(estado_oferta='rechazada')

        # 3. GENERAR LINK MP
        mp_link = None
        try:
            from .mercadopago_service import MercadoPagoService
            mp_service = MercadoPagoService()
            monto_a_cobrar = float(turno_nuevo.monto_seña)
            
            pref_data = {
                'turno_id': turno_nuevo.id,
                'monto_pago': monto_a_cobrar,
                'cliente_nombre': f"{interes.cliente.nombre} {interes.cliente.apellido}",
                'cliente_correo': interes.cliente.correo or "cliente@hairsoft.com",
                'peluquero_nombre': f"{turno_nuevo.peluquero.nombre}",
                'es_pago_total': (tipo_pago == 'TOTAL')
            }
            
            resultado = mp_service.crear_preferencia_seña(pref_data)
            if resultado['success']:
                mp_link = resultado.get('init_point') or resultado.get('sandbox_init_point')
        except Exception as e:
            print(f"⚠️ Error MP: {e}")

        from .tasks import notificar_turno_asignado
        notificar_turno_asignado.delay(turno_nuevo.id)
        
        return Response({
            'success': True,
            'mp_link': mp_link,
            'message': 'Turno confirmado. Redirigiendo a pago...'
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return Response({'error': f'Error interno: {str(e)}'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contar_interesados(request, turno_id):
    """
    Cuenta interesados con lógica flexible de hora para coincidir con la tarea de reoferta.
    """
    try:
        turno = get_object_or_404(Turno, pk=turno_id)
        
        # 1. Filtramos por Fecha, Peluquero y Estado (lo básico)
        candidatos = InteresTurnoLiberado.objects.filter(
            fecha_deseada=turno.fecha,
            peluquero=turno.peluquero,
            estado_oferta='pendiente'
        )

        # 2. Filtramos la hora manualmente ignorando los segundos
        # Esto arregla el problema de "10:00:00" vs "10:00"
        cantidad_real = 0
        for c in candidatos:
            if c.hora_deseada.hour == turno.hora.hour and c.hora_deseada.minute == turno.hora.minute:
                cantidad_real += 1

        return Response({'cantidad': cantidad_real})

    except Exception as e:
        print(f"Error contando interesados: {e}")
        return Response({'cantidad': 0})
    
@api_view(['GET', 'POST'])
@permission_classes([AllowAny]) # Esto permite que entre sin loguearse
def gestionar_cotizacion_externa(request, token):
    cotizacion = get_object_or_404(Cotizacion, token=token)

    if request.method == 'GET':
        if cotizacion.respondio:
            return Response({"ya_respondido": True})
        serializer = CotizacionExternaSerializer(cotizacion)
        return Response(serializer.data)

    if request.method == 'POST':
        if cotizacion.respondio:
            return Response({"error": "Ya respondiste esta solicitud"}, status=400)
        
        cotizacion.precio_ofrecido = request.data.get('precio_ofrecido')
        cotizacion.dias_entrega = request.data.get('dias_entrega')
        cotizacion.comentarios = request.data.get('comentarios', '')
        cotizacion.respondio = True
        cotizacion.fecha_respuesta = timezone.now()
        cotizacion.save()
        return Response({"mensaje": "Éxito"})

# usuarios/views.py (Al final)

class SolicitudPresupuestoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para que el Gerente vea y gestione las licitaciones de stock.
    """
    queryset = SolicitudPresupuesto.objects.all().order_by('-fecha_creacion')
    serializer_class = SolicitudPresupuestoSerializer
    
    def get_queryset(self):
        # Filtramos para no mostrar las que ya están archivadas hace mucho
        return SolicitudPresupuesto.objects.exclude(estado='CERRADA_ARCHIVADA')

    @action(detail=True, methods=['post'], url_path='generar-orden')
    @transaction.atomic
    def generar_orden_compra(self, request, pk=None):
        """
        Acción: El Gerente elige una cotización ganadora -> Se crea el Pedido.
        """
        solicitud = self.get_object()
        cotizacion_id = request.data.get('cotizacion_id')
        
        # 1. Validar que la cotización pertenece a esta solicitud
        try:
            cotizacion_ganadora = Cotizacion.objects.get(id=cotizacion_id, solicitud=solicitud)
        except Cotizacion.DoesNotExist:
            return Response({"error": "Cotización no válida para esta solicitud"}, status=400)

        if solicitud.estado == 'CERRADA':
             return Response({"error": "Esta solicitud ya fue cerrada."}, status=400)

        # 2. Crear el PEDIDO DE COMPRA automáticamente
        # Asumimos que request.user es el gerente logueado
        nuevo_pedido = Pedido.objects.create(
            proveedor=cotizacion_ganadora.proveedor,
            usuario_creador=request.user, 
            estado='CONFIRMADO', # Nace confirmado porque viene de una licitación ganada
            total=cotizacion_ganadora.precio_ofrecido,
            observaciones=f"Autogenerado por Solicitud #{solicitud.id}. Entrega: {cotizacion_ganadora.dias_entrega} días."
        )

        # 3. Crear el detalle del pedido (el producto en cuestión)
        # Calculamos precio unitario
        precio_unitario = cotizacion_ganadora.precio_ofrecido / solicitud.cantidad_requerida
        
        DetallePedido.objects.create(
            pedido=nuevo_pedido,
            producto=solicitud.producto,
            cantidad=solicitud.cantidad_requerida,
            precio_unitario=precio_unitario,
            cantidad_recibida=0,
            precio_propuesto=cotizacion_ganadora.precio_ofrecido # Guardamos el total ofertado
        )

        # 4. Actualizar estados
        solicitud.estado = 'CERRADA'
        solicitud.pedido_generado = nuevo_pedido
        solicitud.save()

        # Marcar cual ganó para estadísticas futuras
        cotizacion_ganadora.es_la_mejor = True
        cotizacion_ganadora.save()

        return Response({
            "mensaje": f"¡Orden de Compra #{nuevo_pedido.id} generada con éxito!",
            "pedido_id": nuevo_pedido.id
        })