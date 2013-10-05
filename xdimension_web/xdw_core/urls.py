from __future__ import absolute_import

from django.conf.urls import patterns, url, include
from django.conf import settings

from rest_framework import routers

from .views.maps import MapViewSet


router = routers.DefaultRouter()
router.register('maps', MapViewSet)


# API entry point
urlpatterns = router.urls