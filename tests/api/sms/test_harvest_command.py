import unittest

from app.api.sms.harvest_action import HarvestCommand
from app.api.sms import app
from app.model.sms_request import SmsRequest
from app.model.user import User

from google.appengine.ext import testbed


class HarvestCommandTest(unittest.TestCase):

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

    def test_harvest_command(self):
        valid_messages = [
            'harvest 20 potato',
            'harvest potato 20',
            'panen 20 potato',
            'panen potato 20'
        ]

        for body in valid_messages:
            self.sms.body = body
            cmd = HarvestCommand(self.sms)
            self.assertTrue(cmd.valid())
            self.assertEqual(20, cmd.amount)
            self.assertEqual('potato', cmd.plant)

    def test_harvest_command_without_harvest(self):
        invalid_messages = [
            'harvest 20',
            'panen 20'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = HarvestCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_harvest_command_without_amount(self):
        invalid_messages = [
            'harvest potato',
            'harvest potato'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = HarvestCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_harvest_command_with_invalid_command(self):
        invalid_messages = [
            'sell 20 potato',
            'sell potato 20',
            'jual 20 potato',
            'jual potato 20'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = HarvestCommand(self.sms)
            self.assertFalse(cmd.valid())
