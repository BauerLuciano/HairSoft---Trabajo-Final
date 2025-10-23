"""
Django settings for hairsoft project.
... (Resto de comentarios)
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-ip8)+yuz^y06zqgl-%w%05^vjroio(3@@4qo(tz_0ssvtpe@3('
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'rest_framework',
    'corsheaders', 
    'dal',
    'dal_select2',
    'widget_tweaks',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    # 🛑 ESTA LÍNEA DEBE SEGUIR COMENTADA/ELIMINADA
    #'django.middleware.csrf.CsrfViewMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# Database
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
        }
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ================================
# CONFIGURACIÓN CORS / CSRF (FINAL)
# ================================

CORS_ALLOW_ALL_ORIGINS = False 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True 
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 🛑 SOLUCIÓN CRÍTICA PARA EL 403 EN LOCALHOST (HTTP) 🛑
# Forzar a Django a no requerir HTTPS para las cookies en desarrollo.
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False 
SESSION_COOKIE_HTTPONLY = True 


# --------------------------------

AUTHENTICATION_BACKENDS = [
    'usuarios.auth_backends.EmailAuthBackend', 
    'django.contrib.auth.backends.ModelBackend', 
]

AUTH_USER_MODEL = 'usuarios.Usuario' # Correctamente definido

# ================================
# CONFIGURACIÓN MERCADO PAGO
# ================================

MERCADO_PAGO = {
    'ACCESS_TOKEN': 'TEST-108294043041566-102218-55b41e3807beeb1a23eadd5aebc04ab3-801234268',
    'PUBLIC_KEY': 'TEST-81162340-88c1-4a97-ae51-e4ce9565e582',
    'BACK_URLS': {
        'success': 'http://localhost:8000/usuarios/api/mercadopago/pago-exitoso/',
        'failure': 'http://localhost:8000/usuarios/api/mercadopago/pago-error/',
        'pending': 'http://localhost:8000/usuarios/api/mercadopago/pago-pendiente/'
    },
    'AUTO_RETURN': 'approved',
    'BINARY_MODE': False
}