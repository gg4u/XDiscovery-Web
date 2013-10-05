from __future__ import absolute_import
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework import permissions

from ..models import Map


class MapSerializer(ModelSerializer):
    class Meta:
        model = Map


class MapViewSet(ModelViewSet):
    queryset = Map.objects.all()
    serializer_class = MapSerializer
    permission_classes = [permissions.AllowAny]