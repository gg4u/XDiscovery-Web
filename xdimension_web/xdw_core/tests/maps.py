from __future__ import absolute_import
import datetime
import json

from django.test import TestCase, LiveServerTestCase
from django.utils.timezone import utc

from ..models import Map
from .utils import get_test_data

__all__ = ['MapTestCase']


class MapTestCase(LiveServerTestCase):

    def create_maps(self, num):
        start = datetime.datetime.now(utc)
        maps = []
        for i in range(num):
            mp = Map(map_data=get_test_data('sharingAppWeb.json'))
            mp.popularity = i
            mp.title = str(i)
            mp.date_created = start - datetime.timedelta(i)
            mp.save()
            maps.append(mp)
        return maps

    def test_html(self):
        resp = self.client.get('/atlas/', follow=True)
        self.assertContains(resp, '/frontend/styles/')

    def test_empty(self):
        resp = self.client.get('/api/map/', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['results']), 0)

    def test_load_map(self):
        Map.objects.create(map_data=get_test_data('sharingAppWeb.json'))
        mp = Map.objects.get()
        self.assertEqual(mp.title, 'titolo')
        self.assertEqual(mp.node_count, 18)
        self.assertTrue(False, 'walk the nodes in the right direction')
        self.assertEqual(mp.node_titles, [u'Leopard', u'Lion', u'Cheetah', u'Asiatic lion', u'Transvaal lion', u'Southwest African lion', u'Indochinese leopard', u'African leopard', u'North China leopard', u'Felis', u'Big cat', u'Arabian leopard', u'Striped hyena', u'Indian leopard', u'Sri Lankan leopard', u'Javan leopard', u'Lycaon pictus', u'Northwest African cheetah'])
        self.assertEqual(mp.last_node_title, 'Cheetah')

    def test_list(self):
        Map.objects.create(map_data=get_test_data('sharingAppWeb.json'))
        resp = self.client.get('/api/map/', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)
        obj = data['map'][0]
        self.assertNotIn('map_data', obj)
        self.assertNotIn('path', obj)

    def test_list_sort_popular(self):
        self.create_maps(10)
        resp = self.client.get('/api/map/',
                               {'ordering': 'popularity'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(10)],
                         [obj['title'] for obj in data['map']])
        # reverse
        resp = self.client.get('/api/map/',
                               {'ordering': '-popularity'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(9, -1, -1)],
                         [obj['title'] for obj in data['map']])

    def test_list_sort_date_created(self):
        self.create_maps(10)
        resp = self.client.get('/api/map/',
                               {'ordering': 'date_created'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(9, -1, -1)],
                         [obj['title'] for obj in data['map']])
        # reverse
        resp = self.client.get('/api/map/',
                               {'ordering': '-date_created'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(10)],
                         [obj['title'] for obj in data['map']])

    def test_detail(self):
        mp = Map.objects.create(map_data=get_test_data('sharingAppWeb.json'))
        resp = self.client.get('/api/map/{}/'.format(mp.pk),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertNotIn('map_data', data)
        self.assertIn('path', data)
