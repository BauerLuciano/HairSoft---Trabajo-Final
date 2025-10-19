# usuarios/forms.py
from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    contrasena_actual = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña actual'}),
        label='Contraseña actual'
    )

    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'contrasena': forms.PasswordInput(render_value=True),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ No exigir contraseña al editar
        self.fields['contrasena'].required = False
        self.fields['contrasena_actual'].required = False

    def clean(self):
        cleaned_data = super().clean()
        usuario = self.instance

        contrasena = cleaned_data.get('contrasena')
        contrasena_actual = cleaned_data.get('contrasena_actual')

        # ✅ Solo validar si se intenta cambiar la contraseña
        if usuario and usuario.pk:
            if contrasena and not contrasena_actual:
                self.add_error('contrasena_actual', 'Debe proporcionar la contraseña actual para cambiar la contraseña.')

        return cleaned_data
    

