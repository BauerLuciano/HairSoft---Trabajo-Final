from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.contrib.auth.hashers import make_password
# 🛑 CORRECCIÓN APLICADA: Importar authenticate y login
from django.contrib.auth import authenticate, login 
from rest_framework import viewsets, status, generics 
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response 
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Rol, Permiso, Usuario, Servicio, CategoriaProducto, CategoriaServicio, Producto, Turno, Proveedor, Venta, DetalleVenta, MetodoPago, Pedido, DetallePedido
from .mercadopago_service import MercadoPagoService
import json
import requests
from .serializers import LoginSerializer, ProveedorSerializer, ProductoSerializer, VentaSerializer, DetalleVentaSerializer, CategoriaProductoSerializer, MetodoPagoSerializer, VentaUpdateSerializer, CategoriaServicioSerializer, PedidoSerializer, DetallePedidoSerializer, PedidoRecepcionSerializer, PedidoBusquedaSerializer
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
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

    rol_id = data.get('rol') or data.get('rol_id')
    data['rol'] = rol_id if rol_id else None

    # 🔹 Validación: un solo administrador
    if rol_id:
        rol = Rol.objects.filter(pk=rol_id).first()
        if rol and rol.nombre.upper() == 'ADMINISTRADOR':
            if Usuario.objects.filter(rol__nombre__iexact='ADMINISTRADOR', estado='ACTIVO').exists():
                return JsonResponse({'status': 'error', 'message': 'Ya existe un administrador activo'}, status=400)

    if 'contrasena' in data and data['contrasena']:
        data['contrasena'] = make_password(data['contrasena'])
    else:
        data.pop('contrasena', None)

    form = UsuarioForm(data)
    if form.is_valid():
        try:
            usuario = form.save()
            return JsonResponse({'status': 'ok', 'id': usuario.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al guardar el usuario: {str(e)}'}, status=500)

    errores = {k: v for k, v in form.errors.items()}
    return JsonResponse({'status': 'error', 'errors': errores}, status=400)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@api_view(['POST'])
@permission_classes([AllowAny])
def login_auth(request):
    print("🚨 LOGIN ENDPOINT HIT")
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated_data = serializer.validated_data
    correo = validated_data.get('username')
    contrasena_ingresada = validated_data.get('password')
    
    print(f"📦 Data Validada - Correo: {correo}")

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
        print("❌ Login failed - Credenciales inválidas")
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
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

    if 'contrasena' in data and data['contrasena']:
        data['contrasena'] = make_password(data['contrasena'])
    else:
        data.pop('contrasena', None)

    form = UsuarioForm(data, instance=usuario)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': 'ok', 'id': usuario.id})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


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
#@csrf_exempt
#def listado_productos(request):
#    if request.method != 'GET':
#        return JsonResponse({'error': 'Método no permitido'}, status=405)
#
#    productos = Producto.objects.all()
#    data = [
#        {
#            'id': p.id,
#            'nombre': p.nombre,
#            'precio': float(p.precio),
#            'stock': p.stock,
#            'categoria': p.categoria.nombre if p.categoria else None
#        } for p in productos
#    ]
#    return JsonResponse(data, safe=False)
#

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
# ================================
# Turnos - Vistas Actualizadas
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
                    'duracion': servicio.duracion
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

            data.append({
                'id': t.id,
                'fecha': t.fecha.isoformat(),
                'hora': t.hora.strftime("%H:%M"),
                'estado': t.estado,  # ← ESTO ESTÁ BIEN, envía 'RESERVADO'
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


# ================================
# usuarios/views.py
# ================================
@csrf_exempt
def crear_turno(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)

        # 1️⃣ Usuario logueado
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': "Debe iniciar sesión para reservar."}, status=401)
        cliente = request.user

        # 2️⃣ Datos del formulario
        peluquero_id = data.get('peluquero_id')
        servicios_ids = data.get('servicios_ids', [])
        fecha = data.get('fecha')
        hora = data.get('hora')
        tipo_pago_seleccionado = data.get('tipo_pago')  # SENA_50 o TOTAL

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
            canal='WEB',
            tipo_pago=tipo_pago_seleccionado,
            medio_pago='MERCADO_PAGO',
            monto_seña=monto_seña_a_guardar,
            monto_total=monto_total,
            estado='RESERVADO'
        )
        turno.servicios.set(servicios)

        print(f"✅ Turno creado temporalmente: {turno.id} - Procesando MP")

        # 7️⃣ Preparar datos para Mercado Pago (SDK)
        mp_service = MercadoPagoService()
        es_pago_total = (tipo_pago_seleccionado == 'TOTAL')

        turno_data = {
            'turno_id': turno.id,
            'monto_pago': float(monto_pago_a_enviar_mp),
            'cliente_nombre': f"{cliente.nombre} {cliente.apellido}",
            'cliente_correo': "test_user_6205179917708892357@testuser.com",  # sandbox
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


@csrf_exempt
def cancelar_turno(request, turno_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        turno = Turno.objects.get(pk=turno_id)
        
        # Verificar si puede ser cancelado
        puede_cancelar, hay_reembolso = turno.puede_ser_cancelado()
        
        if not puede_cancelar:
            return JsonResponse({
                'status': 'error',
                'message': 'No se puede cancelar el turno. Debe cancelarse con al menos 3 horas de anticipación.'
            }, status=400)

        # Cambiar estado a cancelado
        turno.estado = 'CANCELADO'
        turno.reembolsado = hay_reembolso
        turno.save()

        mensaje = 'Turno cancelado exitosamente'
        if hay_reembolso:
            if turno.canal == 'WEB':
                mensaje += '. Seña reembolsada via Mercado Pago.'
            else:
                mensaje += '. Cliente debe pasar a buscar el reembolso.'
        else:
            mensaje += '. No corresponde reembolso.'

        return JsonResponse({
            'status': 'ok',
            'message': mensaje,
            'reembolsado': hay_reembolso
        })

    except Turno.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Turno no encontrado'
        }, status=404)
    except Exception as e:
        print("Error al cancelar turno:", e)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

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
