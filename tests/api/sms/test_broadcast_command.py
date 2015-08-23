import unittest
import json
from mock import patch

from app.api.sms.broadcast_action import BroadcastCommand, BroadcastAction
from app.api.sms.broadcast import app
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.model.district import District

from app.i18n import _
from google.appengine.ext import testbed, ndb


class BroadcastCommandTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.sms = SmsRequest()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.taskqueue_stub = self.testbed.get_stub(
            testbed.TASKQUEUE_SERVICE_NAME)

        ndb.put_multi([
            User(role='farmer', phone_number='+16072809193',
                 first_name='Kat', district_id='sul123'),
            User(role='farmer', phone_number='+15005550006',
                 first_name='Ayu', district_id='sul456'),
            User(role='hutan_biru', phone_number='+123456',
                 first_name='Ratna', district_id='sul000')
        ])

        ndb.put_multi([
            District(id='sul000', name='makasar'),
            District(id='sul123', name='lompoko'),
            District(id='sul456', name='maros')
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
            self.assertEqual('hello farmers', cmd.msg)

    def test_broadcast_command_hb_one_word(self):
        valid_messages = [
            'broadcast lompoko hello',
            'broadcast everyone hello',
            'kirim lompoko hello',
            'kirim semua hello',
        ]

        self.sms.user = User(role='hutan_biru')

        for body in valid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertTrue(cmd.valid())
            self.assertEqual('hello', cmd.msg)

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
            'broadcast hello people',
            'broadcast lompoko hello people',
            'kirim hello people',
            'kirim lompoko hello people',
        ]

        self.sms.user = User(role='farmer', district_id='sul123')  # lompoko

        for body in valid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertTrue(cmd.valid())
            self.assertEqual('hello people', cmd.msg)

    def test_broadcast_command_farmer_one_word(self):
        valid_messages = [
            'broadcast hello',
            'broadcast lompoko hello',
            'kirim hello',
            'kirim lompoko hello'
        ]

        self.sms.user = User(role='farmer', district_id='sul123')  # lompoko

        for body in valid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertTrue(cmd.valid())
            self.assertEqual('hello', cmd.msg)

    def test_broadcast_command_farmer_long(self):
        valid_messages = [
            'broadcast hello friends in sulawesi!',
            'broadcast lompoko hello friends in sulawesi!',
            'kirim hello friends in sulawesi!',
            'kirim lompoko hello friends in sulawesi!'
        ]

        self.sms.user = User(role='farmer', district_id='sul123')  # lompoko

        for body in valid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertTrue(cmd.valid())
            self.assertEqual('hello friends in sulawesi!', cmd.msg)

    def test_broadcast_command_farmer_empty(self):
        invalid_messages = [
            'broadcast',
            'kirim'
        ]

        self.sms.user = User(role='farmer', district_id='sul123')

        for body in invalid_messages:
            self.sms.body = body
            cmd = BroadcastCommand(self.sms)
            self.assertFalse(cmd.valid())

    @patch('app.api.sms.main.dispatcher')
    def test_hb_broadcast_all(self, mock):
        mock.dispatch.return_value = None

        self.sms.body = 'broadcast everyone hello people'
        self.sms.user = User(role='hutan_biru')

        cmd = BroadcastCommand(self.sms)
        res_msg = BroadcastAction(cmd).execute()

        self.assertEqual('Pesan berhasil dikirim ke semua', _(res_msg))

        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 2)  # 2 farmers in db

        for task in tasks:
            self.assertEqual('/v1/sms/broadcast', task.url)

            data = json.loads(task.payload)
            res = self.app.post(task.url, data=data)  # execute task
            r = json.loads(res.data)

            self.assertEqual(200, res.status_code)
            self.assertEqual(r['body'], 'hello people')
            self.assertEqual(r['to'], data['phone_number'])

            # check if farmers only
            query = User.query(User.phone_number == data['phone_number'])
            user = query.fetch()[0]
            self.assertEqual(user.role, 'farmer')

    @patch('app.api.sms.main.dispatcher')
    def test_hb_broadcast_to_one_district(self, mock):
        mock.dispatch.return_value = None

        self.sms.body = 'broadcast lompoko hello people in lompoko'
        self.sms.user = User(role='hutan_biru')

        cmd = BroadcastCommand(self.sms)
        res_msg = BroadcastAction(cmd).execute()

        self.assertEqual('Pesan berhasil dikirim ke lompoko', _(res_msg))

        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 1)  # 1 lompoko farmer in db

        for task in tasks:
            data = json.loads(task.payload)
            res = self.app.post(task.url, data=data)  # execute task
            r = json.loads(res.data)

            self.assertEqual(r['body'], 'hello people in lompoko')

            # check if farmer in lompoko only
            query = User.query(User.phone_number == data['phone_number'])
            user = query.fetch()[0]
            self.assertEqual(user.role, 'farmer')
            self.assertEqual(user.district_id, 'sul123')

    @patch('app.api.sms.main.dispatcher')
    def test_farmer_broadcast(self, mock):
        mock.dispatch.return_value = None

        self.sms.body = 'broadcast hello farmers in lompoko'
        self.sms.user = User(role='farmer', district_id='sul123')

        cmd = BroadcastCommand(self.sms)
        res_msg = BroadcastAction(cmd).execute()

        self.assertEqual('Pesan berhasil dikirim ke lompoko', _(res_msg))

        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 1)  # 1 lompoko farmer in db

        for task in tasks:
            data = json.loads(task.payload)
            res = self.app.post(task.url, data=data)  # execute task
            r = json.loads(res.data)

            self.assertEqual(r['body'], 'hello farmers in lompoko')

            # check if farmer in lompoko only
            query = User.query(User.phone_number == data['phone_number'])
            user = query.fetch()[0]
            self.assertEqual(user.role, 'farmer')
            self.assertEqual(user.district_id, 'sul123')

    @patch('app.api.sms.main.dispatcher')
    def test_farmer_broadcast_with_district(self, mock):
        mock.dispatch.return_value = None

        self.sms.body = 'broadcast lompoko hello farmers in lompoko'
        self.sms.user = User(role='farmer', district_id='sul123')  # lompoko

        cmd = BroadcastCommand(self.sms)
        res_msg = BroadcastAction(cmd).execute()

        self.assertEqual('Pesan berhasil dikirim ke lompoko', _(res_msg))

        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 1)  # 1 lompoko farmer in db

        for task in tasks:
            data = json.loads(task.payload)
            res = self.app.post(task.url, data=data)  # execute task
            r = json.loads(res.data)

            self.assertEqual(r['body'], 'hello farmers in lompoko')

            # check if farmer in lompoko only
            query = User.query(User.phone_number == data['phone_number'])
            user = query.fetch()[0]
            self.assertEqual(user.role, 'farmer')
            self.assertEqual(user.district_id, 'sul123')

    @patch('app.api.sms.main.dispatcher')
    def test_farmer_broadcast_to_unauthorized_district(self, mock):
        mock.dispatch.return_value = None

        self.sms.body = 'broadcast maros did better than us, revenge!'
        self.sms.user = User(role='farmer', district_id='sul123')  # lompoko

        cmd = BroadcastCommand(self.sms)
        res_msg = BroadcastAction(cmd).execute()

        # ignore district, still send to user's registered district
        self.assertEqual('Pesan berhasil dikirim ke lompoko', _(res_msg))

        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 1)  # 1 lompoko farmer in db

        for task in tasks:
            data = json.loads(task.payload)
            res = self.app.post(task.url, data=data)  # execute task
            r = json.loads(res.data)

            # district is considered as message
            self.assertEqual(r['body'], 'maros did better than us, revenge!')

            # check if farmer in lompoko only
            query = User.query(User.phone_number == data['phone_number'])
            user = query.fetch()[0]
            self.assertEqual(user.role, 'farmer')
            self.assertEqual(user.district_id, 'sul123')
