import unittest

from app.api.sms import app
from app.i18n import _
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
        self.testbed.init_taskqueue_stub(root_path='.')

        self.user = User(role='district_leader',
                         phone_number='6072809193',
                         first_name='Kat', district_id='sum123')
        self.user.put()

        District(id='sum123', name='Sumatra', slug='sumatra').put()
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

    def test_broadcast(self):
        # add farmers
        User(role='farmer',
             phone_number='123',
             first_name='farmer1',
             district_id='sum123').put()

        res = self.send('broadcast hello world')

        self.assertIn(_('Message delivered'), res.data)

    @unittest.skip("all commands are being refactored, this case is failing")
    def test_multiple_plants(self):
        self.send('plant potato 5')
        self.send('plant mango 5')
        self.send('plant banana 5')
        self.send('plant tomato 5')
        self.send('plant carrot 5')
        self.send('plant kiwi 5')
        self.send('plant durian 5')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nDurian 5 biji'
                        '\nKiwi 5 biji'
                        '\nWortel 5 biji'
                        '\nTomat 5 biji'
                        '\nPisang 5 biji'
                        '\nMangga 5 biji'
                        '\nKentang 5 biji' in res.data)

        self.send('harvest 5 durian')
        self.send('harvest 5 kiwi')

        res = self.send('look sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKiwi 5 biji'
                        '\nDurian 5 biji' in res.data)

    @unittest.skip("all commands are being refactored, this case is failing")
    def test_single_plant(self):
        self.send('plant potato 5')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nKentang 5 biji' in res.data)

        self.send('harvest 2 potato')

        res = self.send('look plant sumatra')
        self.assertTrue('Total tanam di Sumatra:'
                        '\nKentang 3 biji' in res.data)

        self.send('harvest 1 potato')

        res = self.send('look harvest sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKentang 3 biji' in res.data)

        self.send('sell 1 potato')

        res = self.send('look sumatra')
        self.assertTrue('Total panen di Sumatra:'
                        '\nKentang 2 biji' in res.data)

        res = self.send('look sumatra sell')
        self.assertTrue('Total jual di Sumatra:'
                        '\nKentang 1 biji' in res.data)
