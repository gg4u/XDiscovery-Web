from __future__ import absolute_import
import json
import base64

from django.test import LiveServerTestCase
from django.contrib.auth.models import User

from ..models import Map, MapTopic
from ..maps import save_map
from .test_utils import MapTestCaseMixIn, get_test_data


__all__ = ['MapTestCase', 'MapUploadTestCase']


class MapTestCase(LiveServerTestCase, MapTestCaseMixIn):

    def test_html(self):
        resp = self.client.get('/atlas/', follow=True)
        self.assertContains(resp, '/frontend/styles/')

    def test_empty(self):
        resp = self.client.get('/api-atlas/map', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_load_map(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        mp = Map.objects.get()
        self.assertEqual(mp.title, 'titolo')
        self.assertEqual(mp.node_count, 18)
        self.assertEqual(mp.node_titles, [u'Leopard', u'Lion', u'Cheetah', u'Asiatic lion', u'Transvaal lion', u'Southwest African lion', u'Indochinese leopard', u'African leopard', u'North China leopard', u'Felis', u'Big cat', u'Arabian leopard', u'Striped hyena', u'Indian leopard', u'Sri Lankan leopard', u'Javan leopard', u'Lycaon pictus', u'Northwest African cheetah'])
        self.assertEqual(mp.last_node_title, 'Cheetah')

    def test_list(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api-atlas/map', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)
        obj = data['map'][0]
        self.assertNotIn('map_data', obj)
        self.assertNotIn('path', obj)

    def test_list_sort_popular(self):
        self.create_maps(10)
        resp = self.client.get('/api-atlas/map',
                               {'ordering': 'popularity'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(10)],
                         [obj['title'] for obj in data['map']])
        # reverse
        resp = self.client.get('/api-atlas/map',
                               {'ordering': '-popularity'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(9, -1, -1)],
                         [obj['title'] for obj in data['map']])

    def test_list_sort_date_created(self):
        self.create_maps(10)
        resp = self.client.get('/api-atlas/map',
                               {'ordering': 'date_created'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(9, -1, -1)],
                         [obj['title'] for obj in data['map']])
        # reverse
        resp = self.client.get('/api-atlas/map',
                               {'ordering': '-date_created'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)
        self.assertEqual([str(i) for i in range(10)],
                         [obj['title'] for obj in data['map']])

    def test_list_filter_featured(self):
        self.create_maps(10, featured=False)
        resp = self.client.get('/api-atlas/map',
                               {'featured': '1'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)
        # not featured
        resp = self.client.get('/api-atlas/map',
                               {'featured': '0'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 10)

    def test_list_search_empty(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api-atlas/map',
                               {'topic': 'xxxxxxxxxxx'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_list_search(self):
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api-atlas/map',
                               {'topic': 'lion'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)
        # case-insensitive
        resp = self.client.get('/api-atlas/map',
                               {'topic': 'liON'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)

    def test_list_search_unpublished(self):
        mapp = save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        mapp.status = Map.STATUS_UNPUBLISHED
        save_map(mapp)
        resp = self.client.get('/api-atlas/map',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_list_search_deleted(self):
        mapp = save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        mapp.status = Map.STATUS_DELETED
        save_map(mapp)
        resp = self.client.get('/api-atlas/map',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_list_search_comma(self):
        save_map(Map(map_data=get_test_data('sharing_2.json')))
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api-atlas/map',
                               {'topic': ['camillo borghese, 6th']},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)

    def test_list_search_comma_2(self):
        save_map(Map(map_data=get_test_data('sharing_2.json')))
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api-atlas/map',
                               {'topic': ['camillo borghese, 7th']},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_list_search_comma_3(self):
        save_map(Map(map_data=get_test_data('sharing_2.json')))
        save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api-atlas/map',
                               {'topic': ['camillo borghese, lion']},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 0)

    def test_list_search_2_terms(self):
        mp = save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        topics = [u'African leopard', u'Arabian leopard', u'Asiatic lion', u'Big cat', u'Cheetah', u'Felis', u'Indian leopard', u'Indochinese leopard', u'Javan leopard', u'Leopard', u'Lion', u'Lycaon pictus', u'North China leopard', u'Northwest African cheetah', u'Southwest African lion', u'Sri Lankan leopard', u'Striped hyena', u'titolo', u'Transvaal lion']
        # Topics need to be saved in db
        self.assertEqual(
            topics,
            list(MapTopic.objects.order_by('topic').values_list('topic', flat=True)))
        self.assertEqual(
            topics,
            list(mp.maptopic_set.order_by('topic').values_list('topic', flat=True)))
        resp = self.client.get('/api-atlas/map',
                               {'topic': ['lion', 'felis']},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)
        # case-insensitive
        resp = self.client.get('/api-atlas/map',
                               {'topic': 'liON'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(len(data['map']), 1)

    def test_detail(self):
        mp = save_map(Map(map_data=get_test_data('sharingAppWeb.json')))
        resp = self.client.get('/api-atlas/map/{}'.format(mp.pk),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertNotIn('map_data', data)
        self.assertIn('nodes', data)
        self.assertIn('graph', data)
        self.assertEqual(data['popularity'], 0)
        # popularity is increased
        resp = self.client.get('/api-atlas/map/{}'.format(mp.pk),
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['popularity'], 1)

class MapUploadTestCase(LiveServerTestCase, MapTestCaseMixIn):

    def test_no_auth(self):
        resp = self.client.post('/api-atlas/map',
                                get_test_data('sharingAppWeb.json'),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 401)
        self.assertFalse(Map.objects.count())

    def test_create(self):
        user = User(username='test', email='test@example.com')
        user.set_password('pass')
        user.save()
        resp = self.client.post(
            '/api-atlas/map',
            get_test_data('sharingAppWeb.json'),
            content_type='application/json',
            HTTP_AUTHORIZATION='Basic {}'.format(base64.b64encode('test:pass')))
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(Map.objects.count(), 1)
        mapp = Map.objects.get()
        self.assertEqual(mapp.status, 'U')
