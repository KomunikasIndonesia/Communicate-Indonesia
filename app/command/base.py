from app.util.matcher import match


class Action(object):
    """
    Actions perform operations on an sms message
    """

    def execute(self, command_data):
        """
        Do work on command data

        This operation has side effects
        :param CommandData command_data: The command data
        :return: None
        """
        pass


class CommandData(object):
    """
    Command data parses raw sms into action specific data
    """

    def __init__(self, sms):
        self.sms = sms
        self.cmd = ''


class Command(object):
    """
    Commands parse sms and match sms to operations
    """
    command_data_class = CommandData
    commands = []

    def __init__(self, action):
        self.action = action

    def match(self, sms):
        """
        Return true if the word matches this command
        :param Sms sms: The raw sms
        :return: True if the word matches this command
        """
        data = self.command_data_class(sms)

        for valid_cmd in self.valid_cmds:
            if match(valid_cmd, data.cmd):
                return True

        return False

    def dispatch(self, sms):
        """
        Executes the action associated to this command.
        :param Sms sms: The sms object
        :return: None
        """
        self.action.execute(self.command_data_class(sms))
