import logging

from app.api.sms.base_action import OneArgCommand
from app.command.base import Action
from app.model.farm import Farm

from app.i18n import _
from google.appengine.ext import ndb
from app.model.permission import RECORD_SELL


class SellAction(Action):
    """
    Execute a sell operation.
    """
    CMD = 'sell'

    def __init__(self, command):
        super(SellAction, self).__init__(command)

    def execute(self):
        cmd = self.command
        user = self.command.sms.user

        if RECORD_SELL not in user.permissions:
            logging.info('{} - User {} does not have permission {}'.format(
                cmd.sms.id, user.id, RECORD_SELL))
            return _('Command not allowed')

        harvest_total = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                           Farm.crop_name == cmd.plant,
                                           Farm.action == 'harvest')).get()

        if not harvest_total or harvest_total.quantity < cmd.amount:
            logging.info('{} - Not enough {} harvested'.format(cmd.sms.id,
                                                               cmd.plant))
            return _('Not enough {} harvested').format(cmd.plant)

        sell_total = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                        Farm.crop_name == cmd.plant,
                                        Farm.action == 'sell')).get()
        if not sell_total:
            sell_total = Farm(id=Farm.id(),
                              district_id=user.district_id,
                              action=self.CMD,
                              crop_name=cmd.plant,
                              quantity=0)

        harvest_total.quantity -= cmd.amount
        harvest_total.put()
        sell_total.quantity += cmd.amount
        sell_total.put()

        return _('Sell command succeeded')


class SellCommand(OneArgCommand):
    """
    Represents a sell command

    A sell command takes the form of:
        <command> <value> <sell>
        <command> <sell> <value>

    eg.
        sell 20 potato
        sell potato 20
    """
    VALID_CMDS = [
        'sell',  # en
        'jual',  # in
    ]

    def __init__(self, sms):
        super(SellCommand, self).__init__(sms)
        self.plant = None
        self.amount = None

        words = self.message.split()

        for word in words:
            if word.isdigit():
                self.amount = int(word)
                words.remove(word)
                break

        if words:
            self.plant = ' '.join(words).lower()

    def valid(self):
        return super(SellCommand, self).valid() \
            and self.amount and self.plant
