"""
Django settings for BlinkChat backend.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# ALLOWED_HOSTS: from env, and on Vercel add .vercel.app so DisallowedHost doesn't block
_allowed = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if os.environ.get('VERCEL_URL'):
    _allowed.append(os.environ.get('VERCEL_URL').strip())
    _allowed.append('.vercel.app')  # allow *.vercel.app
ALLOWED_HOSTS = [h.strip() for h in _allowed if h.strip()]

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
ASGI_APPLICATION = 'config.asgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS for Next.js frontend
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

# REST Framework & JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
}

from datetime import timedelta
_jwt_signing_key = os.environ.get('JWT_SECRET') or SECRET_KEY
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'SIGNING_KEY': _jwt_signing_key,
}

# Channels - Redis as channel layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')]},
    }
}

# Redis URL for matchmaking queue (can use same Redis)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379')

# MongoDB for match logs (optional); MONGODB_URI or MONGO_URI
MONGO_URI = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI', 'mongodb://127.0.0.1:27017')
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'blinkchat')

# Port for ASGI (Daphne); use PORT from host (e.g. Vercel/Railway) or default 8000
PORT = int(os.environ.get('PORT', '8000'))
