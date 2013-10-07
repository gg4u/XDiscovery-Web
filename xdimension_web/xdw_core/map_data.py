'''
Import xDimension map data from json.
'''
import json


def set_from_map_data(sender, instance=None, **kwargs):
    if not instance.map_data:
        return
    data = instance.map_data['map']
    if not instance.title:
        instance.title = data['title']
    if not instance.author_name:
        instance.author_name = data['author']['name']
    if not instance.author_surname:
        instance.author_surname = data['author']['surname']
    if not instance.description:
        instance.description = data['description']
    if not instance.picture_url:
        instance.picture_url = data['thumbnail'].get('url', '')
    # XXX FIXME here we should be walking the path from first to last...
    instance.node_titles = [n['title'] for n in data['pagerank']\
                                [:sender.MAX_NODE_TITLES]]
    instance.last_node_title = data['pagerank'][-1]['title']
    instance.node_count = len(data['graph'])
