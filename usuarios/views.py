# usuarios/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Usuario, Turno, Servicio
from .forms import UsuarioForm, TurnoForm
from dal import autocomplete
from django.db.models import Q
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django.views import View
from django.contrib import messages
from django.http import JsonResponse

# ================================
# Usuarios
# ================================

def listado_turnos(request):
    q = request.GET.get('q', '')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')

    turnos = Turno.objects.all()

    # Filtro por cliente
    if q:
        turnos = turnos.filter(
            Q(cliente__nombre__icontains=q) | Q(cliente__apellido__icontains=q)
        )

    # Filtro por rango de fechas
    if fecha_desde:
        turnos = turnos.filter(fecha__gte=parse_date(fecha_desde))
    if fecha_hasta:
        turnos = turnos.filter(fecha__lte=parse_date(fecha_hasta))

    return render(request, 'usuarios/listado_turnos.html', {
        'turnos': turnos,
        'q': q,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta
    })

def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/usuario_form.html', {'form': form})

def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listado_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/usuario_form.html', {'form': form})

def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        return redirect('listado_usuarios')
    return render(request, 'usuarios/usuario_confirm_delete.html', {'usuario': usuario})

# ================================
# Turnos
# ================================
def listado_turnos(request):
    q = request.GET.get('q', '')

    if q:
        turnos = Turno.objects.filter(cliente__nombre__icontains=q) | Turno.objects.filter(cliente__apellido__icontains=q)
    else:
        turnos = Turno.objects.all()

    return render(request, 'usuarios/listado_turnos.html', {
        'turnos': turnos,
        'q': q
    })

def crear_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            if not turno.cliente_id:
                messages.error(request, "Debe seleccionar un cliente válido antes de guardar el turno.")
                return render(request, 'usuarios/registrar_turno.html', {'form': form})
            turno.save()
            form.save_m2m()
            messages.success(request, "Turno registrado correctamente.")
            return redirect('listado_turnos')
    else:
        form = TurnoForm()

    return render(request, 'usuarios/registrar_turno.html', {'form': form})


def editar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            return redirect('listado_turnos')
    else:
        form = TurnoForm(instance=turno)
    return render(request, 'usuarios/registrar_turno.html', {'form': form})


def eliminar_turno(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    if request.method == 'POST':
        turno.delete()
        return redirect('listado_turnos')
    return render(request, 'usuarios/eliminar_turno.html', {'turno': turno})


def listado_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listado_usuarios.html', {'usuarios': usuarios})


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

    peluqueros = Usuario.objects.filter(rol='PEL')
    return render(request, 'usuarios/reporte_turnos.html', {'turnos': turnos, 'peluqueros': peluqueros})

# ================================
# Autocomplete de clientes
# ================================
class ClienteAutocomplete(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        clientes = Usuario.objects.filter(rol='CLI', nombre__icontains=q)
        results = [{'id': c.id, 'text': f'{c.nombre} {c.apellido}'} for c in clientes]
        return JsonResponse({'results': results})
