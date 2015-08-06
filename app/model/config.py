from google.appengine.ext import ndb


class Config(ndb.Model):

    admin_username = ndb.StringProperty()
    admin_apikey = ndb.StringProperty()
