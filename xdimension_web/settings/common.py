# Common settings

import os

DEPLOY_MODE = os.environ.get('DEPLOY_MODE', 'local')

assert DEPLOY_MODE in ('local', 'staging', 'production')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'yes', 'true')

HIDE_CONTENT = os.environ.get('HIDE_CONTENT') in ('1', 'yes', 'true')

TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Rome'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', 'English'),
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STATICFILES_DIRS = (
    ('frontend', os.path.join(os.path.dirname(__file__), '..', '..', 'frontend',
                              'dist')),
)

# version of static assets. Incrementing this value forces static asset
# cache clear in devices
STATIC_VERSION = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get('SECRET_KEY', 'phah6izoo3ahtiPh1zeighae%th4Yei0toh8ol,o')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
)

if os.environ.get('DISABLE_CSRF', '').lower() not in ('true', '1'):
    MIDDLEWARE_CLASSES += (
        'django.middleware.csrf.CsrfViewMiddleware',
        )

MIDDLEWARE_CLASSES += (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'xdimension_web.xdw_web.middleware.WIPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'xdimension_web.xdw_web.middleware.PartialResponseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.cms_settings',
    'sekizai.context_processors.sekizai',
)

ROOT_URLCONF = 'xdimension_web.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'xdimension_web.wsgi.application'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
    # custom apps
    'xdimension_web.xdw_core',
    'xdimension_web.xdw_web',
    # standard stuff
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.webdesign',
    # 'django.contrib.admindocs',
    'json_field',
    # DjangoCMS
    'djangocms_text_ckeditor',
    'cms',
    'mptt',
    'menus',
    'sekizai',
    'djangocms_file',
    'djangocms_picture',
    'djangocms_video',
    'django.contrib.redirects',
    # rest API
    'rest_framework',
    'rest_framework_swagger',
    'south',
    'corsheaders',
    # Misc
    'jfu'  # Uploader
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
CONSOLE_LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'logentries': {
            'format': 'DJ %(levelname)s %(name)s %(module)s: %(message)s',
            },
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': CONSOLE_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'logentries',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'xdimension_web': {
            'handlers': ['console'],
            'level': CONSOLE_LOG_LEVEL,
        },
    }
}

APPEND_SLASH = False  # Otherwise AngularJS complains


ALLOWED_HOSTS = ['xdiscovery.com', 'www.xdiscovery.com',
                 'api-app.xdiscovery.com', 'www-staging.xdiscovery.com',
                 'api-app-staging.xdiscovery.com',
                 'xdiscovery-web.herokuapp.com']

if DEPLOY_MODE == 'staging':
    ALLOWED_HOSTS += ['xdiscovery-web-staging.herokuapp.com']
elif DEPLOY_MODE == 'local':
    ALLOWED_HOSTS += ['localhost', '127.0.0.1']


ADMIN_URL_HASH = os.environ.get('ADMIN_URL_HASH', '')

# djangorestframework
REST_FRAMEWORK = {
    'PAGINATE_BY': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        ('rest_framework.authentication.SessionAuthentication' \
             if os.environ.get('DISABLE_CSRF') not in ('True', '1') \
             else 'xdimension_web.lib.authentication.NoCSRFSessionAuthentication'
         ,)
        ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Disallow automatic forms in API documentation, that sometimes break
    # things because they are a little too invasive in ApiView introspection
    'FORM_METHOD_OVERRIDE': None,
}

REST_API_DOCS_ENABLE = os.environ.get('REST_API_DOCS_ENABLE') in ('True', '1')

# CORS (deveopment only)
if DEPLOY_MODE in ('staging', 'local'):
    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = ('127.0.0.1:9000', 'localhost:9000', 'null', None)
    CORS_ALLOW_HEADERS = ('x-requested-with',
                          'content-type',
                          'accept',
                          'accept-encoding',
                          'origin',
                          'authorization',
                          'x-csrftoken')

# CMS
CMS_TEMPLATES = (
    ('xdw_web/base.html', 'Empty page'),  # TODO: remove this one
    ('xdw_web/cms_templates/landing.html', 'Landing page'),
    ('xdw_web/cms_templates/internal.html', 'Internal page'),
    ('xdw_web/cms_templates/wip.html', 'WIP page')
)

CMS_PLACEHOLDER_CONF = {
    'content': {
        'plugins': ['TextPlugin'],
        'text_only_plugins': ['LinkPlugin'],
        'name': 'Content',
    },
    'carousel': {
        'plugins': ['CarouselPlugin'],
        'name': 'Carousel',
        'limits': {
            'global': 10
        },
    },
    'abstract': {
        'plugins': ['AbstractPlugin'],
        'name': 'Abstract',
        'limits': {
            'global': 1
        },
    },
    'accordion_navigation': {
        'plugins': ['AccordionNavigationPlugin'],
        'name': 'AccordionNavigation',
        'limits': {
            'global': 1
        },
    },
    'accordion': {
        'plugins': ['AccordionPlugin'],
        'name': 'Accordion'
    },
    'box': {
        'plugins': ['BoxPlugin'],
        'name': 'Box',
        'limits': {
            'global': 3
        },
    }
}

CMS_CACHE_DURATIONS = {
    'content': 1,
    'menus': 1,
    'permissions': 3600
}

CMS_SEO_FIELDS = True


# Facebook
FB_APP_ID = {
    'staging': 186960618160957,
    'production': '',
    'local': 186960618160957,
}

FB_SITE_NAME = 'xDiscovery'

SHARING_PROTO = 'http'


# CKeditor

TEXT_ADDITIONAL_TAGS = ('iframe', 'script', 'image', 'svg')
TEXT_ADDITIONAL_ATTRIBUTES = ('scrolling', 'allowfullscreen', 'frameborder', 'xlink:href', 'style')
TEXT_SAVE_IMAGE_FUNCTION = None
TEXT_HTML_SANITIZE = False

# Thumbnail production

ZMQ_WORKER_PORT = 9999
