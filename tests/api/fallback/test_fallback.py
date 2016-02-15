import unittest

from google.appengine.ext import ndb, testbed

from app.api.fallback import app
from app.model.config import Config
from app.model.user import User
from app.i18n import _


class FallbackTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

        ndb.get_context().clear_cache()

        Config(id='test', twilio_phone_number='+321').put()
        self.user = User(role='farmer', phone_number='+123', first_name='name')

    def tearDown(self):
        self.testbed.deactivate()

    def test_fallback_sms_response(self):
        res = self.app.post('/v1/fallback', data={
            'From': self.user.phone_number
        })

        error_msg = _('Sorry, we are having some temporary server issues')

        self.assertEqual(200, res.status_code)
        self.assertEqual('<?xml version="1.0" encoding="UTF-8"?>'
                         '<Response><Sms from="+321" to="+123">'
                         '{}</Sms></Response>'.format(error_msg), res.data)

    def test_fallback_mail(self):
        self.app.post('/v1/fallback', data={
            'From': self.user.phone_number
        })

        admins = [("Ragil Prasetya", "praser05@gmail.com"),
                  ("Giri Kuncoro", "girikuncoro@gmail.com")]

        for name, mail in admins:
            message = self.mail_stub.get_sent_messages(to=mail)
            self.assertEqual(1, len(message))
            self.assertEqual("{} <{}>".format(name, mail), message[0].to)
            self.assertEqual(
                "Communicate Indonesia Support <fallback@ci.com>", message[0].sender)
            self.assertEqual(
                "Fallback alert for Communicate Indonesia service", message[0].subject)
