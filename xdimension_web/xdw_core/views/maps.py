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


# maps.py

# fix per ricerca:
# see: https://docs.djangoproject.com/en/1.7/topics/db/queries/
from django.db.models import Q


class MapSimpleSerializer(ModelSerializer):

    def to_native(self, obj):
        ret = super(MapSimpleSerializer, self).to_native(obj)
        ret.update({'author': {'name': obj.author_name,
                               'surname': obj.author_surname},
                    'thumbnail': {'url': obj.get_thumbnail_url()},
                    'nodeTitles': {
                        'first': obj.first_node_title,
                        'start': obj.node_titles[:10],
                        'last': obj.last_node_title,
                        'count': len(obj.node_titles),
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
        ret = super(MapSerializer, self).to_native(obj)
        data = obj.map_data['map']
        nodes = {id_: {'tapped': True}
                 for id_ in data.get('tappedNodes', ())}
        ret.update({'graph': data.get('graph', data.get('atlas')),
                    'nodes': nodes,
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

'''
# old search against exact titles and topics

class TopicSearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        topics = [t.strip().lower() for t in request.QUERY_PARAMS.getlist('topic')]
        if topics:
            # XXX TODO: escape the regexp contents for safety
            regex = u'({})'.format(u'|'.join([t.replace('(', '\(').replace(')', '\)')]))
            return queryset.filter(maptopic__topic__iregex=regex).distinct()
        return queryset
'''

'''
new search against keywords in topics and titles
'''

class TopicSearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        #cicla sugli argomenti della request per prendere i topics cercati
        topics = []

        if request.QUERY_PARAMS.getlist('topic'):
            topics = set([t.strip().lower() for t in request.QUERY_PARAMS.getlist('topic')])
        if "," in request.GET.get('topic',""):
            topics = set([t.strip().lower() for t in request.GET.get('topic').split(",")])

        q1 = queryset
        q2 = queryset

        for t in topics:
            q1 = q1.filter(title__icontains=t.replace('\\',''))
            q2 = q2.filter(maptopic__topic__icontains=t.replace('\\',''))    

        queryOrder = request.GET.get('ordering',"-popularity").encode("utf-8")

        #estrapola le mappe con nel titolo e nel topic le key prescelte
        q1 = q1.distinct().order_by(queryOrder,"-title").values('id','title')
        q2 = q2.distinct().order_by(queryOrder,"-title").values('id','title')
        #merge
        ids = [x['id'] for x in q1]+[x['id'] for x in q2]
        #query  preservando l ordinamento
        clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(ids)])
        ordering = 'CASE %s END' % clauses
        queryset = queryset.filter(pk__in=ids).extra(select={'ordering': ordering}, order_by=('ordering',));

        # return queryset
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

    def retrieve(self, *args, **kwargs):
        resp = super(MapDetail, self).retrieve(*args, **kwargs)

        # Update popularity counter
        # TODO: decouple from request handling
        self.object.popularity += 1
        self.object.save(update_fields=['popularity'])

        return resp
