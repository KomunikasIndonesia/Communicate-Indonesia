import json
import unittest
from app.api.district import app
from google.appengine.ext import ndb, testbed


class DistrictTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def insert(self, *args, **kwargs):
        return self.app.post('/v1/districts', data=kwargs)

    def list(self, *args, **kwargs):
        return self.app.get('/v1/districts', query_string=kwargs)

    def fetch(self, district_id, **kwargs):
        return self.app.get('/v1/districts/' + district_id, query_string=kwargs)

    def test_insert_district(self):
        res = self.insert(name='sulawesi')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual('sulawesi', data['name'])
        self.assertIsNotNone(data['ts_created'])
        self.assertIsNotNone(data['ts_updated'])

    def test_insert_without_name(self):
        res = self.insert(name=None)
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('name is required', data['error'])

    def test_list_one_district(self):
        self.insert(name='sulawesi')
        res = self.list()
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(1, len(data['districts']))

        district = data['districts'][0]
        self.assertEqual('sulawesi', district['name'])
        self.assertIsNotNone(district['ts_created'])
        self.assertIsNotNone(district['ts_updated'])

    def test_insert_should_abort_on_existing(self):
        self.insert(name='sulawesi')
        res = self.insert(name='sulawesi')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('district sulawesi is already registered', data['error'])

    def test_list_should_order_by_created_time(self):
        self.insert(name='sulawesi')
        self.insert(name='new york')

        res = self.list()
        data = json.loads(res.data)
        districts = data['districts']

        self.assertEqual(2, len(districts))
        self.assertEqual('new york', districts[0]['name'])
        self.assertEqual('sulawesi', districts[1]['name'])

    def test_list_should_filter_by_name(self):
        self.insert(name='sulawesi')
        self.insert(name='new york')

        res = self.list(name='new york')
        data = json.loads(res.data)
        districts = data['districts']

        self.assertEqual(1, len(districts))
        self.assertEqual('new york', districts[0]['name'])

    def test_get_by_id(self):
        res = self.insert(name='sulawesi')
        expected = json.loads(res.data)

        res = self.fetch(expected['id'])
        fetched = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(expected, fetched)
