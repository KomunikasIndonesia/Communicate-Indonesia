import unittest

from app.api.sms.broadcast_action import BroadcastCommand
from app.model.sms_request import SmsRequest
from app.model.user import User


class BroadcastCommandTest(unittest.TestCase):

    def _broadcast_cmd(self, body):
        sms = SmsRequest()
        sms.user = User()
        sms.body = body
        return BroadcastCommand(sms)

    def test_broadcast_command(self):
        valid_messages = [
            'broadcast lompoko hello farmers',
            'kirim lompoko hello farmers',
            'broadcast everyone hello farmers',
            'kirim semua hello farmers',
        ]

        for body in valid_messages[:2]:
            cmd = self._broadcast_cmd(body)
            self.assertTrue(cmd.valid())
            self.assertEqual(None, cmd.district)
            self.assertEqual('lompoko hello farmers', cmd.msg)

        for body in valid_messages[-2:]:
            cmd = self._broadcast_cmd(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('everyone', cmd.district)
            self.assertEqual('hello farmers', cmd.msg)

    def test_broadcast_command_short(self):
        valid_messages = [
            'broadcast lompoko hello',
            'kirim lompoko hello',
            'broadcast everyone hello',
            'kirim semua hello'
        ]

        for body in valid_messages[:2]:
            cmd = self._broadcast_cmd(body)
            self.assertTrue(cmd.valid())
            self.assertEqual(None, cmd.district)
            self.assertEqual('lompoko hello', cmd.msg)

        for body in valid_messages[-2:]:
            cmd = self._broadcast_cmd(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('everyone', cmd.district)
            self.assertEqual('hello', cmd.msg)

    def test_broadcast_command_one_word(self):
        valid_messages = [
            'broadcast hello',
            'kirim hello'
        ]

        for body in valid_messages:
            cmd = self._broadcast_cmd(body)
            self.assertTrue(cmd.valid())
            self.assertEqual(None, cmd.district)
            self.assertEqual('hello', cmd.msg)

    def test_broadcast_command_multiwords_district(self):
        valid_messages = [
            'broadcast new york hello',
            'kirim new york hello'
        ]

        # multiwords will be checked on BroadcastAction
        for body in valid_messages:
            cmd = self._broadcast_cmd(body)
            self.assertTrue(cmd.valid())
            self.assertEqual(None, cmd.district)
            self.assertEqual('new york hello', cmd.msg)

    def test_broadcast_command_invalid(self):
        invalid_messages = [
            'broadcast',
            'kirim',
            'sell hello world',
            'jual hello world'
        ]

        for body in invalid_messages:
            cmd = self._broadcast_cmd(body)
            self.assertFalse(cmd.valid())
