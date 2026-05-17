import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'


def _load_env_file(path):
    """Load KEY=VALUE pairs from a local .env file without extra dependencies."""
    if not path.exists():
        return

    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        if not key or key in os.environ:
            continue

        value = value.strip()
        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {'"', "'"}
        ):
            value = value[1:-1]

        os.environ[key] = value


def _get_bool_env(name, default):
    value = os.environ.get(name)
    if value is None or value.strip() == '':
        return default

    normalized = value.strip().lower()
    if normalized in {'1', 'true', 't', 'yes', 'y', 'on'}:
        return True
    if normalized in {'0', 'false', 'f', 'no', 'n', 'off'}:
        return False

    raise ImproperlyConfigured(
        f'{name} must be a boolean value: true or false.'
    )


def _get_list_env(name):
    return [
        value.strip()
        for value in os.environ.get(name, '').split(',')
        if value.strip()
    ]


_load_env_file(ENV_FILE)

DEBUG = _get_bool_env('DJANGO_DEBUG', default=True)

DEVELOPMENT_SECRET_KEY = 'django-insecure-development-only-change-me'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '').strip()

if DEBUG and not SECRET_KEY:
    SECRET_KEY = DEVELOPMENT_SECRET_KEY

if (
    not DEBUG
    and SECRET_KEY in {'', 'your-secret-key-here', DEVELOPMENT_SECRET_KEY}
):
    raise ImproperlyConfigured(
        'Set DJANGO_SECRET_KEY to a unique value when DJANGO_DEBUG=False.'
    )

ALLOWED_HOSTS = _get_list_env('DJANGO_ALLOWED_HOSTS')

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        'Set DJANGO_ALLOWED_HOSTS to at least one host when DJANGO_DEBUG=False.'
    )

INSTALLED_APPS = [
    'exchange',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

AUTH_USER_MODEL = 'exchange.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SwapSpot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'SwapSpot.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Path to the SQLite database file
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

LOGIN_URL = '/login/'