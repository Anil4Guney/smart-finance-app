"""
Django settings for SmartFinance config project.
"""
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = os.path.join(BASE_DIR, '.env')

# 1. Aşama: Windows gizli karakterlerini aşmak için 'utf-8-sig' ile okumayı deniyoruz
load_dotenv(env_path, override=True, encoding='utf-8-sig')
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 2. Aşama: EĞER HALA BULAMADIYSA, KABA KUVVET İLE İÇİNDEN SÖKÜP ALIYORUZ!
if not GEMINI_API_KEY and os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            if 'GEMINI_API_KEY' in line:
                # Satırı eşittir'den böl, boşlukları ve tırnakları temizle
                GEMINI_API_KEY = line.split('=', 1)[1].strip().strip('\'"')
                os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

if GEMINI_API_KEY:
    # Google'ın kütüphanesi hata vermesin diye şifreyi onun istediği isme de kopyalıyoruz!
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

print("\n" + "="*40)
if GEMINI_API_KEY:
    print(" Şifre alındı!")
else:
    print("Dosyanın içi  boş olabilir mi?")
print("="*40 + "\n")


SECRET_KEY = 'django-insecure-change-this-in-production-smartfinance'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 3. Parti Uygulamalar
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'djoser',
    
    # Bizim Uygulamamız
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


# --- REST Framework Ayarları ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# --- JWT Ayarları ---
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# --- DİKKAT: DJOSER AYARLARI GÜNCELLENDİ! ---
DJOSER = {
    'SERIALIZERS': {
        # Artık Djoser'ın standart ayarlarını değil, bizim finance uygulamasındaki ayarları kullanacak!
        'user_create': 'finance.serializers.CustomUserCreateSerializer',
        'user': 'finance.serializers.CustomUserSerializer',
        'current_user': 'finance.serializers.CustomUserSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticated'],
    },
}

# --- CORS Ayarları ---
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True