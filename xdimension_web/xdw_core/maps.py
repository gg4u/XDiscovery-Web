'''
Manipulation of Map models and friends.
'''

from __future__ import absolute_import

from django.db import transaction

from .models import Map, MapTopic


@transaction.commit_on_success
def save_map(obj):
    ''' Save a map, the right way.
    '''
    if not obj.map_data:
        return
    data = obj.map_data['map']
    if not obj.title:
        obj.title = data['title']
    if not obj.author_name:
        obj.author_name = data['author']['name']
    if not obj.author_surname:
        obj.author_surname = data['author']['surname']
    if not obj.description:
        obj.description = data['description']
    if not obj.picture_url:
        obj.picture_url = data['thumbnail'].get('url', '')
    # XXX FIXME here we should be walking the path from first to last...
    obj.node_titles = [n['title'] for n in data['pagerank']\
                                [:Map.MAX_NODE_TITLES]]
    obj.last_node_title = data['pagerank'][-1]['title']
    obj.node_count = len(data['graph'])
    # save obj into db
    obj.save()
    # Set related model for searching
    obj.maptopic_set.all().delete()
    for n in data['pagerank']:
        # XXX what if title is empty? Is it right to save it lowercased?
        title = n['title'].lower()
        MapTopic.objects.create(map=obj, topic=title, relevance=n['weight'])
    return obj
