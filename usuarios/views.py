# usuarios/views.py
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.views import View
from django.http import JsonResponse
from .models import Usuario, Turno
from .forms import UsuarioForm, TurnoForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password
# ================================
# Usuarios
# ================================

@csrf_exempt
def listado_usuarios(request):
    """
    Devuelve todos los usuarios en formato JSON.
    """
    usuarios = Usuario.objects.all()
    data = [
        {
            'id': u.id,
            'nombre': u.nombre,
            'apellido': u.apellido,
            'rol': u.rol,
            'correo': u.correo,
        } for u in usuarios
    ]
    return JsonResponse({'usuarios': data})


@csrf_exempt
def crear_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        # Hacer hash de la contraseña antes de pasar al formulario
        if 'contrasena' in data:
            data['contrasena'] = make_password(data['contrasena'])

        form = UsuarioForm(data)
        if form.is_valid():
            usuario = form.save()
            return JsonResponse({'status': 'ok', 'id': usuario.id})
        else:
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
        usuario.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# ================================
# Turnos
# ================================

def listado_turnos(request):
    q = request.GET.get('q', '')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    turnos = Turno.objects.all()

    if q:
        turnos = turnos.filter(
            Q(cliente__nombre__icontains=q) | Q(cliente__apellido__icontains=q)
        )
    if fecha_desde:
        turnos = turnos.filter(fecha__gte=parse_date(fecha_desde))
    if fecha_hasta:
        turnos = turnos.filter(fecha__lte=parse_date(fecha_hasta))

    data = [
        {
            'id': t.id,
            'cliente': f'{t.cliente.nombre} {t.cliente.apellido}',
            'fecha': t.fecha,
            'estado': t.estado,
            'peluquero': f'{t.peluquero.nombre} {t.peluquero.apellido}' if t.peluquero else None
        } for t in turnos
    ]
    return JsonResponse({'turnos': data})


@csrf_exempt
def crear_turno(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        form = TurnoForm(data)
        if form.is_valid():
            turno = form.save(commit=False)
            if not turno.cliente_id:
                return JsonResponse({'status': 'error', 'message': 'Debe seleccionar un cliente válido'}, status=400)
            turno.save()
            form.save_m2m()
            return JsonResponse({'status': 'ok', 'id': turno.id})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@csrf_exempt
def editar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        form = TurnoForm(data, instance=turno)
        if form.is_valid():
            turno = form.save()
            return JsonResponse({'status': 'ok', 'id': turno.id})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@csrf_exempt
def eliminar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        turno.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
# ================================
# Reportes
# ================================

def reporte_turnos(request):
    turnos = Turno.objects.all()
    fecha = request.GET.get('fecha')
    estado = request.GET.get('estado')
    peluquero = request.GET.get('peluquero')

    if fecha:
        turnos = turnos.filter(fecha=fecha)
    if estado:
        turnos = turnos.filter(estado=estado)
    if peluquero:
        turnos = turnos.filter(peluquero__id=peluquero)

    data = [
        {
            'id': t.id,
            'cliente': f'{t.cliente.nombre} {t.cliente.apellido}',
            'fecha': t.fecha,
            'estado': t.estado,
            'peluquero': f'{t.peluquero.nombre} {t.peluquero.apellido}' if t.peluquero else None
        } for t in turnos
    ]
    peluqueros = [{'id': p.id, 'nombre': p.nombre} for p in Usuario.objects.filter(rol='PEL')]
    return JsonResponse({'turnos': data, 'peluqueros': peluqueros})

# ================================
# Autocomplete de clientes
# ================================

class ClienteAutocomplete(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        clientes = Usuario.objects.filter(rol='CLI', nombre__icontains=q)
        results = [{'id': c.id, 'text': f'{c.nombre} {c.apellido}'} for c in clientes]
        return JsonResponse({'results': results})
