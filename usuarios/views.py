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
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response 
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Rol, Permiso, Usuario, Servicio, CategoriaProducto, CategoriaServicio, Producto, Turno, Proveedor, Venta, DetalleVenta, MetodoPago, Pedido, DetallePedido, ListaPrecioProveedor, HistorialPrecios
from .mercadopago_service import MercadoPagoService
import json, re, requests
from .serializers import LoginSerializer, ProveedorSerializer, ProductoSerializer, VentaSerializer, DetalleVentaSerializer, CategoriaProductoSerializer, MetodoPagoSerializer, VentaUpdateSerializer, CategoriaServicioSerializer, PedidoSerializer, DetallePedidoSerializer, PedidoRecepcionSerializer, PedidoBusquedaSerializer, ListaPrecioProveedorSerializer, HistorialPreciosSerializer, PrecioSugeridoSerializer, ActualizarListaPreciosSerializer
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from .pdf_utils import generar_comprobante_venta

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
    print("LOGIN ENDPOINT HIT")
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    correo = validated_data.get('username')
    contrasena_ingresada = validated_data.get('password')
    
    print(f"Data Validada - Correo: {correo}")

    try:
        user = Usuario.objects.get(correo=correo)
        
        if user and check_password(contrasena_ingresada, user.contrasena):
            # 🔧 FIX: indicar backend manualmente
            from django.contrib.auth import get_backends, login
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            
            print(f"✅ Login successful - User ID: {user.id}")
            
            user_rol = getattr(user, 'rol', None)
            rol_nombre = user_rol.nombre.upper() if user_rol else 'SIN_ROL'
            
            return Response({
                'status': 'ok',
                'message': 'Login exitoso',
                'user_id': user.id,
                'rol': rol_nombre
            }, status=status.HTTP_200_OK)
        else:
            raise Usuario.DoesNotExist

    except Usuario.DoesNotExist:
        print("Login failed - Credenciales inválidas")
        return Response(
            {'status': 'error', 'message': 'Credenciales inválidas. Usuario no registrado o contraseña incorrecta.'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

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
    # 1. Definimos la fuente de datos (tus 6 productos)
    queryset = Producto.objects.select_related('categoria').all()  # Cargar la categoría relacionada
    
    # 2. Definimos quién los traduce (tu Serializer)
    serializer_class = ProductoSerializer

    # 3. Mantenemos la lógica de filtros que ya tenías
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por nombre (tu código original)
        nombre = self.request.query_params.get('nombre')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        # Filtro por categoría (tu código original)
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        return queryset
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

        # ===== Query base =====
        turnos = Turno.objects.all().select_related('cliente', 'peluquero').prefetch_related('servicios').order_by('fecha', 'hora')

        # ===== Filtro por peluquero =====
        if peluquero_id:
            turnos = turnos.filter(peluquero__id=peluquero_id)

        # ===== Filtro por estado =====
        if estado:
            # Mapear estados del frontend a estados de BD
            estado_map_frontend_to_db = {
                'RESERVADO': 'RESERVADO',
                'CONFIRMADO': 'CONFIRMADO', 
                'CANCELADO': 'CANCELADO',
                'COMPLETADO': 'COMPLETADO',
                # Para compatibilidad con viejo sistema
                'PENDIENTE': 'RESERVADO',
                'PEND': 'RESERVADO',
                'CONF': 'CONFIRMADO',
                'CANC': 'CANCELADO',
                'COMP': 'COMPLETADO'
            }
            estado_bd = estado_map_frontend_to_db.get(estado.upper(), estado.upper())
            turnos = turnos.filter(estado=estado_bd)

        # ===== Filtro por canal =====
        if canal and hasattr(Turno, 'canal'):
            turnos = turnos.filter(canal=canal.upper())

        # ===== Filtro por fechas =====
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

        # ===== Construcción del resultado =====
        data = []
        for t in turnos:
            servicios_list = []
            duracion_total = 0
            
            for servicio in t.servicios.all():
                servicios_list.append({
                    'id': servicio.id,
                    'nombre': servicio.nombre,
                    'precio': float(servicio.precio),
                    'duracion': servicio.duracion,
                    'categoria': servicio.categoria.id if servicio.categoria else None  # ← CORREGIDO
                })
                duracion_total += servicio.duracion

            # Calcular si puede ser modificado/cancelado - CORREGIDO
            puede_modificar = False
            puede_cancelar = False
            
            try:
                ahora = timezone.now()
                # CORRECCIÓN: Crear datetime naive primero y luego hacerlo aware
                fecha_turno_naive = datetime.combine(t.fecha, t.hora)
                fecha_turno = timezone.make_aware(fecha_turno_naive)
                tres_horas_antes = fecha_turno - timedelta(hours=3)
                
                puede_modificar = (t.estado in ['RESERVADO', 'CONFIRMADO'] and 
                                  ahora < tres_horas_antes)
                puede_cancelar = puede_modificar
                
                print(f"Turno {t.id}: {t.estado} - {fecha_turno} - Puede modificar: {puede_modificar}")
                
            except Exception as e:
                print(f"Error en cálculo de permisos turno {t.id}: {e}")
                puede_modificar = False
                puede_cancelar = False

            # ✅✅✅ CORRECCIÓN DEFINITIVA: Formatear fecha manualmente
            fecha_turno_corregida = t.fecha.strftime("%Y-%m-%d")
            
            # DEBUG: Ver qué fecha tenemos realmente
            print(f"🔍 Turno {t.id}: Fecha en BD: {t.fecha} -> Formateada: {fecha_turno_corregida}")

            data.append({
                'id': t.id,
                # ✅✅✅ FECHA CORREGIDA: Formateada manualmente
                'fecha_turno': fecha_turno_corregida,
                'hora_turno': t.hora.strftime("%H:%M"),
                
                # ✅ FECHA Y HORA REALES DEL REGISTRO (automáticas del sistema)
                'fecha_registro_real': t.fecha_creacion.date().isoformat(),
                'hora_registro_real': t.fecha_creacion.time().strftime("%H:%M:%S"),
                'fecha_hora_completa_registro': t.fecha_creacion.isoformat(),
                
                # ✅ Campos para compatibilidad (mantener por si acaso)
                'fecha': fecha_turno_corregida,  # ✅ Usar la fecha corregida
                'hora': t.hora.strftime("%H:%M"),  # Mantener para compatibilidad
                
                'estado': t.estado,
                'canal': getattr(t, 'canal', 'PRESENCIAL'),
                'tipo_pago': getattr(t, 'tipo_pago', 'PENDIENTE'),
                'monto_seña': float(getattr(t, 'monto_seña', 0)),
                'monto_total': float(getattr(t, 'monto_total', 0)),
                'reembolsado': getattr(t, 'reembolsado', False),
                # Datos del cliente
                'cliente_nombre': t.cliente.nombre,
                'cliente_apellido': t.cliente.apellido,
                'cliente_telefono': t.cliente.telefono or '',
                'cliente_dni': t.cliente.dni,
                # Datos del peluquero
                'peluquero_nombre': t.peluquero.nombre,
                'peluquero_apellido': t.peluquero.apellido,
                # Servicios
                'servicios': servicios_list,
                'duracion_total': duracion_total,
                # Permisos calculados
                'puede_modificar': puede_modificar,
                'puede_cancelar': puede_cancelar,
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Error en listado_turnos: {str(e)}")
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)
    
@csrf_exempt
def crear_turno(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)

        # 🔧 DETECTAR CANAL Y APLICAR LÓGICA CORRESPONDIENTE
        canal = data.get('canal', 'WEB')
        
        if canal == 'PRESENCIAL':
            # 🔧 MODO PRESENCIAL: Sin autenticación, cliente viene en el request
            cliente_id = data.get('cliente_id')
            if not cliente_id:
                return JsonResponse({
                    'status': 'error', 
                    'message': "En modo presencial debe especificar un cliente."
                }, status=400)
            
            try:
                cliente = Usuario.objects.get(pk=cliente_id)
            except Usuario.DoesNotExist:
                return JsonResponse({
                    'status': 'error', 
                    'message': "Cliente no encontrado."
                }, status=400)
                
        else:  # CANAL WEB
            # 🔧 MODO WEB: Requiere autenticación del cliente
            if not request.user.is_authenticated:
                return JsonResponse({
                    'status': 'error', 
                    'message': "Debe iniciar sesión para reservar turnos online."
                }, status=401)
            cliente = request.user

        # 2️⃣ Datos del formulario
        peluquero_id = data.get('peluquero_id')
        servicios_ids = data.get('servicios_ids', [])
        fecha = data.get('fecha')
        hora = data.get('hora')
        tipo_pago_seleccionado = data.get('tipo_pago')  # SENA_50 o TOTAL
        medio_pago = data.get('medio_pago', 'EFECTIVO')

        if tipo_pago_seleccionado not in ['SENA_50', 'TOTAL']:
            return JsonResponse({'status': 'error', 'message': "Debe seleccionar una opción de pago válida (Seña o Total)."}, status=400)

        if not all([peluquero_id, servicios_ids, fecha, hora]):
            return JsonResponse({'status': 'error', 'message': "Faltan datos requeridos (peluquero, servicios, fecha y hora)"}, status=400)

        # 3️⃣ Obtener peluquero y servicios
        try:
            peluquero = Usuario.objects.get(pk=peluquero_id)
            servicios = Servicio.objects.filter(pk__in=servicios_ids)
        except Usuario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': "Peluquero no encontrado"}, status=400)

        if not servicios.exists():
            return JsonResponse({'status': 'error', 'message': "No se encontraron los servicios especificados"}, status=400)

        # 4️⃣ Validar fecha y hora
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora, "%H:%M").time()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': "Formato de fecha u hora inválido"}, status=400)

        if fecha_obj < timezone.now().date():
            return JsonResponse({'status': 'error', 'message': "No se pueden agendar turnos en fechas pasadas"}, status=400)

        # Validación disponibilidad
        if Turno.objects.filter(
            fecha=fecha_obj,
            hora=hora_obj,
            peluquero=peluquero,
            estado__in=['RESERVADO', 'CONFIRMADO']
        ).exists():
            return JsonResponse({'status': 'error', 'message': 'El peluquero no está disponible en la fecha y hora solicitada.'}, status=400)

        # 5️⃣ Calcular montos
        monto_total = sum(float(s.precio) for s in servicios)
        if tipo_pago_seleccionado == 'TOTAL':
            monto_pago_a_enviar_mp = monto_total
            monto_seña_a_guardar = monto_total
        else:
            monto_pago_a_enviar_mp = monto_total * 0.5
            monto_seña_a_guardar = monto_pago_a_enviar_mp

        # 6️⃣ Crear turno
        turno = Turno.objects.create(
            cliente=cliente,
            peluquero=peluquero,
            fecha=fecha_obj,
            hora=hora_obj,
            canal=canal,
            tipo_pago=tipo_pago_seleccionado,
            medio_pago=medio_pago,
            monto_seña=monto_seña_a_guardar,
            monto_total=monto_total,
            estado='RESERVADO'
        )
        turno.servicios.set(servicios)

        print(f"✅ Turno creado: {turno.id} - Fecha: {turno.fecha} - Canal: {canal} - Cliente: {cliente.nombre}")

        # 7️⃣ Si es Mercado Pago, procesar pago
        if medio_pago == 'MERCADO_PAGO':
            mp_service = MercadoPagoService()
            es_pago_total = (tipo_pago_seleccionado == 'TOTAL')

            turno_data = {
                'turno_id': turno.id,
                'monto_pago': float(monto_pago_a_enviar_mp),
                'cliente_nombre': f"{cliente.nombre} {cliente.apellido}",
                'cliente_correo': "test_user_6205179917708892357@testuser.com",
                'peluquero_nombre': f"{peluquero.nombre} {peluquero.apellido}",
                'es_pago_total': es_pago_total
            }

            resultado_mp = mp_service.crear_preferencia_seña(turno_data)

            if resultado_mp['success']:
                init_point = resultado_mp.get('init_point')
                return JsonResponse({
                    'status': 'ok',
                    'turno_id': turno.id,
                    'message': 'Turno pre-reservado. Redirigiendo a pago sandbox',
                    'procesar_pago': True,
                    'mp_data': {
                        'init_point': init_point,
                        'preference_id': resultado_mp['preference_id'],
                    }
                })
            else:
                turno.estado = 'CANCELADO_ERROR_MP'
                turno.save()
                error_msg = resultado_mp.get('error', 'Error desconocido al generar el enlace de pago.')
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error al generar pago con Mercado Pago: {error_msg}. El turno fue cancelado.',
                    'turno_id': turno.id
                }, status=400)
        else:
            return JsonResponse({
                'status': 'ok',
                'turno_id': turno.id,
                'message': 'Turno registrado correctamente',
                'procesar_pago': False
            })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': "Error en el formato JSON"}, status=400)
    except Exception as e:
        print(f"❌ Error interno al crear turno: {e}")
        return JsonResponse({'status': 'error', 'message': f"Error interno del servidor: {str(e)}"}, status=500)
    
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

# En usuarios/views.py - REEMPLAZA la función cancelar_turno existente
@csrf_exempt
def cancelar_turno(request, turno_id):
    """Cancelar turno con verificación de estado"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        turno = Turno.objects.get(id=turno_id)
        
        # Verificar si puede ser cancelado
        puede_cancelar, hay_reembolso, mensaje = turno.puede_ser_cancelado()
        
        if not puede_cancelar:
            return JsonResponse({
                'status': 'error',
                'message': mensaje
            }, status=400)

        # Cambiar estado a cancelado
        turno.estado = 'CANCELADO'
        turno.save()

        return JsonResponse({
            'status': 'ok',
            'message': f'Turno cancelado exitosamente. {mensaje}'
        })

    except Turno.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Turno no encontrado'
        }, status=404)
    except Exception as e:
        print(f"Error cancelando turno: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
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

@csrf_exempt
def registrar_interes_turno(request):
    """
    Registrar cliente interesado en un turno específico
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        
        # Para clientes web autenticados
        if request.user.is_authenticated:
            cliente_id = request.user.id
        else:
            # Para modo presencial o no autenticado
            cliente_id = data.get('cliente_id')
            if not cliente_id:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Se requiere cliente_id para usuarios no autenticados'
                }, status=400)
        
        servicio_id = data.get('servicio_id')
        peluquero_id = data.get('peluquero_id')
        fecha_deseada = data.get('fecha_deseada')
        hora_deseada = data.get('hora_deseada')

        if not all([servicio_id, peluquero_id, fecha_deseada, hora_deseada]):
            return JsonResponse({
                'status': 'error',
                'message': 'Faltan datos requeridos: servicio_id, peluquero_id, fecha_deseada, hora_deseada'
            }, status=400)

        from .turno_service import TurnoService
        success, mensaje = TurnoService.registrar_interes_turno(
            cliente_id, servicio_id, peluquero_id, fecha_deseada, hora_deseada
        )

        if success:
            return JsonResponse({
                'status': 'ok',
                'message': mensaje
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': mensaje
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en registrar_interes_turno: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error interno: {str(e)}'
        }, status=500)

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
                'notificado': interes.notificado,
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

# En usuarios/views.py - Agregar estas funciones

@csrf_exempt
def pago_exitoso(request):
    """Maneja la redirección cuando el pago es exitoso"""
    try:
        payment_id = request.GET.get('payment_id')
        status = request.GET.get('status')
        external_reference = request.GET.get('external_reference')  # turno_id
        preference_id = request.GET.get('preference_id')
        
        print(f"✅ Pago exitoso - Turno: {external_reference}, Payment: {payment_id}, Status: {status}")
        
        if external_reference:
            try:
                # Actualizar el turno a CONFIRMADO
                turno = Turno.objects.get(id=external_reference)
                turno.estado = 'CONFIRMADO'
                turno.save()
                print(f"🔄 Turno {external_reference} actualizado a CONFIRMADO")
            except Turno.DoesNotExist:
                print(f"⚠️ Turno {external_reference} no encontrado")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Pago procesado exitosamente. El turno ha sido confirmado.',
            'turno_id': external_reference,
            'payment_id': payment_id
        })
        
    except Exception as e:
        print(f"❌ Error en pago_exitoso: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Error procesando el pago exitoso'
        }, status=400)

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

#-------Comprobante de pruebaaaaaa

# En views.py - Agrega esta función
@api_view(['GET'])
@permission_classes([AllowAny])
def generar_comprobante_pdf(request, venta_id):
    """Genera y descarga el comprobante PDF de una venta"""
    try:
        # Obtener la venta con todos los detalles
        venta = Venta.objects\
            .select_related('cliente', 'usuario', 'medio_pago')\
            .prefetch_related('detalles__producto')\
            .get(id=venta_id)
        
        # Obtener detalles de la venta
        detalles = venta.detalles.all()
        
        # Preparar datos para el serializer (para obtener nombres)
        from .serializers import VentaSerializer
        venta_data = VentaSerializer(venta).data
        
        # Generar PDF
        from .pdf_utils import generar_comprobante_venta
        pdf_content = generar_comprobante_venta(venta_data, detalles)
        
        if pdf_content:
            # Crear respuesta HTTP con el PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="comprobante_venta_{venta_id}.pdf"'
            return response
        else:
            return HttpResponse("Error generando el comprobante", status=500)
            
    except Venta.DoesNotExist:
        return HttpResponse("Venta no encontrada", status=404)
    except Exception as e:
        print(f"❌ Error: {e}")
        return HttpResponse(f"Error interno: {str(e)}", status=500)
    


def generar_comprobante_pdf(request, venta_id):
    """
    Vista para generar y descargar el comprobante PDF de una venta
    """
    try:
        print(f"🔍 VISTA: Iniciando generación PDF para venta {venta_id}")
        
        # Obtener la venta y sus detalles
        venta = get_object_or_404(Venta, id=venta_id)
        detalles = DetalleVenta.objects.filter(venta=venta)
        
        print(f"✅ VISTA: Venta {venta.id} encontrada, {detalles.count()} detalles")
        
        # Generar el PDF
        pdf_content = generar_comprobante_venta(venta, detalles)
        
        if pdf_content:
            print("✅ VISTA: PDF generado, enviando respuesta")
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="comprobante_venta_{venta_id}.pdf"'
            return response
        else:
            print("❌ VISTA: pdf_content es None")
            return HttpResponse("Error al generar el PDF", status=500)
            
    except Exception as e:
        print(f"❌ VISTA: Error: {str(e)}")
        import traceback
        print(f"❌ VISTA: Traceback: {traceback.format_exc()}")
        return HttpResponse(f"Error: {str(e)}", status=500)

#----para anular una venta
# En usuarios/views.py - Agregar esta función
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
    """Registrar recepción de un pedido"""
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        if not pedido.puede_ser_recibido():
            return Response({
                'error': 'No se puede recibir el pedido. Solo se pueden recibir pedidos en estado PENDIENTE o PARCIAL.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Usar el serializer especializado para recepción
        serializer = PedidoRecepcionSerializer(
            pedido, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'message': 'Pedido recibido exitosamente.',
                'pedido_id': pedido.id,
                'estado': pedido.estado,
                'fecha_recepcion': pedido.fecha_recepcion
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

