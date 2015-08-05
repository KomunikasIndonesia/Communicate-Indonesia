import time
from .util import id
from google.appengine.ext import ndb


class Price(ndb.Model):
    # relationship
    district_id = ndb.StringProperty(required=True)

    # price properties
    crop_name = ndb.StringProperty(required=True)
    price = ndb.IntegerProperty(required=True)
    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def toJson(self):
        return {
            'id': self.key.id(),
            'district_id': self.district_id,
            'crop_name': self.crop_name,
            'price': self.price,
            'ts_created': int(time.mktime(self.ts_created.timetuple()) * 1000),
            'ts_updated': int(time.mktime(self.ts_updated.timetuple()) * 1000),
        }

    @staticmethod
    def id():
        return 'P{}'.format(id.generate())
