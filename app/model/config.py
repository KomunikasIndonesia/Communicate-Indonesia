from google.appengine.ext import ndb


class Config(ndb.Model):

    admin_username = ndb.StringProperty()
    admin_apikey = ndb.StringProperty()


def delete_config():
    ndb.delete_multi(Config.query().fetch(keys_only=True))
