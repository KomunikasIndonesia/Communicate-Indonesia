from app.command.base import Command


class OneArgCommand(Command):
    """
    One argument commands

    Format: <command> <rest>
    """
    def __init__(self, sms):
        super(OneArgCommand, self).__init__(sms)
        words = sms.body.split(' ')
        self.sms = sms
        self.cmd = None
        self.message = ''

        if words:
            self.cmd = words[0].strip()
            self.message = ' '.join(words[1:])


class ThreeArgCommand(Command):

    """
    Three argument commands

    Format: <command> <arg0> <arg1>
    """
    def __init__(self, sms):
        """
        Initialize the command based on sms
        :param SmsRequest sms:
        :return:
        """
        super(ThreeArgCommand, self).__init__(sms)
        words = sms.body.split(' ')
        self.sms = sms
        self.cmd = None
        self.args = [None, None]
        self.message = ''

        if words:
            self.cmd = words[0].strip()

        if len(words) >= 3:
            self.args = [word.strip() for word in words[1:3]]
            self.message = ' '.join(words[3:])

        if len(words) == 2:
            self.args = [words[1].strip(), None]
