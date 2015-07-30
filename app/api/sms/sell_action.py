from app.command.base import Command, CommandData, Action


class SellAction(Action):
    pass


class SellCommandData(CommandData):

    def __init__(self, sms):
        super(SellCommandData, self).__init__(sms)

        words = sms.body.split(' ')

        self.cmd = words[0]
        self.plant = words[1]
        self.amount = words[2]


class SellCommand(Command):

    command_data_class = SellCommandData
    commands = [
        'jual',
        'sell',
    ]
