import unittest
from app.api.user import app
from app.model.user import User
from google.appengine.ext import ndb, testbed
import json


class UserTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def insert(self, **kwargs):
        return self.app.post('/v1/users', data=kwargs)

    def retrieve(self, user_id):
        return self.app.get('/v1/users/{0}'.format(user_id))

    def fetch(self, **kwargs):
        return self.app.get('/v1/users', query_string=kwargs)

    def test_insert_user(self):
        res = self.insert(role='farmer', phone_number='1234567',
                          first_name='Kat', last_name='Leigh')

        data = json.loads(res.data)

        self.assertEqual('farmer', data['role'])
        self.assertEqual('1234567', data['phone_number'])
        self.assertEqual('Kat', data['first_name'])
        self.assertEqual('Leigh', data['last_name'])

        self.assertEqual(1, len(User.query().fetch()))

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
                    first_name='Kat', last_name='Leigh')

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
                    first_name='Erika')
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
                    first_name='Erika')

        res = self.fetch()
        data = json.loads(res.data)

        r = data['users']

        self.assertEqual(200, res.status_code)
        self.assertEqual(2, len(r))
        self.assertEqual('123', r[0]['phone_number'])
        self.assertEqual('Erika', r[0]['first_name'])
        self.assertEqual('farmer', r[0]['role'])
        self.assertEqual('321', r[1]['phone_number'])
        self.assertEqual('Kat', r[1]['first_name'])
        self.assertEqual('hutan_biru', r[1]['role'])


if __name__ == '__main__':
    unittest.main()
