from dotenv import load_dotenv

import os
from pathlib import Path
import warnings
import platform

from website_partner_project.logger import LOGGING



load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG",'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')


LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L10N = True
USE_TZ = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles'
    ]

# Third-party apps
INSTALLED_APPS += ['rest_framework',
    'django_celery_results',
    'django.contrib.humanize',
    'corsheaders',
    "django_vite"
    ]
    
# My apps
INSTALLED_APPS += [
    'apps.core',
    'apps.users',
    'apps.partners',
    'apps.advertisers',
    'apps.managers',
    'apps.partnerships',
    'apps.tracking',
    'apps.partner_app',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.core.api_authentication.AdvertiserAPIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

CSRF_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'
CSRF_COOKIE_NAME = 'XSRF-TOKEN'


CSRF_TRUSTED_ORIGINS = [
    os.getenv('TRUSTED_ORIGINS')
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    os.getenv("TRUSTED_ORIGINS")
]


STATIC_URL = os.getenv("STATIC_URL")

# Name of our static files' folder (after called python manage.py collectstatic)
STATIC_ROOT = os.getenv("STATIC_ROOT")

# Include DJANGO_VITE_ASSETS_PATH into STATICFILES_DIRS to be copied inside
# when run command python manage.py collectstatic

STATICFILES_DIRS = [
  BASE_DIR / "assets",
]

AUTH_USER_MODEL  = 'users.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # My middlewares
    'apps.core.middleware.AdminAccessMiddleware'
]

ROOT_URLCONF = 'website_partner_project.urls'

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

WSGI_APPLICATION = 'website_partner_project.wsgi.application'

warnings.filterwarnings('ignore', category=UserWarning, message='.*order.*')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST':os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
    }
}

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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'


USE_TZ = True

CSRF_COOKIE_HTTPONLY = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJANGO_VITE = {
  "default": {
    "manifest_path": os.getenv('MANIFEST_SETTINGS_PATH'),
    "dev_mode": os.getenv('VITE_DEV_MODE','False') == 'True'
  },
}

PARTNER_PAYOUT_SETTINGS = {
    'min_amount': os.getenv('MIN_AMOUNT'),
    'fee_percent': os.getenv('FEE_PERCENT'),
    'payment_methods': [
        {'id': 'bank_card', 'name': 'Банковская карта'}
    ]
}

IS_WINDOWS = platform.system().lower() == 'windows'

# Celery settings
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = [os.getenv('CELERY_ACCEPT_CONTENT')]
CELERY_TASK_SERIALIZER = os.getenv('CELERY_ACCEPT_CONTENT')
CELERY_RESULT_SERIALIZER = os.getenv('CELERY_ACCEPT_CONTENT')
CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE')


if IS_WINDOWS:
    CELERY_WORKER_POOL = 'eventlet'
CELERY_WORKER_CONCURRENCY = 4

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')  # SMTP-сервер Mail.ru
EMAIL_PORT = os.getenv('EMAIL_PORT')  # Для SSL
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')  # Обязательно для Mail.ru
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Полный email
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Пароль от почты или пароль приложения
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')  # Email отправителя