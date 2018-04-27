# -*- coding: utf-8 -*-
import os


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
# TEMPLATE_DEBUG = DEBUG

ADMINS = [
    # ("Your Name", "your_email@example.com"),
]

MANAGERS = ADMINS


SITE_ID = int(os.environ.get("SITE_ID", 1))


# esta configuración es apta para Travis CI.
# modificá tu local_settings.py para la configuración de tu entorno
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',      # 'dev' si seguiste el tutorial textualmente
        # 'PASSWORD': 'dev',          # 'dev' si seguiste el tutorial textualmente
        'HOST': 'postgres',     #127.0.0.1',
        'PORT': '5432',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "es-ES"

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

LOCALE_PATHS = (
    os.path.join(PACKAGE_ROOT, 'locale'),
)
# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/site_media/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(PACKAGE_ROOT, "static"),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = "0u06gl%=^$%!4_0*jrp^w-6#xle1w*yh%^qpg9$%zw4hd#yu_^"

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "corsheaders.middleware.CorsMiddleware"
]

ROOT_URLCONF = "preciosa.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "preciosa.wsgi.application"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PACKAGE_ROOT, "templates"),
        ],
        # 'APP_DIRS': True,
        # 'DEBUG': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:

                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                "account.context_processors.account",
                "pinax_theme_bootstrap.context_processors.theme",
                "preciosa.context_processors.menu",
            ],
            'loaders': [
                # insert your TEMPLATE_LOADERS here
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ]
        },
    },
]

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'easy_thumbnails.processors.scale_and_crop',  # disable this one
    'easy_thumbnails.processors.filters',
)
THUMBNAIL_DEBUG = True

# TEMPLATE_DIRS = [
#     os.path.join(PACKAGE_ROOT, "templates"),
# ]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.postgres",
    "django.contrib.gis",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
    'django.contrib.flatpages',


    # # theme
    "bootstrapform",
    "pinax_theme_bootstrap",
    "pinax_theme_bootstrap_account",

    # # external
    "annoying",
    "account",
    "metron",
    "eventlog",
    "treebeard",
    "django_extensions",
    "cities_light",
    "dal",
    "dal_select2",

    "easy_thumbnails",
    "image_cropping",
    "floppyforms",

    # community and stats
    "feedback",
    "analytical",

    # migrations/deploy
    "dbbackup",

    # tests / debug
    "django_nose",

    # api
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",

    # blog
    "radpress",

    'django_summernote',

    # project
    "preciosa",
    "preciosa.precios",
    "preciosa.voluntarios",
    "preciosa.datos",
    "preciosa.acuerdos",
    "preciosa.api",
    "preciosa.flatpagex"
]

import sys


# compatibilidad con class="alert" de bootstrap 3
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger'
}

from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
    'easy_thumbnails.processors.filters',
) + thumbnail_settings.THUMBNAIL_PROCESSORS

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT, "preciosa.log"),
            'maxBytes': '16777216', # 16megabytes
            'formatter': 'simple'
        },
    },
    "loggers": {
        "main": {
            "handlers": ["console", "logfile"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        'cities_light': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'imports': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}


RADPRESS_TITLE = 'Preciosa | Blog'
RADPRESS_DESCRIPTION = "El blog del proyecto Preciosa"
RADPRESS_LIMIT = 5
RADPRESS_DISQUS = 'preciosa'
RADPRESS_HIDE_EMAIL = True


CITIES_LIGHT_TRANSLATION_LANGUAGES = ['es']
CITIES_LIGHT_CITY_SOURCES = ['http://download.geonames.org/export/dump/AR.zip']


FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

# los command managers de la app 'datos' crean archivos en esta carpeta
DATASETS_ROOT = os.path.join(PROJECT_ROOT, "datasets")


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGIN_URL = 'account_login'
ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = False
ACCOUNT_LOGIN_REDIRECT_URL = "voluntarios_dashboard"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2

AUTHENTICATION_BACKENDS = [
    "account.auth_backends.UsernameAuthenticationBackend",
]

# See http://django-newsletter.readthedocs.org/en/latest/installation.html
NEWSLETTER_CONFIRM_EMAIL = False
NEWSLETTER_RICHTEXT_WIDGET = "django_summernote.widgets.SummernoteInplaceWidget"

# django-db backups
DBBACKUP_STORAGE = 'dbbackup.storage.filesystem_storage'
DBBACKUP_FILESYSTEM_DIRECTORY = os.path.join(PROJECT_ROOT, 'backups')

THUMBNAIL_ALIASES = {
    '': {
        '70x70': dict(size=(70, 70), quality=75, crop="center"),
        'small': dict(size=(50, 50), quality=75, crop="center"),
    }
}

REST_FRAMEWORK = {
    'PAGINATE_BY': 30,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_jsonp.renderers.JSONPRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'preciosa.api.authentication.QueryTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # 'DEFAULT_THROTTLE_CLASSES': (
    #     'rest_framework.throttling.AnonRateThrottle',
    #     'preciosa.api.throttling.AntiAnsiososThrottle',
    #     'preciosa.api.throttling.AntiPerseverantesThrottle',
    # ),
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '30/day',      # anonimamente somos poco permisivos
    #     'anti_ansiosos': '40/min',
    #     'anti_perseverantes': '1000/day',
    # }
}

# usuarios que no tienen THROTTLING
MAGIC_TOKENS = []

# enable cross-site requests from any host
CORS_ORIGIN_ALLOW_ALL = True

# este codigo es de mentira. configurá el tuyo en local_settings.py
GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-123456-1'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['-s', '--nologcapture', '--nocapture',
             '--with-id', '--logging-clear-handlers']


try:
    from local_settings import *    # noqa
except:
    pass

if SITE_ID > 1:
    # APPS solo en produccion y dev

    INSTALLED_APPS = INSTALLED_APPS + [
        # ...
        'raven.contrib.django.raven_compat',
        'djrill'
    ]
