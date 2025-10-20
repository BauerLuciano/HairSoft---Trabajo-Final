# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from .models import Rol
import json

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
    usuarios = Usuario.objects.select_related('rol').all()
    
    if q:
        usuarios = usuarios.filter(
            Q(nombre__icontains=q) |
            Q(apellido__icontains=q) |
            Q(dni__icontains=q)
        )

    data = [
        {
            'id': u.id,
            'nombre': u.nombre or '',
            'apellido': u.apellido or '',
            'dni': u.dni or '',
            'telefono': u.telefono or '',
            'rol_id': u.rol.id if u.rol else None,
            'rol_nombre': u.rol.nombre if u.rol else None,  # <--- importante
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

    # 🔹 Obtener el ID del rol (acepta 'rol' o 'rol_id')
    rol_id = data.get('rol') or data.get('rol_id')
    data['rol'] = rol_id if rol_id else None

    # 🔹 Encriptar la contraseña si viene
    if 'contrasena' in data and data['contrasena']:
        data['contrasena'] = make_password(data['contrasena'])
    else:
        data.pop('contrasena', None)

    # 🔹 Crear el form
    form = UsuarioForm(data)
    if form.is_valid():
        try:
            usuario = form.save()
            return JsonResponse({'status': 'ok', 'id': usuario.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al guardar el usuario: {str(e)}'}, status=500)
    
    # 🔹 Devolver errores claros
    errores = {k: v for k, v in form.errors.items()}
    return JsonResponse({'status': 'error', 'errors': errores}, status=400)

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
class ClienteAutocomplete(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        clientes = Usuario.objects.filter(rol='CLIENTE', estado='ACTIVO')

        if q:
            clientes = clientes.filter(
                Q(nombre__icontains=q) |
                Q(apellido__icontains=q) |
                Q(dni__icontains=q)
            )

        results = [
            {
                'id': c.id,
                'nombre': c.nombre,
                'apellido': c.apellido,
                'dni': c.dni,
                'telefono': c.telefono,
                'correo': c.correo
            } for c in clientes
        ]

        return JsonResponse({'results': results})


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

    peluqueros = Usuario.objects.filter(rol='PELUQUERO', estado='ACTIVO')
    data = [{'id': p.id, 'nombre': f'{p.nombre} {p.apellido}'} for p in peluqueros]
    return JsonResponse(data, safe=False)


# ================================
# Turnos
# ================================
@csrf_exempt
def listado_turnos(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    turnos = Turno.objects.all().order_by('fecha', 'hora')
    data = []
    for t in turnos:
        servicios = [s.nombre for s in t.servicios.all()]
        data.append({
            'id': t.id,
            'fecha': t.fecha.isoformat(),
            'hora': t.hora.strftime("%H:%M"),
            'estado': t.estado,
            'cliente': f'{t.cliente.nombre} {t.cliente.apellido}',
            'peluquero': f'{t.peluquero.nombre} {t.peluquero.apellido}',
            'servicios': servicios
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def crear_turno(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        cliente_id = data.get('cliente')
        peluquero_id = data.get('peluquero')
        servicio_id = data.get('servicio')
        fecha_hora = data.get('fecha_hora')  # "YYYY-MM-DD HH:MM"

        if not fecha_hora or ' ' not in fecha_hora:
            return JsonResponse({'status': 'error', 'message': "Datos inválidos: fecha y hora deben enviarse juntas"}, status=400)

        fecha, hora = fecha_hora.split(' ')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Datos inválidos: {str(e)}'}, status=400)

    try:
        cliente = Usuario.objects.get(pk=cliente_id, rol='CLIENTE')
        peluquero = Usuario.objects.get(pk=peluquero_id, rol='PELUQUERO')
        servicio = Servicio.objects.get(pk=servicio_id)

        turno = Turno.objects.create(
            cliente=cliente,
            peluquero=peluquero,
            fecha=fecha,
            hora=hora
        )
        turno.servicios.add(servicio)
        turno.save()
        return JsonResponse({'status': 'ok', 'id': turno.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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

    roles = Rol.objects.all().order_by('nombre')
    data = [
        {
            'id': r.id,
            'nombre': r.nombre,
            'descripcion': r.descripcion or '',
            'activo': r.activo
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