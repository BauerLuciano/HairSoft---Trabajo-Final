from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import make_password
# 🛑 CORRECCIÓN APLICADA: Importar authenticate y login
from django.contrib.auth import authenticate, login 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response 
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Rol, Permiso, Usuario, Servicio, CategoriaProducto, CategoriaServicio, Producto, Turno
from .mercadopago_service import MercadoPagoService
import json
import requests


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

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_auth(request):
    """Maneja la autenticación por sesión y devuelve el rol."""
    print("🚨 LOGIN ENDPOINT HIT")
    print(f"📝 Method: {request.method}")
    print(f"📦 Data: {request.data}")
    print(f"👤 User: {request.user}")
    print(f"🔐 Authenticated: {request.user.is_authenticated}")
    
    correo = request.data.get('username')
    contrasena = request.data.get('password')
    
    user = authenticate(request, username=correo, password=contrasena)
    print(f"🔍 User authenticated: {user}")

    if user is not None:
        login(request, user)
        print(f"✅ Login successful - User ID: {user.id}")
        
        user_rol = getattr(user, 'rol', None)
        rol_nombre = user_rol.nombre.upper() if user_rol else 'SIN_ROL'
        
        response_data = {
            'status': 'ok',
            'message': 'Login exitoso',
            'user_id': user.id,
            'rol': rol_nombre
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        print("❌ Login failed - Invalid credentials")
        return Response(
            {'status': 'error', 'message': 'Credenciales inválidas'}, 
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
@csrf_exempt
def listado_productos(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    productos = Producto.objects.all()
    data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'stock': p.stock,
            'categoria': p.categoria.nombre if p.categoria else None
        } for p in productos
    ]
    return JsonResponse(data, safe=False)


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


@csrf_exempt
def listado_categorias_productos(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    categorias = CategoriaProducto.objects.all().order_by('nombre')
    data = [{'id': c.id, 'nombre': c.nombre, 'descripcion': getattr(c, 'descripcion', '')} for c in categorias]
    return JsonResponse(data, safe=False)



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

# VISTA QUE CARGA EL USUARIO LOGUEADO EN VUE (SOLUCIONA EL 404 si la URL apunta aquí)
@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def me_api_view(request):
    """Devuelve los datos del usuario logueado para Vue."""
    user = request.user

    if not user.is_authenticated:
        # El decorador IsAuthenticated ya maneja esto, pero es buen chequeo.
        return Response({"detail": "No autenticado."}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Obtener el nombre del rol de la instancia de Rol
    user_rol = getattr(user, 'rol', None)
    rol_nombre = user_rol.nombre.upper() if user_rol else 'SIN_ROL'
    
    # 💡 CRÍTICO: Aquí validamos, si no es CLIENTE, lo sacamos del formulario de reserva.
    # Pero si lo quieres dejar pasar para otros módulos, solo quita este IF y devuelve todos los datos:
    # if rol_nombre != 'CLIENTE':
    #     return Response({"detail": "Acceso restringido a clientes para esta función."}, status=status.HTTP_403_FORBIDDEN)
    
    # 💡 Devuelve los datos usando los NOMBRES DE CAMPOS REALES (nombre, apellido, correo, etc.)
    return Response({
        'id': user.id,
        'nombre': getattr(user, 'nombre', ''), # <-- Usar 'nombre' de tu modelo Usuario
        'apellido': getattr(user, 'apellido', ''), # <-- Usar 'apellido' de tu modelo Usuario
        'dni': getattr(user, 'dni', None),
        'telefono': getattr(user, 'telefono', None),
        'correo': user.correo, 
        'rol': rol_nombre
    }, status=status.HTTP_200_OK)