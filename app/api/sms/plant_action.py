from app.api.sms.base_action import ThreeArgCommand
from app.command.base import Action


class PlantAction(Action):
    """
    Execute a plant operation
    """
    def __init__(self, command):
        super(PlantAction, self).__init__(command)


class PlantCommand(ThreeArgCommand):
    """
    Represents a plant command

    A sell command can take the form of:
        <command> <value> <plant>
        <command> <plant> <value>

    eg.
        sell 20 potato
        sell potato 20
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
