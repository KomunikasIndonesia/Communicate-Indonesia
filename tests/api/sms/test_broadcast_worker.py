import unittest
from app.api.sms.broadcast_worker import app
from app.model.config import Config
from google.appengine.ext import testbed


class BroadcastWorkerTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        Config(id='test', twilio_account_sid='ACCOUNT_SID',
               twilio_auth_token='AUTH_TOKEN', twilio_phone_number='+321').put()

    def _broadcast_sms(self, *args, **kwargs):
        return self.app.post('/v1/sms/broadcast', data=kwargs)

    def test_single_phone_number(self):
        pass

    def test_multiple_phone_numbers(self):
        pass
