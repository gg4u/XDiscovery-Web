from __future__ import absolute_import

from django.contrib.admin import site, ModelAdmin

from .models import Map
from .maps import save_map


class MapAdmin(ModelAdmin):

    def save_model(self, request, obj, form, change):
        save_map(obj)

    class Meta:
        model = Map


site.register(Map, MapAdmin)
