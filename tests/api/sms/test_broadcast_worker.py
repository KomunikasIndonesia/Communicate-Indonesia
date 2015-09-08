import unittest
from mock import patch
import json
from twilio.rest.resources import Messages
from app.api.sms.broadcast_worker import app
from app.model.config import Config
from google.appengine.ext import testbed


class BroadcastWorkerTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        Config(id='test', twilio_account_sid='SID',
               twilio_auth_token='TOKEN', twilio_phone_number='+321').put()

        self.resource = Messages('foo', ('SID', 'TOKEN'))

    def _broadcast_sms(self, **kwargs):
        return self.app.post('/v1/sms/broadcast', data=kwargs)

    @patch('twilio.rest.resources.base.make_request')
    @patch('twilio.rest.resources.base.ListResource.create_instance')
    def test_single_phone_number(self, req_mock, ins_mock):
        task = json.dumps({'phone_numbers': ['+111'],
                           'message': 'hello'})
        res = self._broadcast_sms(task=task)
        r = json.loads(res.data)

        self.assertEqual(1, r['farmers_sent'])
        self.assertEqual('hello', r['body'])

    @patch('twilio.rest.resources.base.make_request')
    @patch('twilio.rest.resources.base.ListResource.create_instance')
    def test_multiple_phone_numbers(self, req_mock, ins_mock):
        task = json.dumps({'phone_numbers': ['+111', '+222', '+333'],
                           'message': 'hello people'})
        res = self._broadcast_sms(task=task)
        r = json.loads(res.data)

        self.assertEqual(3, r['farmers_sent'])
        self.assertEqual('hello people', r['body'])
