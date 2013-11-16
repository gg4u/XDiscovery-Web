# ~*~ coding: utf8 ~*~
from __future__ import absolute_import

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework import fields
from rest_framework import filters
from rest_framework.pagination import PaginationSerializer
from rest_framework import permissions
from rest_framework import authentication

from ..models import Map
from ..maps import save_map


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

    def restore_fields(self, data, files):
        attrs = super(MapSerializer, self).restore_fields(data, files)
        attrs['map_data'] = data
        attrs['status'] = Map.STATUS_UNPUBLISHED
        return attrs

    def save_object(self, obj, **kwargs):
        save_map(obj)

    def to_native(self, obj):
        ret = super(MapSimpleSerializer, self).to_native(obj)
        data = obj.map_data['map']
        ret.update({'graph': data['graph'],
                    'pagerank': data['pagerank'],
                    'path': data['path'],
                    'startNode': data['startNode'],
                    'endNode': data['endNode'],
                    'nodes': {n['id']: {'title': n['title'],
                                        'weight': n['weight']}
                              for n in data['pagerank']}})
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


class TopicSearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        topics = [t.strip().lower() for t in request.QUERY_PARAMS.getlist('topic')]
        if topics:
            # XXX TODO: escape the regexp contents for safety
            regex = '({})'.format('|'.join(topics))
            return queryset.filter(maptopic__topic__iregex=regex).distinct()
        return queryset


class MapList(ListCreateAPIView):
    queryset = Map.objects.filter(status=Map.STATUS_OK)
    serializer_class = MapSerializer
    pagination_serializer_class = MapPaginationSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [authentication.BasicAuthentication]
    filter_backends = (filters.OrderingFilter, TopicSearchFilter,
                       filters.DjangoFilterBackend)
    filter_fields = ('featured',)

    def get_pagination_serializer(self, page):
        context = self.get_serializer_context()
        return MapPaginationSerializer(instance=page, context=context)

    def check_permissions(self, request):
        if (request.method == 'POST' and
            not permissions.IsAuthenticated().has_permission(request, self)):
            self.permission_denied(request)
        super(MapList, self).check_permissions(request)


class MapDetail(RetrieveAPIView):
    queryset = Map.objects.filter(status=Map.STATUS_OK)
    serializer_class = MapSerializer
    permission_classes = [permissions.AllowAny]
