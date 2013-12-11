from __future__ import absolute_import

import datetime
import os

from django.utils.timezone import utc

from ..models import Map
from ..maps import save_map


def get_test_data(name):
    with open(os.path.join(os.path.dirname(__file__), 'data', name)) as f:
        return f.read()


class MapTestCaseMixIn(object):

    def create_maps(self, num, **kwargs):
        defaults = {
            'map_data': get_test_data('sharingAppWeb.json')
            }
        defaults.update(kwargs)
        start = datetime.datetime.now(utc)
        maps = []
        for i in range(num):
            mp = Map(**defaults)
            mp.popularity = i
            if 'title' not in defaults:
                mp.title = str(i)
            mp.date_created = start - datetime.timedelta(i)
            save_map(mp)
            maps.append(mp)
        return maps
