from .util import id
from google.appengine.ext import ndb


class SmsRequest(ndb.Model):

    # sms properties
    twilio_message_id = ndb.StringProperty(required=True)

    from_number = ndb.StringProperty(required=True)
    from_city = ndb.StringProperty()
    from_state = ndb.StringProperty()
    from_zip = ndb.StringProperty()
    from_country = ndb.StringProperty()

    to_number = ndb.StringProperty(required=True)
    to_city = ndb.StringProperty()
    to_state = ndb.StringProperty()
    to_zip = ndb.StringProperty()
    to_country = ndb.StringProperty()

    body = ndb.StringProperty(required=True)

    # sms state
    processed = ndb.BooleanProperty(required=True, default=False)
    ts_processed = ndb.DateTimeProperty()

    ts_created = ndb.DateTimeProperty(auto_now_add=True)
    ts_updated = ndb.DateTimeProperty(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(SmsRequest, self).__init__(*args, **kwargs)

        # the user associated to the from number
        self.user = None

    @property
    def valid(self):
        return self.twilio_message_id and \
            self.from_number and \
            self.to_number and \
            self.body

    @property
    def from_(self):
        return self.from_number

    @property
    def to(self):
        return self.to_number

    @staticmethod
    def id():
        return 'SMS{}'.format(id.generate())
