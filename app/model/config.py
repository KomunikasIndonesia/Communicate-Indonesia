from google.appengine.ext import ndb


class Config(ndb.Model):

    admin_username = ndb.StringProperty()
    admin_apikey = ndb.StringProperty()

    twilio_account_sid = ndb.StringProperty()
    twilio_auth_token = ndb.StringProperty()
    twilio_phone_number = ndb.StringProperty()

    def toJson(self):
        return {
            'admin_username': self.admin_username,
            'admin_apikey': self.admin_apikey,
            'twilio_account_sid': self.twilio_account_sid,
            'twilio_auth_token': self.twilio_auth_token,
            'twilio_phone_number': self.twilio_phone_number
        }
