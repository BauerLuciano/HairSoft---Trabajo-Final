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
    'usuarios.middleware.DisableCSRFMiddleware',  # Deshabilitar CSRF
    'django.middleware.common.CommonMiddleware',   
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
        },
        'CONN_MAX_AGE': 0,  # Persistencia de conexiones
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

# 🚨 CONFIGURACIÓN CORS EXTREMA 🚨
CORS_ALLOW_ALL_ORIGINS = True  # Permitir todos los orígenes en desarrollo
CORS_ALLOW_CREDENTIALS = True  # Permitir cookies

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# 🚨 CONFIGURACIÓN CSRF EXTREMA 🚨
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Deshabilitar CSRF completamente en desarrollo
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Configuración de sesión
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Headers permitidos para CORS
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
]

# Métodos permitidos para CORS
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

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
    # ✅ Access Token de producción dentro de cuenta de prueba
    'ACCESS_TOKEN': 'APP_USR-7404896415144376-102322-584184e7db9ca5b628be4d7e21763ae3-2943677918',
    
    # ✅ Public Key (para frontend si necesitas Bricks / Checkout)
    'PUBLIC_KEY': 'APP_USR-4e145215-f26e-4c2d-8be7-a557300a9154',
    
    # URLs de retorno luego del pago
    'BACK_URLS': {
        'success': 'http://localhost:5173/pago-exitoso',
        'failure': 'http://localhost:5173/pago-error',
        'pending': 'http://localhost:5173/pago-pendiente'
    },
    
    # Auto return si el pago se aprueba
    'AUTO_RETURN': 'approved',
    
    # Binary mode True = solo aprobado o rechazado
    'BINARY_MODE': True,
    
    # Opcional: si querés habilitar sandbox explícitamente (aunque SDK detecta init_point)
    'SANDBOX': True
}


# ================================
# CONFIGURACIÓN REST FRAMEWORK
# ================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# Desactivar logs del admin para evitar el error
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}