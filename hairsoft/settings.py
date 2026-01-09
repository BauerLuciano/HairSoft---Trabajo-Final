"""
Django settings for hairsoft project.
Production Ready: Render + Vercel + Cloudinary
"""

from pathlib import Path
import os
import dj_database_url  # Librería para la DB de Render

BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# CONFIGURACIÓN GENERAL Y SEGURIDAD
# ================================

# Si existe la variable RENDER, estamos en producción -> DEBUG False
# Si no existe (tu PC), estamos en local -> DEBUG True
IS_PRODUCTION = 'RENDER' in os.environ

# En producción usamos la clave de Render. En local usamos la insegura por defecto.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ip8)+yuz^y06zqgl-%w%05^vjroio(3@@4qo(tz_0ssvtpe@3(')

DEBUG = not IS_PRODUCTION

# Permitimos todos los hosts por ahora para facilitar el deploy
ALLOWED_HOSTS = ['*']

# ================================
# APLICACIONES INSTALADAS
# ================================
INSTALLED_APPS = [
    # Librerías de terceros (Orden importante para Cloudinary)
    'cloudinary_storage', # <--- Debe ir antes de staticfiles y cloudinary
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Resto de librerías
    'cloudinary',  # <--- Cloudinary
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
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- VITAL PARA RENDER (Archivos estáticos)
    'corsheaders.middleware.CorsMiddleware',
    
    'usuarios.middleware.DisableCSRFMiddleware', # Tu anti-csrf
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware', 
    'django.middleware.csrf.CsrfViewMiddleware', 
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'usuarios.middleware.AuditoriaMiddleware', # Tu auditoría
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
# BASE DE DATOS (HÍBRIDA)
# ================================
# Lógica: Si Render nos da una base de datos (DATABASE_URL), usamos esa.
# Si no, usamos tu configuración local de PostgreSQL.

if 'DATABASE_URL' in os.environ:
    # Configuración de Producción (Render)
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
    # Tu configuración Local (PostgreSQL 5433)
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
# ARCHIVOS ESTÁTICOS (CSS, JS, Admin)
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Usamos WhiteNoise para servir los estáticos en Render de forma eficiente
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================
# ARCHIVOS MEDIA (IMÁGENES - CLOUDINARY)
# ================================
# Esto hace que las fotos se guarden en la nube en vez de en el disco del servidor
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/' 

# Credenciales de Cloudinary (Se cargan desde Render, o vacías en local si no las pones)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# ================================
# CONFIGURACIÓN CORS / CSRF
# ================================
# En producción permitimos todo inicialmente para evitar dolores de cabeza con Vercel
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

# Estos siguen siendo útiles para seguridad específica, aunque Allow All los sobrescribe un poco
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://hairsoft-frontend.vercel.app", # Agregá aquí tu dominio de Vercel cuando lo tengas
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://hairsoft-backend.onrender.com", # Tu dominio backend (ejemplo)
    "https://hairsoft-frontend.vercel.app",  # Tu dominio frontend
]

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = IS_PRODUCTION # True en producción (HTTPS), False en local
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

SESSION_COOKIE_SECURE = IS_PRODUCTION
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
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# CONFIGURACIÓN MERCADO PAGO
# ================================
# Nota: Podrías mover estos tokens a variables de entorno en Render por seguridad
MERCADO_PAGO = {
    'ACCESS_TOKEN': os.environ.get('MP_ACCESS_TOKEN', 'APP_USR-7404896415144376-102322-584184e7db9ca5b628be4d7e21763ae3-2943677918'),
    'PUBLIC_KEY': os.environ.get('MP_PUBLIC_KEY', 'APP_USR-4e145215-f26e-4c2d-8be7-a557300a9154'),
    'BACK_URLS': {
        # IMPORTANTE: En producción cambiar localhost por tu dominio de Vercel
        'success': os.environ.get('MP_SUCCESS_URL', 'http://localhost:5173/pago-exitoso'),
        'failure': os.environ.get('MP_FAILURE_URL', 'http://localhost:5173/pago-error'),
        'pending': os.environ.get('MP_PENDING_URL', 'http://localhost:5173/pago-pendiente')
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
# CONFIGURACIÓN EMAIL (MAILTRAP)
# ================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.environ.get('EMAIL_USER', 'c5b568c8fbd9b8')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '4aecfad93d7271')
DEFAULT_FROM_EMAIL = 'HairSoft <no-reply@hairsoft.com>'
EMAIL_FAIL_SILENTLY = False

# ================================
# CONFIGURACIÓN CELERY
# ================================
# Si Render nos da un Redis, lo usamos. Si no, modo síncrono (EAGER)
if 'REDIS_URL' in os.environ:
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    CELERY_TASK_ALWAYS_EAGER = False # Realmente asíncrono
else:
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# ================================
# CONFIGURACIÓN TWILIO WHATSAPP
# ================================
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_SID', 'ACb3de53c73913d7ec07a5c253ab2ca97f')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_TOKEN', '0f70fae6755002f66c23c4a50aff0400')
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

# ================================
# LOGGING
# ================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}