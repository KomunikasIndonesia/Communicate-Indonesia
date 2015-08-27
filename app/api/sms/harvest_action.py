import logging
from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm

from app.i18n import _
from google.appengine.ext import ndb
from app.model.permission import RECORD_HARVEST


class HarvestAction(Action):
    """
    Execute a harvest operation.
    """
    CMD = 'harvest'

    def __init__(self, command):
        super(HarvestAction, self).__init__(command)

    def execute(self):
        """
        Update plant and harvest totals
        """
        cmd = self.command
        user = cmd.sms.user

        if RECORD_HARVEST not in user.permissions:
            logging.info('{} - User {} does not have permission {}'.format(
                cmd.sms, user.id, RECORD_HARVEST))
            return _('Command not allowed')

        plant_total = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                         Farm.crop_name == cmd.plant,
                                         Farm.action == 'plant')).get()

        if not plant_total or plant_total.quantity < cmd.amount:
            logging.info('{} - Not enough {} planted'.format(cmd.sms.id,
                                                             cmd.plant))
            return _('Not enough {} planted').format(cmd.plant)

        harvest_total = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                           Farm.crop_name == cmd.plant,
                                           Farm.action == 'harvest')).get()
        if not harvest_total:
            harvest_total = Farm(id=Farm.id(),
                                 district_id=user.district_id,
                                 action=self.CMD,
                                 crop_name=cmd.plant,
                                 quantity=0)

        plant_total.quantity -= cmd.amount
        plant_total.put()
        harvest_total.quantity += cmd.amount
        harvest_total.put()

        return _('Harvest command succeeded')


class HarvestCommand(ThreeArgCommand):
    """
    Represents a harvest command

    A harvest command takes the form of:
        <command> <value> <harvest>
        <command> <harvest> <value>

    eg.
        harvest 20 potato
        harvest potato 20
    """
    VALID_CMDS = [
        'harvest',  # en
        'panen',    # in
    ]

    def __init__(self, sms):
        super(HarvestCommand, self).__init__(sms)
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
