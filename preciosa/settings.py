import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = [
    # ("Your Name", "your_email@example.com"),
]

MANAGERS = ADMINS

# esta configuración es apta para Travis CI.
# modificá tu local_settings.py para la configuración de tu entorno
DATABASES = {
    'default': {
        'ENGINE':'django.contrib.gis.db.backends.postgis',
        'NAME': 'preciosa',
        'USER': 'postgres',      # 'dev' si seguiste el tutorial textualmente
        'PASSWORD': '',          # 'dev' si seguiste el tutorial textualmente
        'HOST': '127.0.0.1',
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

SITE_ID = int(os.environ.get("SITE_ID", 1))

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
USE_TZ = True

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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "account.context_processors.account",
    "pinax_theme_bootstrap.context_processors.theme",
    "preciosa.context_processors.menu"
]


MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "preciosa.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "preciosa.wsgi.application"

TEMPLATE_DIRS = [
    os.path.join(PACKAGE_ROOT, "templates"),
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    'django.contrib.humanize',

    # theme
    "bootstrapform",
    "pinax_theme_bootstrap",
    "pinax_theme_bootstrap_account",

    # external
    "annoying",
    "account",
    "metron",
    "eventlog",
    "treebeard",
    "django_extensions",
    "cities_light",
    "autocomplete_light",
    "easy_thumbnails",
    "image_cropping",
    "rest_framework",

    # community and stats
    "feedback",
    "analytical",

    # migrations/deploy
    "south",
    "dbbackup",

    # tests
    "django_nose",


    #blog
    "radpress",

    #newsletter
    'imperavi',
    'sorl.thumbnail',
    'newsletter',

    # project
    "preciosa",
    "preciosa.precios",
    "preciosa.voluntarios",
    "preciosa.api",
]

# compatibilidad con class="alert" de bootstrap 3
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger'
}

from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
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
        },
    },
    "loggers": {
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

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = False
ACCOUNT_LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2

AUTHENTICATION_BACKENDS = [
    "account.auth_backends.UsernameAuthenticationBackend",
]

# See http://django-newsletter.readthedocs.org/en/latest/installation.html
NEWSLETTER_CONFIRM_EMAIL = False
NEWSLETTER_RICHTEXT_WIDGET = "imperavi.widget.ImperaviWidget"

# django-db backups
DBBACKUP_STORAGE = 'dbbackup.storage.filesystem_storage'
DBBACKUP_FILESYSTEM_DIRECTORY = os.path.join(PROJECT_ROOT, 'backups')

THUMBNAIL_ALIASES = {
    '': {
        '70x70': dict(size=(70, 70), quality=75, crop="center"),
    }
}

REST_FRAMEWORK = {
    'PAGINATE_BY': 30,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100
}





try:
    from local_settings import *    # noqa
except:
    pass


