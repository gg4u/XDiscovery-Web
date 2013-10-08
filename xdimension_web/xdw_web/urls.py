# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views import AtlasView

urlpatterns = patterns(
    'xdw_web.views',
    # Atlas app
    url(r'^', AtlasView.as_view()),
    #url(r'^atlas/', AtlasView.as_view()),
    #url(r'^(views/.*)', AtlasView.as_view()),
)
