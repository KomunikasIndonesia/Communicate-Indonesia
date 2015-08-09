from google.appengine.ext import ndb


class Config(ndb.Model):

    admin_username = ndb.StringProperty()
    admin_apikey = ndb.StringProperty()

    def toJson(self):
        return {
            'admin_username': self.admin_username,
            'admin_apikey': self.admin_apikey
        }
