from __future__ import absolute_import
import json
import base64

from django.test import LiveServerTestCase
from django.contrib.auth.models import User

from ..models import Map, MapTopic
from ..maps import save_map
from ..thumbs import generate_map_thumbnail
from .test_utils import MapTestCaseMixIn, get_test_data


__all__ = ['ThumbTestCase']


class ThumbTestCase(LiveServerTestCase, MapTestCaseMixIn):

    def test_create_thumbs(self):
        save_map(Map(map_data=get_test_data('sharing_3.json')))
        mp = Map.objects.get()
        thumb = generate_map_thumbnail(mp)
        self.assertTrue(thumb)
        thumb.show()
        self.assertEqual(thumb.size, (400, 298))

