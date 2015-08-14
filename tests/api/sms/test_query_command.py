import unittest
from datetime import datetime
from mock import patch

from app.api.sms.query_action import QueryCommand, QueryAction
from app.api.sms import app
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.model.district import District
from app.model.farm import Farm
from app.i18n import _

from google.appengine.ext import testbed, ndb


class QueryCommandTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.sms = SmsRequest()
        self.sms.from_number = '6072809193'

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.user = User(role='farmer', phone_number='6072809193',
                         first_name='Kat', district_id='sul123')
        self.user.put()

        ndb.put_multi([
            District(id='sul123', name='lompoko'),
            District(id='jawa321', name='surabaya')
        ])

        ndb.put_multi([
            Farm(district_id='sul123', action='harvest',
                 crop_name='potato', quantity=20),
            Farm(district_id='sul123', action='harvest',
                 crop_name='carrot', quantity=10),
            Farm(district_id='jawa321', action='harvest',
                 crop_name='banana', quantity=25),
            Farm(district_id='sul123', action='plant',
                 crop_name='rice', quantity=75),
            Farm(district_id='sul123', action='sell',
                 crop_name='milkfish', quantity=43),
        ])

        self.month = datetime.now().strftime('%B')

    def test_query_command(self):
        valid_messages = [
            {
                'filter': ['harvest', 'panen'],
                'msg': [
                    'look lompoko harvest',
                    'look harvest lompoko',
                    'look lompoko',  # default harvest
                    'lihat lompoko panen',
                    'lihat panen lompoko',
                    'lihat lompoko'  # default harvest
                ]
            },
            {
                'filter': ['plant', 'tanam'],
                'msg': [
                    'look lompoko plant',
                    'look plant lompoko',
                    'lihat lompoko tanam',
                    'lihat tanam lompoko'
                ]
            },
            {
                'filter': ['sell', 'jual'],
                'msg': [
                    'look lompoko sell',
                    'look sell lompoko',
                    'lihat lompoko jual',
                    'lihat jual lompoko'
                ]
            }
        ]

        for valid in valid_messages:
            for body in valid['msg']:
                self.sms.body = body
                cmd = QueryCommand(self.sms)
                self.assertTrue(cmd.valid())
                self.assertTrue(cmd.filter in valid['filter'])
                self.assertEqual('lompoko', cmd.district)

    def test_query_command_without_district(self):
        invalid_messages = [
            'look harvest',
            'look plant',
            'look sell',
            'lihat panen',
            'lihat tanam',
            'lihat jual'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = QueryCommand(self.sms)
            self.assertFalse(cmd.valid())

    def test_query_command_with_invalid_command(self):
        invalid_messages = [
            'sell 20 potato',
            'sell potato 20',
            'jual 20 potato',
            'jual potato 20'
        ]

        for body in invalid_messages:
            self.sms.body = body
            cmd = QueryCommand(self.sms)
            self.assertFalse(cmd.valid())

    @patch('app.api.sms.main.dispatcher')
    def test_district_harvest(self, mock):
        mock.dispatch.return_value = None

        self.assertEqual(5, len(Farm.query().fetch()))
        self.assertEqual(2, len(Farm.query(ndb.AND(
            Farm.action == 'harvest', Farm.district_id == 'sul123')).fetch()))

        valid_messages = [
            'look lompoko harvest',
            'look harvest lompoko',
            'look lompoko',
            'lihat lompoko panen',
            'lihat panen lompoko',
            'lihat lompoko'
        ]

        for body in valid_messages:
            self.sms.body = body
            cmd = QueryCommand(self.sms)
            res_msg = QueryAction(cmd).execute()

            self.assertEqual('Total panen di Lompoko ({} 2015):'
                             '\nWortel 10'
                             '\nKentang 20'.format(_(self.month)),
                             res_msg)

    @patch('app.api.sms.main.dispatcher')
    def test_district_plant(self, mock):
        mock.dispatch.return_value = None

        self.assertEqual(5, len(Farm.query().fetch()))
        self.assertEqual(1, len(Farm.query(ndb.AND(
            Farm.action == 'plant', Farm.district_id == 'sul123')).fetch()))

        valid_messages = [
            'look lompoko plant',
            'look tanam lompoko'
        ]

        for body in valid_messages:
            self.sms.body = body
            cmd = QueryCommand(self.sms)
            res_msg = QueryAction(cmd).execute()

            self.assertEqual('Total tanam di Lompoko ({} 2015):'
                             '\nPadi 75'.format(_(self.month)),
                             res_msg)

    @patch('app.api.sms.main.dispatcher')
    def test_district_sell(self, mock):
        mock.dispatch.return_value = None

        self.assertEqual(5, len(Farm.query().fetch()))
        self.assertEqual(1, len(Farm.query(ndb.AND(
            Farm.action == 'sell', Farm.district_id == 'sul123')).fetch()))

        valid_messages = [
            'look lompoko sell',
            'look jual lompoko'
        ]

        for body in valid_messages:
            self.sms.body = body
            cmd = QueryCommand(self.sms)
            res_msg = QueryAction(cmd).execute()

            self.assertEqual('Total jual di Lompoko ({} 2015):'
                             '\nBandeng 43'.format(_(self.month)),
                             res_msg)
