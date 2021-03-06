import logging.config
import os
from datetime import timedelta

import django
import sentry_sdk
from celery.schedules import crontab
from ddtrace import Pin, config, patch_all, tracer
from django.urls import reverse_lazy
from django.utils.log import DEFAULT_LOGGING
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if 'DEV' in os.environ:
    CELERY_TASK_ALWAYS_EAGER = True  # Sync celery tasks in sync
    DEBUG = True

ENABLE_DEBUG_DRAWER_IN_DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY') if not DEBUG else 'DEBUG'

GIT_COMMIT = 'DEBUG' if DEBUG else os.environ.get('GIT_COMMIT')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',') if not DEBUG else []

INTERNAL_IPS = ['127.0.0.1']

USE_X_FORWARDED_HOST = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.postgres',
    'django.contrib.gis',

    'rest_framework',
    'rest_framework.authtoken',

    'django_filters',
    'drf_yasg',
    'rest_framework_tracking',
    'drf_multiple_model',

    'crispy_forms',
    'adminsortable2',
    'django_celery_results',

    'utils',
    'web',
    'management',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'django_extensions',
    'mapwidgets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'management.middleware.AssociateSheltersMiddleware',
]

AUTH_USER_MODEL = 'web.User'

# Datadog
tracer.configure(hostname='ddagent', port=8126, enabled=not DEBUG)
config.django['service_name'] = 'getpet-platform'
config.django['instrument_databases'] = True
config.django['instrument_caches'] = True
config.django['trace_query_string'] = True
config.django['analytics_enabled'] = True
tracer.set_tags({'env': 'production'})

if DEBUG and ENABLE_DEBUG_DRAWER_IN_DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

ROOT_URLCONF = 'getpet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'management.context_processors.user_shelters',
            ],
        },
    },
]

WSGI_APPLICATION = 'getpet.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
IS_POSTGRES_AVAILABLE = 'POSTGRES_DB' in os.environ and 'POSTGRES_USER' in os.environ and 'POSTGRES_PASSWORD' in os.environ

if DEBUG and not IS_POSTGRES_AVAILABLE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
            # <-- IMPORTANT: same name as docker-compose service!
            'PORT': '5432',
        }
    }

# https://lincolnloop.com/blog/django-logging-right-way/
# Disable Django's logging setup
LOGGING_CONFIG = None
LOGGER_HANDLERS = ['console']
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)-12s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # STDERR
            'formatter': 'verbose',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        '': {
            'level': 'WARNING',
            'handlers': LOGGER_HANDLERS,
        },
        'web': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'api': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        'management': {
            'level': 'INFO' if DEBUG else 'WARNING',
            'handlers': LOGGER_HANDLERS,
            'propagate': False,
        },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

# Sentry
SENTRY_SECRET = os.environ.get("SENTRY_SECRET", None)
SENTRY_PROJECT_ID = os.environ.get("SENTRY_PROJECT_ID", None)

if SENTRY_SECRET and SENTRY_PROJECT_ID:
    sentry_sdk.init(
        dsn=f"https://{SENTRY_SECRET}@sentry.io/{SENTRY_PROJECT_ID}",
        release=f"getpet-web@{GIT_COMMIT}",
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        send_default_pii=True,
    )

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'lt'

TIME_ZONE = 'Europe/Vilnius'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

SITE_ID = 1

# By default Django will upload to media with original file permissions. Fix this.
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

REDIS_URL = 'redis://%s:6379/' % os.environ.get('REDIS_PORT_6379_TCP_ADDR', '172.17.0.1')

CELERY_BROKER_URL = REDIS_URL + '2'
CELERY_RESULT_BACKEND = 'django-db'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

CELERY_BEAT_SCHEDULE = {
    'connect_super_users_to_shelters': {
        'task': 'web.tasks.connect_super_users_to_shelters',
        'schedule': timedelta(hours=1)
    },
    'sync_product_metrics': {
        'task': 'web.tasks.sync_product_metrics',
        'schedule': timedelta(minutes=15)
    },
    'randomize_pets_order': {
        'task': 'web.tasks.randomize_pets_order',
        'schedule': crontab(hour='4')
    },
    'randomize_shelters_order': {
        'task': 'web.tasks.randomize_shelters_order',
        'schedule': crontab(hour='4')
    },
}

CELERYD_TASK_SOFT_TIME_LIMIT = 45 * 60
CELERYD_SEND_EVENTS = True

CELERY_TASK_SEND_SENT_EVENT = True
CELERY_TRACK_STARTED = True

if not DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

DJANGORESIZED_DEFAULT_QUALITY = 90
DJANGORESIZED_DEFAULT_KEEP_META = False
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = False

CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_FAIL_SILENTLY = not DEBUG

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 500,
    'DATETIME_FORMAT': "%Y-%m-%dT%H:%M:%SZ",
}

BASE_REAL_DOMAIN = "https://www.getpet.lt/"
BASE_DOMAIN = BASE_REAL_DOMAIN if not DEBUG else "http://localhost:8000/"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

FIREBASE_KEY = os.path.join(BASE_DIR, 'keyfiles', 'firebase.json')
if not DEBUG and not os.path.exists(FIREBASE_KEY):
    raise RuntimeError("firebase.json file is missing. Make sure that it exists.")

# Phone
CONTACT_PHONE = os.environ.get('CONTACT_PHONE')

# E-Mail
EMAIL_FROM = os.environ.get('EMAIL')
EMAIL_TO = [EMAIL_FROM, ]
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_USE_SSL = True
EMAIL_HOST_USER = EMAIL_FROM
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Django all auth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy("management:index")
LOGIN_REDIRECT_URL = reverse_lazy("management:index")
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_FORMS = {
    'login': 'management.forms.LoginForm',
    'signup': 'management.forms.SignupForm',
    'reset_password': 'management.forms.ResetPasswordForm',
}
SOCIALACCOUNT_FORMS = {
    'signup': 'management.forms.SocialSignupForm',
}
SOCIALACCOUNT_QUERY_EMAIL = True

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

ACCOUNT_ADAPTER = 'management.adapters.GetPetAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'management.adapters.GetPetSocialAccountAdapter'

DATADOG_SETTINGS = {
    'host_name': os.environ.get('DATADOG_HOSTNAME', None),
    'api_key': os.environ.get('DATADOG_API_KEY', None),
    'app_key': os.environ.get('DATADOG_APP_KEY', None),
}

MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocation", [54.687157, 25.279652]),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'lt'}}),
        ("markerFitZoom", 12),
    ),
    "GOOGLE_MAP_API_KEY": os.environ.get("GOOGLE_MAP_API_KEY")
}

# Datadog finalization
patch_all()
Pin.override(Pin.get_from(django))
