# usuarios/auth_backends.py

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password 
from .models import Usuario 

class EmailAuthBackend(BaseBackend):
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 1. Busca el usuario por correo
            user = Usuario.objects.get(correo=username)
        except Usuario.DoesNotExist:
            return None 

        # 2. Verifica la contraseña
        is_password_valid = check_password(password, user.contrasena)
        
        # 🛑 ÚLTIMA CORRECCIÓN APLICADA: 
        # Reemplazamos 'user.is_active' por 'user.estado == "ACTIVO"'
        # Si usas otro valor (ej: 'activo' o un booleano), ajústalo aquí.
        if is_password_valid and user.estado == 'ACTIVO': 
            return user
        
        # 3. Si la contraseña no coincide o el usuario no está activo
        return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None