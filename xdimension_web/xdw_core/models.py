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

    FEATURED_NOT = 0
    FEATURED_YES = 1

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
    net = models.IntegerField(db_index=True, blank=True, null=True)
    # Non-editable fields calculated from map_data
    node_count = models.IntegerField(editable=False)
    node_titles = JSONField(editable=False)
    last_node_title = models.CharField(max_length=500, editable=False)
    # for sorting
    date_created = models.DateField(db_index=True, default=now_tz)
    popularity = models.IntegerField(default=0, db_index=True)
    featured = models.IntegerField(default=FEATURED_NOT, db_index=True,
                                   choices=[(FEATURED_NOT, 'no'),
                                            (FEATURED_YES, 'yes')])
    # generic
    status = models.CharField(max_length=1,
                              choices=[(STATUS_OK, 'Ok'),
                                       (STATUS_DELETED, 'Deleted'),
                                       (STATUS_UNPUBLISHED, 'Unpublished')],
                              default=STATUS_OK,
                              db_index=True)

    def get_title(self):
        if self.title:
            return self.title
        if self.node_titles and self.last_node_title:
            return u'from {start} to {end}'.format(start=self.node_titles[0],
                                                   end=self.last_node_title)
        logger.warning('no title found for map {}'.format(self.pk))
        return 'xDiscovery graph'

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
        # XXX FIXME here we should be walking the path from first to last...
        self.node_titles = [n['title'] for n in data['pagerank']\
                                    [:Map.MAX_NODE_TITLES]]
        self.last_node_title = data['pagerank'][-1]['title']
        self.node_count = len(data.get('graph', data.get('atlas')))
        return data


class MapTopic(models.Model):
    ''' For searching. '''
    map = models.ForeignKey(Map)
    topic = models.CharField(max_length=500)
    relevance = models.FloatField()

    class Meta:
        index_together = [
            ['topic', 'relevance']
        ]


class Topic(models.Model):
    topic = models.CharField(max_length=500, primary_key=True)
    # used to automatically GC topic on map deletion
    count = models.IntegerField(default=1)
