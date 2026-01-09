"""
Django settings for hairsoft project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# CONFIGURACIÓN GENERAL
# ================================
SECRET_KEY = 'django-insecure-ip8)+yuz^y06zqgl-%w%05^vjroio(3@@4qo(tz_0ssvtpe@3('
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

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
    'django_filters',
    'usuarios',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders', 
    'dal',
    'dal_select2',
    'widget_tweaks',
]

# ================================
# MIDDLEWARE (CORREGIDO)
# ================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'usuarios.middleware.DisableCSRFMiddleware', # Tu anti-csrf
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', 
    'django.middleware.csrf.CsrfViewMiddleware', # (A veces necesario aunque uses DisableCSRF)
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <--- CLAVE: Identifica al usuario
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.AuditoriaMiddleware',
]

ROOT_URLCONF = 'hairsoft.urls'

# ================================
# TEMPLATES
# ================================
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

# ================================
# BASE DE DATOS
# ================================
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
# VALIDADORES DE CONTRASEÑA
# ================================
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
# ARCHIVOS ESTÁTICOS
# ================================
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# CONFIGURACIÓN CORS / CSRF
# ================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

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
]

CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]

# ================================
# AUTENTICACIÓN PERSONALIZADA
# ================================
AUTHENTICATION_BACKENDS = [
    'usuarios.auth_backends.EmailAuthBackend', 
    'django.contrib.auth.backends.ModelBackend', 
]

AUTH_USER_MODEL = 'usuarios.Usuario'

# ================================
# CONFIGURACIÓN MERCADO PAGO
# ================================
MERCADO_PAGO = {
    'ACCESS_TOKEN': 'APP_USR-7404896415144376-102322-584184e7db9ca5b628be4d7e21763ae3-2943677918',
    'PUBLIC_KEY': 'APP_USR-4e145215-f26e-4c2d-8be7-a557300a9154',
    'BACK_URLS': {
        'success': 'http://localhost:5173/pago-exitoso',
        'failure': 'http://localhost:5173/pago-error',
        'pending': 'http://localhost:5173/pago-pendiente'
    },
    'AUTO_RETURN': 'approved',
    'BINARY_MODE': True,
    'SANDBOX': True
}

# ================================
# CONFIGURACIÓN REST FRAMEWORK
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
# LOGGING
# ================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {'class': 'logging.NullHandler'},
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}

# ================================
# CONFIGURACIÓN EMAIL (MAILTRAP) 📧
# ================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'c5b568c8fbd9b8'
EMAIL_HOST_PASSWORD = '4aecfad93d7271'
DEFAULT_FROM_EMAIL = 'HairSoft <no-reply@hairsoft.com>'
EMAIL_FAIL_SILENTLY = False

# ================================
# CONFIGURACIÓN CELERY (MODO TESTING)
# ================================
# Las tareas se ejecutan sincrónicamente (sin necesidad de Redis)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ================================
# CONFIGURACIÓN TWILIO WHATSAPP (REAL)
# ================================
TWILIO_ACCOUNT_SID = 'ACb3de53c73913d7ec07a5c253ab2ca97f'
TWILIO_AUTH_TOKEN = '0f70fae6755002f66c23c4a50aff0400'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

# ================================
# CONFIGURACIÓN DE IMAGENES PARA EL CATALOGO
# ================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')