import unittest

from app.api.sms.harvest_action import HarvestCommand
from app.model.sms_request import SmsRequest


class HarvestCommandTest(unittest.TestCase):

    def test_harvest_command(self):
        valid_messages = [
            'harvest 20 potato',
            'harvest potato 20',
            'panen 20 potato',
            'panen potato 20'
        ]

        for body in valid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = HarvestCommand(sms)
            self.assertTrue(cmd.valid())
            self.assertEqual(20, cmd.amount)
            self.assertEqual('potato', cmd.plant)

    def test_harvest_command_without_harvest(self):
        invalid_messages = [
            'harvest 20',
            'panen 20'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = HarvestCommand(sms)
            self.assertFalse(cmd.valid())

    def test_harvest_command_without_amount(self):
        invalid_messages = [
            'harvest potato',
            'harvest potato'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = HarvestCommand(sms)
            self.assertFalse(cmd.valid())

    def test_harvest_command_with_invalid_command(self):
        invalid_messages = [
            'sell 20 potato',
            'sell potato 20',
            'jual 20 potato',
            'jual potato 20'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = HarvestCommand(sms)
            self.assertFalse(cmd.valid())
