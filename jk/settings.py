# -*- coding: utf-8 -*-


"""
Django settings for jinneng project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

# for django-pagination, very COOL!
from django.conf import global_settings

DJANGO_DEBUG = os.environ.get('DJANGO_DEBUG')
DEPLOY_TYPE = os.environ.get("DEPLOY_TYPE", "dev")
DB_USER = os.environ.get("DJANGO_DB_USER")
DB_PWD = os.environ.get("DJANGO_DB_PWD")
DB_HOST = os.environ.get("DJANGO_DB_HOST")
DB_PORT = os.environ.get("DJANGO_DB_PORT")
REDIS_HOST = os.environ.get("DJANGO_REDIS_HOST")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's+3msph#0v4o=fvu^*i!42hrp^w5(j6sr#kis@)=8^q3p3=+*m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DJANGO_DEBUG
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']


# Application definition


INSTALLED_APPS = (
    'django_admin_bootstrapped.bootstrap3',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.humanize',
    # The Django sites framework is required
    'django.contrib.sites',

    # custom packages
    'widget_tweaks',  # https://github.com/kmike/django-widget-tweaks/
    'storages',  # django-storage
    's3_folder_storage',  # django-s3-folder-storage
    'compressor',  # django_compressor
    'django_filters',  # django-filters
    'pagination_bootstrap',  # django-pagination-bootstrap
    'crispy_forms',  # django-crispy-forms
    'social.apps.django_app.default',  # python-social-auth
    'localflavor',  # django-localflavor
    'rest_framework',  # djangorestframework
    'tastypie',  # django-tastypie
    'corsheaders',
    'djangular',  # django-angular
    'el_pagination',  # django-el-pagination
    'stock',  # stock
)

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # django-pagination-bootstrap
    'pagination_bootstrap.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'jk.urls'

WSGI_APPLICATION = 'jk.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jk',
        'USER': DB_USER,
        'PASSWORD': DB_PWD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),
                    )
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    'compressor.finders.CompressorFinder',
)

# crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

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
                'django.template.context_processors.request',
            ],
        },
    },
]
# for django-allauth
SITE_ID = 1


# LOGIN LOGOUT
LOGIN_URL = '/jk/login'
LOGOUT_URL = '/jk/home'

# libsass "pip install django-libsass"
COMPRESS_ENABLED = True
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# django-debug-toolbar
#DEBUG_TOOLBAR_PATCH_SETTINGS = False
CONFIG_DEFAULTS = {
    'JQUERY_URL': False
}

# django-devserver
if DEPLOY_TYPE == 'dev':
    DEVSERVER_MODULES = (
        'devserver.modules.sql.SQLRealTimeModule',
        'devserver.modules.sql.SQLSummaryModule',
        'devserver.modules.profile.ProfileSummaryModule',

        # Modules not enabled by default
        'devserver.modules.ajax.AjaxDumpModule',
        'devserver.modules.profile.MemoryUseModule',
        'devserver.modules.cache.CacheSummaryModule',
        'devserver.modules.profile.LineProfilerModule',
    )
    # profiles all views without the need of function decorator
    DEVSERVER_AUTO_PROFILE = False

# S3 storages

if DEPLOY_TYPE == 'dev':
    STATIC_ROOT = '/var/www/static'
    MEDIA_ROOT = '/var/www/media'
    MEDIA_URL = 'http://localhost/media/'
elif DEPLOY_TYPE == 'production':
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'

    DEFAULT_S3_PATH = "media"
    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME

    STATIC_S3_PATH = "static"
    STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = '//s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

    #STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Celery redis
# CELERY SETTINGS
BROKER_URL = 'redis://%s:6379/0' % REDIS_HOST

# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# Just ignore the results, in case you're not consuming results.
CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = False

# django-debug-toolbar
INTERNAL_IPS = ('127.0.0.1',)

# cache: https://github.com/django-pylibmc/django-pylibmc
# CACHES = {
#     'default': {
#         'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
#         'LOCATION': 'localhost:11211',
#         'TIMEOUT': 500,
#         'BINARY': True,
# 'OPTIONS': {  # Maps to pylibmc "behaviors"
#             'tcp_nodelay': True,
#             'ketama': True
# }
#     }
# }

# python social auth
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# django-restframework
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}
