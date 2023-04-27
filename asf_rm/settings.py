"""
Django settings for asf_rm project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/


if "POSTGRES_NAME" environment variable defined, the database engine is posgresql
and the other env variables are POSGRES_USER, POSTGRES_PASSWORD, DB_HOST, DB_PORT
else it is sqlite, and no env variable is required

"""

from pathlib import Path
import os
import json
from urllib.parse import urlparse

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

print("BASE_DIR:", BASE_DIR)

with open(BASE_DIR / 'asf_rm/VERSION') as f:
    VERSION = f.read().strip()
    print(f'MIRA Version: {VERSION}')

try:
    with open(BASE_DIR / 'asf_rm/build.json') as f:
        BUILD = json.load(f)['build']
except FileNotFoundError:
    BUILD = 'unset'
    print('MIRA Build: unset. Please refer to the documentation to set it.')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'

MIRA_URL = os.environ['MIRA_URL']
ALLOWED_HOSTS = [urlparse(MIRA_URL).hostname]
CSRF_TRUSTED_ORIGINS = [MIRA_URL]

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error'] # see https://developers.google.com/recaptcha/docs/faq

PAGINATE_BY = os.environ.get('PAGINATE_BY', default=1000)


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'django.forms',
    'fieldsets_with_inlines',
    'tailwind',
    'theme',
    'iam',
    'core',
    'cal',
    'django_filters',
    'library',
    'serdes',
    'passkeys',
]

if RECAPTCHA_PUBLIC_KEY:
    INSTALLED_APPS.append('captcha')
    print("recaptcha enabled")
else:
    print("recaptcha disabled")


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'asf_rm.urls'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

SESSION_COOKIE_AGE = int(os.environ.get('SESSION_COOKIE_AGE', default=60*15))  # defaults to 15 minutes
SESSION_SAVE_EVERY_REQUEST = os.environ.get('SESSION_SAVE_EVERY_REQUEST', default=True) # prevents session from expiring when user is active
SESSION_EXPIRE_AT_BROWSER_CLOSE = os.environ.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=True)

MIRA_SUPERUSER_EMAIL = os.environ.get('MIRA_SUPERUSER_EMAIL')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
# rescue mail
EMAIL_HOST_RESCUE = os.environ.get('EMAIL_HOST_RESCUE')
EMAIL_PORT_RESCUE = os.environ.get('EMAIL_PORT_RESCUE')
EMAIL_HOST_USER_RESCUE = os.environ.get('EMAIL_HOST_USER_RESCUE')
EMAIL_HOST_PASSWORD_RESCUE = os.environ.get('EMAIL_HOST_PASSWORD_RESCUE')
EMAIL_USE_TLS_RESCUE = os.environ.get('EMAIL_USE_TLS_RESCUE')

EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', default="5")) # seconds

## Licence management
LICENCE_DEPLOYMENT = os.environ.get('LICENCE_DEPLOYMENT', default="On-premises")
LICENCE_TYPE = os.environ.get('LICENCE_TYPE', default="Standard")
LICENCE_SUPPORT = os.environ.get('LICENCE_SUPPORT', default="Standard")
LICENCE_EXPIRATION = os.environ.get('LICENCE_EXPIRATION', default="-")


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "core/templates",
            ],
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

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

WSGI_APPLICATION = 'asf_rm.wsgi.application'

AUTH_USER_MODEL = 'iam.User'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('en','English'),
    ('fr', 'French'),
]

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, '../locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = BASE_DIR / 'staticfiles'   # for collectstatic
STATICFILES_DIRS = [
    BASE_DIR / "static",  # the js files are here
]

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = [
    "127.0.0.1",
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


if 'POSTGRES_NAME' in os.environ:
    print("Postgresql database engine")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['POSTGRES_NAME'],
            'USER': os.environ['POSTGRES_USER'],
            'PASSWORD': os.environ['POSTGRES_PASSWORD'],
            'HOST': os.environ['DB_HOST'],
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
    print("Postgresql database engine")
else:
    print("sqlite database engine")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db/mira.sqlite3",
        }
    }

AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend'] 
FIDO_SERVER_ID=urlparse(MIRA_URL).hostname
FIDO_SERVER_NAME="FidoMira"
# leave KEY_ATTACHMENT undefined to allow both platform and roaming authenticators

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]
