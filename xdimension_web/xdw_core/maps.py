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
        title_prev = obj.__class__.objects.get(pk=obj.pk).title
        topics_prev[title_prev] = {'relevance': 1}
    else:
        topics_prev = {}

    # save obj into db
    obj.save()

    if obj.status == Map.STATUS_OK:
        topics_next = {pr['title'].strip(): {'relevance': pr['weight']}
                       for pr in data['pagerank']}
        topics_next[obj.title] = {'relevance': 1}
    else:
        topics_next = {}

    # Delete all past topics
    for topic in set(topics_prev).difference(topics_next):
        try:
            topic = Topic.objects.get(pk=topic)
        except Topic.DoesNotExist:
            logger.warning('failed to delete topic {}'.format(topic))
        else:
            topic.count -= 1
            if topic.count <= 0:
                topic.delete()
            else:
                topic.save(update_fields=['count'])

    # Create new topics
    for topic in set(topics_next).difference(topics_prev):
        MapTopic.objects.create(map=obj, topic=topic,
                                relevance=topics_next[topic]['relevance'])
        topic, created = Topic.objects.get_or_create(topic=topic)
        if not created:
            topic.count += 1
            topic.save(update_fields=['count'])

    # Alter existing topics
    for topic in set(topics_next).intersection(topics_prev):
        relevance_next = topics_next[topic]['relevance']
        map_topic = topics_prev[topic]
        if (isinstance(map_topic, MapTopic) and
            relevance_next != map_topic.relevance):
            map_topic.relevance = relevance_next
            map_topic.save(update_fields=['relevance'])

    return obj


@transaction.commit_on_success
def delete_map(obj):
    obj.status = Map.STATUS_DELETED
    save_map(obj)
    obj.delete()
