"""
Django settings for hairsoft project.
Production Ready: Render + Vercel + Cloudinary
"""

from pathlib import Path
import os
import dj_database_url  # Librería fundamental para la DB de Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ================================
# CONFIGURACIÓN GENERAL Y SEGURIDAD
# ================================

# Detectamos si estamos en Render verificando si existe la variable RENDER
IS_PRODUCTION = 'RENDER' in os.environ

# En producción usamos la clave secreta de las variables de entorno.
# En local usamos una por defecto para que no te de error.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-ip8)+yuz^y06zqgl-%w%05^vjroio(3@@4qo(tz_0ssvtpe@3(')

# DEBUG debe ser False en producción por seguridad
DEBUG = not IS_PRODUCTION

# Permitimos todos los hosts en producción para evitar errores de dominio en Render
ALLOWED_HOSTS = ['*']

# ================================
# APLICACIONES INSTALADAS
# ================================
INSTALLED_APPS = [
    # 1. Apps nativas de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 2. Librerías de terceros
    'corsheaders',            # Para conectar con Vue/Vercel
    'cloudinary_storage',     # Para guardar imágenes en la nube
    'cloudinary',             # Librería base de Cloudinary
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'dal',
    'dal_select2',
    'widget_tweaks',

    # 3. Tus aplicaciones
    'usuarios',
]

# ================================
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- VITAL PARA RENDER (Archivos estáticos)
    'corsheaders.middleware.CorsMiddleware',      # <--- VITAL PARA VERCEL (Conexión Frontend)
    
    'usuarios.middleware.DisableCSRFMiddleware',  # Tu middleware para facilitar APIs
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'usuarios.middleware.AuditoriaMiddleware',    # Tu auditoría
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
# Si no, usamos tu configuración local (SQLite o PostgreSQL local).

if 'DATABASE_URL' in os.environ:
    # Configuración de Producción (Render)
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
    }
else:
    # Tu configuración Local (PostgreSQL)
    # Si te da error localmente, asegurate de tener tu base 'hairsoft_db' creada.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'hairsoft_db',
            'USER': 'admin',
            'PASSWORD': 'admin',
            'HOST': 'localhost',
            'PORT': '5433', # Ojo con el puerto, dejé el tuyo (5433)
            'OPTIONS': {
                'options': '-c search_path=public'
            },
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
LANGUAGE_CODE = 'es-ar' # Puse Español Argentina
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# ================================
# ARCHIVOS ESTÁTICOS (CSS, JS, Admin)
# ================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 🚨 Esto asegura que Django encuentre los archivos estáticos de las apps
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configuración WhiteNoise para servir estáticos en Render
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ================================
# ARCHIVOS MEDIA (IMÁGENES - CLOUDINARY)
# ================================
# Esto hace que las fotos se guarden en la nube en vez de en el disco del servidor
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/' 

# Credenciales de Cloudinary
# (Render las leerá de Environment Variables, en local podés dejarlas vacías o ponerlas en .env)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# ================================
# CONFIGURACIÓN CORS / CSRF (Para Vercel)
# ================================
# En producción permitimos todo inicialmente para asegurar que el Login funcione
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

# Lista explícita de orígenes permitidos
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://hairsoft-backend.onrender.com",
    # TUS DOMINIOS REALES DE VERCEL:
    "https://hairsoft-trabajo-final.vercel.app",
    "https://hairsoft-tr-git-22f909-luciano-agustin-bauers-projects-1743f39e.vercel.app",
]

# ESTA ES LA PARTE IMPORTANTE PARA EL LOGIN (CSRF):
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://hairsoft-backend.onrender.com",
    # TUS DOMINIOS REALES DE VERCEL:
    "https://hairsoft-trabajo-final.vercel.app",
    "https://hairsoft-tr-git-22f909-luciano-agustin-bauers-projects-1743f39e.vercel.app",
]

# Cookies y Sesiones (Adaptadas para HTTPS en producción)
CSRF_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_HTTPONLY = False 
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
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
# AUTENTICACIÓN
# ================================
AUTHENTICATION_BACKENDS = [
    'usuarios.auth_backends.EmailAuthBackend', 
    'django.contrib.auth.backends.ModelBackend', 
]

AUTH_USER_MODEL = 'usuarios.Usuario'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================================
# MERCADO PAGO
# ================================
MERCADO_PAGO = {
    'ACCESS_TOKEN': os.environ.get('MP_ACCESS_TOKEN', 'APP_USR-7404896415144376-102322-584184e7db9ca5b628be4d7e21763ae3-2943677918'),
    'PUBLIC_KEY': os.environ.get('MP_PUBLIC_KEY', 'APP_USR-4e145215-f26e-4c2d-8be7-a557300a9154'),
    'BACK_URLS': {
        # OJO: Cambiar localhost por URL de Vercel en las variables de entorno de Render
        'success': os.environ.get('MP_SUCCESS_URL', 'http://localhost:5173/pago-exitoso'),
        'failure': os.environ.get('MP_FAILURE_URL', 'http://localhost:5173/pago-error'),
        'pending': os.environ.get('MP_PENDING_URL', 'http://localhost:5173/pago-pendiente')
    },
    'AUTO_RETURN': 'approved',
    'BINARY_MODE': True,
    'SANDBOX': True
}

# ================================
# DJANGO REST FRAMEWORK
# ================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', # Ojo: Permite acceso público por defecto, ajustalo en las vistas
    ],
    'DEFAULT_PAGINATION_CLASS': None,
    'PAGE_SIZE': None,
}

# ================================
# EMAIL (Mailtrap)
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
# CELERY / REDIS
# ================================
if 'REDIS_URL' in os.environ:
    # Producción (Si agregás Redis en Render)
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    CELERY_TASK_ALWAYS_EAGER = False 
else:
    # Local (Sin Redis -> Ejecuta tareas síncronas)
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# ================================
# TWILIO WHATSAPP
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