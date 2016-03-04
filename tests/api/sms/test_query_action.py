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

        District(id='d2', name='Weight', slug='weight').put()
        Farm(action='plant', district_id='d2', crop_name='rice', quantity=10,
             unit_type='weight').put()
        Farm(action='sell', district_id='d2', crop_name='salt', quantity=10,
             unit_type='weight').put()
        Farm(action='sell', district_id='d2', crop_name='rice', quantity=1000,
             unit_type='weight').put()

        District(id='d3', name='Volume', slug='volume').put()
        Farm(action='plant', district_id='d3', crop_name='water', quantity=10,
             unit_type='volume').put()
        Farm(action='sell', district_id='d3', crop_name='water', quantity=1000,
             unit_type='volume').put()
        Farm(action='sell', district_id='d3', crop_name='oil', quantity=1,
             unit_type='volume').put()

        District(id='d4', name='All Unit Types', slug='all unit types').put()
        Farm(action='plant', district_id='d4', crop_name='water', quantity=10,
             unit_type='volume').put()
        Farm(action='plant', district_id='d4', crop_name='rice', quantity=10,
             unit_type='weight').put()
        Farm(action='plant', district_id='d4', crop_name='potato', quantity=10,
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
                         '\nKentang 10 biji', msg)

    def test_lookup_for_multiple_plants(self):
        msg = QueryAction(self._query("sumatra", 'sell')).execute()
        self.assertEqual('Total jual di Sumatra:'
                         '\nWortel 2 biji'
                         '\nKentang 1 biji', msg)

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
                         '\nWortel 2 biji'
                         '\nKentang 1 biji', msg)

    def test_lookup_for_a_single_weight_plant(self):
        msg = QueryAction(self._query('weight', 'plant')).execute()
        self.assertEqual('Total tanam di Weight:'
                         '\nPadi 10 g', msg)

    def test_lookup_for_multiple_weight_plants(self):
        msg = QueryAction(self._query('weight', 'sell')).execute()
        self.assertEqual('Total jual di Weight:'
                         '\nPadi 1 kg'
                         '\nSalt 10 g', msg)

    def test_lookup_for_single_volume_plant(self):
        msg = QueryAction(self._query('volume', 'plant')).execute()
        self.assertEqual('Total tanam di Volume:'
                         '\nWater 10 L', msg)

    def test_lookup_for_multiple_volume_plant(self):
        msg = QueryAction(self._query('volume', 'sell')).execute()
        self.assertEqual('Total jual di Volume:'
                         '\nOil 1 L'
                         '\nWater 1 kL', msg)

    def test_lookup_for_all_unit_types(self):
        msg = QueryAction(self._query('all unit types', 'plant')).execute()
        self.assertEqual('Total tanam di All Unit Types:'
                         '\nKentang 10 biji'
                         '\nPadi 10 g'
                         '\nWater 10 L', msg)
