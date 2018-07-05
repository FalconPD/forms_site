import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ALLOWED_HOSTS = ['.herokuapp.com', 'localhost', '.elasticbeanstalk.com']

# Application definition

INSTALLED_APPS = [
    'field_trips.apps.FieldTripsConfig',
    'widget_tweaks',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.microsoft',
    'url_tools',
    'django_s3_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'forms_site.urls'

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
            'libraries': {
                'calendar': 'templatetags.calendar',
                'getattr': 'templatetags.getattr',
            },
        },
    },
]

WSGI_APPLICATION = 'forms_site.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postresql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.enviorn['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'forms_site',
            'USER': 'forms_site',
            'HOST': 'localhost',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 1
SOCIALACCOUNT_ADAPTER = 'forms_site.adapters.OverrideSocialAccountAdapter'
LOGIN_URL = '/accounts/microsoft/login'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
TEMPLATE_CONTEXT_PROCESSORS = (
    'url_tools.context_processors.current_url',
)

# django-s3-storage settings
DEFAULT_FILE_STORAGE = 'django_s3_storage.storage.S3Storage'
STATICFILES_STORAGE = 'django_s3_storage.storage.StaticS3Storage'
STATIC_URL = 'http://s3.amazonaws.com/' + os.getenv('AWS_S3_BUCKET_NAME') + '/'

AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_ADDRESSING_STYLE = 'auto'
AWS_S3_BUCKET_AUTH = True
AWS_S3_MAX_AGE_SECONDS = 60 * 60
AWS_S3_KEY_PREFIX = 'media'

AWS_S3_BUCKET_NAME_STATIC = os.getenv('AWS_S3_BUCKET_NAME')
AWS_S3_BUCKET_AUTH_STATIC = False
AWS_S3_KEY_PREFIX_STATIC = 'static'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Heroku settings
#import django_heroku
#django_heroku.settings(locals(), staticfiles=False)
