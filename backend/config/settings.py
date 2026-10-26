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
# The chat uses the lighter, faster model; receipts keep the more accurate one.
GEMINI_CHAT_MODEL = os.environ.get('GEMINI_CHAT_MODEL', 'gemini-flash-lite-latest')
# Per request to Gemini, and the most time one user request may spend on retries/fallbacks
# (the web server kills requests after 120 s)
AI_REQUEST_TIMEOUT_SECONDS = int(os.environ.get('AI_REQUEST_TIMEOUT_SECONDS', '20'))
AI_TOTAL_BUDGET_SECONDS = int(os.environ.get('AI_TOTAL_BUDGET_SECONDS', '45'))
# Hard cap on Gemini calls per day across all users (cost / quota protection). 0 = no cap.
AI_DAILY_CALL_LIMIT = int(os.environ.get('AI_DAILY_CALL_LIMIT', '2000'))

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
    'rest_framework_simplejwt.token_blacklist',  # logout / rotated refresh tokens stop working
    'corsheaders',
    'djoser',

    'finance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serves the admin's static files in production
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
        # Serverless Postgres (Neon) drops idle connections; check before reuse instead of failing the request
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'tr'  # validation errors reach users in Turkish
TIME_ZONE = 'Europe/Istanbul'  # 'today' and monthly billing follow Turkish dates
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
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
        # Failed-or-not login attempts per username (slows password guessing)
        'login': os.environ.get('LOGIN_RATE', '20/hour'),
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

DJOSER = {
    # We use JWT only; without this, deleting an account crashes looking for DRF's (unused) token table
    'TOKEN_MODEL': None,
    'SERIALIZERS': {
        'user_create': 'finance.serializers.CustomUserCreateSerializer',
        'user': 'finance.serializers.CustomUserSerializer',
        'current_user': 'finance.serializers.CustomUserSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticated'],
        # No e-mail sending is set up: keep activation / reset flows closed instead of failing with 500s
        'activation': ['rest_framework.permissions.IsAdminUser'],
        'password_reset': ['rest_framework.permissions.IsAdminUser'],
        'password_reset_confirm': ['rest_framework.permissions.IsAdminUser'],
        'username_reset': ['rest_framework.permissions.IsAdminUser'],
        'username_reset_confirm': ['rest_framework.permissions.IsAdminUser'],
        'set_username': ['rest_framework.permissions.IsAdminUser'],
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
    # Tell browsers to use HTTPS only (30 days; raise it once everything is confirmed to work)
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', 60 * 60 * 24 * 30))
    # Hosts like Render already redirect http -> https at the edge; turn this on if yours does not
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SSL_REDIRECT', default=False)

# --- Logging: without this, server errors (500) are NOT printed in production ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'plain': {'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'plain'},
    },
    'root': {'handlers': ['console'], 'level': os.environ.get('LOG_LEVEL', 'INFO')},
    'loggers': {
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': False},
        'django.security': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
    },
}
