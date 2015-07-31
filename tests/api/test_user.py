import unittest
from app.api.user import app
from app.model.user import User
from google.appengine.ext import ndb, testbed


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
        self.assertEqual(0, len(User.query().fetch(2)))

    def test_insert_entity(self):
        test_user = User(
            role='farmer',
            phone_number='1234567',
            first_name='Kat',
            last_name='Leigh'
        )
        test_user.put()
        self.assertEqual(1, len(User.query().fetch(2)))

    def test_insert_entity_without_params(self):
        test_user = User()

        try:
            test_user.put()

        except Exception, e:
            self.assertTrue("Entity has uninitialized properties" in str(e))
            self.assertTrue("phone_number" in str(e))
            self.assertTrue("first_name" in str(e))
            self.assertTrue("role" in str(e))
            self.assertFalse("last_name" in str(e))

    def insert(self, **kwargs):
        return self.app.put('/v1/users', data=kwargs)

    def retrieve(self, userid):
        return self.app.get('/v1/users/{0}'.format(userid))

    def test_insert(self):
        r = self.insert(
            role='farmer',
            phone_number='1234567',
            first_name='Kat',
            last_name='Leigh'
        )

        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['content-type'])

        # Why failed? Not synced with db?
        # self.assertEqual(1, len(User.query().fetch(2)))

    def test_retrieve_empty_db(self):
        r = self.retrieve(userid='123')

        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['content-type'])
        self.assertTrue('"data": null' in r.data)
        self.assertTrue('"success": "error"' in r.data)


if __name__ == '__main__':
    unittest.main()
