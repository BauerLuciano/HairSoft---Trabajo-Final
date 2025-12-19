import threading
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject

_thread_locals = threading.local()

def get_current_request_data():
    return getattr(_thread_locals, 'request_data', {})

# Clase para desactivar CSRF (la que ya tenías)
class DisableCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return self.get_response(request)

class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Intentamos obtener el usuario estándar de Django
        user = getattr(request, 'user', None)

        # 2. Si no hay usuario o es Anónimo, buscamos el TOKEN manualmente
        if not user or user.is_anonymous:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if auth_header:
                # Limpiamos espacios extra y separamos
                parts = auth_header.strip().split()
                
                # Aceptamos 'Token <key>' o 'Bearer <key>'
                if len(parts) == 2 and parts[0].lower() in [b'token', 'token', b'bearer', 'bearer']:
                    key = parts[1]
                    try:
                        # Buscamos el token en la BD
                        token_obj = Token.objects.select_related('user').get(key=key)
                        user = token_obj.user
                        # ¡Lo encontramos! Lo asignamos al request para que el resto del sistema sepa
                        request.user = user
                    except Token.DoesNotExist:
                        pass # Token falso o expirado

        # 3. Datos técnicos
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        
        user_agent = request.META.get('HTTP_USER_AGENT', 'Desconocido')[:250]

        # 4. Guardamos en el hilo global para signals.py
        _thread_locals.request_data = {
            'user': user if user and not user.is_anonymous else None,
            'ip': ip,
            'navegador': user_agent
        }
        
        response = self.get_response(request)
        
        # Limpieza
        _thread_locals.request_data = {}
        
        return response