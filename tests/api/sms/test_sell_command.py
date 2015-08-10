import unittest
from mock import patch

from app.api.sms.sell_action import SellCommand, SellAction
from app.api.sms import app
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.model.farm import Farm
from app.i18n import _

from google.appengine.ext import testbed


class SellCommandTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.sms = SmsRequest()
        self.sms.from_number = '6072809193'

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.user = User(role='farmer', phone_number='6072809193',
                         first_name='Kat', district_id='sul123')
        self.user.put()

    def test_sell_command(self):
        valid_messages = [
            'sell 20 potato',
            'sell potato 20',
            'jual 20 potato',
            'jual potato 20'
        ]

        for body in valid_messages:
            self.sms.body = body
            cmd = SellCommand(self.sms)
            self.assertTrue(cmd.valid())
            self.assertEqual(20, cmd.amount)
            self.assertEqual('potato', cmd.sell)

    def test_sell_command_without_sell(self):
        invalid_messages = [
            'sell 20',
            'jual 20'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = SellCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_sell_command_without_amount(self):
        invalid_messages = [
            'sell potato',
            'sell potato'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = SellCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_sell_command_with_invalid_command(self):
        invalid_messages = [
            'harvest 20 potato',
            'harvest potato 20',
            'panen 20 potato',
            'panen potato 20'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = SellCommand(self.sms)
            self.assertFalse(cmd.valid())

    @patch('app.api.sms.main.dispatcher')
    def test_sell_action(self, mock):
        mock.dispatch.return_value = None

        valid_messages = [
            'sell 20 potato',
            'sell potato 20',
            'jual 20 potato',
            'jual potato 20'
        ]

        for body in valid_messages:
            self.app.post('/v1/sms/twilio', data={
                'MessageSid': 'sid',
                'From': self.user.phone_number,
                'To': '+321',
                'Body': body
            })

        all_sms = SmsRequest.query().fetch()
        self.assertEqual(4, len(all_sms))

        for sms in all_sms:
            cmd = SellCommand(sms)
            res_msg = SellAction(cmd).execute()
            self.assertEqual(_('Sell command succeeded'), res_msg)

        all_data = Farm.query().fetch()
        self.assertEqual(4, len(all_data))

        for data in all_data:
            self.assertEqual('sell', data.action)
            self.assertEqual('potato', data.crop_name)
            self.assertEqual(20, data.quantity)
            self.assertEqual('sul123', data.district_id)
