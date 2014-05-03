from __future__ import absolute_import

from django.contrib.admin import site, ModelAdmin
from django.conf.urls import patterns, url
from django.shortcuts import render
from django.utils.html import format_html
from django.db import transaction
from django.conf import settings
import zmq

from .models import Map
from .maps import save_map, delete_map, _save_map

# For talking to worker
context = zmq.Context()
zmq_socket = context.socket(zmq.PUB)
zmq_socket.connect("tcp://127.0.0.1:{}".format(settings.ZMQ_WORKER_PORT))


class MapAdmin(ModelAdmin):

    date_hierarchy = 'date_created'
    list_display = ['id', 'title', 'date_created', 'show_node_titles',
                    'node_count', 'popularity', 'featured', 'status']
    list_display_links = ['id']
    list_filter = ['status', 'featured']

    actions = ['delete_action', 'publish_action']

    class Meta:
        model = Map

    def save_model(self, request, obj, form, change):
        if obj.status in (Map.STATUS_OK, Map.STATUS_PUBLISHING):
            obj.thumbnail_status = Map.THUMBNAIL_STATUS_DIRTY
        save_map(obj)
        zmq_socket.send('wake up {}'.format(obj.pk))

    def delete_model(self, request, obj):
        delete_map(obj)

    def get_urls(self):
        urls = patterns(
            '',
            url(r'^upload-multi/$',
                self.admin_site.admin_view(self.upload_multi),
                name='upload-multi')
        )
        urls += super(MapAdmin, self).get_urls()
        return urls

    def upload_multi(self, request):
        return render(request, 'xdw_core/admin/upload_multi.html',
                      {'title': 'upload multiple maps'})

    def show_node_titles(self, obj):
        return ', '.join(format_html(u'<i>{}</i>', t)
                         for t in obj.node_titles)
    show_node_titles.allow_tags = True

    def get_actions(self, request):
        actions = super(MapAdmin, self).get_actions(request)
        return {k: v for k, v in actions.items() if k != 'delete_selected'}

    def delete_action(self, request, queryset):
        i = 0
        for i, obj in enumerate(queryset):
            delete_map(obj)
        self.message_user(request, '{} maps deleted'.format(i))
    delete_action.short_description = 'Delete selected maps (forever)'

    def publish_action(self, request, queryset):
        i = 0
        with transaction.commit_on_success():
            for i, obj in enumerate(queryset):
                if obj.status != Map.STATUS_OK:
                    obj.status = Map.STATUS_PUBLISHING
                    obj.thumnail_status = Map.THUMBNAIL_STATUS_DIRTY
                    _save_map(obj)
        self.message_user(request, '{} maps published'.format(i))
        zmq_socket.send('wake up')
    publish_action.short_description = 'Publish selected maps'


site.register(Map, MapAdmin)
