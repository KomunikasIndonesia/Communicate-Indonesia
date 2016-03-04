import unittest
from app.api.sms.register_action import RegisterCommand
from app.model.sms_request import SmsRequest


class RegisterCommandTest(unittest.TestCase):

    def setUp(self):
        self.sms = SmsRequest()

    def test_register_command(self):
        valid_messages = {
            'register potato weight': 'weight',
            'register potato berat': 'weight',
            'daftar potato weight': 'weight',
            'daftar potato berat': 'weight',
            'mendaftar potato weight': 'weight',
            'mendaftar potato berat': 'weight',
            'register potato count': 'count',
            'register potato biji': 'count',
            'register potato volume': 'volume',
        }

        for body, unit_type in valid_messages.items():
            self.sms.body = body
            cmd = RegisterCommand(self.sms)
            self.assertTrue(cmd.valid())
            self.assertEqual('potato', cmd.plant)
            self.assertEqual(unit_type, cmd.unit_type)

    def test_register_command_without_plant(self):
        invalid_messages = [
            'register weight',
            'daftar weight',
            'mendaftar weight',
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = RegisterCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_register_command_without_unit_type(self):
        invalid_messages = [
            'register potato',
            'daftar potato',
            'mendaftar potato'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = RegisterCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_register_command_with_invalid_unit_type(self):
        invalid_messages = [
            'register potato blah',
            'daftar potato stuff',
            'mendaftar potato coun'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = RegisterCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_register_command_should_ignore_cases(self):
        valid_messages = {
            'Register Potato Weight': ('potato', 'weight'),
            'Daftar Potato Berat': ('potato', 'weight'),
            'MenDaftar Potato count': ('potato', 'count'),
            'MenDaftar Potato biji': ('potato', 'count'),
            'Daftar Potato Volume': ('potato', 'volume'),
        }

        for body, (plant, unit_type) in valid_messages.iteritems():
            self.sms.body = body
            cmd = RegisterCommand(self.sms)
            self.assertEqual(plant, cmd.plant)
            self.assertEqual(unit_type, cmd.unit_type)
