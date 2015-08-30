import time
from app.model.permission import (
    RECORD_HARVEST, RECORD_PLANT, RECORD_SELL,
    RETRIEVE_ALL_DISTRICT,
    BROADCAST_OWN_DISTRICT, BROADCAST_ALL
)
from .util import id
from google.appengine.ext import ndb


class User(ndb.Model):
    ROLE_DISTRICT_LEADER = 'district_leader'
    ROLE_FARMER = 'farmer'
    ROLE_HUTAN_BIRU = 'hutan_biru'
    ROLES = [ROLE_DISTRICT_LEADER, ROLE_HUTAN_BIRU, ROLE_FARMER]

    # relationships
    district_id = ndb.StringProperty()

    # user properties
    role = ndb.StringProperty(required=True, choices=set(ROLES))
    phone_number = ndb.StringProperty(required=True)
    first_name = ndb.StringProperty(required=True)
    last_name = ndb.StringProperty()
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return {
            'id': self.key.id(),
            'role': self.role,
            'permissions': self.permissions,
            'district_id': self.district_id,
            'phone_number': self.phone_number,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'ts_created': int(time.mktime(self.ts_created.timetuple()) * 1000),
            'ts_updated': int(time.mktime(self.ts_updated.timetuple()) * 1000),
        }

    @staticmethod
    def id():
        return 'U{}'.format(id.generate())

    @property
    def permissions(self):
        if self.role == self.ROLE_FARMER:
            return [RECORD_PLANT, RECORD_HARVEST, RECORD_SELL,
                    RETRIEVE_ALL_DISTRICT]

        if self.role == self.ROLE_DISTRICT_LEADER:
            return [RECORD_PLANT, RECORD_HARVEST, RECORD_SELL,
                    RETRIEVE_ALL_DISTRICT,
                    BROADCAST_OWN_DISTRICT]

        if self.role == self.ROLE_HUTAN_BIRU:
            return [RETRIEVE_ALL_DISTRICT,
                    BROADCAST_ALL]

        # Empty permission without role.
        # All users should have a role or in the future
        # a permission override
        return []
