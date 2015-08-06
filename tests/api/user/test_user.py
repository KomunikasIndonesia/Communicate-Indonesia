import unittest
from app.api.user import app
from app.model.district import District
from app.model.user import User
from app.model.config import Config
from google.appengine.ext import ndb, testbed
import json
from base64 import b64encode


class UserTest(unittest.TestCase):

    def setUp(self):
        self.APIKEY = '123456789'

        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.district = District(id='district_id', name='sulawesi')
        self.district.put()

        self.config = Config(apikey=self.APIKEY)
        self.config.put()

        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def headers(self, username=None, apikey=None):
        username = username or 'admin'
        apikey = apikey or self.APIKEY

        return {
            'Authorization':
                'Basic ' + b64encode("{}:{}".format(username, apikey))
        }

    def insert(self, **kwargs):
        headers = self.headers()
        return self.app.post('/v1/users', data=kwargs, headers=headers)

    def retrieve(self, user_id):
        headers = self.headers()
        return self.app.get('/v1/users/{}'.format(user_id), headers=headers)

    def fetch(self, **kwargs):
        headers = self.headers()
        return self.app.get('/v1/users', query_string=kwargs, headers=headers)

    def insert_without_auth(self, **kwargs):
        return self.app.post('/v1/users', data=kwargs)

    def retrieve_without_auth(self, user_id):
        return self.app.get('/v1/users/{}'.format(user_id))

    def fetch_without_auth(self, **kwargs):
        return self.app.get('/v1/users', query_string=kwargs)

    def insert_with_invalid_admin(self, **kwargs):
        headers = self.headers(username='billjobs')
        return self.app.post('/v1/users', data=kwargs, headers=headers)

    def retrieve_with_invalid_admin(self, user_id):
        headers = self.headers(username='billjobs')
        return self.app.get('/v1/users/{}'.format(user_id), headers=headers)

    def fetch_with_invalid_admin(self, **kwargs):
        headers = self.headers(username='billjobs')
        return self.app.get('/v1/users', query_string=kwargs, headers=headers)

    def insert_with_invalid_apikey(self, **kwargs):
        headers = self.headers('admin', '663377')
        return self.app.post('/v1/users', data=kwargs, headers=headers)

    def retrieve_with_invalid_apikey(self, user_id):
        headers = self.headers('admin', '663377')
        return self.app.get('/v1/users/{}'.format(user_id), headers=headers)

    def fetch_with_invalid_apikey(self, **kwargs):
        headers = self.headers('admin', '663377')
        return self.app.get('/v1/users', query_string=kwargs, headers=headers)

    def test_insert_user(self):
        res = self.insert(role='farmer', phone_number='1234567',
                          first_name='Kat', last_name='Leigh',
                          district_id=self.district.key.id())

        data = json.loads(res.data)

        self.assertEqual('farmer', data['role'])
        self.assertEqual('1234567', data['phone_number'])
        self.assertEqual('Kat', data['first_name'])
        self.assertEqual('Leigh', data['last_name'])
        self.assertEqual('district_id', data['district_id'])

        self.assertEqual(1, len(User.query().fetch()))

    def test_insert_without_district(self):
        res = self.insert(role='farmer', phone_number='1234567',
                          first_name='Kat', last_name='Leigh')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('district_id is required', data['error'])

    def test_insert_with_non_existent_district(self):
        res = self.insert(role='farmer', phone_number='1234567',
                          first_name='Kat', last_name='Leigh',
                          district_id='Dsomerandomid')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('Dsomerandomid is an invalid district_id', data['error'])

    def test_insert_without_optional_param(self):
        res = self.insert(role='hutan_biru', phone_number='1234567',
                          first_name='Kat')

        data = json.loads(res.data)

        self.assertEqual('hutan_biru', data['role'])
        self.assertEqual('1234567', data['phone_number'])
        self.assertEqual('Kat', data['first_name'])
        self.assertEqual(None, data['last_name'])

        self.assertEqual(1, len(User.query().fetch()))

    def test_insert_without_role(self):
        res = self.insert(phone_number='1234567', first_name='Kat')

        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('role is required', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_without_phone(self):
        res = self.insert(role='farmer', first_name='Kat')

        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('phone_number is required', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_without_name(self):
        res = self.insert(role='farmer', phone_number='1234567')

        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('first_name is required', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_with_undefined_roles(self):
        res = self.insert(role='teacher', phone_number='1234567',
                          first_name='Kat')

        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertTrue('teacher is an invalid role' in data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_with_different_roles(self):
        self.insert(role='farmer', phone_number='1234567',
                    first_name='Kat', last_name='Leigh',
                    district_id=self.district.key.id())

        self.insert(role='hutan_biru', phone_number='1234567',
                    first_name='Kat', last_name='Leigh')

        self.assertEqual(2, len(User.query().fetch()))

    def test_insert_and_retrieve(self):
        req = self.insert(role='hutan_biru', phone_number='321',
                          first_name='Kat', last_name='Leigh')

        data = json.loads(req.data)

        get = self.retrieve(data['id'])
        res = json.loads(get.data)

        self.assertEqual(data['id'], res['id'])
        self.assertEqual(data['role'], res['role'])
        self.assertEqual(data['phone_number'], res['phone_number'])
        self.assertEqual(data['first_name'], res['first_name'])
        self.assertEqual(data['last_name'], res['last_name'])
        self.assertEqual(data['ts_created'], res['ts_created'])
        self.assertEqual(data['ts_updated'], res['ts_updated'])

        self.assertEqual(1, len(User.query().fetch()))

    def test_insert_and_retrieve_without_last_name(self):
        req = self.insert(role='hutan_biru', phone_number='321',
                          first_name='Kat')

        data = json.loads(req.data)

        get = self.retrieve(data['id'])
        res = json.loads(get.data)

        self.assertEqual(data['id'], res['id'])
        self.assertEqual(data['role'], res['role'])
        self.assertEqual(data['phone_number'], res['phone_number'])
        self.assertEqual(data['first_name'], res['first_name'])
        self.assertEqual(None, res['last_name'])
        self.assertEqual(None, data['last_name'])
        self.assertEqual(data['ts_created'], res['ts_created'])
        self.assertEqual(data['ts_updated'], res['ts_updated'])

        self.assertEqual(1, len(User.query().fetch()))

    def test_retrieve_empty_db(self):
        res = self.retrieve('123')
        data = json.loads(res.data)

        self.assertEqual(404, res.status_code)
        self.assertEqual('this resource does not exist', data['error'])

    def test_fetch_empty_db(self):
        res = self.fetch()
        data = json.loads(res.data)

        self.assertEqual(200, res.status_code)
        self.assertEqual(0, len(data['users']))

    def test_fetch_with_phone_number(self):
        self.insert(role='farmer', phone_number='123',
                    first_name='Erika',
                    district_id=self.district.key.id())
        self.insert(role='hutan_biru', phone_number='321',
                    first_name='Kat')

        res = self.fetch(phone_number='123')
        data = json.loads(res.data)

        r = data['users']

        self.assertEqual(200, res.status_code)
        self.assertEqual(1, len(r))
        self.assertEqual('123', r[0]['phone_number'])
        self.assertEqual('Erika', r[0]['first_name'])
        self.assertEqual('farmer', r[0]['role'])

    def test_fetch_without_phone_number(self):
        self.insert(role='hutan_biru', phone_number='321',
                    first_name='Kat')
        self.insert(role='farmer', phone_number='123',
                    first_name='Erika',
                    district_id=self.district.key.id())

        res = self.fetch()
        data = json.loads(res.data)

        r = data['users']

        self.assertEqual(200, res.status_code)
        self.assertEqual(2, len(r))
        self.assertEqual('123', r[0]['phone_number'])
        self.assertEqual('Erika', r[0]['first_name'])
        self.assertEqual('farmer', r[0]['role'])
        self.assertEqual('district_id', r[0]['district_id'])
        self.assertEqual('321', r[1]['phone_number'])
        self.assertEqual('Kat', r[1]['first_name'])
        self.assertEqual('hutan_biru', r[1]['role'])

    def test_insert_without_auth(self):
        res = self.insert_without_auth(role='farmer', phone_number='1234567',
                                       first_name='Kat', last_name='Leigh',
                                       district_id=self.district.key.id())

        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('unauthorized access', data['error'])

        self.assertEqual(0, len(User.query().fetch()))

    def test_retrieve_without_auth(self):
        req = self.insert(role='hutan_biru', phone_number='321',
                          first_name='Kat', last_name='Leigh')

        data = json.loads(req.data)

        res = self.retrieve_without_auth(data['id'])
        r = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('unauthorized access', r['error'])

    def test_fetch_without_auth(self):
        self.insert(role='farmer', phone_number='123',
                    first_name='Erika',
                    district_id=self.district.key.id())

        res = self.fetch_without_auth(phone_number='123')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('unauthorized access', data['error'])

    def test_insert_with_invalid_admin(self):
        res = self.insert_with_invalid_admin(role='farmer',
                                             phone_number='1234567',
                                             first_name='Kat',
                                             district_id=self.district.key.id())

        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('unauthorized access', data['error'])

        self.assertEqual(0, len(User.query().fetch()))

    def test_retrieve_with_invalid_admin(self):
        req = self.insert(role='hutan_biru', phone_number='321',
                          first_name='Kat', last_name='Leigh')

        data = json.loads(req.data)

        res = self.retrieve_with_invalid_admin(data['id'])
        r = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('unauthorized access', r['error'])

    def test_fetch_with_invalid_admin(self):
        self.insert(role='farmer', phone_number='123',
                    first_name='Erika',
                    district_id=self.district.key.id())

        res = self.fetch_with_invalid_admin(phone_number='123')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('unauthorized access', data['error'])

    def test_insert_with_invalid_apikey(self):
        res = self.insert_with_invalid_apikey(role='farmer',
                                              phone_number='1234567',
                                              first_name='Kat',
                                              district_id=self.district.key.id())

        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('invalid apikey', data['error'])

        self.assertEqual(0, len(User.query().fetch()))

    def test_retrieve_with_invalid_apikey(self):
        req = self.insert(role='hutan_biru', phone_number='321',
                          first_name='Kat', last_name='Leigh')

        data = json.loads(req.data)

        res = self.retrieve_with_invalid_apikey(data['id'])
        r = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('invalid apikey', r['error'])

    def test_fetch_with_invalid_apikey(self):
        self.insert(role='farmer', phone_number='123',
                    first_name='Erika',
                    district_id=self.district.key.id())

        res = self.fetch_with_invalid_apikey(phone_number='123')
        data = json.loads(res.data)

        self.assertEqual(400, res.status_code)
        self.assertEqual('invalid apikey', data['error'])


if __name__ == '__main__':
    unittest.main()
