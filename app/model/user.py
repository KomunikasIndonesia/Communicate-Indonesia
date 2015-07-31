from google.appengine.ext import ndb

ROLES = ['hutan_biru', 'farmer']


class User(ndb.Model):
    role = ndb.StringProperty(required=True, choices=set(ROLES))
    phone_number = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty()
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)