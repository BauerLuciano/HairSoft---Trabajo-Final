import threading
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject

_thread_locals = threading.local()

def get_current_request_data():
    return getattr(_thread_locals, 'request_data', {})

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
        user = None

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header:
            parts = auth_header.strip().split()
            if len(parts) == 2:
                prefix = parts[0].decode('utf-8') if isinstance(parts[0], bytes) else parts[0]
                key = parts[1].decode('utf-8') if isinstance(parts[1], bytes) else parts[1]
                
                if prefix.lower() in ['token', 'bearer']:
                    try:
                        token_obj = Token.objects.select_related('user').get(key=key)
                        user = token_obj.user
                        request.user = user  
                    except Token.DoesNotExist:
                        pass

        if not user:
            session_user = getattr(request, 'user', None)
            if isinstance(session_user, SimpleLazyObject):
                session_user._setup()
                session_user = session_user._wrapped
            
            if not getattr(session_user, 'is_anonymous', True):
                user = session_user

        if getattr(user, 'is_anonymous', True):
            user = None

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', 'Desconocido')[:250]

        _thread_locals.request_data = {
            'user': user,
            'ip': ip,
            'navegador': user_agent
        }
        
        try:
            response = self.get_response(request)
            return response
        finally:
            _thread_locals.request_data = {}