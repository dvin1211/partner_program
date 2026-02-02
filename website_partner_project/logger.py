import os
import platform
from pathlib import Path 

def detect_os():
    """Определяем операционную систему"""
    system = platform.system().lower()
    
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':  # macOS
        return 'macos'
    else:
        return 'unknown'

def create_log_dirs(log_path):
    LOG_DIR.mkdir(exist_ok=True)
    os.makedirs(LOG_DIR / 'db', exist_ok=True)
    os.makedirs(LOG_DIR / 'errors', exist_ok=True)
    os.makedirs(LOG_DIR / 'apps', exist_ok=True)

try:
    from django.conf import settings
    
    BASE_DIR = settings.BASE_DIR
except (ImportError, AttributeError):
    BASE_DIR = Path(__file__).resolve().parent.parent

# Создаем папку для логов
system = detect_os()

if system == "windows":
    LOG_DIR = BASE_DIR / 'logs'
elif system == "macos":
    LOG_DIR = BASE_DIR / 'logs'
elif system == 'linux':
    LOG_DIR = Path('/var/log/django')
else:
    LOG_DIR = BASE_DIR / 'logs'

create_log_dirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # Форматирование (Как будут выводиться логи)
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
            'datefmt': '%d/%m/%y %H:%M:%S',
        },
        'detailed': {
            'format': '[{asctime}] {levelname} {name} {module}.{funcName}:{lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    
    # Обработчики (Куда будут записываться логи)
    'handlers': {
        # Консоль
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        # БД
        'database': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'db' / 'django.log',
            'formatter': 'simple',
        },

        # Приложения
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'apps' / 'django.log',
            'formatter': 'detailed',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'errors' / 'errors.log',
            'formatter': 'verbose',
        },
    },
    
    # Логгеры (Какие приложения логгировать)
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },

        # Мои приложения
        'advertisers': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'managers': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'partner_app': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'partners': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'partnerships': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'tracking': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

__all__ = ('LOGGING',)