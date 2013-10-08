# ~*~ coding: utf8 ~*~
from __future__ import absolute_import

import json

from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework import fields
from rest_framework import filters
from rest_framework.pagination import PaginationSerializer
from rest_framework import permissions

from ..models import Map


class MapSimpleSerializer(ModelSerializer):
    def to_native(self, obj):
        ret = super(MapSimpleSerializer, self).to_native(obj)
        ret.update({'author': {'name': obj.author_name,
                               'surname': obj.author_surname},
                    'thumbnail': {'url': obj.picture_url},
                    'nodeTitles': {
                        'start': obj.node_titles,
                        'last': obj.last_node_title
                        }
                    })
        return ret

    class Meta:
        model = Map
        exclude = ('map_data', 'author_name', 'author_surname',
                   'picture_url', 'node_titles', 'last_node_title')


class MapSerializer(MapSimpleSerializer):
    def to_native(self, obj):
        ret = super(MapSimpleSerializer, self).to_native(obj)
        data = obj.map_data['map']
        ret.update({'graph': data['graph'],
                    'pagerank': data['pagerank'],
                    'path': data['path'],
                    'startNode': data['startNode'],
                    'endNode': data['endNode']})
        return ret

    class Meta(MapSimpleSerializer.Meta):
        pass


class MapPaginationSerializer(PaginationSerializer):
    results_field = 'map'
    # Label to be shown under the search box
    topic = fields.SerializerMethodField('get_topic')

    def get_topic(self, page):
        return u', '.join([obj.title for obj in page if obj.title])

    class Meta:
        object_serializer_class = MapSimpleSerializer


class MapList(ListAPIView):
    queryset = Map.objects.filter(status=Map.STATUS_OK)
    serializer_class = MapSerializer
    pagination_serializer_class = MapPaginationSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (filters.OrderingFilter,)

    def get_pagination_serializer(self, page):
        context = self.get_serializer_context()
        return MapPaginationSerializer(instance=page, context=context)


class MapDetail(RetrieveAPIView):
    queryset = Map.objects.filter(status=Map.STATUS_OK)
    serializer_class = MapSerializer
    permission_classes = [permissions.AllowAny]
