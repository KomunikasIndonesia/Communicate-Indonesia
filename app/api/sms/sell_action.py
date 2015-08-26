from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm

from app.i18n import _
from google.appengine.ext import ndb


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

        harvest_total = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                           Farm.crop_name == cmd.plant,
                                           Farm.action == 'harvest')).get()

        if not harvest_total or harvest_total.quantity < cmd.amount:
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


class SellCommand(ThreeArgCommand):
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

        if self.args[0] and self.args[0].isdigit():
            self.amount = int(self.args[0])
            self.plant = self.args[1]

        if self.args[1] and self.args[1].isdigit():
            self.plant = self.args[0]
            self.amount = int(self.args[1])

    def valid(self):
        valid_cmd = any([self.cmd == cmd for cmd in self.VALID_CMDS])
        return valid_cmd and self.amount and self.plant
