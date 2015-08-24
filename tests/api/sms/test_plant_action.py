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

    def _plant(self, plant, amount):
        cmd = PlantCommand(self.sms)
        cmd.plant = plant
        cmd.amount = amount
        return cmd

    def test_should_respond_with_succeed(self):
        cmd = self._plant('potato', 20)
        res_msg = PlantAction(cmd).execute()

        self.assertEqual(_('Plant command succeeded'), res_msg)

    def test_should_store_one_item(self):
        cmd = self._plant('potato', 20)
        PlantAction(cmd).execute()

        all_data = Farm.query().fetch()
        self.assertEqual(1, len(all_data))

        data = all_data[0]
        self.assertEqual('plant', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(20, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_store_multiple_different_items(self):
        PlantAction(self._plant('carrot', 50)).execute()
        PlantAction(self._plant('potato', 20)).execute()

        all_data = Farm.query().fetch()
        self.assertEqual(2, len(all_data))

        data = all_data[0]
        self.assertEqual('plant', data.action)
        self.assertEqual('carrot', data.crop_name)
        self.assertEqual(50, data.quantity)
        self.assertEqual('sul123', data.district_id)

        data = all_data[1]
        self.assertEqual('plant', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(20, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_store_aggregate_amount_for_the_same_item(self):
        PlantAction(self._plant('potato', 50)).execute()
        PlantAction(self._plant('potato', 20)).execute()

        all_data = Farm.query().fetch()
        self.assertEqual(1, len(all_data))

        data = all_data[0]
        self.assertEqual('plant', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(70, data.quantity)
        self.assertEqual('sul123', data.district_id)
