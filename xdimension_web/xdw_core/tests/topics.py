from __future__ import absolute_import
import json

from django.test import TestCase

from ..models import MapTopic
from .test_utils import MapTestCaseMixIn

__all__ = ['TopicTestCase']


class TopicTestCase(TestCase, MapTestCaseMixIn):

    def test_list_empty(self):
        resp = self.client.get('/api/topic')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('topic', data)
        self.assertEqual(data['topic'], [])

    def test_list(self):
        self.create_maps(10)
        resp = self.client.get('/api/topic')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('topic', data)
        self.assertEqual(len(data['topic']), 10)
        self.assertEqual(
            data['topic'],
            [{u'topic': u'leopard'},
             {u'topic': u'lion'},
             {u'topic': u'cheetah'},
             {u'topic': u'asiatic lion'},
             {u'topic': u'transvaal lion'},
             {u'topic': u'southwest african lion'},
             {u'topic': u'indochinese leopard'},
             {u'topic': u'african leopard'},
             {u'topic': u'north china leopard'},
             {u'topic': u'felis'}])

    def test_list_filter(self):
        self.create_maps(10)
        resp = self.client.get('/api/topic', {'q': 'lio'})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertIn('topic', data)
        self.assertEqual(len(data['topic']), 4)
        self.assertEqual(
            data['topic'],
            [{u'topic': u'lion'},
             {u'topic': u'asiatic lion'},
             {u'topic': u'transvaal lion'},
             {u'topic': u'southwest african lion'}])
