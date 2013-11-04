from django.conf.urls import patterns, url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf import settings

from xdw_web.views import RobotsView, AtlasView

admin.autodiscover()

# i18n patterns
urlpatterns = i18n_patterns(
    '',
    # Backoffice
    url(r'^admin{}/'.format(settings.ADMIN_URL_HASH), include(admin.site.urls)),
    # CMS
    url(r'^', include('cms.urls')),
)

# non-i18n patterns
urlpatterns += patterns(
    '',
    # Atlas app
    # XXX the SPA uris should all live under the /atlas/ uri
    url(r'^atlas/', AtlasView.as_view()),
    url(r'^(views/.*)', AtlasView.as_view()),
    # SEO stuff
    url(r'^robots.txt$', RobotsView.as_view()),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemap': []}, name='sitemap'),
    # multiple file upload
    url(r'^upload/', 'xdimension_web.xdw_core.views.upload.upload_multi',
        name='jfu_upload'),
    # REST API
    url(r'^api/', include('xdimension_web.xdw_core.urls',
                          namespace='xdw_core')),
    )

if settings.DEBUG:
    # Asset serving
    urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    url(r'', include('django.contrib.staticfiles.urls')),    
) + urlpatterns


if settings.REST_API_DOCS_ENABLE:
    urlpatterns += patterns(
        '',
        # restframework browser login
        url(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')),
        # REST framework swagger API documentation
        #url(r'^swagger/', include('rest_framework_swagger.urls')),
        )
