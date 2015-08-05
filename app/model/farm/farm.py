import time
from model.util import id
from google.appengine.ext import ndb


class Farm(ndb.Model):
    ACTION = ['harvest', 'plant', 'sell']

    # relationships
    crop_id = ndb.StringProperty(required=True)
    district_id = ndb.StringProperty(required=True)

    # farm properties
    action = ndb.StringProperty(required=True, choices=set(ACTION))
    quantity = ndb.IntegerProperty(required=True)
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def toJson(self):
        return {
            'id': self.key.id(),
            'crop_id': self.crop_id,
            'district_id': self.district_id,
            'action': self.action,
            'quantity': self.quantity,
            'ts_created': int(time.mktime(self.ts_created.timetuple()) * 1000),
            'ts_updated': int(time.mktime(self.ts_updated.timetuple()) * 1000),
        }

    @staticmethod
    def id():
        return 'F{}'.format(id.generate())
