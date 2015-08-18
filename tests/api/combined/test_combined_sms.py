import unittest
from mock import patch

from app.api.sms import app
from app.api.sms.plant_action import PlantCommand, PlantAction
from app.api.sms.harvest_action import HarvestCommand, HarvestAction
from app.api.sms.sell_action import SellCommand, SellAction
from app.api.sms.query_action import QueryCommand, QueryAction
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.model.district import District

from app.i18n import _
from google.appengine.ext import testbed


class CombinedSmsTest(unittest.TestCase):

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

        district = District(id='sul123', name='lompoko')
        district.put()

    def tearDown(self):
        self.testbed.deactivate()

    def send(self, msg):
        self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.sms.from_number,
            'To': '+321',
            'Body': msg
        })

    def execute(self, cmd, action):
        return action(cmd).execute()

    @patch('app.api.sms.main.dispatcher')
    def test_single_plant(self, mock):
        mock.dispatch.return_value = None

        self.send('plant 5 potato')
        sms = SmsRequest.query().fetch()[0]
        res_msg = self.execute(PlantCommand(sms), PlantAction)

        self.assertEqual(_('Plant command succeeded'), res_msg)

        self.send('look lompoko plant')
        sms = SmsRequest.query().fetch()[1]
        res_msg = self.execute(QueryCommand(sms), QueryAction)

        self.assertEqual('Total tanam di Lompoko:'
                         '\nKentang 5', res_msg)

    @patch('app.api.sms.main.dispatcher')
    def test_single_harvest(self, mock):
        mock.dispatch.return_value = None

        self.send('harvest potato 2')
        sms = SmsRequest.query().fetch()[0]
        res_msg = self.execute(HarvestCommand(sms), HarvestAction)

        self.assertEqual(_('Harvest command succeeded'), res_msg)

        self.send('look lompoko')
        sms = SmsRequest.query().fetch()[1]
        res_msg = self.execute(QueryCommand(sms), QueryAction)

        self.assertEqual('Total panen di Lompoko:'
                         '\nKentang 2', res_msg)

    @patch('app.api.sms.main.dispatcher')
    def test_single_sell(self, mock):
        mock.dispatch.return_value = None

        self.send('sell potato 7')
        sms = SmsRequest.query().fetch()[0]
        res_msg = self.execute(SellCommand(sms), SellAction)

        self.assertEqual(_('Sell command succeeded'), res_msg)

        self.send('look sell lompoko')
        sms = SmsRequest.query().fetch()[1]
        res_msg = self.execute(QueryCommand(sms), QueryAction)

        self.assertEqual('Total jual di Lompoko:'
                         '\nKentang 7', res_msg)

    @patch('app.api.sms.main.dispatcher')
    def test_single_plant_harvest(self, mock):
        mock.dispatch.return_value = None

        self.send('plant potato 5')
        sms = SmsRequest.query().fetch()[0]
        self.execute(PlantCommand(sms), PlantAction)

        self.send('harvest potato 1')
        sms = SmsRequest.query().fetch()[1]
        self.execute(HarvestCommand(sms), HarvestAction)

        self.send('harvest potato 3')
        sms = SmsRequest.query().fetch()[2]
        self.execute(HarvestCommand(sms), HarvestAction)

        self.send('look plant lompoko')
        sms = SmsRequest.query().fetch()[3]
        res_msg = self.execute(QueryCommand(sms), QueryAction)

        self.assertEqual('Total tanam di Lompoko:'
                         '\nKentang 5', res_msg)

        self.send('look lompoko')
        sms = SmsRequest.query().fetch()[4]
        res_msg = self.execute(QueryCommand(sms), QueryAction)

        self.assertEqual('Total panen di Lompoko:'
                         '\nKentang 3'
                         '\nKentang 1', res_msg)

        self.send('look sell lompoko')
        sms = SmsRequest.query().fetch()[5]
        res_msg = self.execute(QueryCommand(sms), QueryAction)

        self.assertEqual('Data jual tidak ada', res_msg)
