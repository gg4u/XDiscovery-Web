from __future__ import absolute_import
import datetime
import json

from django.test import TestCase
from django.utils.timezone import utc

from ..models import Map

__all__ = ['MapTestCase']


class MapTestCase(TestCase):

    def test_html(self):
        resp = self.client.get('/atlas/', follow=True)
        self.assertContains(resp, '<h1>Atlas</h1>')

    def test_empty(self):
        resp = self.client.get('/api/maps/', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['results']), 0)

    def test_one_map(self):
        Map.objects.create(map_data='{}',
                           date_created=datetime.datetime.now(utc))
        resp = self.client.get('/api/maps/', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['results']), 1)
