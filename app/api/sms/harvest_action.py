from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm

from app.i18n import _
from google.appengine.ext import ndb


class HarvestAction(Action):
    """
    Execute a harvest operation.
    """
    CMD = 'harvest'

    def __init__(self, command):
        super(HarvestAction, self).__init__(command)

    def execute(self):
        cmd = self.command
        user = cmd.sms.user

        new = Farm(id=Farm.id(),
                   district_id=user.district_id,
                   action=self.CMD,
                   crop_name=cmd.harvest,
                   quantity=cmd.amount)
        new.put()

        query = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                   Farm.crop_name == cmd.harvest,
                                   Farm.action == 'plant'))
        plant = query.fetch()

        if plant:
            plant = plant[0]
            update = plant.key.get()
            update.quantity = plant.quantity - cmd.amount
            update.put()

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
        self.harvest = None
        self.amount = None

        if self.args[0] and self.args[0].isdigit():
            self.amount = int(self.args[0])
            self.harvest = self.args[1]

        if self.args[1] and self.args[1].isdigit():
            self.harvest = self.args[0]
            self.amount = int(self.args[1])

    def valid(self):
        valid_cmd = any([self.cmd == cmd for cmd in self.VALID_CMDS])
        return valid_cmd and self.amount and self.harvest
