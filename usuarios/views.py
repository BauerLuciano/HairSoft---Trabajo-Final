from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from .models import Usuario
from .forms import UsuarioForm
import json
from django.contrib.auth.hashers import make_password

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
    """API para obtener el listado de usuarios, con filtros de búsqueda y serialización correcta."""
    q = request.GET.get('q', '').strip()
    
    try:
        usuarios = Usuario.objects.all()
    except Exception as e:
        print(f"Error al consultar usuarios: {e}")
        return JsonResponse([], safe=False)

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
            'rol': get_rol_abreviado(u.rol),
            'correo': u.correo or '',
            'estado': (u.estado or 'ACTIVO').upper(),
            'fecha_creacion': u.fecha_creacion.isoformat() if u.fecha_creacion else ''
        } for u in usuarios
    ]
    
    return JsonResponse(data, safe=False)

@csrf_exempt
def crear_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        if 'contrasena' in data:
            data['contrasena'] = make_password(data['contrasena'])

        form = UsuarioForm(data)
        if form.is_valid():
            usuario = form.save()
            return JsonResponse({'status': 'ok', 'id': usuario.id})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@csrf_exempt
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        form = UsuarioForm(data, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            return JsonResponse({'status': 'ok', 'id': usuario.id})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@csrf_exempt
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        try:
            usuario.estado = 'INACTIVO'
            usuario.save()
            return JsonResponse({'status': 'ok', 'message': 'Usuario desactivado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al desactivar usuario: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

# ================================
# Placeholders Turnos
# ================================
@csrf_exempt
def listado_turnos(request):
    return JsonResponse({'turnos': []})

@csrf_exempt
def crear_turno(request):
    return JsonResponse({'status': 'ok', 'mensaje': 'crear_turno pendiente'})

@csrf_exempt
def editar_turno(request, pk):
    return JsonResponse({'status': 'ok', 'mensaje': 'editar_turno pendiente'})

@csrf_exempt
def eliminar_turno(request, pk):
    return JsonResponse({'status': 'ok', 'mensaje': 'eliminar_turno pendiente'})

class ClienteAutocomplete(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({'results': []})
