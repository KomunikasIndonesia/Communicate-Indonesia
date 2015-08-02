import unittest
from app.command.base import Dispatcher, Command, Action


class ValidCommand(Command):
    def valid(self):
        return True


class InvalidCommand(Command):
    def valid(self):
        return False


class EchoAction(Action):
    def execute(self):
        return self.command.raw_data


class DispatcherTest(unittest.TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher()

    def test_dispatch_with_valid_command(self):
        self.dispatcher.route(ValidCommand, EchoAction)

        response = self.dispatcher.dispatch('data')
        self.assertEqual('data', response)

        response = self.dispatcher.dispatch('other data')
        self.assertEqual('other data', response)

    def test_dispatch_without_valid_command(self):
        self.dispatcher.route(InvalidCommand, EchoAction)
        self.assertRaises(ValueError, self.dispatcher.dispatch, 'no action')

    def test_dispatch_multiple_valid_commands(self):
        self.dispatcher.route(ValidCommand, EchoAction)
        self.dispatcher.route(ValidCommand, EchoAction)

        self.assertRaises(ValueError, self.dispatcher.dispatch, 'no action')
