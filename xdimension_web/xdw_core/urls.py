from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views.maps import MapDetail, MapList


# API entry point
urlpatterns = patterns(
    '',
    url(r'^map/$', MapList.as_view(), name='map-list'),
    url(r'^map/(?P<pk>\d+)/$', MapDetail.as_view(), name='map-detail'),
    )
