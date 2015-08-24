import unittest

from app.api.sms import app
from app.model.config import Config
from app.model.user import User
from app.model.district import District

from google.appengine.ext import testbed


class SmsAPITest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.user = User(role='farmer', phone_number='6072809193',
                         first_name='Kat', district_id='sum123')
        self.user.put()

        District(id='sum123', name='sumatra').put()
        Config(id='test', twilio_phone_number='+321').put()

    def tearDown(self):
        self.testbed.deactivate()

    def send(self, msg):
        res = self.app.post('/v1/sms/twilio', data={
            'MessageSid': 'sid',
            'From': self.user.phone_number,
            'To': '+321',
            'Body': msg
        })
        return res

    def test_multiple_plants(self):
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

        self.send('harvest 5 durian')
        self.send('harvest 5 kiwi')

        res = self.send('look sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKiwi 5'
                        '\nDurian 5' in res.data)

    def test_single_plant(self):
        self.send('plant 5 potato')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nKentang 5' in res.data)

        self.send('harvest 2 potato')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nKentang 3' in res.data)

        self.send('harvest 1 potato')
        self.send('sell 1 potato')

        res = self.send('look harvest sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKentang 3' in res.data)

        res = self.send('look sumatra')
        # TODO - the sell action should subtract from harvested total
        #      - Fix the bug in sell action for this assertion to work
        # self.assertTrue('Total panen di Sumatra:'
        #                '\nKentang 2' in res.data)

        res = self.send('look sumatra sell')
        self.assertTrue('Total jual di Sumatra:'
                        '\nKentang 1' in res.data)
