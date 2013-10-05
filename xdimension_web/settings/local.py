from __future__ import absolute_import

from .common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEPLOY_MODE = 'local'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'xdimension_web',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

ADMINS = (
    ('marco', 'marco@credra.com'),
)

MANAGERS = ADMINS

MEDIA_ROOT = '.assets/media/'
MEDIA_URL = '/media/'

STATIC_ROOT = '.assets/static/'
STATIC_URL = '/static/%s/' % STATIC_VERSION

REST_API_DOCS_ENABLE = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

