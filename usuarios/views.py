from django.db import models, transaction
from django.db.models import Count, Sum, F, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.signals import user_logged_in
from django.utils.html import strip_tags
from rest_framework import viewsets, status, generics , filters, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response 
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Rol, Permiso, Usuario, Servicio, CategoriaProducto, CategoriaServicio, Producto, Turno, Proveedor, Venta, DetalleVenta, MetodoPago, Pedido, DetallePedido, ListaPrecioProveedor, HistorialPrecios, Marca, InteresTurnoLiberado, Cotizacion, SolicitudPresupuesto, PromocionReactivacion, Auditoria, PasswordResetToken
from .mercadopago_service import MercadoPagoService
import json, re, requests, unicodedata
from .serializers import LoginSerializer, ProveedorSerializer, ProductoSerializer, VentaSerializer, DetalleVentaSerializer, CategoriaProductoSerializer, MetodoPagoSerializer, VentaUpdateSerializer, CategoriaServicioSerializer, PedidoSerializer, DetallePedidoSerializer, PedidoRecepcionSerializer, PedidoBusquedaSerializer, ListaPrecioProveedorSerializer, HistorialPreciosSerializer, PrecioSugeridoSerializer, ActualizarListaPreciosSerializer, CotizacionExternaSerializer, SolicitudPresupuestoSerializer, MarcaSerializer, AuditoriaSerializer, SolicitarResetPasswordSerializer, ResetPasswordConfirmarSerializer, ServicioSerializer, RolSerializer, PermisoSerializer, TurnoSerializer
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from .pdf_utils import generar_comprobante_venta
from decimal import Decimal
import secrets, logging
from django.core.mail import send_mail
from django.conf import settings

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

#CREAR CLIENTE DESDE TURNO PRESENCIAL
@api_view(['POST'])
@permission_classes([AllowAny])
def crear_cliente_desde_turno(request):
    """
    Endpoint específico para crear clientes desde el formulario de turnos presenciales.
    Retorna a la pantalla de turnos con el cliente ya seleccionado.
    """
    try:
        print("📋 Creando cliente desde formulario de turnos...")
        data = request.data
        print(f"📦 Datos recibidos: {data}")
        
        # =========================
        # 🔹 CAMPOS OBLIGATORIOS
        # =========================
        required_fields = ['nombre', 'apellido', 'dni', 'correo', 'contrasena']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'status': 'error',
                    'message': f'El campo {field} es obligatorio'
                }, status=status.HTTP_400_BAD_REQUEST)

        # =========================
        # 🔹 VALIDACIONES
        # =========================
        if not re.match(r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}$', data['nombre']):
            return Response({'status': 'error', 'message': 'El nombre solo debe contener letras y espacios (2-50 caracteres)'}, status=400)

        if not re.match(r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}$', data['apellido']):
            return Response({'status': 'error', 'message': 'El apellido solo debe contener letras y espacios (2-50 caracteres)'}, status=400)

        if not re.match(r'^\d{7,9}$', data['dni']):
            return Response({'status': 'error', 'message': 'El DNI debe contener solo números (7-9 dígitos)'}, status=400)

        telefono = data.get('telefono', '')
        if telefono and not re.match(r'^\+?\d{6,15}$', telefono):
            return Response({'status': 'error', 'message': 'El teléfono solo puede contener números y opcional "+" (6-15 dígitos)'}, status=400)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['correo']):
            return Response({'status': 'error', 'message': 'Correo electrónico inválido'}, status=400)

        if len(data['contrasena']) < 6:
            return Response({'status': 'error', 'message': 'La contraseña debe tener al menos 6 caracteres'}, status=400)

        # =========================
        # 🔹 EVITAR DUPLICADOS
        # =========================
        if Usuario.objects.filter(correo=data['correo']).exists():
            return Response({'status': 'error', 'message': 'Ya existe un usuario con ese correo'}, status=400)

        if Usuario.objects.filter(dni=data['dni']).exists():
            return Response({'status': 'error', 'message': 'Ya existe un usuario con ese DNI'}, status=400)

        # =========================
        # 🔹 OBTENER ROL CLIENTE
        # =========================
        try:
            rol_cliente = Rol.objects.get(nombre__iexact='CLIENTE')
        except Rol.DoesNotExist:
            # Si no existe, crear el rol cliente
            rol_cliente = Rol.objects.create(
                nombre='CLIENTE',
                descripcion='Rol para clientes del sistema'
            )

        # =========================
        # 🔹 HASH DE CONTRASEÑA
        # =========================
        hashed_password = make_password(data['contrasena'])

        # =========================
        # 🔹 CREAR CLIENTE
        # =========================
        cliente = Usuario.objects.create(
            nombre=data['nombre'],
            apellido=data['apellido'],
            dni=data['dni'],
            telefono=telefono,
            correo=data['correo'],
            contrasena=hashed_password,
            rol=rol_cliente,
            estado='ACTIVO'
        )

        print(f"✅ Cliente creado exitosamente: ID={cliente.id}, Nombre={cliente.nombre} {cliente.apellido}")

        # =========================
        # 🔹 RETORNAR DATOS PARA REDIRECCIÓN
        # =========================
        return Response({
            'status': 'ok',
            'id': cliente.id,
            'nombre_completo': f"{cliente.nombre} {cliente.apellido}",
            'message': 'Cliente creado exitosamente. Serás redirigido al formulario de turnos.',
            'redirect_url': f'/turnos/presencial/registrar?nuevo_cliente_id={cliente.id}&nuevo_cliente_nombre={cliente.nombre}+{cliente.apellido}'
        })

    except Exception as e:
        print(f"❌ Error al crear cliente desde turno: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Error al crear el cliente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def login_auth(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    correo = validated_data.get('username')
    contrasena = validated_data.get('password')

    user = authenticate(username=correo, password=contrasena)

    if user:
        # ✅ Generar o recuperar token
        token, created = Token.objects.get_or_create(user=user)
                
        return Response({
            'status': 'ok',
            'message': 'Login exitoso',
            'token': token.key,
            'user_id': user.id,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'rol': user.rol.nombre.upper() if user.rol else 'SIN_ROL',
        })
    else:
        return Response({'error': 'Credenciales inválidas'}, status=401)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        print(f"🚪 LOGOUT SOLICITADO POR: {request.user}") # <--- DEBUG

        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()       
        return Response({'message': 'Chau!'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
@api_view(['POST', 'PATCH', 'PUT']) # ✅ Usamos el decorador de DRF para manejar métodos fácil
@permission_classes([IsAuthenticated]) # ✅ Solo gente logueada
def editar_usuario(request, pk):
    try:
        # 1. Seguridad: Obtener usuario y validar permisos
        usuario = Usuario.objects.get(pk=pk)
        
        # Regla: Solo puedes editar tu propio usuario, a menos que seas Admin/Staff
        if request.user.id != usuario.id and not request.user.is_staff:
             # Opcional: Chequear rol específico si is_staff no es suficiente
             es_admin = request.user.rol and request.user.rol.nombre.upper() in ['ADMINISTRADOR', 'ADMIN']
             if not es_admin:
                return JsonResponse({'status': 'error', 'message': 'No tienes permiso para editar este usuario'}, status=403)

        # 2. Parsear datos
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.copy() # Soporte para form-data

        print(f"🔄 Editando Usuario {pk}. Datos:", data)

        # 3. LOGICA CAMBIO DE CONTRASEÑA (Segura)
        contrasena_nueva = data.get('contrasena_nueva')
        contrasena_actual = data.get('contrasena_actual')

        if contrasena_nueva:
            if not contrasena_actual:
                return JsonResponse({'status': 'error', 'message': 'Para cambiar la contraseña, debes ingresar la actual.'}, status=400)
            
            # Verificar que la actual sea correcta
            from django.contrib.auth.hashers import check_password, make_password
            if not check_password(contrasena_actual, usuario.contrasena):
                return JsonResponse({'status': 'error', 'message': 'La contraseña actual es incorrecta.'}, status=400)
            
            # Si pasa, hasheamos la nueva y la guardamos en data para el form/objeto
            usuario.contrasena = make_password(contrasena_nueva)
            # No pasamos la contraseña al form normal para que no la re-hashee mal o la valide como texto plano

        if 'telefono' in data:
            usuario.telefono = data['telefono']
        
        # Si es Admin, puede cambiar más cosas
        if request.user.is_staff or (request.user.rol and request.user.rol.nombre.upper() == 'ADMINISTRADOR'):
            if 'nombre' in data: usuario.nombre = data['nombre']
            if 'apellido' in data: usuario.apellido = data['apellido']
            if 'rol' in data: usuario.rol_id = data['rol']
            if 'estado' in data: usuario.estado = data['estado']

        usuario.save()
        return JsonResponse({'status': 'ok', 'id': usuario.id, 'message': 'Perfil actualizado correctamente'})

    except Usuario.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        print(f"❌ Error editar_usuario: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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
@api_view(['GET'])
@permission_classes([AllowAny])
def listado_servicios(request):
    query = request.GET.get('q', '')
    
    # ✅ CAMBIO CLAVE: Usamos .all() en vez de .filter(activo=True)
    servicios = Servicio.objects.all().order_by('-id') 

    if query:
        servicios = servicios.filter(nombre__icontains=query)

    data = []
    for s in servicios:
        data.append({
            'id': s.id,
            'nombre': s.nombre,
            'precio': s.precio,
            'duracion': s.duracion,
            'categoria': s.categoria.id if s.categoria else None,
            'categoria_nombre': s.categoria.nombre if s.categoria else 'General',
            'descripcion': s.descripcion if hasattr(s, 'descripcion') else '',
            'activo': s.activo  # ✅ IMPORTANTE: Enviamos el estado al frontend
        })
    
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

# 2. CAMBIAR ESTADO (Sirve para Activar y Desactivar)
@api_view(['POST'])
@permission_classes([AllowAny])
def cambiar_estado_servicio(request, pk):
    try:
        servicio = Servicio.objects.get(pk=pk)
        
        # ✅ INTERRUPTOR: Si es True pasa a False, si es False pasa a True
        servicio.activo = not servicio.activo 
        servicio.save()
        
        estado_nuevo = "activado" if servicio.activo else "desactivado"
        return JsonResponse({'status': 'ok', 'message': f'Servicio {estado_nuevo}', 'activo': servicio.activo})
        
    except Servicio.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_servicio(request, pk):
    try:
        s = Servicio.objects.get(pk=pk)
        data = {
            'id': s.id,
            'nombre': s.nombre,
            'precio': s.precio,
            'duracion': s.duracion,
            'categoria': s.categoria.id if s.categoria else None,
            'categoria_nombre': s.categoria.nombre if s.categoria else None,
            # Aseguramos que la descripción viaje
            'descripcion': s.descripcion if hasattr(s, 'descripcion') else ''
        }
        return JsonResponse(data)
    except Servicio.DoesNotExist:
        return JsonResponse({'error': 'Servicio no encontrado'}, status=404)

# ✅ ESTA ES LA DE GUARDAR ACTUALIZADA (POST)
@csrf_exempt
def editar_servicio(request, pk):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    servicio = Servicio.objects.filter(pk=pk).first()
    if not servicio:
        return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)

    try:
        data = json.loads(request.body)
        # Capturamos datos
        nombre = data.get('nombre', '').strip()
        precio = data.get('precio')
        duracion = data.get('duracion')
        categoria_id = data.get('categoria')
        descripcion = data.get('descripcion', '').strip()

        # Validar nombre duplicado (excluyendo el actual)
        if nombre and Servicio.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
            return JsonResponse({'status': 'error', 'message': 'Ya existe un servicio con ese nombre'}, status=400)

        # Actualizamos campos
        if nombre: servicio.nombre = nombre
        if precio is not None: servicio.precio = precio
        if duracion is not None: servicio.duracion = duracion
        
        # Guardamos descripción y categoría
        if hasattr(servicio, 'descripcion'):
            servicio.descripcion = descripcion
            
        servicio.categoria = CategoriaServicio.objects.filter(pk=categoria_id).first() if categoria_id else None
        
        servicio.save()

        return JsonResponse({'status': 'ok', 'id': servicio.id})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
@api_view(['POST']) # O @csrf_exempt si no usas DRF en este
@permission_classes([AllowAny])
def eliminar_servicio(request, pk):
    try:
        servicio = Servicio.objects.get(pk=pk)
        
        # ✅ SOFT DELETE: Lo marcamos como inactivo
        servicio.activo = False 
        servicio.save()
        
        return JsonResponse({'status': 'ok', 'message': 'Servicio desactivado'})
    except Servicio.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)


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

# En usuarios/views.py

class ProductoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Producto.objects.select_related('categoria', 'marca').prefetch_related('proveedores').all()
    serializer_class = ProductoSerializer
    # pagination_class = None  <-- Opcional, si querés que el dropdown traiga todo de una vez

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por nombre
        nombre = self.request.query_params.get('nombre')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

        # Filtro por categoría
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            try:
                queryset = queryset.filter(categoria_id=int(categoria_id))
            except ValueError:
                pass
        
        # 🔥 NUEVO FILTRO: Estado (para el dropdown de precios)
        estado = self.request.query_params.get('estado')
        if estado:
             queryset = queryset.filter(estado__iexact=estado) # 'ACTIVO' o 'activo'

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
# ================================================================
# FUNCIÓN DE LIMPIEZA AUTOMÁTICA 
# ================================================================
def sanear_turnos_vencidos():
    """
    Revisa si hay turnos 'CONFIRMADOS' que ya pasaron y los pasa a 'COMPLETADO'.
    Se ejecuta automáticamente al listar los turnos.
    """
    try:
        ahora = timezone.now()
        
        # 1. Turnos de días ANTERIORES a hoy que quedaron colgados
        # (Si la fecha es menor a hoy y sigue confirmado, ya fue, se completó)
        count_ayer = Turno.objects.filter(
            estado='CONFIRMADO',
            fecha__lt=ahora.date()
        ).update(estado='COMPLETADO')

        # 2. Turnos de HOY que ya terminaron (hace más de 30 min)
        turnos_hoy = Turno.objects.filter(
            estado='CONFIRMADO',
            fecha=ahora.date()
        ).prefetch_related('servicios')

        for t in turnos_hoy:
            # Calcular duración
            duracion = sum(s.duracion for s in t.servicios.all())
            if duracion == 0: duracion = 30 # Default por si acaso
            
            # Hora fin estimada
            inicio_dt = datetime.combine(t.fecha, t.hora)
            inicio_dt = timezone.make_aware(inicio_dt)
            
            # Le damos 30 minutos de tolerancia después de que termina teóricamente
            fin_con_tolerancia = inicio_dt + timedelta(minutes=duracion + 30)

            if ahora > fin_con_tolerancia:
                t.estado = 'COMPLETADO'
                t.save() # Al guardar dispara la creación de venta si tenés esa lógica en el modelo
                
    except Exception as e:
        print(f"⚠️ Error en saneamiento automático: {e}")

@api_view(['POST'])
@permission_classes([AllowAny])
def crear_turno(request):
    print(f"\n🚀 --- INICIO CREAR TURNO ---")
    try:
        data = request.data
        print(f"📦 DATA RECIBIDA: {data}")

        # ---------------------------------------------------------
        # 1. IDENTIFICACIÓN DEL CLIENTE Y CANAL
        # ---------------------------------------------------------
        cliente = None
        canal = data.get('canal', 'WEB') # Default a WEB si no viene nada
        
        # Lógica para Presencial (Admin registra) o Web (Usuario logueado)
        if canal == 'PRESENCIAL':
            cliente_id = data.get('cliente_id') or data.get('cliente')
            if not cliente_id:
                return Response({'status': 'error', 'message': "Falta seleccionar cliente."}, status=400)
            try:
                cliente = Usuario.objects.get(pk=cliente_id)
            except Usuario.DoesNotExist:
                return Response({'status': 'error', 'message': "Cliente no encontrado"}, status=400)
        
        elif request.user.is_authenticated:
            cliente = request.user
        
        # Intento de fallback si viene cliente_id en modo WEB (raro pero posible)
        if not cliente and data.get('cliente_id'):
             cliente = Usuario.objects.filter(pk=data.get('cliente_id')).first()

        if not cliente:
            return Response({'status': 'error', 'message': "Debes iniciar sesión o indicar el cliente."}, status=401)

        print(f"✅ Cliente: {cliente.nombre} {cliente.apellido} ({canal})")

        # ---------------------------------------------------------
        # 2. DATOS BÁSICOS Y VALIDACIONES
        # ---------------------------------------------------------
        peluquero_id = data.get('peluquero_id')
        servicios_ids = data.get('servicios_ids', [])
        fecha_str = data.get('fecha')
        hora_str = data.get('hora')

        if not all([peluquero_id, fecha_str, hora_str, servicios_ids]):
            return Response({'status': 'error', 'message': "Faltan datos obligatorios (peluquero, fecha, hora, servicios)"}, status=400)

        # Normalizar hora (HH:MM)
        if len(hora_str) > 5: hora_str = hora_str[:5]

        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
        except ValueError as e:
            return Response({'status': 'error', 'message': f"Formato de fecha/hora inválido: {e}"}, status=400)

        peluquero = Usuario.objects.get(pk=peluquero_id)
        servicios = Servicio.objects.filter(pk__in=servicios_ids)
        
        if not servicios.exists():
             return Response({'status': 'error', 'message': "Servicios no válidos"}, status=400)

        # ---------------------------------------------------------
        # 3. VALIDACIÓN DE DISPONIBILIDAD (Lógica Robusta)
        # ---------------------------------------------------------
        # A. Calcular duración y rango del NUEVO turno
        duracion_total = sum(s.duracion for s in servicios) or 30
        inicio_nuevo = datetime.combine(fecha_obj, hora_obj)
        fin_nuevo = inicio_nuevo + timedelta(minutes=duracion_total)

        # B. Buscar conflictos
        turnos_existentes = Turno.objects.filter(
            fecha=fecha_obj,
            peluquero=peluquero,
            estado__in=['RESERVADO', 'COMPLETADO'] 
        ).exclude(estado='CANCELADO') # Por seguridad explícita

        for t in turnos_existentes:
            duracion_t = getattr(t, 'duracion_total', 0)

            if not duracion_t and t.servicios.exists():
                 duracion_t = sum(s.duracion for s in t.servicios.all())
            
            # Si aun así es 0, usamos default 30 min
            if not duracion_t: 
                duracion_t = 30
            
            t_inicio = datetime.combine(fecha_obj, t.hora)
            t_fin = t_inicio + timedelta(minutes=duracion_t)

            # Colisión: (InicioNuevo < FinViejo) Y (FinNuevo > InicioViejo)
            if inicio_nuevo < t_fin and fin_nuevo > t_inicio:
                return Response({
                    'status': 'error', 
                    'message': f'Horario ocupado. Se cruza con turno de {t.hora} a {t_fin.time()}.'
                }, status=400)

        # ---------------------------------------------------------
        # 4. LIMPIEZA DE "ZOMBIES" (Ofertas expiradas)
        # ---------------------------------------------------------
        Turno.objects.filter(
            fecha=fecha_obj, hora=hora_obj, peluquero=peluquero, oferta_activa=True
        ).update(estado='CANCELADO', oferta_activa=False)

        # ---------------------------------------------------------
        # 5. CÁLCULO DE MONTOS (Cupones y Señas)
        # ---------------------------------------------------------
        monto_total_original = sum(float(s.precio) for s in servicios)
        monto_final = monto_total_original
        
        # Aplicar Cupón si existe
        cup_codigo = data.get('cup_codigo')
        promo_usada = None
        if cup_codigo:
            try:
                from .models import PromocionReactivacion
                promo = PromocionReactivacion.objects.filter(codigo=cup_codigo).first()
                if promo and promo.esta_vigente:
                    descuento = monto_total_original * (float(promo.descuento_porcentaje) / 100)
                    monto_final -= descuento
                    promo_usada = promo
            except Exception:
                pass # Si falla el cupón, cobramos normal

        # Definir Pago
        tipo_pago = data.get('tipo_pago', 'SENA_50')
        medio_pago = data.get('medio_pago', 'EFECTIVO')
        
        # Regla de Negocio:
        # - Si es TOTAL: Seña = Total
        # - Si es SENA_50: Seña = 50% del Total
        monto_seña = monto_final * 0.5 if tipo_pago == 'SENA_50' else monto_final

        print(f"💰 Finanzas -> Total: ${monto_final} | Seña a pagar: ${monto_seña} ({tipo_pago})")

        # ---------------------------------------------------------
        # 6. CREACIÓN DEL TURNO (ESTADO CORREGIDO)
        # ---------------------------------------------------------
        turno = Turno.objects.create(
            cliente=cliente,
            peluquero=peluquero,
            fecha=fecha_obj,
            hora=hora_obj,
            canal=canal,
            tipo_pago=tipo_pago,
            medio_pago=medio_pago,
            monto_seña=monto_seña,
            monto_total=monto_final,
            duracion_total=duracion_total,
            estado='RESERVADO', # <--- ¡SIEMPRE RESERVADO AL NACER!
            mp_payment_id=data.get('mp_payment_id') # ID si viene de presencial con tarjeta externa o similar
        )
        turno.servicios.set(servicios)

        # Marcar cupón como usado
        if promo_usada:
            promo_usada.estado = 'USADA'
            promo_usada.turno_canje = turno
            promo_usada.save()

        # ---------------------------------------------------------
        # 7. INTEGRACIÓN MERCADO PAGO (Solo WEB)
        # ---------------------------------------------------------
        mp_data = None
        procesar_pago = False

        # Si es WEB y elige MercadoPago, generamos el link AHORA
        if canal == 'WEB' and medio_pago == 'MERCADO_PAGO':
            print("💳 Iniciando Checkout MercadoPago...")
            try:
                from .mercadopago_service import MercadoPagoService
                mp_service = MercadoPagoService()
                
                pref_data = {
                    'turno_id': turno.id,
                    'monto_pago': float(monto_seña),
                    'cliente_nombre': f"{cliente.nombre} {cliente.apellido}",
                    'cliente_correo': cliente.correo or "cliente@hairsoft.com",
                    'peluquero_nombre': peluquero.nombre,
                    'es_pago_total': (tipo_pago == 'TOTAL')
                }
                
                res_mp = mp_service.crear_preferencia_seña(pref_data)
                
                if res_mp.get('success'):
                    procesar_pago = True
                    # Usamos sandbox o init_point según configuración
                    link = res_mp.get('sandbox_init_point') or res_mp.get('init_point')
                    mp_data = {
                        'init_point': link,
                        'preference_id': res_mp.get('preference_id')
                    }
                    print(f"✅ Link MP generado: {link}")
                else:
                    print(f"❌ Error al crear preferencia MP: {res_mp.get('error')}")

            except Exception as e:
                print(f"💥 Error crítico MP: {e}")

        return Response({
            'status': 'ok',
            'turno_id': turno.id,
            'message': 'Turno reservado con éxito.',
            'procesar_pago': procesar_pago,
            'mp_data': mp_data
        }, status=201)

    except Exception as e:
        print(f"💥 ERROR FATAL EN CREAR_TURNO: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'status': 'error', 'message': f"Error interno: {str(e)}"}, status=500)
    
@csrf_exempt
def listado_turnos(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        # 🧹 PASO 0: LIMPIAR LA CASA ANTES DE MOSTRAR
        # Esto elimina los "zombis" automáticamente
        sanear_turnos_vencidos()

        # ===== Parámetros GET =====
        peluquero_id = request.GET.get('peluquero')
        estado = request.GET.get('estado')
        canal = request.GET.get('canal')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        fecha_exacta = request.GET.get('fecha')

        # ===== Query base =====
        turnos = Turno.objects.all().select_related('cliente', 'peluquero').prefetch_related('servicios').order_by('fecha', 'hora')

        # ===== Filtros =====
        if peluquero_id:
            turnos = turnos.filter(peluquero__id=peluquero_id)

        if estado:
            estado_map = {
                'RESERVADO': 'RESERVADO', 'CONFIRMADO': 'CONFIRMADO', 
                'CANCELADO': 'CANCELADO', 'COMPLETADO': 'COMPLETADO',
                'PENDIENTE': 'RESERVADO'
            }
            if ',' in estado:
                estados_lista = [estado_map.get(e.strip().upper(), e.strip().upper()) for e in estado.split(',')]
                turnos = turnos.filter(estado__in=estados_lista)
            else:
                estado_bd = estado_map.get(estado.upper(), estado.upper())
                turnos = turnos.filter(estado=estado_bd)

        if canal:
            turnos = turnos.filter(canal=canal.upper())

        if fecha_exacta:
            try:
                fecha_e = datetime.strptime(fecha_exacta, "%Y-%m-%d").date()
                turnos = turnos.filter(fecha=fecha_e)
            except ValueError: pass

        if fecha_desde:
            try:
                fecha_d = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
                turnos = turnos.filter(fecha__gte=fecha_d)
            except ValueError: pass
            
        if fecha_hasta:
            try:
                fecha_h = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
                turnos = turnos.filter(fecha__lte=fecha_h)
            except ValueError: pass

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

            # Reglas de negocio para modificar
            try:
                fecha_turno_naive = datetime.combine(t.fecha, t.hora)
                fecha_turno = timezone.make_aware(fecha_turno_naive)
                tres_horas_antes = fecha_turno - timedelta(hours=3)
                
                cumple_tiempo = ahora < tres_horas_antes
                puede_modificar = (t.estado in ['RESERVADO', 'CONFIRMADO'] and (cumple_tiempo or es_admin_o_recep))
                puede_cancelar = puede_modificar
                puede_completar = (t.estado == 'CONFIRMADO' and es_admin_o_recep)

            except Exception:
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
                'peluquero_id': t.peluquero.id,
                'cliente_id': t.cliente.id,
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


    
@csrf_exempt
def verificar_disponibilidad(request):
    """
    Verifica disponibilidad REAL considerando la duración de los servicios.
    Evita solapamientos (que se pisen los horarios).
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        peluquero_id = request.GET.get('peluquero_id')
        fecha = request.GET.get('fecha')
        hora = request.GET.get('hora')
        # Recibimos los servicios para saber cuánto va a durar el turno
        servicios_ids = request.GET.getlist('servicios_ids[]') 

        if not all([peluquero_id, fecha, hora]):
            return JsonResponse({'status': 'error', 'message': "Faltan datos"}, status=400)

        # 1. Calcular duración total del turno que quiere sacar el cliente
        duracion_total = 0
        if servicios_ids:
            servicios = Servicio.objects.filter(id__in=servicios_ids)
            duracion_total = sum(s.duracion for s in servicios)
        
        # Si no mandan servicios, asumimos 30 min por defecto para validar el hueco mínimo
        if duracion_total == 0:
            duracion_total = 30

        # 2. Definir Rango del Nuevo Turno (Inicio y Fin Estimado)
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_inicio = datetime.strptime(hora, "%H:%M").time()
        
        inicio_dt = datetime.combine(fecha_obj, hora_inicio)
        fin_dt = inicio_dt + timedelta(minutes=duracion_total)

        # 3. Traer todos los turnos activos de ese peluquero en ese día
        turnos_existentes = Turno.objects.filter(
            fecha=fecha_obj,
            peluquero_id=peluquero_id,
            estado__in=['RESERVADO', 'CONFIRMADO']
        ).prefetch_related('servicios')

        disponible = True
        mensaje = "Disponible"

        for t in turnos_existentes:
            duracion_t = sum(s.duracion for s in t.servicios.all())
            if duracion_t == 0: duracion_t = 15
            
            t_inicio = datetime.combine(fecha_obj, t.hora)
            t_fin = t_inicio + timedelta(minutes=duracion_t)

            if inicio_dt < t_fin and fin_dt > t_inicio:
                disponible = False
                mensaje = f"Horario ocupado. Hay un turno de {t.hora.strftime('%H:%M')} a {t_fin.time().strftime('%H:%M')}"
                break

        return JsonResponse({
            'status': 'ok',
            'disponible': disponible,
            'mensaje': mensaje,
            'duracion_estimada': duracion_total
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_horarios_disponibles(request):
    fecha_str = request.GET.get('fecha')
    peluquero_id = request.GET.get('peluquero_id')
    servicio_id = request.GET.get('servicio_id')

    print(f"📅 Buscando horarios: Fecha={fecha_str}, Peluquero={peluquero_id}")

    if not all([fecha_str, peluquero_id]):
        return Response({'error': 'Falta fecha o peluquero'}, status=400)

    try:
        fecha_solicitada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        ahora = timezone.now()
        
        # 1. BUSCAR TURNOS OCUPADOS (Solo de ese día y peluquero)
        turnos_ocupados = Turno.objects.filter(
            fecha=fecha_solicitada,
            peluquero_id=peluquero_id, 
            estado__in=['RESERVADO', 'CONFIRMADO', 'COMPLETADO']
        )

        # 2. CONFIGURACIÓN DE JORNADA
        hora_inicio = time(9, 0)
        hora_fin = time(21, 0)
        
        # Duración del slot (según servicio o 30 min default)
        duracion_minutos = 30
        if servicio_id:
            try:
                servicio = Servicio.objects.get(pk=servicio_id)
                duracion_minutos = servicio.duracion
            except:
                pass
        
        delta = timedelta(minutes=duracion_minutos)
        horarios_disponibles = []
        
        # Iterador de tiempo
        actual_dt = datetime.combine(fecha_solicitada, hora_inicio)
        fin_dt = datetime.combine(fecha_solicitada, hora_fin)

        # 3. GENERACIÓN DE SLOTS
        while actual_dt + delta <= fin_dt:
            inicio_slot = actual_dt
            fin_slot = actual_dt + delta
            
            es_valido = True

            if fecha_solicitada == ahora.date():
                if inicio_slot.time() < (ahora + timedelta(minutes=15)).time():
                    es_valido = False 

            if es_valido:
                for t in turnos_ocupados:
                    inicio_turno = datetime.combine(t.fecha, t.hora)
                    duracion_turno = sum(s.duracion for s in t.servicios.all()) or 30
                    fin_turno = inicio_turno + timedelta(minutes=duracion_turno)

                    if max(inicio_slot, inicio_turno) < min(fin_slot, fin_turno):
                        es_valido = False
                        break
            
            if es_valido:
                horarios_disponibles.append(actual_dt.strftime("%H:%M"))
            
            actual_dt += delta

        return Response({'horarios': horarios_disponibles})

    except Exception as e:
        print(f"❌ Error buscando horarios: {e}")
        return Response({'error': str(e)}, status=500)
    
@csrf_exempt
def obtener_turno_por_id(request, turno_id):
    """
    Obtiene el detalle de un turno específico por ID
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener el turno con todas las relaciones necesarias
        turno = Turno.objects\
            .select_related('cliente', 'peluquero')\
            .prefetch_related('servicios')\
            .get(id=turno_id)
        
        # Calcular duración total
        duracion_total = sum(servicio.duracion for servicio in turno.servicios.all())
        
        # Serializar servicios
        servicios_list = []
        for servicio in turno.servicios.all():
            servicios_list.append({
                'id': servicio.id,
                'nombre': servicio.nombre,
                'precio': float(servicio.precio),
                'duracion': servicio.duracion,
                'categoria_id': servicio.categoria.id if servicio.categoria else None,
                'categoria': servicio.categoria.nombre if servicio.categoria else None
            })
        
        # Datos del turno en formato JSON
        turno_data = {
            'id': turno.id,
            'cliente_id': turno.cliente.id,
            'cliente_nombre': turno.cliente.nombre,
            'cliente_apellido': turno.cliente.apellido,
            'cliente_dni': turno.cliente.dni,
            'peluquero_id': turno.peluquero.id,
            'peluquero_nombre': turno.peluquero.nombre,
            'peluquero_apellido': turno.peluquero.apellido,
            'fecha': turno.fecha.strftime("%Y-%m-%d"),
            'fecha_turno': turno.fecha.strftime("%Y-%m-%d"),
            'hora': turno.hora.strftime("%H:%M"),
            'hora_turno': turno.hora.strftime("%H:%M"),
            'estado': turno.estado,
            'canal': turno.canal,
            'tipo_pago': turno.tipo_pago,
            'medio_pago': turno.medio_pago or "EFECTIVO",
            'monto_seña': float(turno.monto_seña) if turno.monto_seña else 0,
            'monto_total': float(turno.monto_total) if turno.monto_total else 0,
            'servicios': servicios_list,
            'duracion_total': duracion_total,
            'oferta_activa': getattr(turno, 'oferta_activa', False),
            'fecha_expiracion_oferta': turno.fecha_expiracion_oferta.isoformat() if getattr(turno, 'fecha_expiracion_oferta', None) else None
        }
        
        return JsonResponse(turno_data)
        
    except Turno.DoesNotExist:
        return JsonResponse({'error': 'Turno no encontrado'}, status=404)
    except Exception as e:
        print(f"Error al obtener turno {turno_id}: {str(e)}")
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)

@csrf_exempt
@api_view(['POST']) # Agregado para que DRF maneje el request si entra por /api/
@permission_classes([AllowAny])
def cambiar_estado_turno(request, turno_id, nuevo_estado):
    """
    Vista para cambiar el estado de un turno desde el frontend.
    Permite transiciones desde RESERVADO o CONFIRMADO hacia COMPLETADO o CANCELADO.
    """
    try:
        # Obtener el turno
        turno = get_object_or_404(Turno, id=turno_id)
        
        print(f"🔄 Cambio estado Turno #{turno.id}: {turno.estado} -> {nuevo_estado}")

        # Estados válidos
        estados_validos = ['RESERVADO', 'CONFIRMADO', 'COMPLETADO', 'CANCELADO']
        
        if nuevo_estado not in estados_validos:
            return JsonResponse({'status': 'error', 'message': f'Estado destino "{nuevo_estado}" no válido'}, status=400)
        
        estado_anterior = turno.estado
        if estado_anterior == 'COMPLETADO':
            return JsonResponse({'status': 'error', 'message': 'El turno ya está COMPLETADO. No se puede modificar.'}, status=400)
        
        if estado_anterior == 'CANCELADO':
            return JsonResponse({'status': 'error', 'message': 'El turno ya está CANCELADO. No se puede revivir.'}, status=400)
        
        if nuevo_estado == 'COMPLETADO':
            # Solo permitimos completar si estaba activo
            if estado_anterior not in ['RESERVADO', 'CONFIRMADO']:
                 return JsonResponse({'status': 'error', 'message': 'Solo turnos reservados o confirmados pueden completarse.'}, status=400)

            # Si era SEÑA, al completar se asume que paga el resto -> Pasa a TOTAL
            if turno.tipo_pago == 'SENA_50':
                turno.tipo_pago = 'TOTAL'

            if turno.monto_total == 0:
                turno.monto_total = sum(s.precio for s in turno.servicios.all()) or 0
            
            if turno.monto_seña == 0 and turno.tipo_pago == 'TOTAL':
                turno.monto_seña = turno.monto_total

        turno.estado = nuevo_estado
        turno.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': f'Estado actualizado correctamente a {nuevo_estado}',
            'turno_id': turno.id
        })
        
    except Exception as e:
        print(f"💥 Error crítico cambiando estado: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt
def completar_turno(request, turno_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        turno = Turno.objects.get(pk=turno_id)        
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
def actualizar_pago_turno(request, turno_id):
    """
    Actualiza el tipo de pago y monto total de un turno
    """
    try:
        turno = get_object_or_404(Turno, id=turno_id)
        data = json.loads(request.body)
        
        tipo_pago = data.get('tipo_pago')
        monto_total = Decimal(data.get('monto_total', 0))
        
        if tipo_pago not in ['SENA_50', 'TOTAL']:
            return JsonResponse({
                'status': 'error',
                'message': 'Tipo de pago no válido'
            }, status=400)
        
        # Actualizar datos
        turno.tipo_pago = tipo_pago
        turno.monto_total = monto_total
        
        # Si es pago total, la seña es igual al total
        if tipo_pago == 'TOTAL':
            turno.monto_seña = monto_total
        
        turno.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': f'Pago actualizado a {tipo_pago} - Total: ${monto_total}',
            'turno_id': turno.id
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

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
    print("\n🔥 DEBUG: Registrando interés MULTI-SERVICIO")
    try:
        data = request.data
        cliente_id = data.get('cliente_id')
        peluquero_id = data.get('peluquero_id')
        servicios_ids = data.get('servicios_ids') # Esperamos lista: [1, 2, 3]
        
        # Manejo flexible de fecha/hora
        fecha_str = data.get('fecha') or data.get('fecha_deseada')
        hora_str = data.get('hora') or data.get('hora_deseada')

        if not all([cliente_id, peluquero_id, servicios_ids, fecha_str, hora_str]):
            return Response({'error': 'Faltan datos'}, status=400)

        # Parseo
        cliente = Usuario.objects.get(pk=cliente_id)
        peluquero = Usuario.objects.get(pk=peluquero_id)
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(str(hora_str)[:5], "%H:%M").time()

        # Si viene un solo ID, lo hacemos lista
        if not isinstance(servicios_ids, list):
            servicios_ids = [servicios_ids]

        created_count = 0
        
        # 🔄 LOOP: Guardamos un registro de interés POR CADA servicio seleccionado
        # Esto permite recuperarlos todos después al aceptar la oferta
        for serv_id in servicios_ids:
            servicio = Servicio.objects.get(pk=serv_id)
            _, created = InteresTurnoLiberado.objects.get_or_create(
                cliente=cliente,
                peluquero=peluquero,
                fecha_deseada=fecha_obj,
                hora_deseada=hora_obj,
                servicio=servicio, # Guardamos CADA servicio
                defaults={'estado_oferta': 'pendiente'}
            )
            if created: created_count += 1

        print(f"✅ Interés guardado para {len(servicios_ids)} servicios.")
        return Response({'success': True, 'message': 'Te avisaremos si se libera.'})

    except Exception as e:
        print(f"❌ Error registrar_interes: {e}")
        return Response({'error': str(e)}, status=500)
    
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
def registrar_pago_turno(request, turno_id):
    """Registra un pago (seña o total) y actualiza estado"""
    try:
        turno = get_object_or_404(Turno, id=turno_id)
        data = json.loads(request.body)
        
        tipo_pago = data.get('tipo_pago')
        monto = Decimal(data.get('monto', 0))
        
        if tipo_pago not in ['SENA_50', 'TOTAL']:
            return JsonResponse({
                'status': 'error',
                'message': 'Tipo de pago no válido'
            }, status=400)
        
        # Actualizar datos de pago
        turno.tipo_pago = tipo_pago
        turno.monto_seña = monto
        
        # Si es pago total, el monto seña es igual al total
        if tipo_pago == 'TOTAL':
            turno.monto_total = monto
        
        # Cambiar estado a CONFIRMADO automáticamente
        turno.estado = 'CONFIRMADO'
        turno.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': f'Pago registrado: {tipo_pago} - ${monto}',
            'turno_id': turno.id,
            'estado': turno.estado
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
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
    
# Asegurate de que estos imports estén arriba en tu archivo
from datetime import datetime, timedelta
from django.utils import timezone

@csrf_exempt
def turnos_ocupados(request):
    fecha = request.GET.get("fecha")
    peluquero_id = request.GET.get("peluquero_id") or request.GET.get("peluquero")

    if not fecha or not peluquero_id:
        return JsonResponse({"error": "Faltan parámetros"}, status=400)

    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Formato de fecha inválido"}, status=400)

    # Traemos turnos que realmente ocupan un slot
    turnos = Turno.objects.filter(
        fecha=fecha_obj,
        peluquero_id=peluquero_id,
        estado__in=['RESERVADO', 'CONFIRMADO', 'COMPLETADO']
    ).prefetch_related('servicios')

    rangos_ocupados = []

    for t in turnos:
        # Calcular duración
        duracion = sum(s.duracion for s in t.servicios.all())
        if duracion == 0: duracion = 30

        # Calcular Inicio y Fin
        inicio = datetime.combine(fecha_obj, t.hora)
        fin = inicio + timedelta(minutes=duracion)

        rangos_ocupados.append({
            "inicio": inicio.strftime("%H:%M"),
            "fin": fin.strftime("%H:%M"),
            "estado": t.estado,
            "id": t.id
        })

    return JsonResponse({
        "fecha": fecha,
        "peluquero": peluquero_id,
        "ocupados": rangos_ocupados 
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
    pagination_class = None



# ================================
# Categorías CRUD
# ================================
# --- FUNCIÓN AUXILIAR PARA COMPARAR SIN ACENTOS ---
def normalizar_texto(texto):
    """Elimina acentos y pasa a minúsculas para comparar (ej: 'Coloración' -> 'coloracion')"""
    if not texto:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) 
                  if unicodedata.category(c) != 'Mn').lower().strip()

@csrf_exempt
def crear_categoria_servicio(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not nombre:
            return JsonResponse({'status': 'error', 'message': 'El nombre es obligatorio'}, status=400)
            
        # 🔥 VALIDACIÓN INSENSIBLE A ACENTOS
        nombre_norm = normalizar_texto(nombre)
        # Traemos todos los nombres y chequeamos en Python
        categorias = CategoriaServicio.objects.all()
        for cat in categorias:
            if normalizar_texto(cat.nombre) == nombre_norm:
                return JsonResponse({'status': 'error', 'message': f'Ya existe la categoría "{cat.nombre}"'}, status=400)
            
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
            # 🔥 VALIDACIÓN INSENSIBLE A ACENTOS (Excluyendo la propia)
            nombre_norm = normalizar_texto(nombre)
            categorias = CategoriaServicio.objects.exclude(pk=pk)
            for c in categorias:
                if normalizar_texto(c.nombre) == nombre_norm:
                    return JsonResponse({'status': 'error', 'message': f'Ya existe otra categoría llamada "{c.nombre}"'}, status=400)
            cat.nombre = nombre
            
        if descripcion is not None:
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
            return JsonResponse({'status': 'error', 'message': 'El nombre es obligatorio'}, status=400)
            
        # 🔥 VALIDACIÓN INSENSIBLE A ACENTOS
        nombre_norm = normalizar_texto(nombre)
        categorias = CategoriaProducto.objects.all()
        for cat in categorias:
            if normalizar_texto(cat.nombre) == nombre_norm:
                return JsonResponse({'status': 'error', 'message': f'Ya existe la categoría "{cat.nombre}" (los acentos no cuentan)'}, status=400)
            
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
            # 🔥 VALIDACIÓN INSENSIBLE A ACENTOS
            nombre_norm = normalizar_texto(nombre)
            categorias = CategoriaProducto.objects.exclude(pk=pk)
            for c in categorias:
                if normalizar_texto(c.nombre) == nombre_norm:
                    return JsonResponse({'status': 'error', 'message': f'Ya existe otra categoría llamada "{c.nombre}"'}, status=400)
            cat.nombre = nombre
            
        if descripcion is not None:
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
# GESTIÓN DE ROLES (DRF)
# ================================

@api_view(['GET'])
@permission_classes([AllowAny])
def listado_roles(request):
    roles = Rol.objects.all().order_by('nombre')
    serializer = RolSerializer(roles, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def crear_rol(request):
    # Usamos el Serializer para validar y guardar
    serializer = RolSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'ok', 'message': 'Rol creado'}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([AllowAny])
def editar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)

    # 1. GET: Cargar datos
    if request.method == 'GET':
        ids_permisos = list(rol.permisos.values_list('id', flat=True))
        return Response({
            'id': rol.id,
            'nombre': rol.nombre,
            'descripcion': rol.descripcion or '',
            'activo': rol.activo, # Aseguramos que mande el estado actual
            'permisos': ids_permisos
        })

    # 2. PUT/PATCH: Guardar cambios
    try:
        data = request.data
        
        if 'nombre' in data:
            rol.nombre = data['nombre'].strip()
        if 'descripcion' in data:
            rol.descripcion = data['descripcion'].strip()
            
        # 👇👇👇 ESTO ES LO QUE FALTABA 👇👇👇
        if 'activo' in data:
            rol.activo = data['activo']
        # 👆👆👆 SIN ESTO, EL BOTÓN NO HACE NADA 👆👆👆

        # Actualizar Permisos
        if 'permisos_ids' in data:
             ids = data['permisos_ids']
             if isinstance(ids, list):
                permisos = Permiso.objects.filter(id__in=ids)
                rol.permisos.set(permisos)
        elif 'permisos' in data:
            ids = data['permisos']
            if isinstance(ids, list):
                permisos = Permiso.objects.filter(id__in=ids)
                rol.permisos.set(permisos)
            
        rol.save()
        return Response({'status': 'ok', 'message': 'Rol actualizado'})
        
    except Exception as e:
        return Response({'message': str(e)}, status=500)
    
@api_view(['POST']) # Usamos POST para acciones destructivas si preferís
@permission_classes([AllowAny])
def eliminar_rol(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    rol.delete()
    return Response({'status': 'ok', 'message': 'Rol eliminado'})

# ================================
# LISTADO DE PERMISOS (Con Grupo Inventado)
# ================================
# En usuarios/views.py

@api_view(['GET'])
@permission_classes([AllowAny])
def listado_permisos(request):
    permisos = Permiso.objects.filter(activo=True).order_by('codigo')
    data = []
    
    for p in permisos:
        # Recuperamos el grupo desde la descripción o inventamos uno 'General'
        grupo_nombre = p.descripcion if p.descripcion else 'General'
        
        data.append({
            'id': p.id,
            'nombre': p.nombre,
            'codigo': p.codigo,
            'grupo': grupo_nombre, # ✅ ESTO ES LO QUE NECESITA EL FRONTEND
            'descripcion': p.descripcion or ''
        })
        
    return Response(data)

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

def procesar_reembolso_si_corresponde(turno):
    """
    Evalúa si corresponde reembolso (regla de 3 horas) y ejecuta la devolución en MP.
    Retorna: (bool: se_hizo_reembolso, str: mensaje)
    """
    try:
        # 1. Armar fecha/hora completa del turno (consciente de zona horaria)
        # Asumiendo que turno.fecha es date y turno.hora es time
        fecha_hora_turno_naive = datetime.combine(turno.fecha, turno.hora)
        fecha_hora_turno = timezone.make_aware(fecha_hora_turno_naive)
        ahora = timezone.now()

        # 2. Calcular diferencia
        tiempo_restante = fecha_hora_turno - ahora
        horas_restantes = tiempo_restante.total_seconds() / 3600

        # 3. Validar Regla de 3 Horas
        if horas_restantes < 3:
            return False, "⏳ Menos de 3hs para el turno. Se aplica penalidad (Sin reembolso)."

        # 4. Validar si hay dinero que devolver
        if not turno.mp_payment_id or turno.monto_seña <= 0:
            if turno.canal == 'PRESENCIAL':
                return False, "🏪 Turno presencial. Devolución manual requerida en caja."
            return False, "⚠️ No hay pago registrado en MP para reembolsar."

        # 5. Ejecutar Reembolso en MercadoPago
        mp_service = MercadoPagoService()
        # Usamos tu función existente que devuelve un dict con 'success'
        resultado_mp_dict = mp_service.devolver_pago(turno.mp_payment_id) 
        resultado_mp = resultado_mp_dict.get('success', False) # Extraemos el booleano

        if resultado_mp: # Asumiendo que devuelve True/False o un objeto truthy
            turno.reembolsado = True
            turno.save()
            return True, f"💰 Reembolso de ${turno.monto_seña} procesado exitosamente por MercadoPago."
        else:
            return False, "❌ Error al conectar con MercadoPago para el reembolso."

    except Exception as e:
        print(f"Error calculando reembolso: {e}")
        return False, f"Error interno procesando reembolso: {str(e)}"

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



# En usuarios/views.py

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_usuario_por_id(request, user_id):
    """Obtiene un usuario específico por ID (Manual y Seguro)"""
    try:
        user = Usuario.objects.get(id=user_id)
        
        # Devolvemos el diccionario a mano para evitar errores de Serializer
        return Response({
            'id': user.id,
            'nombre': user.nombre,
            'apellido': user.apellido,
            'correo': user.correo,
            'dni': user.dni if user.dni else 'No registrado',           # <--- CLAVE
            'telefono': user.telefono if user.telefono else 'No registrado', # <--- CLAVE
            'rol': user.rol.nombre if user.rol else 'Sin rol'
        })
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return Response({'error': str(e)}, status=500)
    
# =================================
# VENTAS
# =================================

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
        
        # 2. SERIALIZAR LA VENTA (Convertir Objeto -> Diccionario)
        # Importamos aquí para evitar ciclos si es necesario, o por orden
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
            return HttpResponse("Error al generar el PDF (contenido vacío)", status=500)
            
    except Exception as e:
        print(f"❌ VISTA: Error: {str(e)}")
        import traceback
        print(f"❌ VISTA: Traceback: {traceback.format_exc()}")
        return HttpResponse(f"Error generando comprobante: {str(e)}", status=500)

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
    """
    Listar y crear pedidos.
    AL CREAR: Envía un correo HTML con diseño Premium al proveedor.
    """
    queryset = Pedido.objects.all()\
        .select_related('proveedor', 'usuario_creador')\
        .prefetch_related('detalles__producto')\
        .order_by('-fecha_pedido')
    serializer_class = PedidoSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        try:
            # 1. Guardar el pedido
            usuario = self.request.user if self.request.user.is_authenticated else None
            pedido = serializer.save(usuario_creador=usuario)

            # 2. 📧 PREPARACIÓN DEL CORREO
            proveedor = pedido.proveedor
            
            if proveedor.email:
                print(f"🎨 Generando correo con diseño premium para: {proveedor.email}")
                
                # Link al portal
                link = f"http://localhost:5173/externo/pedido/{pedido.token}"
                
                asunto = f"📦 Solicitud de Pedido #{pedido.id} | HairSoft"
                
                fecha_formato = timezone.localtime(pedido.fecha_pedido).strftime("%d/%m/%Y a las %H:%M")
                
                # --- DISEÑO HTML "CHETO" ---
                mensaje_html = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Nuevo Pedido</title>
                </head>
                <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                    
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f3f4f6; padding: 40px 0;">
                        <tr>
                            <td align="center">
                                
                                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1);">
                                    
                                    <tr>
                                        <td style="background-color: #1e293b; padding: 30px 40px; text-align: center;">
                                            <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 1px;">HairSoft</h1>
                                            <p style="color: #94a3b8; margin: 8px 0 0; font-size: 14px; text-transform: uppercase; letter-spacing: 2px;">Gestión de Compras</p>
                                        </td>
                                    </tr>

                                    <tr>
                                        <td style="padding: 40px;">
                                            <h2 style="color: #111827; margin-top: 0; font-size: 22px;">¡Hola, {proveedor.nombre}! 👋</h2>
                                            
                                            <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
                                                Hemos generado una nueva orden de compra y necesitamos tu confirmación de <strong>stock y precios</strong> para proceder.
                                            </p>

                                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 30px;">
                                                <tr>
                                                    <td style="padding: 20px;">
                                                        <p style="margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; font-weight: bold;">Referencia del Pedido</p>
                                                        <p style="margin: 5px 0 0; color: #0f172a; font-size: 20px; font-weight: 700;">#{pedido.id}</p>
                                                        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">
                                                        <p style="margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; font-weight: bold;">Fecha de Emisión</p>
                                                        <p style="margin: 5px 0 0; color: #334155; font-size: 16px;">{fecha_formato}</p>
                                                    </td>
                                                </tr>
                                            </table>

                                            <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin-bottom: 30px; text-align: center;">
                                                Hacé clic en el botón de abajo para ver el detalle de los productos y confirmar la disponibilidad:
                                            </p>

                                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                                <tr>
                                                    <td align="center">
                                                        <a href="{link}" target="_blank" style="background-color: #4f46e5; color: #ffffff; padding: 16px 32px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);">
                                                            🚀 Revisar y Confirmar Pedido
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>

                                            <p style="margin-top: 30px; font-size: 13px; color: #9ca3af; text-align: center;">
                                                Si el botón no funciona, copiá este enlace: <br>
                                                <a href="{link}" style="color: #4f46e5;">{link}</a>
                                            </p>
                                        </td>
                                    </tr>

                                    <tr>
                                        <td style="background-color: #f1f5f9; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                                            <p style="margin: 0; font-size: 12px; color: #64748b;">
                                                © 2025 HairSoft - Sistema de Gestión.<br>
                                                Este correo fue enviado automáticamente.
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin-top: 20px; font-size: 12px; color: #9ca3af;">Enviado a través de HairSoft Platform</p>

                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """

                # Texto plano (Fallback)
                mensaje_plano = f"Hola {proveedor.nombre}, tenés un nuevo pedido #{pedido.id}. Ingresá aquí: {link}"

                # Enviar
                send_mail(
                    subject=asunto,
                    message=mensaje_plano,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[proveedor.email],
                    html_message=mensaje_html,
                    fail_silently=False,
                )
                
                # 3. Actualizar Estado
                pedido.estado = 'ENVIADO'
                pedido.save()
                print("✅ Correo PREMIUM enviado correctamente.")

            else:
                print("⚠️ Proveedor sin email. Pedido guardado como PENDIENTE.")

        except Exception as e:
            print(f"❌ Error en el proceso de creación/envío: {e}")
            # No hacemos raise para no bloquear la creación del pedido si falla el mail

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
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        if pedido.estado != 'CONFIRMADO':
            return Response({'error': 'El pedido debe estar CONFIRMADO para recibirse.'}, status=400)

        with transaction.atomic():
            for detalle in pedido.detalles.all():
                producto = detalle.producto
                if producto:
                    # 1. Sumar Stock
                    producto.stock_actual += detalle.cantidad
                    
                    # 2. LÓGICA DE PRECIO (EL FRENO DE MANO) 🛑
                    costo_nuevo = detalle.precio_unitario
                    
                    if costo_nuevo and costo_nuevo > 0:
                        try:
                            # Buscamos tu margen configurado (ej: 30%)
                            lista = ListaPrecioProveedor.objects.get(proveedor=pedido.proveedor, producto=producto)
                            margen = lista.margen_ganancia
                            
                            # Calculamos el precio nuevo teórico
                            precio_nuevo_calculado = costo_nuevo * (1 + (margen / 100))
                            
                            # PRECIO ACTUAL (El que tenés ahora, ej: 30.000)
                            precio_actual = producto.precio if producto.precio else 0
                            
                            # LA REGLA DE ORO: Solo actualizamos si SUBE.
                            if precio_nuevo_calculado > precio_actual:
                                producto.precio = precio_nuevo_calculado
                                print(f"📈 SUBIÓ: {producto.nombre} pasa de ${precio_actual} a ${precio_nuevo_calculado}")
                            else:
                                # Si baja (26.000 < 30.000), NO HACEMOS NADA.
                                print(f"🛡️ PROTEGIDO: El precio nuevo daba ${precio_nuevo_calculado}, pero nos quedamos con ${precio_actual}")
                                
                            # Actualizamos el costo base en la lista del proveedor para referencia futura
                            lista.precio_base = costo_nuevo
                            lista.save()

                        except ListaPrecioProveedor.DoesNotExist:
                            pass

                    producto.save()
            
            pedido.estado = 'ENTREGADO'
            pedido.fecha_recepcion = timezone.now()
            pedido.save()

        return Response({'message': 'Pedido recibido. Stock actualizado. Precios protegidos contra bajas.'})

    except Exception as e:
        return Response({'error': str(e)}, status=400)
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

@api_view(['POST'])
@permission_classes([AllowAny]) # Ajustá según necesites
def enviar_pedido_proveedor(request, pedido_id):
    """
    Envía un correo al proveedor con el link único para gestionar el pedido.
    Usa la configuración SMTP que ya tenés en settings.py.
    """
    try:
        pedido = get_object_or_404(Pedido, id=pedido_id)
        proveedor = pedido.proveedor
        
        if not proveedor.email:
            return Response({'error': 'El proveedor no tiene email cargado'}, status=400)

        # Generamos el link (Asumiendo que tu Vue corre en puerto 5173)
        # Ajustá la URL base si en producción es distinta
        link = f"http://localhost:5173/externo/pedido/{pedido.token}"
        
        asunto = f"Nuevo Pedido de HairSoft #{pedido.id}"
        mensaje = f"""
        Hola {proveedor.nombre},
        
        Te enviamos un nuevo pedido de mercadería.
        Por favor, ingresá al siguiente link para confirmar stock y precios:
        
        {link}
        
        Gracias,
        El equipo de HairSoft.
        """
        
        # Enviar mail usando TU configuración actual
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER, # Usa tu usuario de Mailtrap actual
            [proveedor.email],
            fail_silently=False,
        )
        
        # Actualizamos estado
        pedido.estado = 'ENVIADO'
        pedido.save()
        
        return Response({'message': f'Correo enviado a {proveedor.email}'})

    except Exception as e:
        return Response({'error': str(e)}, status=500)

# ==============================================================================
# GESTIÓN EXTERNA DE PEDIDOS (PARA EL PROVEEDOR) - SIN LOGIN REQUERIDO
# ==============================================================================

@api_view(['GET'])
@permission_classes([AllowAny]) # Pública para que entre con el token
def obtener_pedido_externo(request, token):
    """
    Permite al proveedor ver el pedido usando solo el token del link.
    """
    try:
        # Buscamos por el token UUID
        pedido = get_object_or_404(Pedido, token=token)
        
        # Reutilizamos tu serializer existente, funciona perfecto
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': 'Pedido no encontrado o enlace inválido'}, status=404)

@api_view(['POST'])
@permission_classes([AllowAny]) # Pública
def confirmar_pedido_externo(request, token):
    """
    El proveedor confirma cantidades y precios.
    """
    try:
        pedido = get_object_or_404(Pedido, token=token)
        
        # Validamos que no se pueda responder dos veces
        if pedido.estado not in ['ENVIADO', 'PENDIENTE']: # PENDIENTE por si lo mandaste manual
            return Response({'error': 'Este pedido ya fue respondido o no está disponible.'}, status=400)

        # Recibimos la lista de detalles editada por el proveedor
        datos_recibidos = request.data.get('detalles', [])
        
        with transaction.atomic():
            cambios_realizados = False
            
            for item in datos_recibidos:
                detalle_id = item.get('id')
                nueva_cantidad = item.get('cantidad')
                nuevo_precio = item.get('precio_unitario')
                
                # Buscamos el detalle específico dentro de este pedido
                detalle = pedido.detalles.filter(id=detalle_id).first()
                
                if detalle:
                    if nueva_cantidad is not None:
                        detalle.cantidad = nueva_cantidad
                        cambios_realizados = True
                    if nuevo_precio is not None:
                        detalle.precio_unitario = nuevo_precio
                        cambios_realizados = True
                    
                    # Recalculamos el subtotal de esa línea
                    if detalle.precio_unitario and detalle.cantidad:
                        detalle.subtotal = detalle.cantidad * detalle.precio_unitario
                    
                    detalle.save()
            
            # Actualizamos totales y estado del pedido padre
            pedido.total = pedido.calcular_total()
            pedido.estado = 'CONFIRMADO' # Queda listo para recibir
            pedido.save()

        return Response({
            'message': '¡Gracias! El pedido fue confirmado exitosamente.',
            'nuevo_estado': pedido.estado
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)

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

# DASHBOARD
@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_data(request):
    try:
        # 1. RANGO DE FECHAS
        period = request.GET.get('period', 'semana')
        date_from_str = request.GET.get('date_from')
        date_to_str = request.GET.get('date_to')
        
        hoy = timezone.localtime(timezone.now()) # Usar hora local del servidor
        
        # A) Rango Personalizado (Si vienen fechas explícitas)
        if date_from_str and date_to_str:
            try:
                # Convertimos string YYYY-MM-DD a datetime con zona horaria
                start_date = datetime.strptime(date_from_str, '%Y-%m-%d')
                start_date = timezone.make_aware(start_date).replace(hour=0, minute=0, second=0)
                
                end_date = datetime.strptime(date_to_str, '%Y-%m-%d')
                end_date = timezone.make_aware(end_date).replace(hour=23, minute=59, second=59)
            except ValueError:
                # Si fallan las fechas, fallback a semana
                start_date = hoy - timedelta(days=6)
                start_date = start_date.replace(hour=0, minute=0, second=0)
                end_date = hoy.replace(hour=23, minute=59, second=59)

        # B) Rango Predefinido: HOY
        elif period == 'hoy':
            start_date = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = hoy.replace(hour=23, minute=59, second=59)
        
        # C) Rango Predefinido: MES ACTUAL
        elif period == 'mes':
            start_date = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = hoy.replace(hour=23, minute=59, second=59)
        
        # D) Default: SEMANA (Últimos 7 días)
        else: 
            start_date = hoy - timedelta(days=6)
            start_date = start_date.replace(hour=0, minute=0, second=0)
            end_date = hoy.replace(hour=23, minute=59, second=59)

        # 2. CONSULTAS BASE (Tus filtros originales)
        ventas_periodo = Venta.objects.filter(fecha__range=[start_date, end_date], anulada=False)
        
        # OJO: Aquí sumamos los turnos. Si quieres sumar TODOS los turnos (agendados + completados)
        # quita el filtro estado='COMPLETADO'. Si es solo facturación, déjalo así.
        turnos_periodo = Turno.objects.filter(fecha__range=[start_date, end_date], estado='COMPLETADO')
        
        # 3. KPIs
        ingresos_totales = ventas_periodo.aggregate(total=Sum('total'))['total'] or 0
        servicios_realizados = turnos_periodo.count()
        
        # Productos vendidos
        productos_vendidos = DetalleVenta.objects.filter(
            venta__in=ventas_periodo,
            producto__isnull=False
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        # 4. GRÁFICO (Evolución diaria)
        labels_dias = []
        ventas_por_dia = []
        
        # Calculamos la diferencia en días para iterar
        delta_days = (end_date.date() - start_date.date()).days
        if delta_days < 0: delta_days = 0 # Protección por si acaso
        
        for i in range(delta_days + 1):
            dia_actual = start_date + timedelta(days=i)
            
            # Filtramos ventas de ese día específico
            total_dia = Venta.objects.filter(
                fecha__date=dia_actual.date(), 
                anulada=False
            ).aggregate(total=Sum('total'))['total'] or 0
            
            # Formato de etiqueta
            nombre_dia = dia_actual.strftime('%a')
            num_dia = dia_actual.day
            traduccion = {'Mon':'Lun', 'Tue':'Mar', 'Wed':'Mié', 'Thu':'Jue', 'Fri':'Vie', 'Sat':'Sáb', 'Sun':'Dom'}
            # Traducimos el nombre del día (ej. Mon -> Lun)
            nombre_traducido = next((v for k,v in traduccion.items() if k in nombre_dia), nombre_dia)
            
            label = f"{nombre_traducido} {num_dia}"
            
            labels_dias.append(label)
            ventas_por_dia.append(float(total_dia))

        # 5. TOP SERVICIOS
        top_servicios_query = turnos_periodo.values('servicios__nombre').annotate(
            cantidad=Count('id'),
            ingresos=Sum('servicios__precio')
        ).order_by('-cantidad')[:5]

        servicios_top = []
        for s in top_servicios_query:
            if s['servicios__nombre']:
                servicios_top.append({
                    'nombre': s['servicios__nombre'],
                    'cantidad': s['cantidad'],
                    'ingresos': float(s['ingresos'] or 0)
                })

        # 6. TOP PRODUCTOS
        top_productos_query = DetalleVenta.objects.filter(
            venta__in=ventas_periodo,
            producto__isnull=False
        ).values('producto__nombre').annotate(
            cantidad=Sum('cantidad')
        ).order_by('-cantidad')[:5]

        productos_top = [
            {'nombre': p['producto__nombre'], 'cantidad': p['cantidad']}
            for p in top_productos_query
        ]

        # 7. STOCK BAJO (LÓGICA BLINDADA - Mantenemos la tuya)
        # Cuenta productos con stock <= mínimo o stock 0
        stock_bajo_count = Producto.objects.filter(
            Q(stock_actual__lte=F('stock_minimo')) | Q(stock_actual=0)
        ).count()

        data = {
            'ingresosTotales': float(ingresos_totales),
            'serviciosRealizados': servicios_realizados,
            'productosVendidos': productos_vendidos,
            'stockBajoCount': stock_bajo_count,
            'ventasPorDia': ventas_por_dia,
            'labelsDias': labels_dias,
            'serviciosTop': servicios_top,
            'productosTop': productos_top
        }

        return Response(data)

    except Exception as e:
        print(f"❌ Error Dashboard: {e}")
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


# EN usuarios/views.py

@api_view(["GET"])
@permission_classes([AllowAny])
def listar_marcas(request):
    """
    Devuelve las marcas con la lista de nombres de sus proveedores.
    """
    marcas = Marca.objects.all().annotate(
        productos_count=models.Count("productos"),
        total_proveedores=models.Count("proveedores"),
    ).order_by('nombre')

    data = []
    for marca in marcas:
        # 🔥 CLAVE: Esto manda una lista de strings ["Loreal", "Sedal"]
        proveedores_nombres = list(marca.proveedores.values_list("nombre", flat=True))

        data.append({
            "id": marca.id,
            "nombre": marca.nombre,
            "descripcion": marca.descripcion,
            "estado": marca.estado,
            "estado_display": marca.get_estado_display(),
            "productos_count": marca.productos_count,
            "total_proveedores": marca.total_proveedores,
            "proveedores_nombres": proveedores_nombres, 
            "fecha_creacion": marca.fecha_creacion,
        })

    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def crear_marca(request):
    """Crea marca y asocia proveedores"""
    try:
        data = request.data
        nombre = data.get('nombre')
        
        if not nombre:
            return Response({'message': 'El nombre es obligatorio'}, status=400)
            
        if Marca.objects.filter(nombre__iexact=nombre).exists():
            return Response({'message': 'La marca ya existe'}, status=400)
            
        marca = Marca.objects.create(
            nombre=nombre,
            descripcion=data.get('descripcion', ''),
            estado=data.get('estado', 'activo')
        )
        
        # Guardar proveedores si vienen
        if 'proveedores' in data and isinstance(data['proveedores'], list):
            marca.proveedores.set(data['proveedores'])
            
        return Response({'id': marca.id, 'nombre': marca.nombre}, status=201)
    except Exception as e:
        return Response({'message': str(e)}, status=400)

# En usuarios/views.py

@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def actualizar_marca(request, pk):
    marca = get_object_or_404(Marca, pk=pk)

    if request.method == 'GET':
        # Recuperamos los IDs de forma segura
        ids_proveedores = list(marca.proveedores.values_list('id', flat=True))
        
        return Response({
            'id': marca.id,
            'nombre': marca.nombre,
            'descripcion': marca.descripcion or '', # Si es Null, manda cadena vacía
            'estado': marca.estado,
            'proveedores': ids_proveedores
        })

    if request.method == 'PUT':
        try:
            data = request.data
            
            # Actualizamos campos básicos
            marca.nombre = data.get('nombre', marca.nombre)
            marca.descripcion = data.get('descripcion', marca.descripcion)
            marca.estado = data.get('estado', marca.estado)
            
            # 🔥 CORRECCIÓN CLAVE: Manejo seguro de la lista de proveedores
            proveedores_data = data.get('proveedores')
            
            # Solo intentamos actualizar si proveedores_data es una lista válida
            if proveedores_data is not None and isinstance(proveedores_data, list):
                # Filtramos IDs vacíos o nulos por seguridad
                ids_limpios = [id for id in proveedores_data if id]
                marca.proveedores.set(ids_limpios)
            elif proveedores_data == []: 
                # Si mandan lista vacía explícita, limpiamos las relaciones
                marca.proveedores.clear()
            
            marca.save()
            return Response({'status': 'ok', 'message': 'Marca actualizada correctamente'})
            
        except Exception as e:
            print(f"❌ Error al actualizar marca {pk}: {str(e)}") # Log para ver en terminal
            return Response({'error': f'Error interno: {str(e)}'}, status=400)

@csrf_exempt
def cambiar_estado_marca(request, pk):
    """Cambia el estado de una marca (activo/inactivo)"""
    if request.method != 'PATCH':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        marca = get_object_or_404(Marca, pk=pk)
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        if nuevo_estado not in ['activo', 'inactivo']:
            return JsonResponse({'error': 'Estado inválido'}, status=400)
        
        marca.estado = nuevo_estado
        marca.save()
        
        return JsonResponse({
            'status': 'ok',
            'message': f'Estado cambiado a {nuevo_estado}',
            'marca': {
                'id': marca.id,
                'nombre': marca.nombre,
                'estado': marca.estado
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class MarcaSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    productos_count = serializers.IntegerField(read_only=True)
    total_proveedores = serializers.IntegerField(read_only=True)
    proveedores_nombres = serializers.ListField(child=serializers.CharField(), read_only=True)

    class Meta:
        model = Marca
        fields = [
            "id",
            "nombre",
            "descripcion",
            "estado",
            "estado_display",
            "productos_count",
            "total_proveedores",
            "proveedores_nombres",
            "fecha_creacion",
        ]
    

@csrf_exempt
def eliminar_marca(request, pk):
    """Elimina una marca (si no tiene productos asociados)"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        marca = get_object_or_404(Marca, pk=pk)
        
        # Verificar si tiene productos asociados
        productos_count = Producto.objects.filter(marca=marca).count()
        if productos_count > 0:
            return JsonResponse({
                'error': f'No se puede eliminar la marca porque tiene {productos_count} producto(s) asociado(s)',
                'suggestion': 'Cambie el estado a "inactivo" en su lugar.'
            }, status=400)
        
        marca.delete()
        return JsonResponse({
            'status': 'ok',
            'message': 'Marca eliminada correctamente'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
        
        # Validar que no esté ya cancelado para evitar doble reembolso
        if turno.estado == 'CANCELADO':
             return JsonResponse({'error': 'El turno ya está cancelado'}, status=400)

        print(f"📅 Turno: {turno.fecha} {turno.hora} - Estado: {turno.estado}")

        # 2. PROCESAR REEMBOLSO AUTOMÁTICO 💰
        print("💳 Verificando reembolso automático...")
        reembolso_ok, mensaje_reembolso = procesar_reembolso_si_corresponde(turno)
        print(f"💰 Resultado Reembolso: {mensaje_reembolso}")

        # 3. CAMBIAR ESTADO A CANCELADO
        # Guardamos el estado anterior por si hay que revertir (opcional, pero buena práctica)
        # estado_anterior = turno.estado 
        
        turno.estado = 'CANCELADO'
        turno.oferta_activa = False # Se activa solo si hay interesados abajo
        turno.save()
        
        print("✅ Turno marcado como CANCELADO")

        # 4. BUSCAR INTERESADOS
        # (Asumo que obtener_interesados busca en tu modelo de ListaDeEspera o similar)
        print("🔎 Buscando interesados en lista de espera...")
        interesados = turno.obtener_interesados() 
        cantidad_interesados = interesados.count()
        print(f"👥 Interesados encontrados: {cantidad_interesados}")

        # 5. DECISIÓN: REOFERTA O DISPONIBLE
        if cantidad_interesados > 0:
            print(f"🚀 Iniciando reoferta masiva para {cantidad_interesados} personas...")
            
            # Activar modo reoferta
            turno.oferta_activa = True
            turno.fecha_expiracion_oferta = timezone.now() + timedelta(hours=1)
            turno.save()

            # Importamos aquí para evitar ciclos
            from .tasks import procesar_reoferta_masiva
            
            # Disparar tarea Celery
            procesar_reoferta_masiva.delay(turno_id)
            
            return JsonResponse({
                'status': 'ok',
                'message': f'Turno cancelado. {mensaje_reembolso} Se inició la reoferta para {cantidad_interesados} clientes.',
                'reoferta_iniciada': True,
                'interesados': cantidad_interesados,
                'reembolso_info': mensaje_reembolso
            })
        else:
            print("ℹ️ No hay interesados. El turno pasa a DISPONIBLE directo.")
            turno.estado = 'DISPONIBLE' # Ojo: Chequear si tu sistema permite volver a 'DISPONIBLE' o si borrás el turno.
            turno.cliente = None        # Desvinculamos al cliente original
            turno.monto_seña = 0        # Limpiamos seña
            turno.monto_total = 0       # Limpiamos total
            turno.mp_payment_id = None  # Limpiamos ID de pago
            turno.oferta_activa = False
            turno.save()
            
            return JsonResponse({
                'status': 'ok', 
                'message': f'Turno cancelado y liberado. {mensaje_reembolso} Queda disponible en la agenda.',
                'reoferta_iniciada': False,
                'interesados': 0,
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
        turno = get_object_or_404(Turno, pk=turno_id)
        interes = InteresTurnoLiberado.objects.filter(token_oferta=token, turno_liberado=turno).first()

        if not interes:
            return Response({'error': 'Oferta no encontrada'}, status=404)
        
        # ✅ CORREGIDO: servicio_elegido (con s)
        servicio_elegido = interes.servicio 
        
        # Calculamos precios sobre TU servicio
        precio_base = servicio_elegido.precio
        descuento = Decimal(interes.descuento_aplicado)
        factor = Decimal('1') - (descuento / Decimal('100'))
        
        precio_final = precio_base * factor
        monto_sena = precio_final * Decimal('0.5')

        data = {
            'profesional': f"{turno.peluquero.nombre} {turno.peluquero.apellido}",
            'fecha': turno.fecha.strftime("%d/%m/%Y"),
            'hora': turno.hora.strftime("%H:%M"),
            'servicio': servicio_elegido.nombre,
            'precio_original': float(precio_base),
            'precio_final': float(precio_final),
            'monto_sena': float(monto_sena)
        }
        return Response(data)

    except Exception as e:
        print(f"❌ Error info oferta: {e}")
        return Response({'error': str(e)}, status=500)
    
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
    Permite al cliente cancelar SU turno.
    Si corresponde reembolso, avisa en el backend y notifica amablemente al cliente.
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
        ahora = timezone.now()
        fecha_turno = timezone.make_aware(datetime.combine(turno.fecha, turno.hora))
        tiempo_restante = fecha_turno - ahora

        if tiempo_restante < timedelta(hours=3):
             return Response({
                 'error': 'Ya no puedes cancelar online (faltan menos de 3hs). Por favor llama al local.'
             }, status=400)

        # 4. PROCESAR REEMBOLSO (Usamos la nueva lógica manual)
        reembolso_corresponde, mensaje_tecnico = procesar_reembolso_si_corresponde(turno)
        
        # Definimos el mensaje para el cliente
        mensaje_cliente = "Turno cancelado correctamente."
        if reembolso_corresponde:
            mensaje_cliente += " Nos pondremos en contacto a la brevedad para gestionar tu reintegro."
        else:
            mensaje_cliente += " (No corresponde reintegro por política de cancelación o falta de pago)."

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
            'message': mensaje_cliente, # ✅ Mensaje suave para el frontend
            'debug_info': mensaje_tecnico # (Opcional) Por si quieres verlo en la consola del navegador
        })

    except Turno.DoesNotExist:
        return Response({'error': 'Turno no encontrado'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def aceptar_oferta_turno(request, turno_id, token):
    print(f"🎁 DEBUG: Aceptando oferta Turno {turno_id}")
    try:
        turno_nuevo = get_object_or_404(Turno, pk=turno_id)
        
        # Buscamos por token
        interes_principal = InteresTurnoLiberado.objects.filter(token_oferta=token).first()
        if not interes_principal:
            return Response({'error': 'Oferta no encontrada.'}, status=404)

        if turno_nuevo.estado != 'CANCELADO':
            return Response({'error': 'El turno ya no está disponible.'}, status=400)

        with transaction.atomic():
            # A. RECUPERAR TODOS LOS SERVICIOS QUE EL CLIENTE QUERÍA
            # Buscamos todos los intereses de este cliente para esa fecha/hora
            intereses_todos = InteresTurnoLiberado.objects.filter(
                cliente=interes_principal.cliente,
                fecha_deseada=interes_principal.fecha_deseada,
                hora_deseada=interes_principal.hora_deseada,
                estado_oferta='pendiente' # O enviada
            )
            
            # Limpiamos servicios viejos y ponemos LOS NUEVOS (los 3 que pediste)
            turno_nuevo.servicios.clear()
            total_precio_base = 0
            
            for inte in intereses_todos:
                turno_nuevo.servicios.add(inte.servicio)
                total_precio_base += float(inte.servicio.precio)
                # Marcamos todos como aceptados
                inte.aceptar_oferta()

            # B. CALCULAR PRECIO
            descuento = Decimal(interes_principal.descuento_aplicado)
            precio_final = Decimal(total_precio_base) * (Decimal('1') - (descuento / Decimal('100')))
            monto_seña_nueva = precio_final * Decimal('0.5')
            
            turno_nuevo.monto_total = precio_final
            turno_nuevo.monto_seña = monto_seña_nueva
            turno_nuevo.cliente = interes_principal.cliente
            turno_nuevo.cliente_asignado_reoferta = interes_principal.cliente
            turno_nuevo.oferta_activa = False
            turno_nuevo.canal = 'WEB'

            # C. CANCELACIÓN AGRESIVA DEL TURNO ANTERIOR
            # Buscamos cualquier turno RESERVADO o CONFIRMADO del cliente
            # SIN filtrar por fecha exacta, solo que sea futuro o hoy.
            turnos_viejos = Turno.objects.filter(
                cliente=interes_principal.cliente,
                estado__in=['RESERVADO', 'CONFIRMADO'],
                fecha__gte=timezone.now().date()
            ).exclude(pk=turno_nuevo.pk) # Que no sea este mismo

            saldo_favor = Decimal('0.00')
            id_pago_viejo = None

            if turnos_viejos.exists():
                # Tomamos el primero que aparezca (asumiendo que es el que querés cambiar)
                turno_viejo = turnos_viejos.first()
                print(f"🔄 CANJE: Cancelando turno {turno_viejo.id} ({turno_viejo.fecha} {turno_viejo.hora})")
                
                # Rescatamos la plata
                if turno_viejo.estado == 'CONFIRMADO':
                    saldo_favor = turno_viejo.monto_total if turno_viejo.tipo_pago == 'TOTAL' else turno_viejo.monto_seña
                elif turno_viejo.monto_seña > 0: # Si tiene plata anotada aunque esté reservado
                    saldo_favor = turno_viejo.monto_seña
                
                id_pago_viejo = turno_viejo.mp_payment_id
                
                # CANCELAR EL VIEJO
                turno_viejo.estado = 'CANCELADO'
                turno_viejo.save()

            # D. CONFIRMACIÓN FINAL
            msg = "¡Turno confirmado!"
            
            if saldo_favor >= monto_seña_nueva:
                turno_nuevo.estado = 'RESERVADO' # Queda reservado pago
                # Acá podríamos poner CONFIRMADO si querés que aparezca verde directo
                # Pero respetando tu lógica de 3 estados, queda Reservado con saldo a favor
                
                # Guardamos cuanto pagó realmente (transferido del viejo)
                turno_nuevo.monto_seña = monto_seña_nueva 
                turno_nuevo.mp_payment_id = id_pago_viejo
                
                if saldo_favor > monto_seña_nueva:
                    sobrante = saldo_favor - monto_seña_nueva
                    msg += f" Te sobran ${sobrante} a favor."
                
                response_data = {'success': True, 'message': msg, 'mp_init_point': None}
            else:
                turno_nuevo.estado = 'RESERVADO'
                falta = monto_seña_nueva - saldo_favor
                from .mercadopago_service import MercadoPagoService
                mp = MercadoPagoService()
                pref = mp.crear_preferencia_seña({
                    'turno_id': turno_nuevo.id, 'monto_pago': float(falta),
                    'cliente_nombre': "Cliente", 'cliente_correo': "email@test.com",
                    'peluquero_nombre': "HairSoft", 'es_pago_total': False
                })
                response_data = {'success': True, 'message': f'Aboná la diferencia de ${falta}', 'mp_init_point': pref['init_point']}

            turno_nuevo.save()
            return Response(response_data)

    except Exception as e:
        print(f"❌ Error CRÍTICO aceptar_oferta: {e}")
        return Response({'error': str(e)}, status=500)

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
@permission_classes([AllowAny])
def gestionar_cotizacion_externa(request, token):
    cotizacion = get_object_or_404(Cotizacion, token=token)

    if request.method == 'GET':
        if cotizacion.respondio:
            return Response({"ya_respondido": True})
        
        serializer = CotizacionExternaSerializer(cotizacion)
        data = serializer.data
        
        # Le mandamos al front cuánto pedimos originalmente
        # para que aparezca en el input por defecto
        if hasattr(cotizacion.solicitud, 'cantidad_requerida'):
             data['cantidad_requerida'] = cotizacion.solicitud.cantidad_requerida
             data['producto_nombre'] = cotizacion.solicitud.producto.nombre
             data['proveedor_nombre'] = cotizacion.proveedor.nombre

        return Response(data)

    if request.method == 'POST':
        if cotizacion.respondio:
            return Response({"error": "Ya respondiste esta solicitud"}, status=400)
        
        # 1. CAPTURAMOS LA CANTIDAD QUE ENVÍA EL PROVEEDOR
        cantidad_real = request.data.get('cantidad')
        if cantidad_real:
            cotizacion.cantidad_ofertada = int(cantidad_real)
        
        # 2. Guardamos el resto
        cotizacion.precio_ofrecido = request.data.get('precio_ofrecido')
        cotizacion.dias_entrega = request.data.get('dias_entrega')
        cotizacion.comentarios = request.data.get('comentarios', '')
        
        cotizacion.respondio = True
        cotizacion.fecha_respuesta = timezone.now()
        cotizacion.save()
        
        return Response({"mensaje": "Éxito"})

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

#CUPON DEL PROCESO AUTOMATIZADO - CLIENTES INACTIVOSPSSS
@api_view(['GET'])
@permission_classes([AllowAny])
def validar_cupon(request, codigo):
    """Valida si un cupón existe y está vigente"""
    # Importación local para evitar errores circulares si los hubiera
    from .models import PromocionReactivacion
    from django.utils import timezone

    try:
        promo = PromocionReactivacion.objects.get(codigo=codigo)
        
        if not promo.esta_vigente:
            return Response({'valido': False, 'mensaje': 'Este cupón ya venció o fue usado.'})
            
        return Response({
            'valido': True,
            'descuento': float(promo.descuento_porcentaje),
            'mensaje': f'¡Genial! Tenés un {promo.descuento_porcentaje}% de descuento.',
            'promo_id': promo.id
        })
        
    except PromocionReactivacion.DoesNotExist:
        return Response({'valido': False, 'mensaje': 'Código de cupón inválido.'}, status=404)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

#Marcaaaa
class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    pagination_class = PageNumberPagination
    page_size = 10  # Asegúrate de usar esta clase
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_creacion', 'fecha_modificacion']
    ordering = ['nombre']

    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        marca = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado in ['activo', 'inactivo']:
            marca.estado = nuevo_estado
            marca.save()
            serializer = self.get_serializer(marca)
            return Response({
                'status': 'Estado actualizado',
                'estado': marca.estado,
                'marca': serializer.data
            })
        return Response({'error': 'Estado inválido. Use "activo" o "inactivo".'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def estados(self, request):
        """Obtener lista de estados disponibles"""
        return Response([
            {'value': 'activo', 'label': 'Activo'},
            {'value': 'inactivo', 'label': 'Inactivo'}
        ])

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por estado si se proporciona en query params
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            
        # Filtrar solo activas por defecto si no se especifica
        if not estado and self.request.query_params.get('todos') != 'true':
            queryset = queryset.filter(estado='activo')
            
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Sobrescribir para hacer eliminación lógica en lugar de física"""
        instance = self.get_object()
        
        # Verificar si hay productos asociados
        productos_count = instance.producto_set.count()
        if productos_count > 0:
            return Response({
                'error': f'No se puede eliminar la marca porque tiene {productos_count} producto(s) asociado(s).',
                'suggestion': 'Cambie el estado a "inactivo" en su lugar.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_turnos(request):
    """Devuelve SOLO los turnos del cliente logueado ordenados por fecha."""
    try:
        # 🚨 VERIFICAR SI EL USUARIO ES CLIENTE O ADMIN
        user_rol = None
        if hasattr(request.user, 'rol') and request.user.rol:
            user_rol = request.user.rol.nombre.upper()
        
        print(f"🔍 Usuario ID: {request.user.id}, Nombre: {request.user.nombre}, Rol: {user_rol}")
        
        # 🚨 SI ES ADMIN, BUSCAR TURNOS DE TODOS LOS CLIENTES (para testing)
        if user_rol in ['ADMIN', 'SUPERADMIN']:
            print("⚠️ Usuario es admin, mostrando turnos de prueba")
            # Crear datos de prueba o mostrar últimos turnos
            turnos = Turno.objects.all().order_by('-fecha', '-hora')[:5]
        else:
            # Cliente normal - sus propios turnos
            turnos = Turno.objects.filter(cliente=request.user).order_by('-fecha', '-hora')
        
        print(f"🔍 Turnos encontrados: {turnos.count()}")
        
        data = []
        ahora = timezone.now()
        
        for t in turnos:
            # Calcular duración y nombre de servicios
            servicios_list = list(t.servicios.all())
            duracion = sum(s.duracion for s in servicios_list)
            servicios_str = ", ".join([s.nombre for s in servicios_list])
            
            # Lógica de cancelación (Regla de 3 horas para el cliente)
            fecha_turno = timezone.make_aware(datetime.combine(t.fecha, t.hora))
            tiempo_restante = fecha_turno - ahora
            puede_cancelar = (
                t.estado in ['RESERVADO', 'CONFIRMADO'] and 
                tiempo_restante > timedelta(hours=3)
            )

            data.append({
                'id': t.id,
                'fecha': t.fecha.strftime("%Y-%m-%d"),
                'hora': t.hora.strftime("%H:%M"),
                'peluquero_nombre': f"{t.peluquero.nombre} {t.peluquero.apellido}",
                'servicios': servicios_str,
                'estado': t.estado,
                'tipo_pago': t.tipo_pago,  # ✅ AGREGADO
                'medio_pago': t.medio_pago,  # ✅ AGREGADO
                'canal': t.canal,  # ✅ AGREGADO
                'monto_total': float(t.monto_total),
                'monto_seña': float(t.monto_seña),
                'puede_cancelar': puede_cancelar,
                'duracion': duracion
            })
            
        return Response(data)
        
    except Exception as e:
        print(f"Error en mis_turnos: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_turnos_general(request):
    """
    Vista para el panel de administración/recepción.
    Filtra por peluquero, fecha, estado, etc.
    """
    try:
        # 1. QuerySet Base
        turnos = Turno.objects.all().select_related('cliente', 'peluquero', 'cliente__rol', 'peluquero__rol').prefetch_related('servicios').order_by('-fecha', '-hora')

        # 2. FILTROS
        peluquero_id = request.GET.get('peluquero') or request.GET.get('peluquero_id')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        estado = request.GET.get('estado')
        canal = request.GET.get('canal')
        
        if peluquero_id and peluquero_id != 'undefined':
            turnos = turnos.filter(peluquero_id=peluquero_id)

        if fecha_desde:
            turnos = turnos.filter(fecha__gte=fecha_desde)
        
        if fecha_hasta:
            turnos = turnos.filter(fecha__lte=fecha_hasta)
            
        if estado and estado != 'Todos':
            turnos = turnos.filter(estado=estado)
            
        if canal and canal != 'Todos':
            turnos = turnos.filter(canal=canal)

        # 3. USA EL SERIALIZER (La forma correcta)
        # Esto incluye automáticamente 'medio_pago', 'mp_payment_id', etc.
        serializer = TurnoSerializer(turnos, many=True)
        
        return Response(serializer.data)

    except Exception as e:
        print(f"❌ Error listar_turnos_general: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
    
@api_view(['GET'])
@permission_classes([AllowAny]) # Cambialo a IsAuthenticated cuando quieras cerrar el grifo
def listado_auditoria(request):
    # Traemos todo ordenado por fecha (lo más nuevo arriba)
    logs = Auditoria.objects.all().select_related('usuario').order_by('-fecha')
    serializer = AuditoriaSerializer(logs, many=True)
    return Response(serializer.data)

#Para recuperar la contraseña desde el login
@api_view(['POST'])
@permission_classes([AllowAny])
def solicitar_reset_password(request):
    serializer = SolicitarResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    email = serializer.validated_data['email']
    
    try:
        usuario = Usuario.objects.get(correo=email)
        reset_token = PasswordResetToken.objects.create(usuario=usuario)
        
        # Link al Frontend
        link = f"http://localhost:5173/recuperar-password/{reset_token.token}"
        
        # --- DISEÑO DEL EMAIL HTML ---
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f1f5f9; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 30px; text-align: center; }}
                .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; letter-spacing: 1px; }}
                .content {{ padding: 40px 30px; color: #334155; text-align: center; }}
                .welcome {{ font-size: 20px; font-weight: 600; margin-bottom: 20px; color: #1e293b; }}
                .text {{ font-size: 16px; line-height: 1.6; margin-bottom: 30px; }}
                .btn {{ display: inline-block; background-color: #0ea5e9; color: #ffffff !important; padding: 16px 32px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 16px; transition: background 0.3s; }}
                .btn:hover {{ background-color: #0284c7; }}
                .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>HairSoft</h1>
                </div>
                <div class="content">
                    <div class="welcome">Hola, {usuario.nombre}</div>
                    <div class="text">
                        Recibimos una solicitud para restablecer tu contraseña. 
                        Si fuiste vos, hacé clic en el botón de abajo para crear una nueva.
                    </div>
                    
                    <a href="{link}" class="btn">Restablecer Contraseña</a>
                    
                    <div class="text" style="margin-top: 30px; font-size: 14px; color: #64748b;">
                        Este enlace expirará en 1 hora. <br>
                        Si no solicitaste esto, podés ignorar este correo.
                    </div>
                </div>
                <div class="footer">
                    &copy; 2025 HairSoft. Todos los derechos reservados.
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject="🔐 Recuperación de Contraseña - HairSoft",
            message=plain_message, 
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message 
        )
        
        return Response({"message": "Correo enviado."})

    except Usuario.DoesNotExist:
        return Response({"message": "Correo enviado."}) 

@api_view(['POST'])
@permission_classes([AllowAny])
def confirmar_reset_password(request):
    serializer = ResetPasswordConfirmarSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    token_str = serializer.validated_data['token']
    nueva_pass = serializer.validated_data['nueva_password']

    try:
        reset_token = PasswordResetToken.objects.get(token=token_str)
        
        if not reset_token.es_valido:
            return Response({"error": "El enlace ha expirado o ya fue usado."}, status=400)
            
        usuario = reset_token.usuario
        usuario.set_password(nueva_pass) # Hashea la contraseña
        usuario.save()
        
        # Quemar token
        reset_token.usado = True
        reset_token.save()
        
        return Response({"message": "¡Contraseña actualizada! Ya podés iniciar sesión."})

    except PasswordResetToken.DoesNotExist:
        return Response({"error": "Token inválido."}, status=400)