"""
Django settings for hairsoft project.
"""

from pathlib import Path
import os
import dj_database_url # <--- NUEVO: Para conectar la BD de Railway

BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# CONFIGURACIÓN GENERAL
# ================================
# En Producción (Railway) toma la clave del entorno. En local usa la tuya.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ip8)+yuz^y06zqgl-%w%05^vjroio(3@@4qo(tz_0ssvtpe@3(')

# Si existe la variable 'RAILWAY_ENVIRONMENT', desactiva DEBUG. Si no, es True (tu PC).
DEBUG = 'RAILWAY_ENVIRONMENT' not in os.environ

# Aceptamos todo en producción para evitar errores de dominio en la demo
ALLOWED_HOSTS = ['*']

# ✅ URL DEL FRONTEND (Usando tu Ngrok actual)
# En producción (Railway), podrías definir esto en las variables de entorno.
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://brandi-palmar-pickily.ngrok-free.dev')

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
    
    # Apps de terceros
    'corsheaders', 
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'dal',
    'dal_select2',
    'widget_tweaks',
    
    # NUEVO: Para guardar imágenes en la nube
    'cloudinary_storage',
    'cloudinary',

    'drf_spectacular',
    # Tus apps
    'usuarios',
]

# ================================
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", # <--- NUEVO: OBLIGATORIO para estilos en Railway
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',      # El CORS debe ir alto
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'usuarios.middleware.DisableCSRFMiddleware',  # Tu middleware personalizado
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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

# =================
# BASE DE DATOS
# =================
# Si Railway nos da una base de datos (DATABASE_URL), usamos esa.
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    # SI NO, USAMOS TU CONFIGURACIÓN LOCAL ORIGINAL (No tocamos nada)
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
# ARCHIVOS ESTÁTICOS Y MEDIA (IMÁGENES)
# ================================
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Compresión para servir archivos rápido en Railway
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CLOUDINARY (Solo se activa si ponemos las claves en Railway)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Media files
MEDIA_URL = '/media/'
# Si hay credenciales de Cloudinary, úsalo. Si no, usa carpeta local.
if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# CONFIGURACIÓN CORS / CSRF
# ================================
CORS_ALLOW_ALL_ORIGINS = True # Permitimos todo para asegurar que la demo ande
CORS_ALLOW_CREDENTIALS = True

# Dominios confiables para CSRF (Agregamos comodines para Vercel y Railway)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:8000",
    "https://*.railway.app", # <--- IMPORTANTE
    "https://*.vercel.app",  # <--- IMPORTANTE
    "https://*.ngrok-free.dev", # <--- AGREGADO PARA NGROK
]

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = not DEBUG # True en prod, False en local
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = not DEBUG
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
# MERCADO PAGO
# ================================
# Intenta leer del entorno, si no usa los tuyos hardcodeados
MERCADO_PAGO = {
    'ACCESS_TOKEN': os.environ.get('MP_ACCESS_TOKEN', 'APP_USR-7404896415144376-102322-584184e7db9ca5b628be4d7e21763ae3-2943677918'),
    'PUBLIC_KEY': os.environ.get('MP_PUBLIC_KEY', 'APP_USR-4e145215-f26e-4c2d-8be7-a557300a9154'),
    'BACK_URLS': {
        # OJO: En producción tendrás que cambiar esto por la URL de Vercel en las variables de entorno si quieres que vuelva bien
        'success': os.environ.get('MP_URL_SUCCESS', 'http://localhost:5173/pago-exitoso'),
        'failure': os.environ.get('MP_URL_FAILURE', 'http://localhost:5173/pago-error'),
        'pending': os.environ.get('MP_URL_PENDING', 'http://localhost:5173/pago-pendiente')
    },
    'AUTO_RETURN': 'approved',
    'BINARY_MODE': True,
    'SANDBOX': True
}

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
# CELERY & REDIS (CONFIGURACIÓN HÍBRIDA)
# ================================
if 'REDIS_URL' in os.environ:
    # CONFIGURACIÓN PRODUCCIÓN (RAILWAY)
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    # IMPORTANTE: En producción queremos que sea asíncrono
    CELERY_TASK_ALWAYS_EAGER = False 
else:
    # CONFIGURACIÓN LOCAL (TESTING)
    # Sin Redis, todo síncrono como lo tenías antes
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# ================================
# EMAIL (MAILTRAP)
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
# TWILIO WHATSAPP
# ================================
TWILIO_ACCOUNT_SID = 'ACb3de53c73913d7ec07a5c253ab2ca97f'
TWILIO_AUTH_TOKEN = '0f70fae6755002f66c23c4a50aff0400'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

# ================================
# TAREAS AUTOMÁTICAS (CELERY BEAT)
# ================================
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'reactivar-clientes-diario': {
        'task': 'usuarios.tasks.procesar_reactivacion_clientes_inactivos',
        # Ejecutar todos los días a las 10:00 AM (Hora Argentina configurada en TIME_ZONE)
        'schedule': crontab(hour=8, minute=0),
    },
}