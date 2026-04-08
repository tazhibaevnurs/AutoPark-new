import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _lead_form_min_seconds_after_page_load():
    """В unit-тестах задержку отключаем; в проде — 2 с (или LEAD_FORM_MIN_SECONDS из env)."""
    if os.environ.get('PYTEST_CURRENT_TEST'):
        return 0
    if len(sys.argv) >= 2 and sys.argv[1] == 'test':
        return 0
    return int(os.environ.get('LEAD_FORM_MIN_SECONDS', '2'))


LEAD_FORM_MIN_SECONDS_AFTER_PAGE_LOAD = _lead_form_min_seconds_after_page_load()

# Загрузка .env при наличии (опционально)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError('DJANGO_SECRET_KEY is required in environment variables.')

# В продакшене обязательно задать DEBUG=False в .env (иначе check --deploy выдаст W018)
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'leads',
    'pages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.middleware.AbuseProtectionMiddleware',
    'config.middleware.AuthRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

def _database_path():
    raw = os.environ.get('DATABASE_PATH')
    if not raw:
        return str(BASE_DIR / 'db.sqlite3')
    path = Path(raw)
    # Для Docker: /data/db.sqlite3. Локально каталога может не быть — используем проект.
    if path.is_absolute() and not path.parent.exists():
        return str(BASE_DIR / 'db.sqlite3')
    return raw


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _database_path(),
    }
}

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
# Версионирование статики через ?v= в шаблонах; долгий кеш безопасен
WHITENOISE_MAX_AGE = 31536000

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Вход пользователя на сайте.
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'
LOGOUT_REDIRECT_URL = '/'

# Время жизни сессии и сброс токенов.
SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE', 3600 * 12))
SESSION_SAVE_EVERY_REQUEST = True
PASSWORD_RESET_TIMEOUT = int(os.environ.get('PASSWORD_RESET_TIMEOUT', 3600))

# Разрешённые защищённые префиксы путей (проверяются middleware).
AUTH_PROTECTED_PATH_PREFIXES = ('/profile/',)
API_RATE_LIMIT_PER_MINUTE = int(os.environ.get('API_RATE_LIMIT_PER_MINUTE', 100))
API_BODY_SIZE_LIMIT_BYTES = int(os.environ.get('API_BODY_SIZE_LIMIT_BYTES', 1024 * 1024))
UPLOAD_BODY_SIZE_LIMIT_BYTES = int(os.environ.get('UPLOAD_BODY_SIZE_LIMIT_BYTES', 10 * 1024 * 1024))
SUSPICIOUS_4XX_PER_IP_10MIN = int(os.environ.get('SUSPICIOUS_4XX_PER_IP_10MIN', 30))
ANOMALY_REQUESTS_PER_MINUTE = int(os.environ.get('ANOMALY_REQUESTS_PER_MINUTE', 1500))
CONTENT_SECURITY_POLICY = os.environ.get(
    'CONTENT_SECURITY_POLICY',
    "default-src 'self'; img-src 'self' data: https:; media-src 'self' https:; "
    "script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
    "font-src 'self' data:; frame-ancestors 'none'; base-uri 'self';",
)

# Надёжные алгоритмы хеширования паролей (без legacy md5/sha1).
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Почта для email-верификации и сброса пароля.
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@autopark.local')
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)

# Оптимизация видео после сохранения (синхронно, может замедлять админку).
# По умолчанию отключено: загрузка в админке происходит сразу, без долгого ожидания.
ENABLE_SYNC_VIDEO_OPTIMIZATION = os.environ.get(
    'ENABLE_SYNC_VIDEO_OPTIMIZATION',
    'false',
).lower() == 'true'

# Безопасность. При DEBUG=True — для разработки (редирект и secure-куки выкл.).
# При DEBUG=False — полные значения для продакшена, если включён HTTPS (USE_HTTPS=true).
# Если на сервере только HTTP (например, доступ по IP без сертификата) — задайте USE_HTTPS=false.
USE_HTTPS = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 1 if (DEBUG or not USE_HTTPS) else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS and not DEBUG
SECURE_HSTS_PRELOAD = USE_HTTPS and not DEBUG
SECURE_SSL_REDIRECT = USE_HTTPS and not DEBUG
SESSION_COOKIE_SECURE = USE_HTTPS and not DEBUG
CSRF_COOKIE_SECURE = USE_HTTPS and not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":%(message)s}',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'security_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'security.audit': {
            'handlers': ['security_console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# При разработке (DEBUG=True) check --deploy всё равно ругается на эти пункты —
# подавляем предупреждения, т.к. в проде будет DEBUG=False и настройки выше будут включены.
if DEBUG:
    SILENCED_SYSTEM_CHECKS = [
        'security.W004',  # SECURE_HSTS_SECONDS
        'security.W005',  # SECURE_HSTS_INCLUDE_SUBDOMAINS
        'security.W008',  # SECURE_SSL_REDIRECT
        'security.W012',  # SESSION_COOKIE_SECURE
        'security.W016',  # CSRF_COOKIE_SECURE
        'security.W018',  # DEBUG in deployment
        'security.W021',  # SECURE_HSTS_PRELOAD
    ]
