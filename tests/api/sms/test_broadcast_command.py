import unittest

from app.api.sms.broadcast_action import BroadcastCommand
from app.api.sms import app
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.model.district import District

from google.appengine.ext import testbed, ndb


class BroadcastCommandTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.sms = SmsRequest()
        self.sms.from_number = '6072809193'

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        ndb.put_multi([
            User(role='farmer', phone_number='6072809193',
                 first_name='Kat', district_id='sul123'),
            User(role='hutan_biru', phone_number='123456',
                 first_name='Ratna', district_id='sul000')
        ])

        ndb.put_multi([
            District(id='sul000', name='makasar'),
            District(id='sul123', name='lompoko'),
            District(id='sul456', name='maros'),
            District(id='sul789', name='barru'),
        ])

    def tearDown(self):
        self.testbed.deactivate()

    def test_broadcast_command_hb(self):
        valid_messages = [
            'broadcast lompoko hello farmers',
            'broadcast everyone hello farmers',
            'kirim lompoko hello farmers',
            'kirim semua hello farmers',
        ]

        self.sms.user = User(role='hutan_biru')

        for body in valid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertTrue(cmd.valid())

    def test_broadcast_command_hb_without_message(self):
        invalid_messages = [
            'broadcast lompoko',
            'broadcast everyone',
            'kirim lompoko',
            'kirim semua',
        ]

        self.sms.user = User(role='hutan_biru')

        for body in invalid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_broadcast_command_hb_empty(self):
        invalid_messages = [
            'broadcast',
            'kirim'
        ]

        self.sms.user = User(role='hutan_biru')

        for body in invalid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_broadcast_command_farmer(self):
        valid_messages = [
            'broadcast hello',
            'broadcast lompoko hello people',
            'kirim hello',
            'kirim lompoko hello people',
        ]

        self.sms.user = User(role='farmer', district_id='sul123')  # lompoko

        for body in valid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertTrue(cmd.valid())

    def test_broadcast_command_farmer_empty(self):
        invalid_messages = [
            'broadcast',
            'kirim'
        ]

        self.sms.user = User(role='farmer')

        for body in invalid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertFalse(cmd.valid())
