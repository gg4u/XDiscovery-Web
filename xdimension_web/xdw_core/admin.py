from __future__ import absolute_import

from django.contrib.admin import site, ModelAdmin
from django.conf.urls import patterns, url
from django.shortcuts import render

from .models import Map
from .maps import save_map


class MapAdmin(ModelAdmin):

    def save_model(self, request, obj, form, change):
        save_map(obj)

    def get_urls(self):
        urls = patterns('',
                        url(r'^upload-multi/$', self.admin_site.admin_view(self.upload_multi), name='upload-multi')
        )
        urls += super(MapAdmin, self).get_urls()
        return urls

    def upload_multi(self, request):
        return render(request, 'xdw_core/admin/upload_multi.html',
                      {'title': 'upload multiple maps'})

    class Meta:
        model = Map


site.register(Map, MapAdmin)
