from __future__ import absolute_import

from django.contrib.admin import TabularInline

from .models import CarouselContent


class CarouselContentInline(TabularInline):
    model = CarouselContent
    extra = 0
