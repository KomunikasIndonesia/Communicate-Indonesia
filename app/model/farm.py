import time
from .util import id
from google.appengine.ext import ndb


class Farm(ndb.Model):
    ACTION = ['harvest', 'plant', 'sell']

    # relationship
    district_id = ndb.StringProperty(required=True)

    # farm properties
    action = ndb.StringProperty(required=True, choices=set(ACTION))
    crop_name = ndb.StringProperty(required=True)
    quantity = ndb.IntegerProperty(required=True)
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def toJson(self):
        return {
            'id': self.key.id(),
            'district_id': self.district_id,
            'action': self.action,
            'crop_name': self.crop_name,
            'quantity': self.quantity,
            'ts_created': int(time.mktime(self.ts_created.timetuple()) * 1000),
            'ts_updated': int(time.mktime(self.ts_updated.timetuple()) * 1000),
        }

    @staticmethod
    def id():
        return 'F{}'.format(id.generate())
