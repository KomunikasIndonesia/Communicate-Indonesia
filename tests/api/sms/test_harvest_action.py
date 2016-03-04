import unittest
from google.appengine.ext import testbed
from app.api.sms.harvest_action import HarvestCommand, HarvestAction
from app.model.farm import Farm
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.i18n import _


class HarvestActionTest(unittest.TestCase):

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

        Farm(action='plant', district_id='sul123', crop_name='potato', quantity=10,
             unit_type='count').put()
        Farm(action='plant', district_id='sul123', crop_name='carrot', quantity=5,
             unit_type='count').put()

    def _harvest(self, plant, amount):
        cmd = HarvestCommand(self.sms)
        cmd.plant = plant
        cmd.amount = amount
        return cmd

    def test_should_respond_with_success(self):
        msg = HarvestAction(self._harvest('potato', 5)).execute()
        self.assertEqual(_('Harvest command succeeded'), msg)

    def test_should_store_harvest_for_one_plant(self):
        HarvestAction(self._harvest('potato', 5)).execute()

        all_data = Farm.query(Farm.action == 'harvest').fetch()
        self.assertEqual(1, len(all_data))

        data = all_data[0]
        self.assertEqual('harvest', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(5, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_store_total_harvest_for_one_plant(self):
        HarvestAction(self._harvest('potato', 1)).execute()
        HarvestAction(self._harvest('potato', 2)).execute()

        all_data = Farm.query(Farm.action == 'harvest').fetch()
        self.assertEqual(1, len(all_data))

        data = all_data[0]
        self.assertEqual('harvest', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(3, data.quantity)

    def test_should_store_harvest_for_different_plants_independently(self):
        HarvestAction(self._harvest('potato', 2)).execute()
        HarvestAction(self._harvest('carrot', 3)).execute()

        all_data = Farm.query(Farm.action == 'harvest').fetch()
        self.assertEqual(2, len(all_data))

        data = all_data[0]
        self.assertEqual('harvest', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(2, data.quantity)
        self.assertEqual('sul123', data.district_id)

        data = all_data[1]
        self.assertEqual('harvest', data.action)
        self.assertEqual('carrot', data.crop_name)
        self.assertEqual(3, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_subtract_from_planted_quantity(self):
        HarvestAction(self._harvest('potato', 2)).execute()

        plant_data = Farm.query(Farm.action == 'plant',
                                Farm.crop_name == 'potato').get()

        self.assertEqual(8, plant_data.quantity)

    def test_should_respond_with_error_sms_when_not_enough_planted(self):
        msg = HarvestAction(self._harvest('potato', 100000)).execute()

        self.assertEqual(_('Not enough {} planted').format('potato'), msg)

    def test_should_not_allow_user_without_permission(self):
        self.sms.user.role = None

        msg = HarvestAction(self._harvest('potato', 1)).execute()
        self.assertEqual(_('Command not allowed'), msg)
