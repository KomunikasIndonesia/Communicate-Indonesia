import unittest

from app.api.sms.broadcast_action import BroadcastCommand
from app.model.sms_request import SmsRequest
from app.model.user import User


class BroadcastCommandTest(unittest.TestCase):

    def _broadcast_cmd_hb(self, body):
        sms = SmsRequest()
        sms.user = User(role='hutan_biru')
        sms.body = body
        return BroadcastCommand(sms)

    def _broadcast_cmd_leader(self, body):
        sms = SmsRequest()
        sms.user = User(role='district_leader')
        sms.body = body
        return BroadcastCommand(sms)

    def test_broadcast_command_from_hb(self):
        valid_messages = [
            'broadcast lompoko hello farmers',
            'kirim lompoko hello farmers',
            'broadcast everyone hello farmers',
            'kirim semua hello farmers',
        ]

        for body in valid_messages[:2]:
            cmd = self._broadcast_cmd_hb(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('lompoko', cmd.send_to)
            self.assertEqual('hello farmers', cmd.msg)

        for body in valid_messages[-2:]:
            cmd = self._broadcast_cmd_hb(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('everyone', cmd.send_to)
            self.assertEqual('hello farmers', cmd.msg)

    def test_broadcast_command_short_from_hb(self):
        valid_messages = [
            'broadcast lompoko hello',
            'kirim lompoko hello',
            'broadcast everyone hello',
            'kirim semua hello'
        ]

        for body in valid_messages[:2]:
            cmd = self._broadcast_cmd_hb(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('lompoko', cmd.send_to)
            self.assertEqual('hello', cmd.msg)

        for body in valid_messages[-2:]:
            cmd = self._broadcast_cmd_hb(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('everyone', cmd.send_to)
            self.assertEqual('hello', cmd.msg)

    def test_broadcast_command_invalid_from_hb(self):
        invalid_messages = [
            'broadcast lompoko',
            'broadcast everyone',
            'kirim lompoko',
            'kirim semua',
            'broadcast',
            'kirim',
            'sell hello world',
            'jual hello world'
        ]

        for body in invalid_messages:
            cmd = self._broadcast_cmd_hb(body)
            self.assertFalse(cmd.valid())

    def test_broadcast_command_from_leader(self):
        valid_messages = [
            'broadcast hello people',
            'kirim hello people',
            'broadcast lompoko hello people',
            'kirim lompoko hello people',
        ]

        for body in valid_messages[:2]:
            cmd = self._broadcast_cmd_leader(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('hello', cmd.send_to)
            self.assertEqual('people', cmd.msg)

        for body in valid_messages[-2:]:
            cmd = self._broadcast_cmd_leader(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('lompoko', cmd.send_to)
            self.assertEqual('hello people', cmd.msg)

    def test_broadcast_command_short_from_leader(self):
        valid_messages = [
            'broadcast hello',
            'kirim hello',
            'broadcast lompoko hello',
            'kirim lompoko hello'
        ]

        for body in valid_messages[:2]:
            cmd = self._broadcast_cmd_leader(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('hello', cmd.send_to)
            self.assertEqual(' ', cmd.msg)

        for body in valid_messages[-2:]:
            cmd = self._broadcast_cmd_leader(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('lompoko', cmd.send_to)
            self.assertEqual('hello', cmd.msg)

    def test_broadcast_command_long_from_leader(self):
        valid_messages = [
            'broadcast hello friends in sulawesi!',
            'kirim hello friends in sulawesi!',
            'broadcast lompoko hello friends in sulawesi!',
            'kirim lompoko hello friends in sulawesi!'
        ]

        for body in valid_messages[:2]:
            cmd = self._broadcast_cmd_leader(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('hello', cmd.send_to)
            self.assertEqual('friends in sulawesi!', cmd.msg)

        for body in valid_messages[-2:]:
            cmd = self._broadcast_cmd_leader(body)
            self.assertTrue(cmd.valid())
            self.assertEqual('lompoko', cmd.send_to)
            self.assertEqual('hello friends in sulawesi!', cmd.msg)

    def test_broadcast_command_invalid_from_leader(self):
        invalid_messages = [
            'broadcast',
            'kirim',
            'sell hello world',
            'jual hello world'
        ]

        for body in invalid_messages:
            cmd = self._broadcast_cmd_leader(body)
            self.assertFalse(cmd.valid())
