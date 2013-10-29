# ~*~ coding: utf8 ~*~
from __future__ import absolute_import

from rest_framework.generics import ListAPIView
from rest_framework.serializers import ModelSerializer
from rest_framework import filters
from rest_framework import permissions

from ..models import Topic


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


class TopicSearchFilter(filters.BaseFilterBackend):
    page_size = 10

    def filter_queryset(self, request, queryset, view):
        q = request.QUERY_PARAMS.get('q')
        if q:
            q = q.lower()
            return queryset.filter(pk__contains=q)[:self.page_size]
        return queryset[:self.page_size]


class TopicList(ListAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = (TopicSearchFilter,)

    def get_paginate_by(self):
        # Disable pagination
        return None
