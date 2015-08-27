import unittest
from google.appengine.ext import testbed
from app.api.sms.sell_action import SellCommand, SellAction
from app.model.farm import Farm
from app.model.sms_request import SmsRequest
from app.model.user import User
from app.i18n import _


class SellActionTest(unittest.TestCase):

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

        Farm(action='harvest', district_id='sul123', crop_name='potato', quantity=10).put()
        Farm(action='harvest', district_id='sul123', crop_name='carrot', quantity=5).put()

    def _sell(self, plant, amount):
        cmd = SellCommand(self.sms)
        cmd.plant = plant
        cmd.amount = amount
        return cmd

    def test_should_respond_with_success(self):
        msg = SellAction(self._sell('potato', 5)).execute()
        self.assertEqual(_('Sell command succeeded'), msg)

    def test_should_store_sale_for_one_plant(self):
        SellAction(self._sell('potato', 5)).execute()

        all_data = Farm.query(Farm.action == 'sell').fetch()
        self.assertEqual(1, len(all_data))

        data = all_data[0]
        self.assertEqual('sell', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(5, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_store_total_sale_for_one_plant(self):
        SellAction(self._sell('potato', 1)).execute()
        SellAction(self._sell('potato', 2)).execute()

        all_data = Farm.query(Farm.action == 'sell').fetch()
        self.assertEqual(1, len(all_data))

        data = all_data[0]
        self.assertEqual('sell', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(3, data.quantity)

    def test_should_store_sale_for_different_plants_independently(self):
        SellAction(self._sell('potato', 2)).execute()
        SellAction(self._sell('carrot', 3)).execute()

        all_data = Farm.query(Farm.action == 'sell').fetch()
        self.assertEqual(2, len(all_data))

        data = all_data[0]
        self.assertEqual('sell', data.action)
        self.assertEqual('potato', data.crop_name)
        self.assertEqual(2, data.quantity)
        self.assertEqual('sul123', data.district_id)

        data = all_data[1]
        self.assertEqual('sell', data.action)
        self.assertEqual('carrot', data.crop_name)
        self.assertEqual(3, data.quantity)
        self.assertEqual('sul123', data.district_id)

    def test_should_subtract_from_harvested_quantity(self):
        SellAction(self._sell('potato', 2)).execute()

        harvest_data = Farm.query(Farm.action == 'harvest',
                                  Farm.crop_name == 'potato').get()

        self.assertEqual(8, harvest_data.quantity)

    def test_should_respond_with_error_sms_when_not_enough_harvested(self):
        msg = SellAction(self._sell('potato', 100000)).execute()

        self.assertEqual(_('Not enough {} harvested').format('potato'), msg)

    def test_should_not_allow_user_without_permission(self):
        self.sms.user.role = None

        msg = SellAction(self._sell('potato', 1)).execute()
        self.assertEqual(_('Command not allowed'), msg)
