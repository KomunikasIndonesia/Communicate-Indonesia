import unittest
from app.api.sms.plant_action import PlantCommand, PlantAction
from google.appengine.ext import testbed
from app.model.farm import Farm
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.i18n import _


class PlantActionTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.sms = SmsRequest()
        self.sms.user = User(role='farmer',
                             phone_number='6072809193',
                             first_name='Kat',
                             district_id='sul123')
        self.sms.body = ''

        Farm(action='plant', district_id='sul123', crop_name='potato', quantity=10000,
             unit_type='weight').put()
        Farm(action='plant', district_id='sul123', crop_name='rice', quantity=50,
             unit_type='volume').put()
        Farm(action='plant', district_id='sul123', crop_name='banana', quantity=2,
             unit_type='count').put()

    def _plant(self, plant, amount, unit=None):
        cmd = PlantCommand(self.sms)
        cmd.plant = plant
        cmd.amount = amount
        cmd.unit = unit
        return cmd

    def test_should_respond_with_succeed(self):
        cmd = self._plant('potato', 20, 'g')
        res_msg = PlantAction(cmd).execute()

        self.assertEqual(_('Plant command succeeded'), res_msg)

    def test_should_respond_with_invalid_unit(self):
        cmd = self._plant('potato', 20, 'xyz')
        res_msg = PlantAction(cmd).execute()

        self.assertEqual(_('Invalid unit for plant command'), res_msg)

    def test_should_respond_with_unregistered_plant(self):
        cmd = self._plant('strawberry', 20, 'g')
        res_msg = PlantAction(cmd).execute()

        self.assertEqual(_('Plant not registered'), res_msg)

    def test_should_store_one_item(self):
        cmd = self._plant('potato', 2000, 'g')
        PlantAction(cmd).execute()

        data = Farm.query(Farm.crop_name == 'potato').fetch()[0]

        self.assertEqual('plant', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(12000, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_store_multiple_different_items(self):
        PlantAction(self._plant('rice', 30, 'L')).execute()
        PlantAction(self._plant('potato', 2000, 'g')).execute()

        all_data = Farm.query().fetch()

        data = all_data[1]
        self.assertEqual('plant', data.action)
        self.assertEqual('rice', data.crop_name)
        self.assertEqual(80, data.quantity)
        self.assertEqual('sul123', data.district_id)

        data = all_data[0]
        self.assertEqual('plant', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(12000, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_store_aggregate_amount_for_the_same_item(self):
        PlantAction(self._plant('potato', 50000, 'g')).execute()
        PlantAction(self._plant('potato', 20000, 'g')).execute()

        data = Farm.query(Farm.crop_name == 'potato').fetch()[0]

        self.assertEqual('plant', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(80000, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_not_allow_user_without_permission(self):
        self.sms.user.role = None

        msg = PlantAction(self._plant('potato', 1)).execute()
        self.assertEqual(_('Command not allowed'), msg)

    def test_should_convert_to_default_unit(self):
        PlantAction(self._plant('potato', 30, 'kg')).execute()
        PlantAction(self._plant('rice', 2, 'kL')).execute()

        all_data = Farm.query().fetch()

        data = all_data[0]
        self.assertEqual('plant', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(40000, data.quantity)  # in gram
        self.assertEqual('sul123', data.district_id)

        data = all_data[1]
        self.assertEqual('plant', data.action)
        self.assertEqual('rice', data.crop_name)
        self.assertEqual(2050, data.quantity)  # in litre
        self.assertEqual('sul123', data.district_id)
