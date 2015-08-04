from google.appengine.ext import ndb


class Config(ndb.Model):

    apikey = ndb.StringProperty()

    def toJson(self):
        return {
            'apikey': self.apikey
        }
