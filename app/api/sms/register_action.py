import logging
from app.api.sms.harvest_action import HarvestAction
from app.api.sms.plant_action import PlantAction
from app.api.sms.sell_action import SellAction
from app.i18n import _
from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm
from app.model.permission import REGISTER_PLANT
from google.appengine.ext import ndb


class RegisterAction(Action):
    """
    Execute a register operation
    """
    CMD = 'register'

    def __init__(self, command):
        super(RegisterAction, self).__init__(command)

    def execute(self):
        """
        Register a plant in the system
        """
        cmd = self.command
        user = cmd.sms.user

        if REGISTER_PLANT not in user.permissions:
            logging.info('{} - User {} does not have permission {}'.format(
                cmd.sms.id, user.id, REGISTER_PLANT))
            return _('Command not allowed')

        plant = Farm.query(ndb.AND(Farm.district_id == user.district_id,
                                   Farm.crop_name == cmd.plant,
                                   Farm.action == 'plant')).get()
        if plant:
            logging.info('{} - User {} tried to register an already registered plant {}'.format(
                cmd.sms.id, user.id, cmd.plant))
            return _('Plant already registered')

        Farm(id=Farm.id(),
             district_id=user.district_id,
             action=PlantAction.CMD,
             crop_name=cmd.plant,
             unit_type=cmd.unit_type,
             quantity=0).put()
        Farm(id=Farm.id(),
             district_id=user.district_id,
             action=HarvestAction.CMD,
             crop_name=cmd.plant,
             unit_type=cmd.unit_type,
             quantity=0).put()
        Farm(id=Farm.id(),
             district_id=user.district_id,
             action=SellAction.CMD,
             crop_name=cmd.plant,
             unit_type=cmd.unit_type,
             quantity=0).put()

        return _('Register command succeeded')


class RegisterCommand(ThreeArgCommand):
    """
    Represents a register command

    A register command can take the form of:
        <command> <plant> <unit_type>

    eg.
        register potato weight
        daftar potato berat
        mendaftar kentang berat
    """
    VALID_CMDS = [
        'register',  # en
        'daftar',  # in
        'mendaftar',  # in
    ]

    def __init__(self, sms):
        super(RegisterCommand, self).__init__(sms)
        self.plant = self.args[0].lower() if self.args[0] else None
        self.unit_type = self.args[1].lower() if self.args[1] else None

        if self.unit_type:
            self.unit_type = {
                'biji': 'count',
                'berat': 'weight',
                'volume': 'volume'
            }.get(self.unit_type, self.unit_type)

    def valid(self):
        return super(ThreeArgCommand, self).valid() \
               and self.plant \
               and self.unit_type in Farm.DEFAULT_UNITS.keys()
