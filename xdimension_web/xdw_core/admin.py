from __future__ import absolute_import

from django.contrib.admin import site, ModelAdmin
from django.conf.urls import patterns, url
from django.shortcuts import render
from django.utils.html import format_html

from .models import Map
from .maps import save_map, delete_map


class MapAdmin(ModelAdmin):

    date_hierarchy = 'date_created'
    list_display = ['title', 'date_created', 'show_node_titles', 'node_count',
                    'popularity', 'featured', 'status']
    list_display_links = ['title', 'date_created']
    list_filter = ['status', 'featured']

    actions = ['delete_action', 'publish_action']

    class Meta:
        model = Map

    def save_model(self, request, obj, form, change):
        save_map(obj)

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
        for i, obj in enumerate(queryset):
            obj.status = Map.STATUS_PUBLISHED
            save_map(obj)
        self.message_user(request, '{} maps published'.format(i))
    publish_action.short_description = 'Publish selected maps'


site.register(Map, MapAdmin)
