from __future__ import absolute_import
import json

from django.test import TestCase

from ..models import MapTopic, Map, Topic
from .test_utils import MapTestCaseMixIn
from ..maps import save_map, delete_map

__all__ = ['TopicTestCase']


class TopicTestCase(TestCase, MapTestCaseMixIn):

    def test_list_empty(self):
        resp = self.client.get('/api/topic')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('topic', data)
        self.assertEqual(data['topic'], [])

    def test_topic_create(self):
        mp_1 = self.create_maps(1)[0]
        self.assertEqual(Topic.objects.count(), 18)
        mp_2 = self.create_maps(1)[0]
        self.assertEqual(Topic.objects.count(), 18)
        delete_map(mp_1)
        self.assertEqual(Topic.objects.count(), 18)
        delete_map(mp_2)
        self.assertEqual(Topic.objects.count(), 0)

    def test_topic_create_2(self):
        mp_1 = self.create_maps(1)[0]
        self.assertEqual(Topic.objects.count(), 18)
        mp_1.status = Map.STATUS_DELETED
        save_map(mp_1)
        self.assertEqual(Topic.objects.count(), 0)

    def test_list(self):
        self.create_maps(10)
        resp = self.client.get('/api/topic')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('topic', data)
        self.assertEqual(len(data['topic']), 10)
        self.assertEqual(
            data['topic'],
            [{u'topic': u'Arabian leopard'},
             {u'topic': u'Felis'},
             {u'topic': u'Indochinese leopard'},
             {u'topic': u'Lycaon pictus'},
             {u'topic': u'Leopard'},
             {u'topic': u'Asiatic lion'},
             {u'topic': u'Big cat'},
             {u'topic': u'Transvaal lion'},
             {u'topic': u'African leopard'},
             {u'topic': u'Indian leopard'}])

    def test_list_filter(self):
        self.create_maps(10)
        resp = self.client.get('/api/topic', {'q': 'lio'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('topic', data)
        self.assertEqual(len(data['topic']), 4)
        self.assertEqual(
            data['topic'],
            [{u'topic': u'Asiatic lion'},
             {u'topic': u'Lion'},
             {u'topic': u'Southwest African lion'},
             {u'topic': u'Transvaal lion'}])

    def test_unpublished(self):
        self.create_maps(10, status=Map.STATUS_UNPUBLISHED)
        resp = self.client.get('/api/topic', {'q': 'lio'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('topic', data)
        self.assertEqual(len(data['topic']), 0)
