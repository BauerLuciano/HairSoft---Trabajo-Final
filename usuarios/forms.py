# hairsoft/forms.py
from django import forms
from django.utils import timezone
from .models import Turno, Usuario, Servicio
from datetime import datetime, timedelta

class TurnoForm(forms.ModelForm):
    # Campo de servicios como checkboxes
    servicios = forms.ModelMultipleChoiceField(
        queryset=Servicio.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Turno
        fields = ['cliente', 'fecha', 'hora', 'peluquero', 'servicios']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limitar fechas de hoy hasta 7 días
        hoy = timezone.localdate()
        limite = hoy + timedelta(days=7)
        self.fields['fecha'].widget.attrs['min'] = hoy.isoformat()
        self.fields['fecha'].widget.attrs['max'] = limite.isoformat()
        
        # Mostrar solo peluqueros en el campo peluquero
        self.fields['peluquero'].queryset = Usuario.objects.filter(rol='PEL')


    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        peluquero = cleaned_data.get("peluquero")

        hoy = timezone.localdate()
        ahora = timezone.localtime().time()

        # Fecha no puede ser en el pasado
        if fecha and fecha < hoy:
            self.add_error("fecha", "La fecha no puede ser en el pasado.")

        # Si la fecha es hoy, la hora debe ser futura
        if fecha == hoy and hora and hora <= ahora:
            self.add_error("hora", "La hora debe ser mayor a la actual.")

        # Validar que el peluquero no tenga dos turnos a la vez
        if fecha and hora and peluquero:
            conflicto = Turno.objects.filter(fecha=fecha, hora=hora, peluquero=peluquero)
            if self.instance.pk:
                conflicto = conflicto.exclude(pk=self.instance.pk)
            if conflicto.exists():
                self.add_error("peluquero", "El peluquero ya tiene un turno en esa fecha y hora.")

        return cleaned_data


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'dni', 'contrasena', 'telefono', 'correo', 'rol']

    def clean_rol(self):
        rol = self.cleaned_data['rol']
        if rol == "ADMIN" and Usuario.objects.filter(rol="ADMIN").exists():
            raise forms.ValidationError("Ya existe un administrador. No puede haber más de uno.")
        return rol

def crear_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_turnos')
    else:
        form = TurnoForm()
    return render(request, 'usuarios/registrar_turno.html', {'form': form})
