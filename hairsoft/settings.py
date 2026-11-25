"""
Django settings for hairsoft project.
"""

from pathlib import Path
import os
import dj_database_url 

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path):
    """Carga un archivo .env simple sin dependencias externas.
    No sobreescribe variables de entorno ya definidas."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


# En Render/producción se usan variables de entorno reales; .env es solo para desarrollo local.
if not (os.environ.get('RENDER') or os.environ.get('RENDER_EXTERNAL_HOSTNAME')):
    _load_env_file(BASE_DIR / '.env')

# ================================
# CONFIGURACIÓN GENERAL
# ================================
_INSECURE_SECRET_KEY_DEFAULT = 'django-insecure-ip8)+yuz^y06zqgl-%w%05^vjroio(3@@4qo(tz_0ssvtpe@3('
SECRET_KEY = os.environ.get('SECRET_KEY', _INSECURE_SECRET_KEY_DEFAULT)

# Producción: DEBUG=False incluso si falta configuración.
# Desarrollo local: conserva DEBUG=True por defecto (sin RENDER).
_PRODUCTION_ENV = bool(
    os.environ.get('RENDER')
    or os.environ.get('RENDER_EXTERNAL_HOSTNAME')
)
DEBUG = os.environ.get('DEBUG', 'False' if _PRODUCTION_ENV else 'True').lower() in ('true', '1', 'yes')

if not DEBUG and SECRET_KEY == _INSECURE_SECRET_KEY_DEFAULT:
    raise RuntimeError(
        'SECRET_KEY insegura o no configurada. Definí la variable de entorno SECRET_KEY en producción.'
    )

_DEFAULT_DEV_ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok-free.dev', '.loca.lt']
_env_allowed_hosts = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
_render_external_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()

if DEBUG:
    ALLOWED_HOSTS = list(_DEFAULT_DEV_ALLOWED_HOSTS)
    for _host in _env_allowed_hosts:
        if _host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_host)
else:
    ALLOWED_HOSTS = [h for h in _env_allowed_hosts if h != '*']
    if _render_external_host and _render_external_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_render_external_host)

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
PUBLIC_BACKEND_URL = os.environ.get('PUBLIC_BACKEND_URL', 'https://brandi-palmar-pickily.ngrok-free.dev').rstrip('/')

# ================================
# APLICACIONES INSTALADAS
# ================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'corsheaders', 
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'dal',
    'dal_select2',
    'widget_tweaks',
    
    'cloudinary_storage',
    'cloudinary',

    'drf_spectacular',
    'usuarios',
]

# ================================
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',     
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'usuarios.middleware.DisableCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.AuditoriaMiddleware',
]

ROOT_URLCONF = 'hairsoft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hairsoft.wsgi.application'

# =================
# BASE DE DATOS
# =================
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'hairsoft_db', 
            'USER': 'admin', 
            'PASSWORD': 'admin', 
            'HOST': 'localhost', 
            'PORT': '5433', 
            'OPTIONS': {
                'options': '-c search_path=public'
            },
            'CONN_MAX_AGE': 0,
        }
    }

# ================================
# CACHÉ
# ================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hairsoft-cache',
        'TIMEOUT': 300,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ================================
# INTERNACIONALIZACIÓN
# ================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# ================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

_USE_CLOUDINARY_STORAGE = bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))

STORAGES = {
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.MediaCloudinaryStorage'
            if _USE_CLOUDINARY_STORAGE
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# CONFIGURACIÓN CORS / CSRF
# ================================
_DEFAULT_DEV_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
_DEFAULT_DEV_CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "https://*.ngrok-free.dev",
    "https://*.loca.lt",
]

_env_cors_origins = [o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]
_env_csrf_trusted_origins = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []
    CORS_ALLOW_CREDENTIALS = True

    CSRF_TRUSTED_ORIGINS = list(_DEFAULT_DEV_CSRF_TRUSTED_ORIGINS)
    for _origin in _env_csrf_trusted_origins:
        if _origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(_origin)
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = list(_env_cors_origins)
    if not CORS_ALLOWED_ORIGINS and FRONTEND_URL:
        CORS_ALLOWED_ORIGINS = [FRONTEND_URL.strip()]
    CORS_ALLOW_CREDENTIALS = True

    CSRF_TRUSTED_ORIGINS = [o for o in _env_csrf_trusted_origins if '*' not in o]
    if not CSRF_TRUSTED_ORIGINS and FRONTEND_URL:
        CSRF_TRUSTED_ORIGINS = [FRONTEND_URL.strip()]
    if _render_external_host:
        _render_origin = f"https://{_render_external_host}"
        if _render_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(_render_origin)

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ================================
# SEGURIDAD / HTTPS
# ================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'user-rol',
    'user-id',
    'x-navegador-real',
]

CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]

AUTHENTICATION_BACKENDS = [
    'usuarios.auth_backends.EmailAuthBackend', 
    'django.contrib.auth.backends.ModelBackend', 
]

AUTH_USER_MODEL = 'usuarios.Usuario'

# ================================
# MERCADO PAGO
# ================================
TUNNEL_URL = PUBLIC_BACKEND_URL

MERCADO_PAGO = {
    'ACCESS_TOKEN': os.environ.get('MP_ACCESS_TOKEN', '').strip(),
    'PUBLIC_KEY': os.environ.get('MP_PUBLIC_KEY', '').strip(),
    'WEBHOOK_URL': f"{PUBLIC_BACKEND_URL}/api/mercadopago/webhook/",
    'BINARY_MODE': True,
    'SANDBOX': True
}

if not DEBUG:
    _missing_mp = [
        name for name, value in (
            ('MP_ACCESS_TOKEN', MERCADO_PAGO['ACCESS_TOKEN']),
            ('MP_PUBLIC_KEY', MERCADO_PAGO['PUBLIC_KEY']),
        ) if not value
    ]
    if _missing_mp:
        raise RuntimeError(
            f"Faltan credenciales de Mercado Pago en producción: {', '.join(_missing_mp)}. "
            "Definí estas variables de entorno en Render."
        )

# ================================
# REST FRAMEWORK
# ================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': None,
    'PAGE_SIZE': None,
}

# ================================
# CELERY & REDIS
# ================================
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# 🔥 PARA PRODUCCIÓN/AUTOMATIZACIÓN CAMBIAR A False
CELERY_TASK_ALWAYS_EAGER = False 
CELERY_TASK_EAGER_PROPAGATES = False

CELERY_TASK_ANNOTATIONS = {
    '*': {
        'retry': True,
        'retry_policy': {
            'max_retries': 3,
            'interval_start': 2,
            'interval_step': 2,
            'interval_max': 10,
        }
    }
}

# ================================
# EMAIL (MAILTRAP)
# ================================
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend').strip()
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'sandbox.smtp.mailtrap.io').strip()
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '2525'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '').strip()
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'HairSoft <no-reply@hairsoft.com>').strip()
EMAIL_FAIL_SILENTLY = os.environ.get('EMAIL_FAIL_SILENTLY', 'False').lower() in ('true', '1', 'yes')

if not DEBUG:
    _missing_email = [
        name for name, value in (
            ('EMAIL_HOST_USER', EMAIL_HOST_USER),
            ('EMAIL_HOST_PASSWORD', EMAIL_HOST_PASSWORD),
        ) if not value
    ]
    if _missing_email:
        raise RuntimeError(
            f"Faltan credenciales de correo en producción: {', '.join(_missing_email)}. "
            "Definí estas variables de entorno en Render."
        )

# ================================
# TWILIO WHATSAPP
# ================================
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '').strip()
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '').strip()
TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886').strip()

if not DEBUG:
    _missing_twilio = [
        name for name, value in (
            ('TWILIO_ACCOUNT_SID', TWILIO_ACCOUNT_SID),
            ('TWILIO_AUTH_TOKEN', TWILIO_AUTH_TOKEN),
        ) if not value
    ]
    if _missing_twilio:
        raise RuntimeError(
            f"Faltan credenciales Twilio en producción: {', '.join(_missing_twilio)}. "
            "Definí estas variables de entorno en Render."
        )

# CONFIGURACIÓN DE GOOGLE LOGIN
GOOGLE_CLIENT_ID = "537753408019-uhdhpoqgkqtbkaj25d90601n1f3qguth.apps.googleusercontent.com"