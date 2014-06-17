from __future__ import absolute_import

import dj_database_url
import os

from .common import *

DATABASES = {
    'default': dj_database_url.config()
    }

# Django cache
CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': os.environ.get('MEMCACHIER_SERVERS').replace(',', ';'),
        'TIMEOUT': 500,
        'BINARY': True,
        'VERSION': 1,
        }
    }

# Bypass django cache configuration to contact pylibmc directly
os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '')\
    .replace(',', ';')
os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')


ADMINS = (
    # TODO: fetch admin emails somehow...
    #('user', 'user@example.com'),
)

MANAGERS = ADMINS

INSTALLED_APPS += ('storages',)

# AWS credentials (for both static and media)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_STORAGE_DOMAIN = os.environ.get('AWS_STORAGE_DOMAIN')
# allows conditional upload (needs dateutil)
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False  # Or else CORS will break
AWS_S3_FILE_OVERWRITE = False

# media files (images uploaded by users)
AWS_LOCATION = 'media'  # this only impacts unversioned storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
MEDIA_URL = 'https://%s.s3.amazonaws.com/%s/' % (
    AWS_STORAGE_BUCKET_NAME,
    AWS_LOCATION)

# static assets
AWS_VERSIONED_LOCATION = 'static'  # this only impacts versioned storage
STATICFILES_STORAGE = 'versioned_storages.backends.s3boto.S3BotoStorage'
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/%s/' % (
    AWS_STORAGE_BUCKET_NAME,
    AWS_VERSIONED_LOCATION,
    STATIC_VERSION)

# email (sendgrid)
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = '587'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_HOST_USE_TLS = True
