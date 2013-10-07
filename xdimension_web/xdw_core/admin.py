from __future__ import absolute_import

from django.contrib.admin import site

from .models import Map

site.register(Map)
