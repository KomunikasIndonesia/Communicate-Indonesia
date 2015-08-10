import json
import unittest
from mock import patch

from app.api.sms import app
from google.appengine.ext import ndb, testbed
from app.command.base import NoRouteError, MultipleRouteError
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.i18n import _


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

    @patch('app.api.sms.main.dispatcher')
    def test_request_should_be_logged_in_datastore(self, mock):
        mock.dispatch.return_value = None

        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.user.phone_number,
            'To': '+321',
            'Body': 'jual'
        })

        self.assertEqual(200, res.status_code)

        all_sms = SmsRequest.query().fetch()
        self.assertEqual(1, len(all_sms))

        sms = all_sms[0]
        self.assertEqual('sid', sms.twilio_message_id)
        self.assertTrue(sms.processed)
        self.assertEqual(self.user.phone_number, sms.from_number)
        self.assertEqual('+321', sms.to_number)
        self.assertEqual('jual', sms.body)

    @patch('app.api.sms.main.dispatcher')
    def test_log_bad_request(self, mock):
        mock.dispatch.side_effect = Exception('can not process sms request '
                                              'because of bad action or '
                                              'dispatcher')

        with self.assertRaises(Exception):
            self.app.post('/v1/sms/twilio', data={
                'MessageSid': 'sid',
                'From': self.user.phone_number,
                'To': '+321',
                'Body': 'jual'
            })

        all_sms = SmsRequest.query().fetch()
        self.assertEqual(1, len(all_sms))

        sms = all_sms[0]
        self.assertEqual('sid', sms.twilio_message_id)
        self.assertFalse(sms.processed)
        self.assertEqual(self.user.phone_number, sms.from_number)
        self.assertEqual('+321', sms.to_number)
        self.assertEqual('jual', sms.body)

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

    @patch('app.api.sms.main.dispatcher')
    def test_dispatcher_no_route_error(self, mock):
        mock.dispatch.side_effect = NoRouteError()

        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.user.phone_number,
            'To': '+321',
            'Body': 'jual'
        })

        # should return an sms response to the user
        self.assertEqual(200, res.status_code)
        self.assertEqual('<?xml version="1.0" encoding="UTF-8"?>'
                         '<Response><Sms from="123456" to="+123">'
                         '{}'
                         '</Sms></Response>'.format(_('Unknown command')),
                         res.data)

    @patch('app.api.sms.main.dispatcher')
    def test_dispatcher_multiple_route_error(self, mock):
        mock.dispatch.side_effect = MultipleRouteError()

        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.user.phone_number,
            'To': '+321',
            'Body': 'jual'
        })

        # should return an sms response to the user
        self.assertEqual(200, res.status_code)
        self.assertEqual('<?xml version="1.0" encoding="UTF-8"?>'
                         '<Response><Sms from="123456" to="+123">'
                         '{}'
                         '</Sms></Response>'.format(_('Unknown command')),
                         res.data)

if __name__ == '__main__':
    unittest.main()
