import unittest
from google.appengine.ext import testbed
from app.api.sms.sell_action import SellCommand
from app.model.sms_request import SmsRequest
from app.model.user import User


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

    def _harvest(self, plant, amount):
        cmd = SellCommand(self.sms)
        cmd.plant = plant
        cmd.amount = amount
        return cmd

    def test_should_respond_with_success(self):
        pass

    def test_should_store_sale_for_one_plant(self):
        pass

    def test_should_store_total_sale_for_one_plant(self):
        pass

    def test_should_store_sale_for_different_plants_independently(self):
        pass

    def test_should_subtract_from_harvested_quantity(self):
        pass

    def test_should_respond_with_error_sms_when_not_enough_harvested(self):
        pass
