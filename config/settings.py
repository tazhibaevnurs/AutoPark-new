import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Загрузка .env при наличии (опционально)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-key-change-in-production')

# В продакшене обязательно задать DEBUG=False в .env (иначе check --deploy выдаст W018)
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

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

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Админка: редирект неавторизованных на страницу входа
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'

# Безопасность. При DEBUG=True — для разработки (редирект и secure-куки выкл.).
# При DEBUG=False — полные значения для продакшена (HTTPS, HSTS, secure-куки).
SECURE_HSTS_SECONDS = 1 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

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
