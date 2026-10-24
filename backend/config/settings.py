"""
Django settings for SmartFinance.

All secrets and environment-specific values come from environment variables
(or backend/.env in local development). See .env.example.
"""
import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# utf-8-sig strips the BOM that some Windows editors add to .env files.
load_dotenv(BASE_DIR / '.env', encoding='utf-8-sig')


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=''):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


# --- Core security ---
DEBUG = env_bool('DJANGO_DEBUG', default=False)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-local-development-only'
    else:
        raise ImproperlyConfigured('DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is off.')

ALLOWED_HOSTS = env_list(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,smart-finance-app-6lgi.onrender.com',
)

# --- AI ---
# GEMINI_API_KEY is the main name; GOOGLE_API_KEY is accepted for older .env files.
GEMINI_API_KEY = (
    os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY') or ''
).strip().strip('\'"')

# Gemini model for chat and receipts. 'gemini-flash-latest' always points at Google's
# current Flash model, so the app keeps working when old versions are retired.
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-flash-latest')

# Largest receipt image accepted by /api/scan-receipt/ (bytes).
MAX_RECEIPT_UPLOAD_BYTES = 5 * 1024 * 1024

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'djoser',

    'finance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Production must set DATABASE_URL (PostgreSQL). SQLite is for local development only:
# on hosts like Render its file is wiped on every restart.
# An empty DATABASE_URL= line in .env also falls back to SQLite.
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', '').strip() or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
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
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Limits for the endpoints that call Gemini (each call costs money).
    'DEFAULT_THROTTLE_RATES': {
        'ai_chat': os.environ.get('AI_CHAT_RATE', '30/hour'),
        'receipt_scan': os.environ.get('RECEIPT_SCAN_RATE', '20/hour'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'finance.serializers.CustomUserCreateSerializer',
        'user': 'finance.serializers.CustomUserSerializer',
        'current_user': 'finance.serializers.CustomUserSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticated'],
    },
}

# --- CORS: only these front-end origins may call the API ---
CORS_ALLOWED_ORIGINS = env_list(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000,https://smart-finance-app-kohl.vercel.app',
)
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# --- Extra hardening when running in production ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
