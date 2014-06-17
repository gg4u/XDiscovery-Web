from django.test import TestCase

from xdimension_web.xdw_core.tests.test_utils import MapTestCaseMixIn


class WebTestCase(TestCase, MapTestCaseMixIn):

    def test_no_map(self):
        resp = self.client.get('/en/graph/12', follow=True)
        self.assertEqual(resp.status_code, 404)

    def test_map(self):
        map_ = self.create_maps(1)[0]
        resp = self.client.get('/en/graph/{}'.format(map_.pk))
        self.assertEqual(resp.status_code, 200)
