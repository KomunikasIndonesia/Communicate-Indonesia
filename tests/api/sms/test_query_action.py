import unittest
from google.appengine.ext import testbed
from app.api.sms.query_action import QueryCommand, QueryAction
from app.model.district import District
from app.model.farm import Farm
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.i18n import _


class QueryActionTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()

        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        District(id='d1', name='Sumatra', slug='sumatra').put()
        Farm(action='plant', district_id='d1', crop_name='potato', quantity=10,
             unit_type='count').put()
        Farm(action='sell', district_id='d1', crop_name='potato', quantity=1,
             unit_type='count').put()
        Farm(action='sell', district_id='d1', crop_name='carrot', quantity=2,
             unit_type='count').put()

        self.user = User(id='u1', role=User.ROLE_FARMER, district_id='d1')

    def _query(self, district, action):
        sms = SmsRequest(id=SmsRequest.id())
        sms.body = ''
        sms.user = self.user

        cmd = QueryCommand(sms)
        cmd.filter = action
        cmd.district = district
        return cmd

    def test_lookup_for_a_single_plant(self):
        msg = QueryAction(self._query("sumatra", 'plant')).execute()
        self.assertEqual('Total tanam di Sumatra:'
                         '\nKentang 10', msg)

    def test_lookup_for_multiple_plants(self):
        msg = QueryAction(self._query("sumatra", 'sell')).execute()
        self.assertEqual('Total jual di Sumatra:'
                         '\nWortel 2'
                         '\nKentang 1', msg)

    def test_lookup_when_data_does_not_exist(self):
        res_msg = QueryAction(self._query('sumatra', 'harvest')).execute()
        self.assertEqual('Data panen tidak ada', res_msg)

    def test_district_does_not_exist(self):
        res_msg = QueryAction(self._query('London',
                                          'harvest')).execute()
        self.assertEqual(_('District {} is unknown').format('London'),
                         res_msg)

    def test_should_not_allow_user_without_permission(self):
        self.user.role = None

        msg = QueryAction(self._query('sumatra', 'harvest')).execute()
        self.assertEqual(_('Command not allowed'), msg)

    def test_should_ignore_district_name_case(self):
        msg = QueryAction(self._query('SuMatRa', 'sell')).execute()
        self.assertEqual('Total jual di Sumatra:'
                         '\nWortel 2'
                         '\nKentang 1', msg)
