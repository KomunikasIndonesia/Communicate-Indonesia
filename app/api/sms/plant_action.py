import logging
from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm

from app.i18n import _
from google.appengine.ext import ndb
from app.model.permission import RECORD_PLANT


class PlantAction(Action):
    """
    Execute a plant operation
    """
    CMD = 'plant'

    def __init__(self, command):
        super(PlantAction, self).__init__(command)

    def execute(self):
        """
        Update plant totals
        """
        cmd = self.command
        user = cmd.sms.user

        if RECORD_PLANT not in user.permissions:
            logging.info('{} - User {} does not have permission {}'.format(
                cmd.sms.id, user.id, RECORD_PLANT))
            return _('Command not allowed')

        plant = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                   Farm.crop_name == cmd.plant,
                                   Farm.action == 'plant')).get()
        if not plant:
            plant = Farm(id=Farm.id(),
                         district_id=user.district_id,
                         action=self.CMD,
                         crop_name=cmd.plant,
                         quantity=0)

        plant.quantity += cmd.amount
        plant.put()

        return _('Plant command succeeded')


class PlantCommand(ThreeArgCommand):
    """
    Represents a plant command

    A plant command can take the form of:
        <command> <value> <plant>
        <command> <plant> <value>

    eg.
        plant 20 potato
        plant potato 20
    """
    VALID_CMDS = [
        'plant',  # en
        'tanam',  # in
    ]

    def __init__(self, sms):
        super(PlantCommand, self).__init__(sms)
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
