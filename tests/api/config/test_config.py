import unittest
from app.api.config import app
from app.model.config import Config
from google.appengine.ext import ndb, testbed
import json


class UserTest(unittest.TestCase):

    def setUp(self):
        self.ADMIN = 'admin'
        self.APIKEY = '123456789'

        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def config(self, **kwargs):
        return self.app.get('/v1/config', query_string=kwargs)

    def test_get_config(self):
        res = self.config()
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual({
            'admin_username': None,
            'admin_apikey': None
        }, data)

    def test_update_config(self):
        res = self.config(update='true',
                          admin_username='kat',
                          admin_apikey='123')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual('kat', data['admin_username'])
        self.assertEqual('123', data['admin_apikey'])

        self.assertEqual(1, len(Config.query().fetch()))

    def test_update_config_without_update(self):
        res = self.config(admin_username='kat',
                          admin_apikey='123')
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual({
            'admin_username': None,
            'admin_apikey': None
        }, data)

    def test_update_config_without_username(self):
        res = self.config(update='true',
                          admin_apikey='123')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('missing required parameters', data['error'])

    def test_update_config_without_apikey(self):
        res = self.config(update='true',
                          admin_username='kat')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('missing required parameters', data['error'])


if __name__ == '__main__':
    unittest.main()
