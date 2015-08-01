import unittest
from app.api.user import app
from app.model.user import User
from google.appengine.ext import ndb, testbed
import json
import time


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

    def test_empty_db(self):
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_entity(self):
        test_user = User(role='farmer', phone_number='1234567',
                         first_name='Kat', last_name='Leigh')
        test_user.put()
        self.assertEqual(1, len(User.query().fetch()))

    def insert(self, **kwargs):
        return self.app.put('/v1/users', data=json.dumps(kwargs))

    def retrieve(self, userid):
        return self.app.get('/v1/users/{0}'.format(userid))

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

        self.assertEqual(None, data['last_name'])
        self.assertEqual(1, len(User.query().fetch()))

    def test_insert_empty(self):
        res = self.insert()

        data = json.loads(res.data)

        self.assertEqual('missing request data', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_without_role(self):
        res = self.insert(phone_number='1234567', first_name='Kat')

        data = json.loads(res.data)

        self.assertEqual('role is required', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_without_phone(self):
        res = self.insert(role='farmer', first_name='Kat')

        data = json.loads(res.data)

        self.assertEqual('phone_number is required', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_without_name(self):
        res = self.insert(role='farmer', phone_number='1234567')

        data = json.loads(res.data)

        self.assertEqual('first_name is required', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_insert_with_undefined_roles(self):
        res = self.insert(role='teacher', phone_number='1234567',
                          first_name='Kat')

        data = json.loads(res.data)

        self.assertTrue('invalid role' in data['error'])
        self.assertTrue('should be: hutan_biru or farmer' in data['error'])
        self.assertEqual(0, len(User.query().fetch()))

    def test_with_different_roles(self):
        self.insert(role='farmer', phone_number='1234567',
                    first_name='Kat', last_name='Leigh')

        self.insert(role='hutan_biru', phone_number='1234567',
                    first_name='Kat', last_name='Leigh')

        self.assertEqual(2, len(User.query().fetch()))

    def test_insert_with_non_strings(self):
        res = self.insert(role='hutan_biru', phone_number=321,
                          first_name='Kat')

        data = json.loads(res.data)

        self.assertEqual('phone_number is not string', data['error'])

        res = self.insert(role='hutan_biru', phone_number='321',
                          first_name=123)

        data = json.loads(res.data)

        self.assertEqual('first_name is not string', data['error'])
        self.assertEqual(0, len(User.query().fetch()))

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

    def test_insert_and_retrieve_wihtout_last_name(self):
        req = self.insert(role='hutan_biru', phone_number='321',
                          first_name='Kat')

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

    def test_retrieve_empty_db(self):
        get = self.retrieve('123')
        res = json.loads(get.data)

        self.assertEqual('user not found', res['error'])

    def test_fetch_empty_db(self):
        fetch = self.fetch()
        res = json.loads(fetch.data)

        self.assertEqual(0, len(res['users']))

    def test_fetch_with_phone_number(self):
        self.insert(role='farmer', phone_number='123',
                    first_name='Erika')
        self.insert(role='hutan_biru', phone_number='321',
                    first_name='Kat')

        fetch = self.fetch(phone_number='123')
        res = json.loads(fetch.data)

        r = res['users']

        self.assertEqual(1, len(r))
        self.assertEqual('123', r[0]['phone_number'])
        self.assertEqual('Erika', r[0]['first_name'])
        self.assertEqual('farmer', r[0]['role'])

    def test_fetch_without_phone_number(self):
        self.insert(role='hutan_biru', phone_number='321',
                    first_name='Kat')
        self.insert(role='farmer', phone_number='123',
                    first_name='Erika')

        fetch = self.fetch()
        res = json.loads(fetch.data)

        r = res['users']

        self.assertEqual(2, len(r))

    def test_fetch_sorted_from_recently_created(self):
        self.insert(role='hutan_biru', phone_number='321',
                    first_name='Kat')
        time.sleep(1)

        self.insert(role='farmer', phone_number='123',
                    first_name='Erika')
        time.sleep(1)

        self.insert(role='hutan_biru', phone_number='531',
                    first_name='Ratna')
        time.sleep(1)

        fetch = self.fetch()
        res = json.loads(fetch.data)

        r = res['users']

        self.assertEqual(3, len(r))
        self.assertGreater(r[0]['ts_created'], r[1]['ts_created'])
        self.assertGreater(r[1]['ts_created'], r[2]['ts_created'])
        self.assertGreater(r[0]['ts_created'], r[2]['ts_created'])


if __name__ == '__main__':
    unittest.main()
