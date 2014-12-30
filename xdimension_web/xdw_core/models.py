'''
Base models for the xDimension web project
'''
from __future__ import absolute_import
import logging

from django.db import models
from django.utils.timezone import now as now_tz

from json_field import JSONField

logger = logging.getLogger(__name__)

class Map(models.Model):
    ''' Contains nodes connected into a graph.
    '''

    STATUS_OK = 'O'
    STATUS_DELETED = 'D'
    STATUS_UNPUBLISHED = 'U'
    STATUS_PUBLISHING = 'i'  # request to publish but thumbnail is dirty
    STATUS_CHOICES = [
        (STATUS_OK, 'Ok'),
        (STATUS_DELETED, 'Deleted'),
        (STATUS_UNPUBLISHED, 'Unpublished'),
        (STATUS_PUBLISHING, 'Publishing...')
    ]

    FEATURED_NOT = 0
    FEATURED_YES = 1

    THUMBNAIL_STATUS_OFF = 'x'
    THUMBNAIL_STATUS_DIRTY = 'd'
    THUMBNAIL_STATUS_OK = 'O'
    THUMBNAIL_STATUS_CHOICES = [
        (THUMBNAIL_STATUS_OFF, 'not present'),
        (THUMBNAIL_STATUS_DIRTY, 'in progress'),
        (THUMBNAIL_STATUS_OK, 'ok')
    ]
    # To be stored inside the grouped title list
    MAX_NODE_TITLES = 20

    # provided by user
    map_data = JSONField(help_text='json data from xDimension engine')
    # User-editable fields (override data fetched from map_data)
    title = models.CharField(max_length=500, blank=True)
    author_name = models.CharField(max_length=500, blank=True)
    author_surname = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    picture_url = models.CharField(max_length=1000, blank=True,
                                   help_text='custom thumbnail')
    thumbnail = models.ImageField(upload_to='map_thumbnail', max_length=1000,
                                  blank=True, null=True)
    net = models.IntegerField(db_index=True, blank=True, null=True)
    # Non-editable fields calculated from map_data
    node_count = models.IntegerField(editable=False)
    node_titles = JSONField(editable=False)
    first_node_title = models.CharField(max_length=500, editable=False)
    last_node_title = models.CharField(max_length=500, editable=False)
    # for sorting
    date_created = models.DateField(db_index=True, default=now_tz)
    popularity = models.IntegerField(default=0, db_index=True)
    featured = models.IntegerField(default=FEATURED_NOT, db_index=True,
                                   choices=[(FEATURED_NOT, 'no'),
                                            (FEATURED_YES, 'yes')])
    # generic
    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_OK,
                              db_index=True)
    thumbnail_status = models.CharField(max_length=1,
                                        choices=THUMBNAIL_STATUS_CHOICES,
                                        default=THUMBNAIL_STATUS_OFF,
                                        db_index=True)

    def get_title(self):
        if self.title:
            return self.title
        if self.first_node_title and self.last_node_title:
            return u'from {start} to {end}'.format(start=self.first_node_title,
                                                   end=self.last_node_title)
        logger.warning('no title found for map {}'.format(self.pk))
        return 'xDiscovery graph'

    def get_thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else self.picture_url

    def update_from_map_data(self):
        if not self.map_data:
            return
        data = self.map_data['map']
        if not self.title:
            self.title = data['title']
        if not self.author_name and 'author' in data:
            self.author_name = data['author']['name']
        if not self.author_surname and 'author' in data:
            self.author_surname = data['author']['surname']
        if not self.description:
            self.description = data['description']
        if not self.picture_url and 'thumbnail' in data:
            self.picture_url = data['thumbnail'].get('url', '')
        net = data.get('net')
        try:
            self.net = int(net)
        except (ValueError, TypeError):
            logger.warning('bad value for \"net\" field: {}'.format(net))
        node_titles = []
        if 'startNode' in data:
            self.first_node_title = data['startNode']['title']
        else:
            self.first_node_title = data['pagerank'][0]['title']
        self.node_titles = [n['title'] for n in data['pagerank']\
                                    [:Map.MAX_NODE_TITLES]]
        if 'endNode' in data:
            self.last_node_title = data['endNode']['title']
        else:
            self.last_node_title = data['pagerank'][-1]['title']
        self.node_count = len(data.get('graph', data.get('atlas')))
        return data

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Map._meta.fields]


class MapTopic(models.Model):
    ''' For searching. '''
    map = models.ForeignKey(Map)
    topic = models.CharField(max_length=500)
    relevance = models.FloatField()

    class Meta:
        index_together = [
            ['topic', 'relevance']
        ]

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in MapTopic._meta.fields]





class Topic(models.Model):
    topic = models.CharField(max_length=500, primary_key=True)
    # used to automatically GC topic on map deletion
    count = models.IntegerField(default=1)
