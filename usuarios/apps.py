# usuarios/apps.py

from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
    
    # 🛑 CRÍTICO: Importar las señales en el método ready()
    def ready(self):
        # Importa el archivo signals.py para ejecutar la desconexión
        import usuarios.signals