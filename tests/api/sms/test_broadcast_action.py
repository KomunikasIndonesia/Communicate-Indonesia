import unittest
import json

from google.appengine.ext import testbed
from app.api.sms.broadcast_action import BroadcastCommand, BroadcastAction
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.model.district import District
from app.i18n import _


class BroadcastActionTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.taskqueue_stub = self.testbed.get_stub(
            testbed.TASKQUEUE_SERVICE_NAME)

        User(role='farmer', phone_number='+111',
             first_name='Kat', district_id='d1').put()
        User(role='farmer', phone_number='+222',
             first_name='Ayu', district_id='d2').put()
        User(role='farmer', phone_number='+333',
             first_name='Budi', district_id='d1').put()

        District(id='d1', name='Lompoko', slug='lompoko').put()
        District(id='d2', name='Maros', slug='maros').put()

        self.user_hb = User(role=User.ROLE_HUTAN_BIRU, district_id='d0')
        self.user_leader = User(role=User.ROLE_DISTRICT_LEADER, district_id='d2')

    def _broadcast(self, user, send_to, msg):
        sms = SmsRequest()
        sms.body = ''
        sms.user = user

        cmd = BroadcastCommand(sms)
        cmd.send_to = send_to
        cmd.msg = msg
        return cmd

    def test_should_respond_with_success(self):
        msg = BroadcastAction(
            self._broadcast(self.user_hb, 'everyone', 'hello')).execute()
        self.assertEqual(_('Message sent to {}').format(_('everyone')), msg)

    def test_should_add_to_taskqueue(self):
        BroadcastAction(
            self._broadcast(self.user_hb, 'everyone', 'hello')).execute()
        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(1, len(tasks))

    def test_hb_send_all(self):
        BroadcastAction(
            self._broadcast(self.user_hb, 'everyone', 'hello')).execute()
        tasks = self.taskqueue_stub.get_filtered_tasks()

        data = json.loads(tasks[0].payload)
        self.assertEqual(['+111', '+222', '+333'], data['phone_number'])
        self.assertEqual('hello', data['message'])

    def test_hb_send_other_district(self):
        BroadcastAction(
            self._broadcast(self.user_hb, 'Lompoko', 'hello')).execute()
        tasks = self.taskqueue_stub.get_filtered_tasks()

        data = json.loads(tasks[0].payload)
        self.assertEqual(['+111', '+333'], data['phone_number'])
        self.assertEqual('hello', data['message'])

    def test_hb_district_does_not_exist(self):
        msg = BroadcastAction(
            self._broadcast(self.user_hb, 'Sumatra', 'hello')).execute()
        self.assertEqual(_('District {} is unknown').format('Sumatra'), msg)

    def test_farmer_leader_send_own_district(self):
        BroadcastAction(
            self._broadcast(self.user_leader, 'Maros', 'hello')).execute()
        tasks = self.taskqueue_stub.get_filtered_tasks()

        data = json.loads(tasks[0].payload)
        self.assertEqual(['+222'], data['phone_number'])
        self.assertEqual('hello', data['message'])

    def test_farmer_leader_should_send_to_same_district_only(self):
        BroadcastAction(
            self._broadcast(self.user_leader, 'everyone', 'hello')).execute()
        BroadcastAction(
            self._broadcast(self.user_leader, 'lompoko', 'hello')).execute()

        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(2, len(tasks))

        data = json.loads(tasks[0].payload)
        self.assertEqual(['+222'], data['phone_number'])
        self.assertEqual('everyone hello', data['message'])

        data = json.loads(tasks[1].payload)
        self.assertEqual(['+222'], data['phone_number'])
        self.assertEqual('lompoko hello', data['message'])
