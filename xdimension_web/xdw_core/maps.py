'''
Manipulation of Map models and friends.
'''

from __future__ import absolute_import
import logging

from django.db import transaction

from .models import Map, MapTopic, Topic

logger = logging.getLogger(__name__)


@transaction.commit_on_success
def save_map(obj):
    ''' Save a map, the right way. Mantaining all other ancillary models.
    '''

    data = obj.update_from_map_data()

    if not data:
        return

    # Previous published topics
    if obj.pk is not None:
        topics_prev = {o.topic: o for o in obj.maptopic_set.all()}
    else:
        topics_prev = {}

    # save obj into db
    obj.save()

    if obj.status == Map.STATUS_OK:
        topics_next = {pr['title'].strip(): {'relevance': pr['weight']}
                       for pr in data['pagerank']}
    else:
        topics_next = {}

    # Delete all past topics
    for topic in set(topics_prev).difference(topics_next):
        topics_prev[topic].delete()
        if not Topic.objects.filter(pk=topic).delete():
            logger.warning('failed to delete topic {}'.format(topic))

    # Create new topics
    for topic in set(topics_next).difference(topics_prev):
        MapTopic.objects.create(map=obj, topic=topic,
                                relevance=topics_next[topic]['relevance'])
        Topic.objects.get_or_create(topic=topic)

    # Alter existing topics
    for topic in set(topics_next).intersection(topics_prev):
        relevance_next = topics_next[topic]['relevance']
        map_topic = topics_prev[topic]
        if relevance_next != map_topic.relevance:
            map_topic.relevance = relevance_next
            map_topic.save(update_fields=['relevance'])

    return obj
