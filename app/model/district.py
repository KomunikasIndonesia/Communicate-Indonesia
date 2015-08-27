import time
from .util import id
from google.appengine.ext import ndb


class District(ndb.Model):

    name = ndb.StringProperty(required=True)

    # slug is a unique index based on the district name
    slug = ndb.StringProperty(required=True)

    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def to_dict(self):
        return {
            'id': self.key.id(),
            'name': self.name,
            'slug': self.slug,
            'ts_created': int(time.mktime(self.ts_created.timetuple()) * 1000),
            'ts_updated': int(time.mktime(self.ts_updated.timetuple()) * 1000),
        }

    @staticmethod
    def id():
        return 'D{}'.format(id.generate())
