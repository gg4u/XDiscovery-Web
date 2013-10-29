from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views.maps import MapDetail, MapList
from .views.topics import TopicList


# API entry point
urlpatterns = patterns(
    '',
    url(r'^map$', MapList.as_view(), name='map-list'),
    url(r'^map/(?P<pk>\d+)$', MapDetail.as_view(), name='map-detail'),
    url(r'^topic$', TopicList.as_view(), name='topic-list'),
    )
