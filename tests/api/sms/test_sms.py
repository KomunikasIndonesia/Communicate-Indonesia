import json
import unittest
from mock import patch

from app.api.sms import app
from google.appengine.ext import ndb, testbed
from app.model.user import User


class SmsTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.get_context().clear_cache()

        self.user = User(role='farmer', phone_number='+123', first_name='name')
        self.user.put()

    def tearDown(self):
        self.testbed.deactivate()

    @patch('app.api.sms.main.dispatcher')
    def test_request_with_sms_response(self, mock):
        mock.dispatch.return_value = 'response message'

        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.user.phone_number,
            'To': '+321',
            'Body': 'jual'
        })

        self.assertEqual(200, res.status_code)
        self.assertEqual('<?xml version="1.0" encoding="UTF-8"?>'
                         '<Response><Sms from="123456" to="+123">'
                         'response message'
                         '</Sms></Response>', res.data)

    @patch('app.api.sms.main.dispatcher')
    def test_request_without_sms_response(self, mock):
        mock.dispatch.return_value = None

        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.user.phone_number,
            'To': '+321',
            'Body': 'jual'
        })

        self.assertEqual(200, res.status_code)
        self.assertEqual('<?xml version="1.0" encoding="UTF-8"?>'
                         '<Response />', res.data)

    def test_unknown_from_number(self):
        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': '+111',
            'To': '+321',
            'Body': 'jual'
        })

        self.assertEqual(400, res.status_code)
        self.assertEqual('The phone number +111 does not belong to a user',
                         json.loads(res.data)['error'])


if __name__ == '__main__':
    unittest.main()
