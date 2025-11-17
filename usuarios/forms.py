# usuarios/forms.py
from django import forms
from .models import Usuario
from django.contrib.auth.hashers import check_password, make_password

class UsuarioForm(forms.ModelForm):
    # ✅ CAMBIO: Renombrar a nueva_contrasena para mayor claridad
    nueva_contrasena = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Dejar vacío para mantener la actual',
            'autocomplete': 'new-password'
        }),
        label='Nueva contraseña',
        help_text="Solo complete si desea cambiar la contraseña"
    )
    
    contrasena_actual = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Solo si cambia la contraseña', 
            'autocomplete': 'current-password'
        }),
        label='Contraseña actual',
        help_text="Requerida solo si cambia la contraseña"
    )

    class Meta:
        model = Usuario
        # ✅ QUITAR 'contrasena' - usaremos nueva_contrasena en su lugar
        fields = ['nombre', 'apellido', 'dni', 'telefono', 'correo', 'rol', 'estado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ambos campos son opcionales
        self.fields['nueva_contrasena'].required = False
        self.fields['contrasena_actual'].required = False

    def clean(self):
        cleaned_data = super().clean()
        usuario = self.instance

        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        contrasena_actual = cleaned_data.get('contrasena_actual')

        # ✅ LÓGICA MEJORADA:
        # - Si es NUEVO usuario (creación): nueva_contrasena es obligatoria
        # - Si es usuario EXISTENTE (edición): nueva_contrasena es opcional
        
        if not usuario.pk:  # ✅ CREACIÓN - nueva contraseña obligatoria
            if not nueva_contrasena:
                self.add_error('nueva_contrasena', 'La contraseña es obligatoria para nuevos usuarios.')
        
        else:  # ✅ EDICIÓN - validar solo si se cambia la contraseña
            if nueva_contrasena:
                if not contrasena_actual:
                    self.add_error('contrasena_actual', 'Debe proporcionar la contraseña actual para cambiar la contraseña.')
                elif not check_password(contrasena_actual, usuario.contrasena):
                    self.add_error('contrasena_actual', 'La contraseña actual es incorrecta.')

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        
        nueva_contrasena = self.cleaned_data.get('nueva_contrasena')
        
        # ✅ ACTUALIZAR CONTRASEÑA solo si se proporcionó una nueva
        if nueva_contrasena:
            usuario.contrasena = make_password(nueva_contrasena)
        # ✅ Si es NUEVO usuario y no hay contraseña, ya se validó en clean()
        elif not usuario.pk:
            # Esto no debería pasar porque clean() ya validó
            raise ValueError("Contraseña requerida para nuevo usuario")
        
        if commit:
            usuario.save()
        
        return usuario