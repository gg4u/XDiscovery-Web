from __future__ import absolute_import
import json

from django.test import LiveServerTestCase

from ..models import Map, MapTopic
from ..maps import save_map
from .test_utils import MapTestCaseMixIn, get_test_data


__all__ = ['MapTestCase']


class MapTestCase(LiveServerTestCase, MapTestCaseMixIn):

    def test_html(self):
        resp = self.client.get('/atlas/', follow=True)
        self.assertContains(resp, '/frontend/styles/')

    def test_empty(self):
        resp = self.client.get('/api/map', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_load_map(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        mp = Map.objects.get()
        self.assertEqual(mp.title, 'titolo')
        self.assertEqual(mp.node_count, 18)
        self.assertTrue(False, 'walk the nodes in the right direction')
        self.assertEqual(mp.node_titles, [u'Leopard', u'Lion', u'Cheetah', u'Asiatic lion', u'Transvaal lion', u'Southwest African lion', u'Indochinese leopard', u'African leopard', u'North China leopard', u'Felis', u'Big cat', u'Arabian leopard', u'Striped hyena', u'Indian leopard', u'Sri Lankan leopard', u'Javan leopard', u'Lycaon pictus', u'Northwest African cheetah'])
        self.assertEqual(mp.last_node_title, 'Cheetah')

    def test_list(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api/map', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)
        obj = data['map'][0]
        self.assertNotIn('map_data', obj)
        self.assertNotIn('path', obj)

    def test_list_sort_popular(self):
        self.create_maps(10)
        resp = self.client.get('/api/map',
                               {'ordering': 'popularity'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(10)],
                         [obj['title'] for obj in data['map']])
        # reverse
        resp = self.client.get('/api/map',
                               {'ordering': '-popularity'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(9, -1, -1)],
                         [obj['title'] for obj in data['map']])

    def test_list_sort_date_created(self):
        self.create_maps(10)
        resp = self.client.get('/api/map',
                               {'ordering': 'date_created'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(9, -1, -1)],
                         [obj['title'] for obj in data['map']])
        # reverse
        resp = self.client.get('/api/map',
                               {'ordering': '-date_created'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(10)],
                         [obj['title'] for obj in data['map']])

    def test_list_filter_featured(self):
        self.create_maps(10, featured=False)
        resp = self.client.get('/api/map',
                               {'featured': '1'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)
        # not featured
        resp = self.client.get('/api/map',
                               {'featured': '0'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)

    def test_list_search_empty(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api/map',
                               {'topic': 'xxxxxxxxxxx'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_list_search(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api/map',
                               {'topic': 'lion'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)
        # case-insensitive
        resp = self.client.get('/api/map',
                               {'topic': 'liON'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)


    def test_list_search_2_terms(self):
        mp = save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        topics = [u'african leopard', u'arabian leopard', u'asiatic lion', u'big cat', u'cheetah', u'felis', u'indian leopard', u'indochinese leopard', u'javan leopard', u'leopard', u'lion', u'lycaon pictus', u'north china leopard', u'northwest african cheetah', u'southwest african lion', u'sri lankan leopard', u'striped hyena', u'transvaal lion']
        # Topics need to be saved in db
        self.assertEqual(
            topics,
            list(MapTopic.objects.order_by('topic').values_list('topic', flat=True)))
        self.assertEqual(
            topics,
            list(mp.maptopic_set.order_by('topic').values_list('topic', flat=True)))
        resp = self.client.get('/api/map',
                               {'topic': 'lion,felis'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)
        # case-insensitive
        resp = self.client.get('/api/map',
                               {'topic': 'liON'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)


    def test_detail(self):
        mp = save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api/map/{}'.format(mp.pk),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertNotIn('map_data', data)
        self.assertIn('path', data)
