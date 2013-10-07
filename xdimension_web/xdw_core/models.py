'''
Base models for the xDimension web project
'''
from __future__ import absolute_import

from django.db import models
from django.db.models.signals import pre_save
from django.utils.timezone import now as now_tz

from json_field import JSONField

from .map_data import set_from_map_data


class Map(models.Model):
    ''' Contains nodes connected into a graph.
    '''

    STATUS_OK = 'O'
    STATUS_DELETED = 'D'

    # To be stored inside the grouped title list
    MAX_NODE_TITLES = 20

    # provided by user
    map_data = JSONField(help_text='json data from xDimension engine')
    # User-editable fields (override data fetched from map_data)
    title = models.CharField(max_length=500, blank=True)
    author_name = models.CharField(max_length=500, blank=True)
    author_surname = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    picture_url = models.CharField(max_length=1000, blank=True)
    # Non-editable fields calculated from map_data
    node_count = models.IntegerField(editable=False)
    node_titles = JSONField(editable=False)
    last_node_title = models.CharField(max_length=500, editable=False) 
    # for sorting
    date_created = models.DateField(db_index=True, default=now_tz)
    popularity = models.IntegerField(default=0, db_index=True)
    featured = models.IntegerField(default=0, db_index=True)
    # generic
    status = models.CharField(max_length=1,
                              choices=[(STATUS_OK, 'Ok'),
                                       (STATUS_DELETED, 'Deleted')],
                              default=STATUS_OK,
                              db_index=True)


class MapTopic(models.Model):
    ''' For searching. '''
    map = models.ForeignKey(Map)
    topic = models.CharField(max_length=500)
    relevance = models.IntegerField()

    class Meta:
        index_together = [
            ['topic', 'relevance']
        ]


pre_save.connect(set_from_map_data, sender=Map)
