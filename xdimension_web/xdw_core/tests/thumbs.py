from __future__ import absolute_import
import json
import base64

from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Map, MapTopic
from ..maps import save_map
from ..thumbs import generate_map_thumbnail, save_map_thumbnail
from .test_utils import MapTestCaseMixIn, get_test_data


__all__ = ['ThumbTestCase']


class ThumbTestCase(TestCase, MapTestCaseMixIn):

    def test_create_thumbs(self):
        save_map(Map(map_data=get_test_data('sharing_3.json')))
        mp = Map.objects.get()
        thumb = generate_map_thumbnail(mp)
        self.assertTrue(thumb)
        thumb.show()
        self.assertEqual(thumb.size, (300, 233))
        save_map_thumbnail(mp, thumb)

    def test_create_thumbs_no_img(self):
        save_map(Map(map_data=get_test_data('sharing_4.json')))
        mp = Map.objects.get()
        thumb = generate_map_thumbnail(mp)
        self.assertTrue(thumb)
        thumb.show()
        self.assertEqual(thumb.size, (300, 233))
        save_map_thumbnail(mp, thumb)
