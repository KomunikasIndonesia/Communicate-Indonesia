from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action
from app.model.farm import Farm


class SellAction(Action):
    """
    Execute a sell operation.
    """
    CMD = 'sell'

    def __init__(self, command):
        super(SellAction, self).__init__(command)

    def execute(self):
        user = self.command.sms.user[0]
        new = Farm(id=Farm.id(),
                   district_id=user.district_id,
                   action=self.CMD,
                   crop_name=self.command.sell,
                   quantity=self.command.amount)
        new.put()


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
        self.sell = None
        self.amount = None

        if self.args[0] and self.args[0].isdigit():
            self.amount = int(self.args[0])
            self.sell = self.args[1]

        if self.args[1] and self.args[1].isdigit():
            self.sell = self.args[0]
            self.amount = int(self.args[1])

    def valid(self):
        valid_cmd = any([self.cmd == cmd for cmd in self.VALID_CMDS])
        return valid_cmd and self.amount and self.sell
