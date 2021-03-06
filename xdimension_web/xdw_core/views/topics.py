# ~*~ coding: utf8 ~*~
from __future__ import absolute_import

from rest_framework.generics import ListAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework import filters
from rest_framework import permissions

from ..models import Topic

# fixing search
from ..models import Map
from ..models import MapTopic
from itertools import chain

# topic.py

class TopicSerializer(ModelSerializer):
    result_field = 'topic'

    @property
    def data(self):
        data = super(TopicSerializer, self).data
        if self.many:
            return {'topic': data}
        return data

    class Meta:
        model = Topic
        fields = ['topic']

'''
# old search aginst an exact topic title
class TopicSearchFilter(filters.BaseFilterBackend):
    page_size = 10

    def filter_queryset(self, request, queryset, view):
        q = request.QUERY_PARAMS.get('q')
        if q:
            q = q.lower()
            return queryset.filter(pk__icontains=q).order_by('pk')[:self.page_size]
        return queryset[:self.page_size]
'''

'''
# new search against keywords contained in topics, titles
'''

class TopicSearchFilter(filters.BaseFilterBackend):
    page_size = 10

    def filter_queryset(self, request, queryset, view):
        #prende le keywords
        q = request.QUERY_PARAMS.get('q')
        # ESCAPE
        q = q.replace('\\','')
        original = queryset
        if q:
            q = q.lower()
            #cerca le mappe con titoli che contengono la keyword
            map_titles = Map.objects.filter(title__icontains=q).values("title")
            #crea una lista di Topic presi dai titoli delle mappe trovate prima
            map_titles_topics = [Topic(topic=x['title']) for x in map_titles]
            #prende i topic che contengono la keyword ma che non contengono i titoli della mappe trovati prima
            queryset = queryset.filter(pk__icontains=q).exclude(pk__in=map_titles).order_by('pk')
            #unisce i risultati dai topic e dai titoli delle mappe
            queryset = set(chain(queryset, map_titles_topics))
            #se non trova la keyword esatta tra i topic e i titoli delle mappe, aggiunge
            if not request.QUERY_PARAMS.get('q') in [x.topic for x in queryset]:
                queryset = list(chain(list([Topic(topic=request.QUERY_PARAMS.get('q')),]), queryset))
        #costruisce la lista
        enumerate_queryset = queryset
        queryset = []#[x for x in queryset]

        for index,x in enumerate(enumerate_queryset):
            #topic-maps relationsheep filter
            topic_maps = getattr(x, 'count')
            if topic_maps>0:
                queryset.append(x)

        # if len(queryset) > 0:
        #     queryset.pop(0) 

        #Remove current search so you don't find result that doesn't exists
        return queryset[:self.page_size]


class TopicList(ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (TopicSearchFilter,)

    def get_paginate_by(self):
        # Disable pagination
        return None
