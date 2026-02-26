"""
Django settings for hairsoft project.
"""

from pathlib import Path
import os
import dj_database_url 

BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# CONFIGURACIÓN GENERAL
# ================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ip8)+yuz^y06zqgl-%w%05^vjroio(3@@4qo(tz_0ssvtpe@3(')
DEBUG = 'RAILWAY_ENVIRONMENT' not in os.environ

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', '.ngrok-free.dev', '.loca.lt']

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

MEDIA_URL = '/media/'
if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# CONFIGURACIÓN CORS / CSRF
# ================================
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:8000",
    "https://*.railway.app", 
    "https://*.vercel.app",
    "https://*.ngrok-free.dev",
    "https://*.loca.lt",
]

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = not DEBUG 
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

AUTHENTICATION_BACKENDS = [
    'usuarios.auth_backends.EmailAuthBackend', 
    'django.contrib.auth.backends.ModelBackend', 
]

AUTH_USER_MODEL = 'usuarios.Usuario'

# ================================
# MERCADO PAGO
# ================================
TUNNEL_URL = "https://hairsoft-pago.loca.lt"

MERCADO_PAGO = {
    'ACCESS_TOKEN': os.environ.get('MP_ACCESS_TOKEN', 'APP_USR-7404896415144376-102322-584184e7db9ca5b628be4d7e21763ae3-2943677918'),
    'PUBLIC_KEY': os.environ.get('MP_PUBLIC_KEY', 'APP_USR-4e145215-f26e-4c2d-8be7-a557300a9154'),
    'WEBHOOK_URL': f"{TUNNEL_URL}/api/mercadopago/webhook/",
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
# CELERY & REDIS
# ================================
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'c41a4f03f21d64'
EMAIL_HOST_PASSWORD = '0a2b6876a3cf08'
DEFAULT_FROM_EMAIL = 'HairSoft <no-reply@hairsoft.com>'
EMAIL_FAIL_SILENTLY = False

# ================================
# TWILIO WHATSAPP
# ================================
TWILIO_ACCOUNT_SID = 'ACb3de53c73913d7ec07a5c253ab2ca97f'
TWILIO_AUTH_TOKEN = '0f70fae6755002f66c23c4a50aff0400'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'