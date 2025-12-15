import threading
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

_thread_locals = threading.local()

def get_current_request_data():
    return getattr(_thread_locals, 'request_data', {})

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class DisableCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response

class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)

        # Si Django no encontró usuario (es Anónimo), buscamos el Token a mano
        if not user or user.is_anonymous:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            # Soportar 'Token <key>' y 'Bearer <key>'
            if ' ' in auth_header:
                prefix, key = auth_header.split(' ')[:2]
                if prefix in ['Token', 'Bearer']:
                    try:
                        token_obj = Token.objects.select_related('user').get(key=key)
                        user = token_obj.user
                    except Token.DoesNotExist:
                        pass

        # Datos técnicos
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:250]

        # Guardar en hilo global
        _thread_locals.user = user
        _thread_locals.request_data = {
            'user': user,
            'ip': ip,
            'navegador': user_agent
        }
        
        response = self.get_response(request)
        return response