import unittest
from app.api.sms.sell_action import SellCommand
from app.command.base import Action


class SmsCommandTest(unittest.TestCase):

    def setUp(self):
        self.cmd = SellCommand(Action())

    def test_sell_command(self):
        self.assertTrue(self.cmd.match('jual'))
        self.assertTrue(self.cmd.match('sell'))

        self.assertFalse(self.cmd.match('tanam'))
        self.assertFalse(self.cmd.match('harvest'))
