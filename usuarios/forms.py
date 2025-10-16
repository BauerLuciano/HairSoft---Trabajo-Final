# hairsoft/forms.py
from django import forms
from django.utils import timezone
from .models import Turno, Usuario, Servicio
from datetime import datetime, timedelta

class TurnoForm(forms.ModelForm):
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
        hoy = timezone.localdate()
        limite = hoy + timedelta(days=7)
        self.fields['fecha'].widget.attrs['min'] = hoy.isoformat()
        self.fields['fecha'].widget.attrs['max'] = limite.isoformat()
        self.fields['peluquero'].queryset = Usuario.objects.filter(rol='PELUQUERO')

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        peluquero = cleaned_data.get("peluquero")

        hoy = timezone.localdate()
        ahora = timezone.localtime().time()

        if fecha and fecha < hoy:
            self.add_error("fecha", "La fecha no puede ser en el pasado.")
        if fecha == hoy and hora and hora <= ahora:
            self.add_error("hora", "La hora debe ser mayor a la actual.")
        if fecha and hora and peluquero:
            conflicto = Turno.objects.filter(fecha=fecha, hora=hora, peluquero=peluquero)
            if self.instance.pk:
                conflicto = conflicto.exclude(pk=self.instance.pk)
            if conflicto.exists():
                self.add_error("peluquero", "El peluquero ya tiene un turno en esa fecha y hora.")

        return cleaned_data

class UsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(required=False, widget=forms.PasswordInput)
    contrasena_actual = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'dni', 'contrasena', 'telefono', 'correo', 'rol', 'contrasena_actual']

    def clean_rol(self):
        rol = self.cleaned_data['rol']
        if rol == "ADMINISTRADOR" and Usuario.objects.filter(rol="ADMINISTRADOR").exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un administrador. No puede haber más de uno.")
        return rol

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('contrasena')
        contrasena_actual = cleaned_data.get('contrasena_actual')

        # Si es un usuario nuevo, la contraseña es obligatoria
        if not self.instance.pk and not contrasena:
            raise forms.ValidationError({"contrasena": "La contraseña es obligatoria al crear un usuario."})

        # Si se proporciona una nueva contraseña, validar contrasena_actual
        if contrasena and not contrasena_actual:
            raise forms.ValidationError({"contrasena_actual": "Debe proporcionar la contraseña actual para cambiar la contraseña."})

        return cleaned_data