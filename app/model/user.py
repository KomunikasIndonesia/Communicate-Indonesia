import time
from .util import id
from google.appengine.ext import ndb


class User(ndb.Model):
    ROLE_FARMER = 'farmer'
    ROLE_HUTAN_BIRU = 'hutan_biru'
    ROLES = [ROLE_HUTAN_BIRU, ROLE_FARMER]

    # relationships
    district_id = ndb.StringProperty()

    # user properties
    role = ndb.StringProperty(required=True, choices=set(ROLES))
    phone_number = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty()
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def toJson(self):
        return {
            'id': self.key.id(),
            'role': self.role,
            'district': self.district_id,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'ts_created': int(time.mktime(self.ts_created.timetuple()) * 1000),
            'ts_updated': int(time.mktime(self.ts_updated.timetuple()) * 1000),
        }

    @staticmethod
    def id():
        return 'U{}'.format(id.generate())
