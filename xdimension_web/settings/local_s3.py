from __future__ import absolute_import

import os

from .local import *

INSTALLED_APPS += ('storages',)

# AWS credentials (for both static and media)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY  = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_STORAGE_DOMAIN = os.environ.get('AWS_STORAGE_DOMAIN')
# allows conditional upload (needs dateutil)
AWS_PRELOAD_METADATA = True
AWS_IS_GZIPPED = True
GZIP_CONTENT_TYPES = (
    'text/css',
    'application/javascript',
    'application/x-javascript',
    'image/svg+xml',
)

# media files (images uploaded by users)
AWS_LOCATION = 'media' # this only impacts unversioned storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
MEDIA_URL = 'https://%s.s3.amazonaws.com/%s/' % (
    AWS_STORAGE_BUCKET_NAME,
    AWS_LOCATION)

# static assets
AWS_VERSIONED_LOCATION = 'static' # this only impacts versioned storage
STATICFILES_STORAGE = 'versioned_storages.backends.s3boto.S3BotoStorage'
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/%s/' % (
    AWS_STORAGE_BUCKET_NAME,
    AWS_VERSIONED_LOCATION,
    STATIC_VERSION)
