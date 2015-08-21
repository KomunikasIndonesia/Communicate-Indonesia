import unittest

from app.api.sms import app
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
                         first_name='Kat', district_id='sum123')
        self.user.put()

        district = District(id='sum123', name='sumatra')
        district.put()

    def tearDown(self):
        self.testbed.deactivate()

    def send(self, msg):
        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.sms.from_number,
            'To': '+321',
            'Body': msg
        })
        return res

    def execute(self, cmd, action):
        return action(cmd).execute()

    def test_single_plant(self):
        res = self.send('plant 5 potato')
        self.assertTrue(_('Plant command succeeded') in res.data)

        res = self.send('look sumatra plant')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nKentang 5' in res.data)

    def test_single_harvest(self):
        res = self.send('harvest potato 2')
        self.assertTrue(_('Harvest command succeeded') in res.data)

        res = self.send('look sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKentang 2' in res.data)

    def test_single_sell(self):
        res = self.send('sell potato 7')
        self.assertTrue(_('Sell command succeeded') in res.data)

        res = self.send('look sell sumatra')
        self.assertTrue('Total jual di Sumatra:'
                        '\nKentang 7' in res.data)

    def test_single_plant_harvest_empty_sell(self):
        self.send('plant potato 5')
        self.send('harvest potato 1')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nKentang 4' in res.data)

        res = self.send('look sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKentang 1' in res.data)

        res = self.send('look sell sumatra')
        self.assertTrue('Data jual tidak ada' in res.data)

    def test_multi_plant_empty_harvest(self):
        self.send('plant 5 potato')
        self.send('plant 5 mango')
        self.send('plant 5 banana')
        self.send('plant 5 tomato')
        self.send('plant 5 carrot')
        self.send('plant 5 kiwi')
        self.send('plant 5 durian')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nDurian 5'
                        '\nKiwi 5'
                        '\nWortel 5'
                        '\nTomat 5'
                        '\nPisang 5'
                        '\nMangga 5'
                        '\nKentang 5' in res.data)

        res = self.send('look harvest sumatra')
        self.assertTrue('Data panen tidak ada' in res.data)

    def test_multi_harvest_empty_sell_plant(self):
        self.send('harvest 5 durian')
        self.send('harvest 5 kiwi')

        res = self.send('look sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKiwi 5'
                        '\nDurian 5' in res.data)

        res = self.send('look sell sumatra')
        self.assertTrue('Data jual tidak ada' in res.data)

        res = self.send('look plant sumatra')
        self.assertTrue('Data tanam tidak ada' in res.data)

    def test_multi_different_harvest(self):
        self.send('plant 5 potato')
        self.send('harvest 3 carrot')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nKentang 5' in res.data)

        res = self.send('look sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nWortel 3' in res.data)
