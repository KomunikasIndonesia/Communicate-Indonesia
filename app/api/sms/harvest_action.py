from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm
from app.model.user import User


class HarvestAction(Action):
    """
    Execute a harvest operation.
    """
    CMD = 'harvest'

    def __init__(self, command):
        super(HarvestAction, self).__init__(command)
        self.harvest = command.harvest
        self.amount = command.amount
        self.district_id = command.district()
        self.valid = command.valid()

    def execute(self):
        if not self.valid:
            raise Exception('harvest command is invalid')

        new = Farm(id=Farm.id(),
                   district_id=self.district_id,
                   action=self.CMD,
                   crop_name=self.harvest,
                   quantity=self.amount)
        new.put()

        return new.toJson()


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

    def district(self):
        user = User.query(User.phone_number == self.sms.from_number).get()
        return user.district_id
