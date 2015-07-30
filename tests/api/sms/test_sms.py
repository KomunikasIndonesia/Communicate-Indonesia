import unittest

from app.api.sms import app


class SmsTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_server_is_up(self):
        res = self.app.get('/v1/sms/twilio')
        self.assertEqual('<?xml version="1.0" encoding="UTF-8"?><Response />',
                         res.data)


if __name__ == '__main__':
    unittest.main()
