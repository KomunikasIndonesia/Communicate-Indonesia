import unittest

from app.api.sms.sell_action import SellCommand
from app.model.sms_request import SmsRequest


class SellCommandTest(unittest.TestCase):

    def test_sell_command(self):
        valid_messages = [
            'sell 20 potato',
            'sell potato 20',
            'jual 20 potato',
            'jual potato 20'
        ]

        for body in valid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = SellCommand(sms)
            self.assertTrue(cmd.valid())
            self.assertEqual(20, cmd.amount)
            self.assertEqual('potato', cmd.plant)

    def test_ignore_case(self):
        valid_messages = [
            'SeLL 20 potato',
        ]

        for body in valid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = SellCommand(sms)
            self.assertTrue(cmd.valid())
            self.assertEqual(20, cmd.amount)
            self.assertEqual('potato', cmd.plant)

    def test_sell_command_without_sell(self):
        invalid_messages = [
            'sell 20',
            'jual 20'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = SellCommand(sms)
            self.assertFalse(cmd.valid())

    def test_sell_command_without_amount(self):
        invalid_messages = [
            'sell potato',
            'jual potato'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = SellCommand(sms)
            self.assertFalse(cmd.valid())

    def test_sell_command_with_invalid_command(self):
        invalid_messages = [
            'harvest 20 potato',
            'harvest potato 20',
            'panen 20 potato',
            'panen potato 20'
        ]

        for body in invalid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = SellCommand(sms)
            self.assertFalse(cmd.valid())

    def test_sell_multi_word(self):
        valid_messages = [
            'sell 20 sweet potato',
            'sell sweet potato 20',
            'jual 20 sweet potato',
            'jual sweet potato 20'
        ]

        for body in valid_messages:
            sms = SmsRequest()
            sms.body = body
            cmd = SellCommand(sms)

            self.assertTrue(cmd.valid())
            self.assertEqual(20, cmd.amount)
            self.assertEqual('sweet potato', cmd.plant)

    def test_sell_command_should_ignore_cases(self):
        valid_messages = {
            'sell 20 Potato': 'potato',
            'sell 20 POTATO': 'potato',
            'sell 20 Chinese Broccoli': 'chinese broccoli',
            'sell 20 CHINESE BROCCOLI': 'chinese broccoli'
        }

        for body, v in valid_messages.iteritems():
            sms = SmsRequest()
            sms.body = body
            cmd = SellCommand(sms)
            self.assertEqual(v, cmd.plant)
